# Feature Specification: AI-Assisted Box Selection System

**Feature Branch**: `001-box-selection-system`

**Created**: 2026-08-24

**Status**: Draft

**Input**: User description: "Build a small web-based warehouse box selection system for an ecommerce platform. Given an order containing products, recommend the most suitable shipping box based on product dimensions, quantities, total weight, box internal dimensions, maximum supported weight, and box cost."

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Single Product Order Recommendation (Priority: P1)

A warehouse staff member opens the application, creates an order with a single product and quantity, and requests a shipping box recommendation. The system validates the inputs, evaluates all candidate shipping boxes across all 6 orthogonal rotations, checks maximum weight limits, and recommends the optimal box with a transparent explanation of why it was chosen.

**Why this priority**: Core value proposition of the system. Without single-item deterministic fitting, rotation, weight checks, and volume-cost ranking, the application has zero operational utility.

**Independent Test**: Can be tested end-to-end by entering a product with known dimensions/weight, receiving the exact predicted box (smallest volume, cost tie-breaker), and confirming the step-by-step fit explanation.

**Acceptance Scenarios**:
1. **Given** a product measuring `20 × 10 × 5 cm` weighing `1.5 kg` and candidate boxes `A (25 × 15 × 10 cm, max 5 kg, $2.00)` and `B (30 × 20 × 15 cm, max 10 kg, $3.50)`, **When** staff requests a recommendation for quantity `1`, **Then** the system recommends Box `A` with an explanation stating that Box `A` has the smallest volume (`3750 cm³` vs `9000 cm³`) and supports the order weight (`1.5 kg <= 5.0 kg`).
2. **Given** a product measuring `25 × 10 × 5 cm` and a box with internal dimensions `12 × 28 × 8 cm`, **When** staff requests a recommendation, **Then** the system identifies that the product fits under rotation `(W, L, H) -> (10, 25, 5) <= (12, 28, 8)` and marks the box as physically valid.
3. **Given** a product whose dimensions fit within a box but whose weight (`6.0 kg`) exceeds the box capacity (`5.0 kg`), **When** staff requests a recommendation, **Then** the system rejects that box due to weight capacity violation.

---

### User Story 2 - Multi-Quantity & Multi-Product Order Packing (Priority: P2)

Warehouse staff creates an order containing multiple quantities of a product or multiple distinct products. The system accumulates total order weight, applies a deterministic rectangular bounding packing evaluation across allowable orthogonal orientations, rejects boxes that cannot contain the combined stack/bounding volume or exceed weight capacity, and recommends the optimal box.

**Why this priority**: Most real ecommerce orders contain multiple items or quantities.

**Independent Test**: Can be tested by creating an order with `3` units of Product X or `1` unit of Product X + `2` units of Product Y, verifying total weight computation (`sum(weight * quantity)`), confirming that the computed bounding stack fits inside the recommended box, and verifying that undersized/under-weight boxes are rejected.

**Acceptance Scenarios**:
1. **Given** `3` units of a product `10 × 10 × 10 cm` weighing `1.0 kg` each, **When** staff requests a recommendation, **Then** total order weight is calculated as `3.0 kg`, candidate boxes are evaluated against the stacked bounding dimensions (`30 × 10 × 10 cm` or equivalent rotations), and the smallest valid box supporting `>= 3.0 kg` is recommended.
2. **Given** multiple distinct items whose combined total weight exceeds a box's weight capacity, **When** staff requests a recommendation, **Then** the box is excluded from candidates with a specific reason: `Total weight (X kg) exceeds maximum capacity (Y kg)`.

---

### User Story 3 - No Suitable Box & Boundary State Handling (Priority: P3)

When an order cannot physically fit into any available shipping box, exceeds all box weight capacities, or when the box catalog is empty, the system displays a clear, explanatory "No Suitable Box Found" state detailing the rejection reason for each evaluated box.

**Why this priority**: Warehouse staff need actionable guidance when an order requires manual packing, split shipments, or custom freight packaging.

**Independent Test**: Can be tested with an oversized product (`200 × 200 × 200 cm`) or overweight order (`100 kg`), verifying that the UI displays a clear "No Suitable Box Found" message with diagnostic reasons for every registered box.

**Acceptance Scenarios**:
1. **Given** an order where the product dimensions exceed all available boxes in all 6 orientations, **When** staff requests a recommendation, **Then** the system displays a "No Suitable Box Available" message and shows the specific dimension mismatches for each candidate box.
2. **Given** an empty box catalog, **When** an order is submitted, **Then** the system informs staff that no shipping boxes are registered in the warehouse catalog.

---

### User Story 4 - Catalog & Order Management via Admin (Priority: P4)

Warehouse managers can view, create, edit, and delete Products (dimensions, weight, SKU) and Shipping Boxes (internal dimensions, max weight, cost) through a secure administrative interface.

**Why this priority**: Operational data changes regularly as new packaging sizes or products are introduced.

**Independent Test**: Can be tested by adding a new shipping box in Django admin and immediately seeing it participate in recommendation calculations on the warehouse frontend.

**Acceptance Scenarios**:
1. **Given** a manager logged into the administration console, **When** they add a new box `Small Heavy (15 × 15 × 15 cm, max 20 kg, $1.80)`, **Then** the box is persisted and becomes eligible for subsequent order recommendations.
2. **Given** a product entry in admin, **When** invalid data (negative dimensions or negative weight) is entered, **Then** the form prevents saving and highlights the invalid field.

---

### Edge Cases

