---
name: python-fastapi-refactoring
description: Refactoring and optimization skill for Python FastAPI async applications. Covers async/await patterns, connection pooling, N+1 queries, Pydantic v2 performance, memory optimization, dead code detection, import cleanup, type annotations, error handling, dependency injection, and background task management.
framework:
  - FastAPI
  - Python 3.10+
  - asyncpg
  - SQLAlchemy
  - Pydantic v2
keywords:
  - async
  - await
  - refactoring
  - optimization
  - performance
  - connection-pooling
  - n-plus-1
  - pydantic
  - type-annotations
  - dependency-injection
  - background-tasks
  - dead-code
  - ruff
  - isort
eval_cases:
  - id: 1
    description: Identify blocking I/O in async context
    prompts:
      - |
        # Async/await Anti-patterns

        Given this FastAPI endpoint, identify all blocking calls that would block the event loop and explain how to fix each:

        ```python
        from fastapi import FastAPI
        import asyncio

        app = FastAPI()

        @app.get("/users/{user_id}")
        async def get_user(user_id: int):
            # Blocking: synchronous SQLite
            conn = sqlite3.connect("app.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            result = cursor.fetchone()
            conn.close()
            return {"id": result[0], "name": result[1]}

        @app.get("/reports")
        async def generate_report():
            # Blocking: CPU-bound work
            with open("large_file.csv", "r") as f:
                content = f.read()
            data = [process_row(row) for row in content.split("\n")]
            return {"count": len(data)}
        ```
      - |
        # Connection Pool Misuse

        Analyze this code for connection pool issues and suggest fixes:

        ```python
        @app.get("/items/{item_id}")
        async def get_item(item_id: int):
            pool = await asyncpg.create_pool(DATABASE_URL)
            async with pool.acquire() as conn:
                result = await conn.fetchrow("SELECT * FROM items WHERE id = $1", item_id)
            await pool.close()
            return dict(result)

        @app.get("/batch-items")
        async def get_batch_items(item_ids: list[int]):
            results = []
            for item_id in item_ids:
                conn = await asyncpg.connect(DATABASE_URL)
                result = await conn.fetchrow("SELECT * FROM items WHERE id = $1", item_id)
                await conn.close()
                results.append(result)
            return results
        ```
  - id: 2
    description: N+1 query detection and resolution
    prompts:
      - |
        # N+1 Query Problem

        This endpoint generates N+1 queries. Identify and fix using SQLAlchemy eager loading:

        ```python
        @app.get("/orders/{order_id}")
        async def get_order(order_id: int):
            order = await db.get(Order, order_id)
            items = []
            for item in order.items:
                product = await db.get(Product, item.product_id)
                items.append({"product": product.name, "quantity": item.quantity})
            return {"order": order.id, "items": items}

        @app.get("/users/{user_id}/orders")
        async def get_user_orders(user_id: int):
            user = await db.get(User, user_id)
            orders = []
            for order in user.orders:
                order_items = await db.execute(
                    text("SELECT * FROM order_items WHERE order_id = :id"),
                    {"id": order.id}
                )
                orders.append({"order": order.id, "items": order_items.fetchall()})
            return orders
        ```
      - |
        # Raw SQL Batching

        Convert this N+1 pattern to a batched query:

        ```python
        @app.get("/products/{product_id}/reviews")
        async def get_product_reviews(product_id: int):
            product = await db.fetchone("SELECT * FROM products WHERE id = $1", product_id)
            reviews = await db.fetch("SELECT * FROM reviews WHERE product_id = $1", product_id)
            reviewer_ids = [r["reviewer_id"] for r in reviews]
            # N+1 here:
            reviewers = []
            for rid in reviewer_ids:
                reviewer = await db.fetchone("SELECT * FROM users WHERE id = $1", rid)
                reviewers.append(reviewer)
            return {"product": product, "reviews": reviews, "reviewers": reviewers}
        ```
  - id: 3
    description: Pydantic v2 performance and memory optimization
    prompts:
      - |
        # Pydantic Performance Issues

        Identify expensive operations in these Pydantic models and optimize for hot paths:

        ```python
        from pydantic import BaseModel, field_validator, model_validator
        import re

        class UserProfile(BaseModel):
            email: str
            phone: str
            created_at: datetime

            @field_validator("email")
            @classmethod
            def validate_email(cls, v):
                if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", v):
                    raise ValueError("Invalid email")
                return v.lower()

            @field_validator("phone")
            @classmethod
            def validate_phone(cls, v):
                # Expensive: regex compilation on every call
                if not re.match(r"^\+?1?\d{9,15}$", v):
                    raise ValueError("Invalid phone")
                return v

            @model_validator(mode="after")
            def validate_relationship(self):
                # Expensive: external API call in validator
                if self.email and self.created_at:
                    exists = check_email_existence(self.email)  # sync HTTP call!
                    if not exists:
                        raise ValueError("Email does not exist")
                return self
        ```

        Also suggest `__slots__` usage where appropriate for memory optimization.
      - |
        # Generators vs Lists

        Convert these list comprehensions to generators for memory efficiency:

        ```python
        @app.get("/analytics")
        async def get_analytics():
            all_events = await db.fetch("SELECT * FROM events")
            processed = [transform_event(e) for e in all_events]
            filtered = [e for e in processed if e["value"] > 100]
            aggregated = sum(e["value"] for e in filtered)
            return {"total": aggregated}

        @app.get("/large-dataset")
        async def get_large_dataset():
            items = await db.fetch("SELECT * FROM large_table")
            return {"items": [dict(item) for item in items]}
        ```
  - id: 4
    description: Error handling, dependency injection, and background tasks
    prompts:
      - |
        # Error Handling Issues

        Refactor this code to use proper error handling patterns:

        ```python
        @app.get("/resource/{resource_id}")
        async def get_resource(resource_id: int):
            try:
                result = await db.fetchone("SELECT * FROM resources WHERE id = $1", resource_id)
                if result is None:
                    return {"error": "not found"}
                return dict(result)
            except:
                return {"error": "something went wrong"}

        @app.post("/process")
        async def process_data(data: dict):
            result = risky_operation(data)
            return {"status": "ok", "result": result}
        ```
      - |
        # Dependency Injection Problems

        Identify issues with this dependency injection setup and fix caching problems:

        ```python
        from fastapi import Depends

        async def get_db_connection():
            conn = await asyncpg.connect(DATABASE_URL)
            return conn

        async def get_redis_client():
            client = aioredis.from_url(REDIS_URL)
            return client

        @app.get("/items")
        async def list_items(
            db=Depends(get_db_connection),
            cache=Depends(get_redis_client)
        ):
            # Connection created for EACH request
            cached = await cache.get("items")
            if cached:
                return json.loads(cached)
            items = await db.fetch("SELECT * FROM items")
            await cache.set("items", json.dumps([dict(i) for i in items]), ex=60)
            await db.close()  # Manual cleanup needed
            return items

        @app.get("/config")
        async def get_config(cache=Depends(get_redis_client)):
            # Same redis client re-created per request
            config = await cache.get("config")
            return json.loads(config) if config else {}
        ```
      - |
        # Background Task Anti-patterns

        Fix this background task implementation:

        ```python
        @app.post("/send-notification")
        async def send_notification(user_id: int, message: str):
            asyncio.create_task(notify_user(user_id, message))
            return {"status": "queued"}

        async def notify_user(user_id: int, message: str):
            # No error handling, no await
            await send_email(user_id, message)
            # Fire and forget, exceptions lost

        @app.post("/process-data")
        async def process_data(data: list):
            tasks = []
            for item in data:
                task = asyncio.create_task(process_item(item))
                tasks.append(task)
            # Not awaited, endpoint returns before completion
            return {"status": "processing"}
        ```
