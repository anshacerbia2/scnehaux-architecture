---
doc_meta:
  id: STD-UIP-TKN-002
  title: Enterprise Design Token Governance
  owner: Enterprise Architect
  version: 2.0.0
  status: proposed
  classification: public
  review_cycle_days: 180
  created_date: 2026-01-01
  last_reviewed: 2026-09-28
---

# STD-UIP-TKN-002: Enterprise Design Token Governance

> **Pre-production review draft.** Major rule changes require approval of ADR-UIP-PLT-001 before this revision becomes authoritative.

## 1. Objective & Scope

This standard defines token consumption across web and other UI platforms while preserving semantic intent. A platform may represent the contract differently in CSS, native code, or design tooling. The logical core → semantic → component hierarchy does not prescribe a package count.

## 2. Design Principles

Shared visual decisions use semantic names so a theme can change a value without changing its meaning. Token names alone do not guarantee contrast, layout stability, or cross-platform equivalence; each output must be verified in its consumer context.

## 3. Normative Rules

### 3.1 Consumption boundary

Shared components and product styling MUST use Tier-2 semantic tokens for governed color, typography, spacing, radius, shadow, and motion decisions. Tier-1 values are implementation inputs, not a public shortcut. Context-specific numerical values, intrinsic sizing, and values without a meaningful shared semantic role MAY be used when documented and reviewed; an absolute ban on every raw dimension would prevent ordinary responsive layout.

### 3.2 Semantic use

Consumers MUST choose tokens by intended role and state. A new domain business state MAY map to an existing semantic role. Where no role fits, teams propose a new token or keep the mapping product-local; they MUST NOT silently redefine a global token meaning.

### 3.3 Component aliases

Tier-3 aliases are justified by independent component semantics, not by an arbitrary numeric quota. The proposal records the alias purpose, Tier-2 fallback, theme/state matrix, and migration cost. Duplicate aliases or aliases used only to evade governance are rejected.

### 3.4 Themes and outputs

Every supported theme MUST define or inherit all public semantic variables it uses. Token aliases MUST resolve in the emitted artifact and supported browser scenarios, including alpha colors, shadows, and fonts. A theme MAY be partial only when its inheritance and scope are explicit. Color conformance is measured on actual foreground/background pairs and states.

### 3.5 Cross-platform contract

Cross-platform mappings preserve semantic intent and document platform-specific differences. A common name does not imply pixel identity across web, iOS, and Android.

## 4. Exceptions

An exception records the consumer, reason, owner, affected token, expected duration, and migration path under the applicable governance process. A request to add aliases is reviewed on its merits; it does not automatically mean the component is flawed.

## 5. Enforcement Mechanism

Source analysis checks prohibited direct Tier-1 consumption and raw values in governed shared styles. Packed-package checks validate emitted variables, supported theme inheritance, browser computed values, and visual/accessibility scenarios. These are target gates until implemented and running in CI; this standard does not claim that the extracted baseline already enforces them.
