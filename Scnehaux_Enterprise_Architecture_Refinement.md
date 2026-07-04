# Scnehaux Enterprise Architecture Refinement Proposal

## Philosophy

Architecture is not a representation of source code. Architecture is a
representation of enterprise intent.

-   Vision before implementation.
-   Capability before product.
-   Product before system.
-   System before code.
-   Code before repository.
-   Repository before deployment.

## Proposed Hierarchy

    Enterprise Vision
        ↓
    Enterprise Capability Map
        ↓
    Enterprise Architecture (BDAT)
        ↓
    Platform Architecture
        ↓
    Product Architecture (PAD)
        ↓
    System Architecture (SAD)
        ↓
    ADR
        ↓
    TDD

## Refinements

### 1. Enterprise Capability Map

Add a capability layer before BDAT to define what the enterprise owns.

Suggested Level-1 capabilities: - Core Platform - Identity & Trust -
Business Products - Shared Platform Services - Intelligence Platform -
Developer Ecosystem - Marketplace & Commerce

### 2. BDAT

Capability precedes Business, Data, Application and Technology
Architecture.

### 3. Platform Architecture

Separate cross-product capabilities such as: - Tenant - Identity -
Workflow - Eventing - Notification - Search - Observability - AI

### 4. Product Architecture (PAD)

One PAD per product (IAM, HCM, ERP, CRM, Work Management).

### 5. System Architecture (SAD)

One or more SAD beneath each PAD for bounded contexts.

### 6. ADR

Every decision should trace back to: Capability → Product → System → ADR

### 7. TDD

Implementation artifacts only.

## Traceability

    Vision
     ↓
    Capability
     ↓
    Product
     ↓
    Domain
     ↓
    Bounded Context
     ↓
    System
     ↓
    Component
     ↓
    Code
     ↓
    Repository
     ↓
    Deployment

## Guiding Principle

Repositories are consequences of architecture---not the other way
around.
