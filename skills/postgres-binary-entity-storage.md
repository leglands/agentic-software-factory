---
name: postgres-binary-entity-storage
description: Store entities in PostgreSQL using binary serialization (protobuf/CBOR) for non-queryable fields while keeping queryable fields as native SQL columns. Covers hybrid table design, prost encode/decode, migration, query patterns, indexes, TOAST compression, and pg_stat analysis.
category: data_storage
tags: [postgresql, rust, prost, protobuf, cbor, binary-serialization, hybrid-table-design, toast, migration]
version: 1.0.0
eval_cases:
  - id: hybrid_table_creation
    description: Create a hybrid table with SQL columns for queryable fields and BYTEA for binary payload
    examples:
      - Create table with id, tenant_id, entity_type as SQL columns and data as BYTEA
      - Add appropriate indexes on tenant_id and entity_type
      - Verify TOAST compression is enabled by default
  - id: prost_encode_decode
    description: Implement prost message encoding and decoding in Rust
    examples:
      - Define a protobuf message with prost
      - Encode entity to bytes using prost::Message::encode
      - Decode bytes back to entity using prost::Message::decode
      - Handle decode errors gracefully
  - id: rust_repository_pattern
    description: Implement a repository pattern in Rust for binary entity storage
    examples:
      - Create a generic repository struct with sqlx::PgPool
      - Implement save() that serializes with prost and inserts
      - Implement find_by_id() that deserializes from BYTEA
      - Implement find_by_tenant() that filters on SQL columns
  - id: json_to_binary_migration
    description: Migrate existing JSON(B) columns to binary BYTEA with zero downtime
    examples:
      - Add new BYTEA column alongside existing JSONB
      - Backfill binary column in batches using cursor pagination
      - Dual-write during transition period
      - Drop JSONB column after verification
  - id: query_patterns
    description: Query entities using SQL columns for filtering, deserialize payload in application
    examples:
      - Filter by tenant_id and entity_type in WHERE clause
      - Use ORDER BY on SQL columns
      - Deserialize BYTEA payload in Rust after fetching
      - Implement pagination with LIMIT/OFFSET
  - id: index_strategy
    description: Design and implement indexes for hybrid entity storage
    examples:
      - Create B-tree index on (tenant_id, entity_type)
      - Create partial index for active entities per tenant
      - Analyze query plans with EXPLAIN ANALYZE
      - Consider covering indexes for frequent queries
  - id: toast_compression_analysis
    description: Analyze TOAST compression behavior for large binary payloads
    examples:
      - Check toast_chunk_size and compression for large records
      - Compare pglz vs LZ4 compression ratios
      - Monitor pg_class.reltoastrelid for TOAST tables
      - Estimate optimal chunk size for typical payload sizes
  - id: pg_stat_monitoring
    description: Monitor entity storage performance using pg_stat views
    examples:
      - Query pg_stat_user_tables for table access patterns
      - Monitor heap_blks_read vs heap_blks_hit ratio
      - Check idx_scan vs idx_tup_read for index efficiency
      - Analyze toast_blks_read for TOAST access patterns
  - id: bulk_operations
    description: Implement efficient bulk insert and retrieval for binary entities
    examples:
      - Use COPY protocol for bulk inserts
      - Stream large result sets with cursor
      - Implement batch deserialization with rayon
      - Use prepared statements for repeated operations
  - id: error_handling_prost
    description: Handle prost encoding/decoding errors in the repository layer
    examples:
      - Return custom error type wrapping prost::DecodeError
      - Implement From<sqlx::Error> for repository errors
      - Log decoding failures with entity context
      - Consider dead letter queue for poison pills
  - id: transaction_isolation
    description: Ensure consistency with proper transaction isolation for binary entities
    examples:
      - Use SERIALIZABLE for critical writes
      - Implement optimistic locking with version column
      - Handle serialization failures with retry logic
      - Ensure TOAST data stays with parent row in same transaction
  - id: connection_pooling
    description: Configure connection pool for binary entity workloads
    examples:
      - Set合适的 pool size for concurrent prost encode/decode
      - Configure statement cache for repeated queries
      - Monitor wait_time in pg_stat_activity
      - Consider PgBouncer for connection management
---

# PostgreSQL Binary Entity Storage Skill

## Overview

This skill covers storing entities in PostgreSQL using binary serialization (protobuf/CBOR) for non-queryable fields while maintaining queryable fields as native SQL columns. This hybrid approach optimizes for both query performance and storage efficiency.

## Hybrid Table Design

### Table Schema

