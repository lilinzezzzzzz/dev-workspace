#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_AGENTS="$SCRIPT_DIR/AGENTS.md"
CODEX_TARGET="$HOME/.codex/AGENTS.md"
QODER_TARGET="$HOME/.qoder/AGENTS.md"

if [[ ! -f "$SOURCE_AGENTS" ]]; then
    echo "AGENTS source file not found: $SOURCE_AGENTS" >&2
    exit 1
fi

if ! command -v sha256sum >/dev/null 2>&1; then
    echo "sha256sum is required but not installed" >&2
    exit 1
fi

mkdir -p "$HOME/.codex" "$HOME/.qoder"

install -m 0644 "$SOURCE_AGENTS" "$CODEX_TARGET"
install -m 0644 "$SOURCE_AGENTS" "$QODER_TARGET"

SOURCE_HASH="$(sha256sum "$SOURCE_AGENTS" | awk '{print $1}')"
CODEX_HASH="$(sha256sum "$CODEX_TARGET" | awk '{print $1}')"
QODER_HASH="$(sha256sum "$QODER_TARGET" | awk '{print $1}')"

if [[ "$SOURCE_HASH" != "$CODEX_HASH" ]]; then
    echo "sha256 verification failed for $CODEX_TARGET" >&2
    exit 1
fi

if [[ "$SOURCE_HASH" != "$QODER_HASH" ]]; then
    echo "sha256 verification failed for $QODER_TARGET" >&2
    exit 1
fi

echo "Synced and verified AGENTS.md:"
echo "  $CODEX_TARGET"
echo "  $QODER_TARGET"
echo "sha256: $SOURCE_HASH"
