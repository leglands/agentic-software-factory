---
name: entity-domain-modeling
description: Domain-driven design patterns for SaaS multi-tenant entity modeling in Rust
category: architecture
tags: [ddd, domain-modeling, multi-tenant, rust, sqlx, cqrs]
version: 1.0.0
author: sylvain
created: 2026-01-15
updated: 2026-03-29

eval_cases:
  - id: tenant_isolation
    description: Engineer correctly adds tenant_id to a new entity following the skill pattern
    prompts:
      - "Add a Project entity to the domain model. How do you ensure tenant isolation?"
    expected_behavior: Returns entity with tenant_id field, repository filters by tenant_id, domain methods validate tenant context

  - id: value_object_immutability
    description: Engineer creates a value object that is truly immutable and validated at construction
    prompts:
      - "Create an Email value object that validates format and is immutable"
    expected_behavior: Private constructor, factory method with validation, only getters, no setters, Clone + Copy derives

  - id: aggregate_root_enforcement
    description: Engineer correctly implements aggregate root, preventing direct entity modifications outside aggregate
    prompts:
      - "Create an Order aggregate root with OrderLine entities. How do you prevent direct OrderLine modification?"
    expected_behavior: OrderLine is private/internal, only Order methods can add/remove lines, Order is the repository entry point

  - id: domain_event_dispatch
    description: Engineer correctly publishes domain events that can be consumed by external systems
    prompts:
      - "Publish a ProjectCreated event when a new project is created"
    expected_behavior: Domain event struct with timestamp/tenant_id, event stored in domain entity, dispatcher interface for async handling

  - id: soft_delete_implementation
    description: Engineer correctly implements soft delete without breaking queries
    prompts:
      - "Implement soft delete for the User entity"
    expected_behavior: deleted_at column, repository filters out deleted rows by default, restore method available

  - id: optimistic_locking
    description: Engineer correctly implements optimistic locking to prevent concurrent update conflicts
    prompts:
      - "Add optimistic locking to the Product entity"
    expected_behavior: version column, Version trait implemented, Update fails if version mismatch, domain method returns new version

  - id: audit_trail_fields
    description: Engineer correctly adds all audit trail fields and populates them via repository
    prompts:
      - "Add complete audit trail to the Invoice entity"
    expected_behavior: created_at, updated_at, deleted_at, created_by fields, repository sets created_at/created_by on insert, updated_at on update

  - id: repository_trait_design
    description: Engineer correctly designs repository traits that abstract data access
    prompts:
      - "Design the repository trait for the Tenant entity"
    expected_behavior: Trait with generic Rx/Tx types, methods: find_by_id, find_all, save, delete, exists, count

  - id: proto_to_domain_mapping
    description: Engineer correctly maps protobuf messages to domain entities with validation
    prompts:
      - "Map CreateTenantRequest proto to Tenant domain entity"
    expected_behavior: Proto to domain validation, tenant_id injection, created_by extraction from context, domain entity returned

  - id: cqrs_read_write_separation
    description: Engineer correctly separates command and query models following CQRS pattern
    prompts:
      - "Implement CQRS for the Order domain"
    expected_behavior: Command model with full domain logic, separate query model/dto for reads, repository interfaces are separate

  - id: validation_rules
    description: Engineer correctly implements domain validation with meaningful error messages
    prompts:
      - "Add validation rules to the Registration entity"
    expected_behavior: Validate method returns Result<(), Vec<ValidationError>>, checks business rules, proper error aggregation

  - id: soft_delete_restore
    description: Engineer correctly implements restore functionality for soft-deleted entities
    prompts:
      - "Implement the restore method for soft-deleted entities"
    expected_behavior: deleted_at set to null, domain event dispatched, repository update called, audit trail updated
---

# Domain Entity Modeling for SaaS Multi-Tenant Applications

## Overview

This skill defines patterns and conventions for modeling domain entities in a SaaS multi-tenant environment using Rust. It ensures tenant isolation, auditability, consistency, and maintainability across the entire application.

## Core Principles

1. **Aggregate Root Pattern**: Every entity belongs to an aggregate with a single root
2. **Tenant Isolation**: All tenant data is strictly isolated at the data layer
3. **Event-Driven**: Domain events capture meaningful business occurrences
4. **Auditability**: Every entity maintains a complete audit trail
5. **Optimistic Concurrency**: Prevent lost updates via version-based locking
6. **Validation at Boundaries**: Entities are valid upon construction

---

## 1. Entity Per Aggregate Root

### Pattern

Each aggregate root is a distinct struct with exclusive ownership of invariants. Child entities are held internally and never exposed for direct mutation.

