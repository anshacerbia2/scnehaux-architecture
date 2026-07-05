---
doc_meta:
  id: STD-UIP-PRM-001
  title: Enterprise UI Platform Primitive Components Standard
  owner: Principal Frontend Architect
  version: 1.0.0
  status: adopted
  classification: restricted
  review_cycle_days: 180
  last_reviewed: 2026-05-21
---

# Enterprise UI Platform Primitive Components Standard (STD-UIP-PRM-001)

---

## 1. Objective & Scope

This standard defines the mandatory design patterns, accessibility integrations, polymorphic rendering slots, and property contracts for all reusable primitive UI components developed within the Scnehaux enterprise design system.

It guarantees that core UI primitives are highly accessible, performant, structurally isolated, and customizable across different product layouts.

---

## 2. Design Principles

The primitive component library is built on four core principles to ensure accessibility, behavioral predictability, and performance:

1. **Semantic and Native Structure First**: Components utilize standard semantic HTML elements rather than generic tags, ensuring native compatibility with screen readers and browsers.
2. **Complete Behavioral Encapsulation**: Interactive behaviors and keyboard interactions are governed by internal, deterministic state machines, decoupling logic from style and DOM markup.
3. **Ref & Composition Transparency**: Polymorphic components forward references and merge HTML attributes transparently to preserve runtime node access.
4. **Property Contract Boundaries**: Primitive components strictly receive leaf value properties rather than complex domain objects to avoid parent ref dependency and rendering thrashing.

## 3. Normative Rules

### Headless & Layout Primitive Architecture

Primitives are organized into Layout Primitives (styling and geometry skeletal structure) and Interactive Primitives (stateful accessible widgets).

#### Layout Primitives

- **Zero-Dependency Mandate**: Core layout and presentation elements (such as `Box`, `Flex`, `Grid`, `Text`, `Slot`) must be custom-built with zero external dependencies to ensure absolute bundle size optimization and styling purity.

#### Interactive Primitives (100% In-House Engine)

- **Bespoke Headless Wrappers**: Stateful interactive components (such as `Dialog`, `Dropdown`, `Popover`, `Select`, `Combobox`) MUST be built completely from scratch using our own internal state machines and focus management systems. We strictly prohibit the use of third-party headless libraries (including Radix UI or Headless UI). Our internal engines are solely responsible for fully implementing the W3C WAI-ARIA Authoring Practices (APG) standard, guaranteeing WCAG 2.2 AA accessibility compliance deterministically without relying on black-box dependencies.

#### Visual Segregation

- **Styling Agnosticism**: Primitive logic must remain 100% styling-agnostic. No design tokens, class names, or CSS properties should be hardcoded inside the primitive core. Styling configurations are delegated entirely to the design system wrapper.

---

### Primitive Component Concerns (Separation of Concerns)

To maintain a deterministic, performance-optimized, and highly decoupled architecture, all primitive components must partition their implementations into three isolated concerns: **State Machine (Behavior/Logic Engine)**, **Data Contract (Exposed DOM Contract)**, and **Polymorphism Strategy**.

Any styling configuration (such as component variants, sizes, and recipes) is strictly prohibited within the primitive layer and must be delegated entirely to the downstream Design System (DS) styled wrapper.

#### Behavior & Logic Engine Concern (State Machine)

- **Deterministic State Transition**: Interactive primitives must manage their behavior using Finite State Machines (FSM) or highly encapsulated state engines. Components must not maintain ad-hoc, uncontrolled states that can lead to race conditions or invalid states (e.g., a component being simultaneously `loading` and `disabled`).
- **Input & Event Orchestration**: The logic engine must process keyboard inputs, focus cycles, and gesture events, returning pure state descriptors and handler hooks to the rendering layer.

#### Data Contract Concern (Exposed DOM Contract)

The primitive component must declare an explicit, stable interface to the DOM. The DOM contract is divided into:

- **Component Anatomy (`data-part` & `data-scope`)**: Primitives must segment their layout into defined anatomical parts. Each element in the component's DOM tree must expose its identity:
  - `data-scope="[component]"` (e.g., `data-scope="dialog"`)
  - `data-part="[part-name]"` (e.g., `data-part="trigger"`, `data-part="content"`, `data-part="close"`)
- **Generic Child Slots (`data-slot`)**: For elements passed dynamically by the consumer or standard generic sub-components (such as icons, avatars, labels), components must expose or require a generic `data-slot` attribute (e.g., `data-slot="icon"`, `data-slot="avatar"`, `data-slot="label"`). This allows global theme packages and layout selectors to style children uniformly without coupling to tag names or custom component wrappers.
- **Interactive State Attributes (`data-[state]`)**: Dynamic visual states must be rendered as raw, Boolean or enum data attributes (e.g., `data-state="open|closed"`, `data-active="true|false"`, `data-disabled="true|false"`). Styling sheets must bind exclusively to these attributes.
- **Accessibility Contract (`aria-*`)**: Interactive elements must compile and apply designated `aria-*` and `role` attributes based on the WAI-ARIA specification, bound directly to the active state machine.

