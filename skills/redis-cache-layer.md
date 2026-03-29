---
name: redis-cache-layer
description: Redis caching layer skill for gRPC services covering patterns, serialization, invalidation, and cluster strategies
category: gRPC
tags: [redis, cache, grpc, performance, distributed-systems]
version: 1.0.0
eval_cases:
  - id: cache_aside_basic
    description: Implement cache-aside pattern correctly
    prompt: "Write Rust code for cache-aside pattern: check cache first, on miss fetch from DB and populate cache with TTL. Handle errors gracefully."
    expected: "async fn get_entity<T: DeserializeOwned>(&self, key: &str) -> Result<Option<T>> with cache.fetch().await then db.read().await and cache.insert().await"

  - id: cache_key_design
    description: Design cache keys following tenant:entity:id pattern
    prompt: "Create a Rust function build_cache_key(tenant_id: &str, entity_type: &str, entity_id: &str) -> String that returns tenant:entity:id format"
    expected: "String in format '{tenant}:{entity}:{id}' with proper escaping of colons in values"

  - id: ttl_strategy
    description: Define TTL strategy per entity type
    prompt: "Define a Rust enum EntityType with User(300), Product(3600), Order(600), Config(86400) representing TTL in seconds"
    expected: "pub enum EntityType { User(u64), Product(u64), Order(u64), Config(u64) } with associated TTL values"

  - id: protobuf_serialization
    description: Use protobuf serialization instead of JSON
    prompt: "Write Rust code to serialize a proto message to bytes using prost and deserialize using Message::decode"
    expected: "let bytes = Message::encode_to_vec(&proto); let proto = ProtoMessage::decode(bytes.as_slice())?"

  - id: connection_pooling
    description: Configure connection pool with dead connection detection
    prompt: "Configure redis::aio::ConnectionManager with pool size 32 and detect dead connections on use"
    expected: "ConnectionManager with tokio::sync::Semaphore for limiting connections and reconnection logic"

  - id: circuit_breaker
    description: Implement circuit breaker on Redis failure
    prompt: "Implement circuit breaker pattern: open after 5 failures in 10s window, half-open after 30s, close on success"
    expected: "enum State { Closed, Open, HalfOpen } with failure_count, last_failure_time, and transition logic"

  - id: write_through_invalidation
    description: Implement write-through cache invalidation
    prompt: "Write a Rust function invalidate_on_write(tenant: &str, entity: &str, id: &str) that deletes cache key on entity update"
    expected: "async fn invalidate(key: &str) -> Result<()> with redis::cmd(\"DEL\").arg(key).query_async(&mut conn).await"

  - id: cache_warming
    description: Implement cache warming for hot entities
    prompt: "Write a function warm_cache(tenant_id: &str, entity_ids: Vec<&str>) that prefetches entities from DB and populates cache"
    expected: "async fn warm_cache<T: Deserialize + Message>(...) with futures::future::join_all for batch fetching"

  - id: cache_metrics
    description: Track hit/miss ratio with Prometheus metrics
    prompt: "Add Prometheus counters cache_hits_total and cache_misses_total and compute hit_ratio"
    expected: "counter!(cache_hits_total, tenant = tenant_id, entity = entity_type); histogram!(cache_latency_seconds)"

  - id: redis_cluster
    description: Use Redis Cluster for distributed cache
    prompt: "Configure redis::cluster::ClusterClient for distributed caching across 3 nodes"
    expected: "ClusterClient::new(vec![\"redis://node1:6379\", \"redis://node2:6379\", \"redis://node3:6379\"])"

  - id: lazy_invalidation
    description: Implement lazy cache invalidation
    prompt: "Write a function refresh_on_write that updates cache after DB write completes (lazy refresh)"
    expected: "async fn refresh(key: &str, entity: &T) -> Result<()> with SETEX after successful DB write"

  - id: distributed_lock
    description: Use distributed lock for cache stampede prevention
    prompt: "Implement SETNX-based lock for preventing cache stampede on thundering herd"
    expected: "let acquired = redis::cmd(\"SET\").arg(key_lock).arg(1).nx().ex(5).query_async::<_, bool>(&mut conn).await; if acquired { fetch_and_cache().await; redis::cmd(\"DEL\").arg(key_lock) }"