```rust
// aggregates/project.rs

use crate::domain::value_objects::{ProjectId, TenantId};
use crate::domain::entities::{ProjectMember, ProjectSettings};
use crate::domain::events::{DomainEvent, ProjectCreated, ProjectArchived};
use crate::domain::error::DomainError;
use chrono::{DateTime, Utc};
use uuid::Uuid;
use std::sync::Arc;

#[derive(Debug, Clone)]
pub struct Project {
    id: ProjectId,
    tenant_id: TenantId,
    name: String,
    description: Option<String>,
    status: ProjectStatus,
    members: Vec<ProjectMember>,
    settings: ProjectSettings,
    version: i32,
    created_at: DateTime<Utc>,
    updated_at: DateTime<Utc>,
    deleted_at: Option<DateTime<Utc>>,
    created_by: Uuid,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum ProjectStatus {
    Active,
    Archived,
    OnHold,
}

impl Project {
    pub fn new(
        tenant_id: TenantId,
        name: String,
        description: Option<String>,
        created_by: Uuid,
    ) -> Result<(Self, Vec<DomainEvent>), DomainError> {
        if name.trim().is_empty() {
            return Err(DomainError::ValidationError("Project name cannot be empty".into()));
        }
        if name.len() > 255 {
            return Err(DomainError::ValidationError("Project name exceeds 255 characters".into()));
        }

        let now = Utc::now();
        let id = ProjectId::new();
        
        let project = Self {
            id: id.clone(),
            tenant_id,
            name: name.trim().to_string(),
            description: description.map(|d| d.trim().to_string()).filter(|d| !d.is_empty()),
            status: ProjectStatus::Active,
            members: Vec::new(),
            settings: ProjectSettings::default(),
            version: 1,
            created_at: now,
            updated_at: now,
            deleted_at: None,
            created_by,
        };

        let event = ProjectCreated {
            event_id: Uuid::new_v4(),
            occurred_at: now,
            tenant_id: project.tenant_id.clone(),
            project_id: id,
            project_name: project.name.clone(),
            created_by: project.created_by,
        };

        Ok((project, vec![DomainEvent::ProjectCreated(event)]))
    }

    pub fn add_member(&mut self, user_id: Uuid, role: ProjectRole) -> Result<Vec<DomainEvent>, DomainError> {
        self.ensure_not_deleted()?;
        self.ensure_active()?;

        if self.members.iter().any(|m| m.user_id == user_id) {
            return Err(DomainError::DomainRuleViolation(
                "User is already a member of this project".into(),
            ));
        }

        let member = ProjectMember::new(user_id, role);
        self.members.push(member);
        self.touch()?;

        Ok(vec![])
    }

    pub fn remove_member(&mut self, user_id: Uuid) -> Result<Vec<DomainEvent>, DomainError> {
        self.ensure_not_deleted()?;
        self.ensure_active()?;

        let pos = self.members.iter().position(|m| m.user_id == user_id)
            .ok_or_else(|| DomainError::EntityNotFound("Project member not found".into()))?;
        
        self.members.remove(pos);
        self.touch()?;

        Ok(vec![])
    }

    pub fn archive(&mut self) -> Result<Vec<DomainEvent>, DomainError> {
        self.ensure_not_deleted()?;
        
        if self.status == ProjectStatus::Archived {
            return Err(DomainError::DomainRuleViolation("Project is already archived".into()));
        }

        let now = Utc::now();
        self.status = ProjectStatus::Archived;
        self.updated_at = now;
        self.version += 1;

        let event = ProjectArchived {
            event_id: Uuid::new_v4(),
            occurred_at: now,
            tenant_id: self.tenant_id.clone(),
            project_id: self.id.clone(),
            archived_by: self.created_by,
        };

        Ok(vec![DomainEvent::ProjectArchived(event)])
    }

    pub fn restore(&mut self, restored_by: Uuid) -> Result<Vec<DomainEvent>, DomainError> {
        self.ensure_deleted()?;
        
        let now = Utc::now();
        self.deleted_at = None;
        self.status = ProjectStatus::Active;
        self.updated_at = now;
        self.version += 1;

        Ok(vec![])
    }

    // Query methods
    pub fn id(&self) -> &ProjectId { &self.id }
    pub fn tenant_id(&self) -> &TenantId { &self.tenant_id }
    pub fn name(&self) -> &str { &self.name }
    pub fn description(&self) -> Option<&str> { self.description.as_deref() }
    pub fn status(&self) -> ProjectStatus { self.status.clone() }
    pub fn version(&self) -> i32 { self.version }
    pub fn created_at(&self) -> DateTime<Utc> { self.created_at }
    pub fn updated_at(&self) -> DateTime<Utc> { self.updated_at }
    pub fn deleted_at(&self) -> Option<DateTime<Utc>> { self.deleted_at }
    pub fn created_by(&self) -> Uuid { self.created_by }
    pub fn members(&self) -> &[ProjectMember] { &self.members }
    pub fn settings(&self) -> &ProjectSettings { &self.settings }

    pub fn is_deleted(&self) -> bool { self.deleted_at.is_some() }
    pub fn is_active(&self) -> bool { self.status == ProjectStatus::Active && !self.is_deleted() }

    fn ensure_not_deleted(&self) -> Result<(), DomainError> {
        if self.is_deleted() {
            Err(DomainError::EntityDeleted("Cannot modify deleted entity".into()))
        } else {
            Ok(())
        }
    }

    fn ensure_deleted(&self) -> Result<(), DomainError> {
        if !self.is_deleted() {
            Err(DomainError::DomainRuleViolation("Entity is not deleted".into()))
        } else {
            Ok(())
        }
    }

    fn ensure_active(&self) -> Result<(), DomainError> {
        if self.status != ProjectStatus::Active {
            Err(DomainError::DomainRuleViolation(
                format!("Project is not active (status: {:?})", self.status)
            ))
        } else {
            Ok(())
        }
    }

    fn touch(&mut self) -> Result<(), DomainError> {
        self.updated_at = Utc::now();
        self.version += 1;
        Ok(())
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum ProjectRole {
    Owner,
    Admin,
    Member,
    Viewer,
}

#[derive(Debug, Clone)]
pub struct ProjectMember {
    user_id: Uuid,
    role: ProjectRole,
    joined_at: DateTime<Utc>,
}

impl ProjectMember {
    pub fn new(user_id: Uuid, role: ProjectRole) -> Self {
        Self {
            user_id,
            role,
            joined_at: Utc::now(),
        }
    }

    pub fn user_id(&self) -> Uuid { self.user_id }
    pub fn role(&self) -> ProjectRole { self.role.clone() }
    pub fn joined_at(&self) -> DateTime<Utc> { self.joined_at }
}

#[derive(Debug, Clone)]
pub struct ProjectSettings {
    allow_public_sharing: bool,
    notify_on_complete: bool,
    default_view: ProjectView,
}

impl Default for ProjectSettings {
    fn default() -> Self {
        Self {
            allow_public_sharing: false,
            notify_on_complete: true,
            default_view: ProjectView::Board,
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum ProjectView {
    Board,
    List,
    Calendar,
    Gantt,
}
```

### Key Points

- **Private fields**: Child entities and state are not directly accessible
- **Factory methods**: Construction goes through `new()` or named constructors
- **Mutation via methods**: State changes occur through domain methods that return events
- **Invariant enforcement**: Business rules are validated before mutations
- **Version tracking**: Every mutation increments the version

---

## 2. Value Objects

### Pattern

Value objects are immutable, validated at construction, and compare by value.

