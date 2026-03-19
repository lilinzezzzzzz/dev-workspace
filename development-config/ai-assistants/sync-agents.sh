#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_AGENTS_FILE="$SCRIPT_DIR/AGENTS.md"
SOURCE_AGENTS_DIR="$SCRIPT_DIR/agents"
SOURCE_SKILLS_DIR="$SCRIPT_DIR/skills"
CODEX_ROOT="${CODEX_ROOT:-$HOME/.codex}"
QODER_ROOT="${QODER_ROOT:-$HOME/.qoder}"

require_command() {
    local command_name="$1"

    if ! command -v "$command_name" >/dev/null 2>&1; then
        echo "$command_name is required but not installed" >&2
        exit 1
    fi
}

trim_spaces() {
    local value="$1"

    value="${value#"${value%%[![:space:]]*}"}"
    value="${value%"${value##*[![:space:]]}"}"
    printf '%s\n' "$value"
}

verify_file_copy() {
    local source_path="$1"
    local dest_path="$2"
    local source_hash=""
    local dest_hash=""

    source_hash="$(sha256sum "$source_path" | awk '{print $1}')"
    dest_hash="$(sha256sum "$dest_path" | awk '{print $1}')"

    if [[ "$source_hash" != "$dest_hash" ]]; then
        echo "sha256 verification failed for $dest_path" >&2
        exit 1
    fi
}

sync_path() {
    local source_path="$1"
    local dest_path="$2"
    local dest_parent=""
    local base_name=""
    local staging_path=""

    dest_parent="$(dirname "$dest_path")"
    mkdir -p "$dest_parent"

    if [[ -f "$source_path" ]]; then
        install -m 0644 "$source_path" "$dest_path"
        verify_file_copy "$source_path" "$dest_path"
        echo "Synced file -> $dest_path"
        return 0
    fi

    if [[ ! -d "$source_path" ]]; then
        echo "Unsupported source path: $source_path" >&2
        exit 1
    fi

    base_name="$(basename "$dest_path")"
    staging_path="$(mktemp -d "$dest_parent/.${base_name}.XXXXXX")"
    cp -a "$source_path"/. "$staging_path"/
    rm -rf "$dest_path"
    mv "$staging_path" "$dest_path"

    if ! diff -qr "$source_path" "$dest_path" >/dev/null; then
        echo "directory verification failed for $dest_path" >&2
        exit 1
    fi

    echo "Synced directory -> $dest_path"
}

choose_content() {
    echo "Select content to sync:" >&2
    local content=""

    select content in "AGENTS.md" "agents" "skills" "Exit"; do
        case "$content" in
            "AGENTS.md"|"agents"|"skills")
                printf '%s\n' "$content"
                return 0
                ;;
            "Exit")
                exit 0
                ;;
            *)
                echo "Invalid selection, try again." >&2
                ;;
        esac
    done
}

choose_target_root() {
    echo "Select target assistant:" >&2
    local target=""

    select target in "codex" "qoder" "Exit"; do
        case "$target" in
            codex)
                printf '%s\n' "$CODEX_ROOT"
                return 0
                ;;
            qoder)
                printf '%s\n' "$QODER_ROOT"
                return 0
                ;;
            "Exit")
                exit 0
                ;;
            *)
                echo "Invalid selection, try again." >&2
                ;;
        esac
    done
}

discover_skills() {
    local skill_dir=""
    local -a skills=()

    while IFS= read -r skill_dir; do
        if [[ -f "$skill_dir/SKILL.md" ]]; then
            skills+=("$skill_dir")
        fi
    done < <(find "$SOURCE_SKILLS_DIR" -mindepth 1 -maxdepth 1 -type d | sort)

    printf '%s\n' "${skills[@]}"
}

choose_skill() {
    local -a skills=("$@")
    local -a skill_names=()
    local index=0
    local selected_name=""

    if [[ "${#skills[@]}" -eq 0 ]]; then
        echo "No skill directories found under: $SOURCE_SKILLS_DIR" >&2
        exit 1
    fi

    for index in "${!skills[@]}"; do
        skill_names[index]="$(basename "${skills[index]}")"
    done

    echo "Available skills:" >&2
    select selected_name in "${skill_names[@]}" "Exit"; do
        case "$selected_name" in
            "")
                echo "Invalid selection, try again." >&2
                ;;
            "Exit")
                exit 0
                ;;
            *)
                printf '%s\n' "${skills[REPLY-1]}"
                return 0
                ;;
        esac
    done
}

sync_agents_file() {
    local target_root="$1"

    sync_path "$SOURCE_AGENTS_FILE" "$target_root/AGENTS.md"
}

sync_agents_dir() {
    local target_root="$1"
    local target_dir="$target_root/agents"
    local entry=""
    local entry_count=0

    mkdir -p "$target_dir"

    while IFS= read -r entry; do
        sync_path "$entry" "$target_dir/$(basename "$entry")"
        entry_count=$((entry_count + 1))
    done < <(find "$SOURCE_AGENTS_DIR" -mindepth 1 -maxdepth 1 ! -name '.gitkeep' | sort)

    if [[ "$entry_count" -eq 0 ]]; then
        echo "No syncable entries found under $SOURCE_AGENTS_DIR. Ensured target directory exists: $target_dir"
    fi
}

sync_skill_dir() {
    local -a skills=()
    local skill=""
    local selected_skill=""
    local target_root=""

    while IFS= read -r skill; do
        [[ -n "$skill" ]] && skills+=("$skill")
    done < <(discover_skills)

    selected_skill="$(choose_skill "${skills[@]}")"
    target_root="$(choose_target_root)"
    sync_path "$selected_skill" "$target_root/skills/$(basename "$selected_skill")"
}

sync_selected_content() {
    local content="$1"
    local target_root="$2"

    case "$content" in
        "AGENTS.md")
            sync_agents_file "$target_root"
            ;;
        agents)
            sync_agents_dir "$target_root"
            ;;
        skills)
            sync_skill_dir
            ;;
        *)
            echo "Unsupported content type: $content" >&2
            exit 1
            ;;
    esac
}

main() {
    local content=""
    local target_root=""
    local continue_sync=""

    if [[ $# -ne 0 ]]; then
        echo "This script is interactive and does not accept command-line arguments." >&2
        exit 1
    fi

    if [[ ! -f "$SOURCE_AGENTS_FILE" ]]; then
        echo "AGENTS source file not found: $SOURCE_AGENTS_FILE" >&2
        exit 1
    fi

    if [[ ! -d "$SOURCE_AGENTS_DIR" ]]; then
        echo "Agents source directory not found: $SOURCE_AGENTS_DIR" >&2
        exit 1
    fi

    if [[ ! -d "$SOURCE_SKILLS_DIR" ]]; then
        echo "Skills source directory not found: $SOURCE_SKILLS_DIR" >&2
        exit 1
    fi

    require_command sha256sum
    require_command diff

    while true; do
        content="$(choose_content)"
        if [[ "$content" == "skills" ]]; then
            sync_skill_dir
        else
            target_root="$(choose_target_root)"
            target_root="$(trim_spaces "$target_root")"

            if [[ -z "$target_root" ]]; then
                echo "Target root cannot be empty." >&2
                exit 1
            fi

            sync_selected_content "$content" "$target_root"
        fi

        read -r -p "Sync another item? [y/N]: " continue_sync
        continue_sync="$(trim_spaces "$continue_sync")"
        if [[ ! "$continue_sync" =~ ^([yY]|[yY][eE][sS])$ ]]; then
            break
        fi
    done
}

main "$@"
