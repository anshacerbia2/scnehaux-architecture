---
doc_meta:
  id: STD-IAM-001
  title: Enterprise Identity Security Standard
  owner: Enterprise Security Architect
  version: 1.0.0
  status: approved
  classification: restricted
  review_cycle_days: 180
  last_reviewed: 2026-05-18
---

# Enterprise Identity Security Standard (STD-IAM-001)

---

## 1. Objective & Scope

This standard defines the mandatory cryptographic algorithms, token lifecycles, and tenant isolation policies for any system handling authentication, authorization, or user secrets within the Scnehaux enterprise. It aligns with SOC 2 Type II, ISO 27001, and OWASP ASVS v4.0.3 standards.

## 2. Hardened Security Standards

### 2.1 Cryptographic Credential Hashing
- **Algorithm**: **Argon2id** strictly. Legacy hashing algorithms (bcrypt, PBKDF2, MD5) are prohibited for passwords and API secrets.
- **Salt Complexity**: Must be salted with at least `16 bytes` of cryptographically secure random entropy (`crypto/rand`).
- **Configuration Parameters**:
  - `Memory = 64MB`
  - `Iterations = 3`
  - `Parallelism = 4`
- **CPU Starvation Prevention (Weighted Semaphore Concurrency Isolation)**: Hashing is computationally expensive. To prevent CPU starvation Denial of Service (DoS) attacks, global Argon2id hashing operations must be governed by a Process-Level Weighted Semaphore capped strictly at `Runtime.NumCPU() - 1` (**ADR-E007**). In addition:
  - *Fast-Shedding Backpressure*: If all semaphore slots are occupied, incoming hashing requests must be rejected immediately at the boundary with an HTTP 429 status code to protect host scheduler responsiveness.
  - *Active Cancellation*: Hashing execution must actively monitor context cancellation (`ctx.Done()`) to immediately abort computationally heavy hashing operations if the client terminates the connection mid-flight.
- **Output Storage**: Plaintext credentials must never be stored at rest or written to logs. Only Argon2id hashes are permitted.

### 2.2 JWT Token Lifecycle & Rotation
- **Access Tokens (JWT)**: Short-lived with a maximum Time-To-Live (TTL) of `15 minutes`. Enforces **Algorithmic Duality** based on the client channel boundary (**ADR-E006**):
  - *Internal & Mobile Channels*: Signed with `ES256` (ECDSA P-256) to minimize header overhead and gateway processing latency.
  - *External Federation & B2B Channels*: Signed with `RS256` (RSA 2048-bit) to ensure universal compatibility with standard enterprise OIDC clients.
- **Refresh Tokens**: Maximum TTL of `30 days`. 
- **Refresh Token Rotation (RTR)**: Mandated on all sessions. Upon refreshing, the token family's rotation state is updated in Redis, invalidating the old token JTI and issuing a new one.
- **Cryptographic Rotation Grace Period**: To eliminate false-positive session terminations on mobile clients due to network package retries, a **10-second Grace Period** is mandated on rotated refresh tokens. Duplicate requests using the recently rotated refresh token within this 10-second window must return the already generated token pair. Replays outside the 10-second window must trigger instant, automatic revocation of the entire session token family.

### 2.3 Cryptographic Key Sovereignty
- **Root-of-Trust Isolation**: The master private signing keys must reside securely in an external Key Management Service (KMS / AWS KMS / Vault Transit) in staging and production environments. A secure ephemeral memory fallback signer is permitted solely in local development (DX) environments.
- **High-Performance Paved Road (KMS Envelope Encryption)**: To prevent synchronous network API latency bottlenecks (`15-50ms` per signature) and KMS API rate limit exhaustion on the critical authentication path, systems must utilize **Envelope Encryption** for persistent token keys (**ADR-E006**). The application loads versioned private signing keys from the persistent KMS *only* at startup or key rotation. The decrypted signing key references are cached strictly within the application's secure RAM memory context to perform local, sub-1ms cryptographic signing.
- **Continuous Trust Key Rotation**: The cryptographic signing key lifecycle must implement a deterministic four-state transition machine (**Active**, **Retiring**, **Retired**, **Purged**) utilizing unique version-anchored Key IDs (`kid`). The active signing key is rotated every `30 days`, with a `7-day` retirement phase where the JWKS endpoint continues to advertise the retiring key to verify older outstanding tokens without session disruption.


### 2.4 Session Governance & Monotonic Epochs
To achieve instant, distributed global session invalidation without N-complexity lookup queries, all authentication systems must enforce **Session Epochs**:
- **Monotonic Counters**: Every user account maintains a `session_epoch` integer.
- **JWT Inject**: The active `session_epoch` is injected into the JWT claims payload upon token generation:
  ```json
  {
    "sub": "usr_99a82f",
    "tid": "ten_1028a",
    "x_scnx_ent": ["iam.tenant.write"],
    "epc": 3,
    "exp": 1779998822
  }
  ```
- **Validation**: Middleware must compare the token's epoch with the account's active cached epoch. If `token.epc < account.epoch`, the request is blocked.
- **Outage Resilience (L1 Cache Fallback)**: To prevent authentication failures during Redis outages, validation middleware must fall back to a local process-memory L1 cache containing recently revoked epochs (with a time-to-live of `300s`). JWT cryptographic signatures must continue to be verified, enabling degraded but operational verification instead of failing-closed or blocking authenticated traffic.

### 2.5 Monotonic Entitlements Propagation (PBAC)
- **Entitlements Snapshot**: User permissions (e.g., `iam.tenant.write`) are represented as namespaces and snapshot into the JWT as claims (e.g., `x_scnx_ent`) at token generation to prevent downstream database lookup latency.
- **Device Classification**: All authentication requests must parse and store device metrics (`mobile`, `desktop`, `tablet`, `bot`) to enable anomaly detection.

### 2.6 Immutable Hash-Chained Audit Ledger
Critical identity operations (login, registration, password resets, permission changes) must be appended to an immutable, cryptographically verifiable audit ledger:
- **Hashing**: Each record contains a `row_hash` (SHA256) of its contents.
- **Chaining**: Each record contains a `previous_hash` pointing to its predecessor, guaranteeing that any tampering or retro-active modification is immediately detectable.

### 2.7 Global Security Headers
All external HTTP interface layers must enforce the following secure headers:
- `X-Frame-Options: DENY`
- `X-Content-Type-Options: nosniff`
- `Content-Security-Policy`: Default-deny baseline (`default-src 'none'`).

---

## 3. Compliance & Enforcement

1.  **Static Application Security Testing (SAST)**: Automated scanners run in the build pipeline to prevent the injection of weak random generators (only `crypto/rand` is permitted).
2.  **Timing Attack Protection**: Custom signature validation algorithms must utilize constant-time comparison methods.
3.  **Auditing**: Session revocation pipelines are audited against SOC 2 CC6.1 & CC6.3 requirements.