```rust
// domain/value_objects.rs

use crate::domain::error::DomainError;
use rust_decimal::Decimal;
use std::fmt;
use std::str::FromStr;

#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct TenantId(pub String);

impl TenantId {
    pub fn new() -> Self {
        Self(uuid::Uuid::new_v4().to_string())
    }

    pub fn from_string(s: impl Into<String>) -> Result<Self, DomainError> {
        let s = s.into();
        if s.is_empty() {
            Err(DomainError::ValueObjectError("TenantId cannot be empty".into()))
        } else {
            Ok(Self(s))
        }
    }

    pub fn as_str(&self) -> &str { &self.0 }
}

impl fmt::Display for TenantId {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.0)
    }
}

#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct ProjectId(pub String);

impl ProjectId {
    pub fn new() -> Self {
        Self(uuid::Uuid::new_v4().to_string())
    }

    pub fn from_string(s: impl Into<String>) -> Result<Self, DomainError> {
        let s = s.into();
        if s.is_empty() {
            Err(DomainError::ValueObjectError("ProjectId cannot be empty".into()))
        } else {
            Ok(Self(s))
        }
    }

    pub fn as_str(&self) -> &str { &self.0 }
}

impl Default for ProjectId {
    fn default() -> Self { Self::new() }
}

#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct Email {
    local_part: String,
    domain: String,
    original: String,
}

impl Email {
    pub fn new(address: impl Into<String>) -> Result<Self, DomainError> {
        let original: String = address.into();
        let normalized = original.to_lowercase();

        Self::validate_format(&normalized)?;

        let parts: Vec<&str> = normalized.split('@').collect();
        if parts.len() != 2 {
            return Err(DomainError::ValueObjectError("Invalid email format".into()));
        }

        let (local_part, domain) = (parts[0].to_string(), parts[1].to_string());

        if local_part.is_empty() {
            return Err(DomainError::ValueObjectError("Email local part cannot be empty".into()));
        }

        if domain.len() > 253 {
            return Err(DomainError::ValueObjectError("Email domain too long".into()));
        }

        Ok(Self {
            local_part,
            domain,
            original: normalized,
        })
    }

    fn validate_format(email: &str) -> Result<(), DomainError> {
        if email.len() > 320 {
            return Err(DomainError::ValueObjectError("Email address too long".into()));
        }

        let parts: Vec<&str> = email.split('@').collect();
        if parts.len() != 2 {
            return Err(DomainError::ValueObjectError("Email must contain exactly one @".into()));
        }

        let local = parts[0];
        if local.is_empty() {
            return Err(DomainError::ValueObjectError("Email local part cannot be empty".into()));
        }

        if local.starts_with('.') || local.ends_with('.') || local.contains("..") {
            return Err(DomainError::ValueObjectError("Email local part cannot start/end with dot or contain consecutive dots".into()));
        }

        Ok(())
    }

    pub fn as_str(&self) -> &str { &self.original }
    pub fn local_part(&self) -> &str { &self.local_part }
    pub fn domain(&self) -> &str { &self.domain }
}

impl fmt::Display for Email {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.original)
    }
}

impl FromStr for Email {
    type Err = DomainError;
    fn from_str(s: &str) -> Result<Self, Self::Err> { Self::new(s) }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Money {
    amount: Decimal,
    currency: Currency,
}

#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub enum Currency {
    USD,
    EUR,
    GBP,
    JPY,
    CHF,
}

impl Currency {
    pub fn code(&self) -> &'static str {
        match self {
            Currency::USD => "USD",
            Currency::EUR => "EUR",
            Currency::GBP => "GBP",
            Currency::JPY => "JPY",
            Currency::CHF => "CHF",
        }
    }

    pub fn decimal_places(&self) -> u32 {
        match self {
            Currency::JPY => 0,
            _ => 2,
        }
    }
}

impl Money {
    pub fn new(amount: Decimal, currency: Currency) -> Result<Self, DomainError> {
        if amount < Decimal::ZERO {
            return Err(DomainError::ValueObjectError("Money amount cannot be negative".into()));
        }

        if currency == Currency::JPY && amount.fract() != Decimal::ZERO {
            return Err(DomainError::ValueObjectError("JPY cannot have decimal places".into()));
        }

        Ok(Self { amount, currency })
    }

    pub fn zero(currency: Currency) -> Self {
        Self {
            amount: Decimal::ZERO,
            currency,
        }
    }

    pub fn amount(&self) -> Decimal { self.amount }
    pub fn currency(&self) -> &Currency { &self.currency }

    pub fn add(&self, other: &Money) -> Result<Money, DomainError> {
        if self.currency != other.currency {
            return Err(DomainError::ValueObjectError(
                format!("Cannot add {} to {}", other.currency.code(), self.currency.code())
            ));
        }
        Money::new(self.amount + other.amount, self.currency.clone())
    }
}

#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct PhoneNumber {
    country_code: String,
    national_number: String,
    original: String,
}

impl PhoneNumber {
    pub fn new(number: impl Into<String>) -> Result<Self, DomainError> {
        let original: String = number.into();
        let digits: String = original.chars().filter(|c| c.is_ascii_digit()).collect();

        if digits.len() < 10 || digits.len() > 15 {
            return Err(DomainError::ValueObjectError(
                "Phone number must have between 10 and 15 digits".into()
            ));
        }

        let country_code = format!("+{}", &digits[..digits.len() - 10]);
        let national_number = digits[digits.len() - 10..].to_string();

        Ok(Self {
            country_code,
            national_number,
            original,
        })
    }

    pub fn country_code(&self) -> &str { &self.country_code }
    pub fn national_number(&self) -> &str { &self.national_number }
    pub fn formatted(&self) -> String {
        format!("{} {}", self.country_code, self.national_number)
    }
}
```

### Key Points

- **Immutable**: No setters, `#[derive(Clone, Copy)]` where appropriate
- **Validated at construction**: Fail-fast with clear error messages
- **Value equality**: `PartialEq` compares all fields
- **Domain modeling**: Expresses business concepts, not just data

---

## 3. Domain Events

### Pattern

Domain events represent meaningful business occurrences and are immutable.

