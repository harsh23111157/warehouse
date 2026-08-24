# Implementation Plan: AI-Assisted Box Selection System

**Branch**: `001-box-selection-system` | **Date**: 2026-08-24 | **Spec**: [specs/001-box-selection-system/spec.md](spec.md)

---

## Summary

Build a production-quality, deterministic Django box selection system for an ecommerce warehouse. The system validates orders, calculates total weight, evaluates candidate boxes across all 6 orthogonal product rotations and bounding stacks, eliminates boxes exceeding weight limits or physical boundaries, ranks valid boxes by volume and cost tie-breakers, and renders a clear warehouse UI with transparent selection explanations and itemized rejection diagnostics.

---

## Technical Context

- **Language/Version**: Python 3.13.x (compatible with 3.10+)
- **Primary Dependencies**: Django (standard library only; no DRF, no heavy JS frameworks)
- **Storage**: SQLite (`db.sqlite3` for local development)
- **Testing**: Django test framework (`django.test.TestCase`) and `pytest-django`
- **Target Platform**: Cross-platform (Windows / Linux / macOS local dev server)
- **Project Type**: Django Web Application (Server-rendered HTML with Django templates)
- **Performance Goals**: Sub-50ms recommendation response for 100+ boxes
- **Constraints**: 100% deterministic decision logic; 0% LLM dependency in packing algorithm; zero unrequested service abstractions
- **Scale/Scope**: Warehouse staff order creation, recommendation view, catalog views, Django Admin CRUD

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Principle I (Correctness over Cleverness)**: Plan prioritizes clean, readable Python code without obscure tricks.
- [x] **Principle II (Deterministic Domain Logic)**: Box fitting uses explicit mathematical formulas and orthogonal rotations; no LLMs or probabilistic heuristics.
- [x] **Principle III (Idiomatic Django)**: Standard Models, Forms, Views, Templates, and Admin.
- [x] **Principle IV (Minimal Footprint)**: Only essential models and single `warehouse/packing.py` domain module; no boilerplate repositories/serializers.
- [x] **Principle V (Automated Testing)**: Comprehensive test suite covering rotation, fit, weight rejection, ranking, boundary errors, and edge cases.
- [x] **Principle VI (Input Validation)**: Explicit validation of non-positive dimensions, weights, quantities, and empty orders.
- [x] **Principle VII (Security)**: CSRF enabled, sanitized forms, no hardcoded secrets, DEBUG disabled in production config.
- [x] **Principle VIII (Dependency Minimalism)**: Only standard library and Django core.
- [x] **Principle IX (Warehouse UI)**: Restrained, functional, accessible UI; no marketing cards or emoji icons.
- [x] **Principle X (Documentation Integrity)**: Authentic README, genuine AI_USAGE placeholders, real TEST_OUTPUT logs.
- [x] **Principle XI (Human Oversight)**: Systematic verification and real command execution.

---

## Project Structure

### Documentation & Specifications
```text
specs/001-box-selection-system/
├── spec.md                  # Feature Specification
├── plan.md                  # Implementation Plan (this file)
├── research.md              # Technical research & architectural decisions
├── data-model.md            # Entity schemas, constraints, and domain dataclasses
├── quickstart.md            # Setup, test, and smoke test execution guide
├── contracts/
│   └── ui-contracts.md      # Route specs, form payloads, and context contracts
└── checklists/
    └── requirements.md      # Specification quality checklist
```

### Source Code Layout
```text
assignment/
├── config/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py          # Django project settings
│   ├── urls.py              # Root routing
│   └── wsgi.py
├── warehouse/
│   ├── __init__.py
│   ├── admin.py             # Django Admin for Product, ShippingBox, Order
│   ├── apps.py              # Warehouse AppConfig
│   ├── forms.py             # OrderForm, OrderItemFormSet with boundary validation
│   ├── models.py            # Product, ShippingBox, Order, OrderItem
│   ├── packing.py           # Pure domain packing, 6-axis rotation & ranking engine
│   ├── views.py             # OrderCreateView, RecommendationView, CatalogViews
│   ├── urls.py              # App URLs
│   ├── templates/
│   │   └── warehouse/
│   │       ├── base.html
│   │       ├── order_form.html
│   │       ├── recommendation_result.html
│   │       ├── product_list.html
│   │       └── box_list.html
│   ├── static/
│   │   └── warehouse/
│   │       └── style.css    # High-contrast warehouse CSS (vanilla)
│   └── tests/
│       ├── __init__.py
│       ├── test_models.py   # Model validation & properties
│       ├── test_packing.py  # Pure algorithm unit tests (rotation, fit, weight, ranking)
│       ├── test_forms.py    # Form validation and error checks
│       └── test_views.py    # Request orchestration, response codes, context data
├── manage.py
├── .gitignore
├── README.md
├── AI_USAGE.md
└── TEST_OUTPUT.md
```

---

## Risk Analysis & Mitigation

| Risk | Impact | Mitigation |
|---|---|---|
| Non-deterministic tie-breaking | Inconsistent recommendations between runs | Enforce secondary cost tie-breaker and tertiary ID/name tie-breaker in `packing.py` |
| Large quantity arithmetic / performance | Slow response or memory strain | Use closed-form orthogonal 1D bounding stack evaluation ($O(1)$) instead of iterative item placement |
| Missing box catalog edge case | Unhandled exception on recommendation | Explicit empty catalog check returning clean "No registered boxes" state |
| Invalid dimension submissions | Calculation crash or negative volumes | Strict Django Form validators rejecting `<= 0` values |

---

## Verification Strategy

1. **Unit Tests**:
   - `test_packing.py`: Test 6-axis rotation permutations, symmetry deduplication, exact dimension boundaries, weight limit rejection, volume calculation, and cost tie-breaking.
2. **Model Tests**:
   - `test_models.py`: Test field constraints, `clean()` methods, and calculated properties (`volume`, `total_weight`).
3. **Form Tests**:
   - `test_forms.py`: Test boundary rejection (zero/negative numbers, empty orders).
4. **Integration & View Tests**:
   - `test_views.py`: Test order creation, redirection, recommendation rendering, and "No fit" diagnostic view.
5. **System Validation**:
   - `python manage.py check` (0 issues).
   - `python manage.py makemigrations --check` (0 pending migrations).
   - Record actual test output in `TEST_OUTPUT.md`.
