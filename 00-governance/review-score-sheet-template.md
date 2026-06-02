<!-- lint_disable: missing_metadata, missing_section -->
# Architecture Review Score Sheet

This score sheet is used by the Architecture Review Board (ARB) and Principal Engineers during the manual review phase of PAD, SAD, and strategic ADR documents.

It supplements the automated `linter.py` checks. While the linter ensures structural and policy-as-code compliance, this score sheet evaluates the qualitative engineering aspects.

## Document Meta
- **Document ID**: 
- **Reviewer**: 
- **Date**: 
- **Final Verdict**: [ ] APPROVED / [ ] REJECTED / [ ] REVISIONS REQUIRED

---

## 1. Zero Waste Execution & Determinism (Score: 0-5)
| Criteria | Description | Score | Notes |
| :--- | :--- | :--- | :--- |
| **No Implicit State** | The design avoids shadow state, hidden side-effects, or undocumented background processing. | | |
| **Clear Separation** | Boundaries between Domain Logic, I/O, and UI (if applicable) are clearly delineated with hard boundaries. | | |
| **Resource Efficiency** | Evidence of minimal waste (compute, memory, network calls). Avoids over-engineering. | | |

## 2. Observability & Error Handling (Score: 0-5)
| Criteria | Description | Score | Notes |
| :--- | :--- | :--- | :--- |
| **Traceability** | Distributed tracing and log correlation strategies are defined. | | |
| **Zero Silent Failure** | Error boundary handling is explicit. Failures are surfaced and routed correctly, never swallowed. | | |
| **Metrics** | Defines quantifiable SLIs (Service Level Indicators) aligned with the business capability. | | |

## 3. Resilience & Security Boundary (Score: 0-5)
| Criteria | Description | Score | Notes |
| :--- | :--- | :--- | :--- |
| **Load Shedding** | Mechanisms to shed excess load and fail gracefully are documented. | | |
| **Trust Boundaries** | Explicit network policies, mTLS usage, and Zero Trust validation at the component edge. | | |
| **Blast Radius** | Failure in one component does not cascade synchronously to other domains. | | |

## 4. Referential Integrity & Open-Closed Principle (Score: 0-5)
| Criteria | Description | Score | Notes |
| :--- | :--- | :--- | :--- |
| **Extensibility** | New features can be added via composition without modifying the core domain engine. | | |
| **Dependency Rule** | Direction of dependencies points inward toward the domain. Interfaces belong to the caller. | | |
| **Governance Alignment** | Explicitly adheres to existing standards or provides an approved ADR for deviations. | | |

---

## Summary and Action Items

**Key Strengths:**
- 

**Critical Risks / Violations:**
- 

**Required Revisions before Approval:**
1. 
2. 
