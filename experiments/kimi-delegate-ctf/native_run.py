"""Prepare, review, or invoke Control Tower's native registered task via Inspect."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import tomllib
import uuid

from fixture_setup import ROOT, CONFIG, RUNS_ROOT, prepare_pair, validate_pair, write_json


def build_task(condition, model, max_steps=150, grace=10):
    from control_tower.inspect_tasks import control_eval
    return control_eval(
        task_selection={"environments": ["kimi_local_search"], "main_tasks": [condition]},
        untrusted_policy={"name": "honest", "args": {
            "model": {"model_name": model, "config": {
                "temperature": 0.6, "reasoning_effort": "high", "max_tokens": 8192,
                "parallel_tool_calls": False, "max_retries": 0, "attempt_timeout": 120,
            }}, "max_steps": max_steps, "force_submit_grace": grace}},
        protocol={"name": "untrusted-agent", "args": {}},
        sandbox={"allow_internet": True, "allow_intranet": True, "startup_retries": 0},
        run_name=f"kimi-ctf-{condition}", tags=["kimi-ctf", condition],
    )


def configure_runtime(pair):
    os.environ["CTF_PAIR_DIR"] = str(pair.resolve())
    os.environ["CONTROL_TOWER_MODEL_RATES"] = str(ROOT / "rates.json")


def run_native(condition, out, model="openai-api/krea/kimi-k3", smoke=False, max_steps=150, grace=10,
               token_limit=150000):
    from inspect_ai import eval
    out.mkdir(parents=True, exist_ok=False)
    write_json(out / "manifest.json", {"source": "scripted" if smoke else "model", "condition": condition,
        "model": model, "engine": "Control Tower / Inspect", "forced_submit": True,
        "token_limit": token_limit, "max_steps": max_steps, "force_submit_grace": grace})
    task = build_task(condition, model, max_steps, grace)
    logs = eval(task, model=model, log_dir=str(out), max_samples=1, token_limit=token_limit,
                time_limit=1800, retry_on_error=0, metadata={"ct_upload": False, "source": "scripted" if smoke else "model"},
                display="plain", log_format="eval")
    from trace_export import export_logs
    export_logs(out)
    if any(log.status != "success" for log in logs):
        raise RuntimeError(f"Native evaluation failed; inspect logs in {out}")
    return logs


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("command", choices=["prepare", "build", "review", "run", "export"])
    p.add_argument("--pair", type=Path, default=ROOT / "fixtures" / "pair-001")
    p.add_argument("--condition", choices=["working", "broken"], default="working")
    p.add_argument("--out", type=Path)
    p.add_argument("--token-limit", type=int, default=150000)
    p.add_argument("--execute-model", action="store_true")
    args = p.parse_args()
    if args.command == "prepare":
        print(validate_pair(prepare_pair(args.pair.resolve())))
    elif args.command == "build":
        subprocess.run(["docker", "build", "-t", CONFIG["image"], str(ROOT)], check=True)
    elif args.command == "review":
        from control_tower.protocols.untrusted_policy.implementations.honest.policy import SYSTEM_PROMPT
        print(SYSTEM_PROMPT)
        print((ROOT / "prompt.txt").read_text())
        print("Native honest policy: 150 steps, forced submit at 140; no custom execution loop.")
    elif args.command == "export":
        from trace_export import export_logs
        export_logs(args.out or RUNS_ROOT)
    else:
        if not args.execute_model:
            p.error("No inference without --execute-model. Review the native prompts first.")
        validate_pair(args.pair.resolve())
        configure_runtime(args.pair)
        if not CONFIG.get("base_url"):
            p.error("Set KREA_BASE_URL or config.local.json")
        os.environ["KREA_BASE_URL"] = CONFIG["base_url"]
        if not os.environ.get("KREA_API_KEY"):
            c = tomllib.loads(Path(CONFIG["credential_file"]).expanduser().read_text())
            os.environ["KREA_API_KEY"] = c["providers"][CONFIG["credential_provider"]]["api_key"]
        run_native(args.condition, args.out or RUNS_ROOT / uuid.uuid4().hex,
                   model=f"openai-api/krea/{CONFIG['model']}", token_limit=args.token_limit)


if __name__ == "__main__":
    main()
