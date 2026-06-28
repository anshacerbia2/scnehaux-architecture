# Governance Automation & Next Steps (TODO)

This document tracks the pending automation tasks and backlog items required to enforce the Scnehaux Architecture Governance policies (specifically around PR approvals, CODEOWNERS, and multi-layered document changes).

## 1. GitHub Actions (Sequential Review Automation)
- [ ] **Create `.github/workflows/sequential-review.yml`**: 
  - **Trigger**: `pull_request_review` (submitted).
  - **Condition**: If the PR contains both Domain-level decisions (ADR) and System-level topologies (SAD).
  - **Action**: When the Domain Lead approves the ADR, the workflow automatically pings/assigns the System Lead to review the execution (SAD).
  - **Goal**: Prevent System Leads from wasting time reviewing unapproved architectural concepts, enforcing a top-down DAG approval process without manual coordination.

## 2. CODEOWNERS Configuration
- [ ] **Configure `.github/CODEOWNERS` for the Root Repo**:
  - Implement pattern matching for flat directories to separate Domain vs System authority.
  - **Example**:
    ```text
    # Domain-wide ADRs (Applies to all systems in UI Platform)
    /05-decisions/ui-platform/ADR-UIP-[0-9]*.md         @scnehaux/ui-domain-leads
    
    # System-specific ADRs (Physically in Domain folder, Logically scoped to System)
    /05-decisions/ui-platform/ADR-UIP-CORE-*.md         @scnehaux/ui-core-system-leads
    /05-decisions/ui-platform/ADR-UIP-DASH-*.md         @scnehaux/ui-dashboard-system-leads
    ```

## 3. Governance Policy Updates
- [ ] **Draft PR Culture (GDC-004)**: Until the sequential GitHub Action is fully deployed, update `GDC-004-review-process.md` to officially document the "Draft PR" workflow as a cultural standard. Engineers must open PRs as Drafts and manually request Domain Lead approval before marking as Ready for Review for System Leads.
- [ ] **Master SAD Guidelines (GDC-010)**: Draft the governance rules for "Master SADs" in systems that utilize a multi-repo library/SDK architecture to prevent documentation fragmentation. (This is the immediate next priority).
