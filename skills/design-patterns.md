name: design-patterns
description: Software design patterns skill for architecture critic. Covers SOLID, DRY, KISS, YAGNI, GoF, DDD, CQRS, Event Sourcing, Clean Architecture. Evaluates tradeoffs, anti-patterns, when-to-use and when-NOT-to-use.

trigger: design patterns|architecture review|pattern selection|SOLID|DRY|GoF|DDD|CQRS|clean architecture

vars:
  language: en
  mode: critical

schema:
  input: |
    Pattern or architecture question: {input}
    Context: {context}
  output:
    verdict: APPROVED|REJECTED|RETHINK
    pattern: name
    rationale: 2-3 sentences
    tradeoffs: [plus, minus]
    when_to_use: [condition, ...]
    when_NOT_to_use: [condition, ...]

# PRINCIPLES
principles:
  SOLID:
    Single_Responsibility:
      desc: One class = one reason to change
      wrong: God object, catch-all utils
      right: Small focused classes
    Open_Closed:
      desc: Open for extension, closed for modification
      wrong: Modify existing code for new cases
      right: Strategy, decorator, composition
    Liskov_Substitution:
      desc: Subtype must be substitutable for base
      wrong: Override to do nothing, throw, or change contract
      right: Behavioral subtype
    Interface_Segregation:
      desc: Many specific interfaces > one general
      wrong: Fat interface, implement unused methods
      right: Role interfaces, mixins
    Dependency_Inversion:
      desc: Depend on abstractions, not concretes
      wrong: New MyConcreteClass(), direct instantiation
      right: DI, factories, interfaces

  DRY: Dont_Repeat_Yourself — one piece of knowledge, one location. Avoid copy-paste logic.代价: over-abstraction, premature consolidation.

  KISS: Keep_It_Simple_Stupid — simplest solution wins. Avoid clever hacks, unnecessary indirection.

  YAGNI: You_Aint_Gonna_Need_It — implement when needed, not anticipated. Avoid gold-plating, speculative generality.

# GOF PATTERNS
patterns:
  Factory:
    variants: [Abstract_Factory, Factory_Method, Simple_Factory]
    use_when:
      - Object creation logic is complex or varies
      - Type determined at runtime (config, plugin)
      - Avoid tight coupling to concrete classes
      - Test requires mocking dependencies
    NOT_when:
      - Simple one-liner constructor sufficient
      - Adds unnecessary indirection for trivial objects
      - Creates gods/framework dependency
    examples:
      good: DBConnectionFactory, PluginFactory, HandlerFactory
      bad: ObjectFactory god class, factories for primitives
    tradeoffs:
      -: Indirection, more classes, complexity
      +: Loose coupling, testability, runtime flexibility

  Strategy:
    variants: [Strategy, Policy]
    use_when:
      - Multiple algorithms for one behavior
      - Swap behavior at runtime
      - Avoid conditionals (if/else chain)
      - Open for extension, closed for modification
    NOT_when:
      - Only one algorithm, no variation
      - Strategy is trivial (one line)
      - Creates many tiny classes with no variation
    examples:
      good: SortStrategy, PaymentStrategy, ValidationStrategy
      bad: StrategyPerBitOfLogic, trivial one-liner strategies
    tradeoffs:
      -: More classes, indirection, harder stack traces
      +: Eliminated conditionals, runtime flexibility, SOLID compliance

  Observer:
    variants: [Observer, Pub_Sub, Event_Listener, Listener]
    use_when:
      - One-to-many dependency, notify on state change
      - Loose coupling between publisher and subscribers
      - Decouple event emission from handling
      - Multiple independent handlers for same event
    NOT_when:
      - Tight coupling acceptable
      - Synchronization issues unmanageable
      - Memory leaks from listeners not cleaned up
      - Order of execution critical and undefined
    examples:
      good: UI event handlers, notification systems, AuditLog
      bad: Chatty objects, deeply nested observer chains
    tradeoffs:
      -: Memory leaks, unpredictable order, debugging difficulty
      +: Loose coupling, natural event modeling, extensibility

  Decorator:
    variants: [Decorator, Wrapper, Chain_of_Responsibility]
    use_when:
      - Add behavior to objects dynamically
      - Compose behaviors at runtime
      - Avoid subclass explosion (N behaviors × M types)
      - Open for extension, closed for modification
      - Multiple orthogonal concerns
    NOT_when:
      - Static behavior addition
      - Inheritance simpler (no subclass explosion)
      - Decorator changes identity/contract unexpectedly
      - Deep nesting hard to debug
    examples:
      good: IO streams, Web middleware, LoggingDecorator, CachingDecorator
      bad: DecoratorPerTinyFeature, decorators that change return type
    tradeoffs:
      -: Hard to debug, many small files, runtime complexity
      +: Flexible composition, avoids inheritance explosion, SOLID