```rust
// domain/events.rs

use crate::domain::value_objects::{TenantId, ProjectId};
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use uuid::Uuid;

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "type")]
pub enum DomainEvent {
    ProjectCreated(ProjectCreated),
    ProjectArchived(ProjectArchived),
    ProjectRestored(ProjectRestored),
    ProjectMemberAdded(ProjectMemberAdded),
    ProjectMemberRemoved(ProjectMemberRemoved),
    TenantCreated(TenantCreated),
    TenantSettingsUpdated(TenantSettingsUpdated),
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProjectCreated {
    pub event_id: Uuid,
    pub occurred_at: DateTime<Utc>,
    pub tenant_id: TenantId,
    pub project_id: ProjectId,
    pub project_name: String,
    pub created_by: Uuid,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProjectArchived {
    pub event_id: Uuid,
    pub occurred_at: DateTime<Utc>,
    pub tenant_id: TenantId,
    pub project_id: ProjectId,
    pub archived_by: Uuid,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProjectRestored {
    pub event_id: Uuid,
    pub occurred_at: DateTime<Utc>,
    pub tenant_id: TenantId,
    pub project_id: ProjectId,
    pub restored_by: Uuid,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProjectMemberAdded {
    pub event_id: Uuid,
    pub occurred_at: DateTime<Utc>,
    pub tenant_id: TenantId,
    pub project_id: ProjectId,
    pub user_id: Uuid,
    pub role: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProjectMemberRemoved {
    pub event_id: Uuid,
    pub occurred_at: DateTime<Utc>,
    pub tenant_id: TenantId,
    pub project_id: ProjectId,
    pub user_id: Uuid,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TenantCreated {
    pub event_id: Uuid,
    pub occurred_at: DateTime<Utc>,
    pub tenant_id: TenantId,
    pub tenant_name: String,
    pub created_by: Uuid,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TenantSettingsUpdated {
    pub event_id: Uuid,
    pub occurred_at: DateTime<Utc>,
    pub tenant_id: TenantId,
    pub updated_by: Uuid,
    pub settings_json: String,
}

impl DomainEvent {
    pub fn event_id(&self) -> Uuid {
        match self {
            DomainEvent::ProjectCreated(e) => e.event_id,
            DomainEvent::ProjectArchived(e) => e.event_id,
            DomainEvent::ProjectRestored(e) => e.event_id,
            DomainEvent::ProjectMemberAdded(e) => e.event_id,
            DomainEvent::ProjectMemberRemoved(e) => e.event_id,
            DomainEvent::TenantCreated(e) => e.event_id,
            DomainEvent::TenantSettingsUpdated(e) => e.event_id,
        }
    }

    pub fn occurred_at(&self) -> DateTime<Utc> {
        match self {
            DomainEvent::ProjectCreated(e) => e.occurred_at,
            DomainEvent::ProjectArchived(e) => e.occurred_at,
            DomainEvent::ProjectRestored(e) => e.occurred_at,
            DomainEvent::ProjectMemberAdded(e) => e.occurred_at,
            DomainEvent::ProjectMemberRemoved(e) => e.occurred_at,
            DomainEvent::TenantCreated(e) => e.occurred_at,
            DomainEvent::TenantSettingsUpdated(e) => e.occurred_at,
        }
    }

    pub fn tenant_id(&self) -> &TenantId {
        match self {
            DomainEvent::ProjectCreated(e) => &e.tenant_id,
            DomainEvent::ProjectArchived(e) => &e.tenant_id,
            DomainEvent::ProjectRestored(e) => &e.tenant_id,
            DomainEvent::ProjectMemberAdded(e) => &e.tenant_id,
            DomainEvent::ProjectMemberRemoved(e) => &e.tenant_id,
            DomainEvent::TenantCreated(e) => &e.tenant_id,
            DomainEvent::TenantSettingsUpdated(e) => &e.tenant_id,
        }
    }
}

pub trait EventDispatcher: Send + Sync {
    fn dispatch(&self, event: DomainEvent) -> BoxFuture<()>;
    fn dispatch_batch(&self, events: Vec<DomainEvent>) -> BoxFuture<()>;
}

pub trait EventStore: Send + Sync {
    fn append(&self, event: DomainEvent) -> BoxFuture<Result<(), DomainError>>;
    fn get_events_for_aggregate(&self, tenant_id: &TenantId, aggregate_id: &str) -> BoxFuture<Result<Vec<DomainEvent>, DomainError>>;
    fn get_events_for_tenant(&self, tenant_id: &TenantId) -> BoxFuture<Result<Vec<DomainEvent>, DomainError>>;
}
```

---

## 4. Tenant Isolation

### Pattern

Every table contains `tenant_id`. Repository methods always filter by tenant.

