# BUSINESS TESTING SKILL — SaaS Platforms

## Purpose
Functional/business testing blueprint for multi-tenant SaaS. Inspired by Popinz (education SaaS: persons/groups/planning/pedagogy/evaluations/billing).

## Core Principles

- Test as ADMIN unless role-specific behavior required
- Always assert status_code + response_body + DB state
- Use UUIDs for tenant isolation, never sequential IDs
- UTC timestamps for all datetime fields
- Mock Stripe/Twilio in unit tests; use test fixtures for integration

---

## Multi-Tenant Test Isolation

```python
def tenant_header(tenant_uuid: str) -> dict:
    return {"X-Tenant-ID": tenant_uuid}

@pytest.fixture
def tenant_a(db):
    t = create_tenant(slug="tenant-a")
    yield t
    db.query(Tenant).filter(Tenant.id == t.id).delete()

@pytest.fixture
def tenant_b(db):
    t = create_tenant(slug="tenant-b")
    yield t
    db.query(Tenant).filter(Tenant.id == t.id).delete()

def test_no_cross_tenant_visibility(tenant_a, tenant_b, client):
    create_person(tenant_id=tenant_a.id, name="Alice")
    create_person(tenant_id=tenant_b.id, name="Bob")
    
    r = client.get("/api/persons", headers=tenant_header(tenant_a.id))
    assert r.status_code == 200
    names = [p["name"] for p in r.json()["data"]]
    assert "Alice" in names
    assert "Bob" not in names
```

---

## CRUD Test Patterns

```python
def crud_suite(entity: str, create_payload: dict, update_payload: dict):
    """Generator pattern: create→read→update→read→delete→404"""
    
    def test_crud_flow(self):
        # CREATE
        r = self.client.post(f"/api/{entity}", json=self.create_payload)
        assert r.status_code == 201
        id = r.json()["data"]["id"]
        
        # READ
        r = self.client.get(f"/api/{entity}/{id}")
        assert r.status_code == 200
        assert r.json()["data"]["name"] == self.create_payload["name"]
        
        # UPDATE
        r = self.client.put(f"/api/{entity}/{id}", json=self.update_payload)
        assert r.status_code == 200
        
        # VERIFY UPDATE
        r = self.client.get(f"/api/{entity}/{id}")
        assert r.json()["data"]["name"] == self.update_payload["name"]
        
        # DELETE
        r = self.client.delete(f"/api/{entity}/{id}")
        assert r.status_code == 204
        
        # VERIFY GONE
        r = self.client.get(f"/api/{entity}/{id}")
        assert r.status_code == 404
    
    return test_crud_flow

class TestPersonCrud(crud_suite("persons", PERSON_PAYLOAD, {"name": "Updated"})): pass
```

---

## RBAC Test Matrix

```python
ROLES = ["admin", "teacher", "parent", "student"]
ENDPOINTS = [
    ("/api/persons", ["get", "post"]),
    ("/api/persons/{id}", ["get", "put", "delete"]),
    ("/api/groups", ["get", "post"]),
    ("/api/evaluations", ["get", "post"]),
    ("/api/billing/invoices", ["get"]),
    ("/api/admin/tenants", ["get", "post"]),
]

@pytest.mark.parametrize("role", ROLES)
@pytest.mark.parametrize("endpoint,methods", ENDPOINTS)
def test_rbac_matrix(role, endpoint, methods):
    user = create_user(role=role)
    client = authenticated_client(user)
    
    for method in methods:
        expected = 200 if role_has_access(role, method, endpoint) else 403
        r = method_client(client, method, endpoint)
        assert r.status_code == expected, f"{role} {method} {endpoint} → {r.status_code}"
```

---

## Billing Flow Tests (Stripe)

```python
def test_subscription_lifecycle():
    # CREATE subscription
    r = client.post("/api/billing/subscription", json={
        "plan_id": "plan_pro", "payment_method_id": "pm_test"})
    assert r.status_code == 201
    sub_id = r.json()["data"]["stripe_subscription_id"]
    assert r.json()["data"]["status"] == "active"
    
    # INVOICE generated
    r = client.get("/api/billing/invoices")
    assert any(inv["subscription_id"] == sub_id for inv in r.json()["data"])
    
    # CANCEL subscription
    r = client.post(f"/api/billing/subscription/{sub_id}/cancel")
    assert r.status_code == 200
    assert r.json()["data"]["status"] == "canceled"
    assert r.json()["data"]["cancel_at_period_end"] == True
    
    # REFUND (after period charge)
    r = client.post(f"/api/billing/invoices/{invoice_id}/refund", json={"amount": 10.00})
    assert r.status_code == 200
    assert r.json()["data"]["status"] == "refunded"

def test_subscription_auto_renew():
    sub = create_subscription(status="active", current_period_end=now()+7_days)
    mock_stripe_subscription_update(sub.stripe_id, {"status": "canceled"})
    run_subscription_renewal_job()
    db.refresh(sub)
    assert sub.status == "canceled"
```