```sql
CREATE TABLE entities (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL,
    entity_type     TEXT NOT NULL,
    version         INTEGER NOT NULL DEFAULT 1,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    data            BYTEA NOT NULL,
    
    CONSTRAINT entities_tenant_type_version_uniq UNIQUE (tenant_id, entity_type, id)
);

-- Primary query index
CREATE INDEX idx_entities_tenant_type ON entities (tenant_id, entity_type);

-- Partial index for active entities
CREATE INDEX idx_entities_active ON entities (tenant_id, entity_type, id) 
WHERE deleted_at IS NULL;

-- Index for time-based queries
CREATE INDEX idx_entities_updated ON entities (tenant_id, updated_at DESC);
```

### Design Principles

| Field Type | SQL Column | Use Case |
|------------|------------|----------|
| Primary Key | `id UUID` | Unique identification, FK references |
| Tenant | `tenant_id UUID` | Multi-tenant isolation, JOINs |
| Discriminator | `entity_type TEXT` | Type filtering, polymorphic queries |
| Version | `version INTEGER` | Optimistic locking |
| Timestamps | `created_at`, `updated_at` | Audit, ordering |
| Payload | `data BYTEA` | Binary protobuf/CBOR content |

### Why BYTEA over JSONB?

- **Smaller storage**: Protobuf is typically 30-70% smaller than JSON
- **Strict schema**: Compile-time validation with prost
- **No parsing overhead**: Direct memory mapping possible
- **TOAST-friendly**: Large payloads automatically compressed
- **Queryable metadata stays SQL**: No need to parse to filter

## prost Encode/Decode in Rust

### Cargo Dependencies

```toml
[dependencies]
prost = "0.13"
prost-build = "0.13"
sqlx = { version = "0.8", features = ["runtime-tokio", "uuid", "chrono"] }
tokio = { version = "1", features = ["full"] }
uuid = { version = "1", features = ["v4", "serde"] }
chrono = { version = "0.4", features = ["serde"] }
thiserror = "2"
tracing = "0.1"
```

### Protobuf Message Definition

```protobuf
// entities.proto
syntax = "proto3";

package entities.v1;

message UserProfile {
    string display_name = 1;
    string email = 2;
    map<string, string> preferences = 3;
    repeated string roles = 4;
    bytes avatar_data = 5;
    int64 follower_count = 6;
}

message Order {
    string order_number = 1;
    repeated OrderLine items = 2;
    Money total = 3;
    ShippingAddress shipping = 4;
}

message OrderLine {
    string product_id = 1;
    int32 quantity = 2;
    Money unit_price = 3;
}

message Money {
    string currency = 1;
    int64 amount_cents = 2;
}

message ShippingAddress {
    string street = 1;
    string city = 2;
    string country = 3;
    string postal_code = 4;
}
```

### Build Configuration

```rust
// build.rs
use prost_build;

fn main() {
    let proto_files = &["proto/entities.proto"];
    
    let mut config = prost_build::Config::new();
    config.type_attribute(".", "#[derive(serde::Serialize, serde::Deserialize)]");
    
    prost_build::compile_protos(proto_files, &["proto/"]).unwrap();
}
```

### Entity Trait for Polymorphism

```rust
// entities/src/lib.rs
use prost::{Message, EncodeError, DecodeError};

pub trait Entity: Message + Default + Sized {
    fn entity_type() -> &'static str;
    fn version(&self) -> i32;
}

#[derive(thiserror::Error, Debug)]
pub enum EntityError {
    #[error("encoding failed: {0}")]
    Encode(#[from] EncodeError),
    #[error("decoding failed: {0}")]
    Decode(#[from] DecodeError),
    #[error("serialization failed: {0}")]
    Serialization(String),
    #[error("entity not found: {0}")]
    NotFound(String),
}
```

### UserProfile Implementation

```rust
// entities/src/user.rs
use prost::Message;
use super::Entity;

#[derive(Message, Default)]
pub struct UserProfile {
    #[prost(string, tag = "1")]
    pub display_name: ::prost::alloc::string::String,
    #[prost(string, tag = "2")]
    pub email: ::prost::alloc::string::String,
    #[prost(map = "string, string", tag = "3")]
    pub preferences: ::std::collections::HashMap<::prost::alloc::string::String, ::prost::alloc::string::String>,
    #[prost(string, repeated, tag = "4")]
    pub roles: ::prost::alloc::vec::Vec<::prost::alloc::string::String>,
    #[prost(bytes, tag = "5")]
    pub avatar_data: ::prost::bytes::Bytes,
    #[prost(int64, tag = "6")]
    pub follower_count: i64,
}

impl Entity for UserProfile {
    fn entity_type() -> &'static str {
        "user_profile"
    }
    
    fn version(&self) -> i32 {
        1
    }
}
```

### Encoding/Decoding Utilities

