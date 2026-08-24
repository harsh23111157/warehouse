from decimal import Decimal
from django.test import TestCase
from warehouse.packing import (
    BoxSpec,
    ItemSpec,
    RecommendationResult,
    get_orthogonal_rotations,
    recommend_box,
)


class PackingEngineTests(TestCase):
    """
    Exhaustive unit test suite for the deterministic box selection domain logic.
    """

    def setUp(self):
        # Standard reusable box inventory
        self.box_small = BoxSpec(
            id=1,
            name="Box 1 - Small Mailer",
            length=Decimal("20.00"),
            width=Decimal("15.00"),
            height=Decimal("10.00"),
            max_weight=Decimal("3.000"),
            cost=Decimal("1.50")  # Volume = 3,000 cm³
        )
        self.box_medium = BoxSpec(
            id=2,
            name="Box 2 - Medium Carton",
            length=Decimal("30.00"),
            width=Decimal("20.00"),
            height=Decimal("15.00"),
            max_weight=Decimal("7.000"),
            cost=Decimal("2.50")  # Volume = 9,000 cm³
        )
        self.box_large = BoxSpec(
            id=3,
            name="Box 3 - Large Carton",
            length=Decimal("45.00"),
            width=Decimal("35.00"),
            height=Decimal("25.00"),
            max_weight=Decimal("15.000"),
            cost=Decimal("4.00")  # Volume = 39,375 cm³
        )
        self.all_boxes = [self.box_small, self.box_medium, self.box_large]

    def test_product_fits_without_rotation(self):
        """Item whose standard orientation fits within box is recommended."""
        item = ItemSpec(
            sku="SKU-BOOK",
            name="Novel",
            length=Decimal("18.00"),
            width=Decimal("12.00"),
            height=Decimal("3.00"),
            weight=Decimal("0.500"),
            quantity=1
        )
        result = recommend_box([item], self.all_boxes)
        self.assertTrue(result.is_fit_found)
        self.assertEqual(result.recommended_box.id, self.box_small.id)
        self.assertEqual(result.total_weight, Decimal("0.500"))
        self.assertIn("Selected 'Box 1 - Small Mailer'", result.explanation)

    def test_product_fits_after_rotation(self):
        """Item fitting only when rotated across orthogonal axes is recommended."""
        # Standard: 12x25x4 does NOT fit in Box Small (20x15x10) because length 25 > 20.
        # Rotated to (25, 12, 4) fails, but in Box Medium (30x20x15), (25x12x4) fits.
        # Let's test a box (25x15x10) and item (10x24x8) -> rotated to (24x10x8) fits.
        custom_box = BoxSpec(
            id=10,
            name="Custom Rectangular",
            length=Decimal("25.00"),
            width=Decimal("15.00"),
            height=Decimal("10.00"),
            max_weight=Decimal("5.000"),
            cost=Decimal("2.00")
        )
        item = ItemSpec(
            sku="SKU-TALL",
            name="Tall Cylinder Package",
            length=Decimal("8.00"),
            width=Decimal("24.00"),
            height=Decimal("10.00"),
            weight=Decimal("1.000"),
            quantity=1
        )
        result = recommend_box([item], [custom_box])
        self.assertTrue(result.is_fit_found)
        self.assertEqual(result.recommended_box.id, custom_box.id)
        self.assertEqual(len(result.rejected_boxes), 0)

    def test_product_does_not_fit_any_dimension(self):
        """Oversized item exceeding all dimensions in all rotations is rejected."""
        oversized = ItemSpec(
            sku="SKU-DESK",
            name="Large Monitor",
            length=Decimal("80.00"),
            width=Decimal("60.00"),
            height=Decimal("20.00"),
            weight=Decimal("2.000"),  # Weight fits all boxes (< 3kg), so pure DIMENSIONS failure
            quantity=1
        )
        result = recommend_box([oversized], self.all_boxes)
        self.assertFalse(result.is_fit_found)
        self.assertIsNone(result.recommended_box)
        self.assertEqual(len(result.rejected_boxes), 3)
        self.assertTrue(all(r.reason == "DIMENSIONS" for r in result.rejected_boxes))
        self.assertIn("Order physical dimensions exceed the internal usable dimensions", result.explanation)

    def test_exact_dimension_boundary_is_valid(self):
        """Item whose dimensions exactly match box internal dimensions must fit (inclusive <=)."""
        exact_item = ItemSpec(
            sku="SKU-EXACT",
            name="Exact Fit Box Item",
            length=Decimal("20.00"),
            width=Decimal("15.00"),
            height=Decimal("10.00"),
            weight=Decimal("2.000"),
            quantity=1
        )
        result = recommend_box([exact_item], [self.box_small])
        self.assertTrue(result.is_fit_found)
        self.assertEqual(result.recommended_box.id, self.box_small.id)

    def test_rotation_symmetry_deduplication(self):
        """Cubic and square items have deduplicated rotation sets."""
        cube_rotations = get_orthogonal_rotations(Decimal("10.00"), Decimal("10.00"), Decimal("10.00"))
        self.assertEqual(len(cube_rotations), 1)
        self.assertEqual(cube_rotations[0], (Decimal("10.00"), Decimal("10.00"), Decimal("10.00")))

        square_face_rotations = get_orthogonal_rotations(Decimal("10.00"), Decimal("10.00"), Decimal("20.00"))
        self.assertEqual(len(square_face_rotations), 3)

        asymm_rotations = get_orthogonal_rotations(Decimal("10.00"), Decimal("20.00"), Decimal("30.00"))
        self.assertEqual(len(asymm_rotations), 6)

    def test_order_weight_exactly_at_capacity_is_valid(self):
        """Order weight exactly equal to box max_weight must be accepted."""
        heavy_item = ItemSpec(
            sku="SKU-WEIGHT-EXACT",
            name="Exact Weight Item",
            length=Decimal("10.00"),
            width=Decimal("10.00"),
            height=Decimal("10.00"),
            weight=Decimal("3.000"),  # box_small max_weight is 3.000
            quantity=1
        )
        result = recommend_box([heavy_item], [self.box_small])
        self.assertTrue(result.is_fit_found)
        self.assertEqual(result.recommended_box.id, self.box_small.id)

    def test_order_over_capacity_is_rejected(self):
        """Order exceeding box maximum payload weight is rejected with WEIGHT reason."""
        overweight = ItemSpec(
            sku="SKU-LEAD",
            name="Lead Ingot",
            length=Decimal("10.00"),
            width=Decimal("10.00"),
            height=Decimal("5.00"),
            weight=Decimal("3.500"),  # > box_small (3.0 kg), fits box_medium (7.0 kg)
            quantity=1
        )
        result = recommend_box([overweight], self.all_boxes)
        self.assertTrue(result.is_fit_found)
        self.assertEqual(result.recommended_box.id, self.box_medium.id)
        # Verify Box Small was rejected due to WEIGHT
        small_rejection = [r for r in result.rejected_boxes if r.box.id == self.box_small.id][0]
        self.assertEqual(small_rejection.reason, "WEIGHT")
        self.assertIn("exceeds maximum weight capacity", small_rejection.message)

    def test_multiple_quantity_weight_and_stacking(self):
        """Multiple quantities calculate total weight and 1D orthogonal bounding stack."""
        # Item: 10x10x4 cm, 0.8 kg. Quantity: 3
        # Total weight: 2.4 kg (fits in Box Small max 3.0 kg).
        # Stacked along height: 10x10x12 -> doesn't fit in height 10 if unrotated,
        # but rotated (12x10x10) fits in Box Small (20x15x10).
        book = ItemSpec(
            sku="SKU-STACK-BOOK",
            name="Textbook",
            length=Decimal("10.00"),
            width=Decimal("10.00"),
            height=Decimal("4.00"),
            weight=Decimal("0.800"),
            quantity=3
        )
        result = recommend_box([book], self.all_boxes)
        self.assertTrue(result.is_fit_found)
        self.assertEqual(result.total_weight, Decimal("2.400"))
        self.assertEqual(result.recommended_box.id, self.box_small.id)

    def test_multiple_items_heterogeneous_are_packed(self):
        """Heterogeneous multi-product orders calculate composite bounding dimensions."""
        p1 = ItemSpec(
            sku="SKU-MUG",
            name="Coffee Mug",
            length=Decimal("12.00"),
            width=Decimal("10.00"),
            height=Decimal("10.00"),
            weight=Decimal("0.400"),
            quantity=1
        )
        p2 = ItemSpec(
            sku="SKU-PLATE",
            name="Ceramic Plate",
            length=Decimal("18.00"),
            width=Decimal("18.00"),
            height=Decimal("3.00"),
            weight=Decimal("0.600"),
            quantity=1
        )
        # Combined weight: 1.0 kg.
        # Plate dimensions (18x18) exceed Box Small width (15.00).
        # Box Medium (30x20x15) accommodates both items.
        result = recommend_box([p1, p2], self.all_boxes)
        self.assertTrue(result.is_fit_found)
        self.assertEqual(result.recommended_box.id, self.box_medium.id)
        self.assertEqual(result.total_weight, Decimal("1.000"))

    def test_smallest_valid_box_is_selected(self):
        """System ranks valid boxes by volume and chooses the smallest suitable box."""
        # Both Box Small (3,000 cm³), Box Medium (9,000 cm³), Box Large (39,375 cm³) fit.
        item = ItemSpec(
            sku="SKU-SMALL",
            name="Phone Case",
            length=Decimal("15.00"),
            width=Decimal("8.00"),
            height=Decimal("2.00"),
            weight=Decimal("0.100"),
            quantity=1
        )
        result = recommend_box([item], self.all_boxes)
        self.assertTrue(result.is_fit_found)
        self.assertEqual(result.recommended_box.id, self.box_small.id)

    def test_cheaper_box_breaks_tie_for_equal_volumes(self):
        """When two boxes have identical usable volume, lowest unit cost wins."""
        box_a = BoxSpec(
            id=101,
            name="Box A - Expensive",
            length=Decimal("20.00"),
            width=Decimal("10.00"),
            height=Decimal("10.00"),
            max_weight=Decimal("5.000"),
            cost=Decimal("3.00")  # Volume = 2,000 cm³
        )
        box_b = BoxSpec(
            id=102,
            name="Box B - Economical",
            length=Decimal("20.00"),
            width=Decimal("10.00"),
            height=Decimal("10.00"),
            max_weight=Decimal("5.000"),
            cost=Decimal("1.80")  # Volume = 2,000 cm³
        )
        item = ItemSpec(
            sku="SKU-PEN",
            name="Pen Box",
            length=Decimal("15.00"),
            width=Decimal("5.00"),
            height=Decimal("2.00"),
            weight=Decimal("0.200"),
            quantity=1
        )
        result = recommend_box([item], [box_a, box_b])
        self.assertTrue(result.is_fit_found)
        self.assertEqual(result.recommended_box.id, box_b.id)
        self.assertEqual(result.recommended_box.name, "Box B - Economical")

    def test_stable_final_tie_break(self):
        """When volume and cost are identical, tie breaks deterministically by name / id."""
        box_alpha = BoxSpec(
            id=201,
            name="Alpha Box",
            length=Decimal("20.00"),
            width=Decimal("10.00"),
            height=Decimal("10.00"),
            max_weight=Decimal("5.000"),
            cost=Decimal("2.00")
        )
        box_beta = BoxSpec(
            id=202,
            name="Beta Box",
            length=Decimal("20.00"),
            width=Decimal("10.00"),
            height=Decimal("10.00"),
            max_weight=Decimal("5.000"),
            cost=Decimal("2.00")
        )
        item = ItemSpec(
            sku="SKU-CARD",
            name="Card Deck",
            length=Decimal("10.00"),
            width=Decimal("5.00"),
            height=Decimal("2.00"),
            weight=Decimal("0.100"),
            quantity=1
        )
        # Test order [beta, alpha] -> alpha must still win
        result = recommend_box([item], [box_beta, box_alpha])
        self.assertTrue(result.is_fit_found)
        self.assertEqual(result.recommended_box.name, "Alpha Box")

    def test_no_boxes_returns_no_fit(self):
        """Empty box catalog returns structured no-fit state."""
        item = ItemSpec(
            sku="SKU-TEST",
            name="Test Item",
            length=Decimal("10.00"),
            width=Decimal("10.00"),
            height=Decimal("10.00"),
            weight=Decimal("1.000"),
            quantity=1
        )
        result = recommend_box([item], [])
        self.assertFalse(result.is_fit_found)
        self.assertIsNone(result.recommended_box)
        self.assertIn("No shipping boxes are registered", result.explanation)

    def test_no_weight_fit_returns_diagnostic_explanation(self):
        """When all boxes fail due to weight, explanation mentions weight capacity."""
        heavy_item = ItemSpec(
            sku="SKU-ANVIL",
            name="Anvil",
            length=Decimal("20.00"),
            width=Decimal("10.00"),
            height=Decimal("10.00"),
            weight=Decimal("50.000"),  # Exceeds Box Large max (15 kg)
            quantity=1
        )
        result = recommend_box([heavy_item], self.all_boxes)
        self.assertFalse(result.is_fit_found)
        self.assertIn("exceeds the maximum payload capacity of all 3 registered boxes", result.explanation)
        self.assertEqual(len(result.rejected_boxes), 3)
        self.assertTrue(all(r.reason == "WEIGHT" for r in result.rejected_boxes))

    def test_invalid_domain_data_raises_value_error(self):
        """Non-positive dimensions, weights, quantities raise ValueError on ItemSpec / BoxSpec."""
        with self.assertRaises(ValueError):
            ItemSpec(
                sku="SKU-BAD",
                name="Bad",
                length=Decimal("0.00"),
                width=Decimal("10.00"),
                height=Decimal("10.00"),
                weight=Decimal("1.000"),
                quantity=1
            )
        with self.assertRaises(ValueError):
            ItemSpec(
                sku="SKU-BAD",
                name="Bad",
                length=Decimal("10.00"),
                width=Decimal("10.00"),
                height=Decimal("10.00"),
                weight=Decimal("1.000"),
                quantity=0
            )
        with self.assertRaises(ValueError):
            BoxSpec(
                id=1,
                name="Bad Box",
                length=Decimal("10.00"),
                width=Decimal("10.00"),
                height=Decimal("10.00"),
                max_weight=Decimal("1.000"),
                cost=Decimal("-1.00")
            )
        with self.assertRaises(ValueError):
            recommend_box([], self.all_boxes)

    def test_deterministic_repeated_result(self):
        """Calling recommendation 100 times returns identical winner and explanation."""
        item = ItemSpec(
            sku="SKU-REPEAT",
            name="Repeat Test Item",
            length=Decimal("22.00"),
            width=Decimal("14.00"),
            height=Decimal("8.00"),
            weight=Decimal("1.200"),
            quantity=2
        )
        first_result = recommend_box([item], self.all_boxes)
        for _ in range(100):
            subsequent_result = recommend_box([item], self.all_boxes)
            self.assertEqual(first_result.recommended_box.id, subsequent_result.recommended_box.id)
            self.assertEqual(first_result.explanation, subsequent_result.explanation)
            self.assertEqual(first_result.total_weight, subsequent_result.total_weight)

    def test_explainability_rejected_boxes_structure(self):
        """Verify rejected_boxes list contains structured diagnostics with reasons and messages."""
        item = ItemSpec(
            sku="SKU-MEDIUM-FIT",
            name="Medium Item",
            length=Decimal("25.00"),
            width=Decimal("18.00"),
            height=Decimal("12.00"),
            weight=Decimal("4.000"),
            quantity=1
        )
        result = recommend_box([item], self.all_boxes)
        self.assertTrue(result.is_fit_found)
        self.assertEqual(result.recommended_box.id, self.box_medium.id)
        self.assertEqual(len(result.rejected_boxes), 1)  # Box Small rejected
        rejection = result.rejected_boxes[0]
        self.assertEqual(rejection.box.id, self.box_small.id)
        self.assertEqual(rejection.reason, "DIMENSIONS_AND_WEIGHT")
        self.assertIn("exceeds maximum weight capacity", rejection.message)
        self.assertIn("exceeds box internal dimensions", rejection.message)
