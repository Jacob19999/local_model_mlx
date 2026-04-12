#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PACKAGE_PATH="${ROOT_DIR}/apps/macos-ui"

if ! command -v swift >/dev/null 2>&1; then
  echo "Swift is not installed. Install Xcode or the Swift toolchain first." >&2
  exit 1
fi

exec swift run --package-path "${PACKAGE_PATH}" LocalModelApp

