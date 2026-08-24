# Implementation Tasks: AI-Assisted Box Selection System

**Feature Branch**: `001-box-selection-system`
**Date**: 2026-08-24
**Plan**: [specs/001-box-selection-system/plan.md](plan.md)
**Spec**: [specs/001-box-selection-system/spec.md](spec.md)

---

## Phase 1 — Project Foundation

**Purpose**: Core Django configuration, app registration, routing, and base settings.

- [X] T001 Configure Django settings in `config/settings.py` (register `warehouse` app, configure SQLite database, CSRF, template directories, and static assets)
  - *What changes*: Update `INSTALLED_APPS`, `TEMPLATES`, `STATIC_URL`, `STATICFILES_DIRS` in `config/settings.py`.
  - *Why needed*: Establish clean project foundation conforming to Django conventions and security defaults.
  - *Verification*: Run `python manage.py check`.

- [X] T002 Configure URL routing in `config/urls.py` and `warehouse/urls.py`
  - *What changes*: Create `warehouse/urls.py` and include it in `config/urls.py`.
  - *Why needed*: Route requests to order creation, recommendation, catalog views, and admin.
  - *Verification*: Run `python manage.py check`.

---

## Phase 2 — Domain Models

**Purpose**: Persistent domain entities and database schema.

- [X] T003 [P] Implement `Product` model in `warehouse/models.py`
  - *What changes*: Create `Product` model with `sku`, `name`, `length`, `width`, `height`, `weight`, `is_active`, `volume` property, and `MinValueValidator` constraints.
  - *Why needed*: Store dimensional and physical properties of products.
  - *Verification*: Model unit test in `warehouse/tests/test_models.py`.

- [X] T004 [P] Implement `ShippingBox` model in `warehouse/models.py`
  - *What changes*: Create `ShippingBox` model with `name`, `length`, `width`, `height`, `max_weight`, `cost`, `is_active`, `volume` property, and `MinValueValidator` constraints.
  - *Why needed*: Store usable internal dimensions, payload limits, and unit costs of boxes.
  - *Verification*: Model unit test in `warehouse/tests/test_models.py`.

- [X] T005 Implement `Order` and `OrderItem` models in `warehouse/models.py`
  - *What changes*: Create `Order` (`created_at`, `notes`, `total_weight` property) and `OrderItem` (`order`, `product`, `quantity`).
  - *Why needed*: Persist customer orders and item associations.
  - *Verification*: Model unit test verifying order weight calculation.

- [X] T006 Generate and apply initial database migrations in `warehouse/migrations/`
  - *What changes*: Create `0001_initial.py` migration file and apply to SQLite.
  - *Why needed*: Create database tables for products, boxes, and orders.
  - *Verification*: Run `python manage.py makemigrations --check` and `python manage.py migrate`.

---

## Phase 3 — Validation

**Purpose**: Input sanitization, model-level cleaning, and form boundary validation.

- [X] T007 Implement model-level validation and clean methods in `warehouse/models.py`
  - *What changes*: Add custom `clean()` methods on `Product`, `ShippingBox`, and `OrderItem` to enforce strictly positive dimensions, positive weights, positive quantities, and non-negative costs.
  - *Why needed*: Prevent invalid domain data from corrupting database state.
  - *Verification*: Run model validation tests in `warehouse/tests/test_models.py`.

- [X] T008 Implement `OrderForm` and `OrderItemFormSet` in `warehouse/forms.py`
  - *What changes*: Create `OrderForm` and custom `OrderItemFormSet` with validation rejecting empty orders, non-positive quantities, and missing products.
  - *Why needed*: Handle and sanitize user inputs on the order creation screen.
  - *Verification*: Form unit tests in `warehouse/tests/test_forms.py`.

---

## Phase 4 — Packing & Recommendation Engine

**Purpose**: Pure Python deterministic box fitting, 6-axis rotation, weight validation, and ranking.

- [X] T009 Implement domain dataclasses in `warehouse/packing.py`
  - *What changes*: Define `ItemSpec`, `BoxSpec`, `BoxEvaluation`, and `RecommendationResult` dataclasses.
  - *Why needed*: Provide lightweight, decoupled data structures for recommendation calculation without database overhead.
  - *Verification*: Dataclass instantiation test in `warehouse/tests/test_packing.py`.

