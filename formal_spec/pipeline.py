"""Formal specification generation pipeline adapted from LLM-sts-pipeline.

The original repository's implementation is notebook-centric. This module
extracts the same three-stage structure — annotation, lifting, translation —
and preserves the retry / validation loop so it can be reused as a library.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from config import AppConfig
from dataset.mbpp_loader import MBPPProblem
from llm.client import ChatMessage


PROMPT_DIR = Path(__file__).resolve().parent.parent / "prompts"


def _load_prompt(name: str) -> str:
    return (PROMPT_DIR / name).read_text(encoding="utf-8")


def strip_code_fences(text: str) -> str:
    stripped = text.strip()
    stripped = re.sub(r"^```[a-zA-Z0-9_+-]*\s*", "", stripped)
    stripped = re.sub(r"\s*```$", "", stripped)
    return stripped.strip()


def parse_json_response(raw: str) -> Any:
    return json.loads(strip_code_fences(raw))


@dataclass
class FormalSpecStageArtifacts:
    annotation: Any | None = None
    lifted: Any | None = None
    translation: Any | None = None
    validation_errors: list[str] = field(default_factory=list)
    refinement_attempts: int = 0
    validation_status: str = "pending"


@dataclass
class FormalSpecResult:
    task_id: int | str
    problem_text: str
    artifacts: FormalSpecStageArtifacts
    final_spec: dict[str, Any]
    raw_responses: dict[str, str]


GENERIC_PLACEHOLDERS = {
    "inputs satisfy the problem statement",
    "inputs satisfy problem statement",
    "the result satisfies the task description",
    "the result satisfies task description",
    "result satisfies the task description",
    "result satisfies task description",
    "none",
    "true",
    "n/a",
}


def normalize_formal_spec(
    spec: Any,
    *,
    problem: Any,
    artifacts: FormalSpecStageArtifacts | None = None,
) -> dict[str, Any] | None:
    """Normalize LLM output into standard {'operations': [...]} schema."""
    if not isinstance(spec, (dict, list)):
        return None

    if isinstance(spec, list):
        operations_list = spec
    else:
        if "operations" in spec and isinstance(spec["operations"], list):
            operations_list = spec["operations"]
        elif "operations" in spec and isinstance(spec["operations"], dict):
            operations_list = [spec["operations"]]
        else:
            # Check if root has operation fields
            op_fields = {"operationId", "operationName", "Precondition", "Function", "Postcondition", "precondition", "postcondition", "function"}
            if any(f in spec for f in op_fields):
                operations_list = [spec]
            else:
                # Check other possible container keys
                found = False
                for k in ["formal_spec", "formal_specification", "specs", "specification"]:
                    if k in spec:
                        val = spec[k]
                        operations_list = val if isinstance(val, list) else [val]
                        found = True
                        break
                if not found:
                    operations_list = [spec]

    task_id = getattr(problem, "task_id", 0)
    task_text = getattr(problem, "text", getattr(problem, "prompt", str(problem)))
    entry_point = getattr(problem, "entry_point", None) or f"task_{task_id}"

    normalized_ops: list[dict[str, Any]] = []
    alias_map = {
        "Precondition": ["precondition", "preconditions", "Preconditions", "pre_condition", "pre_conditions", "requires", "Requires"],
        "Postcondition": ["postcondition", "postconditions", "Postconditions", "post_condition", "post_conditions", "ensures", "Ensures"],
        "Function": ["function", "func", "signature", "operation", "entry_point"],
        "LABEL": ["label", "type"],
        "operationId": ["operation_id", "op_id", "id"],
        "operationName": ["operation_name", "op_name", "name"],
        "actionable_sentences": ["actionable_sentence", "sentences", "requirements"],
        "lifted_nl": ["lifted", "lifted_requirements", "lifted_constraints"],
        "assumptions": ["assumption"],
        "invariants": ["invariant"],
    }

    for idx, item in enumerate(operations_list):
        if not isinstance(item, dict):
            continue
        op = dict(item)

        # Normalize field names
        for standard_key, aliases in alias_map.items():
            if standard_key not in op or op[standard_key] in (None, "", []):
                for alias in aliases:
                    if alias in op and op[alias] not in (None, "", []):
                        op[standard_key] = op[alias]
                        break

        # Defaults for missing metadata
        if "operationId" not in op or not op["operationId"]:
            op["operationId"] = f"OP-{task_id}_{idx}"
        if "operationName" not in op or not op["operationName"]:
            op["operationName"] = entry_point
        if "LABEL" not in op or not op["LABEL"]:
            op["LABEL"] = "FUNCTIONAL_SPEC"

        # Backfill actionable_sentences from annotation stage if missing
        if "actionable_sentences" not in op or not op["actionable_sentences"]:
            if artifacts and isinstance(artifacts.annotation, dict) and artifacts.annotation.get("actionable_sentences"):
                op["actionable_sentences"] = artifacts.annotation["actionable_sentences"]
            else:
                op["actionable_sentences"] = [task_text]

        # Backfill lifted_nl from lifted stage if missing
        if "lifted_nl" not in op or not op["lifted_nl"]:
            if artifacts and isinstance(artifacts.lifted, dict) and artifacts.lifted.get("lifted_nl"):
                op["lifted_nl"] = artifacts.lifted["lifted_nl"]
            else:
                op["lifted_nl"] = [f"whenever {op.get('operationName', entry_point)} is invoked, it must satisfy the requirements"]

        if "assumptions" not in op:
            op["assumptions"] = []
        if "invariants" not in op:
            op["invariants"] = []

        normalized_ops.append(op)

    return {"operations": normalized_ops}


def _validate_formal_spec(problem: Any, spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(spec, dict):
        return ["Formal spec must be a JSON object."]
    operations = spec.get("operations")
    if not isinstance(operations, list) or not operations:
        errors.append("Formal spec must contain a non-empty operations list.")
        return errors

    for index, op in enumerate(operations):
        if not isinstance(op, dict):
            errors.append(f"Operation {index} is not an object.")
            continue
        op_id = op.get("operationId", f"OP-{index}")
        for field_name in ["operationId", "operationName", "actionable_sentences", "lifted_nl", "LABEL", "Precondition", "Function", "Postcondition"]:
            if field_name not in op or op[field_name] in (None, "", []):
                errors.append(f"Operation {op_id} is missing {field_name}.")

        # Check for generic non-informative placeholders
        pre = str(op.get("Precondition", "")).strip().lower()
        post = str(op.get("Postcondition", "")).strip().lower()
        if pre in GENERIC_PLACEHOLDERS or len(pre) < 5:
            errors.append(f"Operation {op_id} has generic or empty Precondition: '{op.get('Precondition')}'. Must specify concrete domain conditions.")
        if post in GENERIC_PLACEHOLDERS or len(post) < 5:
            errors.append(f"Operation {op_id} has generic or empty Postcondition: '{op.get('Postcondition')}'. Must specify concrete domain conditions.")

        if isinstance(op.get("Precondition"), str) and "assert(" in op["Precondition"]:
            errors.append(f"Operation {op_id} leaks implementation details into Precondition.")
        if isinstance(op.get("Postcondition"), str) and "sorted(" in op["Postcondition"]:
            errors.append(f"Operation {op_id} leaks implementation details into Postcondition.")
    return errors


def _repair_prompt(problem: Any, artifacts: FormalSpecStageArtifacts, errors: list[str]) -> str:
    task_id = getattr(problem, "task_id", 0)
    task_text = getattr(problem, "text", getattr(problem, "prompt", str(problem)))
    entry_point = getattr(problem, "entry_point", None) or f"task_{task_id}"
    return (
        "You are repairing a formal specification for a programming task, data science pipeline, or API call.\n\n"
        f"Task ID: {task_id}\n"
        f"Entry point / Function: {entry_point}\n"
        f"Task text:\n{task_text}\n\n"
        f"Validation errors:\n- " + "\n- ".join(errors) + "\n\n"
        "Return a corrected raw JSON object with the following exact schema:\n"
        "{\n"
        '  "operations": [\n'
        "    {\n"
        f'      "operationId": "OP-{task_id}",\n'
        f'      "operationName": "{entry_point}",\n'
        '      "actionable_sentences": ["<extracted requirement sentences>"],\n'
        '      "lifted_nl": ["<lifted constraints>"],\n'
        '      "LABEL": "FUNCTIONAL_SPEC",\n'
        '      "Precondition": "<concrete, problem-specific precondition (inputs, types, ranges, or auth state)>",\n'
        '      "Function": "<function or tool call signature with types>",\n'
        '      "Postcondition": "<concrete, problem-specific postcondition (guarantees, relations, or return status)>",\n'
        '      "assumptions": ["..."],\n'
        '      "invariants": ["..."]\n'
        "    }\n"
        "  ]\n"
        "}\n\n"
        "CRITICAL: Do NOT use generic placeholders like 'inputs satisfy the problem statement'. "
        "State the exact inputs, prerequisites, return properties, or state changes."
    )


def generate_formal_spec(problem: Any, *, client, model: str, config: AppConfig) -> FormalSpecResult:
    artifacts = FormalSpecStageArtifacts()
    raw_responses: dict[str, str] = {}
    task_id = getattr(problem, "task_id", 0)
    task_text = getattr(problem, "text", getattr(problem, "prompt", str(problem)))
    entry_point = getattr(problem, "entry_point", None) or f"task_{task_id}"

    prompt_annotation = _load_prompt("formal_spec_annotation.txt").format(task_text=task_text, task_id=task_id)
    prompt_lift = _load_prompt("formal_spec_lift.txt")
    prompt_translate = _load_prompt("formal_spec_translate.txt")


    for attempt in range(1, config.formal_spec_retries + 1):
        artifacts.refinement_attempts = attempt
        try:
            raw_annotation = client.chat(
                messages=[ChatMessage(role="system", content="You are an expert in formal methods."), ChatMessage(role="user", content=prompt_annotation)],
                model=model,
                temperature=0.2,
                max_tokens=4096,
            )
            raw_responses["annotation"] = raw_annotation
            annotation = parse_json_response(raw_annotation)
            artifacts.annotation = annotation

            raw_lift = client.chat(
                messages=[ChatMessage(role="system", content="You are an expert in formal methods and temporal logic."), ChatMessage(role="user", content=prompt_lift + "\n\nANNOTATION:\n" + json.dumps(annotation, indent=2, ensure_ascii=False))],
                model=model,
                temperature=0.2,
                max_tokens=4096,
            )
            raw_responses["lifted"] = raw_lift
            lifted = parse_json_response(raw_lift)
            artifacts.lifted = lifted

            translate_content = (
                f"{prompt_translate}\n\n"
                f"TASK ID: {task_id}\n"
                f"ENTRY POINT / FUNCTION: {entry_point}\n\n"
                f"TASK DESCRIPTION:\n{task_text}\n\n"
                f"ANNOTATIONS:\n{json.dumps(annotation, indent=2, ensure_ascii=False)}\n\n"
                f"LIFTED REQUIREMENTS:\n{json.dumps(lifted, indent=2, ensure_ascii=False)}"
            )
            raw_translate = client.chat(
                messages=[ChatMessage(role="system", content="You are an expert formal specification translator."), ChatMessage(role="user", content=translate_content)],
                model=model,
                temperature=0.2,
                max_tokens=4096,
            )
            raw_responses["translation"] = raw_translate
            translation_raw = parse_json_response(raw_translate)
            translation = normalize_formal_spec(translation_raw, problem=problem, artifacts=artifacts)
            artifacts.translation = translation

            if isinstance(translation, dict):
                errors = _validate_formal_spec(problem, translation)
            else:
                errors = ["Translation stage must return a JSON object."]

            if not errors:
                artifacts.validation_status = "validated"
                return FormalSpecResult(
                    task_id=task_id,
                    problem_text=task_text,
                    artifacts=artifacts,
                    final_spec=translation,
                    raw_responses=raw_responses,
                )

            artifacts.validation_errors = errors
            repair_prompt = _repair_prompt(problem, artifacts, errors)
            raw_repair = client.chat(
                messages=[ChatMessage(role="system", content="You repair formal specifications."), ChatMessage(role="user", content=repair_prompt)],
                model=model,
                temperature=0.2,
                max_tokens=4096,
            )
            raw_responses[f"repair_{attempt}"] = raw_repair
            repaired_raw = parse_json_response(raw_repair)
            repaired = normalize_formal_spec(repaired_raw, problem=problem, artifacts=artifacts)
            artifacts.translation = repaired
            if isinstance(repaired, dict):
                errors = _validate_formal_spec(problem, repaired)
                if not errors:
                    artifacts.validation_status = "validated_after_repair"
                    return FormalSpecResult(
                        task_id=task_id,
                        problem_text=task_text,
                        artifacts=artifacts,
                        final_spec=repaired,
                        raw_responses=raw_responses,
                    )
                artifacts.validation_errors = errors
        except Exception as exc:
            artifacts.validation_errors = [str(exc)]
            continue

    artifacts.validation_status = "failed"
    fallback = {
        "task_id": task_id,
        "operations": [
            {
                "operationId": f"TASK-{task_id}",
                "operationName": entry_point,
                "actionable_sentences": [task_text],
                "lifted_nl": [f"whenever {entry_point} is called, it must satisfy the task description"],
                "LABEL": "FALLBACK_SPEC",
                "Precondition": "inputs satisfy the problem statement",
                "Function": f"{entry_point}(...) -> Any",
                "Postcondition": "the result satisfies the task description",
            }
        ],
        "validation_status": "fallback",
    }
    return FormalSpecResult(
        task_id=task_id,
        problem_text=task_text,
        artifacts=artifacts,
        final_spec=fallback,
        raw_responses=raw_responses,
    )