---

## Data Integrity Tests

```python
def test_fk_constraint_blocks_invalid_reference():
    r = client.post("/api/evaluations", json={
        "student_id": "00000000-0000-0000-0000-000000000000"})
    assert r.status_code == 400
    assert "foreign key" in r.json()["error"].lower()

def test_cascade_delete_group_removes_members():
    group = create_group_with_members(n=5)
    client.delete(f"/api/groups/{group.id}")
    assert db.query(Person).filter(Person.group_id == group.id).count() == 0

def test_orphan_detection():
    person = create_person(group_id=None)
    r = client.get(f"/api/persons/{person.id}/group")
    assert r.status_code == 404 or r.json()["data"] is None

def test_unique_constraint_enforced():
    create_person(email="dup@example.com")
    r = client.post("/api/persons", json={"email": "dup@example.com"})
    assert r.status_code == 409
```

---

## Pagination/Filtering

```python
@pytest.mark.parametrize("n,expected_page", [(0, 1), (1, 1), (50, 2), (99, 2)])
def test_pagination_boundaries(n, expected_page):
    create_persons(n)
    r = client.get("/api/persons?page=1&per_page=50")
    assert r.status_code == 200
    assert r.json()["meta"]["total_pages"] == expected_page

def test_filter_by_date_range():
    create_event(starts_at=datetime(2024,1,1,tzinfo=UTC))
    create_event(starts_at=datetime(2024,6,1,tzinfo=UTC))
    r = client.get("/api/events?from=2024-01-01&to=2024-03-01")
    assert len(r.json()["data"]) == 1

def test_empty_result_returns_200():
    r = client.get("/api/persons?filter=nonexistent")
    assert r.status_code == 200
    assert r.json()["data"] == []

def test_sort_stable():
    r = client.get("/api/persons?sort=name&order=asc")
    names = [p["name"] for p in r.json()["data"]]
    assert names == sorted(names)
```

---

## Date/Timezone Handling

```python
def test_datetime_stored_utc():
    naive_dt = datetime(2024, 7, 15, 14, 30, 0)
    r = client.post("/api/events", json={"starts_at": naive_dt.isoformat()})
    event = db.query(Event).get(r.json()["data"]["id"])
    assert event.starts_at.tzinfo is not None

def test_datetime_display_respects_timezone():
    event = create_event(starts_at=datetime(2024,7,15,14,0,0,tzinfo=UTC))
    r = client.get(f"/api/events/{event.id}?tz=America/New_York")
    displayed = parse_datetime(r.json()["data"]["starts_at"])
    assert displayed.hour == 10  # UTC-4

def test_dst_transition_handling():
    create_evaluation(due_date=datetime(2024,3,10,2,30,0,tzinfo=UTC))  # DST spring forward
    r = client.get("/api/evaluations")
    assert r.status_code == 200
```

---

## Bulk Operations

```python
def test_csv_import_creates_entities():
    csv = "name,email,role\nAlice,alice@test.com,student\nBob,bob@test.com,teacher"
    r = client.post("/api/persons/import", files={"file": ("import.csv", csv, "text/csv")})
    assert r.status_code == 201
    assert r.json()["meta"]["created"] == 2
    assert r.json()["meta"]["errors"] == 0

def test_batch_update_respects_tenant():
    persons = [create_person(tenant_id=tenant_a.id) for _ in range(3)]
    r = client.post("/api/persons/batch", json={
        "ids": [p.id for p in persons],
        "updates": {"active": False}})
    assert all(not p.active for p in db.query(Person).filter(Person.id.in_([p.id for p in persons])))

def test_mass_delete_requires_confirmation():
    r = client.delete("/api/persons?all=true")
    assert r.status_code == 400
    assert "confirmation" in r.json()["error"]

def test_bulk_operation_partial_failure():
    ids = [valid_id, "00000000-0000-0000-0000-000000000000"]
    r = client.post("/api/groups/batch", json={"ids": ids, "action": "archive"})
    assert r.status_code == 207  # Multi-status
    assert r.json()["results"][1]["status"] == "error"
```

---

## Audit Trail Verification