- **Zero or Negative Quantity**: Reject order submission with a clear validation error ("Quantity must be greater than zero").
- **Non-positive Dimensions / Weights**: Forms reject values `<= 0` on product and box creation.
- **Identical Dimensions on Multiple Axes (Cubes / Square Faces)**: System deduplicates orientation permutations to prevent redundant evaluation cycles.
- **Exact Volume & Cost Ties**: When two boxes have identical usable volume and identical cost, the system breaks ties deterministically by box name or identifier alphabetical order.
- **Empty Order Submission**: Submitting an order without any selected products produces an actionable validation prompt rather than a crash.
- **Extreme Scale Orders**: System handles large quantities safely without arithmetic overflow or infinite loops.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST maintain product records with `name`, `SKU`, `length` (cm), `width` (cm), `height` (cm), and `weight` (kg).
- **FR-002**: System MUST maintain shipping box records with `name`, `internal_length` (cm), `internal_width` (cm), `internal_height` (cm), `max_weight` (kg), and `cost` (currency/dollars).
- **FR-003**: System MUST provide a warehouse web interface where staff can select products, enter quantities, and create an order.
- **FR-004**: System MUST calculate total order weight strictly as `sum(product_weight * quantity)`.
- **FR-005**: System MUST evaluate physical fit by testing rectangular cuboids across all 6 orthogonal orientations: `(L,W,H)`, `(L,H,W)`, `(W,L,H)`, `(W,H,L)`, `(H,L,W)`, and `(H,W,L)`.
- **FR-006**: For multi-quantity / multi-item orders, the system MUST use a deterministic bounding packing model (stacking along viable alignment axes) and test if the resulting composite dimensions fit within the candidate box in at least one orientation.
- **FR-007**: System MUST eliminate any box whose `max_weight` is less than the total order weight.
- **FR-008**: System MUST eliminate any box whose internal dimensions cannot contain the product(s) in any orientation.
- **FR-009**: System MUST rank all valid candidate boxes according to:
  1. Smallest internal volume (`length * width * height`).
  2. Lowest unit cost (secondary tie-breaker).
  3. Deterministic box identifier/name sort (tertiary tie-breaker).
- **FR-010**: System MUST display the top-ranked recommended box clearly in the UI.
- **FR-011**: System MUST display a human-readable explanation of why the recommended box was selected (e.g., volume efficiency, orientation used, weight headroom).
- **FR-012**: If no boxes are eligible, the system MUST display an explicit "No Suitable Box Found" notification and provide itemized rejection reasons for rejected boxes (dimension overflow, weight limit overflow).
- **FR-013**: System MUST reject non-positive dimensions, non-positive weights, non-positive quantities, and negative costs at the validation boundary.
- **FR-014**: System MUST provide Django Admin access to manage Products, Shipping Boxes, and view recorded Orders.
- **FR-015**: The core recommendation algorithm MUST be completely deterministic and execute without any external LLM or network API dependency.

---

### Key Entities

- **Product**:
  - `name`: string (human-readable product name)
  - `sku`: string (unique stock keeping unit)
  - `length`: decimal > 0 (cm)
  - `width`: decimal > 0 (cm)
  - `height`: decimal > 0 (cm)
  - `weight`: decimal > 0 (kg)
- **ShippingBox**:
  - `name`: string (box type name, e.g., "Box 1 - Small", "Medium Mailer")
  - `length`: decimal > 0 (cm, internal usable length)
  - `width`: decimal > 0 (cm, internal usable width)
  - `height`: decimal > 0 (cm, internal usable height)
  - `max_weight`: decimal > 0 (kg, maximum supported payload weight)
  - `cost`: decimal >= 0 (monetary cost per unit)
  - Derived attribute: `volume` = `length * width * height`
- **Order**:
  - `created_at`: datetime
  - `status`: string/choice
- **OrderItem**:
  - `order`: ForeignKey -> Order
  - `product`: ForeignKey -> Product
  - `quantity`: integer >= 1
- **RecommendationResult**:
  - `recommended_box`: ShippingBox (nullable if no fit)
  - `is_fit_found`: boolean
  - `total_weight`: decimal (kg)
  - `explanation`: string
  - `candidate_evaluations`: list of box evaluation details (box name, status: valid/rejected, reason, volume, cost)

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Warehouse staff can configure an order and receive an optimal box recommendation in under 3 clicks from the main screen.
- **SC-002**: 100% of recommendation decisions are deterministic, reproducible, and verifiable against exact mathematical rules.
- **SC-003**: 100% of invalid inputs (negative values, zero quantities, empty orders) produce actionable inline error feedback without server crashes (500 errors).
- **SC-004**: Recommendation computation completes in under 50 milliseconds for typical warehouse catalogs (100+ boxes).
- **SC-005**: 100% of business rules (fit, rotation, weight check, ranking, tie-breaking, rejection logging) are verified by passing automated unit/integration tests.
- **SC-006**: A new developer can set up, migrate, test, and run the project locally within 5 minutes following the README.

---

## Assumptions

- **Measurement Units**: Standardized to centimeters (cm) for linear dimensions, kilograms (kg) for weight, and local currency (e.g., USD/$) for box costs.
- **Product Rigidness**: Products are rigid rectangular cuboids that do not deform or compress under packing.
- **Internal Usable Dimensions**: Box dimensions represent internal usable space; wall thickness is pre-factored into the box catalog measurements.
- **Packing Model**: Multi-item / multi-quantity orders utilize orthogonal bounding stack packing (aligning items along primary axes to form a composite bounding cuboid). Complex irregular geometric interlocking is out of scope.
- **Authentication**: Warehouse staff UI operates without forced login for local warehouse station speed, while administrative management is secured behind Django Admin authentication.
