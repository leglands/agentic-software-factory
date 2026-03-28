---
name: Rust Refactoring & Performance Optimization
description: Master advanced Rust patterns for hot-path optimization, zero-copy architectures, unsafe auditing, and compile-time guarantees. Apply iterator idioms, buffer reuse strategies, and type-state design to eliminate allocations and improve throughput.
version: 1.0.0
tags: [rust, performance, refactoring, unsafe, zero-copy, iterator, type-state]
scope: rust-dev
created: 2026-03-27
updated: 2026-03-27
eval_cases:
  - id: identify-hotpath
    prompt: |
      Given the following Rust function, identify the hot path and suggest where
      #[inline] or #[cold] annotations should be applied. Explain the reasoning
      based on call frequency and branch probability.

      ```rust
      pub fn process_buffer(input: &[u8]) -> Option<Vec<u8>> {
          if input.is_empty() {
              return None;
          }
          let mut result = Vec::with_capacity(input.len());
          for byte in input.iter() {
              if *byte == 0xFF {
                  result.push(0x00);
              } else {
                  result.push(*byte);
              }
          }
          Some(result)
      }

      fn helper_transform(b: u8) -> u8 {
          if b == 0xFF { 0x00 } else { b }
      }
      ```
    checks:
      - criteria: "Identifies `process_buffer` as hot path"
      - criteria: "Identifies `helper_transform` as cold/called frequently"
      - criteria: "Explains branch prediction for 0xFF check"
    expectations:
      - output_contains: "#[inline]"
      - output_contains: "#[cold]"
      - output_contains: "helper_transform"
      - output_contains: "hot"

  - id: apply-zero-copy
    prompt: |
      Refactor this code to eliminate per-call allocations using buffer reuse
      and zero-copy techniques. Replace the `.clone()` calls with zero-copy
      alternatives where possible. Use `&mut [u8]` for buffer reuse.

      ```rust
      #[derive(Debug)]
      pub struct Record {
          pub id: u64,
          pub name: String,
          pub payload: Vec<u8>,
      }

      impl Record {
          pub fn serialize(&self) -> Vec<u8> {
              let mut buf = Vec::with_capacity(64);
              buf.extend_from_slice(&self.id.to_le_bytes());
              buf.extend_from_slice(self.name.as_bytes());
              buf.extend_from_slice(&self.payload.len().to_le_bytes());
              buf.extend_from_slice(&self.payload);
              buf
          }

          pub fn deserialize(data: &[u8]) -> Option<Self> {
              if data.len() < 24 { return None; }
              let id = u64::from_le_bytes(data[0..8].try_into().unwrap());
              let name_len = u64::from_le_bytes(data[8..16].try_into().unwrap()) as usize;
              let payload_len = u64::from_le_bytes(data[16..24].try_into().unwrap()) as usize;
              if data.len() < 24 + name_len + payload_len { return None; }
              let name = String::from_utf8(data[24..24+name_len].to_vec()).ok()?;
              let payload = data[24+name_len..24+name_len+payload_len].to_vec();
              Some(Record { id, name, payload })
          }
      }
      ```
    checks:
      - criteria: "Uses &mut [u8] buffer for serialization"
      - criteria: "Eliminates .to_vec() and .clone() in deserialize"
      - criteria: "Uses Cow<str> or similar zero-copy type"
    expectations:
      - output_contains: "&mut [u8]"
      - output_contains_no: ".clone()"
      - output_contains_no: ".to_vec()"
      - rust_compiles: true

  - id: prove-isomorphism
    prompt: |
      Prove whether these two implementations are isomorphic under lifetime
      elision rules. If not, explain what lifetimes must be added and why.

      ```rust
      // Version A
      fn first_word(s: &str) -> &str {
          &s[..s.find(' ').unwrap_or(s.len())]
      }

      // Version B — does this compile? Explain.
      fn first_word(s: &str) -> &str {
          use std::collections::HashMap;
          let mut map: HashMap<&str, &str> = HashMap::new();
          map.insert("key", s);
          &s[..s.find(' ').unwrap_or(s.len())]
      }
      ```
    checks:
      - criteria: "Correctly states whether Version B compiles"
      - criteria: "Explains lifetime elision rules"
      - criteria: "Identifies the HashMap borrow issue"
    expectations:
      - output_contains: "Version B"
      - output_contains: "lifetime"
      - output_contains: "does not compile" or "error"

  - id: cleanup-dead-code
    prompt: |
      Audit the following module for dead code, unnecessary allocations, and
      clippy::perf warnings. List each issue with file:line reference and
      fix. Then apply the fixes.

      ```rust
      #![allow(dead_code)]

      use std::collections::HashMap;

      fn unused_import() {
          let map: HashMap<u32, u32> = HashMap::new();
          map.insert(1, 2);
      }

      enum Color {
          Red,
          Green,
          Blue,
      }

      fn match_handling(c: Color) -> u8 {
          match c {
              Color::Red => 0,
              Color::Green => 1,
              Color::Blue => 2,
              // What about other variants?
          }
      }

      #[allow(dead_code)]
      const NEVER_USED: i32 = 42;

      fn slow_collect(items: &[i32]) -> Vec<i32> {
          items.iter().map(|x| x * 2).collect()
      }
      ```
    checks:
      - criteria: "Identifies unused import"
      - criteria: "Flags #[allow(dead_code)]"
      - criteria: "Suggests iterator without collect() or explains why collect is needed"
      - criteria: "Mentions cargo clippy"
    expectations:
      - output_contains: "HashMap"
      - output_contains: "#[allow(dead_code)]"
      - output_contains: "clippy"
      - output_contains: "NEVER_USED"
