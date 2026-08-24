# Technical Research & Architecture Decisions: AI-Assisted Box Selection System

**Feature**: `001-box-selection-system`
**Date**: 2026-08-24
**Status**: Completed

---

## 1. Packing & Orientation Algorithm

### Decision
Implement deterministic 6-axis orthogonal rotation and 1D orthogonal bounding stack packing in `warehouse/packing.py`.

### Mathematical Formulation
1. **Rotational Permutations**:
   Given product dimensions $(l, w, h)$, the 6 orthogonal orientations are:
   $$\mathcal{O}(l, w, h) = \{(l, w, h), (l, h, w), (w, l, h), (w, h, l), (h, l, w), (h, w, l)\}$$
   Permutations with duplicate dimension tuples (e.g. cubes $(10, 10, 10)$ or square faces $(10, 10, 20)$) are deduplicated into a unique set $|\mathcal{O}| \le 6$.

2. **Single-SKU Multi-Quantity Stacking**:
   For quantity $Q$ of product $(l, w, h)$, the item can be stacked along its length, width, or height:
   $$\mathcal{S}(l, w, h, Q) = \{(Q \cdot l, w, h), (l, Q \cdot w, h), (l, w, Q \cdot h)\}$$
   Each stacked bounding shape $S \in \mathcal{S}$ is then evaluated across all orientation permutations $\mathcal{O}(S)$ against candidate box internal dimensions $(L_{box}, W_{box}, H_{box})$.

3. **Multi-SKU Order Bounding**:
   For multi-product orders, calculate the composite bounding dimensions across primary alignment axes and sum the individual item volumes/weights to verify physical feasibility before testing candidate alignments.

4. **Containment Condition**:
   A bounding shape $(l_s, w_s, h_s)$ fits in box $(L_{box}, W_{box}, H_{box})$ if and only if:
   $$l_s \le L_{box} \quad \land \quad w_s \le W_{box} \quad \land \quad h_s \le H_{box}$$

### Rationale
- 100% deterministic, reproducible, and verifiable.
- $O(1)$ computation time per box candidate.
- Accurately models real warehouse packing for common orders without introducing NP-hard 3D heuristic packing libraries.

### Alternatives Considered
- *Arbitrary 3D Bin Packing Library (e.g., py3dbp)*: Rejected due to non-deterministic heuristics, black-box placement bugs, and external dependency violations.
- *Simple Volume-Only Summation*: Rejected because total volume ignores rigid dimensional constraints (e.g., a 50cm rod fits into a 10×10×10 box by volume, but physically protrudes).

---

## 2. Box Ranking & Tie-Breaking

### Decision
Rank eligible candidate boxes via a 4-tier lexicographical key:
1. **Feasibility**: `is_weight_valid AND is_dimension_valid` (Boolean True first).
2. **Usable Volume**: $V_{box} = L_{box} \times W_{box} \times H_{box}$ in $\text{cm}^3$ (Ascending - smallest volume first).
3. **Unit Cost**: $\text{Cost}_{box}$ (Ascending - lowest cost first).
4. **Deterministic Identifier**: `(name, id)` (Ascending alphabetical/numeric sort).

### Rationale
- Minimizes dimensional weight surcharges and packaging void-fill material.
- Minimizes box procurement expenditure when volumes are equivalent.
- Guarantees 100% deterministic, testable output across Python versions and database engines.

---

## 3. Architecture & Separation of Concerns

### Decision
Adopt standard, idiomatic Django architecture:
- `warehouse/models.py`: Persistent database entities (`Product`, `ShippingBox`, `Order`, `OrderItem`).
- `warehouse/packing.py`: Pure domain calculation functions and dataclasses (`PackageItem`, `BoxCandidate`, `FitResult`, `RecommendationResult`). Pure Python with zero database dependencies for instant unit testability.
- `warehouse/forms.py`: Django Forms for order creation, product selection, and numerical validation.
- `warehouse/views.py`: Request orchestration and template context delivery.
- `warehouse/admin.py`: Django Admin configuration for catalog and order inspection.
- `warehouse/templates/`: Django HTML templates with high-contrast, warehouse-tailored styling.

### Rationale
- Prevents bloat: No unrequested service layers, serializer hierarchies, or repository wrappers.
- Testing ergonomics: `packing.py` can be tested in isolation with simple unit tests; views and models are tested via standard Django test tools.

---

## 4. Input & Boundary Validation

### Decision
Enforce strict boundary validation at model and form levels:
- Dimensions ($L, W, H$) and weights ($W$): `DecimalField` with `MinValueValidator(Decimal('0.01'))`.
- Quantities ($Q$): `IntegerField` with `MinValueValidator(1)`.
- Box Cost: `DecimalField` with `MinValueValidator(Decimal('0.00'))`.
- Empty order submission: Form validation error (`ValidationError("Order must contain at least one item.")`).

---

## 5. Security & Invariants

### Decision
- CSRF middleware enabled on all form POST requests.
- Django `SECRET_KEY` loaded from environment or local development fallback.
- `DEBUG = False` configurable via settings for production verification.
- Zero raw SQL; utilize Django ORM queries.
