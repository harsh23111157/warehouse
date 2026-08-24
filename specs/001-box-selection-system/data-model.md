# Data Model: AI-Assisted Box Selection System

**Feature**: `001-box-selection-system`
**Date**: 2026-08-24
**Status**: Completed

---

## 1. Django Models (`warehouse/models.py`)

### `Product`
Represents an item in the ecommerce warehouse inventory.

| Field Name | Type | Constraints & Options | Description |
|---|---|---|---|
| `id` | AutoField | Primary Key | Unique internal ID |
| `sku` | CharField | `max_length=64`, `unique=True`, `db_index=True` | Unique Stock Keeping Unit |
| `name` | CharField | `max_length=255` | Human-readable product name |
| `length` | DecimalField | `max_digits=8`, `decimal_places=2`, `validators=[MinValueValidator(0.01)]` | Length in centimeters (cm) |
| `width` | DecimalField | `max_digits=8`, `decimal_places=2`, `validators=[MinValueValidator(0.01)]` | Width in centimeters (cm) |
| `height` | DecimalField | `max_digits=8`, `decimal_places=2`, `validators=[MinValueValidator(0.01)]` | Height in centimeters (cm) |
| `weight` | DecimalField | `max_digits=8`, `decimal_places=3`, `validators=[MinValueValidator(0.001)]` | Weight in kilograms (kg) |
| `is_active` | BooleanField | `default=True` | Whether product is active in warehouse |
| `created_at` | DateTimeField | `auto_now_add=True` | Creation timestamp |

**Model Methods**:
- `volume` (property): Returns $L \times W \times H$ ($\text{cm}^3$).
- `dimensions_tuple`: Returns `(length, width, height)`.

---

### `ShippingBox`
Represents an available box type in warehouse packaging inventory.

| Field Name | Type | Constraints & Options | Description |
|---|---|---|---|
| `id` | AutoField | Primary Key | Unique internal ID |
| `name` | CharField | `max_length=128`, `unique=True` | Name (e.g. "Small Mailer", "Box 1") |
| `length` | DecimalField | `max_digits=8`, `decimal_places=2`, `validators=[MinValueValidator(0.01)]` | Usable internal length (cm) |
| `width` | DecimalField | `max_digits=8`, `decimal_places=2`, `validators=[MinValueValidator(0.01)]` | Usable internal width (cm) |
| `height` | DecimalField | `max_digits=8`, `decimal_places=2`, `validators=[MinValueValidator(0.01)]` | Usable internal height (cm) |
| `max_weight` | DecimalField | `max_digits=8`, `decimal_places=3`, `validators=[MinValueValidator(0.001)]` | Maximum supported payload (kg) |
| `cost` | DecimalField | `max_digits=8`, `decimal_places=2`, `validators=[MinValueValidator(0.00)]` | Unit procurement cost ($) |
| `is_active` | BooleanField | `default=True` | Active for recommendation |
| `created_at` | DateTimeField | `auto_now_add=True` | Creation timestamp |

**Model Methods**:
- `volume` (property): Returns $L \times W \times H$ ($\text{cm}^3$).
- `dimensions_tuple`: Returns `(length, width, height)`.

---

### `Order`
Represents a warehouse packing order placed by warehouse staff.

| Field Name | Type | Constraints & Options | Description |
|---|---|---|---|
| `id` | AutoField | Primary Key | Unique order identifier |
| `created_at` | DateTimeField | `auto_now_add=True` | Order creation timestamp |
| `notes` | CharField | `max_length=255`, `blank=True` | Optional warehouse staff notes |

**Model Methods**:
- `total_weight` (property): Computed as $\sum (\text{item.product.weight} \times \text{item.quantity})$.
- `total_item_count` (property): Computed as $\sum \text{item.quantity}$.

---

### `OrderItem`
Line item association between an Order and a Product.

| Field Name | Type | Constraints & Options | Description |
|---|---|---|---|
| `id` | AutoField | Primary Key | Unique item identifier |
| `order` | ForeignKey | `to='Order'`, `on_delete=models.CASCADE`, `related_name='items'` | Parent order reference |
| `product` | ForeignKey | `to='Product'`, `on_delete=models.PROTECT`, `related_name='order_items'` | Product reference |
| `quantity` | PositiveIntegerField | `validators=[MinValueValidator(1)]` | Units of product (>= 1) |

---

## 2. Ephemeral Domain Structures (`warehouse/packing.py`)

Pure dataclasses used during calculation (not persisted to avoid derived data duplication):

```python
from dataclasses import dataclass
from decimal import Decimal
from typing import List, Optional, Tuple

@dataclass(frozen=True)
class ItemSpec:
    sku: str
    name: str
    length: Decimal
    width: Decimal
    height: Decimal
    weight: Decimal
    quantity: int

@dataclass(frozen=True)
class BoxSpec:
    id: int
    name: str
    length: Decimal
    width: Decimal
    height: Decimal
    max_weight: Decimal
    cost: Decimal

@dataclass(frozen=True)
class BoxEvaluation:
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
    is_fit_found: bool
    recommended_box: Optional[BoxSpec]
    explanation: str
    total_weight: Decimal
    evaluations: List[BoxEvaluation]
```
