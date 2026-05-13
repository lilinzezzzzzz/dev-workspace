#!/usr/bin/env bash
set -euo pipefail

CHECK_ONLY=0
WITH_SUDO=0
CLASH_PORT_PATTERN='7890|7891|7892|7893|7895|7897'

usage() {
  cat <<'USAGE'
用法:
  ./restore_network_no_proxy.sh [--check-only] [--with-sudo]

选项:
  --check-only   仅检查代理相关状态，不修改任何设置。
  --with-sudo    同时以 root 身份执行只读检查，包括防火墙规则、路由和系统代理文件。

本脚本用于清除 flclash/Clash 残留的常见用户级代理设置：
GNOME 代理、Git 代理、SSH ProxyCommand/ProxyJump、npm/yarn/pnpm
代理，以及 systemd 用户环境代理变量。root 级别的防火墙检查为只读，
不会修改系统配置。
USAGE
}

log() {
  printf '\n== %s ==\n' "$1"
}

run() {
  if [[ "$CHECK_ONLY" -eq 1 ]]; then
    printf '[check-only] %q' "$1"
    shift
    printf ' %q' "$@"
    printf '\n'
    return 0
  fi

  "$@"
}

has_cmd() {
  command -v "$1" >/dev/null 2>&1
}

grep_ssh_proxy_lines() {
  local file="$1"

  grep -nEi "^[[:space:]]*(proxycommand|proxyjump)[[:space:]].*((127\\.0\\.0\\.1|localhost|::1).*(${CLASH_PORT_PATTERN})|(${CLASH_PORT_PATTERN}).*(127\\.0\\.0\\.1|localhost|::1)|clash|flclash|mihomo)" "$file" || true
}

clear_gnome_proxy() {
  if ! has_cmd gsettings; then
    echo "未找到 gsettings；跳过 GNOME 代理清理。"
    return 0
  fi

  log "Clear GNOME proxy"
  run gsettings set org.gnome.system.proxy mode 'none'
  run gsettings set org.gnome.system.proxy autoconfig-url ''

  for schema in http https socks ftp; do
    run gsettings set "org.gnome.system.proxy.${schema}" host ''
    run gsettings set "org.gnome.system.proxy.${schema}" port 0
  done
}

clear_ssh_proxy_config() {
  local ssh_config="${HOME}/.ssh/config"

  if [[ ! -f "$ssh_config" ]]; then
    echo "未发现 ~/.ssh/config；跳过 SSH 代理清理。"
    return 0
  fi

  log "Clear SSH proxy config"
  local matches=()
  mapfile -t matches < <(grep_ssh_proxy_lines "$ssh_config")

  if [[ "${#matches[@]}" -eq 0 ]]; then
    echo "未发现 SSH Clash 代理配置项。"
    return 0
  fi

  printf '将清理以下 SSH 代理配置行：\n'
  printf '%s\n' "${matches[@]}"

  if [[ "$CHECK_ONLY" -eq 1 ]]; then
    echo "[check-only] 未修改 ~/.ssh/config。"
    return 0
  fi

  local backup="${ssh_config}.bak.$(date +%Y%m%d%H%M%S)"
  local tmp
  tmp="$(mktemp "${ssh_config}.tmp.XXXXXX")"

  cp -p "$ssh_config" "$backup"
  awk -v ports="$CLASH_PORT_PATTERN" '
    function suspicious(line, lower) {
      lower = tolower(line)
      if (lower !~ /^[[:space:]]*(proxycommand|proxyjump)[[:space:]]/) {
        return 0
      }
      if (lower ~ /(clash|flclash|mihomo)/) {
        return 1
      }
      if (lower ~ /(127\.0\.0\.1|localhost|::1)/ && lower ~ "(" ports ")") {
        return 1
      }
      return 0
    }
    !suspicious($0)
  ' "$ssh_config" > "$tmp"

  chmod --reference="$ssh_config" "$tmp" 2>/dev/null || chmod 600 "$tmp"
  mv "$tmp" "$ssh_config"
  echo "已备份原 SSH 配置到：${backup}"
}

clear_git_proxy() {
  if ! has_cmd git; then
    echo "未找到 git；跳过 Git 代理清理。"
    return 0
  fi

  log "Clear global Git proxy"
  local keys=()
  mapfile -t keys < <(
    git config --global --name-only --get-regexp '(^http\..*\.proxy$|^http\.proxy$|^https\.proxy$)' 2>/dev/null || true
  )

  if [[ "${#keys[@]}" -eq 0 ]]; then
    echo "未发现全局 Git 代理配置项。"
    return 0
  fi

  local key
  for key in "${keys[@]}"; do
    echo "Unset Git config: ${key}"
    run git config --global --unset-all "$key" || true
  done
}

clear_node_proxy() {
  log "Clear Node package manager proxy"

  if has_cmd npm; then
    run npm config delete proxy || true
    run npm config delete https-proxy || true
    run npm config delete noproxy || true
  else
    echo "未找到 npm；跳过 npm 代理清理。"
  fi

  if has_cmd yarn; then
    run yarn config delete proxy || true
    run yarn config delete https-proxy || true
  fi

  if has_cmd pnpm; then
    run pnpm config delete proxy || true
    run pnpm config delete https-proxy || true
    run pnpm config delete noproxy || true
  fi
}

