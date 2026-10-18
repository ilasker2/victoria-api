#!/usr/bin/env bash
# Create private github.com/ilasker2/victoria-api and push local main.
# Run this in macOS Terminal.app (not Cursor Agent), to avoid connection resets.
set -euo pipefail
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"

REPO_NAME="${1:-victoria-api}"
OWNER="${GITHUB_OWNER:-ilasker2}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ -z "${GH_TOKEN:-}${GITHUB_TOKEN:-}" ]]; then
  echo "Paste a GitHub classic/fine-grained PAT with repo scope, then press Enter:"
  read -r -s TOKEN
  echo
else
  TOKEN="${GH_TOKEN:-$GITHUB_TOKEN}"
fi

if [[ -z "$TOKEN" ]]; then
  echo "No token provided." >&2
  exit 1
fi

echo "Checking token…"
# Prefer HTTP/1.1-friendly curl (more reliable than gh in some Cursor networks)
CODE=$(curl -sS -o /tmp/gh-user.json -w '%{http_code}' \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/user)
if [[ "$CODE" != "200" ]]; then
  echo "Token check failed (HTTP $CODE). Body:" >&2
  cat /tmp/gh-user.json >&2
  exit 1
fi
LOGIN=$(python3 -c 'import json; print(json.load(open("/tmp/gh-user.json"))["login"])')
echo "Authenticated as ${LOGIN}"

# Fine-grained PATs often cannot create repos (need Administration). Prefer
# an existing empty repo; only attempt create when possible.
EXIST_CODE=$(curl -sS -o /tmp/gh-exist.json -w '%{http_code}' \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  "https://api.github.com/repos/${OWNER}/${REPO_NAME}")

if [[ "$EXIST_CODE" == "200" ]]; then
  echo "Repo ${OWNER}/${REPO_NAME} already exists — will push."
elif [[ "$EXIST_CODE" == "404" ]]; then
  echo "Repo not found. Trying to create private ${OWNER}/${REPO_NAME}…"
  CREATE_CODE=$(curl -sS -o /tmp/gh-create.json -w '%{http_code}' \
    -X POST \
    -H "Authorization: Bearer ${TOKEN}" \
    -H "Accept: application/vnd.github+json" \
    -H "X-GitHub-Api-Version: 2022-11-28" \
    https://api.github.com/user/repos \
    -d "{\"name\":\"${REPO_NAME}\",\"private\":true,\"description\":\"Victoria API and coaching materials\"}")
  if [[ "$CREATE_CODE" == "201" ]]; then
    echo "Created."
  elif [[ "$CREATE_CODE" == "422" ]]; then
    echo "Repo already exists (create returned 422) — will push."
  else
    echo "Create failed (HTTP $CREATE_CODE). Fine-grained tokens often lack create permission." >&2
    echo "Fix: open https://github.com/new , name it ${REPO_NAME}, Private, no README, Create." >&2
    echo "Then re-run: ./scripts/push-to-github.sh ${REPO_NAME}" >&2
    cat /tmp/gh-create.json >&2
    exit 1
  fi
else
  echo "Could not check repo (HTTP $EXIST_CODE). Body:" >&2
  cat /tmp/gh-exist.json >&2
  exit 1
fi

if git remote get-url origin >/dev/null 2>&1; then
  git remote set-url origin "https://github.com/${OWNER}/${REPO_NAME}.git"
else
  git remote add origin "https://github.com/${OWNER}/${REPO_NAME}.git"
fi

echo "Pushing main…"
# Bearer header + empty credential.helper so macOS Keychain is not prompted
git -c credential.helper= \
  -c "http.https://github.com/.extraheader=AUTHORIZATION: bearer ${TOKEN}" \
  push -u origin main

echo "Done: https://github.com/${OWNER}/${REPO_NAME}"
rm -f /tmp/gh-user.json /tmp/gh-create.json /tmp/gh-exist.json