---

# Python FastAPI Refactoring & Optimization Skill

## Overview

This skill focuses on refactoring and optimizing FastAPI applications with async Python. It addresses common anti-patterns in async contexts, database interaction, memory usage, and code quality.

## Core Principles

1. **Never block the event loop** - All I/O must be async
2. **Reuse connections** - Pool management is critical for performance
3. **Batch queries** - Eliminate N+1 patterns at the source
4. **Optimize hot paths** - Pydantic validation must be cheap
5. **Explicit over implicit** - Clear error handling, no bare excepts

---

## 1. Async/Await: Identify Blocking Calls

### Problem

Syncstdlib functions, blocking I/O libraries, and CPU-bound operations block the event loop in async context.

### Common Blockers

| Blocker | Solution |
|---------|----------|
| `sqlite3`, `psycopg2` | Use `asyncpg`, `aiopg`, `sqlalchemy.ext.asyncio` |
| `requests` | Use `httpx.AsyncClient` or `aiohttp` |
| `open()` for files | Use `aiofiles` |
| `time.sleep()` | Use `asyncio.sleep()` |
| CPU-bound work | Offload to `run_in_executor()` or worker process |

### Detection Pattern

```python
# ANTI-PATTERN: Blocking database call
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    conn = sqlite3.connect("app.db")  # BLOCKS
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return {"id": result[0], "name": result[1]}

# FIXED: Use asyncpg with connection pool
from asyncpg import Pool

pool: Pool = None

@app.on_event("startup")
async def startup():
    global pool
    pool = await asyncpg.create_pool(DATABASE_URL, min_size=5, max_size=20)

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    async with pool.acquire() as conn:
        result = await conn.fetchrow(
            "SELECT id, name FROM users WHERE id = $1", user_id
        )
    return dict(result)
```

