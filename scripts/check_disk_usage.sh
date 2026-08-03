#!/usr/bin/env bash

set -euo pipefail

threshold="${DISK_USAGE_THRESHOLD:-80}"
mount_point="${DISK_USAGE_MOUNT:-/}"

if [[ ! "$threshold" =~ ^[0-9]+$ ]] || (( threshold < 1 || threshold > 100 )); then
  echo "DISK_USAGE_THRESHOLD 必须是 1 到 100 之间的整数" >&2
  exit 2
fi

usage="$(df -P "$mount_point" | awk 'NR == 2 { gsub(/%/, "", $5); print $5 }')"
if [[ ! "$usage" =~ ^[0-9]+$ ]]; then
  echo "无法读取挂载点 ${mount_point} 的磁盘使用率" >&2
  exit 2
fi

if (( usage >= threshold )); then
  message="磁盘使用率告警: mount=${mount_point} usage=${usage}% threshold=${threshold}%"
  logger -p daemon.err -t dev-workspace-disk-usage -- "$message"
  echo "$message" >&2
  exit 1
fi