---

# Rust Refactoring & Performance Optimization

## Hot/Cold Path Annotations

### `#[inline]` — Force Inlining

- **Always**: accessors, small trait methods, closures passed to iterators
- **Never**: complex functions w/ deep call stacks, error paths
- **Hint**: `#[inline(always)]` for tiny hot functions; `#[inline]` lets compiler decide

```rust
#[inline]
pub fn len(&self) -> usize {
    self.size
}

#[cold]
#[inline(never)]
pub fn report_error(&self, err: &Error) {
    eprintln!("Error: {}", err);
}
```

### `#[cold]` — Mark Unlikely Branches

- Error handlers, fallback paths, logging in hot loops
- Compiler uses for basic block ordering → instruction cache friendliness

## Buffer Reuse Pattern

Avoid per-call `Vec` allocation → reuse scratch buffer:

```rust
use std::mem::MaybeUninit;

pub struct Serializer {
    buf: Vec<u8>,
}

impl Serializer {
    pub fn new() -> Self {
        Serializer { buf: Vec::with_capacity(256) }
    }

    /// Zero-allocation serialization into pre-allocated buffer.
    /// Caller provides `dst` slice; this function writes into it directly.
    pub fn serialize_into<'a>(&mut self, src: &Record, dst: &'a mut [u8]) -> Result<&'a [u8], ()> {
        if dst.len() < 64 {
            return Err(());
        }
        dst[0..8].copy_from_slice(&src.id.to_le_bytes());
        let name_bytes = src.name.as_bytes();
        dst[8..8 + name_bytes.len()].copy_from_slice(name_bytes);
        Ok(&dst[..8 + name_bytes.len()])
    }
}
```

## Zero-Copy Techniques

### `Cow<str>` / `Cow<[u8]>`

```rust
use std::borrow::Cow;

fn sanitize(input: &str) -> Cow<str> {
    if input.contains(|c: char| c.is_control()) {
        Cow::Owned(input.replace(|c: char| c.is_control(), ""))
    } else {
        Cow::Borrowed(input) // Zero copy — no allocation
    }
}
```

### Zero-Copy Deserialization with `&[u8]`

```rust
// BAD: allocates Vec for payload
fn read_payload(data: &[u8]) -> Vec<u8> {
    data[8..].to_vec()
}

// GOOD: borrows, no allocation
fn read_payload(data: &[u8]) -> &[u8] {
    &data[8..]
}
```

### `into_` Methods for Ownership Transfer

```rust
struct Inner(Vec<u8>);

impl From<Vec<u8>> for Inner {
    fn from(v: Vec<u8>) -> Self {
        Inner(v)
    }
}

impl Inner {
    // Consumes self, avoids clone
    fn into_bytes(self) -> Vec<u8> {
        self.0
    }
}
```

## Streaming with Iterators

Avoid `.collect()` when processing large inputs:

```rust
// BAD: allocates entire Vec
let doubled: Vec<i32> = (0..1_000_000).map(|x| x * 2).collect();

// GOOD: lazy iterator, no allocation
let iter = (0..1_000_000).map(|x| x * 2);

// If you must iterate: use for_each or find directly
let sum: i64 = iter.sum();

// Or use itertools for chunked processing
use itertools::Itertools;
for chunk in &iter.into_iter().chunks(1024) {
    process_chunk(chunk?);
}
```

## `unsafe` Audit Checklist

1. **Minimize scope**: wrap unsafe in safe abstractions immediately
2. **Document invariants**: every unsafe block needs comment explaining why UB is impossible
3. **Mark with `UNSAFE_BODY` or custom marker**: `const UNSAFE_BODY: &str = "...";`
4. **Validate pointers**: check null, alignment, validity before dereferencing
5. **Use `MaybeUninit`**: for uninitialized memory, never use `std::mem::uninitialized()`

```rust
/// # Safety
/// `ptr` must be non-null and properly aligned.
/// The referent must be live for the duration of 'a.
unsafe fn borrow_unchecked<'a, T>(ptr: *const T) -> &'a T {
    &*ptr
}
```

## Lifetime Elision Cleanup

Lifetime elision rules (Rust 2018+):
- Each input reference → own lifetime
- If exactly one input lifetime → assigned to all output lifetimes
- Otherwise → user must annotate