### CPU-Bound Work

```python
import asyncio
from concurrent.futures import ProcessPoolExecutor

executor = ProcessPoolExecutor(max_workers=4)

@app.get("/report")
async def generate_report():
    loop = asyncio.get_event_loop()
    # Run CPU-bound work in thread pool to avoid blocking
    result = await loop.run_in_executor(executor, process_large_file, "data.csv")
    return {"status": "complete", "result": result}
```

---

## 2. Connection Pooling

### asyncpg Pool Best Practices

```python
from asyncpg import Pool, create_pool
from contextlib import asynccontextmanager

# Create pool at startup, destroy at shutdown
pool: Pool = None

@app.on_event("startup")
async def startup():
    global pool
    pool = await create_pool(
        DATABASE_URL,
        min_size=10,
        max_size=100,
        command_timeout=60,
        max_queries=50000,
        max_inactive_connection_lifetime=300,
    )

@app.on_event("shutdown")
async def shutdown():
    await pool.close()

# Use dependency injection for request-scoped connections
async def get_db() -> Pool:
    return pool
```

### httpx.AsyncClient Reuse

```python
from httpx import AsyncClient, ASGITransport
from contextlib import asynccontextmanager

# Module-level client
http_client: AsyncClient = None

@app.on_event("startup")
async def startup():
    global http_client
    http_client = AsyncClient(
        timeout=30.0,
        limits=Limits(max_connections=100, max_keepalive_connections=20),
    )

@app.on_event("shutdown")
async def shutdown():
    await http_client.aclose()

# For dependency injection pattern
@asynccontextmanager
async def get_http_client():
    async with AsyncClient() as client:
        yield client

@app.get("/external-data")
async def fetch_data():
    response = await http_client.get("https://api.example.com/data")
    return response.json()
```

### Anti-pattern: Creating Connections Per Request

