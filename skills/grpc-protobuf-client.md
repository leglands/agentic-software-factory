---
name: grpc-protobuf-client
description: Consuming gRPC services from TypeScript/Rust clients using protobuf binary format (NOT JSON transcoding). Covers tonic client in Rust, grpc-web from browser, protobuf code generation, streaming RPCs, interceptors for auth, error handling Status codes, deadline/timeout, retry policy, connection pooling.
triggers:
  - consume grpc service from typescript
  - tonic grpc client rust
  - grpc-web browser client
  - protobuf code generation
  - grpc streaming rpc client
  - grpc interceptors auth
  - grpc error handling status
  - grpc deadline timeout
  - grpc retry policy
  - grpc connection pooling
eval_cases:
  - description: "Generate TypeScript gRPC-web client from .proto files using protoc-gen-es and @connectrpc/connect-web. Configure Binary format with fetch-based transport."
    pass_if: |
      protoc --es_out=generated --es_opt=target=ts \
        --connectrpc_out=generated --connectrpc_opt=import_extension=.pb.ts \
        -I proto proto/*.proto
      # Client uses Binary format: import { createPromiseClient } from '@connectrpc/connect';
      # import { createGrpcWebTransport } from '@connectrpc/connect-web';
      # const transport = createGrpcWebTransport({
      #   baseUrl: 'https://api.example.com',
      #   httpVersion: 'HTTP/2',
      #   useBinaryFormat: true,
      # });

  - description: "Generate Rust tonic client from .proto files using tonic-build. Configure channel with appropriate transport and connection pool."
    pass_if: |
      // Cargo.toml: tonic-build = "0.24"
      // build.rs: tonic_build::compile_protos("proto/service.proto").unwrap();
      // src/generated.rs: include!("generated.tonic.rs");
      //
      // Connection pool with hyper socket address:
      // let channel = Channel::from_shared("http://[::1]:50051")?
      //     .pool_config(PoolConfig::new().max_idle_per_channel(16))
      //     .connect()
      //     .await?;

  - description: "Implement Rust tonic interceptors for JWT authentication and metadata propagation across all RPC calls."
    pass_if: |
      #[derive(Clone)]
      struct AuthInterceptor {
          token: String,
      }
      impl Interceptor for AuthInterceptor {
          fn call(&mut self, request: tonic::Request<()>) -> Result<tonic::Request<()>, tonic::Status> {
              let mut req = request;
              let meta = req.metadata_mut();
              meta.insert("authorization", self.token.parse().unwrap());
              Ok(req)
          }
      }
      // Use with client: let client = MyService::with_interceptor(channel, auth_interceptor);

  - description: "Handle gRPC Status codes in Rust client: convert tonic::Status to domain errors, map NOT_FOUND to Option<T>, handle UNAUTHENTICATED with token refresh."
    pass_if: |
      match tonic::Status::from_error(err) {
          tonic::Status::NotFound(_) => Ok(None),
          tonic::Status::Unauthenticated(_) => {
              let new_token = refresh_token().await?;
              let mut updated = self.clone();
              updated.token = new_token;
              updated.call(request).await
          }
          s => Err(MyError::Grpc(s.code().description().to_string())),
      }

  - description: "Implement streaming RPC client in TypeScript using @connectrpc/connect. Handle ServerStreamResponse and backpressure with async generators."
    pass_if: |
      // Server streaming:
      const stream = client.serverStream({ filter: 'active' });
      for await (const item of stream) {
          console.log('received:', item);
      }
      // Client streaming:
      const clientStream = client.clientStream();
      for (const item of items) {
          clientStream.send(item);
      }
      const result = await clientStream.closeAndReceive();

  - description: "Implement streaming RPC in Rust using tonic with mpsc channel for bidir streaming. Handle backpressure with bounded buffer."
    pass_if: |
      // Server streaming
      let mut stream = client.server_stream(Request::new(req)).await?.into_inner();
      while let Some(item) = stream.message().await? {
          tokio::spawn(handle_item(item));
      }
      // Bidirectional streaming with bounded channel
      let (tx, rx) = mpsc::channel(100);
      let response = client.bidi_stream(Request::new(rx)).await?.into_inner();
      // tx.send(item).await? with proper backpressure

  - description: "Configure deadline/timeout on gRPC requests in Rust using tonic with the Timeout or Tower timeout middleware. Handle DeadlineExceeded status code."
    pass_if: |
      use tower::timeout::Timeout;
      use tonic::transport::Channel;
      
      let channel = Channel::from_static("http://[::1]:50051")
          .timeout(Duration::from_secs(5));
      // Or per-call:
      let response = client
          .some_rpc(request)
          .timeout(Duration::from_secs(3))
          .await?;
      // Handle: tonic::Status::DeadlineExceeded => Err(TimeoutError)

  - description: "Implement gRPC retry policy in Rust using tonic with Tower Retry middleware. Configure exponential backoff with jitter for transient failures."
    pass_if: |
      use tower::retry::Retry;
      use tower::timeout::Timeout;
      
      let retry_policy = Retry::new(
          Move |_| {
              let mut policy = Policy::new(
                  ExponentialBackoff::new(Duration::from_secs(1))
                      .map_current_time(|d| d + Duration::from_millis(rand::random::<u64>() % 100))
              );
              policy = policy.add_tonic_policy(TonicRetryPolicy);
              policy
          },
          service.clone(),
      );

  - description: "Configure gRPC-web browser client with proper CORS headers, binary format, and AbortSignal for request cancellation."
    pass_if: |
      import { createGrpcWebTransport } from '@connectrpc/connect-web';
      const transport = createGrpcWebTransport({
          baseUrl: 'https://api.example.com',
          useBinaryFormat: true,
          interceptors: [new AuthInterceptor()],
          readAbortSignal: controller.signal,
      });
      // CORS: response.headers.get('Access-Control-Allow-Origin') verified by transport

  - description: "Generate and use protobuf TypeScript types from .proto files. Handle well-known types (Timestamp, Duration, Any) with proper JSON serialization fallback."
    pass_if: |
      // google/protobuf/timestamp.proto -> google.protobuf.Timestamp
      const timestamp = proto.google.protobuf.Timestamp.create({
          seconds: BigInt(Math.floor(Date.now() / 1000)),
          nanos: 0,
      });
      // JSON serialization for logging:
      const json = JSON.stringify(timestamp, (_, v) => typeof v === 'bigint' ? v.toString() : v);

  - description: "Implement gRPC connection keepalive and health checks in Rust using tonic with tower-grpc and grpcio Health service."
    pass_if: |
      use tonic_health::client;
      
      let channel = Channel::connect("http://[::1]:50051").await?;
      let mut health = client::make_health_client(channel);
      let ( Serving { status, .. }, ) = health.watch().ready().await?.into_inner();
      // Keepalive config:
      let channel = Channel::from_static("http://[::1]:50051")
          .keepalive_time(Duration::from_secs(30))
          .keepalive_timeout(Duration::from_secs(10))
          .connect()
          .await?;

  - description: "Handle gRPC error propagation from server to TypeScript client. Map google.rpc.Status details to typed domain errors with retry decision logic."
    pass_if: |
      import { ConnectError } from '@connectrpc/connect';
      try {
          await client.someRpc(req);
      } catch (e) {
          if (e instanceof ConnectError) {
              const status = e.rawOrigin;
              if (e.code === 'RESOURCE_EXHAUSTED') {
                  // retry with backoff
              }
              const details = e.findDetails();
              // map to domain error
          }
      }

category: client-development
tags:
  - grpc
  - protobuf
  - tonic
  - connect-rpc
  - grpc-web
  - typescript
  - rust
  - streaming
  - interceptors
  - error-handling
---

# Consuming gRPC Services with Protobuf Binary Format

This skill covers consuming gRPC services from **TypeScript** (browser via grpc-web) and **Rust** (tonic) clients using native protobuf binary format. It explicitly excludes JSON transcoding mode.

---

## 1. Protobuf Code Generation

### TypeScript (grpc-web via Connect-RPC)

```bash
npm install @bufbuild/protobuf @connectrpc/connect @connectrpc/connect-web @connectrpc/connect-protoc-gen-es
```

```bash
protoc \
  --es_out=generated \
  --es_opt=target=ts \
  --connectrpc_out=generated \
  --connectrpc_opt=import_extension=.pb.ts \
  -I proto \
  proto/*.proto
```

```typescript
// src/client.ts
import { createPromiseClient } from '@connectrpc/connect';
import { createGrpcWebTransport } from '@connectrpc/connect-web';
import { MyService } from '../generated/gen/connectrpc/my_service_connect';

const transport = createGrpcWebTransport({
  baseUrl: 'https://api.example.com',
  useBinaryFormat: true,
  httpVersion: 'HTTP/2',
});

export const client = createPromiseClient(MyService, transport);
```

### Rust (tonic)

```toml
# Cargo.toml
[dependencies]
tonic = "0.24"
prost = "0.13"
tokio = { version = "1", features = ["full"] }

[build-dependencies]
tonic-build = "0.24"
```

```rust
// build.rs
fn main() -> Result<(), Box<dyn std::error::Error>> {
    tonic_build::configure()
        .build_server(false)
        .build_client(true)
        .compile_protos(&["proto/my_service.proto"], &["proto"])?;
    Ok(())
}
```

```rust
// src/client.rs
pub mod generated {
    tonic::include_proto!("my_service");
}

use generated::my_service_client::MyServiceClient;
use tonic::transport::Channel;

pub async fn create_client() -> Result<MyServiceClient<Channel>, tonic::Error> {
    let channel = Channel::from_static("http://[::1]:50051")
        .connect()
        .await?;
    Ok(MyServiceClient::new(channel))
}
```

---

## 2. Connection Pooling (Rust)

```rust
use tonic::transport::{Channel, Endpoint, PoolConfig};

pub async fn create_pooled_channel(
    addr: &str,
    max_idle_per_channel: usize,
) -> Result<Channel, tonic::Error> {
    let pool_config = PoolConfig::new()
        .max_idle_per_channel(max_idle_per_channel)
        .max_remotely_initialized_per_channel(16)
        .init_idle_timeout(std::time::Duration::from_secs(300));

    let channel = Endpoint::from_static(addr)
        .pool_config(pool_config)
        .connect()
        .await?;

    Ok(channel)
}
```

---

## 3. Interceptors for Authentication

### Rust: JWT Metadata Interceptor

```rust
use tonic::{Request, Status, Interceptor};
use std::future::Future;
use tokio::task::Context;
use tower::{Service, ServiceBuilder};
use hyper::body::HttpBody;

#[derive(Clone)]
struct AuthInterceptor {
    token: String,
}

impl Interceptor for AuthInterceptor {
    fn call(&mut self, mut request: Request<()>) -> Result<Request<()>, Status> {
        let meta = request.metadata_mut();
        meta.insert("authorization", format!("Bearer {}", self.token).parse().unwrap());
        Ok(request)
    }
}

// Usage
let mut interceptor = AuthInterceptor { token: my_jwt.to_string() };
let client = MyServiceClient::with_interceptor(channel, interceptor);
```

### Rust: Tower-based Interceptor Stack

```rust
use tower::ServiceBuilder;
use tower_auth::AuthLayer;

let client = MyServiceClient::with_interceptor(
    channel,
    move |mut req: Request<()>| {
        req.metadata_mut().insert("x-api-key", api_key.parse().unwrap());
        Ok(req)
    }
);
```

### TypeScript: Auth Interceptor

```typescript
import { Interceptor, PromiseClient } from '@connectrpc/connect';
import { createPromiseClient } from '@connectrpc/connect';

const authInterceptor: Interceptor = (next) => async (req) => {
  const token = await getAccessToken();
  req.header.set('authorization', `Bearer ${token}`);
  return next(req);
};

const transport = createGrpcWebTransport({
  baseUrl: 'https://api.example.com',
  useBinaryFormat: true,
  interceptors: [authInterceptor],
});

export const client = createPromiseClient(MyService, transport);
```

---

## 4. Error Handling and Status Codes

### Rust: Status Code Mapping

```rust
use tonic::{Status, Code};

async fn handle_grpc_result<T>(result: Result<T, Status>) -> Result<T, MyError> {
    match result {
        Ok(value) => Ok(value),
        Err(status) => match status.code() {
            Code::NotFound => Err(MyError::NotFound(status.message().to_string())),
            Code::Unauthenticated => Err(MyError::AuthExpired(status.message().to_string())),
            Code::DeadlineExceeded => Err(MyError::Timeout),
            Code::ResourceExhausted => Err(MyError::RateLimited),
            Code::Unavailable => Err(MyError::ServiceUnavailable),
            _ => Err(MyError::Grpc(status.code().description().to_string())),
        },
    }
}

#[derive(Debug)]
pub enum MyError {
    NotFound(String),
    AuthExpired(String),
    Timeout,
    RateLimited,
    ServiceUnavailable,
    Grpc(String),
}
```

### TypeScript: ConnectError Handling

```typescript
import { ConnectError, Code } from '@connectrpc/connect';

async function callWithErrorHandling<T>(
  fn: () => Promise<T>
): Promise<T> {
  try {
    return await fn();
  } catch (e) {
    if (e instanceof ConnectError) {
      switch (e.code) {
        case Code.NotFound:
          throw new NotFoundError(e.message);
        case Code.Unauthenticated:
          await refreshToken();
          return fn();
        case Code.DeadlineExceeded:
          throw new TimeoutError();
        case Code.ResourceExhausted:
          throw new RateLimitError();
        default:
          throw new GrpcError(e.code, e.message);
      }
    }
    throw e;
  }
}
```

---

## 5. Streaming RPCs

### TypeScript: Server Streaming

```typescript
const stream = client.serverStream({ filter: 'active' });
for await (const item of stream) {
  console.log('Server event:', item);
}
```

### TypeScript: Client Streaming

```typescript
const clientStream = client.uploadEvents();
const events = generateEvents();

for (const event of events) {
  await clientStream.send(event);
}

const summary = await clientStream.closeAndReceive();
```

### TypeScript: Bidirectional Streaming

```typescript
const bidiStream = client.exchangeStream();
const producer = async () => {
  for (const item of dataSource) {
    await bidiStream.send({ id: item.id, value: item.value });
  }
  await bidiStream.complete();
};
const consumer = async () => {
  for await (const response of bidiStream) {
    processResponse(response);
  }
};
await Promise.all([producer(), consumer()]);
```

### Rust: Server Streaming

```rust
use tokio_stream::StreamExt;

let mut stream = client.server_stream(Request::new(req)).await?.into_inner();
while let Some(item) = stream.message().await? {
    println!("Received: {:?}", item);
}
```

### Rust: Bidirectional Streaming with Backpressure

```rust
use tokio::sync::mpsc;
use tokio_stream::wrappers::ReceiverStream;

async fn bidir_streaming_example(
    client: &mut MyServiceClient<Channel>,
) -> Result<(), tonic::Status> {
    let (tx, rx) = mpsc::channel::<Request>(100); // bounded buffer for backpressure

    let request = Request::new(ReceiverStream::new(rx));
    let mut response_stream = client.bidi_stream(request).await?.into_inner();

    // Producer
    let tx_clone = tx.clone();
    tokio::spawn(async move {
        for item in data_iterator {
            if tx_clone.send(Request::new(item)).await.is_err() {
                break;
            }
        }
    });

    // Consumer
    while let Some(response) = response_stream.message().await? {
        process(response);
    }

    Ok(())
}
```

---

## 6. Deadline / Timeout

### Rust: Per-Request Timeout with Tower

```rust
use tower::timeout::Timeout;
use std::time::Duration;

let channel = Channel::from_static("http://[::1]:50051")
    .timeout(Duration::from_secs(5))
    .connect()
    .await?;

let response = client
    .some_rpc(request)
    .timeout(Duration::from_secs(3))
    .await
    .map_err(|e| {
        if e.is::<tonic::Status>() {
            MyError::GrpcTimeout
        } else {
            MyError::Other(e.to_string())
        }
    })?;
```

### Rust: Global Channel Timeout

```rust
let channel = Channel::from_static("http://[::1]:50051")
    .connect_timeout(Duration::from_secs(10))
    .await?;
```

### TypeScript: AbortSignal with Timeout

```typescript
const controller = new AbortController();
const timeoutId = setTimeout(() => controller.abort(), 5000);

try {
  const response = await client.someRpc(req, {
    signal: controller.signal,
  });
  clearTimeout(timeoutId);
} catch (e) {
  if (e instanceof ConnectError && e.code === Code.DeadlineExceeded) {
    throw new TimeoutError();
  }
}
```

---

## 7. Retry Policy

### Rust: Tower Retry with Exponential Backoff

```rust
use tower::retry::Retry;
use tower::timeout::Timeout;
use std::time::Duration;
use rand::Rng;

#[derive(Clone)]
struct TonicRetryPolicy;

impl<S> Policy<S, Request<()>, tower::retry::Reason<&tonic::Status>> for TonicRetryPolicy
where
    S: Clone,
{
    type Future = std::future::Ready<Result<Self::Response, tower::retry::Error<Self::Retry>>>;
    type Response = ();
    type Retry = tonic::Status;

    fn retry(&self, request: &Request<()>, reason: &tonic::Status) -> Option<Self::Retry> {
        match reason {
            tonic::Status::Unavailable => Some(reason.clone()),
            tonic::Status::ResourceExhausted(_) => Some(reason.clone()),
            _ => None,
        }
    }

    fn clone(&self) -> Self {
        TonicRetryPolicy
    }
}

let exponential_backoff = ExponentialBackoff::new(Duration::from_secs(1))
    .map_current_time(|d| {
        d + Duration::from_millis(rand::thread_rng().gen_range(0..100))
    })
    .max_delay(Duration::from_secs(30))
    .factor(2);

let retry_service = Retry::new(TonicRetryPolicy, client);
let timeout_service = Timeout::new(retry_service, Duration::from_secs(10));
```

### TypeScript: Client-Side Retry with Backoff

```typescript
import { createPromiseClient, Transport } from '@connectrpc/connect';

async function withRetry<T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  baseDelay: number = 1000
): Promise<T> {
  let lastError: Error | null = null;
  
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      return await fn();
    } catch (e) {
      lastError = e;
      if (e instanceof ConnectError) {
        if (e.code !== Code.Unavailable && e.code !== Code.ResourceExhausted) {
          throw e;
        }
      }
      const delay = baseDelay * Math.pow(2, attempt) + Math.random() * 100;
      await new Promise(r => setTimeout(r, delay));
    }
  }
  throw lastError;
}

const result = await withRetry(() => client.someRpc(request));
```

---

## 8. Connection Keepalive and Health Checks

### Rust: Keepalive Configuration

```rust
let channel = Channel::from_static("http://[::1]:50051")
    .keepalive_time(Duration::from_secs(30))
    .keepalive_timeout(Duration::from_secs(10))
    .connect()
    .await?;
```

### Rust: Health Check via grpc-health-probe

```rust
use tonic_health::client;

async fn check_health(channel: Channel) -> Result<bool, tonic::Status> {
    let mut health = client::make_health_client(channel);
    let (Serving { status, .. }, ) = health.watch().ready().await?.into_inner();
    Ok(status == tonic_health::ServingStatus::Serving)
}
```

---

## 9. Well-Known Types

### TypeScript: Timestamp and Duration

```typescript
import { Timestamp, Duration } from '@bufbuild/protobuf';
import { google } from '@bufbuild/protobuf';

// Creating Timestamp
const timestamp = new Timestamp({
  seconds: BigInt(Math.floor(Date.now() / 1000)),
  nanos: 0,
});

// Using in request
const req = new SomeRequest({
  created_at: timestamp,
  timeout: new Duration({ seconds: BigInt(30), nanos: 0 }),
});

// JSON serialization
const json = JSON.stringify(timestamp, (k, v) =>
  typeof v === 'bigint' ? v.toString() : v
);
```

### Rust: Timestamp and Duration

```rust
use prost::well_known_types::timestamp::Timestamp;
use prost::well_known_types::duration::Duration;

let ts = Timestamp {
    seconds: chrono::Utc::now().timestamp(),
    nanos: 0,
    ..Default::default()
};

let dur = Duration {
    seconds: 30,
    nanos: 0,
};
```

---

## 10. CORS for grpc-web

### Server Headers Required

```
Access-Control-Allow-Origin: https://app.example.com
Access-Control-Allow-Methods: POST, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization, X-Grpc-Web
Access-Control-Expose-Headers: grpc-status, grpc-message
```

### Client: grpc-web Fetch Transport

```typescript
import { createGrpcWebTransport } from '@connectrpc/connect-web';

const transport = createGrpcWebTransport({
  baseUrl: 'https://api.example.com',
  useBinaryFormat: true,
  credentials: 'include',
});

const client = createPromiseClient(MyService, transport);
```

---

## 11. Best Practices

1. **Always use binary format** — `useBinaryFormat: true` in Connect-RPC; avoid JSON transcoding for production performance.

2. **Pool connections** — Reuse channels across requests; configure `max_idle_per_channel` based on concurrency needs.

3. **Set timeouts** — Both per-request and global channel timeouts prevent hanging connections.

4. **Implement proper backoff** — Exponential backoff with jitter for retries avoids thundering herd.

5. **Handle UNAUTHENTICATED gracefully** — Token refresh and request retry is a common pattern.

6. **Use bounded channels for streaming** — Prevents memory exhaustion on high-throughput streams.

7. **Health check on startup** — Verify gRPC service is reachable before starting application logic.

8. **Propagate context** — Include request IDs, tracing spans in gRPC metadata for observability.
