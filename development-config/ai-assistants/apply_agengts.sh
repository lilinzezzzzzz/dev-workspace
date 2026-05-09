#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_RULES_DIR="$SCRIPT_DIR/rules"
SOURCE_AGENTS_FILE="$SOURCE_RULES_DIR/agents.md"
SOURCE_REFERENCES_DIR="$SOURCE_RULES_DIR/references"
SOURCE_CODEX_CONFIG_FILE="$SCRIPT_DIR/configs/codex-config.toml"
SOURCE_SKILLS_DIR="$SCRIPT_DIR/skills"
SOURCE_SHARED_SKILLS_DIR="$SOURCE_SKILLS_DIR/_shared"
CODEX_ROOT="${CODEX_ROOT:-$HOME/.codex}"
QODER_ROOT="${QODER_ROOT:-$HOME/.qoder}"
EXIT_SENTINEL="__SYNC_AGENTS_EXIT__"
ALL_SKILLS_SENTINEL="__SYNC_AGENTS_ALL_SKILLS__"
EXCLUDED_RULE_TOP_LEVEL_FILES=(
    "reference-loading-test-prompts.md"
)

require_command() {
    local command_name="$1"

    if ! command -v "$command_name" >/dev/null 2>&1; then
        echo "$command_name is required but not installed" >&2
        exit 1
    fi
}

require_file() {
    local file_path="$1"
    local description="$2"

    if [[ ! -f "$file_path" ]]; then
        echo "$description not found: $file_path" >&2
        exit 1
    fi
}

require_dir() {
    local dir_path="$1"
    local description="$2"

    if [[ ! -d "$dir_path" ]]; then
        echo "$description not found: $dir_path" >&2
        exit 1
    fi
}

command_exists() {
    local command_name="$1"

    command -v "$command_name" >/dev/null 2>&1
}

is_excluded_rule_top_level_entry() {
    local entry_path="$1"
    local entry_name=""
    local excluded_name=""

    entry_name="$(basename "$entry_path")"

    for excluded_name in "${EXCLUDED_RULE_TOP_LEVEL_FILES[@]}"; do
        if [[ "$entry_name" == "$excluded_name" ]]; then
            return 0
        fi
    done

    return 1
}

sha256_file() {
    local file_path="$1"

    if command_exists sha256sum; then
        sha256sum "$file_path" | awk '{print $1}'
        return 0
    fi

    if command_exists shasum; then
        shasum -a 256 "$file_path" | awk '{print $1}'
        return 0
    fi

    if command_exists openssl; then
        openssl dgst -sha256 -r "$file_path" | awk '{print $1}'
        return 0
    fi

    echo "A SHA-256 tool is required but not installed (tried: sha256sum, shasum, openssl)" >&2
    exit 1
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

    source_hash="$(sha256_file "$source_path")"
    dest_hash="$(sha256_file "$dest_path")"

    if [[ "$source_hash" != "$dest_hash" ]]; then
        echo "sha256 verification failed for $dest_path" >&2
        exit 1
    fi
}

assert_safe_directory_dest() {
    local dest_path="$1"

    if [[ -z "$dest_path" || "$dest_path" == "/" || "$dest_path" == "$HOME" ]]; then
        echo "Refusing to replace unsafe directory path: $dest_path" >&2
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

    assert_safe_directory_dest "$dest_path"
    base_name="$(basename "$dest_path")"
    staging_path="$(mktemp -d "$dest_parent/.${base_name}.XXXXXX")"
    cp -R "$source_path"/. "$staging_path"/
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

    while true; do
        echo "1) rules" >&2
        echo "2) skills" >&2
        echo "3) codex-config" >&2
        echo "4) exit" >&2
        read -r -p "#? " content
        content="$(trim_spaces "$content")"

        case "$content" in
            1|rules)
                printf '%s\n' "rules"
                return 0
                ;;
            2|skills)
                printf '%s\n' "skills"
                return 0
                ;;
            3|codex-config|config)
                printf '%s\n' "config"
                return 0
                ;;
            4|exit)
                printf '%s\n' "$EXIT_SENTINEL"
                return 0
                ;;
            *)
                echo "Invalid selection, try again." >&2
                ;;
        esac
    done
}