```rust
// domain/repositories/project_repository.rs

use crate::domain::value_objects::TenantId;
use crate::domain::entities::Project;
use crate::domain::error::DomainError;
use async_trait::async_trait;
use sqlx::PgPool;
use uuid::Uuid;

#[async_trait]
pub trait ProjectRepository: Send + Sync {
    async fn find_by_id(&self, tenant_id: &TenantId, id: &Uuid) -> Result<Option<Project>, DomainError>;
    async fn find_all(&self, tenant_id: &TenantId) -> Result<Vec<Project>, DomainError>;
    async fn find_active(&self, tenant_id: &TenantId) -> Result<Vec<Project>, DomainError>;
    async fn save(&self, tenant_id: &TenantId, project: &mut Project) -> Result<(), DomainError>;
    async fn delete(&self, tenant_id: &TenantId, id: &Uuid) -> Result<(), DomainError>;
    async fn exists(&self, tenant_id: &TenantId, id: &Uuid) -> Result<bool, DomainError>;
    async fn count(&self, tenant_id: &TenantId) -> Result<i64, DomainError>;
}

pub struct SqlxProjectRepository {
    pool: PgPool,
}

impl SqlxProjectRepository {
    pub fn new(pool: PgPool) -> Self { Self { pool } }
}

#[async_trait]
impl ProjectRepository for SqlxProjectRepository {
    async fn find_by_id(&self, tenant_id: &TenantId, id: &Uuid) -> Result<Option<Project>, DomainError> {
        let result = sqlx::query_as::<_, ProjectRow>(
            r#"
            SELECT id, tenant_id, name, description, status, version,
                   created_at, updated_at, deleted_at, created_by
            FROM projects
            WHERE tenant_id = $1 AND id = $2 AND deleted_at IS NULL
            "#,
        )
        .bind(tenant_id.as_str())
        .bind(id)
        .fetch_optional(&self.pool)
        .await
        .map_err(|e| DomainError::DatabaseError(e.to_string()))?;

        Ok(result.map(|row| row.into_domain()))
    }

    async fn find_all(&self, tenant_id: &TenantId) -> Result<Vec<Project>, DomainError> {
        let results = sqlx::query_as::<_, ProjectRow>(
            r#"
            SELECT id, tenant_id, name, description, status, version,
                   created_at, updated_at, deleted_at, created_by
            FROM projects
            WHERE tenant_id = $1
            ORDER BY created_at DESC
            "#,
        )
        .bind(tenant_id.as_str())
        .fetch_all(&self.pool)
        .await
        .map_err(|e| DomainError::DatabaseError(e.to_string()))?;

        Ok(results.into_iter().map(|row| row.into_domain()).collect())
    }

    async fn find_active(&self, tenant_id: &TenantId) -> Result<Vec<Project>, DomainError> {
        let results = sqlx::query_as::<_, ProjectRow>(
            r#"
            SELECT id, tenant_id, name, description, status, version,
                   created_at, updated_at, deleted_at, created_by
            FROM projects
            WHERE tenant_id = $1 AND deleted_at IS NULL AND status = 'Active'
            ORDER BY name ASC
            "#,
        )
        .bind(tenant_id.as_str())
        .fetch_all(&self.pool)
        .await
        .map_err(|e| DomainError::DatabaseError(e.to_string()))?;

        Ok(results.into_iter().map(|row| row.into_domain()).collect())
    }

    async fn save(&self, tenant_id: &TenantId, project: &mut Project) -> Result<(), DomainError> {
        if project.version() == 1 {
            sqlx::query(
                r#"
                INSERT INTO projects (id, tenant_id, name, description, status, version,
                                    created_at, updated_at, deleted_at, created_by)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                "#,
            )
            .bind(project.id().as_str())
            .bind(tenant_id.as_str())
            .bind(&project.name())
            .bind(project.description())
            .bind(format!("{:?}", project.status()))
            .bind(project.version())
            .bind(project.created_at())
            .bind(project.updated_at())
            .bind(project.deleted_at())
            .bind(project.created_by())
            .execute(&self.pool)
            .await
            .map_err(|e| DomainError::DatabaseError(e.to_string()))?;
        } else {
            let affected = sqlx::query(
                r#"
                UPDATE projects
                SET name = $3, description = $4, status = $5, version = $6,
                    updated_at = $7, deleted_at = $8
                WHERE tenant_id = $1 AND id = $2 AND version = $9
                "#,
            )
            .bind(tenant_id.as_str())
            .bind(project.id().as_str())
            .bind(&project.name())
            .bind(project.description())
            .bind(format!("{:?}", project.status()))
            .bind(project.version())
            .bind(project.updated_at())
            .bind(project.deleted_at())
            .bind(project.version() - 1)
            .execute(&self.pool)
            .await
            .map_err(|e| DomainError::DatabaseError(e.to_string()))?;

            if affected.rows_affected() == 0 {
                return Err(DomainError::ConcurrencyError(
                    "Project was modified by another transaction".into()
                ));
            }
        }
        Ok(())
    }

    async fn delete(&self, tenant_id: &TenantId, id: &Uuid) -> Result<(), DomainError> {
        let affected = sqlx::query(
            r#"
            UPDATE projects
            SET deleted_at = NOW(), version = version + 1, updated_at = NOW()
            WHERE tenant_id = $1 AND id = $2 AND deleted_at IS NULL
            "#,
        )
        .bind(tenant_id.as_str())
        .bind(id)
        .execute(&self.pool)
        .await
        .map_err(|e| DomainError::DatabaseError(e.to_string()))?;

        if affected.rows_affected() == 0 {
            return Err(DomainError::EntityNotFound(format!("Project {} not found", id)));
        }

        Ok(())
    }

    async fn exists(&self, tenant_id: &TenantId, id: &Uuid) -> Result<bool, DomainError> {
        let result = sqlx::query_scalar::<_, i64>(
            r#"SELECT COUNT(*) FROM projects WHERE tenant_id = $1 AND id = $2 AND deleted_at IS NULL"#
        )
        .bind(tenant_id.as_str())
        .bind(id)
        .fetch_one(&self.pool)
        .await
        .map_err(|e| DomainError::DatabaseError(e.to_string()))?;

        Ok(result > 0)
    }

    async fn count(&self, tenant_id: &TenantId) -> Result<i64, DomainError> {
        let result = sqlx::query_scalar::<_, i64>(
            r#"SELECT COUNT(*) FROM projects WHERE tenant_id = $1 AND deleted_at IS NULL"#
        )
        .bind(tenant_id.as_str())
        .fetch_one(&self.pool)
        .await
        .map_err(|e| DomainError::DatabaseError(e.to_string()))?;

        Ok(result)
    }
}

#[derive(sqlx::FromRow)]
struct ProjectRow {
    id: String,
    tenant_id: String,
    name: String,
    description: Option<String>,
    status: String,
    version: i32,
    created_at: chrono::DateTime<chrono::Utc>,
    updated_at: chrono::DateTime<chrono::Utc>,
    deleted_at: Option<chrono::DateTime<chrono::Utc>>,
    created_by: Uuid,
}

impl ProjectRow {
    fn into_domain(self) -> Project {
        // Reconstruct domain entity from row
        // This would use a private constructor or builder
        todo!("Implement domain reconstruction")
    }
}
```

### Key Points

- **Always filter by tenant_id**: Every query includes `WHERE tenant_id = $1`
- **Cross-tenant access impossible**: Repository methods take tenant context as parameter
- **Soft delete respected**: Queries include `deleted_at IS NULL`

---

## 5. Soft Delete

### Pattern

Entities are never physically deleted; `deleted_at` timestamp marks deletion.

```sql
-- Database migration for soft delete
ALTER TABLE projects ADD COLUMN deleted_at TIMESTAMPTZ;
CREATE INDEX idx_projects_tenant_deleted ON projects(tenant_id, deleted_at);
CREATE INDEX idx_projects_tenant_status ON projects(tenant_id, status) WHERE deleted_at IS NULL;
```

```rust
// domain/entities/traits.rs

pub trait SoftDeletable {
    fn delete(&mut self, deleted_by: Uuid) -> Result<Vec<DomainEvent>, DomainError>;
    fn restore(&mut self, restored_by: Uuid) -> Result<Vec<DomainEvent>, DomainError>;
    fn is_deleted(&self) -> bool;
}

pub trait DeletableRepository {
    async fn soft_delete(&self, tenant_id: &TenantId, id: &Uuid) -> Result<(), DomainError>;
    async fn restore(&self, tenant_id: &TenantId, id: &Uuid) -> Result<(), DomainError>;
    async fn find_deleted(&self, tenant_id: &TenantId) -> Result<Vec<Self::Entity>, DomainError>;
}
```

---

## 6. Audit Trail

### Pattern

Every entity maintains `created_at`, `updated_at`, `deleted_at`, and `created_by`.

```rust
// Audit fields on every entity
pub struct Project {
    id: ProjectId,
    tenant_id: TenantId,
    name: String,
    description: Option<String>,
    status: ProjectStatus,
    version: i32,           // Optimistic locking
    created_at: DateTime<Utc>,
    updated_at: DateTime<Utc>,
    deleted_at: Option<DateTime<Utc>>,  // Soft delete
    created_by: Uuid,                  // Audit trail
}

// Repository sets these on insert
impl Project {
    pub fn created_by(&self) -> Uuid { self.created_by }
}

// Use cases set updated_at/updated_by
impl Project {
    pub fn touch(&mut self) {
        self.updated_at = Utc::now();
        self.version += 1;
    }
}
```

### SQL Pattern

