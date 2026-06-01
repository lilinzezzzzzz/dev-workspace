#!/usr/bin/env bash
set -euo pipefail

# Default config. Edit these values for a different local environment, or
# override them at runtime with NAVICAT_DIR, NAVICAT_APPIMAGE, and NAVICAT_PROXY.
DEFAULT_NAVICAT_DIR="/home/lilinze/workspace"
DEFAULT_NAVICAT_APPIMAGE="navicat17-premium-lite-cs-x86_64.AppImage"
DEFAULT_NAVICAT_PROXY="http://127.0.0.1:7897"

navicat_dir="${NAVICAT_DIR:-$DEFAULT_NAVICAT_DIR}"
navicat_appimage="${NAVICAT_APPIMAGE:-$DEFAULT_NAVICAT_APPIMAGE}"
proxy_url="${NAVICAT_PROXY-$DEFAULT_NAVICAT_PROXY}"

cd "$navicat_dir"

exec env \
  HTTP_PROXY="$proxy_url" \
  HTTPS_PROXY="$proxy_url" \
  ALL_PROXY="$proxy_url" \
  http_proxy="$proxy_url" \
  https_proxy="$proxy_url" \
  all_proxy="$proxy_url" \
  "./$navicat_appimage"