choose_rules_target() {
    echo "Select rules target:" >&2
    local target=""

    while true; do
        echo "1) codex -> AGENTS.md + references" >&2
        echo "2) qoder -> project .qoder path" >&2
        echo "3) exit" >&2
        read -r -p "#? " target
        target="$(trim_spaces "$target")"

        case "$target" in
            1|codex)
                printf '%s\n' "codex"
                return 0
                ;;
            2|qoder)
                printf '%s\n' "qoder"
                return 0
                ;;
            3|exit)
                printf '%s\n' "$EXIT_SENTINEL"
                return 0
                ;;
            *)
                echo "Invalid selection, try again." >&2
                ;;
        esac
    done
}

prompt_qoder_root_dir() {
    local target_root=""

    while true; do
        echo "Enter Qoder project .qoder path(Example: /path/to/project/.qoder):" >&2
        read -r -p "#? " target_root
        target_root="$(trim_spaces "$target_root")"

        if [[ -n "$target_root" ]]; then
            if [[ "$(basename "$target_root")" != ".qoder" ]]; then
                echo "Qoder project path must end with .qoder." >&2
                continue
            fi

            if [[ ! -d "$target_root" ]]; then
                echo "Qoder project .qoder directory not found: $target_root" >&2
                continue
            fi

            printf '%s\n' "$target_root"
            return 0
        fi

        echo "Qoder project .qoder path cannot be empty." >&2
    done
}

resolve_qoder_rules_dir() {
    local target_root="$1"

    printf '%s\n' "$target_root/rules"
}

choose_target() {
    echo "Select target assistant:" >&2
    local target=""

    select target in "both" "codex" "qoder" "exit"; do
        case "$target" in
            both|codex|qoder)
                printf '%s\n' "$target"
                return 0
                ;;
            "exit")
                printf '%s\n' "$EXIT_SENTINEL"
                return 0
                ;;
            *)
                echo "Invalid selection, try again." >&2
                ;;
        esac
    done
}

resolve_target_roots() {
    local target="$1"

    case "$target" in
        codex)
            printf '%s\n' "$CODEX_ROOT"
            ;;
        qoder)
            printf '%s\n' "$QODER_ROOT"
            ;;
        both)
            printf '%s\n' "$CODEX_ROOT"
            printf '%s\n' "$QODER_ROOT"
            ;;
        *)
            echo "Unsupported target assistant: $target" >&2
            exit 1
            ;;
    esac
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
    select selected_name in "all" "${skill_names[@]}" "exit"; do
        case "$selected_name" in
            "")
                echo "Invalid selection, try again." >&2
                ;;
            "all")
                printf '%s\n' "$ALL_SKILLS_SENTINEL"
                return 0
                ;;
            "exit")
                printf '%s\n' "$EXIT_SENTINEL"
                return 0
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
    sync_references_dir "$target_root"
}

sync_codex_config_file() {
    local target_root="$1"

    sync_path "$SOURCE_CODEX_CONFIG_FILE" "$target_root/config.toml"
}

sync_directory_entries() {
    local source_dir="$1"
    local target_dir="$2"
    local empty_message="$3"
    local entry=""
    local entry_count=0

    mkdir -p "$target_dir"

    while IFS= read -r entry; do
        sync_path "$entry" "$target_dir/$(basename "$entry")"
        entry_count=$((entry_count + 1))
    done < <(find "$source_dir" -mindepth 1 -maxdepth 1 ! -name '.gitkeep' | sort)

    if [[ "$entry_count" -eq 0 ]]; then
        echo "$empty_message. Ensured target directory exists: $target_dir"
    fi
}

sync_references_dir() {
    local target_dir="$1"

    sync_directory_entries \
        "$SOURCE_REFERENCES_DIR" \
        "$target_dir/references" \
        "No syncable entries found under $SOURCE_REFERENCES_DIR"
}

