---
doc_meta:
  id: STD-UIP-TKN-002
  title: Enterprise Design Token Governance
  owner: Enterprise Architect
  version: 1.0.0
  status: adopted
  classification: public
---

# STD-UIP-TKN-002: Enterprise Design Token Governance

## 1. Objective & Scope
This standard establishes the non-negotiable strategic guardrails for design token consumption across all Scnehaux UI platforms (Web, iOS, Android). It acts as the **C2 Platform-Agnostic** authority to prevent semantic entropy and ensure absolute visual consistency across the enterprise.

## 2. Design Principles
The primary philosophy of the token governance is to strictly separate structural visual intent (semantic tokens) from raw rendering coordinates (primitive values). By enforcing consumption at the semantic layer, we guarantee interoperability and allow core values to mutate (e.g., during theme switches) without affecting product layout.

## 3. Normative Rules

### 3.1 The Zero-Bypass Mandate
Product teams across all platforms are strictly forbidden from hardcoding raw color values (HEX, RGB, HSL) or raw dimensional values into application layouts.
*   **Mandate**: All structural and visual styling MUST resolve through Tier-2 (Semantic) design tokens.

### 3.2 Semantic Usage Doctrine
The token matrix relies on four core Emphasis layers (`subtle`, `default`, `strong`, `contrast`).
*   **Mandate**: Tokens must be used for their intended architectural purpose. Misusing a high-prominence token (e.g., `contrast`) for a low-prominence background container is a direct violation.

### 3.3 Domain Semantic Layering
When a domain team encounters a unique business state (e.g., `fraud_detected`), they must not introduce new global token schemas.
*   **Mandate**: Portals must map their local business states to existing global semantic schemes.

### 3.4 Typography Density Families
Typography must be selected based on semantic reading context.
*   **Mandate**: Teams must utilize density groups (e.g., compact data grids vs. readable documentation) to ensure cross-platform typographic rhythm.

### 3.5 Tier-3 Alias Budgeting
To prevent the unrestricted explosion of component-level overrides (Tier-3 aliases), the Enterprise Architecture Board enforces a strict alias budget.
*   **Mandate**: Each core component is limited to a maximum of **5 custom Tier-3 aliases**.

## 4. Exceptions
Any request to exceed the Tier-3 alias budget implies a structural flaw in the component's design and requires a formal architectural exception approved through the enterprise governance review process. Teams needing more than 5 aliases must submit a refactor proposal or an exemption request documenting the structural justification.

## 5. Enforcement Mechanism
Each platform repository must implement automated static analysis to block raw literal styling and enforce alias limits at the CI/CD pipeline.
