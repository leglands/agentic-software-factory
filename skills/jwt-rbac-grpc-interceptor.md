---
name: jwt-rbac-grpc-interceptor
description: Implement JWT refresh token flow with RBAC authorization in gRPC interceptors using tonic (Rust) and grpc-web (TypeScript). Covers token pair management, role extraction, permission guards, tenant isolation, and secure httpOnly cookie storage.
trigger: |
  Match when user asks about:
  - JWT authentication in gRPC/tonic interceptors
  - RBAC authorization middleware for gRPC services
  - Refresh token flow with access/refresh pairs
  - gRPC-web authentication with TypeScript
  - Multi-tenant isolation via tenant_id claims
  - Permission-based access control guards
  - Secure token storage patterns (httpOnly cookies)
  - Role/permission extraction from JWT claims
eval_cases:
  - id: 1
    prompt: "Write a tonic (Rust) interceptor that validates a JWT access token from metadata, extracts the user_id and roles claim, and returns gRPC status UNAUTHENTICATED on invalid/expired tokens."
  - id: 2
    prompt: "Implement a RoleGuard tonic middleware that checks if the authenticated user has the required permission for an RPC method. Include a custom Attribute for #[has_permission]."
  - id: 3
    prompt: "Design a TypeScript grpc-web interceptor that automatically refreshes the access token using a refresh token stored in httpOnly cookie. Handle 401 responses and retry with new token."
  - id: 4
    prompt: "Create a token refresh endpoint/service that accepts a refresh token, validates it, issues a new access/refresh pair, and sets httpOnly cookies. Include rotation of refresh tokens."
  - id: 5
    prompt: "Write a multi-tenant RBAC middleware chain for tonic that extracts tenant_id from JWT claims and validates that the user belongs to the requested tenant."
  - id: 6
    prompt: "Implement JWT claims struct with standard fields (sub, exp, iat, roles, permissions, tenant_id) and a builder pattern for constructing claims in auth service."
  - id: 7
    prompt: "Create a permission matrix defining access for roles: admin, moderator, user, guest. Map RPC methods to required permissions. Show how to enforce in interceptor."
  - id: 8
    prompt: "Write client-side TypeScript code to attach JWT access token to grpc-web requests via metadata. Include error handling for expired tokens and redirect to login."
  - id: 9
    prompt: "Implement sliding window refresh token expiration. Refresh token should be valid for 7 days but refresh on each use. Show how to detect reuse and revoke family."
  - id: 10
    prompt: "Create integration tests for the auth flow: login, authenticated request, token refresh, permission denied, tenant isolation violation, concurrent refresh race."
  - id: 11
    prompt: "Design the JWT token pair structure with jti (JWT ID) for refresh token rotation tracking. Show how to store issued token IDs for revocation."
  - id: 12
    prompt: "Write tonic Interceptor that extracts tenant_id from JWT and injects it into request context. Services read tenant context without parsing JWT again."
---

# JWT Refresh Tokens + RBAC Authorization in gRPC Interceptors

## Overview

This skill covers authentication and authorization for gRPC services using:
- **Rust/tonic** for the gRPC server
- **TypeScript/grpc-web** for client-side
- **JWT access/refresh token pairs** with secure httpOnly cookie storage
- **RBAC** (Role-Based Access Control) with permission guards
- **Multi-tenant isolation** via `tenant_id` claim

---

## 1. JWT Claims Structure

### Rust Claims Definition

```rust
use serde::{Deserialize, Serialize};
use std::collections::HashSet;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Claims {
    pub sub: String,          // user_id
    pub exp: usize,           // expiration timestamp
    pub iat: usize,           // issued at
    pub jti: Option<String>,  // JWT ID (for refresh token tracking)
    pub roles: Vec<String>,   // e.g., ["admin", "user"]
    pub permissions: HashSet<String>, // e.g., ["posts:read", "posts:write"]
    pub tenant_id: String,    // multi-tenant isolation
}

impl Claims {
    pub fn builder() -> ClaimsBuilder {
        ClaimsBuilder::default()
    }

    pub fn has_role(&self, role: &str) -> bool {
        self.roles.iter().any(|r| r == role)
    }

    pub fn has_permission(&self, permission: &str) -> bool {
        self.permissions.contains(permission)
    }
}

#[derive(Default)]
pub struct ClaimsBuilder {
    sub: Option<String>,
    exp: Option<usize>,
    iat: Option<usize>,
    jti: Option<String>,
    roles: Vec<String>,
    permissions: HashSet<String>,
    tenant_id: Option<String>,
}

impl ClaimsBuilder {
    pub fn user_id(mut self, sub: impl Into<String>) -> Self {
        self.sub = Some(sub.into());
        self
    }

    pub fn expiration(mut self, exp: usize) -> Self {
        self.exp = Some(exp);
        self
    }

    pub fn issued_at(mut self, iat: usize) -> Self {
        self.iat = Some(iat);
        self
    }

    pub fn jti(mut self, jti: impl Into<String>) -> Self {
        self.jti = Some(jti.into());
        self
    }

    pub fn roles(mut self, roles: Vec<String>) -> Self {
        self.roles = roles;
        self
    }

    pub fn permissions(mut self, permissions: HashSet<String>) -> Self {
        self.permissions = permissions;
        self
    }

    pub fn tenant_id(mut self, tenant_id: impl Into<String>) -> Self {
        self.tenant_id = Some(tenant_id.into());
        self
    }

    pub fn build(self) -> Claims {
        Claims {
            sub: self.sub.expect("sub required"),
            exp: self.exp.expect("exp required"),
            iat: self.iat.unwrap_or_else(|| std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap().as_secs() as usize),
            jti: self.jti,
            roles: self.roles,
            permissions: self.permissions,
            tenant_id: self.tenant_id.expect("tenant_id required"),
        }
    }
}
```

