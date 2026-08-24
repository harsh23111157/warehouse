import json
import logging
import urllib.error
import urllib.request
from decimal import Decimal
from typing import Any, Dict, List, Optional
from django.conf import settings
from warehouse.packing import RecommendationResult

logger = logging.getLogger(__name__)


def generate_ai_explanation(
    result: Optional[RecommendationResult],
    order_items: List[Any]
) -> Dict[str, Any]:
    """
    Optional AI-Assisted Logistics Explanation Layer.
    
    NON-NEGOTIABLE INVARIANTS:
    1. The AI NEVER selects boxes or decides physical fit.
    2. The AI receives only derived, structured deterministic facts.
    3. Failures/timeouts degrade gracefully with zero impact on the deterministic result.
    4. Credentials remain strictly server-side.
    """
    if not getattr(settings, "AI_ENABLED", False):
        return {
            "available": False,
            "explanation": None,
            "status": "DISABLED",
            "model": None,
            "tokens_used": 0
        }

    api_key = getattr(settings, "AI_API_KEY", "").strip()
    base_url = getattr(settings, "AI_API_BASE_URL", "https://router.bynara.id/v1").rstrip("/")
    primary_model = getattr(settings, "AI_MODEL", "agnes-2.5-flash")
    timeout = getattr(settings, "AI_TIMEOUT_SECONDS", 20)

    if not api_key or not base_url:
        return {
            "available": False,
            "explanation": None,
            "status": "MISSING_CONFIG",
            "model": primary_model,
            "tokens_used": 0
        }

    if not result or not order_items:
        return {
            "available": False,
            "explanation": None,
            "status": "NO_DATA",
            "model": primary_model,
            "tokens_used": 0
        }

    # Prepare minimal structured facts
    items_summary = [
        f"- {item.quantity}x {item.product.name} ({item.product.length}x{item.product.width}x{item.product.height} cm, {item.product.weight} kg)"
        for item in order_items
        if hasattr(item, "product") and item.product
    ]

    if result.is_fit_found and result.recommended_box:
        box = result.recommended_box
        decision_facts = (
            f"DETERMINISTIC RECOMMENDATION: {box.name}\n"
            f"- Box Internal Dimensions: {box.length}x{box.width}x{box.height} cm\n"
            f"- Box Usable Volume: {box.volume:.2f} cm³\n"
            f"- Box Max Weight: {box.max_weight:.3f} kg\n"
            f"- Box Unit Cost: ${box.cost:.2f}\n"
            f"- Order Total Weight: {result.total_weight:.3f} kg\n"
            f"- Rejection Count: {len(result.rejected_boxes)} other boxes disqualified.\n"
            f"- Deterministic Reason: {result.explanation}"
        )
    else:
        decision_facts = (
            f"DETERMINISTIC RESULT: NO SUITABLE BOX FOUND\n"
            f"- Order Total Weight: {result.total_weight:.3f} kg\n"
            f"- Rejection Details:\n" +
            "\n".join([f"  * {r.box.name}: {r.message}" for r in result.rejected_boxes[:5]])
        )

    system_prompt = (
        "You are an AI warehouse logistics assistant. Your role is to provide a concise (2-3 sentences) "
        "human-friendly packing summary for warehouse packing staff based strictly on the provided "
        "deterministic decision and physical facts. Do NOT change or invent box names, dimensions, or weights. "
        "Maintain a calm, professional, warehouse-operational tone."
    )

    user_prompt = (
        f"Order Items:\n" + "\n".join(items_summary) + "\n\n" +
        f"Facts:\n{decision_facts}\n\n"
        "Provide a concise packaging summary and practical handling tip for the warehouse packer:"
    )

    # Candidate models list with automatic fallback
    candidate_models = [primary_model]
    if "agnes-2.5-flash" not in candidate_models:
        candidate_models.append("agnes-2.5-flash")
    if "ox-alpha" not in candidate_models:
        candidate_models.append("ox-alpha")

    endpoint = f"{base_url}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) WarehouseBoxSelection/1.0"
    }

    last_error_status = "UNKNOWN"

    for model_name in candidate_models:
        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": 160,
            "temperature": 0.2
        }

        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(endpoint, data=data_bytes, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                response_body = response.read().decode("utf-8")
                resp_json = json.loads(response_body)
                choices = resp_json.get("choices", [])
                usage = resp_json.get("usage", {})
                tokens_used = usage.get("total_tokens", 0)

                if choices and "message" in choices[0]:
                    ai_text = choices[0]["message"].get("content", "").strip()
                    if ai_text:
                        return {
                            "available": True,
                            "explanation": ai_text,
                            "status": "SUCCESS",
                            "model": model_name,
                            "tokens_used": tokens_used
                        }
                last_error_status = "EMPTY_RESPONSE"
        except urllib.error.HTTPError as e:
            logger.warning("AI Provider HTTP error %d for model %s: %s", e.code, model_name, e.reason)
            last_error_status = f"HTTP_ERROR_{e.code}"
        except (urllib.error.URLError, TimeoutError) as e:
            logger.warning("AI Provider timeout/network error for model %s: %s", model_name, e)
            last_error_status = "TIMEOUT_OR_NETWORK_ERROR"
        except Exception as e:
            logger.warning("AI Provider error for model %s: %s", model_name, e)
            last_error_status = "ERROR"

    return {
        "available": False,
        "explanation": None,
        "status": last_error_status,
        "model": primary_model,
        "tokens_used": 0
    }
