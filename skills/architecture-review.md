---
name: architecture-review
description: 'Guides the agent through reviewing software architecture for clean design,
  SOLID principles, domain-driven design patterns, and scalability. Use this skill
  when assessing system structure, evaluating architectural decisions, or creating
  Architecture Decision Records (ADRs).

  '
metadata:
  category: development
  triggers:
  - when user asks to review architecture
  - when assessing code structure and organization
  - when user mentions SOLID, DDD, or clean architecture
  - when evaluating scalability of a system
  - when creating Architecture Decision Records
eval_cases:
- id: tight-coupling
  prompt: "Review this Python service architecture:\nclass OrderService:\n    def\
    \ __init__(self):\n        self.db = MySQLConnector(host=\"localhost\", user=\"\
    root\", password=\"admin\")\n        self.mailer = SendgridMailer(api_key=\"SG.xxx\"\
    )\n        self.stripe = StripeClient(secret=\"sk_live_xxx\")\n    def place_order(self,\
    \ order): ...\n"
  should_trigger: true
  checks:
  - regex:tight.*coupl|depend.*inject|DI|interface|abstract|hard.*cod|invers
  - no_placeholder
  - length_min:100
  expectations:
  - identifies tight coupling between OrderService and concrete implementations
  - recommends dependency injection / interface abstractions
  - may reference SOLID Dependency Inversion Principle
  tags:
  - solid
  - coupling
  - dip
- id: missing-adr
  prompt: 'We''re choosing between PostgreSQL and MongoDB for our main data store

    in a multi-tenant SaaS platform handling structured financial data.

    What architectural considerations apply?

    '
  should_trigger: true
  checks:
  - regex:ADR|Architecture Decision|trade-off|ACID|schema|relational|document
  - no_placeholder
  - length_min:150
  expectations:
  - recommends creating an ADR to document the decision
  - 'explains trade-offs: PostgreSQL ACID/relational vs MongoDB schema-flex'
  - considers multi-tenancy and structured data requirements
  tags:
  - adr
  - database-choice
- id: well-designed-module
  prompt: 'Review this module structure:

    # auth/

    #   __init__.py

    #   service.py    — AuthService with login/register/token operations

    #   middleware.py — require_auth() FastAPI dependency

    #   models.py     — User dataclass

    '
  should_trigger: true
  checks:
  - length_min:40
  - regex:separation|clean|concern|well.struct|good|organized|minimal|single.*responsib|SRP
  - not_regex:god.*class|too.*many.*responsib|tight.*coupl|should.*split|refactor.*needed
  expectations:
  - recognizes clean separation of concerns (service/middleware/models)
  - does NOT invent architectural problems that don't exist
  - acknowledges the module is well-structured
  tags:
  - negative
- id: god-class-detection
  prompt: "Review this Java class:\nclass CustomerManager {\n  void createCustomer()\
    \ { ... }\n  void updateCustomer() { ... }\n  void deleteCustomer() { ... }\n\
    \  void sendEmail() { ... }\n  void generateReport() { ... }\n  void validateBilling()\
    \ { ... }\n  void syncWithExternalCRM() { ... }\n}\n"
  checks:
  - regex:god.*class|single.*responsib|SRP|too.*many|should.*split|one.*reason
  - length_min:80
  expectations:
  - identifies SRP violation
  - recommends splitting into separate services
  - mentions the class has multiple reasons to change
- id: interface-segregation-violation
  prompt: "This interface is used by both a Bird and a Penguin:\ninterface Animal\
    \ {\n  void fly();\n  void walk();\n  void swim();\n}\n"
  checks:
  - regex:interface.*segregation|fat.*interface|ISP|client.*specific|role.*interface
  - length_min:60
  expectations:
  - identifies fat interface violation
  - recommends splitting into Flyable, Walkable, Swimmable interfaces
  - mentions Interface Segregation Principle
- id: domain-infrastructure-leak
  prompt: "In domain/User.java:\nimport com.mysql.DriverManager;\nimport org.springframework.stereotype.Component;\n\
    public class User {\n  private Connection conn = DriverManager.getConnection(url);\n\
    \  public void save() { ... }\n}\n"
  checks:
  - regex:domain.*layer|infrastructure.*leak|dependency.*rule|pure.*domain|nothing.*external
  - length_min:80
  expectations:
  - identifies infrastructure leak into domain layer
  - recommends User should only define domain logic
  - recommends moving DB access to infrastructure layer