### TypeScript Claims Interface

```typescript
export interface JwtClaims {
  sub: string;
  exp: number;
  iat: number;
  jti?: string;
  roles: string[];
  permissions: string[];
  tenant_id: string;
}

export interface TokenPair {
  access_token: string;
  refresh_token: string;
}
```

---

## 2. Permission Matrix

```rust
use std::collections::HashMap;

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum Permission {
    PostsRead,
    PostsWrite,
    PostsDelete,
    UsersRead,
    UsersWrite,
    UsersDelete,
    TenantAdmin,
    SystemAdmin,
}

impl Permission {
    pub fn as_str(&self) -> &'static str {
        match self {
            Permission::PostsRead => "posts:read",
            Permission::PostsWrite => "posts:write",
            Permission::PostsDelete => "posts:delete",
            Permission::UsersRead => "users:read",
            Permission::UsersWrite => "users:write",
            Permission::UsersDelete => "users:delete",
            Permission::TenantAdmin => "tenant:admin",
            Permission::SystemAdmin => "system:admin",
        }
    }
}

#[derive(Debug, Clone)]
pub struct RolePermissions {
    pub role: &'static str,
    pub permissions: Vec<Permission>,
}

pub fn role_permissions_matrix() -> HashMap<String, Vec<Permission>> {
    HashMap::from([
        ("guest".to_string(), vec![Permission::PostsRead]),
        ("user".to_string(), vec![Permission::PostsRead, Permission::PostsWrite]),
        ("moderator".to_string(), vec![Permission::PostsRead, Permission::PostsWrite, Permission::PostsDelete, Permission::UsersRead]),
        ("admin".to_string(), vec![Permission::PostsRead, Permission::PostsWrite, Permission::PostsDelete, Permission::UsersRead, Permission::UsersWrite, Permission::UsersDelete, Permission::TenantAdmin]),
        ("superadmin".to_string(), vec![Permission::PostsRead, Permission::PostsWrite, Permission::PostsDelete, Permission::UsersRead, Permission::UsersWrite, Permission::UsersDelete, Permission::TenantAdmin, Permission::SystemAdmin]),
    ])
}
```

---

## 3. Tonic JWT Interceptor

```rust
use tonic::{service::Interceptor, Status, Request, Response};
use http::HeaderMap;
use jsonwebtoken::{decode, DecodingKey, Validation, Algorithm};

#[derive(Clone)]
pub struct JwtInterceptor {
    decoding_key: DecodingKey,
    validation: Validation,
}

impl JwtInterceptor {
    pub fn new(secret: &[u8]) -> Self {
        let decoding_key = DecodingKey::from_secret(secret);
        let mut validation = Validation::new(Algorithm::HS256);
        validation.validate_exp = true;
        
        Self {
            decoding_key,
            validation,
        }
    }

    pub fn with_issuer(mut self, issuer: &str) -> Self {
        self.validation.set_issuer(&[issuer]);
        self.validation.validate_exp = true;
        self
    }
}

impl Interceptor for JwtInterceptor {
    fn call(&mut self, mut request: Request<()>) -> Result<Response<()>, Status> {
        let metadata = request.metadata();
        
        let token = extract_bearer_token(metadata)
            .ok_or_else(|| Status::unauthenticated("Missing authorization header"))?;

        let claims = validate_token(token, &self.decoding_key, &self.validation)
            .map_err(|e| Status::unauthenticated(format!("Invalid token: {}", e)))?;

        request.extensions_mut().insert(ClaimsContext::new(claims));
        
        Ok(request.into_response())
    }
}

fn extract_bearer_token(metadata: & tonic::metadata::MetadataMap) -> Option<String> {
    let auth_header = metadata.get("authorization")?;
    let auth_str = auth_header.to_str().ok()?;
    auth_str.strip_prefix("Bearer ").map(|s| s.to_string())
}

fn validate_token(
    token: &str,
    key: &DecodingKey,
    validation: &Validation,
) -> Result<Claims, jsonwebtoken::errors::Error> {
    let token_data = decode::<Claims>(token, key, validation)?;
    Ok(token_data.claims)
}

#[derive(Clone)]
pub struct ClaimsContext {
    pub claims: Claims,
}

impl ClaimsContext {
    pub fn new(claims: Claims) -> Self {
        Self { claims }
    }

    pub fn user_id(&self) -> &str {
        &self.claims.sub
    }

    pub fn tenant_id(&self) -> &str {
        &self.claims.tenant_id
    }

    pub fn roles(&self) -> &[String] {
        &self.claims.roles
    }

    pub fn permissions(&self) -> &std::collections::HashSet<String> {
        &self.claims.permissions
    }

    pub fn has_role(&self, role: &str) -> bool {
        self.claims.has_role(role)
    }

    pub fn has_permission(&self, permission: &str) -> bool {
        self.claims.has_permission(permission)
    }
}
```

