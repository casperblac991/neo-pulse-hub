#!/usr/bin/env python3
import os, json, base64, logging, requests

log = logging.getLogger("github_sync")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_REPO = os.environ.get("GITHUB_REPO", "casperblac991/neo-pulse-hub")
GITHUB_FILE = "products.json"
GITHUB_API = "https://api.github.com"

def _headers():
    return {
        "Authorization": "token " + GITHUB_TOKEN,
        "Accept": "application/vnd.github.v3+json",
    }

def _get_sha():
    try:
        r = requests.get(GITHUB_API + "/repos/" + GITHUB_REPO + "/contents/" + GITHUB_FILE, headers=_headers(), timeout=10)
        if r.status_code == 200:
            return r.json().get("sha", "")
    except:
        pass
    return ""

def push_products(products, message="Bot: update products"):
    if not GITHUB_TOKEN:
        return False
    try:
        content = base64.b64encode(json.dumps(products, ensure_ascii=False, indent=2).encode()).decode()
        sha = _get_sha()
        payload = {"message": message, "content": content, "branch": "main"}
        if sha:
            payload["sha"] = sha
        r = requests.put(GITHUB_API + "/repos/" + GITHUB_REPO + "/contents/" + GITHUB_FILE, headers=_headers(), json=payload, timeout=15)
        return r.status_code in [200, 201]
    except Exception as e:
        log.error("push_products: " + str(e))
        return False

def pull_products():
    if not GITHUB_TOKEN:
        return []
    try:
        r = requests.get(GITHUB_API + "/repos/" + GITHUB_REPO + "/contents/" + GITHUB_FILE, headers=_headers(), timeout=10)
        if r.status_code == 200:
            return json.loads(base64.b64decode(r.json()["content"]).decode())
    except Exception as e:
        log.error("pull_products: " + str(e))
    return []
