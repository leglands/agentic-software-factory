---
name: js-node-refactoring
version: 1.0.0
description: JavaScript/Node.js refactoring patterns and performance optimization techniques. Covers event loop, memory leaks, N+1 queries, streams, dead code, bundle size, and security.
metadata:
  category: development
  source: 'antigravity-awesome-skills (MIT)'
  triggers:
  - js node refactor
  - javascript performance optimization
  - node.js memory leak detection
  - n+1 query pattern
  - bundle size optimization
eval_cases:
- id: js-refactor-event-loop
  prompt: How do I detect and fix event loop blocking in Node.js?
  should_trigger: true
  checks:
  - length_min:150
  - no_placeholder
  expectations:
  - Identifies sync operations in async context
  - Explains detection methods (benchmarks, async_hooks)
  - Provides non-blocking alternatives
  tags:
  - javascript
  - nodejs
  - event-loop
- id: js-refactor-memory-leaks
  prompt: What are common memory leak patterns in Node.js and how do I fix them?
  should_trigger: true
  checks:
  - length_min:150
  - no_placeholder
  expectations:
  - Lists closure, timer, and event listener issues
  - Shows heap snapshot analysis approach
  - Provides remediation patterns
  tags:
  - javascript
  - nodejs
  - memory-leak
  - performance
- id: js-refactor-n-plus-1
  prompt: How do I identify and fix N+1 query patterns with Prisma/Sequelize/Knex?
  should_trigger: true
  checks:
  - length_min:120
  - no_placeholder
  expectations:
  - Explains N+1 detection in ORM context
  - Shows eager loading / include patterns
  - Demonstrates batched queries as alternative
  tags:
  - javascript
  - nodejs
  - orm
  - n-plus-1
  - database
- id: js-refactor-bundle-perf
  prompt: How do I reduce bundle size and improve load performance in a JS app?
  should_trigger: true
  checks:
  - length_min:120
  - no_placeholder
  expectations:
  - Covers tree shaking, dynamic imports, code splitting
  - Mentions bundle analysis tools
  - Addresses dead code elimination
  tags:
  - javascript
  - bundle-size
  - performance
  - webpack
  - vite
---

# JavaScript/Node.js Refactoring & Performance Optimization

## Table of Contents