---

## 4. Permission Guard Middleware

```rust
use tonic::{Request, Status};
use std::future::Future;
use std::pin::Pin;
use std::marker::PhantomData;

#[derive(Clone)]
pub struct RequiredPermission {
    pub permission: &'static str,
}

impl RequiredPermission {
    pub const fn new(permission: &'static str) -> Self {
        Self { permission }
    }
}

pub trait PermissionGuard: Send + Sync {
    fn check(&self, claims: &Claims) -> bool;
}

pub struct RoleGuard {
    required_roles: Vec<String>,
}

impl RoleGuard {
    pub fn one_of(roles: &[&str]) -> Self {
        Self {
            required_roles: roles.iter().map(|s| s.to_string()).collect(),
        }
    }
}

impl PermissionGuard for RoleGuard {
    fn check(&self, claims: &Claims) -> bool {
        self.required_roles.iter().any(|r| claims.has_role(r))
    }
}

pub struct PermissionGuardLayer<P: PermissionGuard> {
    guard: P,
    _phantom: PhantomData<()>,
}

impl<P: PermissionGuard> PermissionGuardLayer<P> {
    pub fn new(guard: P) -> Self {
        Self {
            guard,
            _phantom: PhantomData,
        }
    }
}

pub fn require_permission(permission: &'static str) -> RequiredPermission {
    RequiredPermission::new(permission)
}

pub fn require_role(role: &str) -> RoleGuard {
    RoleGuard::one_of(&[role])
}

pub fn require_any_role(roles: &[&str]) -> RoleGuard {
    RoleGuard::one_of(roles)
}

pub async fn check_permission<G: PermissionGuard + 'static>(
    guard: &G,
    request: Request<()>,
) -> Result<Request<()>, Status> {
    let claims = request
        .extensions()
        .get::<ClaimsContext>()
        .ok_or_else(|| Status::unauthenticated("No claims in context"))?
        .claims();

    if guard.check(claims) {
        Ok(request)
    } else {
        Err(Status::permission_denied("Insufficient permissions"))
    }
}
```

---

## 5. Tenant Isolation Middleware

```rust
use tonic::{Request, Status};

#[derive(Clone)]
pub struct TenantContext {
    tenant_id: String,
    user_id: String,
}

impl TenantContext {
    pub fn new(tenant_id: String, user_id: String) -> Self {
        Self { tenant_id, user_id }
    }

    pub fn tenant_id(&self) -> &str {
        &self.tenant_id
    }

    pub fn user_id(&self) -> &str {
        &self.user_id
    }
}

pub struct TenantInterceptor {
    validation: bool,
}

impl TenantInterceptor {
    pub fn new() -> Self {
        Self { validation: true }
    }

    pub fn without_validation() -> Self {
        Self { validation: false }
    }
}

impl tonic::service::Interceptor for TenantInterceptor {
    fn call(&self, mut request: Request<()>) -> Result<Response<()>, Status> {
        let claims_ctx = request
            .extensions()
            .get::<ClaimsContext>()
            .ok_or_else(|| Status::unauthenticated("Missing claims"))?;

        let tenant_ctx = TenantContext::new(
            claims_ctx.claims.tenant_id.clone(),
            claims_ctx.claims.sub.clone(),
        );

        request.extensions_mut().insert(tenant_ctx);

        Ok(request.into_response())
    }
}

pub fn extract_tenant_id(request: &Request<()>) -> Result<String, Status> {
    request
        .extensions()
        .get::<TenantContext>()
        .map(|ctx| ctx.tenant_id().to_string())
        .ok_or_else(|| Status::internal("Tenant context not set"))
}

pub fn validate_tenant_access(
    request: &Request<()>,
    requested_tenant_id: &str,
) -> Result<(), Status> {
    let ctx = request
        .extensions()
        .get::<TenantContext>()
        .ok_or_else(|| Status::unauthenticated("Missing tenant context"))?;

    if ctx.tenant_id() != requested_tenant_id {
        return Err(Status::permission_denied(format!(
            "Access denied to tenant '{}'",
            requested_tenant_id
        )));
    }

    Ok(())
}
```

---

## 6. Token Refresh Service

### gRPC Refresh Service Definition