```rust
// entities/src/codec.rs
use prost::{Message, EncodeError, DecodeError};
use super::EntityError;

pub fn encode<E: Message>(entity: &E) -> Result<Vec<u8>, EntityError> {
    let mut buf = Vec::with_capacity(entity.encoded_len());
    entity.encode(&mut buf).map_err(EntityError::Encode)?;
    Ok(buf)
}

pub fn decode<E: Message + Default>(bytes: &[u8]) -> Result<E, EntityError> {
    E::decode(bytes).map_err(EntityError::Decode)
}

pub fn encode_to_box<E: Message>(entity: &E) -> Result<prost::bytes::Bytes, EntityError> {
    let mut buf = Vec::with_capacity(entity.encoded_len());
    entity.encode(&mut buf).map_err(EntityError::Encode)?;
    Ok(prost::bytes::Bytes::from(buf))
}
```

## Rust Repository Pattern

### Repository Trait

```rust
// repository/src/traits.rs
use async_trait::async_trait;
use uuid::Uuid;
use std::error::Error;

#[async_trait]
pub trait EntityRepository<E: 'static>: Send + Sync {
    async fn save(&self, tenant_id: Uuid, entity: E) -> Result<E, Box<dyn Error + Send + Sync>>;
    async fn find_by_id(&self, tenant_id: Uuid, id: Uuid) -> Result<Option<E>, Box<dyn Error + Send + Sync>>;
    async fn find_by_type(&self, tenant_id: Uuid, entity_type: &str) -> Result<Vec<E>, Box<dyn Error + Send + Sync>>;
    async fn delete(&self, tenant_id: Uuid, id: Uuid) -> Result<bool, Box<dyn Error + Send + Sync>>;
}
```

### PostgreSQL Repository Implementation

```rust
// repository/src/postgres.rs
use sqlx::postgres::{PgPool, PgRow};
use sqlx::Row;
use uuid::Uuid;
use std::error::Error;
use async_trait::async_trait;
use crate::codec::{encode, decode};
use super::traits::{EntityRepository};
use entities::{Entity, EntityError};

pub struct PostgresEntityRepository {
    pool: PgPool,
}

impl PostgresEntityRepository {
    pub fn new(pool: PgPool) -> Self {
        Self { pool }
    }
    
    async fn find_row_by_id(
        &self, 
        tenant_id: Uuid, 
        id: Uuid
    ) -> Result<Option<PgRow>, sqlx::Error> {
        sqlx::query_as::<_, PgRow>(
            r#"
            SELECT id, tenant_id, entity_type, version, created_at, updated_at, data
            FROM entities
            WHERE tenant_id = $1 AND id = $2
            "#,
        )
        .bind(tenant_id)
        .bind(id)
        .fetch_optional(&self.pool)
        .await
    }
}

#[async_trait]
impl<E: Entity + prost::Message + Default + Send + Sync + 'static> 
    EntityRepository<E> 
    for PostgresEntityRepository 
{
    async fn save(
        &self, 
        tenant_id: Uuid, 
        entity: E
    ) -> Result<E, Box<dyn Error + Send + Sync>> {
        let entity_type = E::entity_type();
        let version = entity.version();
        let data = encode(&entity).map_err(|e| Box::new(e) as Box<dyn Error + Send + Sync>)?;
        
        let row = sqlx::query_as::<_, PgRow>(
            r#"
            INSERT INTO entities (id, tenant_id, entity_type, version, data)
            VALUES (gen_random_uuid(), $1, $2, $3, $4)
            ON CONFLICT (tenant_id, entity_type, id) 
            DO UPDATE SET 
                data = EXCLUDED.data,
                version = entities.version + 1,
                updated_at = NOW()
            RETURNING id, tenant_id, entity_type, version, created_at, updated_at, data
            "#,
        )
        .bind(tenant_id)
        .bind(entity_type)
        .bind(version)
        .bind(&data)
        .fetch_one(&self.pool)
        .await?;
        
        let data: Vec<u8> = row.get("data");
        let saved = decode::<E>(&data).map_err(|e| Box::new(e) as Box<dyn Error + Send + Sync>)?;
        Ok(saved)
    }
    
    async fn find_by_id(
        &self, 
        tenant_id: Uuid, 
        id: Uuid
    ) -> Result<Option<E>, Box<dyn Error + Send + Sync>> {
        let row = self.find_row_by_id(tenant_id, id).await?;
        
        match row {
            Some(row) => {
                let data: Vec<u8> = row.get("data");
                let entity = decode::<E>(&data).map_err(|e| Box::new(e) as Box<dyn Error + Send + Sync>)?;
                Ok(Some(entity))
            }
            None => Ok(None),
        }
    }
    
    async fn find_by_type(
        &self, 
        tenant_id: Uuid, 
        entity_type: &str
    ) -> Result<Vec<E>, Box<dyn Error + Send + Sync>> {
        let rows = sqlx::query_as::<_, PgRow>(
            r#"
            SELECT id, tenant_id, entity_type, version, created_at, updated_at, data
            FROM entities
            WHERE tenant_id = $1 AND entity_type = $2
            ORDER BY created_at DESC
            "#,
        )
        .bind(tenant_id)
        .bind(entity_type)
        .fetch_all(&self.pool)
        .await?;
        
        let mut entities = Vec::with_capacity(rows.len());
        for row in rows {
            let data: Vec<u8> = row.get("data");
            let entity = decode::<E>(&data).map_err(|e| Box::new(e) as Box<dyn Error + Send + Sync>)?;
            entities.push(entity);
        }
        Ok(entities)
    }
    
    async fn delete(
        &self, 
        tenant_id: Uuid, 
        id: Uuid
    ) -> Result<bool, Box<dyn Error + Send + Sync>> {
        let result = sqlx::query(
            r#"
            DELETE FROM entities
            WHERE tenant_id = $1 AND id = $2
            "#,
        )
        .bind(tenant_id)
        .bind(id)
        .execute(&self.pool)
        .await?;
        
        Ok(result.rows_affected() > 0)
    }
}
```

