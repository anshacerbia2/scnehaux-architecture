---
doc_meta:
  id: STD-GLB-001
  title: Enterprise API Design Standard
  owner: Architecture Review Board
  version: 1.1.0
  status: approved
  classification: public
  governed_by: [EAD-004]
  review_cycle_days: 365
  created_date: 2026-01-01
  last_updated: 2026-08-18
  last_reviewed: 2026-08-18
---

# STD-GLB-001: Enterprise API Design Standard

## Objective & Scope

This standard defines the mandatory design principles and HTTP protocol usage for all synchronous REST APIs within the Scnehaux enterprise to ensure a consistent developer experience and operational reliability.

## Design Principles

- REST APIs must be predictable, stateless, and deeply consistent across all domains.
- We prioritize developer experience and explicit contracts over clever optimization.

## Normative Rules

### API Contracts & Envelope

- APIs MUST use JSON over HTTP.
- Responses SHOULD NOT use custom envelopes for standard data (return direct arrays/objects) to minimize payload bloat.
- Error responses MUST conform to **RFC 9457 (Problem Details for HTTP APIs)**, which obsoletes RFC 7807.

  The two are wire-compatible: RFC 9457 keeps every member 7807 defined and adds the optional `errors` array for reporting several problems in one response. A conforming 7807 document is therefore a conforming 9457 document, so no existing implementation breaks. The citation is corrected because `EAD-004 §5.3` mandates 9457, and a standard naming the obsoleted RFC sends implementers to a document that no longer defines the registry.

### Versioning

- APIs MUST be versioned at the URL path level (e.g., `/api/v1/users`).
- Header-based versioning is PROHIBITED due to complexity in CDN caching and network edge routing.

### Pagination

- List endpoints returning unbounded data MUST be paginated.
- Cursor-based pagination (e.g., `?after=xyz&limit=100`) is MANDATORY for all core entities. Offset-based pagination (`?offset=100`) is strictly PROHIBITED for large datasets due to database scanning penalties.

### Security & Authentication

- All requests MUST be authenticated at the API Gateway using JWT via the `Authorization: Bearer <token>` header.
- Internal machine-to-machine calls MUST use mTLS or an internal service mesh token.

### Rate Limiting

All public-facing APIs MUST return standard rate-limit headers:

- `X-RateLimit-Limit`
- `X-RateLimit-Remaining`
- `X-RateLimit-Reset`

## Exceptions

Legacy systems currently running SOAP or XML are exempt until their scheduled sunset dates.

## Enforcement Mechanism

API schema validation via the API Gateway and CI/CD spectral linters.