```protobuf
syntax = "proto3";

package auth.v1;

service AuthService {
  rpc RefreshToken(RefreshTokenRequest) returns (RefreshTokenResponse);
  rpc RevokeTokens(RevokeTokensRequest) returns (RevokeTokensResponse);
}

message RefreshTokenRequest {
  string refresh_token = 1;
}

message RefreshTokenResponse {
  string access_token = 1;
  string refresh_token = 2;
  int64 access_token_expires_in = 3;
  int64 refresh_token_expires_in = 4;
}

message RevokeTokensRequest {
  string refresh_token = 1;
}

message RevokeTokensResponse {
  bool success = 1;
}
```

### Rust Refresh Token Handler

```rust
use std::sync::Arc;
use tokio::sync::RwLock;
use std::collections::HashSet;
use jsonwebtoken::{encode, EncodingKey, Header};
use uuid::Uuid;
use std::collections::hash_map::DefaultHasher;
use std::hash::{Hash, Hasher};

pub struct RefreshTokenStore {
    issued_tokens: RwLock<HashSet<u64>>,
    revoked_families: RwLock<HashSet<u64>>,
}

impl RefreshTokenStore {
    pub fn new() -> Self {
        Self {
            issued_tokens: RwLock::new(HashSet::new()),
            revoked_families: RwLock::new(HashSet::new()),
        }
    }

    pub async fn store_token_hash(&self, jti: &str) {
        let hash = self.hash_jti(jti);
        self.issued_tokens.write().await.insert(hash);
    }

    pub async fn is_token_known(&self, jti: &str) -> bool {
        let hash = self.hash_jti(jti);
        self.issued_tokens.read().await.contains(&hash)
    }

    pub async fn revoke_token_family(&self, jti: &str) {
        let hash = self.hash_jti(jti);
        self.revoked_families.write().await.insert(hash);
    }

    pub async fn is_family_revoked(&self, jti: &str) -> bool {
        let hash = self.hash_jti(jti);
        self.revoked_families.read().await.contains(&hash)
    }

    fn hash_jti(&self, jti: &str) -> u64 {
        let mut hasher = DefaultHasher::new();
        jti.hash(&mut hasher);
        hasher.finish()
    }
}

pub struct TokenService {
    secret: Vec<u8>,
    access_token_ttl: usize,
    refresh_token_ttl: usize,
    token_store: Arc<RefreshTokenStore>,
}

impl TokenService {
    pub fn new(
        secret: Vec<u8>,
        access_token_ttl: usize,
        refresh_token_ttl: usize,
        token_store: Arc<RefreshTokenStore>,
    ) -> Self {
        Self {
            secret,
            access_token_ttl,
            refresh_token_ttl,
            token_store,
        }
    }

    pub async fn refresh_tokens(
        &self,
        refresh_token: &str,
    ) -> Result<TokenPair, TokenRefreshError> {
        let token_data = jsonwebtoken::decode::<Claims>(
            refresh_token,
            &DecodingKey::from_secret(&self.secret),
            &Validation::new(Algorithm::HS256),
        )
        .map_err(|_| TokenRefreshError::InvalidToken)?;

        let claims = token_data.claims;

        if !self.token_store.is_token_known(&claims.jti.clone().unwrap_or_default()).await {
            self.token_store.revoke_token_family(&claims.jti.clone().unwrap_or_default()).await;
            return Err(TokenRefreshError::TokenReuseDetected);
        }

        if self.token_store.is_family_revoked(&claims.jti.clone().unwrap_or_default()).await {
            return Err(TokenRefreshError::TokenReuseDetected);
        }

        self.token_store.revoke_token_family(&claims.jti.unwrap_or_default()).await;

        let new_pair = self.generate_token_pair(&claims.sub, &claims.roles, &claims.permissions, &claims.tenant_id).await?;

        Ok(new_pair)
    }

    pub async fn generate_token_pair(
        &self,
        user_id: &str,
        roles: &[String],
        permissions: &HashSet<String>,
        tenant_id: &str,
    ) -> Result<TokenPair, TokenRefreshError> {
        let now = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_secs() as usize;

        let access_jti = Uuid::new_v4().to_string();
        let refresh_jti = Uuid::new_v4().to_string();

        let access_claims = Claims::builder()
            .user_id(user_id)
            .expiration(now + self.access_token_ttl)
            .issued_at(now)
            .jti(&access_jti)
            .roles(roles.to_vec())
            .permissions(permissions.clone())
            .tenant_id(tenant_id)
            .build();

        let refresh_claims = Claims::builder()
            .user_id(user_id)
            .expiration(now + self.refresh_token_ttl)
            .issued_at(now)
            .jti(&refresh_jti)
            .roles(roles.to_vec())
            .permissions(permissions.clone())
            .tenant_id(tenant_id)
            .build();

        let access_token = encode(
            &Header::default(),
            &access_claims,
            &EncodingKey::from_secret(&self.secret),
        )
        .map_err(|_| TokenRefreshError::TokenGenerationFailed)?;

        let refresh_token = encode(
            &Header::default(),
            &refresh_claims,
            &EncodingKey::from_secret(&self.secret),
        )
        .map_err(|_| TokenRefreshError::TokenGenerationFailed)?;

        self.token_store.store_token_hash(&refresh_jti).await;

        Ok(TokenPair {
            access_token,
            refresh_token,
        })
    }
}

#[derive(Debug)]
pub enum TokenRefreshError {
    InvalidToken,
    TokenReuseDetected,
    TokenGenerationFailed,
}
```

