#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CODEX_TARGET="${CODEX_TARGET:-$HOME/.codex/skills}"
QODER_TARGET="${QODER_TARGET:-$HOME/.qoder/skills}"

discover_skills() {
    local skill_dir=""
    local -a dirs=()

    while IFS= read -r skill_dir; do
        dirs+=("$skill_dir")
    done < <(
        find "$SCRIPT_DIR" -mindepth 1 -maxdepth 1 -type d | sort
    )

    local -a skills=()
    for skill_dir in "${dirs[@]}"; do
        if [[ -f "$skill_dir/SKILL.md" ]]; then
            skills+=("$skill_dir")
        fi
    done

    printf '%s\n' "${skills[@]}"
}

choose_skill() {
    local -a skills=("$@")
    local -a skill_names=()
    local index=0

    if [[ "${#skills[@]}" -eq 0 ]]; then
        echo "No skill directories found under: $SCRIPT_DIR" >&2
        exit 1
    fi

    for index in "${!skills[@]}"; do
        skill_names[index]="$(basename "${skills[index]}")"
    done

    echo "Available skills:" >&2
    local skill_name=""
    select skill_name in "${skill_names[@]}" "Exit"; do
        case "$skill_name" in
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

choose_target() {
    echo "Select target:" >&2
    local target=""
    select target in "codex" "qoder" "both" "custom" "Exit"; do
        case "$target" in
            codex|qoder|both)
                printf '%s\n' "$target"
                return 0
                ;;
            custom)
                local custom_target=""
                read -r -p "Enter custom skill root directory: " custom_target >&2
                custom_target="${custom_target#"${custom_target%%[![:space:]]*}"}"
                custom_target="${custom_target%"${custom_target##*[![:space:]]}"}"
                custom_target="${custom_target/#\~/$HOME}"

                if [[ -z "$custom_target" ]]; then
                    echo "Invalid target path: path cannot be empty." >&2
                    exit 1
                fi

                if [[ "$custom_target" != /* ]]; then
                    echo "Invalid target path: $custom_target" >&2
                    exit 1
                fi

                if [[ -e "$custom_target" && ! -d "$custom_target" ]]; then
                    echo "Invalid target path: $custom_target" >&2
                    exit 1
                fi

                printf 'custom:%s\n' "$custom_target"
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

copy_skill() {
    local source_dir="$1"
    local target_root="$2"
    local skill_name
    local dest_dir
    local staging_dir

    skill_name="$(basename "$source_dir")"
    dest_dir="$target_root/$skill_name"

    mkdir -p "$target_root"
    staging_dir="$(mktemp -d "$target_root/.${skill_name}.XXXXXX")"
    cp -a "$source_dir"/. "$staging_dir"/
    rm -rf "$dest_dir"
    mv "$staging_dir" "$dest_dir"

    echo "Synced $skill_name -> $dest_dir"
}

main() {
    mapfile -t skills < <(discover_skills)

    local selected_skill=""
    local selected_target=""
    local custom_target=""
    selected_skill="$(choose_skill "${skills[@]}")"
    selected_target="$(choose_target)"

    case "$selected_target" in
        codex)
            copy_skill "$selected_skill" "$CODEX_TARGET"
            ;;
        qoder)
            copy_skill "$selected_skill" "$QODER_TARGET"
            ;;
        both)
            copy_skill "$selected_skill" "$CODEX_TARGET"
            copy_skill "$selected_skill" "$QODER_TARGET"
            ;;
        custom:*)
            custom_target="${selected_target#custom:}"
            copy_skill "$selected_skill" "$custom_target"
            ;;
    esac
}

main "$@"