## Migration Strategy from JSON to Binary

### Phase 1: Add New Column (Zero Downtime)

```sql
-- Step 1: Add BYTEA column
ALTER TABLE entities ADD COLUMN data_binary BYTEA;

-- Step 2: Create migration status column
ALTER TABLE entities ADD COLUMN migration_status TEXT DEFAULT 'pending';

CREATE INDEX idx_entities_migration_pending ON entities (tenant_id) 
WHERE migration_status = 'pending';
```

### Phase 2: Backfill in Batches

```sql
-- Create function to migrate batch
CREATE OR REPLACE FUNCTION migrate_entity_batch(
    p_batch_size INTEGER DEFAULT 1000
) RETURNS INTEGER AS $$
DECLARE
    v_migrated INTEGER := 0;
    v_id UUID;
    v_data_json JSONB;
    v_data_binary BYTEA;
BEGIN
    FOR v_id, v_data_json IN 
        SELECT id, data 
        FROM entities 
        WHERE migration_status = 'pending'
        ORDER BY created_at
        LIMIT p_batch_size
        FOR UPDATE SKIP LOCKED
    LOOP
        BEGIN
            -- Convert JSONB to protobuf (handled in application)
            -- For now, mark as in_progress
            UPDATE entities 
            SET migration_status = 'in_progress'
            WHERE id = v_id;
            
            v_migrated := v_migrated + 1;
        EXCEPTION WHEN OTHERS THEN
            UPDATE entities 
            SET migration_status = 'failed'
            WHERE id = v_id;
        END;
    END LOOP;
    
    RETURN v_migrated;
END;
$$ LANGUAGE plpgsql;
```

### Rust Migration Script

```rust
// migration/src/json_to_binary.rs
use sqlx::PgPool;
use uuid::Uuid;
use tracing::{info, warn};

pub async fn migrate_entity(
    pool: &PgPool,
    id: Uuid,
    json_data: &serde_json::Value,
) -> Result<Vec<u8>, Box<dyn std::error::Error + Send + Sync>> {
    // Parse JSON to intermediate struct
    #[derive(serde::Deserialize)]
    struct LegacyUserProfile {
        display_name: String,
        email: String,
        preferences: Option<std::collections::HashMap<String, String>>,
        roles: Option<Vec<String>>,
        avatar_data: Option<String>, // Base64 encoded
        follower_count: Option<i64>,
    }
    
    let legacy: LegacyUserProfile = serde_json::from_value(json_data.clone())?;
    
    // Convert to protobuf
    let profile = entities::UserProfile {
        display_name: legacy.display_name,
        email: legacy.email,
        preferences: legacy.preferences.unwrap_or_default(),
        roles: legacy.roles.unwrap_or_default(),
        avatar_data: legacy.avatar_data
            .map(|b| prost::bytes::Bytes::from(base64::decode(&b).unwrap_or_default()))
            .unwrap_or_default(),
        follower_count: legacy.follower_count.unwrap_or(0),
    };
    
    Ok(entities::codec::encode(&profile)?)
}

pub async fn run_migration_batch(
    pool: &PgPool,
    batch_size: i64,
) -> Result<i64, Box<dyn std::error::Error + Send + Sync>> {
    let mut tx = pool.begin().await?;
    
    let rows = sqlx::query!(
        r#"
        SELECT id, data as "data: serde_json::Value"
        FROM entities
        WHERE migration_status = 'pending'
        ORDER BY created_at
        LIMIT $1
        FOR UPDATE SKIP LOCKED
        "#,
        batch_size
    )
    .fetch_all(&mut *tx)
    .await?;
    
    let mut migrated = 0i64;
    
    for row in rows {
        match migrate_entity(pool, row.id, &row.data).await {
            Ok(binary_data) => {
                sqlx::query!(
                    r#"
                    UPDATE entities 
                    SET data_binary = $1, 
                        migration_status = 'completed',
                        updated_at = NOW()
                    WHERE id = $2
                    "#,
                    &binary_data,
                    row.id
                )
                .execute(&mut *tx)
                .await?;
                migrated += 1;
            }
            Err(e) => {
                warn!(entity_id = %row.id, error = %e, "Migration failed");
                sqlx::query!(
                    "UPDATE entities SET migration_status = 'failed' WHERE id = $1",
                    row.id
                )
                .execute(&mut *tx)
                .await?;
            }
        }
    }
    
    tx.commit().await?;
    info!(migrated = migrated, "Migration batch completed");
    Ok(migrated)
}
```