```sql
-- Insert with audit fields
INSERT INTO projects (id, tenant_id, name, description, status, version,
                     created_at, updated_at, deleted_at, created_by)
VALUES ($1, $2, $3, $4, $5, 1, NOW(), NOW(), NULL, $6);

-- Update with audit fields
UPDATE projects
SET name = $3,
    updated_at = NOW(),
    version = version + 1
WHERE tenant_id = $1 AND id = $2;
```

---

## 7. Optimistic Locking

### Pattern

Version column prevents lost updates in concurrent scenarios.

```rust
// domain/entities/traits.rs

pub trait Versioned {
    fn version(&self) -> i32;
    fn increment_version(&mut self);
}

pub trait OptimisticLocking {
    type Error;
    fn save_with_version(&self, expected_version: i32) -> Result<(), Self::Error>;
}

// Repository implementation
async fn save(&self, project: &mut Project) -> Result<(), DomainError> {
    let result = sqlx::query(
        r#"
        UPDATE projects
        SET name = $3, version = version + 1, updated_at = NOW()
        WHERE tenant_id = $1 AND id = $2 AND version = $4
        "#
    )
    .bind(tenant_id)
    .bind(project.id())
    .bind(&project.name())
    .bind(project.version())  // Current version as expected
    .execute(&self.pool)
    .await?;

    if result.rows_affected() == 0 {
        return Err(DomainError::ConcurrencyError(
            "Entity was modified by another user".into()
        ));
    }

    project.increment_version();
    Ok(())
}
```

---

## 8. Entity Validation Rules

### Pattern

Validation returns aggregated errors; entities are always in valid state.

```rust
// domain/error.rs

use thiserror::Error;

#[derive(Debug, Error)]
pub enum DomainError {
    #[error("Validation error: {0}")]
    ValidationError(String),

    #[error("Validation errors: {0:?}")]
    ValidationErrors(Vec<ValidationError>),

    #[error("Value object error: {0}")]
    ValueObjectError(String),

    #[error("Entity not found: {0}")]
    EntityNotFound(String),

    #[error("Entity deleted: {0}")]
    EntityDeleted(String),

    #[error("Domain rule violation: {0}")]
    DomainRuleViolation(String),

    #[error("Concurrency error: {0}")]
    ConcurrencyError(String),

    #[error("Database error: {0}")]
    DatabaseError(String),

    #[error("Unauthorized: {0}")]
    Unauthorized(String),
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ValidationError {
    pub field: String,
    pub message: String,
}

impl ValidationError {
    pub fn new(field: impl Into<String>, message: impl Into<String>) -> Self {
        Self {
            field: field.into(),
            message: message.into(),
        }
    }
}

pub type ValidationResult<T> = Result<T, Vec<ValidationError>>;

pub trait Validatable {
    fn validate(&self) -> ValidationResult<()>;
}
```

```rust
// Example validation in entity
impl Project {
    pub fn new(
        tenant_id: TenantId,
        name: String,
        description: Option<String>,
        created_by: Uuid,
    ) -> Result<(Self, Vec<DomainEvents>), DomainError> {
        let mut errors = Vec::new();

        if name.trim().is_empty() {
            errors.push(ValidationError::new("name", "Project name is required"));
        } else if name.len() > 255 {
            errors.push(ValidationError::new("name", "Project name cannot exceed 255 characters"));
        }

        if let Some(ref desc) = description {
            if desc.len() > 2000 {
                errors.push(ValidationError::new("description", "Description cannot exceed 2000 characters"));
            }
        }

        if !errors.is_empty() {
            return Err(DomainError::ValidationErrors(errors));
        }

        // Proceed with construction
    }
}
```

---

## 9. Repository Pattern with SQLx

### Pattern

Repository traits define contracts; implementations handle persistence.

```rust
// domain/repositories/mod.rs

pub mod traits;
pub mod project_repository;
pub mod tenant_repository;
pub mod user_repository;

pub use traits::*;
pub use project_repository::*;
pub use tenant_repository::*;
pub use user_repository::*;
```

```rust
// domain/repositories/traits.rs

use crate::domain::value_objects::TenantId;
use crate::domain::entities::*;
use crate::domain::error::DomainError;
use async_trait::async_trait;
use uuid::Uuid;

#[async_trait]
pub trait TenantRepository: Send + Sync {
    async fn find_by_id(&self, id: &TenantId) -> Result<Option<Tenant>, DomainError>;
    async fn find_by_slug(&self, slug: &str) -> Result<Option<Tenant>, DomainError>;
    async fn find_all(&self) -> Result<Vec<Tenant>, DomainError>;
    async fn save(&self, tenant: &mut Tenant) -> Result<(), DomainError>;
    async fn delete(&self, id: &TenantId) -> Result<(), DomainError>;
    async fn exists(&self, id: &TenantId) -> Result<bool, DomainError>;
}

#[async_trait]
pub trait UserRepository: Send + Sync {
    async fn find_by_id(&self, tenant_id: &TenantId, id: &Uuid) -> Result<Option<User>, DomainError>;
    async fn find_by_email(&self, tenant_id: &TenantId, email: &str) -> Result<Option<User>, DomainError>;
    async fn find_all(&self, tenant_id: &TenantId) -> Result<Vec<User>, DomainError>;
    async fn save(&self, tenant_id: &TenantId, user: &mut User) -> Result<(), DomainError>;
    async fn delete(&self, tenant_id: &TenantId, id: &Uuid) -> Result<(), DomainError>;
    async fn exists(&self, tenant_id: &TenantId, id: &Uuid) -> Result<bool, DomainError>;
    async fn count(&self, tenant_id: &TenantId) -> Result<i64, DomainError>;
}
```

---

## 10. Proto to Domain Entity Mapping

### Pattern

gRPC messages map to domain entities at the service boundary with validation.

