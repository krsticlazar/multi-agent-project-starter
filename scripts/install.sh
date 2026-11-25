#!/usr/bin/env bash
set -eu
shopt -s dotglob nullglob

if [[ $# != 1 || -z $1 ]]; then
    printf 'Usage: bash scripts/install.sh <project-directory>\n' >&2
    exit 2
fi

source_path=$(dirname -- "${BASH_SOURCE[0]}")/../template
if [[ -L $source_path ]]; then
    printf 'Extract the template into a real directory before installing.\n' >&2
    exit 2
fi
source_root=$(cd -P -- "$source_path" && pwd -P)
target_root=$1
while [[ $target_root != / && $target_root == */ ]]; do
    target_root=${target_root%/}
done

if [[ -L $target_root || ( -e $target_root && ! -d $target_root ) ]]; then
    printf 'Destination must be a directory, without a link at its root: %s\n' "$target_root" >&2
    exit 2
fi
if [[ -d $target_root ]]; then
    target_root=$(cd -P -- "$target_root" && pwd -P)
else
    target_parent=$(cd -P -- "$(dirname -- "$target_root")" && pwd -P)
    target_root=${target_parent%/}/$(basename -- "$target_root")
fi
case "$target_root/" in
    "$source_root/"*) printf 'Choose a destination outside the template directory.\n' >&2; exit 2 ;;
esac
if [[ ! -d $target_root ]]; then
    mkdir -- "$target_root"
fi

install_tree() {
    local source_dir=$1 target_dir=$2 prefix=$3 entry name relative destination
    for entry in "$source_dir"/*; do
        name=${entry##*/}
        relative=$prefix$name
        case "$name" in
            .git|.runtime|__pycache__|.env|.env.*|*.key|*.pem) continue ;;
        esac
        if [[ $relative == .claude/settings.local.json ]]; then
            continue
        fi
        destination=$target_dir/$name
        if [[ -L $entry ]]; then
            printf 'Skipped source link %s\n' "$relative"
        elif [[ -L $destination || ( -e $destination && ! -d $destination ) ]]; then
            printf 'Kept existing %s\n' "$relative"
        elif [[ -d $entry ]]; then
            mkdir -p -- "$destination"
            install_tree "$entry" "$destination" "$relative/"
        elif [[ -e $destination ]]; then
            printf 'Kept existing %s\n' "$relative"
        elif [[ -f $entry ]]; then
            (set -o noclobber; cat -- "$entry" > "$destination")
            printf 'Installed %s\n' "$relative"
        else
            printf 'Skipped non-regular source file %s\n' "$relative"
        fi
    done
}

install_tree "$source_root" "$target_root" ''
printf 'Installation finished in %s. Review any kept paths before running ASK_ME.md.\n' "$target_root"
