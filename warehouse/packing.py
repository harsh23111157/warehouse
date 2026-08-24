from dataclasses import dataclass
from decimal import Decimal
import itertools
from typing import List, Optional, Tuple


@dataclass(frozen=True)
class ItemSpec:
    """
    Immutable specification of a physical product item and its ordered quantity.
    Dimensions in cm; weight in kg; quantity >= 1.
    """
    sku: str
    name: str
    length: Decimal
    width: Decimal
    height: Decimal
    weight: Decimal
    quantity: int

    def __post_init__(self):
        if self.length <= Decimal("0.00"):
            raise ValueError(f"Item {self.sku} length must be > 0 (got {self.length}).")
        if self.width <= Decimal("0.00"):
            raise ValueError(f"Item {self.sku} width must be > 0 (got {self.width}).")
        if self.height <= Decimal("0.00"):
            raise ValueError(f"Item {self.sku} height must be > 0 (got {self.height}).")
        if self.weight <= Decimal("0.000"):
            raise ValueError(f"Item {self.sku} weight must be > 0 (got {self.weight}).")
        if self.quantity < 1:
            raise ValueError(f"Item {self.sku} quantity must be >= 1 (got {self.quantity}).")

    @property
    def unit_volume(self) -> Decimal:
        return self.length * self.width * self.height

    @property
    def total_weight(self) -> Decimal:
        return self.weight * Decimal(self.quantity)


@dataclass(frozen=True)
class BoxSpec:
    """
    Immutable specification of an available warehouse shipping box.
    Internal dimensions in cm; max payload weight in kg; unit cost in $.
    """
    id: int
    name: str
    length: Decimal
    width: Decimal
    height: Decimal
    max_weight: Decimal
    cost: Decimal

    def __post_init__(self):
        if self.length <= Decimal("0.00"):
            raise ValueError(f"Box {self.name} length must be > 0 (got {self.length}).")
        if self.width <= Decimal("0.00"):
            raise ValueError(f"Box {self.name} width must be > 0 (got {self.width}).")
        if self.height <= Decimal("0.00"):
            raise ValueError(f"Box {self.name} height must be > 0 (got {self.height}).")
        if self.max_weight <= Decimal("0.000"):
            raise ValueError(f"Box {self.name} max_weight must be > 0 (got {self.max_weight}).")
        if self.cost < Decimal("0.00"):
            raise ValueError(f"Box {self.name} cost cannot be negative (got {self.cost}).")

    @property
    def volume(self) -> Decimal:
        return self.length * self.width * self.height

    @property
    def dimensions_tuple(self) -> Tuple[Decimal, Decimal, Decimal]:
        return (self.length, self.width, self.height)


@dataclass(frozen=True)
class BoxRejection:
    """
    Diagnostic explanation for why a candidate box was disqualified.
    """
    box: BoxSpec
    reason: str  # "DIMENSIONS", "WEIGHT", "DIMENSIONS_AND_WEIGHT"
    message: str


@dataclass(frozen=True)
class BoxEvaluation:
    """
    Comprehensive evaluation of a single box candidate against an order.
    """
    box: BoxSpec
    is_valid: bool
    is_weight_valid: bool
    is_dimension_valid: bool
    rejection_reasons: List[str]
    tested_orientation: Optional[Tuple[Decimal, Decimal, Decimal]]
    volume: Decimal
    cost: Decimal


@dataclass(frozen=True)
class RecommendationResult:
    """
    Explainable result containing the optimal recommended box or structured no-fit diagnostics.
    """
    is_fit_found: bool
    recommended_box: Optional[BoxSpec]
    explanation: str
    total_weight: Decimal
    total_items: int
    evaluations: List[BoxEvaluation]
    rejected_boxes: List[BoxRejection]


def get_orthogonal_rotations(
    length: Decimal, width: Decimal, height: Decimal
) -> List[Tuple[Decimal, Decimal, Decimal]]:
    """
    Generates all unique 3D orthogonal axis-aligned orientation permutations.
    Deduplicates identical dimension tuples (e.g. for cubes or square cross-sections)
    while preserving deterministic ordering.
    """
    perms = list(itertools.permutations([length, width, height], 3))
    unique_rotations: List[Tuple[Decimal, Decimal, Decimal]] = []
    seen = set()
    for rot in perms:
        if rot not in seen:
            seen.add(rot)
            unique_rotations.append(rot)
    return unique_rotations


def calculate_total_weight(items: List[ItemSpec]) -> Decimal:
    """Calculates exact total order weight as sum(weight * quantity)."""
    return sum((item.total_weight for item in items), Decimal("0.000"))