```rust
// adapters/grpc/mappers.rs

use crate::domain::entities::{Tenant, User, Project};
use crate::domain::value_objects::{TenantId, Email};
use crate::domain::error::DomainError;
use crate::proto::tenant::{CreateTenantRequest, UpdateTenantRequest};
use crate::proto::project::{CreateProjectRequest, UpdateProjectRequest};
use uuid::Uuid;
use chrono::Utc;

pub trait ProtoMapper {
    type Domain;
    type Proto;
    fn to_domain(proto: Self::Proto) -> Result<Self::Domain, DomainError>;
}

pub struct CreateTenantRequestMapper;

impl ProtoMapper for CreateTenantRequestMapper {
    type Domain = Tenant;
    type Proto = CreateTenantRequest;

    fn to_domain(proto: CreateTenantRequest) -> Result<Self::Domain, DomainError> {
        let tenant_id = TenantId::new();
        let name = proto.name.trim().to_string();
        
        if name.is_empty() {
            return Err(DomainError::ValidationError("Tenant name is required".into()));
        }

        if name.len() > 255 {
            return Err(DomainError::ValidationError("Tenant name too long".into()));
        }

        let created_by = Uuid::parse_str(&proto.created_by)
            .map_err(|_| DomainError::ValidationError("Invalid created_by UUID".into()))?;

        Tenant::new(tenant_id, name, created_by)
    }
}

pub struct CreateProjectRequestMapper;

impl ProtoMapper for CreateProjectRequestMapper {
    type Domain = Project;
    type Proto = CreateProjectRequest;

    fn to_domain(proto: CreateProjectRequest) -> Result<Self::Domain, DomainError> {
        let tenant_id = TenantId::from_string(&proto.tenant_id)
            .map_err(|_| DomainError::ValidationError("Invalid tenant_id".into()))?;

        let name = proto.name.trim().to_string();
        if name.is_empty() {
            return Err(DomainError::ValidationError("Project name is required".into()));
        }

        let description = if proto.description.is_empty() {
            None
        } else {
            Some(proto.description)
        };

        let created_by = Uuid::parse_str(&proto.created_by)
            .map_err(|_| DomainError::ValidationError("Invalid created_by UUID".into()))?;

        Project::new(tenant_id, name, description, created_by)
            .map(|(entity, _events)| entity)
    }
}

pub struct ProjectToProtoMapper;

impl ProjectToProtoMapper {
    pub fn to_proto(project: &Project) -> crate::proto::project::Project {
        crate::proto::project::Project {
            id: project.id().as_str().to_string(),
            tenant_id: project.tenant_id().as_str().to_string(),
            name: project.name().to_string(),
            description: project.description().unwrap_or_default(),
            status: format!("{:?}", project.status()),
            version: project.version(),
            created_at: Some(prost_types::Timestamp::from(project.created_at())),
            updated_at: Some(prost_types::Timestamp::from(project.updated_at())),
            deleted_at: project.deleted_at().map(|dt| prost_types::Timestamp::from(dt)),
            created_by: project.created_by().to_string(),
        }
    }
}
```

---

## 11. CQRS Read/Write Separation

### Pattern

Commands modify state; queries read optimized projections.

```rust
// domain/cqrs/mod.rs

pub mod commands;
pub mod queries;
pub mod projections;

pub use commands::*;
pub use queries::*;
```

```rust
// domain/cqrs/commands.rs

use crate::domain::entities::{Project, User, Tenant};
use crate::domain::value_objects::TenantId;
use crate::domain::events::DomainEvent;
use crate::domain::error::DomainError;
use uuid::Uuid;
use std::sync::Arc;

pub struct CommandContext {
    pub tenant_id: TenantId,
    pub user_id: Uuid,
    pub user_context: UserContext,
}

#[derive(Debug, Clone)]
pub struct UserContext {
    pub permissions: Vec<String>,
    pub roles: Vec<String>,
}

pub trait CommandHandler<C, R> {
    async fn handle(&self, ctx: &CommandContext, cmd: C) -> Result<R, DomainError>;
}

pub struct CreateProjectCommand {
    pub name: String,
    pub description: Option<String>,
}

pub struct UpdateProjectCommand {
    pub project_id: Uuid,
    pub name: Option<String>,
    pub description: Option<String>,
}

pub struct ArchiveProjectCommand {
    pub project_id: Uuid,
}

pub struct ProjectCommandHandler<R> {
    pub repository: Arc<R>,
    pub event_dispatcher: Arc<dyn crate::domain::events::EventDispatcher>,
}

impl<R> ProjectCommandHandler<R>
where
    R: crate::domain::repositories::ProjectRepository + Send + Sync,
{
    pub async fn handle_create(
        &self,
        ctx: &CommandContext,
        cmd: CreateProjectCommand,
    ) -> Result<Project, DomainError> {
        let (mut project, events) = Project::new(
            ctx.tenant_id.clone(),
            cmd.name,
            cmd.description,
            ctx.user_id,
        )?;

        self.repository.save(&ctx.tenant_id, &mut project).await?;
        self.event_dispatcher.dispatch_batch(events).await?;

        Ok(project)
    }

    pub async fn handle_update(
        &self,
        ctx: &CommandContext,
        cmd: UpdateProjectCommand,
    ) -> Result<Project, DomainError> {
        let mut project = self.repository
            .find_by_id(&ctx.tenant_id, &cmd.project_id)
            .await?
            .ok_or_else(|| DomainError::EntityNotFound("Project not found".into()))?;

        if let Some(name) = cmd.name {
            project.update_name(name)?;
        }
        if let Some(desc) = cmd.description {
            project.update_description(desc)?;
        }

        self.repository.save(&ctx.tenant_id, &mut project).await?;
        Ok(project)
    }

    pub async fn handle_archive(
        &self,
        ctx: &CommandContext,
        cmd: ArchiveProjectCommand,
    ) -> Result<(), DomainError> {
        let mut project = self.repository
            .find_by_id(&ctx.tenant_id, &cmd.project_id)
            .await?
            .ok_or_else(|| DomainError::EntityNotFound("Project not found".into()))?;

        let events = project.archive()?;
        
        self.repository.save(&ctx.tenant_id, &mut project).await?;
        self.event_dispatcher.dispatch_batch(events).await?;

        Ok(())
    }
}
```