- id: liskov-substitution-violation
  prompt: "interface ReadOnlyRepository {\n  void save(Item item);\n}\nclass ReadOnlyFileSystem\
    \ implements ReadOnlyRepository {\n  void save(Item item) { throw new UnsupportedOperationException();\
    \ }\n}\n"
  checks:
  - regex:Liskov|substitution|contract|violat|break.*expect
  - length_min:70
  expectations:
  - identifies LSP violation where save() throws exception
  - recommends separating read and write interfaces
  - explains that subclasses should not strengthen preconditions or weaken postconditions
- id: cqrs-suggestion
  prompt: 'Our reporting system runs complex aggregation queries on 50M+ records.

    It blocks write operations and causes timeouts. Current architecture:

    one PostgreSQL database, standard CRUD repositories.

    '
  checks:
  - regex:CQRS|separate.*read.*write|command.*query|read.*replica|scalability
  - length_min:100
  expectations:
  - recommends CQRS pattern to separate read and write models
  - identifies the bottleneck from analytical queries on write database
  - suggests read replicas or separate read model
- id: bounded-context-confusion
  prompt: 'In our e-commerce system, the Customer object is used everywhere:

    Customer in OrderService, Customer in ShippingService,

    Customer in BillingService, Customer in MarketingService.

    Each service has different fields they use from Customer.

    '
  checks:
  - regex:bounded.*context|shared.*domain|context.*mapping|ubiquitous.*language|ddd
  - length_min:80
  expectations:
  - identifies bounded context confusion
  - recommends each context should have its own Customer representation
  - mentions anti-corruption layer or context mapping
- id: adr-recommended-api-choice
  prompt: 'We need to choose between REST, GraphQL, and gRPC for our microservice

    communication. 50 services, high throughput, need for streaming.

    Team is experienced with all three technologies.

    '
  checks:
  - regex:ADR|trade-off|REST.*GraphQL.*gRPC|architecture.*decision|document
  - length_min:100
  expectations:
  - recommends creating an ADR
  - 'discusses trade-offs: REST simplicity, GraphQL flexibility, gRPC performance/streaming'
  - considers the specific requirements (50 services, high throughput, streaming)
- id: aggregate-root-boundary
  prompt: 'Direct repository access bypassing aggregate:

    OrderRepository repo;

    repo.findOrderItemById(itemId).updateQuantity(5); // Called directly

    // vs going through Order aggregate root

    '
  checks:
  - regex:aggregate.*root|entity.*access|boundary|transaction|consistency
  - length_min:70
  expectations:
  - identifies violation of aggregate root pattern
  - recommends all access go through Order aggregate
  - explains aggregate enforces invariants and consistency boundaries
- id: clean-structure-review
  prompt: "Review this package structure:\nsrc/\n  domain/entities/User.java\n  domain/valueobjects/Email.java\n\
    \  application/commands/CreateUserHandler.java\n  application/queries/GetUserHandler.java\n\
    \  infrastructure/persistence/JpaUserRepository.java\n  presentation/rest/UserController.java\n"
  checks:
  - regex:clean.*arch|layer.*separat|dependency.*rule|well.*struct|concern
  - length_min:80
  expectations:
  - recognizes proper layered architecture
  - notes dependency rule is respected
  - acknowledges separation of concerns across domain/application/infrastructure/presentation
- id: open-closed-violation
  prompt: "switch(paymentType) {\n  case \"credit\": processCreditCard(); break;\n\
    \  case \"debit\": processDebitCard(); break;\n  case \"paypal\": processPayPal();\
    \ break;\n}\n// Adding crypto requires modifying this method\n"
  checks:
  - regex:open.*closed|extension|modification|strategy.*pattern|factory|polymorphism
  - length_min:60
  expectations:
  - identifies OCP violation
  - recommends Strategy pattern or polymorphism
  - suggests PaymentProcessor interface with implementations
- id: scalability-cache-design
  prompt: 'Our API receives 10,000 requests/sec for user profile data.

    Database can''t handle the load. Data rarely changes but reads are high volume.

    Current: Node.js + PostgreSQL, no caching layer.

    '
  checks:
  - regex:cache|redis|memcached|read.*replica|CDN|scalability|cache-aside
  - length_min:80
  expectations:
  - recommends caching layer (Redis/Memcached)
  - discusses cache-aside or read-through patterns
  - considers TTL and cache invalidation strategies