def can_fit_single_cuboid_in_box(
    cuboid: Tuple[Decimal, Decimal, Decimal],
    box_dims: Tuple[Decimal, Decimal, Decimal]
) -> Tuple[bool, Optional[Tuple[Decimal, Decimal, Decimal]]]:
    """
    Evaluates if a single rectangular cuboid (l, w, h) fits inside box dimensions (L, W, H)
    in at least one orthogonal rotation using inclusive inequality (<=).
    """
    box_l, box_w, box_h = box_dims
    rotations = get_orthogonal_rotations(cuboid[0], cuboid[1], cuboid[2])
    for rot_l, rot_w, rot_h in rotations:
        if rot_l <= box_l and rot_w <= box_w and rot_h <= box_h:
            return True, (rot_l, rot_w, rot_h)
    return False, None


def generate_candidate_stack_shapes(items: List[ItemSpec]) -> List[Tuple[Decimal, Decimal, Decimal]]:
    """
    Generates candidate composite rectangular bounding shapes for the order.
    - Single item, Q=1: Returns [(L, W, H)]
    - Single item, Q>1: Returns 1D orthogonal stacks along length (Q*L, W, H),
      width (L, Q*W, H), and height (L, W, Q*H).
    - Multi-item (heterogeneous): Returns composite bounding stacks aggregated
      along primary alignment axes (stack along H, stack along L, stack along W).
    """
    if len(items) == 1:
        item = items[0]
        q = Decimal(item.quantity)
        if item.quantity == 1:
            return [(item.length, item.width, item.height)]
        # 1D orthogonal stacking configurations for identical items
        return [
            (item.length * q, item.width, item.height),
            (item.length, item.width * q, item.height),
            (item.length, item.width, item.height * q),
        ]

    # Multi-product packing configurations
    # Stack configuration 1: Stack along height (e.g. books on top of each other)
    h_stack_l = max(item.length for item in items)
    h_stack_w = max(item.width for item in items)
    h_stack_h = sum((item.height * Decimal(item.quantity) for item in items), Decimal("0.00"))

    # Stack configuration 2: Stack along length (e.g. items lined up in length)
    l_stack_l = sum((item.length * Decimal(item.quantity) for item in items), Decimal("0.00"))
    l_stack_w = max(item.width for item in items)
    l_stack_h = max(item.height for item in items)

    # Stack configuration 3: Stack along width (e.g. items side by side)
    w_stack_l = max(item.length for item in items)
    w_stack_w = sum((item.width * Decimal(item.quantity) for item in items), Decimal("0.00"))
    w_stack_h = max(item.height for item in items)

    return [
        (h_stack_l, h_stack_w, h_stack_h),
        (l_stack_l, l_stack_w, l_stack_h),
        (w_stack_l, w_stack_w, w_stack_h),
    ]


def can_fit_items_in_box(
    items: List[ItemSpec],
    box: BoxSpec
) -> Tuple[bool, Optional[Tuple[Decimal, Decimal, Decimal]], Optional[str]]:
    """
    Determines if the order items can physically fit inside the box internal dimensions.
    Returns: (is_fit, matching_box_orientation, failure_message)
    """
    candidate_shapes = generate_candidate_stack_shapes(items)
    box_dims = box.dimensions_tuple

    for shape in candidate_shapes:
        fits, matching_rot = can_fit_single_cuboid_in_box(shape, box_dims)
        if fits:
            return True, matching_rot, None

    # Check for individual item exceeding box dimensions
    for item in items:
        fits_alone, _ = can_fit_single_cuboid_in_box((item.length, item.width, item.height), box_dims)
        if not fits_alone:
            return (
                False,
                None,
                f"Product '{item.name}' ({item.length}x{item.width}x{item.height}cm) exceeds box internal dimensions in all orientations."
            )

    return (
        False,
        None,
        f"Order packing stack exceeds internal dimensions ({box.length}x{box.width}x{box.height}cm) in all orientations."
    )


def evaluate_box(
    box: BoxSpec,
    items: List[ItemSpec],
    total_weight: Decimal
) -> Tuple[BoxEvaluation, Optional[BoxRejection]]:
    """
    Evaluates a single box against an order, returning structured evaluation and rejection details.
    """
    reasons: List[str] = []
    is_weight_valid = True
    is_dimension_valid = True

    # 1. Weight capacity check
    if total_weight > box.max_weight:
        is_weight_valid = False
        reasons.append(
            f"Total order weight ({total_weight:.3f} kg) exceeds maximum weight capacity ({box.max_weight:.3f} kg)."
        )

    # 2. Dimensional fit check
    dim_fit, matching_orientation, dim_message = can_fit_items_in_box(items, box)
    if not dim_fit:
        is_dimension_valid = False
        reasons.append(dim_message or "Dimensions exceeded.")

    is_valid = is_weight_valid and is_dimension_valid

    rejection: Optional[BoxRejection] = None
    if not is_valid:
        if not is_weight_valid and not is_dimension_valid:
            rejection_category = "DIMENSIONS_AND_WEIGHT"
        elif not is_weight_valid:
            rejection_category = "WEIGHT"
        else:
            rejection_category = "DIMENSIONS"

        rejection = BoxRejection(
            box=box,
            reason=rejection_category,
            message="; ".join(reasons)
        )

    evaluation = BoxEvaluation(
        box=box,
        is_valid=is_valid,
        is_weight_valid=is_weight_valid,
        is_dimension_valid=is_dimension_valid,
        rejection_reasons=reasons,
        tested_orientation=matching_orientation,
        volume=box.volume,
        cost=box.cost
    )

    return evaluation, rejection


