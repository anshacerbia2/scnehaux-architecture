---
doc_meta:
  id: STD-E015
  title: Enterprise UI Platform Primitive Components Standard
  owner: Principal Frontend Architect
  version: 1.0.0
  status: approved
  classification: restricted
  review_cycle_days: 180
  last_reviewed: 2026-05-21
---

# Enterprise UI Platform Primitive Components Standard (STD-E015)

---

## 1. Objective & Scope

This standard defines the mandatory design patterns, accessibility integrations, polymorphic rendering slots, and property contracts for all reusable primitive UI components developed within the Scnehaux enterprise design system.

It guarantees that core UI primitives are highly accessible, performant, structurally isolated, and customizable across different product layouts.

---

## 2. Headless & Layout Primitive Architecture

Primitives are organized into Layout Primitives (styling and geometry skeletal structure) and Interactive Primitives (stateful accessible widgets).

### 2.1 Layout Primitives (Zero External Dependencies)
- **Zero-Dependency Mandate**: Core layout and presentation elements (such as `Box`, `Flex`, `Grid`, `Text`, `Slot`) must be custom-built with zero external dependencies (no Radix UI or third-party libraries) to ensure absolute bundle size optimization and styling purity.

### 2.2 Interactive Primitives (Radix UI Integration)
- **Accessible Headless Wrappers**: Stateful interactive components (such as `Dialog`, `Dropdown`, `Popover`, `Select`, `Combobox`) must build upon Radix UI headless wrappers to leverage WCAG 2.2 AA accessibility compliance, keyboard focus traps, and screen reader behaviors without re-implementing complex browser interaction models.

### 2.3 Visual Segregation
- **Styling Agnosticism**: Primitive logic must remain 100% styling-agnostic. No design tokens, class names, or CSS properties should be hardcoded inside the primitive core. Styling configurations are delegated entirely to the design system wrapper.

---

## 3. Primitive Component Concerns (Separation of Concerns)

To maintain a deterministic, performance-optimized, and highly decoupled architecture, all primitive components must partition their implementations into three isolated concerns: **State Machine (Behavior/Logic Engine)**, **Data Contract (Exposed DOM Contract)**, and **Polymorphism Strategy**. 

Any styling configuration (such as component variants, sizes, and recipes) is strictly prohibited within the primitive layer and must be delegated entirely to the downstream Design System (DS) styled wrapper.

### 3.1 Behavior & Logic Engine Concern (State Machine)
- **Deterministic State Transition**: Interactive primitives must manage their behavior using Finite State Machines (FSM) or highly encapsulated state engines. Components must not maintain ad-hoc, uncontrolled states that can lead to race conditions or invalid states (e.g., a component being simultaneously `loading` and `disabled`).
- **Input & Event Orchestration**: The logic engine must process keyboard inputs, focus cycles, and gesture events, returning pure state descriptors and handler hooks to the rendering layer.

### 3.2 Data Contract Concern (Exposed DOM Contract)
The primitive component must declare an explicit, stable interface to the DOM. The DOM contract is divided into:
- **Component Anatomy (`data-part` & `data-scope`)**: Primitives must segment their layout into defined anatomical parts. Each element in the component's DOM tree must expose its identity:
  - `data-scope="[component]"` (e.g., `data-scope="dialog"`)
  - `data-part="[part-name]"` (e.g., `data-part="trigger"`, `data-part="content"`, `data-part="close"`)
- **Generic Child Slots (`data-slot`)**: For elements passed dynamically by the consumer or standard generic sub-components (such as icons, avatars, labels), components must expose or require a generic `data-slot` attribute (e.g., `data-slot="icon"`, `data-slot="avatar"`, `data-slot="label"`). This allows global theme packages and layout selectors to style children uniformly without coupling to tag names or custom component wrappers.
- **Interactive State Attributes (`data-[state]`)**: Dynamic visual states must be rendered as raw, Boolean or enum data attributes (e.g., `data-state="open|closed"`, `data-active="true|false"`, `data-disabled="true|false"`). Styling sheets must bind exclusively to these attributes.
- **Accessibility Contract (`aria-*`)**: Interactive elements must compile and apply designated `aria-*` and `role` attributes based on the WAI-ARIA specification, bound directly to the active state machine.

