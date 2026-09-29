---
doc_meta:
  id: STD-UIP-PRM-001
  title: Enterprise UI Platform Primitive Components Standard
  owner: Principal Frontend Architect
  version: 2.0.0
  status: approved
  classification: restricted
  governed_by: [PAD-PLT-003]
  authorized_by: [ADR-UIP-PLT-001]
  review_cycle_days: 180
  created_date: 2026-01-01
  last_reviewed: 2026-09-29
---

# Enterprise UI Platform Primitive Components Standard (STD-UIP-PRM-001)

> **Implementation boundary:** approval of this behavioral contract does not assert that the extracted implementation already conforms.

---

## 1. Objective & Scope

This standard defines the public behavior, accessibility, composition, and ownership contracts for reusable UI primitives. Release evidence, not the choice of an implementation library, establishes whether a primitive meets the contract.

---

## 2. Design Principles

The primitive component library is built on four core principles to ensure accessibility, behavioral predictability, and performance:

1. **Semantic and Native Structure First**: Components utilize standard semantic HTML elements rather than generic tags, ensuring native compatibility with screen readers and browsers.
2. **Behavioral Ownership**: A primitive owns its documented keyboard, focus, state, and ARIA behavior; native browser behavior is preferred when it satisfies the contract.
3. **Ref & Composition Transparency**: Polymorphic components forward references and merge HTML attributes transparently to preserve runtime node access.
4. **Property Contract Boundaries**: Primitive props describe reusable presentation and interaction, not product authorization or business decisions.

## 3. Normative Rules

### Headless & Layout Primitive Architecture

Primitives are organized into Layout Primitives (styling and geometry skeletal structure) and Interactive Primitives (stateful accessible widgets).

#### Layout Primitives

- Core layout and presentation elements (such as `Box`, `Flex`, `Grid`, `Text`, `Slot`) preserve small, semantic DOM contracts. An external dependency is evaluated on measured cost and provenance; zero dependencies does not automatically optimize a bundle.

#### Interactive Primitives

- Every composite widget MUST expose a documented behavior matrix for keyboard, focus, pointer, touch, disabled state, controlled/uncontrolled state, and assistive technology.
- Button, Disclosure/Accordion, Navigation, Sidebar, and layout primitives use native/custom behavior.
- Combobox, Select, Menu, Dialog, Popover, Listbox, and Tabs use selected React Aria hooks behind the `@scnx/core-ui` contract. Vendor types and APIs MUST NOT leak into public types or props. Stable promotion requires APG behavior, manual NVDA and VoiceOver checks, bundle evidence, internationalization, security, maintenance, and license/provenance review.
- Using a third-party foundation does not transfer responsibility for the integration's accessibility or the consuming page's WCAG conformance to that dependency.

#### Public polymorphism

- Interactive parts expose `asChild` only where composition is required. Typography and layout primitives MAY expose a closed `as` tag union. A component MUST NOT expose both. Remaining components keep a fixed semantic element.
- `asChild` promotion requires tested ref typing, handler order, semantic output, disabled behavior, router Link composition, single-child failure, and Slot provenance/license.
- Primitive logic remains styling-agnostic. Stable `data-*` state hooks MAY form part of its public behavior contract; visual tokens, classes, and CSS remain owned by the styled layer.

---

### Primitive Component Concerns (Separation of Concerns)

To maintain a deterministic, performance-optimized, and highly decoupled architecture, all primitive components must partition their implementations into three isolated concerns: **State Machine (Behavior/Logic Engine)**, **Data Contract (Exposed DOM Contract)**, and **Polymorphism Strategy**.

Any styling configuration (such as component variants, sizes, and recipes) is strictly prohibited within the primitive layer and must be delegated entirely to the downstream Design System (DS) styled wrapper.

#### Behavior & Logic Engine Concern (State Machine)

- **Deterministic State Transition**: Interactive primitives must define valid states and transitions. A finite state machine is one implementation option; the public contract and tests determine correctness.
- **Input & Event Orchestration**: The logic engine must process keyboard inputs, focus cycles, and gesture events, returning pure state descriptors and handler hooks to the rendering layer.

#### Data Contract Concern (Exposed DOM Contract)

The primitive component must declare an explicit, stable interface to the DOM. The DOM contract is divided into:

- **Component Anatomy (`data-part` & `data-scope`)**: Publicly styled parts expose stable identifiers where the styling contract needs them:
  - `data-scope="[component]"` (e.g., `data-scope="dialog"`)
  - `data-part="[part-name]"` (e.g., `data-part="trigger"`, `data-part="content"`, `data-part="close"`)
