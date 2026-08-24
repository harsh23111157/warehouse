<!--
Sync Impact Report
Version: initial -> 1.0.0
Modified Principles: initial template placeholders -> 11 ratified core principles
Added Sections:
  - Core Principles (I. Correctness Over Cleverness, II. Deterministic Domain Logic, III. Idiomatic Django Architecture, IV. Minimal Footprint & No Unnecessary Abstractions, V. Automated Verification of Business Rules, VI. Exhaustive Input & Boundary Validation, VII. Secure Django Defaults, VIII. Dependency Minimalism, IX. Warehouse-Oriented UI Utility, X. Documentation Integrity & No Fabrication, XI. Human Oversight of AI Implementation)
  - Technical & Domain Governance Rules (Architecture, Domain Modeling, Recommendation Engine, Validation, Testing, Security, Documentation, Dependency Management, UI Quality, AI-Assisted Development, Verification)
  - Governance & Enforcement Policy
Removed Sections: None (replaced generic template scaffold)
Follow-up TODOs: None
-->

# AI-Assisted Box Selection System Constitution

## Core Principles

### I. Correctness Over Cleverness
The primary objective of the system is absolute mathematical correctness and real-world warehouse utility. Code must be transparent, readable, and auditable by any Python/Django engineer. Eschew clever one-liners, overly generic meta-programming, and speculative flexibility.

### II. Deterministic and Explainable Domain Logic (NON-NEGOTIABLE)
The core box selection and recommendation algorithm MUST be 100% deterministic, reproducible, and explainable. The recommendation must derive strictly from product dimensions, product weight, item quantities, box internal dimensions, box maximum weight capacity, and box unit cost. **An LLM or non-deterministic heuristic MUST NEVER be used to make box selection or fitting decisions.** Every recommendation must provide human-understandable explanation details (e.g., orientation tested, volume utilization, weight limit headroom).

### III. Idiomatic Django Architecture
Follow standard, idiomatic Django architecture patterns:
- **Models**: Encapsulate persistent entities (Products, Boxes, Orders) with database constraints.
- **Forms**: Validate, clean, and sanitize user input.
- **Views**: Orchestrate HTTP request/response flows.
- **Templates**: Render semantic HTML server-side.
- **Django Admin**: Provide operational data management.
Do NOT introduce Django REST Framework (DRF), GraphQL, or decoupled API layers unless an external API specification is explicitly mandated.

### IV. Minimal Footprint & No Unnecessary Abstractions
Every abstraction must have a concrete, demonstrable reason. Do NOT introduce service layers, repositories, factories, custom manager hierarchies, serializers, DTOs, or generic utility modules for single-use logic. Write the minimum amount of clear, maintainable code necessary to fulfill the requirements.

### V. Automated Verification of Business Rules
Every business rule, geometric fitting constraint, weight limit, and edge case must be backed by fast, automated tests. Tests must verify observable system behavior and mathematical invariants rather than internal implementation details.

### VI. Exhaustive Input & Boundary Validation
The system MUST explicitly detect and gracefully handle all boundary and invalid inputs at the form/domain boundary before recommendation calculation. Zero values, negative numbers, missing entities, empty catalogs, oversized products, and overweight orders must trigger clear validation feedback without crashing or unhandled exceptions.

### VII. Secure Django Defaults
Security standards are non-negotiable:
- CSRF protection must remain enabled on all mutating views.
- Authentication and authorization checks must not be bypassed for convenience.
- Never trust raw client input; sanitize via Django Forms.
- Never construct raw SQL strings.
- Never commit secrets, credentials, or `.env` files.
- `DEBUG = False` in production settings.

### VIII. Dependency Minimalism
Do not introduce external packages for functionality already provided by the Python standard library (e.g., `math`, `itertools`, `dataclasses`, `decimal`) or Django core. Every additional third-party package must be explicitly justified.

### IX. Warehouse-Oriented UI Utility
The UI must be designed for warehouse efficiency, speed, and readability. Avoid consumer SaaS aesthetics (excessive gradients, glassmorphism, decorative animations, marketing fluff, fake metrics, or emoji icons). Prioritize high contrast, clear visual hierarchy, accessible input controls, explicit validation messages, responsive layout, and transparent recommendation breakdowns.