---

## 7. TypeScript grpc-web Interceptor

```typescript
import * as grpcWeb from 'grpc-web';
import { Metadata } from 'grpc-web';
import { TokenPair, JwtClaims } from './types';

const ACCESS_TOKEN_COOKIE = 'access_token';
const REFRESH_TOKEN_COOKIE = 'refresh_token';
const TOKEN_REFRESH_ENDPOINT = '/api/auth/refresh';

export class AuthInterceptor implements grpcWeb.Interceptor {
  private refreshPromise: Promise<TokenPair> | null = null;
  private onUnauthorized: (() => void) | null = null;

  constructor(options?: { onUnauthorized?: () => void }) {
    this.onUnauthorized = options?.onUnauthorized ?? null;
  }

  async intercept(
    request: grpcWeb.Request,
    invoker: (request: grpcWeb.Request) => Promise<grpcWeb.Response>
  ): Promise<grpcWeb.Response> {
    try {
      const token = this.getAccessToken();
      if (token) {
        request.getMetadata()['Authorization'] = `Bearer ${token}`;
      }
      return await invoker(request);
    } catch (error) {
      if (this.isUnauthorizedError(error) && this.getRefreshToken()) {
        return this.handleUnauthorized(request, invoker);
      }
      throw error;
    }
  }

  private async handleUnauthorized(
    request: grpcWeb.Request,
    invoker: (request: grpcWeb.Request) => Promise<grpcWeb.Response>
  ): Promise<grpcWeb.Response> {
    try {
      const newTokens = await this.refreshTokens();
      const metadata = request.getMetadata();
      metadata['Authorization'] = `Bearer ${newTokens.access_token}`;
      return await invoker(request);
    } catch (refreshError) {
      this.clearTokens();
      if (this.onUnauthorized) {
        this.onUnauthorized();
      }
      throw refreshError;
    }
  }

  async refreshTokens(): Promise<TokenPair> {
    if (this.refreshPromise) {
      return this.refreshPromise;
    }

    this.refreshPromise = this.doRefreshTokens();
    try {
      return await this.refreshPromise;
    } finally {
      this.refreshPromise = null;
    }
  }

  private async doRefreshTokens(): Promise<TokenPair> {
    const refreshToken = this.getRefreshToken();
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    const response = await fetch(TOKEN_REFRESH_ENDPOINT, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ refresh_token: refreshToken }),
      credentials: 'include',
    });

    if (!response.ok) {
      throw new grpcWeb.Status.create(grpcWeb.Status.UNAUTHENTICATED, 'Token refresh failed');
    }

    const data = await response.json() as { 
      access_token: string; 
      refresh_token: string;
    };

    this.setAccessToken(data.access_token);
    this.setRefreshToken(data.refresh_token);

    return { access_token: data.access_token, refresh_token: data.refresh_token };
  }

  private getAccessToken(): string | null {
    return this.getCookie(ACCESS_TOKEN_COOKIE);
  }

  private getRefreshToken(): string | null {
    return this.getCookie(REFRESH_TOKEN_COOKIE);
  }

  private setAccessToken(token: string): void {
    this.setCookie(ACCESS_TOKEN_COOKIE, token, { httpOnly: false, secure: true, sameSite: 'strict' });
  }

  private setRefreshToken(token: string): void {
    this.setCookie(REFRESH_TOKEN_COOKIE, token, { httpOnly: true, secure: true, sameSite: 'strict', path: '/' });
  }

  private clearTokens(): void {
    this.deleteCookie(ACCESS_TOKEN_COOKIE);
    this.deleteCookie(REFRESH_TOKEN_COOKIE);
  }

  private getCookie(name: string): string | null {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) {
      return parts.pop()?.split(';').shift() ?? null;
    }
    return null;
  }

  private setCookie(name: string, value: string, options: CookieOptions): void {
    const { httpOnly, secure, sameSite, path, maxAge } = options;
    let cookieStr = `${encodeURIComponent(name)}=${encodeURIComponent(value)}`;
    if (secure) cookieStr += '; Secure';
    if (httpOnly) cookieStr += '; HttpOnly';
    if (sameSite) cookieStr += `; SameSite=${sameSite}`;
    if (path) cookieStr += `; Path=${path}`;
    if (maxAge) cookieStr += `; Max-Age=${maxAge}`;
    document.cookie = cookieStr;
  }

  private deleteCookie(name: string): void {
    document.cookie = `${name}=; Max-Age=0; Path=/`;
  }

  private isUnauthorizedError(error: unknown): boolean {
    if (error instanceof grpcWeb.Status) {
      return error.code === grpcWeb.Status.UNAUTHENTICATED;
    }
    return false;
  }
}

interface CookieOptions {
  httpOnly?: boolean;
  secure?: boolean;
  sameSite?: 'strict' | 'lax' | 'none';
  path?: string;
  maxAge?: number;
}
```