# DDD CONCEPTS
ddd:
  Aggregate:
    desc: Cluster of related objects treated as one unit. One AggregateRoot controls consistency.
    use_when:
      - Complex object graphs with invariants
      - Transaction boundary needed
      - Prevent direct manipulation of internal entities
    NOT_when:
      - Flat objects, no invariants
      - Aggregate becomes god object
      - Distributed transactions required
    rules:
      - AggregateRoot is the only entry point
      - References by ID between aggregates
      - Changes within aggregate atomic
    examples:
      good: Order->OrderLine, Account->Transaction
      bad: GodAggregate containing entire system

  Repository:
    desc: Abstraction over persistence. Collection-like interface for accessing aggregates.
    use_when:
      - Need to decouple domain from persistence
      - Test domain logic without DB
      - Swap persistence technology
    NOT_when:
      - CRUD on simple DTOs only
      - Repository becomes god DAO
      - Domain logic leaks into repository
    patterns:
      - Collection-oriented: add(), remove(), find()
      - Persistence-oriented: save(), delete(), find()
    examples:
      good: IOrderRepository, IUserRepository
      bad: GeneralRepository<T>, Repository with ORM methods

  Domain_Event:
    desc: Immutable record of something significant that happened in domain.
    use_when:
      - Capture side effects for auditing
      - Decouple components via event bus
      - Maintain consistency via eventual processing
      - Trigger workflows
    NOT_when:
      - Synchronous tight coupling fine
      - Event payload changes frequently
      - No consumers need the event
    patterns:
      - Immutable event record
      - EventBus for dispatching
      - EventHandler per concern
    examples:
      good: OrderPlaced, PaymentReceived, UserRegistered
      bad: GenericDomainEvent<T>, event with behavior