### X. Documentation Integrity (Zero Fabrication)
Documentation, test summaries, and reports must reflect actual codebase state and genuine command execution outputs. Never invent or fabricate test results, benchmarks, performance metrics, AI interaction history, or user research.

### XI. Human Oversight & AI Discipline
All AI-generated code, schemas, and templates must be systematically reviewed, executed, and verified. AI interaction logs must reside in `AI_USAGE.md` as authentic records (or structured templates for genuine user completion), free of artificial chat transcripts or manufactured personal reflections.

---

## Technical & Domain Rules

### 1. Domain Modeling
- Store physical measurements using explicit numeric precision (`DecimalField` or `FloatField`) with documented units (e.g., cm for dimensions, kg/g for weight, currency for cost).
- Enforce relational integrity and database-level validation (`MinValueValidator`, positive constraints).
- Explicitly separate product dimensions and box internal usable dimensions.

### 2. Recommendation Engine & Geometric Constraints
- The box recommendation engine must evaluate candidate boxes through explicit filtering stages:
  1. **Weight Capacity Filter**: `Total Order Weight = sum(product_weight * quantity) <= box.max_weight`.
  2. **Geometric Fit Evaluation**: Test rectangular fit against internal dimensions `(box.length, box.width, box.height)`.
  3. **Orientation Handling**: Test all 6 orthogonal axis-aligned product orientations:
     - `(L, W, H)`, `(L, H, W)`, `(W, L, H)`, `(W, H, L)`, `(H, L, W)`, `(H, W, L)`.
     - Deduplicate permutations when dimensions are identical.
  4. **Multi-Item Model Definition**: Explicitly document the packing model (e.g., single item, single SKU multiple quantity along an optimal dimension bounding stack, or combined bounding volume). Do not claim to solve arbitrary multi-SKU 3D NP-hard bin packing unless explicitly required.
  5. **Selection & Tie-Breaking**:
     - Rank valid boxes by smallest internal volume (`L * W * H`).
     - Secondary tie-breaker: Lowest unit cost.
     - Tertiary tie-breaker: Deterministic identifier sorting (box ID/name).
  6. **Empty State**: Return an explicit, explanatory "No Suitable Box Found" state if no box satisfies weight or dimensional constraints.

### 3. Testing Standards
- Test suite must run cleanly via `pytest` or `python manage.py test`.
- Minimum required automated test scenarios:
  - Exact dimensional fit and rotational fitting (fitting only when rotated).
  - Dimensional rejection (exceeding length, width, or height in all orientations).
  - Total weight exceeding box maximum weight capacity.
  - Multi-quantity items within and exceeding box limits.
  - Ranking order verification (smallest volume first).
  - Cost tie-breaking verification.
  - Empty order, empty box catalog, and zero/negative quantity or dimension rejection.

### 4. Verification Workflow
- Implementation completion requires:
  1. `python manage.py check` passes with 0 issues.
  2. `python manage.py makemigrations --check` detects no unapplied model drift.
  3. Full automated test suite passes with 100% green status.
  4. Real test execution outputs recorded in `TEST_OUTPUT.md`.
  5. Manual walkthrough of UI order input and recommendation rendering.

---

## Governance

- **Authority**: This Constitution supersedes all informal coding conventions and ad-hoc practices for the AI-Assisted Box Selection System.
- **Complexity Gate**: Any proposed abstraction (e.g., custom services, design patterns, additional libraries) must be justified against Principles III, IV, and VIII.
- **Amendments**: Amendments require updating this document with an incremented version number and updating the Sync Impact Report header.
- **Semantic Versioning Policy**:
  - `MAJOR`: Fundamental redefinition of core architecture, domain rules, or governance principles.
  - `MINOR`: New domain rules, additional constraints, or expanded architectural guidelines.
  - `PATCH`: Wording clarifications, typo fixes, or non-semantic formatting updates.

**Version**: 1.0.0 | **Ratified**: 2026-08-24 | **Last Amended**: 2026-08-24