```python
# ANTI-PATTERN
@app.get("/items/{item_id}")
async def get_item(item_id: int):
    conn = await asyncpg.connect(DATABASE_URL)  # New connection each time
    result = await conn.fetchrow("SELECT * FROM items WHERE id = $1", item_id)
    await conn.close()
    return dict(result)

# FIXED: Use pool
@app.get("/items/{item_id}")
async def get_item(item_id: int, pool: Pool = Depends(get_db)):
    async with pool.acquire() as conn:
        result = await conn.fetchrow("SELECT * FROM items WHERE id = $1", item_id)
    return dict(result)
```

---

## 3. N+1 Queries

### SQLAlchemy: Eager Loading

```python
from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload, Relationship

# ANTI-PATTERN: Lazy loading causes N+1
@app.get("/orders/{order_id}")
async def get_order(order_id: int, session: AsyncSession = Depends(get_session)):
    order = await session.get(Order, order_id)
    # Each access to order.items triggers a query
    items = [{"product": item.product.name, "qty": item.quantity} for item in order.items]
    return {"order_id": order.id, "items": items}

# FIXED: Use selectinload for to-many relationships
@app.get("/orders/{order_id}")
async def get_order(order_id: int, session: AsyncSession = Depends(get_session)):
    stmt = (
        select(Order)
        .where(Order.id == order_id)
        .options(
            selectinload(Order.items).joinedload(OrderItem.product)
        )
    )
    result = await session.execute(stmt)
    order = result.scalar_one()
    items = [{"product": item.product.name, "qty": item.quantity} for item in order.items]
    return {"order_id": order.id, "items": items}
```

### Raw SQL: Batch Fetch

```python
# ANTI-PATTERN: N+1 for reviewers
reviews = await db.fetch("SELECT * FROM reviews WHERE product_id = $1", product_id)
reviewers = []
for review in reviews:
    reviewer = await db.fetchrow("SELECT * FROM users WHERE id = $1", review["reviewer_id"])
    reviewers.append(reviewer)

# FIXED: Batch query with UNNEST
@app.get("/products/{product_id}/reviews")
async def get_product_reviews(product_id: int):
    reviews = await db.fetch("SELECT * FROM reviews WHERE product_id = $1", product_id)
    reviewer_ids = [r["reviewer_id"] for r in reviews]
    
    if not reviewer_ids:
        return {"reviews": reviews, "reviewers": []}
    
    # Single query for all reviewers
    placeholders = ",".join(f"${i+2}" for i in range(len(reviewer_ids)))
    reviewers = await db.fetch(
        f"SELECT * FROM users WHERE id IN ({placeholders})",
        *reviewer_ids
    )
    reviewer_map = {r["id"]: r for r in reviewers}
    return {
        "reviews": reviews,
        "reviewers": [reviewer_map[rid] for rid in reviewer_ids]
    }
```

### SQLAlchemy Batch with async_scoped_session

```python
from sqlalchemy.ext.asyncio import async_scoped_session

async def batch_get_products(product_ids: list[int]) -> dict[int, Product]:
    stmt = select(Product).where(Product.id.in_(product_ids))
    result = await session.execute(stmt)
    products = result.scalars().all()
    return {p.id: p for p in products}
```

---

## 4. Pydantic v2 Performance

### Avoid Expensive Validators in Hot Paths

```python
from pydantic import BaseModel, field_validator, model_validator, ConfigDict
import re

# COMPILE REGEX ONCE, NOT PER VALIDATION
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
PHONE_REGEX = re.compile(r"^\+?1?\d{9,15}$")

class UserBase(BaseModel):
    email: str
    phone: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not EMAIL_REGEX.match(v):
            raise ValueError("Invalid email format")
        return v.lower()

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not PHONE_REGEX.match(v):
            raise ValueError("Invalid phone format")
        return v

# For high-throughput endpoints, use model_config to skip validation
class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, validate_assignment=False)
    
    id: int
    email: str
    phone: str
```

### model_validator: Avoid External Calls