### Phase 3: Dual-Write Transition

```rust
// During transition period, write to both columns
async fn dual_write(
    &self,
    tenant_id: Uuid,
    entity: impl Entity,
) -> Result<(), Box<dyn Error + Send + Sync>> {
    let json_data = serde_json::to_value(&entity)?;
    let binary_data = encode(&entity)?;
    
    sqlx::query!(
        r#"
        INSERT INTO entities (id, tenant_id, entity_type, version, data, data_json)
        VALUES (gen_random_uuid(), $1, $2, $3, $4, $5)
        ON CONFLICT (tenant_id, entity_type, id) 
        DO UPDATE SET 
            data = EXCLUDED.data,
            data_json = EXCLUDED.data_json,
            version = entities.version + 1,
            updated_at = NOW()
        "#,
        tenant_id,
        entity.entity_type(),
        entity.version(),
        &binary_data,
        &json_data
    )
    .execute(&self.pool)
    .await?;
    
    Ok(())
}
```

### Phase 4: Cleanup

```sql
-- After verification, drop old columns
ALTER TABLE entities DROP COLUMN IF EXISTS data_json;
ALTER TABLE entities DROP COLUMN IF EXISTS migration_status;

-- Rename new column
ALTER TABLE entities RENAME COLUMN data_binary TO data;

-- Rebuild indexes
REINDEX TABLE entities;
```

## Query Patterns

### Filter on SQL Columns, Deserialize in App

```rust
// repository/src/queries.rs

pub struct EntityQuery {
    pub tenant_id: Uuid,
    pub entity_type: Option<String>,
    pub ids: Option<Vec<Uuid>>,
    pub created_after: Option<DateTime<Utc>>,
    pub created_before: Option<DateTime<Utc>>,
    pub limit: Option<i64>,
    pub offset: Option<i64>,
}

impl PostgresEntityRepository {
    pub async fn query(
        &self,
        query: EntityQuery,
    ) -> Result<Vec<EntityResult>, Box<dyn Error + Send + Sync>> {
        let mut sql = String::from(
            "SELECT id, tenant_id, entity_type, version, created_at, updated_at, data \
             FROM entities WHERE tenant_id = $1"
        );
        let mut param_idx = 2;
        let mut params: Vec<String> = vec![query.tenant_id.to_string()];
        
        if let Some(ref types) = query.entity_type {
            param_idx += 1;
            sql.push_str(&format!(" AND entity_type = ${}", param_idx));
            params.push(types.clone());
        }
        
        if let Some(ref ids) = query.ids {
            param_idx += 1;
            sql.push_str(&format!(" AND id = ANY(${})", param_idx));
            params.push(ids.iter().map(|u| u.to_string()).collect::<Vec<_>>().join(","));
        }
        
        if let Some(after) = query.created_after {
            param_idx += 1;
            sql.push_str(&format!(" AND created_at >= ${}", param_idx));
            params.push(after.to_rfc3339());
        }
        
        if let Some(before) = query.created_before {
            param_idx += 1;
            sql.push_str(&format!(" AND created_at <= ${}", param_idx));
            params.push(before.to_rfc3339());
        }
        
        sql.push_str(" ORDER BY created_at DESC");
        
        if let Some(limit) = query.limit {
            param_idx += 1;
            sql.push_str(&format!(" LIMIT ${}", param_idx));
            params.push(limit.to_string());
        }
        
        if let Some(offset) = query.offset {
            param_idx += 1;
            sql.push_str(&format!(" OFFSET ${}", param_idx));
            params.push(offset.to_string());
        }
        
        let rows = sqlx::query(&sql)
            .bind(query.tenant_id)
            .fetch_all(&self.pool)
            .await?;
        
        let mut results = Vec::with_capacity(rows.len());
        for row in rows {
            let data: Vec<u8> = row.get("data");
            let entity_type: String = row.get("entity_type");
            
            let entity: Box<dyn Entity> = match entity_type.as_str() {
                "user_profile" => Box::new(decode::<UserProfile>(&data)?),
                "order" => Box::new(decode::<Order>(&data)?),
                _ => return Err(Box::new(EntityError::UnknownType(entity_type))),
            };
            
            results.push(EntityResult {
                id: row.get("id"),
                tenant_id: row.get("tenant_id"),
                entity_type: row.get("entity_type"),
                version: row.get("version"),
                created_at: row.get("created_at"),
                updated_at: row.get("updated_at"),
                entity,
            });
        }
        
        Ok(results)
    }
}
```

