#!/usr/bin/env python3
"""Smoke-test API endpoints from OpenAPI schema against a running server."""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

SKIP_PATH_RE = re.compile(
	r"(login|register|logout|recover|reset-password|change-password|"
	r"request-password|confirm-|upload|import|export|render|generate|"
	r"debug/|process-pending|request-deletion|reject-deletion|"
	r"celery/|/admin/)",
	re.I,
)
MUTATING_METHODS = frozenset({"post", "put", "patch", "delete"})


@dataclass
class Context:
	ids: dict[str, list[Any]] = field(default_factory=lambda: defaultdict(list))
	token: str = ""


def http_request(
	base: str,
	method: str,
	path: str,
	*,
	token: str = "",
	body: dict | None = None,
	params: dict | None = None,
	timeout: int = 30,
) -> tuple[int, str]:
	url = base.rstrip("/") + path
	if params:
		qs = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
		if qs:
			url += ("&" if "?" in url else "?") + qs
	data = None
	headers = {"Accept": "application/json"}
	if token:
		headers["Authorization"] = f"Bearer {token}"
	if body is not None:
		data = json.dumps(body).encode()
		headers["Content-Type"] = "application/json"
	req = urllib.request.Request(url, data=data, headers=headers, method=method.upper())
	try:
		with urllib.request.urlopen(req, timeout=timeout) as resp:
			raw = resp.read().decode("utf-8", errors="replace")
			return resp.status, raw
	except urllib.error.HTTPError as exc:
		raw = exc.read().decode("utf-8", errors="replace")
		return exc.code, raw
	except Exception as exc:  # noqa: BLE001
		return 0, str(exc)


def login(base: str, login_email: str, password: str) -> str:
	status, raw = http_request(
		base,
		"POST",
		"/api/v1/auth/login",
		body={"login": login_email, "password": password},
	)
	if status != 200:
		raise RuntimeError(f"login failed {status}: {raw[:300]}")
	data = json.loads(raw)
	token = data.get("access_token") or data.get("token")
	if not token:
		raise RuntimeError(f"no token in login response: {raw[:300]}")
	return token


def substitute_path(path: str, ctx: Context) -> str | None:
	out = path
	for match in re.finditer(r"\{([^}]+)\}", path):
		name = match.group(1)
		candidates = ctx.ids.get(name, [])
		if not candidates:
			# common fallbacks
			fallbacks = {
				"deal_id": ctx.ids.get("id", []),
				"order_id": ctx.ids.get("id", []),
				"product_id": ctx.ids.get("id", []),
				"company_id": ctx.ids.get("company_id", []) or ctx.ids.get("id", []),
				"employee_id": ctx.ids.get("employee_id", []) or ctx.ids.get("id", []),
				"chat_id": ctx.ids.get("chat_id", []) or ctx.ids.get("id", []),
				"template_id": ctx.ids.get("template_id", []) or ctx.ids.get("id", []),
				"spec_id": ctx.ids.get("spec_id", []) or ctx.ids.get("id", []),
				"announcement_id": ctx.ids.get("announcement_id", []) or ctx.ids.get("id", []),
				"category": ["news"],
				"type": ["specification", "supply_contract"],
				"role": ["buyer", "seller"],
				"document_type": ["supply_contract", "order", "bill"],
				"token": ["invalid-smoke-token"],
				"inn": ["1234567890"],
			}
			candidates = fallbacks.get(name, [])
		if not candidates:
			return None
		out = out.replace("{" + name + "}", str(candidates[0]))
	return out


def collect_ids(data: Any, ctx: Context, depth: int = 0) -> None:
	if depth > 6:
		return
	if isinstance(data, dict):
		for key, val in data.items():
			if key == "id" or key.endswith("_id"):
				if isinstance(val, (int, str)):
					ctx.ids[key].append(val)
					if key == "id":
						ctx.ids["id"].append(val)
			collect_ids(val, ctx, depth + 1)
	elif isinstance(data, list):
		for item in data[:20]:
			collect_ids(item, ctx, depth + 1)


def seed_context(base: str, ctx: Context) -> None:
	seed_calls: list[tuple[str, str, dict | None]] = [
		("GET", "/api/v1/auth/me", None),
		("GET", "/api/v1/company", None),
		("GET", "/api/v1/purchases/deals", None),
		("GET", "/api/v1/purchases/orders", None),
		("GET", "/api/v1/me/products", None),
		("GET", "/api/v1/chats", None),
		("GET", "/api/v1/companies", None),
		("GET", "/api/v1/products", None),
		("GET", "/api/v1/announcements", None),
		("GET", "/api/v1/locations/tree", None),
		("GET", "/api/v1/cities-filter", None),
		("GET", "/api/v1/purchases/supply-contract-templates", {"type": "specification"}),
		("GET", "/api/v1/purchases/supply-contract-templates", {"type": "supply_contract"}),
		("GET", "/api/v1/purchases/units", None),
		("GET", "/api/v1/purchases/document-forms", None),
	]
	for method, path, params in seed_calls:
		status, raw = http_request(base, method, path, token=ctx.token, params=params)
		if status == 200:
			try:
				collect_ids(json.loads(raw), ctx)
			except json.JSONDecodeError:
				pass
	# explicit deal id for editor flows
	if ctx.ids.get("id"):
		ctx.ids.setdefault("deal_id", []).extend(ctx.ids["id"][:5])