- **Generic Child Slots (`data-slot`)**: For elements passed dynamically by the consumer or standard generic sub-components (such as icons, avatars, labels), components must expose or require a generic `data-slot` attribute (e.g., `data-slot="icon"`, `data-slot="avatar"`, `data-slot="label"`). This allows global theme packages and layout selectors to style children uniformly without coupling to tag names or custom component wrappers.
- **Interactive State Attributes (`data-[state]`)**: Dynamic visual states must be rendered as raw, Boolean or enum data attributes (e.g., `data-state="open|closed"`, `data-active="true|false"`, `data-disabled="true|false"`). Styling sheets must bind exclusively to these attributes.
- **Accessibility Contract (`aria-*`)**: Interactive elements must compile and apply designated `aria-*` and `role` attributes based on the WAI-ARIA specification, bound directly to the active state machine.

#### Polymorphism & Rendering Strategy

Use the native element when it represents the action accurately. Interactive parts MAY expose `asChild` only at approved composition points. Typography and layout primitives MAY expose a closed `as` tag union. A component MUST NOT expose both. Each supported form preserves ref, event, accessible-name, disabled, and native semantic behavior.

#### Styled Separation (Zero Recipes Rule)

- **Styling Agnosticism**: Primitives carry no styling. They must not import stylesheets, style engines (such as Tailwind or Panda CSS), or define design token recipes (such as sizes, color variants, or visual treatments).
- **Design System Responsibility**: Styling, visual recipes, and token variables reside in `@scnx/system`, which may wrap `@scnx/core-ui` primitives.

---

### Polymorphism & Slot API

- A polymorphic implementation MUST preserve the native meaning of the rendered element. Links require a destination; actions use button semantics. An anchor with `role="button"` must implement the missing Space behavior or be replaced with a native button.
- Ref composition, merged-handler order, ARIA attributes, TypeScript props, semantic tags, and invalid multi-child behavior MUST be tested for every supported polymorphic form.
- Slot cloning and dynamic tag selection are evaluated on correctness and measured consumer cost. `Slot.tsx` MUST pass provenance and license review before an `asChild` API becomes stable. Similarity to another library is not proof of provenance; any derived code requires appropriate attribution.

---

### Property Contracts

To keep component boundaries isolated and APIs clean:

- **Public Props**: Shared primitives accept presentation and interaction inputs, not Product domain aggregates or authorization decisions. Complex values such as option collections are allowed when required by the widget contract; stability and rendering cost are measured rather than inferred from value shape alone.

---

### Accessibility Integration

- **Semantic HTML First**: A primitive renders the native element (`<button>`, `<a href>`, `<nav>`, `<input>`, `<dialog>`) whenever one provides the required semantics and behavior. A composite widget without a native equivalent (listbox, menu, tabs, tree, grid) follows its APG pattern, which assigns roles and states to generic elements. Generic elements with ARIA roles are prohibited only where a native element fits.
- **Focus Management**: A modal overlay (modal dialog, drawer, or alert dialog) contains focus while open and restores focus to its trigger, or to a documented fallback when the trigger no longer exists, on close. A non-modal overlay (popover, non-modal dialog, menu) does not trap focus: it follows its APG pattern for moving focus in, closing on Escape, and returning focus, and it leaves the rest of the page operable.
- **Focus Indicator**: Every focusable part shows a `:focus-visible` outline as defined in STD-GLB-FE-005 section 3.9. Shadows may enhance but never replace it.
- **Keyboard Navigation**: Components must implement the keyboard navigation specifications declared in the WAI-ARIA Authoring Practices Guide (APG).
- **Per-pattern matrix**: Required keys are defined per widget, not by counting `onKeyDown` occurrences or imposing one key list on all widgets.
- **Evidence**: Source tests cover behavior; packed-package consumers and manual assistive-technology checks cover integration. Results are recorded in a Component Accessibility Conformance Report using applicable WCAG 2.2 and APG criteria. The report is not a VPAT or complete-page certification.

---

## 4. Exceptions

An exception must document the affected public behavior and its impact on consumers. A widget that fails a required contract is excluded from stable exports until repaired or explicitly scoped as experimental.

## 5. Enforcement Mechanism

- **Behavior tests**: Unit and interaction tests execute the per-widget matrix, including native keyboard behavior, focus restoration, reduced motion, and controlled/uncontrolled state.
- **Consumer tests**: Packed-package tests verify public exports, ref behavior, DOM semantics, and supported SSR/RSC use.
- **Manual review**: Screen-reader and high-contrast results are recorded for each stable complex widget. Automated lint and axe checks cannot alone establish conformance.