1. [Event Loop Blocking Detection](#1-event-loop-blocking-detection)
2. [Memory Leak Patterns](#2-memory-leak-patterns)
3. [N+1 Query Patterns in ORMs](#3-n1-query-patterns-in-orms)
4. [Promise.all vs Sequential Awaits](#4-promiseall-vs-sequential-awaits)
5. [Stream Processing](#5-stream-processing)
6. [Dead Code Elimination](#6-dead-code-elimination)
7. [Bundle Size Optimization](#7-bundle-size-optimization)
8. [ESLint --fix Patterns](#8-eslint---fix-patterns)
9. [Unused Dependencies](#9-unused-dependencies)
10. [Security Pitfalls](#10-security-pitfalls)
11. [CommonJS to ESM Migration](#11-commonjs-to-esm-migration)

---

## 1. Event Loop Blocking Detection

### The Problem

Node.js runs on a single-threaded event loop. Synchronous blocking operations freeze the entire process, degrading throughput.

### Detection

```bash
# Baseline throughput measurement
node -e "
  const http = require('http');
  const server = http.createServer((req, res) => {
    const start = Date.now();
    // simulate work
    let sum = 0;
    for (let i = 0; i < 1e7; i++) sum += i;
    res.end('OK ' + (Date.now() - start) + 'ms');
  });
  server.listen(3000);
"

# Use clinic.js for flame graphs
npx clinic doctor -- node server.js

# Use async_hooks for tracing
node --require async_hooks/trace server.js
```

### Antipattern: Sync in Async

```javascript
// BAD: Blocking the event loop
app.get('/slow', async (req, res) => {
  const data = fs.readFileSync('/large-file.txt'); // BLOCKS
  const result = heavyComputation(data);
  res.json(result);
});

// GOOD: Non-blocking alternatives
app.get('/slow', async (req, res) => {
  const data = await fs.promises.readFile('/large-file.txt');
  const result = await computeInWorker(data); // Worker thread
  res.json(result);
});
```

### Offload Heavy Work to Worker Threads

```javascript
const { Worker } = require('worker_threads');

function runInWorker(workerPath, data) {
  return new Promise((resolve, reject) => {
    const worker = new Worker(workerPath, { workerData: data });
    worker.on('message', resolve);
    worker.on('error', reject);
    worker.on('exit', (code) => {
      if (code !== 0) reject(new Error(`Worker stopped with exit code ${code}`));
    });
  });
}
```

### Patterns to Avoid

| Blocking Call | Non-blocking Alternative |
|---------------|---------------------------|
| `fs.readFileSync` | `fs.promises.readFile` |
| `JSON.parse(str)` (large) | `JSON.parse(str)` in Worker |
| `for/while` loops > 1ms | `setImmediate` chunking |
| `crypto.pbkdf2Sync` | `crypto.promises.pbkdf2` |
| `require()` large modules at runtime | Dynamic `import()` |

---

## 2. Memory Leak Patterns

### 2.1 Closures Holding References

```javascript
// LEAK: Closure captures large object
function createHandler() {
  const largeData = Buffer.alloc(1e8); // 100MB
  return function handler(req, res) {
    // largeData is retained even when handler is "done"
    res.send('done');
  };
}

// FIX: Release references when done
function createHandler() {
  const largeData = Buffer.alloc(1e8);
  return function handler(req, res) {
    try {
      res.send('done');
    } finally {
      largeData = null; // Allow GC
    }
  };
}
```

### 2.2 Timers Not Cleared

```javascript
// LEAK: Interval never cleared
function startPolling() {
  setInterval(() => {
    fetchData();
  }, 1000);
  // Returns nothing, interval keeps running
}

// FIX: Return cleanup function
function startPolling() {
  const id = setInterval(() => fetchData(), 1000);
  return () => clearInterval(id); // Call on cleanup
}

// Usage
const stop = startPolling();
// When done
stop();
```

### 2.3 Event Listeners Not Removed

```javascript
// LEAK: Listeners accumulate
server.on('connection', (socket) => {
  socket.on('data', handleData);
});

// FIX: Remove listener when done
function handleConnection(socket) {
  socket.on('data', handleData);
  socket.once('close', () => {
    socket.removeListener('data', handleData);
  });
}
```

### Detection with Heap Snapshots

```bash
# Take heap snapshot
kill -USR2 <node-pid>
# Or use v8-profiler
node --prof server.js
node --prof-process isolate-*.log > profile.txt

# Use Chrome DevTools
# 1. Enable DEBUG mode
node --inspect server.js
# 2. Open chrome://inspect, load Heap Snapshot
```

---

## 3. N+1 Query Patterns in ORMs

### 3.1 Prisma

```typescript
// N+1: fetches users, then N queries for each post
const users = await prisma.user.findMany();
for (const user of users) {
  user.posts = await prisma.post.findMany({ where: { userId: user.id } });
}

// FIX: Use include
const users = await prisma.user.findMany({
  include: { posts: true },
});
```

### 3.2 Sequelize

```javascript
// N+1
const users = await User.findAll();
for (const user of users) {
  user.posts = await user.getPosts();
}

// FIX: Eager loading
const users = await User.findAll({
  include: [{ model: Post, as: 'posts' }],
});
```

### 3.3 Knex

```javascript
// N+1
const users = await knex('users').select('*');
for (const user of users) {
  user.projects = await knex('projects').where('user_id', user.id);
}

// FIX: Join or batch
const users = await knex('users')
  .select('users.*', 'projects.name as project_name')
  .leftJoin('projects', 'users.id', 'projects.user_id');

// Or use withFetch and groupBy in application
```

### Batch/Chunk Queries for Large Datasets

```typescript
async function getUsersWithPosts(userIds: number[]) {
  const batchSize = 100;
  const results = [];
  for (let i = 0; i < userIds.length; i += batchSize) {
    const batch = userIds.slice(i, i + batchSize);
    const posts = await prisma.post.findMany({
      where: { userId: { in: batch } },
    });
    results.push(...posts);
  }
  return results;
}
```

---

## 4. Promise.all vs Sequential Awaits

### Sequential When Dependencies Exist

```javascript
// BAD: Unnecessary latency
const user = await fetchUser(id);
const profile = await fetchProfile(user.profileId); // depends on user
const settings = await fetchSettings(user.settingId); // depends on user

// Total: t1 + t2 + t3

// GOOD: Parallel when possible
const [user, profile, settings] = await Promise.all([
  fetchUser(id),
  fetchProfile(user.profileId),
  fetchSettings(user.settingId),
]);
```

### Sequential When Order Matters

```javascript
// Must wait for first to complete before second
await initializeDatabase();
await runMigrations();
```

### Mixed: Parallel with Sequential Groups

```javascript
// Group 1: parallel (no dependencies)
const [config, cache] = await Promise.all([
  loadConfig(),
  initCache(),
]);

// Group 2: sequential (depends on group 1)
await validateConfig(config);
await warmCache(cache);
```

### Error Handling

```javascript
// ALL SETTLED: Never rejects
const results = await Promise.allSettled([
  fetchResource('a'),
  fetchResource('b'),
  fetchResource('c'),
]);

results.forEach((result) => {
  if (result.status === 'fulfilled') {
    console.log('Got:', result.value);
  } else {
    console.error('Failed:', result.reason);
  }
});
```

---

## 5. Stream Processing

### Problem: Loading Entire File

```javascript
// BAD: Loads entire 5GB file into memory
const data = await fs.promises.readFile('/huge-file.csv');
const lines = data.toString().split('\n');
```

### Solution: Stream Processing

```javascript
import { createReadStream } from 'fs';
import { parse } from 'csv-parse';

async function processLargeCSV(filePath) {
  return new Promise((resolve, reject) => {
    const results = [];
    createReadStream(filePath)
      .pipe(parse({ columns: true }))
      .on('data', (row) => {
        // Process row by row, memory stays constant
        results.push(transform(row));
      })
      .on('end', () => resolve(results))
      .on('error', reject);
  });
}
```

### Backpressure Handling

```javascript
const { Transform } = require('stream');

class BatchTransform extends Transform {
  constructor(batchSize = 100) {
    super({ objectMode: true });
    this.batchSize = batchSize;
    this.batch = [];
  }

  _transform(row, enc, cb) {
    this.batch.push(row);
    if (this.batch.length >= this.batchSize) {
      this.push(this.processBatch(this.batch));
      this.batch = [];
    }
    cb();
  }

  _flush(cb) {
    if (this.batch.length > 0) {
      this.push(this.processBatch(this.batch));
    }
    cb();
  }

  processBatch(rows) {
    return rows.map(transform);
  }
}
```

### HTTP Streams

```javascript
// Streaming response to client
const { createReadStream } = require('fs');

app.get('/download', (req, res) => {
  res.setHeader('Content-Type', 'application/octet-stream');
  createReadStream('/large-file.zip').pipe(res);
});
```

---

## 6. Dead Code Elimination

### 6.1 Unused Exports

```javascript
// exports that are never imported elsewhere
module.exports = { unusedHelper, AnotherUnused };

// Detection
npx depcheck ./project
# or
npm run build 2>&1 | grep "is defined but never used"
```

### 6.2 Unreachable Branches

```javascript
// Always true/false conditions
if (process.env.NODE_ENV === 'development') {
  // This branch is only for dev
} else {
  // Production branch - but may have dead code after refactor
}

// After build-time elimination (terser/webpack)
if (false) {
  // This code is DEAD
}
```

### 6.3 Barrel File Bloat

```javascript
// index.ts - imports EVERYTHING even if only one is used
export { UserService } from './UserService';
export { ProductService } from './ProductService';
export { OrderService } from './OrderService';
// ... 50 more

// FIX: Import directly
import { UserService } from './services/UserService';
```

### Automated Dead Code Detection

```bash
# ESLint unused vars
npx eslint . --no-eslintrc --rule '{"no-unused-vars":"warn"}'

# TypeScript unused
npx tsc --noEmit --reportUnusedLocals

# Webpack bundle analysis
npx webpack-bundle-analyzer dist/stats.json
```

---

## 7. Bundle Size Optimization

### Tree Shaking

```javascript
// BAD: Imports entire lodash
import _ from 'lodash';
const arr = _.flattenDeep(nested);

// GOOD: Named imports (tree-shakeable)
import { flattenDeep } from 'lodash-es';
const arr = flattenDeep(nested);

// BEST: Native or specialized
const arr = nested.flat(Infinity);
```

### Dynamic Imports (Code Splitting)

```javascript
// Lazy load heavy feature
const HeavyChart = React.lazy(() => import('./HeavyChart'));

// Or route-based splitting (React Router)
<Route path="/dashboard" component={lazy(() => import('./Dashboard'))} />

// Node.js dynamic import
const { heavyFunc } = await import('./heavy-module.js');
```

### Vite Configuration

```javascript
// vite.config.js
export default {
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          utils: ['lodash-es', 'date-fns'],
        },
      },
    },
    chunkSizeWarningLimit: 500, // KB
  },
};
```

### Bundle Analysis

```bash
npx vite-bundle-visualizer
# or
npx webpack-bundle-analyzer dist/bundle-stats.json
```

### Code Splitting Strategies

| Strategy | Use Case |
|----------|----------|
| Route-based | Different pages/routes |
| Vendor | Third-party libs (rarely change) |
| Feature | Lazy load optional features |
| Dynamic | Runtime conditional execution |

---

## 8. ESLint --fix Patterns

### Auto-fixable Rules

```bash
# Fix all auto-fixable issues
npx eslint . --fix

# Fix specific rules
npx eslint . --fix --rule 'no-unused-vars: error'

# List auto-fixable rules
npx eslint --print-config . | jq '.rules[] | select(.fix) | key'
```

### Common Auto-fixable Patterns

```javascript
// no-unused-vars: "off" | "warn" | "error"
// Removes declared but unused variables

// semi: ["error", "always"] | ["error", "never"]
// Adds or removes semicolons

// quotes: ["error", "single"] | ["error", "double"]
// Normalizes quote style

// comma-dangle: ["error", "always-multiline"]
// Adds trailing commas

// indent: Error -> consistent indentation
// Adds/removes indentation

// no-trailing-spaces: Error
// Removes trailing whitespace
```

### Prettier Integration

```bash
# Run prettier first, then eslint --fix
npx prettier --write . && npx eslint . --fix
```

### eslint.config.js

```javascript
import js from '@eslint/js';
import globals from 'globals';

export default [
  js.configs.recommended,
  {
    files: ['**/*.js'],
    languageOptions: {
      globals: {
        ...globals.node,
        ...globals.es2021,
      },
    },
    rules: {
      'no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
      'no-console': 'warn',
      'prefer-const': 'error',
      'object-shorthand': 'error',
    },
  },
];
```

---

## 9. Unused Dependencies

### Detection

```bash
# Find unused deps
npx depcheck

# Or npm
npm prune --dry-run

# pnpm
pnpm prune --dry-run

# Check for missing deps
npx syncpack list-mismatches
```

### Cleanup Process

```bash
# 1. Run depcheck
npx depcheck

# 2. Review and remove from package.json
npm uninstall <unused-package>

# 3. Verify no runtime errors
npm run test

# 4. Update lockfile
npm install
```

### pnpm Workspace Cleanup

```bash
# Remove unused from workspace
pnpm prune

# List all deps
pnpm list --depth 0
```

---

## 10. Security Pitfalls

### 10.1 eval()

```javascript
// DANGEROUS: Arbitrary code execution
const userInput = req.body.code;
const result = eval(userInput); // NEVER do this

// FIX: Use safer alternatives
const vm = require('vm');
const result = vm.runInNewContext(userInput, { console, Math, ... });
// Or for math: use mathjs library
```

### 10.2 innerHTML / DOM XSS

```javascript
// DANGEROUS
element.innerHTML = userInput; // XSS vector

// SAFE
element.textContent = userInput;
// Or sanitize first
import DOMPurify from 'dompurify';
element.innerHTML = DOMPurify.sanitize(userInput);
```

### 10.3 Prototype Pollution

```javascript
// DANGEROUS: Merge user object into prototype
const payload = JSON.parse('{"__proto__": {"admin": true}}');
Object.assign(target, payload);

// FIX: Validate keys
const safeMerge = (target, source) => {
  for (const key of Object.keys(source)) {
    if (key === '__proto__' || key === 'constructor' || key === 'prototype') {
      throw new Error('Invalid key');
    }
    target[key] = source[key];
  }
  return target;
};
```

### 10.4 ReDoS (Regular Expression DoS)

```javascript
// DANGEROUS: Catastrophic backtracking
const regex = /^(\w+)+$/;

// SAFE: Use anchors, avoid nested quantifiers
const regex = /^\w+$/;
// Or use library like safe-regex
```

### Security Checklist

- [ ] Never use `eval()` or `new Function()`
- [ ] Sanitize HTML with DOMPurify before innerHTML
- [ ] Validate and block prototype pollution keys
- [ ] Use safe-regex to validate regex patterns
- [ ] Scan dependencies for vulnerabilities: `npm audit`

---

## 11. CommonJS to ESM Migration

### Key Differences

| CommonJS | ESM |
|----------|-----|
| `module.exports` | `export default` / `export` |
| `require()` | `import` |
| `__dirname` | `import.meta.url` |
| `require.resolve()` | `import.meta.resolve()` |
| Synchronous require | Top-level await, async import() |

### Basic Migration

```javascript
// CJS: const/index.js
const express = require('express');
const { helper } = require('./utils');
module.exports = { app: express(), helper };

// ESM: const/index.mjs
import express from 'express';
import { helper } from './utils.js'; // Note .js extension
const app = express();
export { app, helper };
// or
export default { app, helper };
```

### package.json Type Field

```json
{
  "type": "module"
}
```

### Dynamic Imports

```javascript
// CJS
const lodash = require('lodash');

// ESM
import lodash from 'lodash'; // static
// or
const lodash = await import('lodash'); // dynamic
```

### __dirname / __filename Replacement

```javascript
// CJS
const path = require('path');
console.log(__dirname);

// ESM
import { fileURLToPath } from 'url';
import { dirname } from 'path';
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
```

### Testing ESM Migration

```bash
# Check for CJS patterns
npx is-esm ./src --verbose

# Verify with node --experimental-modules
node --input-type=module --check <file>
```

---

## Quick Reference Commands

```bash
# Format and lint
npx prettier --write . && npx eslint . --fix

# Type check
npx tsc --noEmit

# Bundle analysis
npx vite-bundle-visualizer 2>/dev/null || npx webpack-bundle-analyzer dist/stats.json

# Dependency audit
npm audit
npx depcheck

# Performance profiling
npx clinic doctor -- node server.js
npx autocannon http://localhost:3000

# Memory leak detection
node --expose-gc --inspect server.js
# Then Chrome DevTools heap snapshots
```
