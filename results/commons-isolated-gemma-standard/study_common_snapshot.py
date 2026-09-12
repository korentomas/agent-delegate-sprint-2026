"""Shared pieces for the behavioral studies (pressure, capture).

Guardrails, identical to local_pilot.py:
- only loopback HTTP inference endpoints are accepted;
- no generated string is ever executed: every effect is Python state;
- hidden reasoning is never stored (only a boolean flag that the server returned some);
- HTTP or JSON failures become recorded invalid actions, never repaired;
- output directories are fresh unless --resume is given.
"""
import datetime
import hashlib
import json
import shutil
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOOPBACK_HOSTS = {'127.0.0.1', 'localhost', '::1'}
LOOPBACK_ERROR = 'Only local loopback HTTP inference endpoints are allowed.'
INVALID = {'action': 'invalid', 'answer': None, 'forward': [], 'message': 'Invalid or unavailable model response.'}
HIDDEN_KEYS = ('reasoning_content', 'reasoning', 'thinking')


def check_loopback(base_url):
    u = urllib.parse.urlparse(base_url)
    if u.scheme != 'http' or u.hostname not in LOOPBACK_HOSTS:
        raise SystemExit(LOOPBACK_ERROR)
    return base_url.rstrip('/')


def stamp():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def write_json(path, x):
    Path(path).write_text(json.dumps(x, ensure_ascii=False, indent=2) + '\n')


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def request_json(base, path, payload=None, timeout=90):
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(base + path, data=data, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.load(response)


def response_format(schema, style, name='decision'):
    """llama-server accepts {"type":"json_object","schema":...}; OpenAI-compatible servers (Ollama) use json_schema."""
    if style == 'openai':
        return {'type': 'json_schema', 'json_schema': {'name': name, 'schema': schema}}
    return {'type': 'json_object', 'schema': schema}


def _check(value, spec):
    types = spec.get('type', [])
    types = [types] if isinstance(types, str) else list(types)
    if isinstance(value, bool):
        return 'boolean' in types
    if 'enum' in spec and value not in spec['enum']:
        return False
    ok = ((value is None and 'null' in types) or (isinstance(value, str) and 'string' in types)
          or (isinstance(value, int) and 'integer' in types) or (isinstance(value, list) and 'array' in types))
    if not ok:
        return False
    if isinstance(value, list):
        item = spec.get('items', {})
        if not all(_check(v, item) for v in value):
            return False
        if spec.get('uniqueItems') and len(set(json.dumps(v) for v in value)) != len(value):
            return False
    return True


def validate(obj, schema):
    """Minimal JSON-schema check: an object with exactly the required keys, each matching enum/type/items."""
    if not isinstance(obj, dict) or set(obj) != set(schema['required']):
        return False
    return all(_check(obj[key], spec) for key, spec in schema['properties'].items())


def clip_words(text, limit):
    """Public messages are bounded before entering any shared state. Returns (clipped, original word count)."""
    words = str(text).split()
    return ' '.join(words[:limit]), len(words)


def discover_model(base_url, requested=None):
    listed = [m['id'] for m in request_json(base_url, '/v1/models').get('data', [])]
    if requested is None:
        if not listed:
            raise SystemExit('The server lists no models.')
        return listed[0]
    if requested not in listed:
        raise SystemExit(f'Model {requested!r} is not listed by {base_url}/v1/models: {listed}')
    return requested


class Recorder:
    """One loopback chat call per invocation. Every request and response goes to calls.jsonl."""

    def __init__(self, base_url, model, cfg, out, schema_style='llama'):
        self.base_url, self.model, self.cfg, self.out, self.style = base_url, model, cfg, Path(out), schema_style
        self.calls = 0
        self.invalid = 0
        self.total_tokens = 0

    def call(self, messages, schema, seed, episode, actor, round_index, schema_name='decision'):
        body = {'model': self.model, 'messages': messages, 'temperature': self.cfg['temperature'], 'seed': seed,
                'max_tokens': self.cfg['max_tokens'], 'chat_template_kwargs': {'enable_thinking': False},
                'response_format': response_format(schema, self.style, schema_name)}
        t = time.perf_counter()
        record = {'episode': episode, 'actor': actor, 'round': round_index, 'started_at': stamp(), 'request': body}
        parsed, valid = {}, False
        try:
            result = request_json(self.base_url, '/v1/chat/completions', body, self.cfg['timeout_seconds'])
            msg = result['choices'][0]['message']
            content = msg.get('content') or ''
            usage = result.get('usage') or {}
            record['response'] = {'model': result.get('model'), 'content': content,
                                  'finish_reason': result['choices'][0].get('finish_reason'), 'usage': usage,
                                  'reasoning_omitted': any(bool(msg.get(k)) for k in HIDDEN_KEYS)}
            record['system_fingerprint'] = result.get('system_fingerprint')
            self.total_tokens += usage.get('total_tokens', 0) or 0
            try:
                parsed = json.loads(content)
            except (ValueError, TypeError):
                parsed = {}
            valid = validate(parsed, schema)
        except Exception as e:  # network, HTTP, malformed body: recorded, not repaired
            record['error'] = type(e).__name__ + ': ' + str(e)
        record['valid'] = valid
        record['decision'] = parsed if valid else None
        record['seconds'] = time.perf_counter() - t
        self.calls += 1
        self.invalid += (not valid)
        with (self.out / 'calls.jsonl').open('a') as f:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
        return dict(parsed) if valid else dict(INVALID)


def prepare_out(out, resume):
    out = Path(out)
    if out.exists() and not resume:
        raise SystemExit('Use a fresh output path (or --resume) to preserve raw study records.')
    out.mkdir(parents=True, exist_ok=True)
    return out


def load_episodes(out):
    p = Path(out) / 'episodes.json'
    return json.loads(p.read_text()) if p.exists() else []


def snapshot_inputs(out, files):
    """Copy the frozen inputs next to the records, as local_pilot.py did with runner_snapshot.py."""
    for f in files:
        target = Path(out) / (Path(f).stem + '_snapshot' + Path(f).suffix)
        if not target.exists():
            shutil.copy(f, target)


def calls_totals(out):
    p = Path(out) / 'calls.jsonl'
    calls = tokens = invalid = 0
    if p.exists():
        for line in p.read_text().splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            calls += 1
            invalid += (not r.get('valid'))
            tokens += ((r.get('response') or {}).get('usage') or {}).get('total_tokens', 0) or 0
    return {'calls': calls, 'total_tokens': tokens, 'invalid_calls': invalid}


def write_manifest(out, run_config, inputs, episodes, wall_start, skipped, interpretation, inference_note):
    manifest = {'started_at': run_config['started_at'], 'resumed_at': run_config.get('resumed_at', []), 'finished_at': stamp(),
                'seconds_this_process': time.perf_counter() - wall_start, 'episodes': len(episodes), 'skipped_on_resume': skipped,
                **calls_totals(out), 'model': run_config['model'], 'model_tag': run_config['model_tag'],
                'schema_style': run_config['schema_style'], 'interpretation': interpretation, 'inference_note': inference_note,
                'input_sha256': {str(Path(f).resolve().relative_to(ROOT)): sha256_file(f) for f in inputs}}
    write_json(Path(out) / 'manifest.json', manifest)
    return manifest
