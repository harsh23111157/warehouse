# Test Output & System Verification Report

**Environment**:
- **Python**: 3.12.11 (CPython Windows x86_64)
- **Django**: 6.1.0
- **Pytest**: 9.1.1
- **Database Engine**: SQLite 3

---

## 1. Django System Checks

**Command**:
```bash
python manage.py check
```

**Output**:
```text
System check identified no issues (0 silenced).
```

---

## 2. Database Migrations Status

**Command**:
```bash
python manage.py makemigrations --check
```

**Output**:
```text
No changes detected
```

---

## 3. Automated Test Suite Execution (Django Test Runner)

**Command**:
```bash
python manage.py test -v 2
```

**Output**:
```text
Creating test database for alias 'default' ('file:memorydb_default?mode=memory&cache=shared')...
Operations to perform:
  Synchronize unmigrated apps: messages, staticfiles
  Apply all migrations: admin, auth, contenttypes, sessions, warehouse
Synchronizing apps without migrations:
  Creating tables...
    Running deferred SQL...
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying admin.0001_initial... OK
  Applying admin.0002_logentry_remove_auto_add... OK
  Applying admin.0003_logentry_add_action_flag_choices... OK
  Applying contenttypes.0002_remove_content_type_name... OK
  Applying auth.0002_alter_permission_name_max_length... OK
  Applying auth.0003_alter_user_email_max_length... OK
  Applying auth.0004_alter_user_username_opts... OK
  Applying auth.0005_alter_user_last_login_null... OK
  Applying auth.0006_require_contenttypes_0002... OK
  Applying auth.0007_alter_validators_add_error_messages... OK
  Applying auth.0008_alter_user_username_max_length... OK
  Applying auth.0009_alter_user_last_name_max_length... OK
  Applying auth.0010_alter_group_name_max_length... OK
  Applying auth.0011_update_proxy_permissions... OK
  Applying auth.0012_alter_user_first_name_max_length... OK
  Applying sessions.0001_initial... OK
  Applying warehouse.0001_initial... OK

test_admin_index_renders_custom_theme (warehouse.tests.test_admin.AdminInterfaceTests.test_admin_index_renders_custom_theme)
GET /admin/ renders custom theme branding. ... ok
test_admin_models_registered (warehouse.tests.test_admin.AdminInterfaceTests.test_admin_models_registered)
Verify Product, ShippingBox, and Order are registered in admin. ... ok
test_admin_site_custom_titles (warehouse.tests.test_admin.AdminInterfaceTests.test_admin_site_custom_titles)
Verify custom admin branding headers and titles. ... ok
test_ai_disabled_via_settings (warehouse.tests.test_ai.AIServiceTests.test_ai_disabled_via_settings)
When AI_ENABLED is False, provider is not called. ... ok
test_ai_malformed_response_degrades_gracefully (warehouse.tests.test_ai.AIServiceTests.test_ai_malformed_response_degrades_gracefully)
Malformed response without 'choices' returns EMPTY_RESPONSE without crashing. ... ok
test_ai_missing_api_key_returns_missing_config (warehouse.tests.test_ai.AIServiceTests.test_ai_missing_api_key_returns_missing_config)
When API key is empty, provider is not called. ... ok
test_ai_provider_http_error_degrades_gracefully (warehouse.tests.test_ai.AIServiceTests.test_ai_provider_http_error_degrades_gracefully)
HTTP 500 error from provider does not crash and returns available=False. ... ok
test_ai_provider_timeout_degrades_gracefully (warehouse.tests.test_ai.AIServiceTests.test_ai_provider_timeout_degrades_gracefully)
TimeoutError from provider does not crash and returns available=False. ... ok
test_ai_successful_response (warehouse.tests.test_ai.AIServiceTests.test_ai_successful_response)
AI provider returns a valid OpenAI-compatible completion. ... ok
test_deterministic_engine_is_completely_independent_of_ai (warehouse.tests.test_ai.AIServiceTests.test_deterministic_engine_is_completely_independent_of_ai)
Proof that the deterministic recommendation engine functions identically whether AI is enabled, disabled, crashing, or throwing exceptions. ... ok
test_order_form_valid (warehouse.tests.test_forms.OrderFormTests.test_order_form_valid)
OrderForm with optional note is valid. ... ok
test_order_item_formset_rejects_empty_items (warehouse.tests.test_forms.OrderFormTests.test_order_item_formset_rejects_empty_items)
FormSet with no product selected fails validation. ... ok
test_order_item_formset_rejects_zero_quantity (warehouse.tests.test_forms.OrderFormTests.test_order_item_formset_rejects_zero_quantity)
FormSet with quantity 0 fails validation. ... ok
test_order_item_formset_valid_single_item (warehouse.tests.test_forms.OrderFormTests.test_order_item_formset_valid_single_item)
OrderItemFormSet with valid product and quantity is valid. ... ok
test_order_item_rejects_zero_quantity (warehouse.tests.test_models.OrderModelTests.test_order_item_rejects_zero_quantity)
OrderItem quantity < 1 must fail validation. ... ok
test_order_total_weight_calculation (warehouse.tests.test_models.OrderModelTests.test_order_total_weight_calculation)
Total order weight must equal sum(product_weight * quantity). ... ok
test_product_clean_valid (warehouse.tests.test_models.ProductModelTests.test_product_clean_valid)
Valid product clean() passes without error. ... ok
test_product_creation_and_volume (warehouse.tests.test_models.ProductModelTests.test_product_creation_and_volume)
Verify volume is correctly calculated as L * W * H. ... ok
test_product_rejects_non_positive_length (warehouse.tests.test_models.ProductModelTests.test_product_rejects_non_positive_length)
Product length <= 0 must fail validation. ... ok
test_product_rejects_non_positive_weight (warehouse.tests.test_models.ProductModelTests.test_product_rejects_non_positive_weight)
Product weight <= 0 must fail validation. ... ok
test_shipping_box_rejects_negative_cost (warehouse.tests.test_models.ShippingBoxModelTests.test_shipping_box_rejects_negative_cost)
Box cost < 0 must fail validation. ... ok
test_shipping_box_rejects_zero_dimension (warehouse.tests.test_models.ShippingBoxModelTests.test_shipping_box_rejects_zero_dimension)
Box with zero dimension must fail validation. ... ok
test_shipping_box_volume_and_dimensions (warehouse.tests.test_models.ShippingBoxModelTests.test_shipping_box_volume_and_dimensions)
Verify usable volume is calculated correctly. ... ok
test_cheaper_box_breaks_tie_for_equal_volumes (warehouse.tests.test_packing.PackingEngineTests.test_cheaper_box_breaks_tie_for_equal_volumes)
When two boxes have identical usable volume, lowest unit cost wins. ... ok
test_deterministic_repeated_result (warehouse.tests.test_packing.PackingEngineTests.test_deterministic_repeated_result)
Calling recommendation 100 times returns identical winner and explanation. ... ok
test_exact_dimension_boundary_is_valid (warehouse.tests.test_packing.PackingEngineTests.test_exact_dimension_boundary_is_valid)
Item whose dimensions exactly match box internal dimensions must fit (inclusive <=). ... ok
test_explainability_rejected_boxes_structure (warehouse.tests.test_packing.PackingEngineTests.test_explainability_rejected_boxes_structure)
Verify rejected_boxes list contains structured diagnostics with reasons and messages. ... ok
test_invalid_domain_data_raises_value_error (warehouse.tests.test_packing.PackingEngineTests.test_invalid_domain_data_raises_value_error)
Non-positive dimensions, weights, quantities raise ValueError on ItemSpec / BoxSpec. ... ok
test_multiple_items_heterogeneous_are_packed (warehouse.tests.test_packing.PackingEngineTests.test_multiple_items_heterogeneous_are_packed)
Heterogeneous multi-product orders calculate composite bounding dimensions. ... ok
test_multiple_quantity_weight_and_stacking (warehouse.tests.test_packing.PackingEngineTests.test_multiple_quantity_weight_and_stacking)
Multiple quantities calculate total weight and 1D orthogonal bounding stack. ... ok
test_no_boxes_returns_no_fit (warehouse.tests.test_packing.PackingEngineTests.test_no_boxes_returns_no_fit)
Empty box catalog returns structured no-fit state. ... ok
test_no_weight_fit_returns_diagnostic_explanation (warehouse.tests.test_packing.PackingEngineTests.test_no_weight_fit_returns_diagnostic_explanation)
When all boxes fail due to weight, explanation mentions weight capacity. ... ok
test_order_over_capacity_is_rejected (warehouse.tests.test_packing.PackingEngineTests.test_order_over_capacity_is_rejected)
Order exceeding box maximum payload weight is rejected with WEIGHT reason. ... ok
test_order_weight_exactly_at_capacity_is_valid (warehouse.tests.test_packing.PackingEngineTests.test_order_weight_exactly_at_capacity_is_valid)
Order weight exactly equal to box max_weight must be accepted. ... ok
test_product_does_not_fit_any_dimension (warehouse.tests.test_packing.PackingEngineTests.test_product_does_not_fit_any_dimension)
Oversized item exceeding all dimensions in all rotations is rejected. ... ok
test_product_fits_after_rotation (warehouse.tests.test_packing.PackingEngineTests.test_product_fits_after_rotation)
Item fitting only when rotated across orthogonal axes is recommended. ... ok
test_product_fits_without_rotation (warehouse.tests.test_packing.PackingEngineTests.test_product_fits_without_rotation)
Item whose standard orientation fits within box is recommended. ... ok
test_rotation_symmetry_deduplication (warehouse.tests.test_packing.PackingEngineTests.test_rotation_symmetry_deduplication)
Cubic and square items have deduplicated rotation sets. ... ok
test_smallest_valid_box_is_selected (warehouse.tests.test_packing.PackingEngineTests.test_smallest_valid_box_is_selected)
System ranks valid boxes by volume and chooses the smallest suitable box. ... ok
test_stable_final_tie_break (warehouse.tests.test_packing.PackingEngineTests.test_stable_final_tie_break)
When volume and cost are identical, tie breaks deterministically by name / id. ... ok
test_box_list_view (warehouse.tests.test_views.WarehouseViewTests.test_box_list_view)
GET /boxes/ returns 200 and lists boxes. ... ok
test_order_ai_explanation_json_endpoint (warehouse.tests.test_views.WarehouseViewTests.test_order_ai_explanation_json_endpoint)
GET /order/<id>/ai-explanation/ returns JSON without blocking. ... ok
test_order_create_view_get (warehouse.tests.test_views.WarehouseViewTests.test_order_create_view_get)
GET / returns 200 and renders order creation form. ... ok
test_order_create_view_post_invalid_re_renders_errors (warehouse.tests.test_views.WarehouseViewTests.test_order_create_view_post_invalid_re_renders_errors)
POST / with empty items re-renders 200 with validation error. ... ok
test_order_create_view_post_valid_redirects (warehouse.tests.test_views.WarehouseViewTests.test_order_create_view_post_valid_redirects)
POST / with valid items creates order and redirects to recommendation view. ... ok
test_product_list_view (warehouse.tests.test_views.WarehouseViewTests.test_product_list_view)
GET /products/ returns 200 and lists products. ... ok
test_recommendation_view_404_for_nonexistent_order (warehouse.tests.test_views.WarehouseViewTests.test_recommendation_view_404_for_nonexistent_order)
GET recommendation for nonexistent order returns 404. ... ok
test_recommendation_view_renders_no_fit_state (warehouse.tests.test_views.WarehouseViewTests.test_recommendation_view_renders_no_fit_state)
GET recommendation view with oversized item renders 'No Available Box' banner. ... ok
test_recommendation_view_renders_winner_and_explanation (warehouse.tests.test_views.WarehouseViewTests.test_recommendation_view_renders_winner_and_explanation)
GET recommendation view renders recommended box card and explanation. ... ok

----------------------------------------------------------------------
Ran 49 tests in 4.865s

OK
Destroying test database for alias 'default' ('file:memorydb_default?mode=memory&cache=shared')...
System check identified no issues (0 silenced).
```

---

## 4. Pytest Execution

**Command**:
```bash
pytest
```

**Output**:
```text
============================= test session starts =============================
platform win32 -- Python 3.12.11, pytest-9.1.1, pluggy-1.6.0
django: version: 6.1, settings: config.settings (from ini)
rootdir: D:\assignment
configfile: pytest.ini
plugins: django-4.14.0
collected 49 items

warehouse\tests\test_admin.py ...                                        [  6%]
warehouse\tests\test_ai.py .......                                       [ 20%]
warehouse\tests\test_forms.py ....                                       [ 28%]
warehouse\tests\test_models.py .........                                 [ 46%]
warehouse\tests\test_packing.py .................                        [ 81%]
warehouse\tests\test_views.py .........                                  [100%]

============================= 49 passed in 6.07s ==============================
```