### Using Cursor-Based Pagination

```rust
pub async fn query_cursor(
    &self,
    tenant_id: Uuid,
    entity_type: &str,
    cursor: Option<(Uuid, chrono::DateTime<Utc>)>,
    limit: i64,
) -> Result<Vec<EntityResult>, Box<dyn Error + Send + Sync>> {
    let sql = if cursor.is_some() {
        r#"
        SELECT id, tenant_id, entity_type, version, created_at, updated_at, data
        FROM entities
        WHERE tenant_id = $1 AND entity_type = $2 
          AND (created_at, id) < ($3, $4)
        ORDER BY created_at DESC, id DESC
        LIMIT $5
        "#
    } else {
        r#"
        SELECT id, tenant_id, entity_type, version, created_at, updated_at, data
        FROM entities
        WHERE tenant_id = $1 AND entity_type = $2
        ORDER BY created_at DESC, id DESC
        LIMIT $3
        "#
    };
    
    let rows = if let Some((id, ts)) = cursor {
        sqlx::query_as::<_, PgRow>(sql)
            .bind(tenant_id)
            .bind(entity_type)
            .bind(ts)
            .bind(id)
            .bind(limit)
            .fetch_all(&self.pool)
            .await?
    } else {
        sqlx::query_as::<_, PgRow>(sql)
            .bind(tenant_id)
            .bind(entity_type)
            .bind(limit)
            .fetch_all(&self.pool)
            .await?
    };
    
    // ... process rows
    Ok(results)
}
```

## Index Strategy

### Index Types for Hybrid Storage

```sql
-- B-tree index for equality queries
CREATE INDEX idx_entities_tenant_type 
    ON entities (tenant_id, entity_type);

-- B-tree for range queries on timestamps
CREATE INDEX idx_entities_tenant_created 
    ON entities (tenant_id, created_at DESC);

-- Partial index for active records
CREATE INDEX idx_entities_active 
    ON entities (tenant_id, entity_type, created_at DESC) 
    WHERE deleted_at IS NULL;

-- Partial index for specific entity type
CREATE INDEX idx_entities_users_active 
    ON entities (tenant_id, created_at DESC) 
    WHERE entity_type = 'user_profile' AND deleted_at IS NULL;

-- Covering index to avoid heap access
CREATE INDEX idx_entities_covering 
    ON entities (tenant_id, entity_type, created_at DESC) 
    INCLUDE (version, updated_at)
    WHERE deleted_at IS NULL;
```

### Index Selection with EXPLAIN

```sql
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT id, tenant_id, entity_type, version, created_at, updated_at, data
FROM entities
WHERE tenant_id = '550e8400-e29b-41d4-a716-446655440000'
  AND entity_type = 'user_profile'
  AND deleted_at IS NULL
ORDER BY created_at DESC
LIMIT 100;
```

### Index Maintenance

```sql
-- Monitor index usage
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan ASC;

-- Reindex to reclaim space after heavy deletes
REINDEX INDEX CONCURRENTLY idx_entities_active;

-- Analyze to update statistics
ANALYZE entities;
```

## TOAST Compression

### Understanding TOAST

PostgreSQL automatically compresses and out-of-line stores large column values (typically >2KB) in a separate TOAST table.

```sql
-- Check TOAST table for entities
SELECT 
    c.relname AS table_name,
    c.reltoastrelid::regclass AS toast_table,
    pg_size_pretty(pg_total_relation_size(c.reltoastrelid)) AS toast_size,
    a.attname AS column_name,
    a.attlen AS column_size
FROM pg_class c
JOIN pg_attribute a ON a.attrelid = c.oid
WHERE c.relname = 'entities'
  AND a.attnum > 0;
```

### TOAST Configuration

```sql
-- Check current TOAST settings
SHOW toast_tuple_target;
SHOW toast_compression_target;
SHOW toast_max_chunk_size;

-- Default values:
-- toast_tuple_target = 248 (bytes before TOASTing)
-- toast_compression_target = 0.2 (20% compression ratio target)
-- toast_max_chunk_size = 1996 (bytes per chunk)
```

### Measuring Compression Ratio

