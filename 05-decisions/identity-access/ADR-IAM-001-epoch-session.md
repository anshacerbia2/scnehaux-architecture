---
doc_meta:
  id: ADR-IAM-001
  title: ADR-IAM-001 Epoch-Based Session Management
  adr_type: foundational
  status: accepted
  created: 2026-05-01
  created_by: Enterprise Architect
---

# ADR-IAM-001: Adopting Session Epochs for Low-Latency, O(1) Distributed Global Session Revocation

---

## 1. Title

Adopting Session Epochs for Low-Latency, O(1) Distributed Global Session Revocation

## 2. Status

| Date       | Status   | ADR Type     | Reviewers                 | Approver             |
| ---------- | -------- | ------------ | ------------------------- | -------------------- |
| 2026-05-01 | accepted | foundational | Architecture Review Board | Enterprise Architect |

## 3. Context

As Scnehaux scales to support multiple high-throughput distributed microservices, the ability to instantly invalidate sessions (during critical events like password changes, user suspensions, or tenant locks) is a non-negotiable security requirement. Traditional session revocation requires searching and deleting individual session records or JTIs from a persistent database or cache, which is an O(N) database-intensive operation that introduces latency and eventual consistency security risks.

Furthermore, long-lived sessions require Refresh Tokens. Standard static refresh tokens are vulnerable to replay attacks if compromised. To secure them, **Refresh Token Rotation (RTR)** must be used. However, standard RTR (which revokes a token family instantly when an old token is reused) introduces a severe operational vulnerability: on flaky mobile networks, automatic client retries can cause legitimate older tokens to be re-sent, triggering false theft detections and logging out innocent users.

## 4. Decision Drivers

By combining Session Epochs with RTR Grace Periods, we balance ironclad security with resilient user experiences:

- **Constant-Time O(1) Revocation:** Moving session validation to a Redis-cached epoch check achieves sub-millisecond validation latency.
- **Flaky-Network Resilience:** The 10-second grace period guarantees that legitimate automatic retries from cellular clients entering tunnels or switching towers do not trigger spurious, annoying logouts.
- **Fail-Secure Theft Mitigation:** Replays outside the 10-second window are blocked, keeping the token family secure while preventing malicious long-term session hijackings.

## 5. Decision

We officially adopt **Session Epochs** and **Refresh Token Rotation (RTR) with a Cryptographic Grace Period** as the primary enterprise mechanisms for low-latency global session invalidation and secure, resilient token rotation.

### 4.1 Session Epochs for O(1) Global Revocation

Every user account in the identity database carries a monotonic integer field named `session_epoch`. When a JWT is issued, the current `epoch` value is injected directly into the token's claims (`"epc"`).

Authentication middlewares compare the token's `"epc"` claim with the account's active `session_epoch` cached in Redis. If `token.epc < cached.epoch`, the token is instantly rejected. Globally revoking all active sessions for a user or tenant is achieved by incrementing the `session_epoch` counter.

### 4.2 Refresh Token Rotation (RTR) with Cryptographic Grace Period

Upon each refresh request:

1. The server invalidates the old Refresh Token JTI (`RT-1`), issues a new Refresh Token (`RT-2`), and updates the session's active JTI in Redis.
2. The old `RT-1` is recorded in a Redis-backed blacklist with a timestamp of rotation.
3. To mitigate mobile network dropped connection retries, we introduce a **10-second Cryptographic Rotation Grace Period**.
4. If a duplicate request using `RT-1` is received within 10 seconds of rotation, the server degrades gracefully: instead of triggering theft detection, it returns the _already generated_ `RT-2` and access token.
5. If `RT-1` is replayed _after_ the 10-second grace period has expired, it is classified as a critical **Theft Attempt**. The system immediately invalidates the entire session family, revokes all tokens, and flags the account for audit.

## 6. Consequences

### Positive

- **O(1) Execution**: Session invalidation is completed instantly with a single write (incrementing the epoch integer).
- **Sub-Millisecond Middleware Latency**: Middleware checks are lightweight memory comparisons in Redis rather than complex DB table lookups.
- **Fail-Secure Architecture**: Suspending an account instantly blocks all active tokens across all services.
- **Seamless User Experience**: Eliminates false-positive logout events under poor cell reception.

### Negative

- **Cache Dependency**: Middleware depends on Redis for fast epoch and rotation blacklist checks.
- **10-Second Vulnerability Window**: If an attacker steals `RT-1` and replays it in less than 10 seconds, they can acquire a valid token before the system blocks the family. This is an acceptable trade-off given the extreme rarity of active MITM attacks within a 10-second window compared to the daily frequency of mobile network drops.

### Tradeoffs

- We trade a minute 10-second security exposure during rotation for massive mobile client reliability and reduced API error rates.

### Operational Impact

- The `session_epoch` field in PostgreSQL is updated atomically during events (password reset, account suspension).
- Redis holds a direct, lightweight key-value mapping (e.g., `user:usr_123:epoch` -> `1`).
- Used refresh tokens are blacklisted in Redis with a TTL of `24 hours` matching the maximum refresh token skew, avoiding memory accumulation.

### Security Impact

- Enforces an immediate, fail-closed security posture during account compromises while keeping the perimeter resilient.

### Scalability Impact

- Storing single integers in Redis allows the system to easily support millions of active sessions with zero memory exhaustion.

### Operational

- Applied in the `scnehaux-iam` AuthN middleware.
- Standard claims format:
  ```json
  {
    "sub": "usr_9921a",
    "tid": "ten_1028b",
    "x_scnx_ent": ["iam.tenant.write"],
    "epc": 3,
    "exp": 1779998822
  }
  ```

## 7. Compliance Impact

### Related Standards

- [Technology Architecture Strategy (EAD-004)](../../01-enterprise/EAD-004-technology-architecture.md)
- [Scnehaux IAM System Architecture Document (SAD-001)](../../04-system/scnehaux-iam/scnehaux-iam.sad.md)

### Compliance Status

Compliant.

### Required Waivers

None.

## 8. Alternatives Considered

### Alternative A: Database Loop Revocation (Scanning and Deleting JTIs)

- **Pros**: Standard and mature SQL.
- **Cons**: O(N) execution time. In distributed environments, deleting thousands of active records introduces locks, connection pool exhaustion, and high database write loads during emergency mass logouts.
- **Why Rejected**: Unviable due to slow response times and high performance penalties.

### Alternative B: Zero-Grace Period Refresh Token Rotation

- **Pros**: Hardest security boundary; instant revocation on any reuse.
- **Cons**: Extremely high rate of false-positive session terminations on mobile clients due to network package retries.
- **Why Rejected**: Severely damages UX and increases customer support tickets for random logouts.