def recommend_box(
    items: List[ItemSpec],
    available_boxes: List[BoxSpec]
) -> RecommendationResult:
    """
    Deterministic box recommendation engine.
    1. Validates inputs.
    2. Calculates total weight.
    3. Evaluates all candidate boxes across 6-axis orthogonal rotations and bounding stacks.
    4. Filters invalid boxes (weight or dimension violations).
    5. Ranks valid boxes by:
       - Usable internal volume ascending (smallest volume preferred)
       - Unit cost ascending (cheaper box tie-breaker)
       - Box name ascending (alphabetical tie-breaker)
       - Box ID ascending (stable final tie-breaker)
    6. Returns RecommendationResult with winner and itemized rejection diagnostics.
    """
    if not items:
        raise ValueError("Order must contain at least one item.")

    total_weight = calculate_total_weight(items)
    total_items = sum(item.quantity for item in items)

    if not available_boxes:
        return RecommendationResult(
            is_fit_found=False,
            recommended_box=None,
            explanation="No shipping boxes are registered in the warehouse catalog.",
            total_weight=total_weight,
            total_items=total_items,
            evaluations=[],
            rejected_boxes=[]
        )

    evaluations: List[BoxEvaluation] = []
    rejected_boxes: List[BoxRejection] = []
    valid_evaluations: List[BoxEvaluation] = []

    for box in available_boxes:
        evaluation, rejection = evaluate_box(box, items, total_weight)
        evaluations.append(evaluation)
        if rejection:
            rejected_boxes.append(rejection)
        if evaluation.is_valid:
            valid_evaluations.append(evaluation)

    if not valid_evaluations:
        # Generate diagnostic explanation of why no box fits
        weight_failures = [r for r in rejected_boxes if r.reason == "WEIGHT"]
        dim_failures = [r for r in rejected_boxes if r.reason == "DIMENSIONS"]

        if len(weight_failures) == len(rejected_boxes):
            explanation = (
                f"No suitable box found: Total order weight ({total_weight:.3f} kg) "
                f"exceeds the maximum payload capacity of all {len(available_boxes)} registered boxes."
            )
        elif len(dim_failures) == len(rejected_boxes):
            explanation = (
                f"No suitable box found: Order physical dimensions exceed the internal "
                f"usable dimensions of all {len(available_boxes)} registered boxes in all orientations."
            )
        else:
            explanation = (
                f"No suitable box found: None of the {len(available_boxes)} registered boxes meet "
                f"both the dimensional fit and weight capacity requirements for this order."
            )

        return RecommendationResult(
            is_fit_found=False,
            recommended_box=None,
            explanation=explanation,
            total_weight=total_weight,
            total_items=total_items,
            evaluations=evaluations,
            rejected_boxes=rejected_boxes
        )

    # Deterministic ranking:
    # 1. Usable internal volume (ascending)
    # 2. Unit cost (ascending)
    # 3. Box name (ascending)
    # 4. Box ID (ascending)
    valid_evaluations.sort(
        key=lambda e: (e.box.volume, e.box.cost, e.box.name, e.box.id)
    )

    winner_eval = valid_evaluations[0]
    winner_box = winner_eval.box
    orientation_str = (
        f"{winner_eval.tested_orientation[0]:.1f}x{winner_eval.tested_orientation[1]:.1f}x{winner_eval.tested_orientation[2]:.1f} cm"
        if winner_eval.tested_orientation else "standard orientation"
    )

    explanation = (
        f"Selected '{winner_box.name}' because it is the smallest box ({winner_box.volume:,.2f} cm³) "
        f"capable of holding the order items (packed as {orientation_str}) and supports the total "
        f"order weight of {total_weight:.3f} kg (capacity: {winner_box.max_weight:.3f} kg) at unit cost ${winner_box.cost:.2f}."
    )

    return RecommendationResult(
        is_fit_found=True,
        recommended_box=winner_box,
        explanation=explanation,
        total_weight=total_weight,
        total_items=total_items,
        evaluations=evaluations,
        rejected_boxes=rejected_boxes
    )
