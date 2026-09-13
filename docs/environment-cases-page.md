# Environment cases page

The sixteen proposed cases from the discussion, presented as a standalone, responsive table. These are proposals, not evaluation results.

Build from the repository root:

```sh
python3 scripts/build_environment_cases.py
```

Upload `dist/environment-cases/` to any static host. The output is a single self-contained HTML file with no external assets or JavaScript dependencies.

Preview locally:

```sh
python3 -m http.server 8099 --bind 127.0.0.1 --directory dist/environment-cases
```

Open http://127.0.0.1:8099/. The catalogue is integrated into this fork’s `main`. The GitHub Pages workflow
deploys `web/`, including `/environment-cases/`, at
https://korentomas.github.io/agent-delegate-sprint-2026/environment-cases/.