triggers:
  - pattern: "redis cache"
    skill: redis-cache-layer
  - pattern: "cache-aside"
    skill: redis-cache-layer
  - pattern: "cache invalidation"
    skill: redis-cache-layer
  - pattern: "redis cluster"
    skill: redis-cache-layer
  - pattern: "cache warming"
    skill: redis-cache-layer
  - pattern: "circuit breaker redis"
    skill: redis-cache-layer
---

# Redis Cache Layer for gRPC Services

## Overview

Redis serves as the primary caching layer for gRPC services in this monorepo. It provides low-latency data access, reduces database load, and enables horizontal scaling of cache capacity via Redis Cluster.

## Cache-Aside Pattern (Read-Through)

The cache-aside pattern is the primary read strategy:

1. Application checks cache for requested key
2. On cache **hit**: return cached value immediately
3. On cache **miss**: fetch from persistent store, populate cache with TTL, return value

```rust
pub async fn get_entity<T: Message + Default + DeserializeOwned>(
    cache: &CacheLayer,
    db: &DbPool,
    tenant: &str,
    entity_type: EntityType,
    id: &str,
) -> Result<Option<T>> {
    let key = build_cache_key(tenant, entity_type.name(), id);
    
    if let Some(bytes) = cache.get(&key).await? {
        increment_counter!("cache_hits_total", "tenant" => tenant, "entity" => entity_type.name());
        let entity = T::decode(bytes.as_slice())?;
        return Ok(Some(entity));
    }
    
    increment_counter!("cache_misses_total", "tenant" => tenant, "entity" => entity_type.name());
    
    let entity = db.fetch_entity(entity_type.table(), id).await?;
    
    if let Some(ref e) = entity {
        let bytes = Message::encode_to_vec(e);
        cache.set(&key, bytes, entity_type.ttl()).await?;
    }
    
    Ok(entity)
}
```

## Cache Key Design

### Naming Convention

```
{tenant}:{entity}:{id}
```

- **tenant**: Customer/namespace identifier (e.g., `acme-corp`)
- **entity**: Entity type in plural (e.g., `users`, `orders`, `products`)
- **id**: Entity UUID or primary key

### Key Prefixing

Use key prefixes for operational convenience:

```
cache:tenant:acme-corp:users:550e8400-e29b-41d4-a716-446655440000
```

### Rust Implementation

```rust
pub fn build_cache_key(tenant: &str, entity: &str, id: &str) -> String {
    format!("cache:tenant:{}:{}:{}", escape_key(tenant), entity, id)
}

fn escape_key(s: &str) -> String {
    s.replace(':', "\\:")
}

pub fn parse_cache_key(key: &str) -> Option<(String, String, String)> {
    let parts: Vec<&str> = key.split(':').collect();
    if parts.len() >= 5 && parts[0] == "cache" && parts[1] == "tenant" {
        Some((parts[2].to_string(), parts[3].to_string(), parts[4].to_string()))
    } else {
        None
    }
}
```

## TTL Strategy Per Entity Type

| Entity Type | TTL | Rationale |
|-------------|-----|-----------|
| User | 300s (5 min) | Frequent updates, moderate staleness tolerance |
| Product | 3600s (1 hr) | Catalog rarely changes, high read volume |
| Order | 600s (10 min) | Status changes frequently, low tolerance for stale data |
| Config | 86400s (24 hr) | Near-static, manually invalidated on change |
| Session | 1800s (30 min) | Must align with auth token expiry |
| RateLimit | 60s (1 min) | Short-lived, precise counting required |

```rust
#[derive(Clone, Copy)]
pub enum EntityType {
    User,
    Product,
    Order,
    Config,
    Session,
    RateLimit,
}

impl EntityType {
    pub fn name(&self) -> &'static str {
        match self {
            EntityType::User => "users",
            EntityType::Product => "products",
            EntityType::Order => "orders",
            EntityType::Config => "configs",
            EntityType::Session => "sessions",
            EntityType::RateLimit => "rate_limits",
        }
    }
    
    pub fn ttl_seconds(&self) -> u64 {
        match self {
            EntityType::User => 300,
            EntityType::Product => 3600,
            EntityType::Order => 600,
            EntityType::Config => 86400,
            EntityType::Session => 1800,
            EntityType::RateLimit => 60,
        }
    }
    
    pub fn table(&self) -> &'static str {
        match self {
            EntityType::User => "users",
            EntityType::Product => "products",
            EntityType::Order => "orders",
            EntityType::Config => "configs",
            EntityType::Session => "sessions",
            EntityType::RateLimit => "rate_limits",
        }
    }
}
```