# ARCHITECTURAL PATTERNS
architectures:
  CQRS:
    desc: Command Query Responsibility Segregation. Separate read and write models.
    use_when:
      - Read/write workloads differ significantly
      - Complex read queries (joins, aggregates)
      - Scalability requires independent optimization
      - Different data representations for UI vs storage
    NOT_when:
      - Simple CRUD, similar read/write
      - Team unfamiliar with event-driven
      - Overhead unjustified for small scale
      - Eventual consistency issues unacceptable
    components:
      Commands: Intent to change state, return void or result
      Queries: Intent to read, no side effects
      ReadModels: Denormalized, optimized for queries
      WriteModel: Normalized, enforces business rules
    tradeoffs:
      -: Complexity, eventual consistency, more infrastructure
      +: Independent scaling, optimized queries, clear separation

  Event_Sourcing:
    desc: Store state changes as sequence of events. Replay to reconstruct state.
    use_when:
      - Full audit trail required
      - Complex state reconstruction needed
      - Temporal queries (state at any point)
      - Debugging by replaying
      - CQRS with audit
    NOT_when:
      - Simple CRUD sufficient
      - Storage cost unacceptable (events grow)
      - Event schema changes problematic
      - Projections slow for many events
    mechanics:
      - Events are immutable facts
      - Aggregate replays events to reconstruct
      - Snapshots for optimization
      - Projections for read models
    tradeoffs:
      -: Complexity, event schema evolution, storage, eventual consistency
      +: Complete audit, time travel debugging, natural CQRS companion

  Clean_Architecture:
    layers:
      Domain:
        - Entities, Value Objects
        - Domain Services
        - Domain Events
        - No external dependencies
        - Pure business logic
      Application:
        - Use Cases, Commands, Queries
        - Application Services
        - Orchestration
        - Depends on Domain only
      Infrastructure:
        - Repositories implementations
        - External services adapters
        - Frameworks (DB, HTTP, MQ)
        - Depends on Application
      Presentation:
        - Controllers, Gateways
        - DTOs, Mappers
        - Depends on Application
    rules:
      - Dependencies point inward only
      - Inner layers know nothing of outer
      - External frameworks at outer boundary
      - Business rules in Domain
    use_when:
      - Long-lived projects
      - Complex domain logic
      - Testability critical
      - Team size > 3
    NOT_when:
      - Trivial CRUD app
      - Prototype/MVP with unknown lifespan
      - Team < 2
      - Overkill for simple requirements

# ANTI-PATTERNS
anti_patterns:
  God_Object: Class controlling everything
  Golden_Pattern: Pattern used without justification
  Patternitis: Patterns where simpler code suffices
  Singleton_Absession: Global state via singleton
  ServiceLocator_Antipattern: Runtime DI over constructor injection
  Deep_Inheritance_Taxonomy: 7-level class hierarchy
  Anemic_Domain_Model: Entities with no behavior, all logic in services
  Transaction_Script: All logic in procedural scripts

# EVALUATION CRITERIA
eval_criteria:
  - Pattern justified by concrete problem, not theoretical elegance
  - Tradeoffs consciously evaluated, not ignored
  - Complexity added proportional to benefit
  - Pattern composition coherent, not pattern salad
  - Anti-patterns recognized and avoided
  - Context (team size, project age, scale) considered