---

## 8. TypeScript Client Usage

```typescript
import { grpc } from 'grpc-web';
import { AuthInterceptor } from './auth-interceptor';
import { SomeServiceClient } from './generated/some_service_pb_service';

const authInterceptor = new AuthInterceptor({
  onUnauthorized: () => {
    window.location.href = '/login';
  },
});

const client = new SomeServiceClient('https://api.example.com', {
  interceptors: [authInterceptor],
});

async function makeAuthenticatedCall() {
  const metadata = new grpc.Metadata();
  
  try {
    const response = await client.someRpc(
      new SomeRequest(),
      metadata
    );
    return response;
  } catch (error) {
    console.error('RPC failed:', error);
    throw error;
  }
}

function attachTokenToMetadata(metadata: grpc.Metadata, token: string): grpc.Metadata {
  metadata.set('Authorization', `Bearer ${token}`);
  return metadata;
}
```

---

## 9. HTTP-only Cookie Server Handler (Express/Node)

```typescript
import express, { Request, Response, NextFunction } from 'express';
import { decode, verify, Algorithm } from 'jsonwebtoken';
import { TokenPair, JwtClaims } from './types';

const ACCESS_TOKEN_COOKIE = 'access_token';
const REFRESH_TOKEN_COOKIE = 'refresh_token';
const ACCESS_TOKEN_MAX_AGE = 15 * 60;
const REFRESH_TOKEN_MAX_AGE = 7 * 24 * 60 * 60;

export function authRouter(tokenService: TokenService): express.Router {
  const router = express.Router();

  router.post('/refresh', async (req: Request, res: Response, next: NextFunction) => {
    try {
      const { refresh_token } = req.body;

      if (!refresh_token) {
        res.status(400).json({ error: 'Refresh token required' });
        return;
      }

      const result = await tokenService.refreshTokens(refresh_token);

      res.cookie(ACCESS_TOKEN_COOKIE, result.access_token, {
        httpOnly: false,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'strict',
        maxAge: ACCESS_TOKEN_MAX_AGE * 1000,
      });

      res.cookie(REFRESH_TOKEN_COOKIE, result.refresh_token, {
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'strict',
        maxAge: REFRESH_TOKEN_MAX_AGE * 1000,
        path: '/',
      });

      res.json({
        access_token: result.access_token,
        refresh_token: result.refresh_token,
        access_token_expires_in: ACCESS_TOKEN_MAX_AGE,
        refresh_token_expires_in: REFRESH_TOKEN_MAX_AGE,
      });
    } catch (error) {
      res.clearCookie(ACCESS_TOKEN_COOKIE);
      res.clearCookie(REFRESH_TOKEN_COOKIE);
      res.status(401).json({ error: 'Invalid or expired refresh token' });
    }
  });

  router.post('/logout', (req: Request, res: Response) => {
    const refreshToken = req.cookies[REFRESH_TOKEN_COOKIE];
    
    if (refreshToken) {
      tokenService.revokeRefreshToken(refreshToken).catch(console.error);
    }

    res.clearCookie(ACCESS_TOKEN_COOKIE);
    res.clearCookie(REFRESH_TOKEN_COOKIE, { path: '/' });
    res.json({ success: true });
  });

  return router;
}

export function cookieParser(): express.RequestHandler {
  return express.cookieParser();
}
```

---

## 10. gRPC Service with RBAC Example

### Rust Service Implementation