## Cache Invalidation Strategies

### Write-Through Invalidation

Invalidate cache immediately before or after database write. Use for **high-consistency** requirements.

```rust
pub async fn update_entity<T: Message>(
    cache: &CacheLayer,
    db: &DbPool,
    tenant: &str,
    entity_type: EntityType,
    id: &str,
    updates: T,
) -> Result<()> {
    let key = build_cache_key(tenant, entity_type.name(), id);
    
    // Write to database
    db.update_entity(entity_type.table(), id, &updates).await?;
    
    // Invalidate cache (lazy approach: next read fetches fresh data)
    cache.delete(&key).await?;
    
    Ok(())
}
```

### Lazy Refresh (Refresh-Aside)

Update cache after successful DB write. Use when **cache population is expensive**.

```rust
pub async fn update_and_refresh<T: Message>(
    cache: &CacheLayer,
    db: &DbPool,
    tenant: &str,
    entity_type: EntityType,
    id: &str,
    updates: T,
) -> Result<()> {
    let key = build_cache_key(tenant, entity_type.name(), id);
    
    db.update_entity(entity_type.table(), id, &updates).await?;
    
    // Refresh cache with new value
    let bytes = Message::encode_to_vec(&updates);
    cache.set(&key, bytes, entity_type.ttl()).await?;
    
    Ok(())
}
```

### Bulk Invalidation

```rust
pub async fn invalidate_entity_pattern(
    cache: &CacheLayer,
    tenant: &str,
    entity_type: EntityType,
) -> Result<u64> {
    let pattern = format!("cache:tenant:{}:{}:*", escape_key(tenant), entity_type.name());
    let mut cursor = 0u64;
    let mut total_deleted = 0u64;
    
    loop {
        let (new_cursor, keys): (u64, Vec<String>) = redis::cmd("SCAN")
            .arg(cursor)
            .arg("MATCH", &pattern)
            .arg("COUNT", 100)
            .query_async(&mut cache.conn())
            .await?;
        
        if !keys.is_empty() {
            let deleted: u64 = redis::cmd("DEL")
                .arg(&keys)
                .query_async(&mut cache.conn())
                .await?;
            total_deleted += deleted;
        }
        
        cursor = new_cursor;
        if cursor == 0 {
            break;
        }
    }
    
    Ok(total_deleted)
}
```

## Binary Serialization

### Protobuf (Recommended for gRPC)

```rust
use prost::Message;

pub fn serialize_proto<T: Message>(entity: &T) -> Vec<u8> {
    Message::encode_to_vec(entity)
}

pub fn deserialize_proto<T: Message + Default>(bytes: &[u8]) -> Result<T> {
    T::decode(bytes).map_err(|e| CacheError::Deserialize(e.to_string()))
}

pub async fn cache_get_proto<T: Message + Default>(
    cache: &CacheLayer,
    key: &str,
) -> Result<Option<T>> {
    match cache.get_raw(key).await? {
        Some(bytes) => Ok(Some(deserialize_proto(&bytes)?)),
        None => Ok(None),
    }
}
```

### MessagePack (Alternative)

```rust
use rmp_serde::{encode::Serializer, decode::Deserializer};
use serde::{Deserialize, Serialize};

pub fn serialize_msgpack<T: Serialize>(entity: &T) -> Result<Vec<u8>> {
    let mut buf = Vec::new();
    entity.serialize(&mut Serializer::new(&mut buf))
        .map_err(|e| CacheError::Serialize(e.to_string()))?;
    Ok(buf)
}

pub fn deserialize_msgpack<T: DeserializeOwned>(bytes: &[u8]) -> Result<T> {
    let mut de = Deserializer::new(bytes);
    Deserialize::deserialize(&mut de)
        .map_err(|e| CacheError::Deserialize(e.to_string()))
}
```

### Comparison

| Format | Size | Speed | Schema Evolution | gRPC Native |
|--------|------|-------|------------------|-------------|
| Protobuf | Small | Fast | Yes | Yes |
| MessagePack | Medium | Fast | Limited | No |
| JSON | Large | Medium | Yes | No |