```rust
// domain/cqrs/queries.rs

use crate::domain::value_objects::TenantId;
use crate::domain::error::DomainError;
use sqlx::PgPool;
use uuid::Uuid;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProjectSummary {
    pub id: Uuid,
    pub name: String,
    pub status: String,
    pub member_count: i64,
    pub created_at: chrono::DateTime<chrono::Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProjectDetails {
    pub id: Uuid,
    pub tenant_id: Uuid,
    pub name: String,
    pub description: Option<String>,
    pub status: String,
    pub version: i32,
    pub created_at: chrono::DateTime<chrono::Utc>,
    pub updated_at: chrono::DateTime<chrono::Utc>,
    pub created_by: Uuid,
    pub members: Vec<ProjectMemberSummary>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProjectMemberSummary {
    pub user_id: Uuid,
    pub role: String,
    pub joined_at: chrono::DateTime<chrono::Utc>,
}

pub struct ProjectQueryHandler {
    pool: PgPool,
}

impl ProjectQueryHandler {
    pub fn new(pool: PgPool) -> Self { Self { pool } }

    pub async fn get_summary(
        &self,
        tenant_id: &TenantId,
        project_id: &Uuid,
    ) -> Result<Option<ProjectSummary>, DomainError> {
        let result = sqlx::query_as::<_, ProjectSummaryRow>(
            r#"
            SELECT p.id, p.name, p.status, p.created_at,
                   COUNT(m.id)::bigint as member_count
            FROM projects p
            LEFT JOIN project_members m ON p.id = m.project_id
            WHERE p.tenant_id = $1 AND p.id = $2 AND p.deleted_at IS NULL
            GROUP BY p.id, p.name, p.status, p.created_at
            "#
        )
        .bind(tenant_id.as_str())
        .bind(project_id)
        .fetch_optional(&self.pool)
        .await
        .map_err(|e| DomainError::DatabaseError(e.to_string()))?;

        Ok(result.map(|row| ProjectSummary {
            id: row.id,
            name: row.name,
            status: row.status,
            member_count: row.member_count,
            created_at: row.created_at,
        }))
    }

    pub async fn get_details(
        &self,
        tenant_id: &TenantId,
        project_id: &Uuid,
    ) -> Result<Option<ProjectDetails>, DomainError> {
        let project_row = sqlx::query_as::<_, ProjectDetailsRow>(
            r#"
            SELECT id, tenant_id, name, description, status, version,
                   created_at, updated_at, created_by
            FROM projects
            WHERE tenant_id = $1 AND id = $2 AND deleted_at IS NULL
            "#
        )
        .bind(tenant_id.as_str())
        .bind(project_id)
        .fetch_optional(&self.pool)
        .await
        .map_err(|e| DomainError::DatabaseError(e.to_string()))?;

        match project_row {
            Some(row) => {
                let members = self.get_members(project_id).await?;
                Ok(Some(ProjectDetails {
                    id: row.id,
                    tenant_id: row.tenant_id,
                    name: row.name,
                    description: row.description,
                    status: row.status,
                    version: row.version,
                    created_at: row.created_at,
                    updated_at: row.updated_at,
                    created_by: row.created_by,
                    members,
                }))
            }
            None => Ok(None),
        }
    }

    pub async fn list_summaries(
        &self,
        tenant_id: &TenantId,
    ) -> Result<Vec<ProjectSummary>, DomainError> {
        let results = sqlx::query_as::<_, ProjectSummaryRow>(
            r#"
            SELECT p.id, p.name, p.status, p.created_at,
                   COUNT(m.id)::bigint as member_count
            FROM projects p
            LEFT JOIN project_members m ON p.id = m.project_id
            WHERE p.tenant_id = $1 AND p.deleted_at IS NULL
            GROUP BY p.id, p.name, p.status, p.created_at
            ORDER BY p.created_at DESC
            "#
        )
        .bind(tenant_id.as_str())
        .fetch_all(&self.pool)
        .await
        .map_err(|e| DomainError::DatabaseError(e.to_string()))?;

        Ok(results.into_iter().map(|row| ProjectSummary {
            id: row.id,
            name: row.name,
            status: row.status,
            member_count: row.member_count,
            created_at: row.created_at,
        }).collect())
    }

    async fn get_members(&self, project_id: &Uuid) -> Result<Vec<ProjectMemberSummary>, DomainError> {
        let rows = sqlx::query_as::<_, ProjectMemberRow>(
            r#"
            SELECT user_id, role, joined_at
            FROM project_members
            WHERE project_id = $1
            ORDER BY joined_at ASC
            "#
        )
        .bind(project_id)
        .fetch_all(&self.pool)
        .await
        .map_err(|e| DomainError::DatabaseError(e.to_string()))?;

        Ok(rows.into_iter().map(|row| ProjectMemberSummary {
            user_id: row.user_id,
            role: row.role,
            joined_at: row.joined_at,
        }).collect())
    }
}

#[derive(sqlx::FromRow)]
struct ProjectSummaryRow {
    id: Uuid,
    name: String,
    status: String,
    created_at: chrono::DateTime<chrono::Utc>,
    member_count: i64,
}

#[derive(sqlx::FromRow)]
struct ProjectDetailsRow {
    id: Uuid,
    tenant_id: Uuid,
    name: String,
    description: Option<String>,
    status: String,
    version: i32,
    created_at: chrono::DateTime<chrono::Utc>,
    updated_at: chrono::DateTime<chrono::Utc>,
    created_by: Uuid,
}

#[derive(sqlx::FromRow)]
struct ProjectMemberRow {
    user_id: Uuid,
    role: String,
    joined_at: chrono::DateTime<chrono::Utc>,
}
```

---

## Database Schema Conventions

```sql
-- Every table has these columns in this order:
CREATE TABLE projects (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Tenant isolation (always NOT NULL, indexed)
    tenant_id UUID NOT NULL,
    
    -- Domain fields
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'Active',
    
    -- Optimistic locking
    version INTEGER NOT NULL DEFAULT 1,
    
    -- Audit trail
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    created_by UUID NOT NULL,
    
    -- Constraints
    CONSTRAINT projects_name_length CHECK (char_length(name) >= 1 AND char_length(name) <= 255),
    CONSTRAINT projects_version_positive CHECK (version >= 1)
);

-- Required indexes for tenant isolation
CREATE INDEX idx_projects_tenant_id ON projects(tenant_id);
CREATE INDEX idx_projects_tenant_deleted ON projects(tenant_id, deleted_at) WHERE deleted_at IS NULL;
CREATE INDEX idx_projects_tenant_status ON projects(tenant_id, status) WHERE deleted_at IS NULL;

-- Soft delete function
CREATE OR REPLACE FUNCTION soft_delete_row()
RETURNS TRIGGER AS $$
BEGIN
    NEW.deleted_at = NOW();
    NEW.updated_at = NOW();
    NEW.version = NEW.version + 1;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

---

## Summary Checklist

- [ ] Entity per aggregate root with private child entities
- [ ] Value objects are immutable, validated at construction
- [ ] Domain events capture meaningful business occurrences
- [ ] `tenant_id` on every table, filtered in every query
- [ ] Soft delete via `deleted_at` timestamp
- [ ] Audit trail: `created_at`, `updated_at`, `deleted_at`, `created_by`
- [ ] Optimistic locking via `version` column
- [ ] Entity validation returns aggregated errors
- [ ] Repository traits define contracts; SQLx implements persistence
- [ ] Proto messages map to domain entities at service boundaries
- [ ] CQRS separates command and query models
