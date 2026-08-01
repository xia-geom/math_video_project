#!/usr/bin/env bash
# Shared helpers for render deliverables.

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
    local scene_file="${1:-}"
    local drive_dir
    drive_dir="$(resolve_google_drive_video_dir)"
    local programme_dir="$drive_dir/1 - Programme principal"

    case "$scene_file" in
        *scenes/erreurs_frequentes_fr/*)
            printf '%s\n' "$drive_dir/2 - Erreurs fréquentes"
            ;;
        *scenes/algebre_et_polynomes_fr/*)
            printf '%s\n' "$programme_dir/01 - Nombres réels et algèbre"
            ;;
        *scenes/fonctions_et_graphiques_fr/*)
            printf '%s\n' "$programme_dir/02 - Fonctions et graphiques"
            ;;
        *scenes/exponentielles_et_logarithmes_fr/*)
            printf '%s\n' "$programme_dir/03 - Exponentielles et logarithmes"
            ;;
        *scenes/probabilites_fr/*)
            printf '%s\n' "$programme_dir/04 - Probabilités et dénombrement"
            ;;
        *scenes/vecteurs_fr/*)
            printf '%s\n' "$programme_dir/05 - Vecteurs"
            ;;
        *scenes/matrices_fr/*)
            printf '%s\n' "$programme_dir/06 - Matrices"
            ;;
        *scenes/geometrie_fr/*)
            printf '%s\n' "$programme_dir/08 - Géométrie"
            ;;
        *scenes/trigonometrie_fr/*)
            printf '%s\n' "$programme_dir/07 - Trigonométrie"
            ;;
        *scenes/notations_fr/*)
            printf '%s\n' "$programme_dir/09 - Notations"
            ;;
        *)
            return 1
            ;;
    esac
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