## Connection Pooling

### Connection Manager with Pool Limits

```rust
use redis::{aio::ConnectionManager, Client};
use tokio::sync::Semaphore;

pub struct CacheLayer {
    conn: ConnectionManager,
    semaphore: Arc<Semaphore>,
    pool_size: usize,
}

impl CacheLayer {
    pub async fn new(redis_url: &str, pool_size: usize) -> Result<Self> {
        let client = Client::open(redis_url)?;
        let conn = ConnectionManager::new(client).await?;
        
        Ok(Self {
            conn,
            semaphore: Arc::new(Semaphore::new(pool_size)),
            pool_size,
        })
    }
    
    pub async fn get(&self, key: &str) -> Result<Option<Vec<u8>>> {
        let _permit = self.semaphore.acquire().await?;
        
        let mut conn = self.conn.clone();
        redis::cmd("GET")
            .arg(key)
            .query_async::<_, Option<Vec<u8>>>(&mut conn)
            .await
            .map_err(Into::into)
    }
    
    pub async fn set(&self, key: &str, value: Vec<u8>, ttl_seconds: u64) -> Result<()> {
        let _permit = self.semaphore.acquire().await?;
        
        let mut conn = self.conn.clone();
        redis::cmd("SETEX")
            .arg(key)
            .arg(ttl_seconds)
            .arg(value)
            .query_async::<_, ()>(&mut conn)
            .await
            .map_err(Into::into)
    }
}
```

### Dead Connection Detection

```rust
impl CacheLayer {
    pub async fn get_safe(&self, key: &str) -> Result<Option<Vec<u8>>> {
        let result = self.get(key).await;
        
        match result {
            Ok(v) => Ok(v),
            Err(CacheError::Redis(ref e)) if is_connection_error(e) => {
                // Reconnect and retry once
                self.reconnect().await?;
                self.get(key).await
            }
            Err(e) => Err(e),
        }
    }
    
    fn is_connection_error(e: &redis::RedisError) -> bool {
        matches!(e.kind(), 
            redis::ErrorKind::IoError | 
            redis::ErrorKind::ResponseError |
            redis::ErrorKind::ClusterDown
        )
    }
}
```

## Circuit Breaker on Redis Failure

```rust
use std::time::{Duration, Instant};
use tokio::sync::Mutex;

#[derive(Clone)]
pub struct CircuitBreaker {
    state: Arc<Mutex<CircuitState>>,
    failure_threshold: u32,
    recovery_timeout: Duration,
}

#[derive(Clone, Debug, PartialEq)]
pub enum CircuitState {
    Closed,
    Open,
    HalfOpen,
}

#[derive(Debug)]
pub struct CircuitBreakerConfig {
    pub failure_threshold: u32,  // Open after N failures
    pub recovery_timeout: Duration,  // Try half-open after this duration
}

impl CircuitBreaker {
    pub fn new(config: CircuitBreakerConfig) -> Self {
        Self {
            state: Arc::new(Mutex::new(CircuitState::Closed)),
            failure_threshold: config.failure_threshold,
            recovery_timeout: config.recovery_timeout,
        }
    }
    
    pub async fn is_allowed(&self) -> bool {
        let state = self.state.lock().await;
        match &*state {
            CircuitState::Closed => true,
            CircuitState::Open { last_failure, failures } => {
                if failures >= &self.failure_threshold {
                    if last_failure.elapsed() >= self.recovery_timeout {
                        drop(state);
                        *self.state.lock().await = CircuitState::HalfOpen;
                        true
                    } else {
                        false
                    }
                } else {
                    true
                }
            }
            CircuitState::HalfOpen => true,
        }
    }
    
    pub async fn record_success(&self) {
        *self.state.lock().await = CircuitState::Closed;
    }
    
    pub async fn record_failure(&self) {
        let mut state = self.state.lock().await;
        match &mut *state {
            CircuitState::Closed => {
                *state = CircuitState::Open { 
                    last_failure: Instant::now(), 
                    failures: 1 
                };
            }
            CircuitState::HalfOpen => {
                *state = CircuitState::Open { 
                    last_failure: Instant::now(), 
                    failures: self.failure_threshold 
                };
            }
            CircuitState::Open { failures, .. } => {
                *failures += 1;
            }
        }
    }
}

pub async fn execute_with_circuit_breaker<T, F, Fut>(
    breaker: &CircuitBreaker,
    operation: F,
    fallback: impl FnOnce() -> Fut,
) -> Result<T>
where
    F: FnOnce() -> Fut,
    Fut: std::future::Future<Output = Result<T>>,
{
    if !breaker.is_allowed().await {
        return fallback().await;
    }
    
    match operation().await {
        Ok(v) => {
            breaker.record_success().await;
            Ok(v)
        }
        Err(e) => {
            breaker.record_failure().await;
            Err(e)
        }
    }
}
```

