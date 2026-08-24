# Quickstart & Verification Guide: AI-Assisted Box Selection System

**Feature**: `001-box-selection-system`
**Date**: 2026-08-24
**Status**: Completed

---

## 1. Setup Environment

```bash
# 1. Activate virtual environment
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1

# 2. Apply database migrations
python manage.py migrate

# 3. Load sample warehouse seed data (optional fixture / command)
python manage.py loaddata sample_warehouse_data.json
```

---

## 2. Run Automated Test Suite

```bash
# Run Django test suite
python manage.py test warehouse

# Or run pytest
pytest
```

---

## 3. Run Django System Checks

```bash
python manage.py check
python manage.py makemigrations --check
```

---

## 4. Launch Local Development Server

```bash
python manage.py runserver
```
- Open browser at `http://127.0.0.1:8000/` for the warehouse packing interface.
- Open `http://127.0.0.1:8000/admin/` for inventory and catalog management.

---

## 5. End-to-End Smoke Test Flow

1. **Verify Catalog**: Navigate to `/products/` and `/boxes/` to ensure sample items are listed.
2. **Single Product Recommendation**:
   - On `/`, select `Sample Mug (12 × 10 × 10 cm, 0.4 kg)` with quantity `1`.
   - Submit form -> verify redirected to recommendation page.
   - Verify recommended box is `Small Mailer` with explanation.
3. **Rotation Verification**:
   - Select product `Book (25 × 18 × 4 cm, 0.6 kg)` with quantity `1`.
   - Box with dimensions `20 × 28 × 10 cm` must be recommended via rotated fit `(18 × 25 × 4 cm)`.
4. **Weight Limit Rejection**:
   - Select `Cast Iron Weight (10 × 10 × 10 cm, 12 kg)`.
   - Boxes with max weight `< 12 kg` must show rejection status due to weight limit.
5. **No Fit State**:
   - Select `Large Appliance (120 × 100 × 80 cm, 40 kg)`.
   - System displays "No Suitable Box Found" with itemized reasons for all catalog boxes.