def query_params_for(path: str, spec: dict) -> dict | None:
	if "supply-contract-templates" in path and "{template_id}" not in path:
		if "default" in path:
			return {"type": "specification"}
		if "type" in path or path.endswith("/supply-contract-templates"):
			return {"type": "specification"}
	params: dict[str, Any] = {}
	for p in spec.get("parameters", []):
		if p.get("in") != "query" or not p.get("required"):
			continue
		name = p.get("name", "")
		schema = p.get("schema", {})
		enum = schema.get("enum")
		if enum:
			params[name] = enum[0]
		elif schema.get("type") == "string":
			params[name] = "specification" if name == "type" else "test"
		elif schema.get("type") == "integer":
			params[name] = 1
	return params or None


def run_smoke(base: str, login_email: str, password: str) -> int:
	openapi_url = base.rstrip("/") + "/api/v1/openapi.json"
	with urllib.request.urlopen(openapi_url, timeout=60) as resp:
		schema = json.loads(resp.read())

	ctx = Context(token=login(base, login_email, password))
	seed_context(base, ctx)

	results = {
		"ok": [],
		"client_error": [],
		"server_error": [],
		"skipped": [],
		"network": [],
	}

	endpoints: list[tuple[str, str, dict]] = []
	for path, ops in sorted(schema.get("paths", {}).items()):
		for method, spec in ops.items():
			if method not in ("get", "post", "put", "patch", "delete"):
				continue
			full = path if path.startswith("/api/") else ("/api/v1" + path if path.startswith("/") else f"/api/v1/{path}")
			endpoints.append((method, full, spec))

	for method, path, spec in endpoints:
		if SKIP_PATH_RE.search(path):
			results["skipped"].append((method.upper(), path, "skip pattern"))
			continue
		if method in MUTATING_METHODS:
			results["skipped"].append((method.upper(), path, "mutating"))
			continue
		if path in ("/api/v1/openapi.json", "/api/v1/docs", "/api/v1/redoc"):
			continue

		concrete = substitute_path(path, ctx)
		if concrete is None:
			results["skipped"].append((method.upper(), path, "no path params"))
			continue

		params = query_params_for(path, spec)
		status, raw = http_request(base, method, concrete, token=ctx.token, params=params)
		entry = (method.upper(), concrete + (f"?{urllib.parse.urlencode(params)}" if params else ""), status, raw[:200])

		if status == 0:
			results["network"].append(entry)
		elif status >= 500:
			results["server_error"].append(entry)
		elif status >= 400:
			results["client_error"].append(entry)
		else:
			results["ok"].append(entry)

	print(f"\n=== API smoke: {base} as {login_email} ===")
	print(f"Seeded IDs: { {k: v[:3] for k, v in ctx.ids.items() if v} }")
	print(f"OK: {len(results['ok'])} | 4xx: {len(results['client_error'])} | 5xx: {len(results['server_error'])} | skipped: {len(results['skipped'])} | network: {len(results['network'])}")

	if results["server_error"]:
		print("\n--- 5xx ERRORS ---")
		for method, url, status, snippet in results["server_error"]:
			print(f"{status} {method} {url}")
			print(f"  {snippet}\n")

	if results["network"]:
		print("\n--- NETWORK ERRORS ---")
		for method, url, status, snippet in results["network"]:
			print(f"{method} {url}: {snippet}")

	# group 4xx for review (exclude expected 404)
	unexpected_4xx = [
		e for e in results["client_error"]
		if e[2] not in (401, 403, 404, 405, 422)
	]
	if unexpected_4xx:
		print(f"\n--- unexpected 4xx ({len(unexpected_4xx)}) ---")
		for method, url, status, snippet in unexpected_4xx[:30]:
			print(f"{status} {method} {url}: {snippet[:120]}")

	# dedupe 4xx by status+path pattern
	by_status = defaultdict(list)
	for method, url, status, snippet in results["client_error"]:
		by_status[status].append((method, url))
	print("\n--- 4xx summary ---")
	for status in sorted(by_status):
		print(f"  {status}: {len(by_status[status])}")

	return len(results["server_error"]) + len(results["network"])


def main() -> None:
	parser = argparse.ArgumentParser()
	parser.add_argument("--base", default="https://tradesynergy.ru")
	parser.add_argument("--login", required=True)
	parser.add_argument("--password", required=True)
	args = parser.parse_args()
	code = run_smoke(args.base, args.login, args.password)
	sys.exit(1 if code else 0)


if __name__ == "__main__":
	main()