---

# Architecture Review

This skill enables the agent to review software architecture for clean design principles,
evaluate trade-offs, and document decisions using Architecture Decision Records.

## Use this skill when

- Reviewing overall system architecture
- Evaluating module/package structure
- Checking SOLID principle adherence
- Assessing scalability and performance architecture
- Creating or reviewing ADRs
- Evaluating design patterns usage

## Do not use this skill when

- Reviewing individual code quality (use code-review-excellence)
- Doing security-specific review (use security-audit)
- Implementing features (use development skills)

## Instructions

### Clean Architecture Assessment

Evaluate layer separation:

```
┌─────────────────────────────────────────┐
│           Presentation Layer            │  Controllers, Views, CLI
│    (depends on Application layer)       │
├─────────────────────────────────────────┤
│           Application Layer             │  Use Cases, DTOs, Services
│    (depends on Domain layer)            │
├─────────────────────────────────────────┤
│             Domain Layer                │  Entities, Value Objects, Interfaces
│    (depends on NOTHING external)        │
├─────────────────────────────────────────┤
│         Infrastructure Layer            │  DB, APIs, File System, Queue
│    (implements Domain interfaces)       │
└─────────────────────────────────────────┘
```

**Dependency Rule**: Dependencies point INWARD only. Domain never imports from Infrastructure.

```typescript
// ❌ WRONG: Domain depends on infrastructure
// domain/user.ts
import { PrismaClient } from "@prisma/client"; // Infrastructure leak!

// ✅ CORRECT: Domain defines interface, infrastructure implements
// domain/user-repository.ts
export interface UserRepository {
  findById(id: string): Promise<User | null>;
  save(user: User): Promise<void>;
}

// infrastructure/prisma-user-repository.ts
import { PrismaClient } from "@prisma/client";
import { UserRepository } from "../domain/user-repository";

export class PrismaUserRepository implements UserRepository {
  constructor(private prisma: PrismaClient) {}

  async findById(id: string): Promise<User | null> {
    return this.prisma.user.findUnique({ where: { id } });
  }

  async save(user: User): Promise<void> {
    await this.prisma.user.upsert({ where: { id: user.id }, create: user, update: user });
  }
}
```

### SOLID Principles Checklist

#### S — Single Responsibility

```typescript
// ❌ VIOLATION: Class does too many things
class UserService {
  createUser() {}
  sendWelcomeEmail() {}
  generateReport() {}
  validateCreditCard() {}
}

// ✅ CORRECT: Each class has one reason to change
class UserService {
  createUser() {}
}
class EmailService {
  sendWelcomeEmail() {}
}
class ReportService {
  generateReport() {}
}
class PaymentService {
  validateCreditCard() {}
}
```

#### O — Open/Closed

```typescript
// ✅ Open for extension, closed for modification
interface PaymentProcessor {
  process(amount: number): Promise<PaymentResult>;
}

class StripeProcessor implements PaymentProcessor {}
class PayPalProcessor implements PaymentProcessor {}
// Adding new processor doesn't modify existing code
```

#### L — Liskov Substitution

```typescript
// ❌ VIOLATION: Square breaks Rectangle contract
class Rectangle {
  setWidth(w) {}
  setHeight(h) {}
}
class Square extends Rectangle {
  setWidth(w) {
    this.width = w;
    this.height = w;
  } // Breaks expectations
}
```

#### I — Interface Segregation

```typescript
// ❌ VIOLATION: Fat interface
interface Worker {
  work(): void;
  eat(): void;
  sleep(): void;
}

// ✅ CORRECT: Segregated interfaces
interface Workable {
  work(): void;
}
interface Feedable {
  eat(): void;
}
```

#### D — Dependency Inversion

```typescript
// ❌ VIOLATION: High-level depends on low-level
class OrderService {
  private db = new MySQLDatabase(); // Direct dependency
}

// ✅ CORRECT: Both depend on abstractions
class OrderService {
  constructor(private repository: OrderRepository) {} // Interface
}
```

### Domain-Driven Design Patterns

#### Bounded Contexts

