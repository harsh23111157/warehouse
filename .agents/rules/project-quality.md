# Project Quality & Engineering Rules: AI-Assisted Box Selection System

These rules govern all design, implementation, testing, review, and verification work on the AI-Assisted Box Selection System for an ecommerce warehouse.

---

## 1. Project & Technology Baseline

### Context
- **Project**: AI-Assisted Box Selection System for an ecommerce warehouse.
- **Domain**: Automated, deterministic recommendation of optimal shipping boxes based on product dimensions, weights, quantities, box specs, and business ranking rules.

### Stack & Invariants
- **Language**: Python 3.x
- **Framework**: Django
- **Database**: SQLite for local development (unless repository configuration explicitly specifies another engine)
- **Frontend**: Django templates for the primary UI; Vanilla JavaScript strictly where client interaction genuinely requires it
- **Testing**: `pytest` or Django test framework (`django.test`), using one consistent convention throughout
- **Dependencies**: No unnecessary frontend frameworks; no unnecessary third-party packages. Rely on Python standard library and Django core.

---

## 2. Engineering Principles

### 1. No AI Slop
- Do not generate large amounts of code without first inspecting and understanding the repository and current architecture.
- Do not create abstractions merely because they appear architecturally sophisticated.
- Prefer simple, explicit Django code over unnecessary service layers, repositories, factories, managers, serializers, DTOs, or generic frameworks.
- Every abstraction must have a concrete, demonstrable reason.

### 2. Human-Readable Code
- Code must look like it was written and reviewed by a competent Python/Django engineer.
- **Prefer**:
  - Descriptive names
  - Small, focused functions
  - Clear control flow
  - Explicit domain logic
  - Type hints where useful
  - Meaningful docstrings only where they add real information
- **Avoid**:
  - Clever one-liners
  - Excessive or generated-looking comments
  - Unnecessary defensive programming
  - Repeated abstractions
  - Giant functions or giant files
  - Generic utility modules containing unrelated helpers

### 3. Django Conventions
- Follow standard Django conventions idiomatic to clean projects:
  - **Models**: Persistent domain entities and relational integrity
  - **Forms**: Form validation, clean methods, and user input sanitization
  - **Views**: Request orchestration and response generation
  - **Templates**: Semantic HTML presentation and layout hierarchy
  - **Django Admin**: Operational data management and inspection
  - **Tests**: Located close to the relevant application behavior
- Do not introduce Django REST Framework unless the specification genuinely requires a standalone REST API.

### 4. Deterministic Domain Logic
- The box recommendation algorithm must be **100% deterministic**.
- The recommendation must be fully reproducible from:
  - Product dimensions (Length, Width, Height)
  - Product weight
  - Product quantity
  - Box internal dimensions (Length, Width, Height)
  - Box maximum weight capacity
  - Box unit cost
- **Never use an LLM or non-deterministic heuristic to decide which box fits.**
- The algorithm must have explicit, testable, verifiable mathematical rules.

### 5. Dimensions & Orientations
- Do not silently assume that product dimensions can only be compared in their stored orientation.
- Where appropriate, evaluate all six axis-aligned orthogonal orientations of a rectangular product:
  1. `(L, W, H)`
  2. `(L, H, W)`
  3. `(W, L, H)`
  4. `(W, H, L)`
  5. `(H, L, W)`
  6. `(H, W, L)`
- Deduplicate permutations when dimensions are equal (e.g., cubes or square cross-sections).
- The implementation must clearly document whether the packing model supports:
  - A single product item,
  - Multiple quantities of the same product,
  - Multiple different products,
  - Or a specific constrained packing model (e.g., 1D bounding stack / bounding box).
- Do not pretend to solve arbitrary 3D bin packing unless the specification explicitly requires it.

### 6. Weight Handling
- Total order weight must be computed strictly as: `product_weight × quantity` (or sum of weights across all items).
- A box is **invalid** when the total order weight exceeds the box's maximum supported weight.

### 7. Box Ranking & Selection
- Ranking criteria must be explicitly documented and tested.
- Follow clear, deterministic business rules:
  1. Filter to candidate boxes that can physically contain the order and support the weight.
  2. Choose the smallest suitable box by internal volume.
  3. Use box unit cost as a secondary tie-breaker (lowest cost wins).
  4. Use a deterministic tertiary tie-breaker (e.g., box name or ID alphabetical/numeric sort) if volume and cost are identical.
