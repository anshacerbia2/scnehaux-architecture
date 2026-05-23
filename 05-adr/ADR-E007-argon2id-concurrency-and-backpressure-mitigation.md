---
doc_meta:
  id: ADR-E007
  title: ADR-E007 Argon2id CPU Concurrency and Backpressure Mitigation
  owner: Enterprise Architect
  version: 1.0.0
  status: approved
  classification: public
  review_cycle_days: 180
  last_reviewed: 2026-05-18
---

# ADR-E007: Argon2id CPU Concurrency and Backpressure Mitigation

---

## 1. Title
Enforcing Bounded Concurrency, Fast-Shedding Backpressure, and Throttling for Cryptographic Password Hashing

## 2. Status
Accepted

## 3. Context
The Scnehaux enterprise mandates **Argon2id** as the default cryptographic hashing algorithm for all user credentials to comply with OWASP and SOC 2 standards. Compliant Argon2id parameters are intentionally designed to be CPU-hard and memory-intensive (e.g., 64MB memory, 3 iterations, 4 parallelism) to prevent high-performance offline brute-force cracking using specialized GPU clusters.

However, this high computational cost introduces a severe runtime vulnerability: the login (`/api/v1/auth/login`) and registration (`/api/v1/auth/register`) endpoints become ideal targets for **CPU Exhaustion Denial of Service (DoS)** attacks. If multiple computationally expensive authentication requests are handled inline synchronously on incoming HTTP goroutines without bounds, an attacker can launch concurrent authentication requests to easily consume all CPU cores, starving other microservices and causing complete system unresponsiveness.

## 4. Decision
We officially mandate a **Layered Concurrency and Backpressure Throttling System** to protect the identity gateway from CPU starvation.

### 4.1 Bounded Concurrency via Weighted Semaphores
All Argon2id hashing operations (both creation and comparison) must execute strictly under the control of a global **Weighted Semaphore**. 
*   The maximum number of concurrent Argon2id operations running globally within a single application process is capped at **`Runtime.NumCPU() - 1`** (or a configured thread ceiling matching CPU allocation).
*   This guarantees that at least one CPU core remains fully available to handle health checks, logging, database connections, and standard HTTP requests even under maximum authentication stress.

### 4.2 Backpressure & Fast-Shedding (Fast-Fail 429)
If the weighted semaphore is fully saturated:
*   Incoming authentication requests must not build up indefinitely in memory.
*   The system must enforce **Fast-Shedding**. Requests that cannot acquire a semaphore slot within a strict timeout (e.g., 100ms) must be aborted immediately, returning an **HTTP 429 Too Many Requests** error to the client. This prevents heap exhaustion, database connection pool depletion, and out-of-memory (OOM) crashes.

### 4.3 Context-Driven Active Cancellation
*   The hashing engine must periodically inspect the request context state (`ctx.Done()`).
*   If the client disconnects, aborts the request, or the gateway timeout is reached, the ongoing Argon2id calculation must be cancelled immediately, reclaiming valuable CPU execution cycles.

### 4.4 Boundary Protection (Edge Rate Limiting)
We enforce a sliding-window rate limiter (IP-based and account-based) at the edge API gateway (or Redis-backed middleware layer) to intercept and drop brute-force attempts *before* they can reach the application-layer semaphore.

---

## 5. Rationale

### Why a Semaphore Over a Channel-Backed Worker Pool?
A standard Go channel-backed worker pool is effective for queuing, but it can lead to memory bloat if thousands of expensive requests accumulate in the queue waiting for a free worker thread. A weighted semaphore allows us to check thread occupancy instantly and apply **immediate backpressure**, shedding excess load before allocating memory for the password payload or starting goroutines.

### Why Concurrency Guarding is Vital:
Under peak traffic, a single server node with 8 CPU cores can only process approximately 40 concurrent Argon2id hashing operations per second before CPU utilization hits 100%. Without a concurrency guard, a minor botnet attack of 500 concurrent requests would completely freeze the operating system's scheduler. The semaphore ensures the system degrades gracefully, sacrificing a small fraction of authentication requests (returning 429) to keep the core server healthy.

---

## 6. Alternatives Considered

### Alternative A: Inline Synchronous Hashing (Vulnerable)
*   **Pros**: Minimal code overhead, no concurrency architecture to maintain.
*   **Cons**: Trivial DoS vulnerability. A few concurrent dummy requests can completely freeze the server.
*   **Why Rejected**: Unviable for any production environment requiring high availability.

### Alternative B: Queue Accumulation Without Shedding
*   **Pros**: No requests are rejected; all logins are eventually processed in order.
*   **Cons**: Leads to massive request queues, thread starvation, socket timeouts, and eventual out-of-memory crashes due to heap accumulation of pending HTTP requests.
*   **Why Rejected**: Damages UX and leads to hard server crashes.

---

## 7. Consequences

### Positive
- **CPU Starvation Defeated**: The identity gateway remains completely responsive and healthy under heavy authentication attacks.
- **Graceful Degradation**: Clear backpressure signals (HTTP 429) are returned to edge gateways under load.
- **Resource Recovery**: Instantly reclaims CPU cycles when users abort slow connections.

### Negative
- **Temporary Login Denials**: Legitimate users might receive an HTTP 429 error during massive traffic spikes if the authentication capacity is temporarily saturated.
- **Complex Thread Management**: Requires writing and maintaining non-blocking semaphore wrappers in the platform layer.

### Tradeoffs
- We trade a temporary rejection of excess login requests (HTTP 429) during peak starvation for absolute platform availability and system survival.

---

## 8. Risks
- **Semaphore Lock Leakage**: If a hashing operation panics or exits prematurely without releasing the semaphore slot, the capacity is permanently reduced, leading to eventual permanent denial of service.
  - *Mitigation*: The semaphore acquisition and release cycle must be wrapped in strict `defer` statements to guarantee release under all execution paths.

---

## 9. Implementation Notes

### Go Concurrency-Guarded Hasher Pattern:
```go
package security

import (
    "context"
    "errors"
    "golang.org/x/sync/semaphore"
)

type BoundedHasher struct {
    sem    *semaphore.Weighted
    hasher Hasher
}

func NewBoundedHasher(hasher Hasher, maxWorkers int64) *BoundedHasher {
    return &BoundedHasher{
        sem:    semaphore.NewWeighted(maxWorkers),
        hasher: hasher,
    }
}

func (h *BoundedHasher) Hash(ctx context.Context, password string) (string, error) {
    // Attempt to acquire execution slot with context timeout
    if err := h.sem.Acquire(ctx, 1); err != nil {
        return "", errors.New("platform/security: server authentication capacity fully saturated (HTTP 429)")
    }
    defer h.sem.Release(1)

    // Periodically verify context cancellation before and during calculations
    if err := ctx.Err(); err != nil {
        return "", err
    }

    return h.hasher.Hash(password)
}
```

---

## 10. Related Documents
- [Scnehaux IAM Software Architecture Document (SAD-001)](file:///d:/Ansha/architecture-description/scnehaux-architecture/03-applications/scnehaux-iam/scnehaux-iam.sad.md)
- [Enterprise Security Standard (STD-E003)](file:///d:/Ansha/architecture-description/scnehaux-architecture/05-standards/STD-E003-identity-security-standard.md)