```rust
// A: compiles — single input lifetime
fn first_word(s: &str) -> &str { ... }

// B: does NOT compile — HashMap holds &str that outlive function
fn broken(s: &str) -> &str {
    let mut m = HashMap::new();
    m.insert("key", s); // s is borrowed here
    &s[..1] // trying to return a borrow of s — lifetime issue
}
```

## `cargo clippy -W clippy::perf`

Run before/after benchmarks:

```bash
cargo clippy --workspace -- -W clippy::perf -W clippy::pedantic
```

Common perf warnings:
- `iter-clone` → use `copied()` or `cloned()` appropriately
- `into_iter` on `&Vec` → use `iter()` instead
- `redundant_allocation` → wrap in `Box<[T]>` instead of `Vec<T>`
- `unnecessary_filter_map` → `filter().map()` or `map().filter()`

## Criterion Benchmarks

```rust
use criterion::{black_box, criterion_group, criterion_main, Criterion};

fn bench_serialize(c: &mut Criterion) {
    let record = Record { id: 1, name: "test".into(), payload: vec![0u8; 32] };
    c.bench_function("serialize", |b| {
        b.iter(|| {
            let mut ser = Serializer::new();
            let mut buf = vec![0u8; 256];
            black_box(ser.serialize_into(black_box(&record), &mut buf));
        })
    });
}

criterion_group!(benches, bench_serialize);
criterion_main!(benches);
```

Run: `cargo bench`

## Dead Code Audit

```bash
# Find unused imports, unreachable code
cargo clippy --workspace -- -D clippy::unused -D clippy::unreachable

# cargo udeps — find unused dependencies
cargo install cargo-udeps
cargo +nightly udeps --workspace

# List all #[allow(dead_code)] locations
grep -rn 'allow(dead_code)' src/
```

### Checklist

- [ ] Remove `use` statements for items never referenced
- [ ] Check for `impl`s where all methods are `#[allow(dead_code)]`
- [ ] `#[allow(dead_code)]` on `struct`/`enum` → consider `#[derive(Debug)]` or `#[derive(PartialEq)]` usage
- [ ] Unreachable match arms: use `unreachable!()` or `#[deny(unreachable_patterns)]`

## Dependency Audit

```bash
# Scan for vulnerabilities
cargo audit

# Check for outdated dependencies
cargo outdated

# Update lockfile
cargo update
```

## Error Handling

### Libraries: `thiserror` over `anyhow`

```rust
use thiserror::Error;

#[derive(Debug, Error)]
pub enum ParseError {
    #[error("unexpected end of input at byte {0}")]
    UnexpectedEof(usize),

    #[error("invalid header: expected {expected}, found {found}")]
    InvalidHeader { expected: u32, found: u32 },
}

// Propagate with ?
impl TryFrom<&[u8]> for Record {
    type Error = ParseError;

    fn try_from(data: &[u8]) -> Result<Self, Self::Error> {
        let id = u64::from_le_bytes(
            data.get(0..8).ok_or(ParseError::UnexpectedEof(0))?
                .try_into()
                .map_err(|_| ParseError::UnexpectedEof(0))?
        );
        Ok(Record { id })
    }
}
```

### `anyhow` is for applications (binary crates) where ergonomics > abstraction cost.

## Type State Pattern

Encode invariants at type level → invalid states unrepresentable:

```rust
use std::marker::PhantomData;

// Marker types
pub struct Unconnected;
pub struct Connected;

// Connection state machine
pub struct TcpStream<State> {
    fd: i32,
    _state: PhantomData<State>,
}

impl TcpStream<Unconnected> {
    pub fn connect(addr: &str) -> Result<TcpStream<Connected>, std::io::Error> {
        // syscalls...
        Ok(TcpStream { fd: 3, _state: PhantomData })
    }
}

impl TcpStream<Connected> {
    pub fn send(&self, data: &[u8]) -> Result<(), std::io::Error> {
        // syscalls...
        Ok(())
    }

    pub fn close(self) -> TcpStream<Unconnected> {
        // syscalls...
        TcpStream { fd: -1, _state: PhantomData }
    }
}

// COMPILE-TIME guarantee: cannot call .send() on Unconnected stream
// TcpStream<Unconnected> does not implement send()
```

---

## Quick Reference

| Pattern | When to Use | Command |
|---------|-------------|---------|
| `#[inline]` | Tiny hot functions | `cargo clippy -W clippy::inline` |
| `#[cold]` | Error handlers, fallback | `cargo clippy -W clippy::cold_ulikely` |
| Buffer reuse | Serialization in loops | Manual `&mut [u8]` + capacity |
| `Cow<>` | Conditional string/bytes transformation | `std::borrow::Cow` |
| `thiserror` | Libraries, public APIs | `cargo add thiserror` |
| `anyhow` | Binaries, main application | `cargo add anyhow` |
| Type state | Protocol state machines | `PhantomData<State>` |
| `cargo audit` | Dependency vulnerabilities | `cargo install cargo-audit` |
| `cargo udeps` | Unused dependencies | `cargo +nightly udeps` |
