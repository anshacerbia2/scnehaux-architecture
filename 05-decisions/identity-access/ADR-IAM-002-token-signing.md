---
doc_meta:
  id: ADR-IAM-002
  title: ADR-IAM-002 Token Signing Algorithm and Key Lifecycle Management
  adr_type: foundational
  status: accepted
  created: 2026-05-01
  created_by: Enterprise Architect
---

# ADR-IAM-002: Establishing Algorithmic Duality and Continuous Key Lifecycle Management for Secure Token Issuance

---

## 1. Title

Establishing Algorithmic Duality and Continuous Key Lifecycle Management for Secure Token Issuance

## 2. Status

| Date       | Status   | ADR Type     | Reviewers                 | Approver             |
| ---------- | -------- | ------------ | ------------------------- | -------------------- |
| 2026-05-01 | accepted | foundational | Architecture Review Board | Enterprise Architect |

## 3. Context

The Scnehaux enterprise identity platform must issue cryptographically signed JSON Web Tokens (JWT) to represent authenticated identity across our distributed service landscape. In high-throughput microservice request chains, every byte of the HTTP header counts. Large tokens increase network latency and memory allocation. ECDSA (`ES256`) signatures are highly compact (64 bytes in IEEE P1363 format) and fast to generate compared to RSA (`RS256`) signatures with 2048/3072-bit keys.

However, in external B2B integrations, identity federation, and legacy environments, `RS256` remains the undisputed industry standard. Third-party clients often struggle to parse ECDSA signatures due to historical encoding mismatches (such as ASN.1 DER vs. IEEE P1363 raw concatenation). Furthermore, cryptographic signing keys must be rotated periodically for security compliance without disrupting active user sessions or causing developer friction (DX).

## 4. Decision Drivers

### Why Algorithmic Duality?

By selecting `ES256` for internal microservices, we shrink headers by 30-40%. Over billions of internal requests, this saves significant bandwidth and network card context-switch CPU overhead. However, refusing to support `RS256` for B2B federation violates standard operational interoperability. A dual-algorithm JWKS gives us the best of both worlds: modern, lightweight internal performance and robust, legacy-compatible public boundaries.

### Why a Verification Window?

When a key is rotated, any client holding a token signed by the old key will instantly experience authorization failures if the old public key is immediately dropped from the JWKS. By keeping the old key in a `Retiring` state for the maximum token lifespan, we achieve automated key transitions with zero downtime or false-positive security logouts.

---

## 5. Decision

We officially establish **Algorithmic Duality** and a **Four-State Key Lifecycle** as the standards for secure token signing, public key exposure, and trust continuity.

### 4.1 Algorithmic Duality (Context-Driven Signing)

Token signing is divided based on integration context:

1.  **Internal Ecosystem & Mobile Clients**: We standardize on **`ES256`** (ECDSA P-256) to optimize payload size, CPU signing speed, and edge bandwidth utilization.
2.  **Public OIDC & B2B Federation**: We standardize on **`RS256`** (RSA 2048-bit) to guarantee maximum interoperability and frictionless B2B onboarding.
3.  **Dual-Algorithm JWKS**: The enterprise JWKS endpoint (`/.well-known/jwks.json`) must dynamically advertise both active RSA and ECDSA public verification keys, mapped to distinct Key IDs (`kid`).

### 4.2 Four-State Key Lifecycle State Machine

To guarantee trust continuity during rotation, signing keys transition through a strict state machine:

1.  **`Active`**: The key is active. It is used to sign new tokens and verify existing tokens. Advertised in the public JWKS.
2.  **`Retiring`**: A new key has been promoted to `Active`. The retiring key is strictly prohibited from signing new tokens, but **remains advertised in the JWKS** to verify existing unexpired tokens. Keys remain in this state for the duration of the _Maximum Token TTL_ (e.g., 24 hours for refresh tokens).
3.  **`Retired`**: The verification window has expired. The key is removed from the active JWKS advertising list but cached in secure cold storage.
4.  **`Purged`**: The key is permanently deleted from all databases and secure memory boundaries.

### 4.3 Key Storage Duality (Ergonomics vs. Production Hardening)

- **Local Development (DX Fallback)**: The application boots using an ephemeral `software` signer that generates keys in-memory. This eliminates the need for complex local infrastructure setups (such as Vault or AWS KMS).
- **Staging & Production**: Keys are persisted in a centralized Key Management Service (AWS KMS or HashiCorp Vault Transit engine) or versioned encrypted datastores to prevent all active user sessions from being instantly invalidated upon container restarts.

---

## 6. Consequences

### Positive

- **Bandwidth Reduction**: Shrinks internal request tokens significantly.
- **Continuous Trust**: Rotating keys does not log out active users or cause API failures.
- **Excellent Developer Ergonomics**: Developers can spin up the full stack locally in under 5 seconds using the software fallback signer.

### Negative

- **Downstream Parsing Complexity**: Downstream verifiers must inspect the JWT header `"alg"` and `"kid"` claims to load the correct public key and verification algorithm dynamically.
- **Double Key Management**: Requires managing two concurrent active key pairs (ECDSA & RSA) in the KMS.

### Tradeoffs

- We trade minor complexity in the verifier library and key management for massive bandwidth savings, B2B compatibility, and automated key rotation.

---

### Operational

### Go Signature Transpilation (ASN.1 DER to IEEE P1363):

```go
// ASN.1 DER signature representation from Go standard crypto library
type ecdsaSignature struct {
    R, S *big.Int
}

// Convert DER to IEEE P1363 (standard 64-byte JWT format)
var parsedSig ecdsaSignature
asn1.Unmarshal(sigDER, &parsedSig)

rBytes := parsedSig.R.Bytes()
sBytes := parsedSig.S.Bytes()

sigBytes := make([]byte, 64)
copy(sigBytes[32-len(rBytes):32], rBytes)
copy(sigBytes[64-len(sBytes):64], sBytes)
```

---

## 7. Compliance Impact

### Related Standards

- [Identity Platform Domain Strategy (PAD-PLT-001)](../../03-domain/PAD-PLT-001-identity-platform/PAD-PLT-001-identity-platform.pad.md)
- [Scnehaux IAM System Architecture Document (SAD-001)](../../04-system/scnehaux-iam/scnehaux-iam.sad.md)
- [ADR-IAM-001 (Epoch Sessions)](ADR-IAM-001-epoch-session.md) - Relies on fast verification to bypass database hits.

### Compliance Status

Compliant.

### Required Waivers

None.

## 8. Alternatives Considered

### Alternative A: Absolute ES256-Only Enforcement

- **Pros**: Ultra-compact tokens, highly modern codebase.
- **Cons**: Breaks B2B integrations. Many enterprise federation platforms (e.g., legacy corporate Active Directory instances or older SaaS gateways) fail to process ECDSA keys.
- **Why Rejected**: Unviable for B2B interoperability and corporate integration speed.

### Alternative B: Ephemeral Keys in Production

- **Pros**: Zero database or storage requirements.
- **Cons**: Container restarts invalidate all active user refresh sessions, forcing hundreds of thousands of users to log out.
- **Why Rejected**: Completely unacceptable user experience and high operational instability.

---