```python
# ANTI-PATTERN: External API call in validator
@model_validator(mode="after")
def validate_email_exists(self):
    exists = check_email_existence(self.email)  # BLOCKING!
    if not exists:
        raise ValueError("Email does not exist")
    return self

# FIXED: Move validation to endpoint, use async
@app.post("/users")
async def create_user(user: UserCreate):
    # Validate existence asynchronously in endpoint
    if not await check_email_async(user.email):
        raise HTTPException(status_code=400, detail="Email does not exist")
    return await user_service.create(user)
```

### `__slots__` for Dataclasses

```python
from dataclasses import dataclass
from typing import ClassVar

@dataclass(slots=True)
class Point:
    x: float
    y: float
    
    # Class variables still work with slots
    scale: ClassVar[float] = 1.0

# Memory savings: ~40% less per instance
# Access speed: slightly faster due to fixed layout
```

---

## 5. Memory Optimization

### Generators Over Lists

```python
# ANTI-PATTERN: Loads all into memory
@app.get("/events")
async def get_events():
    events = await db.fetch("SELECT * FROM events")
    processed = [transform_event(e) for e in events]
    filtered = [e for e in processed if e["value"] > 100]
    return {"total": sum(e["value"] for e in filtered)}

# FIXED: Use async generators
from fastapi.responses import StreamingResponse

@app.get("/events")
async def get_events():
    async def event_generator():
        async with pool.acquire() as conn:
            async with conn.transaction():
                async for row in conn.cursor("SELECT * FROM events"):
                    event = transform_event(dict(row))
                    if event["value"] > 100:
                        yield event
    
    return StreamingResponse(event_generator(), media_type="application/json")

# Or for aggregation without streaming:
@app.get("/analytics")
async def get_analytics():
    total = 0
    count = 0
    async with pool.acquire() as conn:
        async with conn.transaction():
            async for row in conn.cursor("SELECT value FROM events"):
                total += row["value"]
                count += 1
    return {"total": total, "count": count}
```

### WeakRef for Caches

```python
import weakref
from typing import Any

class WeakCache:
    def __init__(self):
        self._cache = weakref.WeakValueDictionary()
    
    def get(self, key: str) -> Any | None:
        return self._cache.get(key)
    
    def set(self, key: str, value: Any) -> None:
        self._cache[key] = value

# For immutable cached data, use WeakKeyDictionary with keys
import weakref

_cache: weakref.WeakKeyDictionary = weakref.WeakKeyDictionary()

def get_cached_result(obj: SomeClass) -> Any:
    if obj in _cache:
        return _cache[obj]
    result = expensive_computation(obj)
    _cache[obj] = result
    return result
```

---

## 6. Dead Code Detection

### Tools

```bash
# Vulture: find unused code
pip install vulture
vulture . --min-confidence 80

# Ruff: F811 (redefined loop), F401 (unused imports)
ruff check . --select F811,F401 --ignore F811,F401

# Combined workflow
ruff check . --select F401,F811,F841,F842 --fix
vulture . --min-confidence 90
```

### Common Patterns

```python
# F401: Unused imports
import os  # noqa: F401  # Used in type hints only

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from my_module import SomeClass  # Only for type checking

# F811: Redefined names
import math
result = math.sin(0)  # shadowed by below

def sin(x):  # Name matches imported function
    return x  # This shadows math.sin

# F841: Unused variables
def process(data):
    result = transform(data)  # result unused
    return transform(data)  # Should use result instead
```

---

## 7. Import Cleanup

### isort + ruff Configuration

```toml
# pyproject.toml
[tool.ruff]
line-length = 100
target-version = "py310"

[tool.ruff.lint]
select = ["I", "E", "F", "W"]
ignore = ["E501"]

[tool.isort]
profile = "ruff"
line_length = 100
```

### Commands

