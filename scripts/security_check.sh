#!/usr/bin/env bash
set -euo pipefail

disallowed_tracked_pattern='(^|/)(\.env(\..*)?|id_(rsa|dsa|ecdsa|ed25519)|secrets/|private/|credentials/)|\.(pem|key|p12|pfx|crt|cer|der|kubeconfig|sqlite|sqlite3|db)$'

if git ls-files | grep -E "$disallowed_tracked_pattern" | grep -v '^\.env\.example$' >/tmp/nidaryx_disallowed_files.txt; then
  echo "Disallowed sensitive-looking files are tracked:"
  cat /tmp/nidaryx_disallowed_files.txt
  exit 1
fi

secret_token_pattern='AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----|ghp_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,}|xox[baprs]-[A-Za-z0-9-]{10,}'
assignment_pattern="(secret(_key)?|password)[[:space:]]*[:=][[:space:]]*[\"'][^\"']{8,}"

set +e
git grep -n -I -E "$secret_token_pattern" -- . ':!docs/source/*.docx' >/tmp/nidaryx_secret_tokens.txt
token_status=$?
git grep -n -I -E "$assignment_pattern" -- . ':!docs/source/*.docx' >/tmp/nidaryx_secret_assignments.txt
assignment_status=$?
set -e

if [ "$token_status" -eq 0 ] || [ "$assignment_status" -eq 0 ]; then
  echo "Potential secret pattern found in tracked source."
  cat /tmp/nidaryx_secret_tokens.txt /tmp/nidaryx_secret_assignments.txt
  exit 1
fi

if [ "$token_status" -ne 1 ] || [ "$assignment_status" -ne 1 ]; then
  echo "Secret scan failed unexpectedly."
  exit 1
fi

echo "security-check-ok"
