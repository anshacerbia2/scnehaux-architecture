---
doc_meta:
  id: ADR-GLB-FE-003
  title: ADR-GLB-FE-003 Standardization on Enterprise Meta-Framework
  adr_type: foundational
  status: accepted
  created: 2026-01-01
  created_date: 2026-01-01
  created_by: Principal Frontend Architect
---

# ADR-GLB-FE-003: Standardization on Enterprise Meta-Framework (Next.js)

---

## 1. Title

Standardization on Enterprise Meta-Framework (Next.js & Turbopack)

## 2. Status

| Date       | Status   | ADR Type     | Reviewers                              | Approver                  |
| ---------- | -------- | ------------ | -------------------------------------- | ------------------------- |
| 2026-04-04 | proposed | foundational | Frontend SMEs (Subject Matter Experts) | Architecture Review Board |
| 2026-04-07 | accepted | foundational | Frontend SMEs (Subject Matter Experts) | Architecture Review Board |

## 3. Context

Following the decision to use React as the foundational rendering engine ([ADR-GLB-FE-001](ADR-GLB-FE-001-react-ecosystem.md)) and Rsbuild/Vite for SPAs ([ADR-GLB-FE-002](ADR-GLB-FE-002-build-toolchain.md)), the enterprise requires a standardized approach for applications that demand Server-Side Rendering (SSR), Search Engine Optimization (SEO), and full-stack API capabilities. Historically, teams have built custom Node.js Express servers to hydrate React, leading to severe architectural fragmentation, memory leaks, and complex deployment topologies.

## 4. Decision Drivers

- **SEO & Core Web Vitals**: Public-facing applications (B2C) require sub-second First Contentful Paint (FCP) and perfect search engine indexing, which cannot be achieved reliably with pure Single Page Applications (SPAs).
- **React Server Components (RSC)**: The enterprise must align with React's paradigm shift towards server-first rendering to reduce client-side JavaScript payloads.
- **Infrastructure Standardization**: DevOps requires a predictable, standardized deployment topology for full-stack frontend applications (Node.js/Edge).
- **Compiler Performance**: The meta-framework must possess a high-performance compiler capable of scaling to enterprise-grade repositories without suffering from legacy Webpack sluggishness.

## 5. Decision

We will standardize **Next.js** (App Router paradigm) as the exclusive and mandatory meta-framework for all enterprise applications requiring Server-Side Rendering (SSR), Static Site Generation (SSG), or React Server Components (RSC).

- **Turbopack**: All Next.js applications must utilize **Turbopack** (the Rust-based compiler) for local development to ensure parity with our sub-second developer velocity mandate.
- **Architectural Boundary**: Next.js is strictly reserved for B2C applications or dashboards where SEO and initial load performance are critical. For isolated, highly interactive B2B internal tools without SEO requirements, teams must default to Rsbuild/Vite ([ADR-GLB-FE-002](ADR-GLB-FE-002-build-toolchain.md)) to avoid unnecessary Node.js server overhead.

## 6. Consequences

### Positive

- **Out-of-the-box Performance**: Teams get SSR, Image Optimization, and Font Optimization with zero manual configuration.
- **Payload Reduction**: Leveraging React Server Components (RSC) drastically reduces the Javascript shipped to the browser.
- **Unified DX**: Turbopack provides the same Rust-powered sub-second compilation speed that we achieved with Rsbuild in SPAs.

### Negative & Risks

- **Operational Cost**: Next.js requires active Node.js compute (or Edge Functions), which is significantly more expensive and complex to scale than hosting static Rsbuild SPAs on an S3 bucket.
- **Paradigm Shift**: Engineers must undergo extensive upskilling to understand the mental model of RSC vs Client Boundaries (`"use client"`).

### Operational

- All Next.js applications must strictly enforce the `"use server"` and `"use client"` directives according to the Enterprise React Standards.
- Custom Express.js servers for React hydration are strictly prohibited.

## 7. Compliance Impact

### Related Standards

- [ADR-GLB-FE-001 (React Ecosystem)](ADR-GLB-FE-001-react-ecosystem.md)
- [ADR-GLB-FE-002 (Build Toolchains)](ADR-GLB-FE-002-build-toolchain.md)
- [STD-GLB-FE-001 (Tech Stack)](../../02-standards/_global/STD-GLB-FE-001-tech-stack.md)

### Compliance Status

Compliant.

### Required Waivers

None.

## 8. Alternatives Considered

- **Remix**: Rejected. While possessing excellent Web Standards adherence, the external talent pool, ecosystem maturity, and native support for React Server Components (RSC) currently favor Next.js at an enterprise scale.
- **Nuxt**: Rejected. Incompatible with the foundational mandate to standardize exclusively on the React ecosystem.