```bash
# Format and fix imports
isort .
ruff check . --fix

# Pre-commit hook example
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: ruff-format
        name: ruff format
        entry: ruff format
        language: system
        types: [python]
      - id: ruff
        name: ruff
        entry: ruff check --fix
        language: system
        types: [python]
      - id: isort
        name: isort
        entry: isort .
        language: system
        types: [python]
```

---

## 8. Type Annotations

### Complete Typing for Public APIs

```python
from typing import TypedDict, AsyncIterator, Literal
from collections.abc import AsyncGenerator

# BAD: Any in public API
def process_data(data: Any) -> Any:  # noqa: RUF006
    return data

# GOOD: Complete type annotations
class UserDict(TypedDict):
    id: int
    name: str
    email: str

def process_data(data: list[UserDict]) -> dict[str, int]:
    return {"count": len(data)}

# Async generators
async def fetch_events() -> AsyncIterator[Event]:
    async with pool.acquire() as conn:
        async with conn.transaction():
            async for row in conn.cursor("SELECT * FROM events"):
                yield Event.from_row(row)

# Use Literal for string unions
def parse_status(status: Literal["active", "pending", "deleted"]) -> Status:
    ...
```

### Type Checking with mypy

```bash
# pyproject.toml
[tool.mypy]
python_version = "3.10"
strict = true
warn_return_any = true
warn_unused_ignores = true

# Run
mypy . --strict
```

---

## 9. Error Handling

### Explicit Exceptions, No Bare Except

```python
from fastapi import HTTPException
from fastapi.responses import JSONResponse

# BAD: Bare except catches everything
@app.get("/resource/{resource_id}")
async def get_resource(resource_id: int):
    try:
        result = await db.fetchrow("SELECT * FROM resources WHERE id = $1", resource_id)
        return dict(result)
    except:  # noqa: E722
        return {"error": "something went wrong"}

# GOOD: Specific exception handling
@app.get("/resource/{resource_id}")
async def get_resource(resource_id: int):
    try:
        result = await db.fetchrow("SELECT * FROM resources WHERE id = $1", resource_id)
    except ConnectionError as e:
        logger.error(f"Database connection failed: {e}")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")
    except Exception as e:
        logger.exception(f"Unexpected error fetching resource {resource_id}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
    if result is None:
        raise HTTPException(status_code=404, detail=f"Resource {resource_id} not found")
    
    return dict(result)
```

### Custom Exception Classes

```python
from fastapi import HTTPException

class ResourceNotFoundError(HTTPException):
    def __init__(self, resource_id: int):
        super().__init__(
            status_code=404,
            detail=f"Resource {resource_id} not found"
        )

class DatabaseConnectionError(HTTPException):
    def __init__(self, cause: str):
        super().__init__(
            status_code=503,
            detail="Database temporarily unavailable"
        )
        self.cause = cause

@app.get("/resource/{resource_id}")
async def get_resource(resource_id: int):
    try:
        result = await db.fetchrow("SELECT * FROM resources WHERE id = $1", resource_id)
    except ConnectionError as e:
        raise DatabaseConnectionError(str(e))
    
    if not result:
        raise ResourceNotFoundError(resource_id)
    
    return dict(result)
```

---

## 10. Dependency Injection

### Depends() Caching

```python
from functools import lru_cache
from fastapi import Depends

# Per-request dependency (new instance each request)
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

@app.get("/items")
async def list_items(session: AsyncSession = Depends(get_db_session)):
    ...

# App-scoped dependency (shared across requests) - use lru_cache
@lru_cache
def get_settings() -> Settings:
    return Settings()

@app.get("/config")
async def get_config(settings: Settings = Depends(get_settings)):
    return settings

# Request-scoped with explicit lifespan
from contextlib import asynccontextmanager
from fastapi import FastAPI

_request_redis: dict = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    _request_redis["client"] = await aioredis.from_url(REDIS_URL)
    yield
    await _request_redis["client"].close()

app = FastAPI(lifespan=lifespan)

@app.get("/data")
async def get_data():
    client = _request_redis["client"]  # Same instance per request
    ...
```

