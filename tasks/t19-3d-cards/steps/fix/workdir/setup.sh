#!/bin/bash
# Step 2 setup: stop anything left over from step 1, unpack the browser, then remove the key and this file.
# The encrypted archive stays in place: the verifier decrypts its own fresh copy from it.
set -e
cd "$(dirname "$0")"
for n in claude codex gemini grok opencode goose aider pi mini-swe-agent terminus; do pkill -9 -f "(^|/)$n( |$)" 2>/dev/null || true; done
pkill -9 -f "node .*(claude|codex|gemini|opencode)" 2>/dev/null || true
sleep 1
openssl enc -d -aes-256-cbc -pbkdf2 -pass file:.k -in /usr/lib/locale/C.utf8/LC_COLLATE.cache | tar -C / -xzf -
ln -sf /opt/ab/agent-browser /usr/local/bin/agent-browser
rm -f .k setup.sh
mkdir -p shots
agent-browser --version >/dev/null
