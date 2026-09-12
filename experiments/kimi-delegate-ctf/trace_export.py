"""Export native .eval logs to inspectable JSON/JSONL, plus a comparison summary."""
import json
from pathlib import Path
from inspect_ai.log import read_eval_log

TOKEN_BUDGET_MESSAGE_KEY = "_token_budget_awareness"


def export_logs(root):
    root = Path(root)
    rows = []
    for path in sorted(root.rglob("*.eval")):
        log = read_eval_log(str(path))
        for sample in log.samples or []:
            data = sample.model_dump(mode="json", exclude_none=True)
            scores = list((data.get("scores") or {}).values())
            score = next((s for s in scores if "main_task_success" in (s.get("metadata") or {})), {})
            meta = (score.get("metadata") or {}).get("main_task_success", {})
            events = data.get("events", [])
            usage = {}
            budget_updates = []
            for event in events:
                if event.get("event") != "model":
                    continue
                for message in event.get("input", []):
                    message_metadata = message.get("metadata") or {}
                    if message_metadata.get(TOKEN_BUDGET_MESSAGE_KEY):
                        budget_updates.append({
                            key: message_metadata[key]
                            for key in ("used", "limit", "remaining", "remaining_percent")
                        })
                model_usage = (event.get("output") or {}).get("usage") or {}
                totals = usage.setdefault(event.get("model", "unknown"), {})
                for key, value in model_usage.items():
                    if isinstance(value, (int, float)):
                        totals[key] = totals.get(key, 0) + value
            row = {
                "sample_id": str(sample.id), "epoch": sample.epoch,
                "source": (log.eval.metadata or {}).get("source", "unknown"),
                "condition": meta.get("condition", "unknown"),
                "outcome": "error" if sample.error else meta.get("outcome", "incomplete"),
                "success": (score.get("value") or {}).get("main_task_success") == "C", "delegate_request": meta.get("delegate_request"),
                "model_calls": sum(e.get("event") == "model" for e in events),
                "tool_calls": sum(e.get("event") == "tool" for e in events),
                "forced_submit_calls": sum(e.get("event") == "model" and isinstance(e.get("tool_choice"), dict)
                    and e["tool_choice"].get("name") == "submit" for e in events),
                "model_usage": usage,
                "token_budget_updates": budget_updates,
                "limit": data.get("limit"), "error": data.get("error"),
                "native_log": str(path.relative_to(root)),
            }
            # Inspect discovers legacy JSON logs by timestamp-prefixed filenames.
            # Keep derived exports out of that namespace to avoid phantom runs.
            export = path.parent / f"export-{path.stem}-sample-{sample.epoch}-{str(sample.id).replace('/', '_')}"
            export.with_suffix(".json").write_text(json.dumps({"summary": row, "sample": data}, indent=2) + "\n")
            with export.with_suffix(".jsonl").open("w") as f:
                for event in events:
                    f.write(json.dumps(event) + "\n")
            rows.append(row)
    (root / "summary.json").write_text(json.dumps(rows, indent=2) + "\n")
    lines = ["# Native CTF run summary", "", "Scripted rows validate the harness; they are not Kimi behavior.", "",
             "| Source | Condition | Outcome | Flag correct | Model calls | Forced submits | Last budget |",
             "|---|---|---|---|---:|---:|---|"]
    for row in rows:
        last_budget = row["token_budget_updates"][-1] if row["token_budget_updates"] else None
        budget_text = (
            f"{last_budget['remaining']:,} / {last_budget['limit']:,} left"
            if last_budget else "unaware"
        )
        lines.append(f"| {row['source']} | {row['condition']} | {row['outcome']} | {row['success']} | {row['model_calls']} | {row['forced_submit_calls']} | {budget_text} |")
    (root / "summary.md").write_text("\n".join(lines) + "\n")
    return rows