### 3.3 Polymorphism & Rendering Strategy (Tag `as` vs. `Slot`)
Primitives must allow custom rendering nodes without sacrificing performance:
- **Primary Option: Tag Selection (`as` Prop)**: By default, components must utilize tag-name selection via an `as` prop (e.g., `as="span"`, `as="a"`). This is the highest-performance path because it renders the dynamic tag directly with zero virtual DOM node manipulation.
- **Secondary Option: Component Composition (`Slot` / `asChild`)**: The custom Scnehaux `asChild` composition pattern using our native custom Slot engine is reserved as a secondary option. Because the custom `Slot` utility performs runtime element cloning and prop merging (`React.cloneElement`), it is prohibited in high-frequency rendering pipelines (such as virtualized list elements, grid cells, active motion animations) to prevent garbage collection spikes and CPU thrashing.

### 3.4 Styled Separation (Zero Recipes Rule)
- **Styling Agnosticism**: Primitives must remain 100% styling-agnostic. They must not import stylesheets, style engines (such as Tailwind or Panda CSS), or define design token recipes (such as sizes, color variants, or visual treatments).
- **Design System Responsibility**: All styling, visual recipes, and token variables must reside in the downstream styled components package (e.g. `@scnx/core-ui`) that wraps the primitive.

---

## 4. Polymorphism & Slot API (asChild Pattern)

Polymorphic elements that allow downstream consumers to customize the DOM node must support the `asChild` composition pattern using Scnehaux's native custom Slot engine. Bypassing this engine or importing third-party slot packages (such as Radix UI's Slot) is prohibited.

### 4.1 Standard Polymorphic Contract
The polymorphic composition system must enforce a uniform property and reference contract:
- **Ref Transparency**: The custom Slot engine must forward and compose refs transparently, ensuring that parent and child refs are chained without memory leaks or unnecessary re-renders. Under React 19, `ref` must be processed as a standard property.
- **Intelligent Attribute Merging**: The Slot engine must perform a shallow merge of properties (`className`, inline `style`) and chain event execution sequences (executing both parent and child handlers).
- **TypeScript Contract Safety**: Components supporting polymorphism must expose an `asChild` contract using generic type helpers that omit overlapping native HTML attributes to prevent compiler bailouts.
- **Reference Implementation**: For concrete code blueprints, type definitions (e.g. `SlotProps`), and integration examples, developers must refer to the local repository technical standards and decision records (e.g., `STD-SCNX-UI-JS-004` and `ADR-SCNX-UI-JS-003`).

### 4.2 Performance Constraints
- **Low-Frequency Layouts**: The use of `asChild` is permitted in static areas or low-frequency rendering contexts (such as card layouts, main layout headers).
- **High-Frequency Execution**: The `asChild` pattern is prohibited in high-frequency rendering environments (such as active animations, drag-and-drop loops, dynamic list virtualizers). Under these performance-sensitive contexts, components must use dynamic `as` prop tags (e.g. `const Comp = as || 'div'; return <Comp />`) to bypass children array cloning overhead.

---

## 5. Property Contracts

To guarantee component boundary isolation and maintain clean API design:
- **UI Primitives (Leaf Props)**: Generic UI primitives (such as Buttons, Inputs, Badges, Tooltips) must accept only leaf primitive values (such as `label`, `isDisabled`, `onClick`) as props. Passing complex domain objects as props to generic UI primitives is prohibited.
- **Rationale**:
  - **Re-render Isolation**: Restricting props to leaf primitives isolates the component from parent object reference changes, preventing unnecessary rendering cycles in legacy/bailout compilation states.
  - **Testing Simplification**: Restricting props streamlines unit testing by eliminating the need to construct complex mock domain objects.

---

## 6. Accessibility Integration

- **Semantic HTML First**: Primitives must render native semantic HTML tags (`<button>`, `<a>`, `<nav>`, `<input>`) instead of styling generic tags (`<div>`, `<span>`) with custom ARIA attributes.
- **Focus Management**: Overlay structures (Dialogs, Drawers, Modals) must trap focus internally during activation and restore focus to the trigger element upon closure.
- **Keyboard Navigation**: Components must implement the keyboard navigation specifications declared in the WAI-ARIA Authoring Practices Guide (APG).

---

## 7. Compliance & Enforcement

- **Accessibility Audits**: Build pipelines must execute static accessibility testing (e.g. `eslint-plugin-jsx-a11y`) to block accessibility violations.
- **Waiver Protocol**: Custom polymorphic patterns or non-headless interactive widgets require a documented project ADR and approval by the Architecture Review Board. The Board must respond with a review decision within **5 business days** of the ADR submission.