clear_systemd_user_env() {
  if ! has_cmd systemctl; then
    echo "未找到 systemctl；跳过 systemd 用户环境清理。"
    return 0
  fi

  log "Clear systemd user proxy environment"
  run systemctl --user unset-environment \
    HTTP_PROXY HTTPS_PROXY ALL_PROXY NO_PROXY \
    http_proxy https_proxy all_proxy no_proxy \
    FTP_PROXY ftp_proxy \
    WS_PROXY WSS_PROXY ws_proxy wss_proxy \
    NPM_CONFIG_PROXY NPM_CONFIG_HTTP_PROXY NPM_CONFIG_HTTPS_PROXY NPM_CONFIG_NOPROXY \
    npm_config_proxy npm_config_http_proxy npm_config_https_proxy npm_config_noproxy \
    YARN_HTTP_PROXY YARN_HTTPS_PROXY YARN_NO_PROXY \
    DOCKER_HTTP_PROXY DOCKER_HTTPS_PROXY \
    PIP_PROXY || true
}

check_user_state() {
  log "User-level proxy state"

  echo "-- environment --"
  env | grep -Ei '^(http|https|all|no|ftp|ws|wss)_proxy=|^(HTTP|HTTPS|ALL|NO|FTP|WS|WSS)_PROXY=' || true

  if has_cmd gsettings; then
    echo "-- GNOME proxy --"
    gsettings get org.gnome.system.proxy mode || true
    gsettings list-recursively org.gnome.system.proxy \
      | grep -Ei "mode|host|port|autoconfig|7890|7891|7892|7893|7895|7897|clash|flclash|mihomo" || true
  fi

  if has_cmd git; then
    echo "-- Git proxy --"
    git config --global --get-regexp '.*proxy.*' || true
  fi

  if [[ -f "${HOME}/.ssh/config" ]]; then
    echo "-- SSH proxy --"
    grep_ssh_proxy_lines "${HOME}/.ssh/config"
  fi

  if has_cmd npm; then
    echo "-- npm proxy --"
    npm config get proxy || true
    npm config get https-proxy || true
  fi
}

check_runtime_state() {
  log "Runtime proxy-related state"

  echo "-- process --"
  ps -eo pid=,comm= | grep -Ei '(^|/)(flclash|clash|mihomo)$|flclash|clash|mihomo' || true

  echo "-- listening ports --"
  if has_cmd ss; then
    ss -ltnp | grep -Ei '7890|7891|7892|7893|7895|7897|clash|flclash|mihomo' || true
  fi

  echo "-- routing --"
  ip rule show || true
  ip route show table all | grep -Ei 'fwmark|local default|dev lo|789|clash|mihomo' || true
}

check_root_state() {
  if [[ "$WITH_SUDO" -ne 1 ]]; then
    return 0
  fi

  if ! has_cmd sudo; then
    echo "未找到 sudo；跳过 root 级别检查。"
    return 0
  fi

  log "Root-level firewall and system proxy checks"
  sudo bash -lc '
    echo "-- nft suspicious --"
    nft list ruleset 2>/dev/null | grep -Ei "clash|flclash|mihomo|7890|7891|7892|7893|7895|7897|tproxy|redirect|redir" || true

    echo "-- iptables suspicious --"
    iptables-save 2>/dev/null | grep -Ei "clash|flclash|mihomo|7890|7891|7892|7893|7895|7897|TPROXY|REDIRECT" || true

    echo "-- ip6tables suspicious --"
    ip6tables-save 2>/dev/null | grep -Ei "clash|flclash|mihomo|7890|7891|7892|7893|7895|7897|TPROXY|REDIRECT" || true

    echo "-- system proxy files suspicious --"
    grep -RInE "proxy|7890|7891|7892|7893|7895|7897|clash|flclash|mihomo" \
      /etc/environment /etc/profile /etc/profile.d /etc/apt/apt.conf.d 2>/dev/null || true
  '
}

main() {
  while [[ "$#" -gt 0 ]]; do
    case "$1" in
      --check-only)
        CHECK_ONLY=1
        ;;
      --with-sudo)
        WITH_SUDO=1
        ;;
      -h|--help)
        usage
        exit 0
        ;;
      *)
        echo "Unknown argument: $1" >&2
        usage >&2
        exit 2
        ;;
    esac
    shift
  done

  clear_gnome_proxy
  clear_git_proxy
  clear_ssh_proxy_config
  clear_node_proxy
  clear_systemd_user_env
  check_user_state
  check_runtime_state
  check_root_state

  log "Done"
  if [[ "$CHECK_ONLY" -eq 1 ]]; then
    echo "只读检查模式完成，未修改任何设置。"
  else
    echo "用户级代理清理完成。请重新打开终端和应用程序，以丢弃已继承的代理环境变量。"
  fi
  if [[ "$WITH_SUDO" -eq 0 ]]; then
    echo "如需检查 root 防火墙规则和系统代理文件，请使用 --with-sudo 参数运行。"
  fi
}

main "$@"