- Do not introduce arbitrary or unexplained heuristic scoring formulas.

### 8. Edge Cases
Explicitly handle and test:
- No products in order / empty catalog
- Zero quantity or negative quantity
- Zero or negative dimensions
- Zero or negative weight
- No boxes configured in catalog
- Product too large for every available box
- Order weight exceeding all box capacities
- Multiple boxes with equal suitability (exact ties)
- Rotated products fitting where non-rotated fail
- Duplicate dimensions across axis permutations

### 9. Security & Hardening
- Follow Django security defaults strictly:
  - Never disable CSRF protection.
  - Never disable authentication or permission checks to make development easier.
  - Never trust raw request values; validate via Django Forms / clean methods.
  - Never use raw SQL queries without a concrete, documented need.
  - Never hardcode secrets or API keys.
  - Never commit `.env` or local secret files.
  - Never expose `DEBUG = True` in production configurations.

### 10. Automated Testing
- Every business rule and edge case must have automated tests.
- Tests must verify behavior rather than implementation details.
- Minimum required test coverage:
  - Valid product/box fit
  - 3D product rotation fit
  - Weight rejection
  - Dimension rejection
  - Multiple item quantities
  - No suitable box handling (empty recommendation state)
  - Ranking order verification
  - Tie-breaking rules
  - Invalid domain data validation (negative numbers, zero values)
  - Empty order handling

### 11. User Interface (UI)
- The UI must be restrained, functional, and professional.
- **Avoid**:
  - Excessive gradients, glassmorphism, or flashy animations
  - Huge hero sections or marketing copy
  - Fake dashboard metrics or unnecessary metric cards
  - Decorative elements with no warehouse utility
  - Emoji used as interface icons
- **Prioritize**:
  - Clear information hierarchy
  - High readability and contrast
  - Clear, accessible primary actions
  - Useful empty states and error notices
  - Real-time or clear validation feedback
  - Transparent explanations of why a box was recommended
  - Responsive layout usable on warehouse tablets/desktops

### 12. Database Management
- Manage all schema changes through standard Django migrations (`makemigrations` / `migrate`).
- Do not modify database tables or columns manually.
- Do not commit local development database files (`db.sqlite3`) unless explicitly required.

### 13. Dependency Hygiene
- Before adding any third-party dependency, check if Python standard library or Django already solves the problem.
- Do not install packages merely for convenience.

### 14. Documentation Integrity
- Documentation must describe actual implementation decisions and real code paths.
- **Never invent or fabricate**:
  - Test results or benchmark numbers
  - Performance measurements
  - AI prompts or fake conversation transcripts
  - Verification steps that were not actually run
  - User research or fake metrics
  - Deployment results

### 15. AI Usage Tracking (`AI_USAGE.md`)
- The assignment explicitly requires an `AI_USAGE.md` document.
- Do not fabricate the user's AI interaction history.
- Do not generate the user's personal "What I learned" response.
- Do not generate fake chat transcripts.
- Provide clean, structured templates and placeholders for the user to document their actual interaction history.

### 16. Empirical Verification
- Never claim that tests pass without executing them.
- Post-implementation verification protocol:
  1. Run the test suite (`python manage.py test` or `pytest`).
  2. Inspect failures, fix root causes, and re-run until all pass cleanly.
  3. Run Django system checks (`python manage.py check`).
  4. Inspect and verify migrations (`python manage.py makemigrations --check`).
  5. Manually exercise the primary user flow.

### 17. Change Discipline
- Before modifying any file:
  - Inspect existing code and understand why it exists.
  - Make the smallest surgical change necessary.
  - Do not rewrite unrelated files or refactor working code unnecessarily.

### 18. Finishing Standard
Before declaring any milestone or the project complete, verify:
- All functional requirements are implemented.
- All domain rules and edge cases have automated tests passing.
- Django migrations apply cleanly with no pending drift.
- Django checks pass with 0 errors.
- No debug artifacts, temporary scripts, or secrets remain.
- `README.md` accurately describes setup, architecture, and usage.
- `AI_USAGE.md` contains structured placeholders for genuine user records.
- `TEST_OUTPUT.md` contains actual, unedited test execution outputs.
- When uncertain, stop and explain the uncertainty instead of inventing an answer.