sync_qoder_rules_dir() {
    local target_dir="$1"
    local references_dir="$target_dir/references"
    local entry=""

    mkdir -p "$target_dir"

    sync_path "$SOURCE_AGENTS_FILE" "$target_dir/$(basename "$SOURCE_AGENTS_FILE")"

    while IFS= read -r entry; do
        if [[ "$entry" == "$SOURCE_AGENTS_FILE" || "$entry" == "$SOURCE_REFERENCES_DIR" ]]; then
            continue
        fi

        if is_excluded_rule_top_level_entry "$entry"; then
            continue
        fi

        sync_path "$entry" "$target_dir/$(basename "$entry")"
    done < <(find "$SOURCE_RULES_DIR" -mindepth 1 -maxdepth 1 ! -name '.gitkeep' | sort)

    sync_directory_entries \
        "$SOURCE_REFERENCES_DIR" \
        "$references_dir" \
        "No syncable entries found under $SOURCE_REFERENCES_DIR"
}

sync_skill_dir() {
    local -a skills=()
    local -a selected_skills=()
    local -a target_roots=()
    local shared_skill_dir="$SOURCE_SHARED_SKILLS_DIR"
    local skill=""
    local selected_skill=""
    local selected_target=""
    local target_root=""

    while IFS= read -r skill; do
        [[ -n "$skill" ]] && skills+=("$skill")
    done < <(discover_skills)

    selected_skill="$(choose_skill "${skills[@]}")"
    if [[ "$selected_skill" == "$EXIT_SENTINEL" ]]; then
        exit 0
    fi

    if [[ "$selected_skill" == "$ALL_SKILLS_SENTINEL" ]]; then
        selected_skills=("${skills[@]}")
    else
        selected_skills=("$selected_skill")
    fi

    selected_target="$(choose_target)"
    if [[ "$selected_target" == "$EXIT_SENTINEL" ]]; then
        exit 0
    fi

    target_roots=()
    while IFS= read -r target_root; do
        [[ -n "$target_root" ]] && target_roots+=("$target_root")
    done < <(resolve_target_roots "$selected_target")

    for target_root in "${target_roots[@]}"; do
        sync_path "$shared_skill_dir" "$target_root/skills/$(basename "$shared_skill_dir")"

        for skill in "${selected_skills[@]}"; do
            sync_path "$skill" "$target_root/skills/$(basename "$skill")"
        done
    done
}

main() {
    local content=""
    local qoder_rules_dir=""
    local qoder_root=""
    local rules_target=""

    if [[ $# -ne 0 ]]; then
        echo "This script is interactive and does not accept command-line arguments." >&2
        exit 1
    fi

    require_file "$SOURCE_AGENTS_FILE" "Codex AGENTS source file"
    require_file "$SOURCE_CODEX_CONFIG_FILE" "Codex config source file"
    require_dir "$SOURCE_RULES_DIR" "Rules source directory"
    require_dir "$SOURCE_REFERENCES_DIR" "Rules references source directory"
    require_dir "$SOURCE_SKILLS_DIR" "Skills source directory"
    require_dir "$SOURCE_SHARED_SKILLS_DIR" "Shared skills source directory"

    require_command diff

    content="$(choose_content)"
    if [[ "$content" == "$EXIT_SENTINEL" ]]; then
        exit 0
    fi

    if [[ "$content" == "skills" ]]; then
        sync_skill_dir
        return 0
    fi

    if [[ "$content" == "config" ]]; then
        CODEX_ROOT="$(trim_spaces "$CODEX_ROOT")"
        if [[ -z "$CODEX_ROOT" ]]; then
            echo "CODEX_ROOT cannot be empty." >&2
            exit 1
        fi

        sync_codex_config_file "$CODEX_ROOT"
        return 0
    fi

    rules_target="$(choose_rules_target)"
    if [[ "$rules_target" == "$EXIT_SENTINEL" ]]; then
        exit 0
    fi

    if [[ "$rules_target" == "qoder" ]]; then
        qoder_root="$(prompt_qoder_root_dir)"
        qoder_rules_dir="$(resolve_qoder_rules_dir "$qoder_root")"
        sync_qoder_rules_dir "$qoder_rules_dir"
        return 0
    fi

    CODEX_ROOT="$(trim_spaces "$CODEX_ROOT")"
    if [[ -z "$CODEX_ROOT" ]]; then
        echo "CODEX_ROOT cannot be empty." >&2
        exit 1
    fi

    sync_agents_file "$CODEX_ROOT"
}

main "$@"
