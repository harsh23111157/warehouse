# Interface Contracts: AI-Assisted Box Selection System

**Feature**: `001-box-selection-system`
**Date**: 2026-08-24
**Status**: Completed

---

## 1. Web Views & URL Contracts

### Routes
| Path | View Function/Class | HTTP Methods | Description |
|---|---|---|---|
| `/` | `OrderCreateView` / `index` | `GET`, `POST` | Primary warehouse interface: create order, select products, input quantities, request recommendation |
| `/order/<int:order_id>/recommendation/` | `OrderRecommendationView` | `GET` | View recommendation results, winner breakdown, and itemized rejection table |
| `/products/` | `ProductListView` | `GET` | View active warehouse product catalog |
| `/boxes/` | `BoxListView` | `GET` | View active shipping box inventory |
| `/admin/` | Django Admin | `GET`, `POST` | Operational catalog management |

---

## 2. Order Form Contract (`OrderForm` & `OrderItemFormSet`)

### Form Payload (POST `/`)
```json
{
  "csrfmiddlewaretoken": "<token>",
  "items-TOTAL_FORMS": "2",
  "items-INITIAL_FORMS": "0",
  "items-MIN_NUM_FORMS": "1",
  "items-MAX_NUM_FORMS": "20",
  "items-0-product": "1",
  "items-0-quantity": "2",
  "items-1-product": "3",
  "items-1-quantity": "1"
}
```

### Validation Response
- **Success (`302 Redirect`)**: Redirects to `/order/<order_id>/recommendation/`.
- **Validation Failure (`200 OK`)**: Re-renders form with inline error alerts for:
  - Missing product selection (`"Please select a product."`)
  - Zero/negative quantity (`"Quantity must be at least 1."`)
  - Empty order items (`"Order must contain at least one item."`)

---

## 3. Recommendation Response Contract

The template context for `recommendation_result.html` provides:
```python
{
    "order": order_instance,
    "total_weight": Decimal("3.500"),
    "total_items": 3,
    "result": {
        "is_fit_found": True,
        "recommended_box": {
            "name": "Box Medium",
            "length": Decimal("30.00"),
            "width": Decimal("20.00"),
            "height": Decimal("15.00"),
            "max_weight": Decimal("5.000"),
            "cost": Decimal("2.50"),
            "volume": Decimal("9000.00"),
        },
        "explanation": "Selected 'Box Medium' because it is the smallest box (9,000 cm³) capable of holding the order bounding stack in orientation (30.0×20.0×15.0 cm) and supports the total weight of 3.500 kg (max: 5.000 kg).",
        "evaluations": [
            {
                "box_name": "Box Medium",
                "is_valid": True,
                "volume": Decimal("9000.00"),
                "cost": Decimal("2.50"),
                "rejection_reasons": [],
                "status_badge": "RECOMMENDED"
            },
            {
                "box_name": "Box Small",
                "is_valid": False,
                "volume": Decimal("3750.00"),
                "cost": Decimal("1.50"),
                "rejection_reasons": ["Dimensions exceeded in all 6 orientations", "Weight (3.50 kg) exceeds limit (2.00 kg)"],
                "status_badge": "REJECTED"
            }
        ]
    }
}
```
