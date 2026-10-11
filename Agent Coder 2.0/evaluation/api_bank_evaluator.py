"""API-Bank evaluator comparing predicted tool call and arguments with ground truth."""

from __future__ import annotations

import ast
import json
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from dataset.api_bank_loader import APIBankTurn


def _coerce_api_descriptions(api_descriptions: str | dict | list | None) -> dict[str, dict[str, Any]]:
    """Build a registry of mock API definitions from the task description payload."""
    registry: dict[str, dict[str, Any]] = {}
    if not api_descriptions:
        return registry

    payload: Any = api_descriptions
    if isinstance(payload, str):
        text = payload.strip()
        if not text:
            return registry
        try:
            payload = json.loads(text)
        except Exception:
            try:
                payload = ast.literal_eval(text)
            except Exception:
                return registry

    if isinstance(payload, dict):
        items = payload.get("apis", payload.get("tools", [payload]))
        if not isinstance(items, list):
            items = [items]
    elif isinstance(payload, list):
        items = payload
    else:
        items = []

    for item in items:
        if not isinstance(item, dict):
            continue
        name = item.get("name") or item.get("api_name")
        if not name:
            continue
        registry[str(name)] = item

    return registry


def _mock_execute_api(api_name: str, params: dict[str, Any], api_descriptions: str | dict | list | None) -> tuple[bool, str | None]:
    """Simulate whether the parsed call would succeed against the mock API registry."""
    registry = _coerce_api_descriptions(api_descriptions)
    if not registry:
        return True, None

    api_spec = registry.get(api_name)
    if api_spec is None:
        return False, f"API '{api_name}' is not defined in the available mock API registry"

    input_params = api_spec.get("input_parameters") or {}
    if not isinstance(input_params, dict):
        return False, f"API '{api_name}' has no usable input parameter schema"

    for field_name, field_spec in input_params.items():
        if not isinstance(field_spec, dict):
            continue
        if field_name not in params:
            return False, f"Missing required parameter '{field_name}' for API '{api_name}'"

        value = params[field_name]
        expected_type = str(field_spec.get("type", "")).lower()
        if expected_type == "str" and not isinstance(value, str):
            return False, f"Parameter '{field_name}' for API '{api_name}' must be a string"
        if expected_type in {"int", "float"}:
            try:
                float(value)
            except Exception:
                return False, f"Parameter '{field_name}' for API '{api_name}' must be numeric"

    date_format_hints = {
        "new_appointment_date": "%Y-%m-%d",
        "start_time": "%Y-%m-%d %H:%M:%S",
        "end_time": "%Y-%m-%d %H:%M:%S",
    }
    for field_name, fmt in date_format_hints.items():
        if field_name not in params:
            continue
        value = params[field_name]
        if not isinstance(value, str):
            return False, f"Parameter '{field_name}' for API '{api_name}' must be a string"
        try:
            datetime.strptime(value, fmt)
        except ValueError:
            return False, f"Parameter '{field_name}' for API '{api_name}' is not in the required format {fmt}"

    return True, None


@dataclass(frozen=True)
class APIBankEvaluationResult:
    passed: bool
    parsed_api_name: str | None
    parsed_params: dict[str, Any] | None
    api_match: bool
    params_match: bool
    raw_response: str
    error: str | None = None


def parse_api_call(text: str) -> tuple[str | None, dict[str, Any] | None]:
    """Parse text into (api_name, param_dict) from [ApiName(key=val)]."""
    if not text:
        return None, None

    match = re.search(r"\[([A-Za-z_]\w*)\s*\((.*?)\)\]", text, re.DOTALL)
    if not match:
        match = re.search(r"\b([A-Za-z_]\w*)\s*\((.*?)\)", text, re.DOTALL)
        if not match:
            return None, None

    api_name = match.group(1).strip()
    arg_str = match.group(2).strip()

    expression = f"{api_name}({arg_str})"
    try:
        call = ast.parse(expression, mode="eval").body
        if not isinstance(call, ast.Call):
            return api_name, {}
        arguments: dict[str, Any] = {}
        for kw in call.keywords:
            try:
                arguments[kw.arg] = ast.literal_eval(kw.value)
            except Exception:
                arguments[kw.arg] = str(kw.value)
        return api_name, arguments
    except Exception:
        params: dict[str, Any] = {}
        kv_pairs = re.findall(r"([a-zA-Z_]\w*)\s*=\s*(['\"].*?['\"]|[^,)]+)", arg_str)
        for k, v in kv_pairs:
            v_clean = v.strip().strip("'\"")
            params[k] = v_clean
        return api_name, params


def evaluate_api_bank(turn: APIBankTurn, generated_output: str) -> APIBankEvaluationResult:
    """Evaluate predicted API call against ground truth turn expectations by both matching and mock execution."""
    api_name, params = parse_api_call(generated_output)

    if not api_name:
        return APIBankEvaluationResult(
            passed=False,
            parsed_api_name=None,
            parsed_params=None,
            api_match=False,
            params_match=False,
            raw_response=generated_output,
            error="Could not parse API call syntax [ApiName(...)] from output",
        )

    api_match = (api_name.lower() == turn.expected_api_name.lower())

    params_match = False
    if params is not None and turn.expected_param_dict is not None:
        norm_parsed = {str(k): str(v) for k, v in params.items()}
        norm_expected = {str(k): str(v) for k, v in turn.expected_param_dict.items()}
        params_match = (norm_parsed == norm_expected)

    runtime_success = False
    runtime_error = None
    if api_match and params_match:
        runtime_success, runtime_error = _mock_execute_api(api_name, params, turn.api_descriptions)

    passed = api_match and params_match and runtime_success

    if passed:
        return APIBankEvaluationResult(
            passed=True,
            parsed_api_name=api_name,
            parsed_params=params,
            api_match=True,
            params_match=True,
            raw_response=generated_output,
            error=None,
        )

    if not api_match:
        error = "API name mismatch"
    elif not params_match:
        error = "Parameter mismatch"
    elif runtime_error:
        error = runtime_error
    else:
        error = "API call failed mock execution"

    return APIBankEvaluationResult(
        passed=False,
        parsed_api_name=api_name,
        parsed_params=params,
        api_match=api_match,
        params_match=params_match,
        raw_response=generated_output,
        error=error,
    )


__all__ = ["APIBankEvaluationResult", "parse_api_call", "evaluate_api_bank"]