```python
def test_audit_log_records_create():
    r = client.post("/api/persons", json=PERSON_PAYLOAD)
    audit = db.query(AuditLog).filter(
        AuditLog.entity_type == "person",
        AuditLog.entity_id == r.json()["data"]["id"],
        AuditLog.action == "create"
    ).first()
    assert audit is not None
    assert audit.actor_id == current_user.id
    assert audit.changes == {"name": [None, PERSON_PAYLOAD["name"]]}

def test_audit_log_records_delete():
    person = create_person()
    client.delete(f"/api/persons/{person.id}")
    audit = db.query(AuditLog).filter(
        AuditLog.entity_type == "person",
        AuditLog.entity_id == person.id,
        AuditLog.action == "delete"
    ).first()
    assert audit.changes == {"name": [person.name, None], "deleted_at": [None, Any]}

def test_audit_immutable(self):
    r = client.put(f"/api/audit-logs/{audit_id}", json={"action": "hack"})
    assert r.status_code == 405
```

---

## GDPR Compliance

```python
def test_data_export_contains_all_pii():
    create_person(name="Test", email="test@test.com", phone="+1234567890")
    r = client.get("/api/gdpr/export")
    assert r.status_code == 200
    assert "test@test.com" in r.json()["data"]["persons"][0]["email"]

def test_right_to_erasure_deletes_pii():
    person = create_person(email="erase@test.com")
    r = client.delete(f"/api/gdpr/erase/{person.id}")
    assert r.status_code == 204
    # Email should be anonymized
    db.expire_all()
    assert db.query(Person).get(person.id).email.startswith("deleted_")

def test_consent_tracking():
    r = client.post("/api/consent", json={"type": "marketing", "granted": True})
    assert r.status_code == 201
    consent = db.query(Consent).filter_by(person_id=current_user.id).first()
    assert consent.type == "marketing"
    assert consent.granted == True
    assert consent.timestamp is not None

def test_consent_withdrawal_revokes_access():
    create_consent(person_id=user.id, type="marketing", granted=True)
    client.post("/api/consent/withdraw", json={"type": "marketing"})
    consent = db.query(Consent).filter_by(person_id=user.id, type="marketing").first()
    assert consent.granted == False

def test_data_retention_auto_purge():
    old = create_person(created_at=now() - 365_days)
    run_retention_job(days=365)
    db.expire_all()
    assert db.query(Person).get(old.id) is None
```

---

## EVALUATION CASES

| # | Case | Key Assertions |
|---|------|----------------|
| 1 | Create person → verify in DB + API response | status 201, UUID returned, DB row exists |
| 2 | Admin deletes student → cascade removes enrollments | enrollments count = 0, audit log entry |
| 3 | Teacher POST /api/evaluations → 201 | role has permission |
| 4 | Student GET /api/billing/invoices → 403 | RBAC enforced |
| 5 | Stripe webhook: invoice.paid → subscription status = active | async job processes event |
| 6 | Import CSV with 1 invalid row → 2 created, 1 error | partial success, error report |
| 7 | Paginate 100 persons, page 3, per_page=25 | correct 4 items, has_next=False |
| 8 | Event at 01:30 UTC on DST day → display in EST | hour=21 (UTC-4), no data loss |
| 9 | Concurrent batch update same entity → last wins | no orphan state, audit shows both |
| 10 | GDPR export for deleted user → anonymized data | no real PII in export |
| 11 | Unique email constraint → second create fails 409 | DB constraint + API error |
| 12 | Student transfers group → enrollments moved | FK updated, audit logged |
| 13 | Subscription refund → invoice.status = refunded | Stripe mock called, DB updated |
| 14 | Filter persons by active=false → only inactive | SQL WHERE clause applied |
| 15 | Consent withdrawal → new consent entry, old unchanged | immutable log, revocation tracked |

---

## Test Utilities

```python
def create_tenant(**kwargs) -> Tenant:
    return db.query(Tenant).create(**kwargs)

def create_user(role: str, tenant_id: str = None, **kwargs) -> User:
    defaults = {"role": role, "tenant_id": tenant_id or current_tenant()}
    defaults.update(kwargs)
    return db.query(User).create(**defaults)

def authenticated_client(user: User) -> TestClient:
    token = jwt_encode({"sub": user.id, "role": user.role})
    return TestClient(app, headers={"Authorization": f"Bearer {token}"})

def assert_schema(r: Response, schema: dict):
    for field, expected_type in schema.items():
        assert field in r.json()["data"]
        assert isinstance(r.json()["data"][field], expected_type)
```

---

## Anti-Patterns to Avoid

- Do NOT assert only status_code (check body)
- Do NOT share fixtures across tenants without isolation
- Do NOT use real timestamps in assertions (use `Any` matcher)
- Do NOT test Stripe without mock (use `stripe.StripeClient` patch)
- Do NOT ignore timezone-naive datetime (reject at API boundary)