```rust
use tonic::{Request, Response, Status};
use std::sync::Arc;
use crate::auth::{ClaimsContext, TenantContext, PermissionGuard, RoleGuard};
use crate::auth::Permission::PostsWrite;

#[derive(Clone)]
pub struct PostsService {
    db: Arc<Database>,
}

#[tonic::async_trait]
impl posts_server::Posts for PostsService {
    async fn create_post(
        &self,
        request: Request<CreatePostRequest>,
    ) -> Result<Response<Post>, Status> {
        let claims = request
            .extensions()
            .get::<ClaimsContext>()
            .ok_or_else(|| Status::unauthenticated("Missing claims"))?
            .claims();

        if !claims.has_permission("posts:write") {
            return Err(Status::permission_denied("Requires posts:write permission"));
        }

        let tenant_ctx = request
            .extensions()
            .get::<TenantContext>()
            .ok_or_else(|| Status::internal("Missing tenant context"))?;

        let post = self.db
            .create_post(CreatePostRequest {
                title: request.get_ref().title.clone(),
                content: request.get_ref().content.clone(),
            }, &tenant_ctx.tenant_id())
            .await
            .map_err(|e| Status::internal(format!("Database error: {}", e)))?;

        Ok(Response::new(post))
    }

    async fn list_posts(
        &self,
        request: Request<ListPostsRequest>,
    ) -> Result<Response<ListPostsResponse>, Status> {
        let tenant_ctx = request
            .extensions()
            .get::<TenantContext>()
            .ok_or_else(|| Status::internal("Missing tenant context"))?;

        let posts = self.db
            .list_posts(&tenant_ctx.tenant_id())
            .await
            .map_err(|e| Status::internal(format!("Database error: {}", e)))?;

        Ok(Response::new(ListPostsResponse { posts }))
    }

    async fn delete_post(
        &self,
        request: Request<DeletePostRequest>,
    ) -> Result<Response<DeletePostResponse>, Status> {
        let claims = request
            .extensions()
            .get::<ClaimsContext>()
            .ok_or_else(|| Status::unauthenticated("Missing claims"))?
            .claims();

        if !claims.has_permission("posts:delete") {
            return Err(Status::permission_denied("Requires posts:delete permission"));
        }

        let tenant_ctx = request
            .extensions()
            .get::<TenantContext>()
            .ok_or_else(|| Status::internal("Missing tenant context"))?;

        self.db
            .delete_post(request.get_ref().post_id, &tenant_ctx.tenant_id())
            .await
            .map_err(|e| Status::internal(format!("Database error: {}", e)))?;

        Ok(Response::new(DeletePostResponse { success: true }))
    }
}

fn build_server() -> posts_server::PostsServer<PostsService> {
    let jwtInterceptor = JwtInterceptor::new(secret.as_bytes())
        .with_issuer("auth-service");

    let tenantInterceptor = TenantInterceptor::new();

    tonic::transport::Server::builder()
        .layer(tonic::service::interceptor(jwtInterceptor))
        .layer(tonic::service::interceptor(tenantInterceptor))
        .add_service(posts_server::PostsServer::new(PostsService::new(db)))
        .into_service()
}
```

---

## 11. RBAC Middleware Chain

```rust
use std::future::Future;
use std::pin::Pin;
use std::sync::Arc;
use tonic::{Request, Status, Response};
use tower::{Layer, Service};

#[derive(Clone)]
pub struct RbacLayer {
    auth_interceptor: JwtInterceptor,
    tenant_interceptor: TenantInterceptor,
}

impl RbacLayer {
    pub fn new(secret: &[u8]) -> Self {
        Self {
            auth_interceptor: JwtInterceptor::new(secret),
            tenant_interceptor: TenantInterceptor::new(),
        }
    }
}

impl<S> Layer<S> for RbacLayer {
    type Service = RbacService<S>;

    fn layer(&self, inner: S) -> Self::Service {
        RbacService {
            inner,
            auth_interceptor: self.auth_interceptor.clone(),
            tenant_interceptor: self.tenant_interceptor.clone(),
        }
    }
}

#[derive(Clone)]
pub struct RbacService<S> {
    inner: S,
    auth_interceptor: JwtInterceptor,
    tenant_interceptor: TenantInterceptor,
}

impl<S, T> Service<Request<T>> for RbacService<S>
where
    S: Service<Request<T>, Response = Response<()>> + Send + 'static,
    S::Future: Send + 'static,
{
    type Response = Response<()>;
    type Error = Status;
    type Future = Pin<Box<dyn Future<Output = Result<Self::Response, Self::Error>> + Send>>;

    fn poll_ready(
        &mut self,
        cx: &mut std::task::Context<'_>,
    ) -> std::task::Poll<Result<(), Self::Error>> {
        self.inner.poll_ready(cx)
    }

    fn call(&mut self, mut request: Request<T>) -> Self::Future {
        let mut auth_interceptor = self.auth_interceptor.clone();
        let mut tenant_interceptor = self.tenant_interceptor.clone();

        Box::pin(async move {
            let mut request = auth_interceptor.call(request).await?;
            request = tenant_interceptor.call(request).await?;
            self.inner.call(request).await
        })
    }
}
```

---

## 12. Integration Test Example

