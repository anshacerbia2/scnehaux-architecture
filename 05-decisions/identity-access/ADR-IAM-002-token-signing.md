---
doc_meta:
  id: ADR-IAM-002
  title: ADR-IAM-002 Token Signing Algorithm and Key Lifecycle Management
  adr_type: foundational
  status: accepted
  created: 2026-01-01
  created_date: 2026-01-01
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
| 2026-08-18 | accepted | foundational | Architecture Review Board | Enterprise Architect |

**Amended 2026-08-18: the algorithm profile in §4.1 is replaced by a single `PS256`
baseline.** The four-state key lifecycle in §4.2 and the storage duality in §4.3 are
unchanged and remain the operative decision. The replacement and its reasoning are in
§4.1; `STD-IAM-002 §3.2.2` is the operative profile.

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

### 4.1 Signing Algorithm: a Single `PS256` Baseline

**Amended 2026-08-18.** The original algorithmic duality — `ES256` internal, `RS256` external, dual-algorithm JWKS — is replaced by one baseline:

1.  **Every audience class**: tokens are signed with **`PS256`** (RSASSA-PSS with SHA-256), with an RSA modulus of at least **3072 bits**.
2.  **Single-algorithm JWKS**: the enterprise JWKS endpoint advertises active and retiring `PS256` keys only.
3.  **`RS256` by exception**: permitted for an `external` registration whose relying party cannot verify `PS256`, and only with a named accountable owner, a recorded reason, and an expiry date. `ES256` is not adopted.

Three findings drove the replacement, and each contradicts a premise of the original.

**`RS256` is prohibited by the profile we are aligning to.** The Financial-grade API profile — the most rigorously reviewed OAuth security profile in production, and the one open banking is audited against — permits `PS256` and `ES256` and forbids `RS256`. PKCS#1 v1.5 signature padding, which `RS256` uses, carries no security proof; PSS does. The original decision made `RS256` the external default on interoperability grounds, which selected the one algorithm the reference profile rejects.

**The bandwidth premise does not hold in this estate.** The original argued that `ES256` saves 30–40% of header size across billions of internal requests. `EAD-006 §5.4` establishes that service-to-service calls inside the runtime are authenticated by mutual TLS with workload identity, not by a bearer token. Internal tokens are presented at the edge and to protected resources, not on every internal hop, so the volume the saving was computed against is not there.

**A second algorithm is a second attack surface, and the original said so.** Its own Consequences list names "Downstream Parsing Complexity" and "Double Key Management" as costs. Algorithm confusion — a verifier selecting the algorithm from the token rather than from its own configuration — is an exploited defect class, and it lives in exactly the branch a dual profile requires every verifier to carry. One algorithm removes the branch, halves key custody, and leaves nothing for a verifier to select.

The operative profile is `STD-IAM-002 §3.2.2`, which fixes the allowlist and the exception form. `none` and every symmetric algorithm remain prohibited, and a verifier determines the expected algorithm from its own configuration rather than from the token.

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
- [ADR-IAM-001 (Adopt the Keycloak Identity Kernel)](ADR-IAM-001-keycloak-identity-kernel.md) - The kernel holds the signing keys this lifecycle governs.

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

### Alternative C: Retain the ES256 and RS256 Duality

_Evaluated at the 2026-08-18 amendment._

- **Pros**: the compact-token argument for internal traffic, and `RS256` acceptance by every relying party without an exception record.
- **Cons**: `RS256` is prohibited by the Financial-grade API profile, so the external half selects the one algorithm the reference profile rejects. Two algorithms require two key lifecycles, two rotation schedules, and an algorithm branch in every verifier, which is where algorithm confusion lives. The bandwidth saving is computed against a request volume that mutual TLS under `EAD-006 §5.4` means does not exist.
- **Why Rejected**: it pays a real cost in key custody and verifier surface for a saving the architecture does not realise, while mandating a padding scheme that carries no security proof.

### Alternative D: EdDSA (Ed25519) as the Baseline

_Evaluated at the 2026-08-18 amendment._

- **Pros**: the strongest modern signature choice — compact, fast, deterministic, and free of the nonce-reuse failure mode that makes ECDSA implementations fragile.
- **Cons**: relying-party and gateway support across the OIDC ecosystem remains materially thinner than for RSA, and an external B2B party unable to verify it has no fallback inside a single-algorithm profile.
- **Why Rejected**: the better choice cryptographically and the wrong one for a profile that must also serve external federation. Revisit when relying-party support is no longer the limiting factor.

---