### Usage with Cache Layer

```rust
impl CacheLayer {
    pub async fn get_with_breaker<T: Message + Default>(
        &self,
        key: &str,
    ) -> Result<Option<T>> {
        execute_with_circuit_breaker(
            &self.circuit_breaker,
            || self.get_proto(key),
            || async { Ok(None) },  // Fallback: bypass cache on Redis failure
        )
        .await
    }
}
```

## Cache Warming

### Startup Warming

```rust
pub async fn warm_cache_batch<T: Message + Default + Clone>(
    cache: &CacheLayer,
    db: &DbPool,
    tenant: &str,
    entity_type: EntityType,
    ids: Vec<String>,
) -> Result<CacheWarmResult> {
    let key_prefix = format!("cache:tenant:{}:{}", escape_key(tenant), entity_type.name());
    
    let tasks: Vec<_> = ids.iter().map(|id| {
        let db = db.clone();
        let key = format!("{}:{}", key_prefix, id);
        async move {
            if let Some(entity) = db.fetch_by_id(entity_type.table(), id).await? {
                let bytes = Message::encode_to_vec(&entity);
                Ok((key, bytes))
            } else {
                Err(CacheError::NotFound)
            }
        }
    }).collect();
    
    let results = futures::future::join_all(tasks).await;
    let mut warmed = 0u64;
    let mut failed = 0u64;
    
    for result in results {
        match result {
            Ok((key, bytes)) => {
                if cache.set(&key, bytes, entity_type.ttl_seconds()).await.is_ok() {
                    warmed += 1;
                } else {
                    failed += 1;
                }
            }
            Err(_) => failed += 1,
        }
    }
    
    Ok(CacheWarmResult { warmed, failed })
}

#[derive(Debug)]
pub struct CacheWarmResult {
    pub warmed: u64,
    pub failed: u64,
}
```

### Hot Data Prioritization

```rust
pub async fn warm_hot_entities(
    cache: &CacheLayer,
    db: &DbPool,
    tenant: &str,
) -> Result<()> {
    // Top 100 most-accessed products
    let hot_products = db.fetch_hot_entity_ids("products", "access_count", 100).await?;
    warm_cache_batch(cache, db, tenant, EntityType::Product, hot_products).await?;
    
    // Active users (logged in within last hour)
    let active_users = db.fetch_active_user_ids(Duration::from_hours(1)).await?;
    warm_cache_batch(cache, db, tenant, EntityType::User, active_users).await?;
    
    Ok(())
}
```

## Cache Metrics

### Prometheus Metrics

```rust
use prometheus::{Counter, Histogram, Gauge, Registry};

pub struct CacheMetrics {
    hits: CounterVec,
    misses: CounterVec,
    latency: HistogramVec,
    errors: CounterVec,
    circuit_breaker_state: GaugeVec,
}

impl CacheMetrics {
    pub fn new(registry: &Registry) -> Self {
        let hits = CounterVec::new(
            OptStrings::new("cache_hits_total"),
            &["tenant", "entity", "result"],
            registry,
        ).unwrap();
        
        let misses = CounterVec::new(
            OptStrings::new("cache_misses_total"),
            &["tenant", "entity"],
            registry,
        ).unwrap();
        
        let latency = HistogramVec::new(
            OptStrings::new("cache_operation_duration_seconds"),
            &["operation"],
            registry,
        ).unwrap();
        
        let errors = CounterVec::new(
            OptStrings::new("cache_errors_total"),
            &["tenant", "entity", "error_type"],
            registry,
        ).unwrap();
        
        let circuit_breaker_state = GaugeVec::new(
            OptStrings::new("cache_circuit_breaker_state"),
            &["cache_layer"],
            registry,
        ).unwrap();
        
        Self { hits, misses, latency, errors, circuit_breaker_state }
    }
    
    pub fn record_hit(&self, tenant: &str, entity: &str, found: bool) {
        self.hits.with_label_values(&[tenant, entity, if found { "found" } else { "not_found" }]).inc();
    }
    
    pub fn record_miss(&self, tenant: &str, entity: &str) {
        self.misses.with_label_values(&[tenant, entity]).inc();
    }
    
    pub fn record_latency(&self, operation: &str, duration: Duration) {
        self.latency.with_label_values(&[operation]).observe(duration.as_secs_f64());
    }
    
    pub fn hit_ratio(&self, tenant: &str, entity: &str) -> f64 {
        let hits = self.hits.with_label_values(&[tenant, entity, "found"]).get();
        let misses = self.misses.with_label_values(&[tenant, entity]).get();
        let total = hits + misses;
        if total > 0 { hits as f64 / total as f64 } else { 0.0 }
    }
}
```