### Anti-pattern: Creating Connections in Dependency

```python
# BAD: Connection created but never properly released
async def get_db():
    conn = await asyncpg.connect(DATABASE_URL)
    return conn

# GOOD: Proper cleanup with context manager
async def get_db(pool: Pool = Depends(get_pool)):
    async with pool.acquire() as conn:
        yield conn
```

---

## 11. Background Tasks

### asyncio.create_task with Proper Error Handling

```python
import asyncio
import logging
from fastapi import BackgroundTasks

logger = logging.getLogger(__name__)

# ANTI-PATTERN: Fire and forget, exceptions lost
@app.post("/send-notification")
async def send_notification(user_id: int, message: str):
    asyncio.create_task(notify_user(user_id, message))  # No error handling!
    return {"status": "queued"}

# GOOD: Background task with error handling
async def notify_user_with_logging(user_id: int, message: str):
    try:
        await send_email(user_id, message)
        logger.info(f"Notification sent to user {user_id}")
    except Exception as e:
        logger.error(f"Failed to send notification to user {user_id}: {e}")
        await save_failed_notification(user_id, message, str(e))

@app.post("/send-notification")
async def send_notification(
    user_id: int,
    message: str,
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(notify_user_with_logging, user_id, message)
    return {"status": "queued"}
```

### Multiple Background Tasks

```python
from fastapi import BackgroundTasks

@app.post("/process-batch")
async def process_batch(
    items: list[Item],
    background_tasks: BackgroundTasks
):
    async def process_with_error_handling(item: Item):
        try:
            await process_item(item)
        except Exception as e:
            logger.error(f"Failed to process item {item.id}: {e}")
            await mark_item_failed(item.id)
    
    # Add all tasks - FastAPI runs them concurrently
    for item in items:
        background_tasks.add_task(process_with_error_handling, item)
    
    return {"status": "processing", "count": len(items)}

# Alternative: asyncio.gather for more control
@app.post("/process-batch")
async def process_batch(items: list[Item]):
    async def process_item_safe(item: Item):
        try:
            return await process_item(item)
        except Exception as e:
            logger.error(f"Failed to process item {item.id}: {e}")
            return None
    
    results = await asyncio.gather(
        *[process_item_safe(item) for item in items],
        return_exceptions=True  # Don't raise on first exception
    )
    
    successful = [r for r in results if r is not None and not isinstance(r, Exception)]
    failed = [r for r in results if isinstance(r, Exception)]
    
    return {
        "status": "complete",
        "successful": len(successful),
        "failed": len(failed)
    }
```

---

## Summary Checklist

- [ ] All I/O operations are async (no `requests`, `sqlite3`, `sync` in async functions)
- [ ] Database uses connection pooling (`asyncpg.create_pool`, reuse connections)
- [ ] `httpx.AsyncClient` created once and reused
- [ ] SQLAlchemy eager loading (`selectinload`, `joinedload`) for relationships
- [ ] Raw SQL uses batch queries instead of loops
- [ ] Pydantic validators use pre-compiled regex, no blocking calls
- [ ] Hot path models use `model_config = ConfigDict(from_attributes=True, validate_assignment=False)`
- [ ] `__slots__` on dataclasses where appropriate
- [ ] Large datasets use generators/streaming, not lists
- [ ] `ruff --select F811,F401,F841` finds no issues
- [ ] `vulture` reports no dead code
- [ ] `isort` and `ruff --fix` applied
- [ ] No `Any` in public API type signatures
- [ ] No bare `except:`, all exceptions explicitly caught
- [ ] `HTTPException` with appropriate status codes (404, 503, 500)
- [ ] Database connections use context managers (`async with pool.acquire()`)
- [ ] `BackgroundTasks.add_task()` for fire-and-forget with error handling
- [ ] `asyncio.gather(return_exceptions=True)` for multiple concurrent tasks