# EVAL CASES
eval_cases:
  - id: 1
    scenario: "E-commerce checkout. Need to charge different payment methods (Credit, Debit, PayPal, Crypto). Add new methods quarterly."
    expected: Strategy or Abstract Factory
    verdict: APPROVED

  - id: 2
    scenario: "Small CRUD API. One developer. 5 entities. Simple create/read/update/delete."
    expected: Basic service/repository. No GoF needed.
    verdict: REJECTED

  - id: 3
    scenario: "Order aggregate contains Customer entity. Other aggregates need Customer data."
    expected: Reference by ID, not object reference
    verdict: APPROVED

  - id: 4
    scenario: "Team debates adding Decorator pattern to add logging to 3 service methods. Each log line is 2 words."
    expected: Simple AOP or wrapper if needed. Most likely KISS violation.
    verdict: REJECTED

  - id: 5
    scenario: "Event-driven fintech. All transactions must be auditable. Regulatory requirement."
    expected: Event Sourcing
    verdict: APPROVED

  - id: 6
    scenario: "Startup MVP. Unknown product-market fit. Team of 2. 6-month runway."
    expected: Simple architecture. YAGNI, KISS.
    verdict: REJECTED

  - id: 7
    scenario: "Inventory system. Need to enforce invariants: stock >= 0, reserved <= available."
    expected: DDD Aggregate with invariant enforcement
    verdict: APPROVED

  - id: 8
    scenario: "Read-heavy dashboard. 80% reads, complex aggregations, denormalized views."
    expected: CQRS with separate read models
    verdict: APPROVED

  - id: 9
    scenario: "Junior dev wants to use Observer for every service communication 'for flexibility'."
    expected: Direct call if coupling acceptable. Observer adds complexity.
    verdict: REJECTED

  - id: 10
    scenario: "Microservices. Services communicate via events. Need audit trail across services."
    expected: Event Sourcing + Domain Events + CQRS
    verdict: APPROVED

  - id: 11
    scenario: "API gateway routes requests. Simple proxy. No business logic."
    expected: No pattern. Simple conditional routing.
    verdict: REJECTED

  - id: 12
    scenario: "Legacy monolith to microservices. Domain has 200 entities. Need clear boundaries."
    expected: DDD Bounded Contexts, Clean Architecture
    verdict: APPROVED

  - id: 13
    scenario: "User registration. Send welcome email, create profile, allocate default resources."
    expected: Domain Event + Handlers (Observer/Pub-Sub)
    verdict: APPROVED

  - id: 14
    scenario: "Dev adds Repository interface for every table, even join tables with no behavior."
    expected: Repository only for aggregates, not every table.
    verdict: REJECTED

  - id: 15
    scenario: "Complex rules engine. Premium calculation varies by product, region, season, customer tier."
    expected: Strategy pattern for algorithms. Possibly Rule Engine.
    verdict: APPROVED

  - id: 16
    scenario: "Chatty HTTP. Service A calls B, B calls C, C calls D for one user request."
    expected: Facade, or rethink granularity. YAGNI/chatty service smell.
    verdict: REJECTED

  - id: 17
    scenario: "Payment processing. Must integrate with 8 providers. Fraud check must be swappable."
    expected: Strategy or Abstract Factory for providers
    verdict: APPROVED

  - id: 18
    scenario: "Small internal tool. 3 tables. One developer. Used by 5 people."
    expected: Basic MVC or simple service. Over-engineering antipattern.
    verdict: REJECTED

  - id: 19
    scenario: "Enterprise system. Regulatory audit requires showing state at any past date."
    expected: Event Sourcing
    verdict: APPROVED

  - id: 20
    scenario: "Developer wraps every class in Decorator 'to follow Open-Closed'."
    expected: Decorator only when composition needed. Patternitis.
    verdict: REJECTED

  - id: 21
    scenario: "Bounded context with 3 aggregates. Cross-aggregate consistency required."
    expected: Domain Event + SAGA/Process Manager for eventual consistency
    verdict: APPROVED

  - id: 22
    scenario: "IoT system. 10k devices reporting. Need to process and display in real-time."
    expected: CQRS + Event Streaming (Kafka) + Projections
    verdict: APPROVED

  - id: 23
    scenario: "Config-driven CRUD generator. Generate services/repos from YAML."
    expected: Factory pattern if complex, else simple generation.
    verdict: RETHINK

  - id: 24
    scenario: "Monolithic shopping cart. Adding marketplace for third-party sellers."
    expected: Add bounded context for marketplace. Keep cart bounded context clean.
    verdict: APPROVED

  - id: 25
    scenario: "Dev creates IInterface for every class 'for testability'. 1:1 mapping."
    expected: Interface segregation only when multiple implementations exist or needed.
    verdict: REJECTED

# OUTPUT FORMAT
output_format: |
  ## Analysis
  
  **Input:** {input}
  
  **Verdict:** {verdict}
  
  **Recommended Pattern:** {pattern}
  
  **Rationale:** {rationale}
  
  **Tradeoffs:**
  - PRO: {plus}
  - CON: {minus}
  
  **Use When:** {when_to_use}
  
  **Avoid When:** {when_NOT_to_use}

# SKILL COMMANDS
commands:
  analyze: Evaluate architecture decision
    args: [scenario, context]
    returns: [verdict, pattern, rationale]

  anti_pattern_detect: Scan for known anti-patterns
    args: [code_snippet]
    returns: [smells, suggestions]

  pattern_selector: Guide pattern selection
    args: [problem_description]
    returns: [recommended_patterns, alternatives]

  principle_check: Validate against design principles
    args: [code_architecture]
    returns: [violations, compliant_items]