```rust
#[cfg(test)]
mod auth_integration_tests {
    use super::*;
    use jsonwebtoken::{encode, EncodingKey, Header};
    use std::collections::HashSet;

    fn create_test_token(claims: &Claims, secret: &[u8]) -> String {
        encode(
            &Header::default(),
            claims,
            &EncodingKey::from_secret(secret),
        )
        .unwrap()
    }

    fn test_claims() -> Claims {
        let mut permissions = HashSet::new();
        permissions.insert("posts:read".to_string());
        permissions.insert("posts:write".to_string());

        Claims::builder()
            .user_id("user-123")
            .expiration(chrono::Utc::now().timestamp() as usize + 3600)
            .issued_at(chrono::Utc::now().timestamp() as usize)
            .jti("test-jti-1")
            .roles(vec!["user".to_string()])
            .permissions(permissions)
            .tenant_id("tenant-abc")
            .build()
    }

    #[tokio::test]
    async fn test_valid_token_authentication() {
        let secret = b"test-secret-key-256-bits-long!!!";
        let claims = test_claims();
        let token = create_test_token(&claims, secret);

        let interceptor = JwtInterceptor::new(secret);
        let request = Request::builder()
            .metadata("authorization", format!("Bearer {}", token))
            .build()
            .unwrap();

        let result = interceptor.call(request).await;
        assert!(result.is_ok());
    }

    #[tokio::test]
    async fn test_expired_token_rejected() {
        let secret = b"test-secret-key-256-bits-long!!!";
        let mut claims = test_claims();
        claims.exp = chrono::Utc::now().timestamp() as usize - 3600;
        let token = create_test_token(&claims, secret);

        let interceptor = JwtInterceptor::new(secret);
        let request = Request::builder()
            .metadata("authorization", format!("Bearer {}", token))
            .build()
            .unwrap();

        let result = interceptor.call(request).await;
        assert!(result.is_err());
    }

    #[tokio::test]
    async fn test_permission_guard_allows_sufficient_permissions() {
        let claims = test_claims();
        let guard = RoleGuard::one_of(&["user", "moderator", "admin"]);

        assert!(guard.check(&claims));
    }

    #[tokio::test]
    async fn test_permission_guard_denies_insufficient_permissions() {
        let mut claims = test_claims();
        claims.roles = vec!["guest".to_string()];

        let guard = RoleGuard::one_of(&["admin"]);

        assert!(!guard.check(&claims));
    }

    #[tokio::test]
    async fn test_tenant_isolation_rejects_cross_tenant_access() {
        let request = Request::builder()
            .extension(TenantContext::new("tenant-abc".to_string(), "user-123".to_string()))
            .build()
            .unwrap();

        let result = validate_tenant_access(&request, "tenant-xyz");
        assert!(result.is_err());
        assert_eq!(result.unwrap_err().code(), tonic::Code::PermissionDenied);
    }

    #[tokio::test]
    async fn test_token_refresh_with_rotation() {
        let token_store = Arc::new(RefreshTokenStore::new());
        let token_service = TokenService::new(
            b"test-secret-key-256-bits-long!!!".to_vec(),
            900,
            604800,
            token_store.clone(),
        );

        let tokens = token_service
            .generate_token_pair("user-1", &["user"], &HashSet::new(), "tenant-1")
            .await
            .unwrap();

        assert!(token_store.is_token_known("new-jti").await);

        let new_tokens = token_service.refresh_tokens(&tokens.refresh_token).await.unwrap();
        assert_ne!(tokens.refresh_token, new_tokens.refresh_token);
    }

    #[tokio::test]
    async fn test_refresh_token_reuse_detected() {
        let token_store = Arc::new(RefreshTokenStore::new());
        let token_service = TokenService::new(
            b"test-secret-key-256-bits-long!!!".to_vec(),
            900,
            604800,
            token_store.clone(),
        );

        let tokens = token_service
            .generate_token_pair("user-1", &["user"], &HashSet::new(), "tenant-1")
            .await
            .unwrap();

        let _first_refresh = token_service.refresh_tokens(&tokens.refresh_token).await.unwrap();
        let second_refresh = token_service.refresh_tokens(&tokens.refresh_token).await;

        assert!(second_refresh.is_err());
    }
}
```

---

## Summary Checklist

| Component | Location | Key Points |
|-----------|----------|------------|
| JWT Claims | `auth/claims.rs` | `sub`, `exp`, `iat`, `jti`, `roles`, `permissions`, `tenant_id` |
| Tonic Interceptor | `auth/interceptor.rs` | Bearer token extraction, `ClaimsContext` injection |
| Permission Guard | `auth/guard.rs` | `RoleGuard`, `PermissionGuard` trait, method-level checks |
| Tenant Isolation | `auth/tenant.rs` | `TenantContext`, `validate_tenant_access()` |
| Token Refresh | `auth/service.rs` | Rotation, reuse detection, sliding window |
| grpc-web Interceptor | `client/auth.interceptor.ts` | Automatic refresh, httpOnly cookie handling |
| HTTP Cookie Handler | `server/routes.ts` | Set/clear cookies, CORS configuration |
| RBAC Middleware Chain | `server/rbac.layer.rs` | Layer composition for full auth stack |

---

## Security Considerations

1. **Token Storage**: Access tokens in memory/localStorage; refresh tokens in httpOnly cookies only
2. **Token Rotation**: Each refresh issues new refresh token, invalidates old one
3. **Reuse Detection**: Refresh token reuse triggers family revocation
4. **Tenant Isolation**: Validate `tenant_id` on every request
5. **Short Access TTL**: Access tokens expire in 15 minutes; refresh tokens in 7 days
6. **Secure Cookies**: `Secure`, `HttpOnly`, `SameSite=Strict`
7. **Algorithm**: Always use `HS256` with strong secrets (256+ bits) or `RS256` for asymmetric