#### Polymorphism & Rendering Strategy (Tag `as` vs. `Slot`)

Primitives must allow custom rendering nodes without sacrificing performance:

- **Primary Option: Tag Selection (`as` Prop)**: By default, components must utilize tag-name selection via an `as` prop (e.g., `as="span"`, `as="a"`). This is the highest-performance path because it renders the dynamic tag directly with zero virtual DOM node manipulation.
- **Secondary Option: Component Composition (`Slot` / `asChild`)**: The custom Scnehaux `asChild` composition pattern using our native custom Slot engine is reserved as a secondary option. Because the custom `Slot` utility performs runtime element cloning and prop merging (`React.cloneElement`), it is prohibited in high-frequency rendering pipelines (such as virtualized list elements, grid cells, active motion animations) to prevent garbage collection spikes and CPU thrashing.

#### Styled Separation (Zero Recipes Rule)

- **Styling Agnosticism**: Primitives must remain 100% styling-agnostic. They must not import stylesheets, style engines (such as Tailwind or Panda CSS), or define design token recipes (such as sizes, color variants, or visual treatments).
- **Design System Responsibility**: All styling, visual recipes, and token variables must reside in the downstream styled components package (e.g. `@scnx/core-ui`) that wraps the primitive.

---

### Polymorphism & Slot API (asChild Pattern)

Polymorphic elements that allow downstream consumers to customize the DOM node must support the `asChild` composition pattern using Scnehaux's native custom Slot engine. Bypassing this engine or importing third-party slot packages (such as Radix UI's Slot) is prohibited.

#### Standard Polymorphic Contract

The polymorphic composition system must enforce a uniform property and reference contract:

- **Ref Transparency**: The custom Slot engine must forward and compose refs transparently, ensuring that parent and child refs are chained without memory leaks or unnecessary re-renders. Under React 19, `ref` must be processed as a standard property.
- **Intelligent Attribute Merging**: The Slot engine must perform a shallow merge of properties (`className`, inline `style`) and chain event execution sequences (executing both parent and child handlers).
- **TypeScript Contract Safety**: Components supporting polymorphism must expose an `asChild` contract using generic type helpers that omit overlapping native HTML attributes to prevent compiler bailouts.
- **Reference Implementation**: For concrete code blueprints, type definitions (e.g. `SlotProps`), and integration examples, developers must refer to the local repository technical standards and decision records.

#### Performance Constraints

- **Low-Frequency Layouts**: The use of `asChild` is permitted in static areas or low-frequency rendering contexts (such as card layouts, main layout headers).
- **High-Frequency Execution**: The `asChild` pattern is prohibited in high-frequency rendering environments (such as active animations, drag-and-drop loops, dynamic list virtualizers). Under these performance-sensitive contexts, components must use dynamic `as` prop tags (e.g. `const Comp = as || 'div'; return <Comp />`) to bypass children array cloning overhead.

---

### Property Contracts

To guarantee component boundary isolation and maintain clean API design:

- **UI Primitives (Leaf Props)**: Generic UI primitives (such as Buttons, Inputs, Badges, Tooltips) must accept only leaf primitive values (such as `label`, `isDisabled`, `onClick`) as props. Passing complex domain objects as props to generic UI primitives is prohibited.
- **Rationale**:
  - **Re-render Isolation**: Restricting props to leaf primitives isolates the component from parent object reference changes, preventing unnecessary rendering cycles in legacy/bailout compilation states.
  - **Testing Simplification**: Restricting props streamlines unit testing by eliminating the need to construct complex mock domain objects.

---

### Accessibility Integration

- **Semantic HTML First**: Primitives must render native semantic HTML tags (`<button>`, `<a>`, `<nav>`, `<input>`) instead of styling generic tags (`<div>`, `<span>`) with custom ARIA attributes.
- **Focus Management**: Overlay structures (Dialogs, Drawers, Modals) must trap focus internally during activation and restore focus to the trigger element upon closure.
- **Keyboard Navigation**: Components must implement the keyboard navigation specifications declared in the WAI-ARIA Authoring Practices Guide (APG).

---

## 4. Exceptions

None. All primitive component architecture rules apply unconditionally. Deviations require formal architectural exception approval through the enterprise governance review process.

## 5. Enforcement Mechanism

- **Accessibility Audits**: Build pipelines must execute static accessibility testing (e.g. `eslint-plugin-jsx-a11y`) to block accessibility violations.
- **Waiver Protocol**: Custom polymorphic patterns or non-headless interactive widgets require a documented project ADR and approval by the Architecture Review Board. The Board must respond with a review decision within **5 business days** of the ADR submission.