- [X] T010 Implement 6-axis orthogonal rotation and symmetry deduplication in `warehouse/packing.py`
  - *What changes*: Write `get_orthogonal_rotations(length, width, height)` returning unique `(L, W, H)` permutations.
  - *Why needed*: Test products in all physical spatial orientations.
  - *Verification*: Test rotation permutations for cubic and rectangular items in `warehouse/tests/test_packing.py`.

- [X] T011 Implement 1D orthogonal bounding stack calculation in `warehouse/packing.py`
  - *What changes*: Write `calculate_stack_dimensions(items)` evaluating bounding dimensions across allowable alignment axes.
  - *Why needed*: Determine physical fit for multi-quantity and multi-product orders.
  - *Verification*: Test stacking calculations in `warehouse/tests/test_packing.py`.

- [X] T012 Implement box evaluation, weight filtering, and deterministic ranking in `warehouse/packing.py`
  - *What changes*: Write `recommend_box(order_items, available_boxes)` filtering by weight and dimensions, ranking by smallest volume, and tie-breaking by lowest cost and box name.
  - *Why needed*: Core deterministic recommendation engine.
  - *Verification*: Test ranking and tie-breaking against spec scenarios in `warehouse/tests/test_packing.py`.

- [X] T013 Implement selection explanation and itemized rejection diagnostic generator in `warehouse/packing.py`
  - *What changes*: Generate human-readable explanation strings and per-box rejection reasons (dimension overflow, weight limit overflow).
  - *Why needed*: Ensure transparency and explainability for warehouse operators.
  - *Verification*: Test explanation output in `warehouse/tests/test_packing.py`.

---

## Phase 5 — Django Views & Routing

**Purpose**: HTTP request orchestration, form submission handling, and template context delivery.

- [X] T014 Implement `OrderCreateView` in `warehouse/views.py`
  - *What changes*: Create view handling GET (render order form with available products) and POST (validate formset, save Order and OrderItems, redirect to recommendation view).
  - *Why needed*: Enable warehouse staff to create orders and submit for packing.
  - *Verification*: View tests in `warehouse/tests/test_views.py`.

- [X] T015 Implement `OrderRecommendationView` in `warehouse/views.py`
  - *What changes*: Create view fetching order, invoking `recommend_box()`, and passing `RecommendationResult` to the result template.
  - *Why needed*: Display recommendation and rejection breakdown for an order.
  - *Verification*: View tests in `warehouse/tests/test_views.py`.

- [X] T016 [P] Implement `ProductListView` and `BoxListView` in `warehouse/views.py`
  - *What changes*: Create views rendering active product catalog and active shipping box specifications.
  - *Why needed*: Allow warehouse staff to inspect available inventory and box specs.
  - *Verification*: View tests in `warehouse/tests/test_views.py`.

---

## Phase 6 — UI Templates & Styling

**Purpose**: High-contrast, warehouse-focused templates with zero marketing fluff.

- [X] T017 Create base template in `warehouse/templates/warehouse/base.html`
  - *What changes*: Create accessible HTML5 skeleton with header navigation, warehouse title, main content area, and message banners.
  - *Why needed*: Common layout hierarchy across all warehouse screens.
  - *Verification*: Template rendering in view tests.

- [X] T018 Create order creation template in `warehouse/templates/warehouse/order_form.html`
  - *What changes*: Build accessible form with product selectors, quantity inputs, add-row buttons, CSRF token, and inline validation error blocks.
  - *Why needed*: Interactive order entry UI.
  - *Verification*: Form rendering test in `warehouse/tests/test_views.py`.

- [X] T019 Create recommendation result template in `warehouse/templates/warehouse/recommendation_result.html`
  - *What changes*: Build recommendation display: Winner Card (box name, dimensions, volume, cost, weight capacity), Selection Explanation banner, and Itemized Rejection Diagnostic Table for disqualified boxes.
  - *Why needed*: Present clear recommendation and diagnostic feedback to staff.
  - *Verification*: Result rendering test in `warehouse/tests/test_views.py`.

- [X] T020 [P] Create catalog templates in `warehouse/templates/warehouse/product_list.html` and `box_list.html`
  - *What changes*: Build tabular views of products (SKU, name, dimensions, weight) and boxes (name, dimensions, max weight, cost, volume).
  - *Why needed*: Fast catalog inspection for warehouse staff.
  - *Verification*: Catalog rendering tests in `warehouse/tests/test_views.py`.

