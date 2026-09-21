#!/usr/bin/env bash
# Shared helpers for render deliverables.

resolve_render_dist_dir() {
    local root_dir="$1"
    local artifact_name="$2"
    local quality="$3"
    if [[ "$quality" == "qh" ]]; then
        printf '%s\n' "$root_dir/dist/$artifact_name"
    else
        printf '%s\n' "$root_dir/dist/_previews/$quality/$artifact_name"
    fi
}

resolve_render_output_stem() {
    local artifact_name="$1"
    local quality="$2"
    if [[ "$quality" == "qh" ]]; then
        printf '%s\n' "$artifact_name"
    else
        printf '%s\n' "${artifact_name}__${quality}"
    fi
}

expand_user_path() {
    case "$1" in
        "~") printf '%s\n' "$HOME" ;;
        "~/"*) printf '%s\n' "$HOME/${1#\~/}" ;;
        *) printf '%s\n' "$1" ;;
    esac
}

resolve_google_drive_video_dir() {
    if [[ -n "${GOOGLE_DRIVE_VIDEO_DIR:-}" ]]; then
        expand_user_path "$GOOGLE_DRIVE_VIDEO_DIR"
    else
        printf '%s\n' "/Users/xiaxiao/My Drive/Math Video Project"
    fi
}

resolve_google_drive_video_theme_dir() {
    local scene_file="${1:-}" root_dir python route drive_dir
    root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
    python="${RENDER_PYTHON:-$root_dir/.venv/bin/python}"
    [[ -x "$python" ]] || python="$(command -v python3)"
    route="$("$python" "$root_dir/tools/course_catalog.py" route "$scene_file")" || return 1
    drive_dir="$(resolve_google_drive_video_dir)"
    printf '%s\n' "$drive_dir/$route"
}

copy_render_mp4_to_drive() {
    local src="$1"
    local _scene_class="$2"
    local scene_file="${3:-}"

    if [[ "${RENDER_SKIP_DRIVE_COPY:-}" == "1" || ! -f "$src" ]]; then
        return 0
    fi

    case "$src" in
        *.mp4) ;;
        *) return 0 ;;
    esac

    local drive_dir
    if ! drive_dir="$(resolve_google_drive_video_theme_dir "$scene_file")"; then
        echo "Drive MP4 skipped: unclassified scene $scene_file"
        return 0
    fi

    local target="$drive_dir/$(basename "$src")"

    if ! mkdir -p "$drive_dir"; then
        echo "WARN: could not create Google Drive folder: $drive_dir" >&2
        return 0
    fi

    if cp "$src" "$target"; then
        echo "Drive MP4: $target"
    else
        echo "WARN: could not copy MP4 to Google Drive: $target" >&2
    fi
}