```sql
-- Create test table to measure compression
CREATE TABLE entities_test (
    id UUID PRIMARY KEY,
    data BYTEA
);

-- Insert same data with different compressions
INSERT INTO entities_test 
SELECT gen_random_uuid(), encode(protobuf_data, 'base64')
FROM generate_series(1, 10000);

-- Analyze compression
SELECT 
    compression,
    pg_column_size(data) AS compressed_size,
    pg_column_size(data || repeat('x', 1000)) AS padded_size,
    pg_column_size(data) / NULLIF(pg_column_size(data || repeat('x', 1000)), 0)::float AS ratio
FROM (
    SELECT 
        data,
        CASE 
            WHEN pg_column_size(data) < 1000 THEN 'inline'
            ELSE 'toast'
        END AS compression
    FROM entities_test
) sub;
```

### Monitoring TOAST Usage

```sql
-- Check TOAST access patterns
SELECT 
    schemaname,
    relname,
    toast_blks_read,
    toast_blks_hit,
    toast_blks_hit::float / NULLIF(toast_blks_read + toast_blks_hit, 0) AS toast_hit_ratio
FROM pg_statio_user_tables
WHERE relname = 'entities';

-- TOAST hit ratio should be > 0.95 for hot data
-- If too low, consider keeping more data in-row or increasing work_mem
```

### Optimizing for TOAST

```sql
-- For frequently accessed large fields, consider inlining
ALTER TABLE entities ADD COLUMN small_avatar BYTEA;

-- Move to inline storage for small avatars (< 2KB)
UPDATE entities 
SET small_avatar = substring(data from 1 for 2000)
WHERE pg_column_size(substring(data from 1 for 2000)) < 2000;

-- Create index on TOAST-ed data for full-text search
CREATE INDEX idx_entities_data_gin 
    ON entities USING gin (data);
```

## pg_stat Analysis

### Key Metrics

```sql
-- Table access statistics
SELECT 
    relname AS table_name,
    seq_scan,
    seq_tup_read,
    idx_scan,
    idx_tup_fetch,
    heap_blks_read,
    heap_blks_hit,
    heap_blks_hit::float / NULLIF(heap_blks_read + heap_blks_hit, 0) AS heap_hit_ratio,
    n_tup_ins,
    n_tup_upd,
    n_tup_del,
    n_live_tup,
    n_dead_tup,
    last_vacuum,
    last_autovacuum,
    last_analyze,
    last_autoanalyze
FROM pg_stat_user_tables
WHERE relname = 'entities';
```

### Cache Hit Ratio Analysis

```sql
-- Calculate overall cache hit ratio
SELECT 
    sum(heap_blks_hit) AS total_cache_hits,
    sum(heap_blks_read) AS total_disk_reads,
    sum(heap_blks_hit)::float / 
        NULLIF(sum(heap_blks_hit) + sum(heap_blks_read), 0) AS hit_ratio
FROM pg_statio_user_tables;

-- Target: > 0.95 for hot data
-- If lower, consider:
--   1. Increasing shared_buffers
--   2. Adding RAM
--   3. Using pg_prewarm to warm cache
```

### Index Efficiency

```sql
-- Index usage analysis
SELECT 
    indexrelname AS index_name,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch,
    idx_tup_fetch::float / NULLIF(idx_scan, 0) AS tuples_per_scan
FROM pg_stat_user_indexes
WHERE relname = 'entities'
ORDER BY idx_scan DESC;

-- High idx_scan with low idx_tup_fetch = efficient index
-- High idx_scan with high idx_tup_fetch = good selectivity
```

### Dead Tuples and Bloat

```sql
-- Monitor dead tuples and bloat
SELECT 
    relname,
    n_dead_tup,
    n_live_tup,
    n_dead_tup::float / NULLIF(n_live_tup + n_dead_tup, 0) AS dead_ratio,
    pg_size_pretty(pg_relation_size(relid)) AS table_size,
    pg_size_pretty(pg_total_relation_size(relid)) AS total_size,
    CASE 
        WHEN pg_total_relation_size(relid) > pg_relation_size(relid) * 1.2 
        THEN 'bloated'
        ELSE 'ok'
    END AS bloat_status
FROM pg_stat_user_tables
WHERE relname = 'entities';
```

### Query Performance Monitoring

```sql
-- Find slow queries using pg_stat_statements
SELECT 
    query,
    calls,
    total_exec_time / calls AS avg_exec_time_ms,
    rows / calls AS avg_rows,
    stddev_exec_time AS exec_time_stddev,
    (shared_blks_hit * 100.0 / NULLIF(shared_blks_hit + shared_blks_read, 0)) AS cache_hit_pct
FROM pg_stat_statements
WHERE query LIKE '%entities%'
ORDER BY total_exec_time DESC
LIMIT 20;
```