- [X] T021 [P] Create high-contrast warehouse stylesheet in `warehouse/static/warehouse/style.css`
  - *What changes*: Write clean Vanilla CSS with readable typography, distinct status badges (`RECOMMENDED`, `REJECTED`), high-contrast buttons, and responsive grid/tables.
  - *Why needed*: Ergonomic, functional UI without bloated JS frameworks.
  - *Verification*: Browser test and static asset verification.

---

## Phase 7 — Django Admin Configuration

**Purpose**: Operational inventory and catalog management.

- [X] T022 Register admin models in `warehouse/admin.py`
  - *What changes*: Register `ProductAdmin` (list display: SKU, name, dimensions, weight, active; search: name, SKU), `ShippingBoxAdmin` (list display: name, dimensions, max weight, cost, volume), and `OrderAdmin` with `OrderItemInline`.
  - *Why needed*: Allow warehouse managers to manage packaging types and products.
  - *Verification*: Admin registration checks in test suite.

---

## Phase 8 — Automated Test Suite

**Purpose**: Exhaustive automated verification of all business rules, geometric invariants, and edge cases.

- [X] T023 Implement domain packing tests in `warehouse/tests/test_packing.py`
  - *What changes*: Write test cases covering:
    - 6-axis orthogonal rotation and deduplication
    - Dimensional rejection (exceeding length, width, height in all orientations)
    - Weight limit rejection (`order_weight > box.max_weight`)
    - Volume ranking (smallest box chosen)
    - Cost tie-breaking (lowest cost wins on identical volume)
    - Multi-quantity item stacking
    - Empty catalog and un-fittable item handling ("No suitable box")
  - *Why needed*: Guarantee 100% deterministic, mathematically sound domain behavior.
  - *Verification*: Run `python manage.py test warehouse.tests.test_packing`.

- [X] T024 Implement model and form validation tests in `warehouse/tests/test_models.py` and `warehouse/tests/test_forms.py`
  - *What changes*: Write test cases for:
    - Negative and zero dimensions, weights, quantities
    - Negative box cost rejection
    - Empty order submission rejection
    - Derived model properties (`volume`, `total_weight`)
  - *Why needed*: Enforce strict boundary validation.
  - *Verification*: Run `python manage.py test warehouse.tests.test_models warehouse.tests.test_forms`.

- [X] T025 Implement view, integration, and AI tests in `warehouse/tests/test_views.py`, `test_ai.py`, and `test_admin.py`
  - *What changes*: Write end-to-end integration tests for:
    - GET order form -> POST valid order -> redirect to recommendation -> render winner card
    - GET recommendation for oversized order -> render "No Suitable Box Found" state
    - Asynchronous JSON AI explanation endpoint (`/order/<id>/ai-explanation/`)
    - AI fault-tolerance (timeouts, HTTP errors, malformed responses, independent deterministic engine execution)
    - Custom admin theme branding
    - Catalog listing views
  - *Why needed*: Validate HTTP flows, template rendering, and error handling.
  - *Verification*: Run `python manage.py test`.

---

## Phase 9 — Documentation

**Purpose**: Accurate, reproducible setup and assignment documentation.

- [X] T026 Create project `README.md`
  - *What changes*: Write clear documentation covering overview, architecture, packing approach, setup, test runs, and workflows.
  - *Why needed*: Ensure any reviewer can set up, run, and understand the project in <5 minutes.
  - *Verification*: Manual walkthrough of README instructions.

- [X] T027 Create `AI_USAGE.md` structure
  - *What changes*: Write structured template placeholders for genuine user AI interaction history without fabricating artificial chat transcripts.
  - *Why needed*: Fulfill assignment requirement with 100% integrity.
  - *Verification*: Review against Constitution Principle X.

---

## Phase 10 — Verification & Quality Gates

**Purpose**: Final quality audit and execution proof.

- [X] T028 Run full automated test suite, capture real output in `TEST_OUTPUT.md`, and execute Django quality checks
  - *What changes*: Run `python manage.py test`, redirect actual output to `TEST_OUTPUT.md`, run `python manage.py check`, and run `python manage.py makemigrations --check`.
  - *Why needed*: Provide empirical verification that all 51 quality checklist criteria pass.
  - *Verification*: 100% passing tests, 0 check errors, 0 pending migrations.