```
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Ordering   │  │   Shipping   │  │   Billing    │
│              │  │              │  │              │
│  Order       │  │  Shipment    │  │  Invoice     │
│  LineItem    │  │  Tracking    │  │  Payment     │
│  Customer*   │  │  Address     │  │  Customer*   │
└──────────────┘  └──────────────┘  └──────────────┘

* Customer may have different representations in each context
```

#### Aggregate Roots

```typescript
// Order is the aggregate root — all access goes through it
class Order {
  private items: OrderItem[] = [];

  addItem(product: Product, quantity: number): void {
    // Enforce business rules at the aggregate boundary
    if (this.status !== "draft") throw new Error("Cannot modify submitted order");
    const existing = this.items.find((i) => i.productId === product.id);
    if (existing) {
      existing.increaseQuantity(quantity);
    } else {
      this.items.push(new OrderItem(product, quantity));
    }
  }

  get total(): Money {
    return this.items.reduce((sum, item) => sum.add(item.subtotal), Money.zero());
  }
}
```

### Architecture Decision Record (ADR) Template

```markdown
# ADR-001: [Title]

## Status

[Proposed | Accepted | Deprecated | Superseded by ADR-XXX]

## Context

[What is the issue that we're seeing that is motivating this decision?]

## Decision

[What is the change that we're proposing and/or doing?]

## Consequences

### Positive

- [Benefit 1]
- [Benefit 2]

### Negative

- [Trade-off 1]
- [Trade-off 2]

### Risks

- [Risk 1 and mitigation strategy]

## Alternatives Considered

### Alternative A: [Name]

- Pros: [...]
- Cons: [...]
- Rejected because: [...]
```

### Scalability Assessment

| Dimension   | Question                        | Pattern                         |
| ----------- | ------------------------------- | ------------------------------- |
| Read scale  | Can reads be cached?            | Cache-aside, CDN, read replicas |
| Write scale | Can writes be queued?           | Message queue, event sourcing   |
| Compute     | Can processing be parallelized? | Worker pools, serverless        |
| Storage     | Does data grow unboundedly?     | Archival, partitioning, TTL     |
| Network     | Are there chatty services?      | Batch APIs, BFF pattern         |

### Code Organization Review

```
✅ GOOD structure:
src/
├── domain/          # Business logic (pure, no dependencies)
│   ├── entities/
│   ├── value-objects/
│   └── repositories/  (interfaces only)
├── application/     # Use cases, orchestration
│   ├── commands/
│   ├── queries/
│   └── services/
├── infrastructure/  # External implementations
│   ├── database/
│   ├── http/
│   └── messaging/
└── presentation/    # API controllers, CLI, UI
    ├── rest/
    ├── graphql/
    └── cli/

❌ BAD structure:
src/
├── models/          # Mixed concerns
├── utils/           # Dumping ground
├── helpers/         # More dumping ground
└── index.ts         # God file
```

## Output Format

```
## Architecture Review: [System/Module Name]

### Layer Analysis
| Layer | Status | Issues |
|-------|--------|--------|
| Domain | ✅ Clean | No external dependencies |
| Application | ⚠️ | Leaks infrastructure details |
| Infrastructure | ✅ | Properly implements interfaces |
| Presentation | ❌ | Contains business logic |

### SOLID Compliance
| Principle | Status | Notes |
|-----------|--------|-------|
| S - Single Responsibility | ✅ | Services are focused |
| O - Open/Closed | ⚠️ | Switch statements in PaymentService |
| L - Liskov Substitution | ✅ | No violations found |
| I - Interface Segregation | ❌ | UserService interface too fat |
| D - Dependency Inversion | ✅ | DI container properly used |

### Findings
1. **[Critical]** Business logic in controller layer — move to application service
2. **[Important]** No clear bounded context boundaries — services are tightly coupled
3. **[Suggestion]** Consider CQRS for the reporting module

### ADR Recommendations
- ADR-XXX: Adopt CQRS for reporting queries
- ADR-XXX: Define bounded context boundaries
```

## Anti-patterns

- **NEVER** put business logic in controllers or API handlers
- **NEVER** let domain entities depend on infrastructure
- **NEVER** create "God classes" that do everything
- **NEVER** use the `utils/` or `helpers/` folder as a dumping ground
- **NEVER** skip ADRs for significant architectural decisions
- **NEVER** couple services directly — use interfaces/events
- **NEVER** ignore scalability until it's too late — plan for it
- **NEVER** over-engineer — YAGNI applies to architecture too