### Real-Time Monitoring View

```sql
CREATE VIEW entity_storage_monitor AS
WITH table_stats AS (
    SELECT 
        schemaname,
        relname,
        seq_scan,
        idx_scan,
        heap_blks_read,
        heap_blks_hit,
        idx_blks_read,
        idx_blks_hit,
        n_tup_ins,
        n_tup_upd,
        n_tup_del,
        n_live_tup,
        n_dead_tup,
        last_vacuum,
        last_analyze
    FROM pg_stat_user_tables
    WHERE relname = 'entities'
),
toast_stats AS (
    SELECT 
        relname,
        toast_blks_read,
        toast_blks_hit
    FROM pg_statio_user_tables
    WHERE relname = 'entities'
)
SELECT 
    t.schemaname,
    t.relname,
    t.seq_scan,
    t.idx_scan,
    t.heap_blks_hit::float / NULLIF(t.heap_blks_read + t.heap_blks_hit, 0) AS heap_hit_ratio,
    t.idx_blks_hit::float / NULLIF(t.idx_blks_read + t.idx_blks_hit, 0) AS idx_hit_ratio,
    COALESCE(tst.toast_blks_hit, 0)::float / 
        NULLIF(COALESCE(tst.toast_blks_hit, 0) + COALESCE(tst.toast_blks_read, 0), 0) 
        AS toast_hit_ratio,
    t.n_live_tup,
    t.n_dead_tup,
    t.n_tup_ins,
    t.n_tup_upd,
    t.n_tup_del,
    t.last_vacuum,
    t.last_analyze,
    pg_size_pretty(pg_relation_size(t.relid::regclass)) AS table_size
FROM table_stats t
LEFT JOIN toast_stats tst ON t.relname = tst.relname;

-- Usage:
SELECT * FROM entity_storage_monitor;
```

### Setting Up Continuous Monitoring

```sql
-- Create function to collect metrics
CREATE OR REPLACE FUNCTION collect_entity_metrics()
RETURNS void AS $$
BEGIN
    INSERT INTO entity_metrics_history (
        collected_at,
        heap_hit_ratio,
        idx_hit_ratio,
        toast_hit_ratio,
        n_live_tup,
        n_dead_tup
    )
    SELECT 
        NOW(),
        heap_blks_hit::float / NULLIF(heap_blks_read + heap_blks_hit, 0),
        idx_blks_hit::float / NULLIF(idx_blks_read + idx_blks_hit, 0),
        0, -- toast stats require separate query
        n_live_tup,
        n_dead_tup
    FROM pg_stat_user_tables
    WHERE relname = 'entities';
END;
$$ LANGUAGE plpgsql;

-- Add to pg_cron or cron job
-- SELECT cron.schedule('collect-entity-metrics', '*/5 * * * *', 'SELECT collect_entity_metrics()');
```

## Complete Example: User Profile Service

```rust
// examples/user-profile-service/src/main.rs
use uuid::Uuid;
use sqlx::postgres::PgPoolOptions;
use std::error::Error;

mod entities;
mod repository;
mod codec;

use entities::{Entity, UserProfile};
use repository::PostgresEntityRepository;

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error + Send + Sync>> {
    let pool = PgPoolOptions::new()
        .max_connections(10)
        .connect("postgres://user:pass@localhost/entities")
        .await?;

    let repo = PostgresEntityRepository::new(pool);
    
    // Create user profile
    let mut profile = UserProfile::default();
    profile.display_name = "Alice".to_string();
    profile.email = "alice@example.com".to_string();
    profile.preferences.insert("theme".to_string(), "dark".to_string());
    profile.roles.push("admin".to_string());
    profile.follower_count = 42;
    
    let tenant_id = Uuid::new_v4();
    let saved = repo.save(tenant_id, profile).await?;
    
    // Query by tenant
    let found = repo.find_by_id(tenant_id, saved.id).await?;
    assert!(found.is_some());
    
    // Query by type
    let all_profiles = repo.find_by_type(tenant_id, "user_profile").await?;
    println!("Found {} profiles", all_profiles.len());
    
    Ok(())
}
```

## Summary

| Aspect | Recommendation |
|--------|-----------------|
| Table Design | SQL columns for queryable fields (id, tenant_id, type, timestamps, version) |
| Payload Storage | BYTEA for binary protobuf/CBOR data |
| Indexes | B-tree on (tenant_id, entity_type), partial indexes for active records |
| TOAST | Default compression, monitor toast_blks_hit ratio |
| Migration | Batch backfill with status column, dual-write transition |
| Monitoring | Track heap_hit_ratio > 0.95, dead tuples, index efficiency |
| Rust Client | Use prost for encode/decode, repository pattern for data access |