### Key Metrics to Monitor

| Metric | Description | Alert Threshold |
|--------|-------------|------------------|
| `cache_hits_total` | Cache hit count | N/A |
| `cache_misses_total` | Cache miss count | N/A |
| `cache_hit_ratio` | Hit / (Hit + Miss) | < 0.7 |
| `cache_operation_duration_seconds` | Operation latency p99 | > 10ms |
| `cache_errors_total` | Redis errors | > 10/min |
| `cache_circuit_breaker_state` | 0=closed, 1=open, 2=half-open | = 1 |

## Redis Cluster Configuration

```rust
use redis::cluster::{ClusterClient, ClusterConnection};
use std::time::Duration;

pub struct RedisClusterCache {
    client: ClusterClient,
    pool_size: usize,
}

impl RedisClusterCache {
    pub async fn new(
        nodes: Vec<String>,
        pool_size: usize,
    ) -> Result<Self> {
        let client = ClusterClient::new(
            redis::cluster::ClusterClientConfig::new()
                .max_redirects(3)
                .read_timeout(Duration::from_millis(500))
                .write_timeout(Duration::from_millis(500))
                .pool_size(pool_size),
            nodes,
        ).map_err(|e| CacheError::Cluster(e.to_string()))?;
        
        Ok(Self { client, pool_size })
    }
    
    pub async fn get_connection(&self) -> Result<ClusterConnection> {
        self.client.get_connection()
            .map_err(|e| CacheError::Cluster(e.to_string()))
    }
    
    pub async fn get(&self, key: &str) -> Result<Option<Vec<u8>>> {
        let mut conn = self.get_connection().await?;
        redis::cmd("GET")
            .arg(key)
            .query_async::<_, Option<Vec<u8>>>(&mut conn)
            .await
            .map_err(Into::into)
    }
    
    pub async fn set(&self, key: &str, value: Vec<u8>, ttl_seconds: u64) -> Result<()> {
        let mut conn = self.get_connection().await?;
        redis::cmd("SETEX")
            .arg(key)
            .arg(ttl_seconds)
            .arg(value)
            .query_async::<_, ()>(&mut conn)
            .await
            .map_err(Into::into)
    }
    
    pub async fn mget(&self, keys: Vec<String>) -> Result<Vec<Option<Vec<u8>>>> {
        let mut conn = self.get_connection().await?;
        redis::cmd("MGET")
            .arg(&keys)
            .query_async::<_, Vec<Option<Vec<u8>>>>(&mut conn)
            .await
            .map_err(Into::into)
    }
}
```

### Key-Node Mapping

Redis Cluster uses hash slots (16384 total). Keys with same prefix go to same node:

```rust
pub fn get_slot(key: &str) -> u16 {
    let mut hasher = DefaultHasher::new();
    key.hash(&mut hasher);
    (hasher.finish() % 16384) as u16
}

pub async fn get_from_node(&self, key: &str) -> Result<Option<Vec<u8>>> {
    let slot = get_slot(key);
    let node = self.client.slot_for_key(key).await?;
    self.get_from_specific_node(&node, key).await
}
```

### Multi-Key Operations with Cross-Slot Handling

```rust
impl RedisClusterCache {
    pub async fn mget_safe(&self, keys: Vec<String>) -> Result<Vec<Option<Vec<u8>>>> {
        // Group keys by slot
        let mut slot_keys: HashMap<u16, Vec<String>> = HashMap::new();
        for key in keys {
            let slot = get_slot(&key);
            slot_keys.entry(slot).or_default().push(key);
        }
        
        // Execute MGET per slot (same slot = same node)
        let mut results = Vec::new();
        for (_slot, keys) in slot_keys {
            let slot_result = self.mget(keys).await?;
            results.extend(slot_result);
        }
        
        Ok(results)
    }
}
```

## Distributed Lock for Cache Stampede Prevention

```rust
pub struct DistributedLock {
    redis: Arc<RedisClusterCache>,
}

impl DistributedLock {
    pub async fn acquire(&self, key: &str, ttl_seconds: u64) -> Result<bool> {
        let lock_key = format!("{}:lock", key);
        let mut conn = self.redis.get_connection().await?;
        
        // SETNX with expiry
        let result: bool = redis::cmd("SET")
            .arg(&lock_key)
            .arg("1")
            .arg("NX")
            .arg("EX", ttl_seconds)
            .query_async(&mut conn)
            .await
            .map_err(|e| CacheError::Lock(e.to_string()))?;
        
        Ok(result)
    }
    
    pub async fn release(&self, key: &str) -> Result<()> {
        let lock_key = format!("{}:lock", key);
        let mut conn = self.redis.get_connection().await?;
        
        redis::cmd("DEL")
            .arg(&lock_key)
            .query_async::<_, ()>(&mut conn)
            .await?;
        
        Ok(())
    }
}

pub async fn get_with_stampede_protection<T: Message + Default>(
    cache: &CacheLayer,
    db: &DbPool,
    lock: &DistributedLock,
    key: &str,
) -> Result<Option<T>> {
    // Try cache first
    if let Some(v) = cache.get_proto(key).await? {
        return Ok(Some(v));
    }
    
    // Cache miss - try to acquire lock
    if lock.acquire(key, 5).await.unwrap_or(false) {
        // We got the lock - fetch from DB and populate
        let result = fetch_and_cache(cache, db, key).await;
        let _ = lock.release(key).await;
        result
    } else {
        // Another process is populating - wait and retry cache
        tokio::time::sleep(Duration::from_millis(100)).await;
        cache.get_proto(key).await
    }
}

async fn fetch_and_cache<T: Message + Default>(
    cache: &CacheLayer,
    db: &DbPool,
    key: &str,
) -> Result<Option<T>> {
    // Double-check cache (another request might have populated)
    if let Some(v) = cache.get_proto(key).await? {
        return Ok(Some(v));
    }
    
    // Fetch from DB
    let entity = db.fetch_by_key(key).await?;
    
    if let Some(ref e) = entity {
        let bytes = Message::encode_to_vec(e);
        cache.set(key, bytes, 300).await?;
    }
    
    Ok(entity)
}
```

## Error Handling

```rust
#[derive(Debug, thiserror::Error)]
pub enum CacheError {
    #[error("Redis error: {0}")]
    Redis(#[from] redis::RedisError),
    
    #[error("Serialization error: {0}")]
    Serialize(String),
    
    #[error("Deserialization error: {0}")]
    Deserialize(String),
    
    #[error("Not found: {0}")]
    NotFound,
    
    #[error("Cluster error: {0}")]
    Cluster(String),
    
    #[error("Lock error: {0}")]
    Lock(String),
    
    #[error("Circuit breaker open")]
    CircuitBreakerOpen,
}
```

## Best Practices Summary

1. **Always use binary serialization** (protobuf/msgpack) for performance - never JSON
2. **Design keys as `tenant:entity:id`** for multi-tenant isolation
3. **Set appropriate TTL per entity type** - balance freshness vs performance
4. **Implement circuit breaker** - Redis failures should not crash your service
5. **Use connection pooling** - pool size should match concurrency needs
6. **Monitor hit ratio** - alert when below 0.7
7. **Warm cache on startup** - populate hot data before traffic arrives
8. **Use distributed locks** - prevent cache stampede on thundering herd
9. **Invalidate on write** - keep cache consistent with source of truth
10. **Use Redis Cluster** - enables horizontal scaling and fault tolerance
