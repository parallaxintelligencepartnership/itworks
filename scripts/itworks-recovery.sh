#!/usr/bin/env bash
# Explicit recovery operations only; normal lint/resume never invokes mutations.
set -euo pipefail
umask 077
fail() { printf '%s\n' "Recovery blocked: $*" >&2; exit 1; }
[ "$#" -ge 1 ] || fail 'operation required'
operation=$1; shift
if command -v shasum >/dev/null 2>&1; then
    raw_digest() { shasum -a 256 < "$1"; }
elif command -v sha256sum >/dev/null 2>&1; then
    raw_digest() { sha256sum < "$1"; }
else fail 'SHA-256 utility required'; fi
digest() {
    local value
    value=$(raw_digest "$1" | awk '{print $1}') || return 1
    [ "${#value}" -eq 64 ] || return 1
    case "$value" in *[!0123456789abcdefABCDEF]*) return 1;; esac
    printf '%s\n' "$value"
}
valid_digest() {
    [ "${#1}" -eq 64 ] || return 1
    case "$1" in *[!0123456789abcdefABCDEF]*) return 1;; esac
}
mode() {
    local system value
    system=$(uname -s) || return 1
    case "$system" in
        Darwin) value=$(stat -f '%Lp' "$1") || return 1;;
        Linux) value=$(stat -c '%a' "$1") || return 1;;
        *) return 1;;
    esac
    [ -n "$value" ] && [ "${#value}" -le 4 ] || return 1
    case "$value" in *[!01234567]*) return 1;; esac
    printf '%s\n' "$value"
}
safe_git() {
    local repository=$1; shift
    GIT_OPTIONAL_LOCKS=0 git -c core.fsmonitor=false -C "$repository" "$@"
}
status_preflight() {
    local status
    # status may run configured clean/process filters while inspecting content.
    # Refuse these before status; never echo executable configuration values.
    if safe_git "$1" config --name-only --get-regexp '^filter\..*\.(clean|process)$' >/dev/null 2>&1; then
        fail 'Git clean/process filters require a separately reviewed snapshot method'
    else
        status=$?
        [ "$status" -eq 1 ] || fail 'cannot inspect Git filter configuration'
    fi
}
canonical() {
    case "$1" in *$'\n'*|*$'\r'*|*$'\t'*) fail 'control character in root path';; esac
    (cd "$1" && pwd -P)
}
new_path() {
    [ ! -e "$1" ] && [ ! -L "$1" ] || fail 'destination already exists'
    local parent leaf
    parent=$(dirname "$1"); leaf=$(basename "$1")
    [ "$leaf" != '.' ] && [ "$leaf" != '..' ] || fail 'unsafe destination'
    parent=$(canonical "$parent") || return 1
    printf '%s/%s\n' "$parent" "$leaf"
}
external() {
    [ "$2" != / ] || fail 'no destination can be external to filesystem root'
    case "$1/" in "$2/"*) fail 'recovery destination is inside project or plugin';; esac
}
# Enumerates only state, refuses links/special paths and unsafe manifest names.
inventory() {
    local root=$1 path relative file_digest file_mode
    [ ! -L "$root/.itworks" ] || fail 'state is a symlink; decide its target explicitly'
    [ -d "$root/.itworks" ] || fail 'state directory missing'
    find "$root/.itworks" -print0 | while IFS= read -r -d '' path; do
        relative=${path#"$root/"}
        case "$relative" in *$'\n'*|*$'\r'*|*$'\t'*) fail 'unsupported control character in state path';; esac
        [ ! -L "$path" ] || fail 'state contains symlink'
        file_mode=$(mode "$path") || fail 'cannot read state file mode'
        if [ -d "$path" ]; then printf 'D\t%s\t%s\n' "$file_mode" "$relative"
        elif [ -f "$path" ]; then
            file_digest=$(digest "$path") || fail 'cannot hash state file'
            printf 'F\t%s\t%s\t%s\n' "$file_mode" "$file_digest" "$relative"
        else fail 'state contains special file'; fi
    done || return 1
    if [ -e "$root/SHIPPED.md" ] || [ -L "$root/SHIPPED.md" ]; then
        [ -f "$root/SHIPPED.md" ] && [ ! -L "$root/SHIPPED.md" ] || fail 'SHIPPED is not a regular file'
        file_mode=$(mode "$root/SHIPPED.md") || fail 'cannot read ship history mode'
        file_digest=$(digest "$root/SHIPPED.md") || fail 'cannot hash ship history'
        printf 'F\t%s\t%s\tSHIPPED.md\n' "$file_mode" "$file_digest"
    fi
}
manifest() { inventory "$1" | LC_ALL=C sort; }
copy_state() {
    cp -pR "$1/.itworks" "$2/.itworks"
    if [ -f "$1/SHIPPED.md" ]; then cp -p "$1/SHIPPED.md" "$2/SHIPPED.md"; fi
}
verified_backup() {
    local metadata identity value project_count=0 plugin_count=0 cache_count=0 retention_count=0
    for metadata in VERIFIED manifest.tsv manifest.sha256 identity.txt identity.sha256; do
        [ -f "$1/$metadata" ] && [ ! -L "$1/$metadata" ] || fail 'backup metadata missing or symlinked'
    done
    [ ! -L "$1/payload" ] || fail 'backup payload is symlinked'
    value=$(cat "$1/VERIFIED") || fail 'cannot read backup verification marker'
    [ "$value" = verified ] || fail 'backup is not verified'
    local stored_hash actual_hash
    for metadata in identity manifest; do
        stored_hash=$(cat "$1/$metadata.sha256") || fail 'cannot read metadata hash'
        valid_digest "$stored_hash" || fail 'stored metadata hash is malformed'
        if [ "$metadata" = identity ]; then
            actual_hash=$(digest "$1/identity.txt") || fail 'cannot hash backup identity'
        else
            actual_hash=$(digest "$1/manifest.tsv") || fail 'cannot hash backup manifest'
        fi
        [ "$actual_hash" = "$stored_hash" ] || fail 'backup metadata digest mismatch'
    done
    while IFS= read -r identity || [ -n "$identity" ]; do
        value=${identity#*=}
        case "$identity" in
            project=*) project_count=$((project_count+1)); recorded_project=$value;;
            plugin=*) plugin_count=$((plugin_count+1)); recorded_plugin=$value;;
            cache=*) cache_count=$((cache_count+1)); recorded_cache=$value;;
            'retention=30 days AND two verified sessions') retention_count=$((retention_count+1)); continue;;
            *) fail 'unexpected or malformed backup identity field';;
        esac
        case "$value" in /*) ;; *) fail 'identity root must be absolute';; esac
        case "$value" in *$'\n'*|*$'\r'*|*$'\t'*|*//*|*/./*|*/../*|*/.|*/..|*/) fail 'identity root is not canonical';; esac
        if [ -d "$value" ]; then
            canonical_value=$(canonical "$value") || fail 'cannot resolve identity root'
            [ "$canonical_value" = "$value" ] || fail 'identity root now resolves elsewhere'
        fi
    done < "$1/identity.txt"
    [ "$project_count:$plugin_count:$cache_count:$retention_count" = 1:1:1:1 ] || fail 'backup identity fields missing or duplicated'
    local actual
    actual=$(manifest "$1/payload") || fail 'cannot inspect backup'
    backup_manifest=$(cat "$1/manifest.tsv") || fail 'cannot read backup manifest'
    [ "$actual" = "$backup_manifest" ] || fail 'backup hash or mode mismatch'
}
case "$operation" in
snapshot)
    [ "$#" = 4 ] || fail 'snapshot PROJECT BACKUP PLUGIN INSTALLED_CACHE'
    project=$(canonical "$1"); backup=$(new_path "$2"); plugin=$(canonical "$3"); cache=$(canonical "$4")
    external "$backup" "$project"; external "$backup" "$plugin"; external "$backup" "$cache"
    before=$(manifest "$project") || fail 'cannot inspect source'
    source_git=0; plugin_git=0
    if safe_git "$project" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
        status_preflight "$project"; source_git=1
    fi
    if safe_git "$plugin" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
        status_preflight "$plugin"; plugin_git=1
    fi
    mkdir "$backup"; mkdir "$backup/payload"
    printf '%s\n' "$before" > "$backup/manifest.tsv"
    printf 'project=%s\nplugin=%s\ncache=%s\nretention=30 days AND two verified sessions\n' "$project" "$plugin" "$cache" > "$backup/identity.txt"
    if [ "$source_git" -eq 1 ]; then
        safe_git "$project" rev-parse HEAD > "$backup/project-head.txt"
        safe_git "$project" status --porcelain=v1 -z > "$backup/project-status.bin"
    fi
    [ ! -f "$plugin/.claude-plugin/plugin.json" ] || digest "$plugin/.claude-plugin/plugin.json" > "$backup/plugin-manifest.sha256"
    if [ "$plugin_git" -eq 1 ]; then
        safe_git "$plugin" rev-parse HEAD > "$backup/plugin-head.txt"
        safe_git "$plugin" status --porcelain=v1 -z > "$backup/plugin-status.bin"
    fi
    # Content identity of the recovery/validation runtime, even in a dirty tree.
    for runtime in "$plugin"/scripts/itworks-*.sh "$plugin"/scripts/itworks-*.awk; do
        if [ -f "$runtime" ]; then
            runtime_digest=$(digest "$runtime") || fail 'cannot hash plugin runtime'
            printf '%s  %s\n' "$runtime_digest" "${runtime#"$plugin/"}"
        fi
    done > "$backup/plugin-runtime.sha256"
    copy_state "$project" "$backup/payload"
    copied_manifest=$(manifest "$backup/payload") || fail 'cannot inspect backup copy'
    [ "$copied_manifest" = "$before" ] || fail 'backup did not preserve bytes/modes'
    current_manifest=$(manifest "$project") || fail 'cannot re-inspect source'
    [ "$current_manifest" = "$before" ] || fail 'source changed during backup; retain both'
    digest "$backup/identity.txt" > "$backup/identity.sha256"
    digest "$backup/manifest.tsv" > "$backup/manifest.sha256"
    printf 'verified\n' > "$backup/VERIFIED"
    printf '%s\n' "$backup"
    ;;
staging-copy|restore-to-empty)
    [ "$#" = 2 ] || fail 'operation BACKUP EMPTY_DESTINATION'
    backup=$(canonical "$1"); destination=$(new_path "$2")
    verified_backup "$backup"
    external "$destination" "$backup"
    while IFS= read -r identity; do
        case "$identity" in project=*|plugin=*|cache=*) external "$destination" "${identity#*=}";; esac
    done < "$backup/identity.txt"
    mkdir "$destination"; copy_state "$backup/payload" "$destination"
    restored_manifest=$(manifest "$destination") || fail 'cannot inspect restored state'
    [ "$restored_manifest" = "$backup_manifest" ] || fail 'restored bytes differ; retain evidence'
    printf '%s\n' "$destination"
    ;;
verify-before-write)
    [ "$#" = 2 ] || fail 'verify-before-write PROJECT BACKUP'
    project=$(canonical "$1"); backup=$(canonical "$2")
    verified_backup "$backup"
    [ "$project" = "$recorded_project" ] || fail 'project differs from backup identity'
    current_manifest=$(manifest "$project") || fail 'cannot inspect source before write'
    [ "$current_manifest" = "$backup_manifest" ] || fail 'source changed; preserve both and reconcile'
    ;;
apply)
    [ "$#" = 4 ] || fail 'apply PROJECT BACKUP STAGING PLUGIN'
    project=$(canonical "$1"); backup=$(canonical "$2"); staging=$(canonical "$3"); plugin=$(canonical "$4")
    external "$backup" "$project"; external "$backup" "$plugin"
    external "$staging" "$project"; external "$staging" "$backup"
    verified_backup "$backup"
    [ "$project" = "$recorded_project" ] || fail 'project differs from backup identity'
    external "$staging" "$recorded_plugin"; external "$staging" "$recorded_cache"
    manifest "$staging" >/dev/null
    bash "$plugin/scripts/itworks-lint.sh" "$staging"
    # Recovery is verified in another directory before the first write.
    restore=$(mktemp -d "$(dirname "$backup")/itworks-restore.XXXXXX")
    copy_state "$backup/payload" "$restore"
    restore_manifest=$(manifest "$restore") || fail 'cannot inspect restore rehearsal'
    [ "$restore_manifest" = "$backup_manifest" ] || fail 'restore rehearsal failed'
    current_manifest=$(manifest "$project") || fail 'cannot inspect source before write'
    [ "$current_manifest" = "$backup_manifest" ] || fail 'source changed before write; preserve both'
    # Multi-file changes are NOT atomic. Stop other writers before this operation.
    rollback() {
        trap - ERR HUP INT TERM
        printf 'Apply failed; backup=%s staging=%s restore=%s\n' "$backup" "$staging" "$restore" >&2
        # Keep failed state separately; never remove the only surviving copy.
        failed=$(mktemp -d "$(dirname "$backup")/itworks-failed.XXXXXX") || exit 1
        if ! mv "$project/.itworks" "$failed/.itworks"; then fail 'restore failed; manual recovery required'; fi
        if [ -e "$project/SHIPPED.md" ]; then
            if ! mv "$project/SHIPPED.md" "$failed/SHIPPED.md"; then fail 'restore failed; manual recovery required'; fi
        fi
        if ! copy_state "$restore" "$project"; then fail 'restore failed; keep backup and failed state; manual recovery required'; fi
        restored_manifest=$(manifest "$project") || fail 'cannot inspect restored state; manual recovery required'
        if [ "$restored_manifest" != "$backup_manifest" ]; then fail 'restored hashes differ; manual recovery required'; fi
        printf 'Original state restored and verified; failed candidate retained at %s\n' "$failed" >&2
        exit 1
    }
    trap rollback ERR HUP INT TERM
    # Copy regular files individually to expose partial-write failures. No state
    # file deletion is allowed: removed staged paths mean blocked interpretation.
    while IFS= read -r -d '' path; do
        relative=${path#"$project/"}
        [ -e "$staging/$relative" ] || fail 'staging omits original state; deletion is not supported'
    done < <(find "$project/.itworks" -type f -print0)
    while IFS= read -r path; do
        relative=${path#"$staging/"}
        mkdir -p "$project/$relative"
        staged_mode=$(mode "$path") || rollback
        chmod "$staged_mode" "$project/$relative"
    done < <(find "$staging/.itworks" -type d | LC_ALL=C sort)
    while IFS= read -r path; do
        relative=${path#"$staging/"}
        mkdir -p "$(dirname "$project/$relative")"
        cp -p "$path" "$project/$relative"
    done < <(find "$staging/.itworks" -type f | LC_ALL=C sort)
    if [ -f "$staging/SHIPPED.md" ]; then cp -p "$staging/SHIPPED.md" "$project/SHIPPED.md"; fi
    bash "$plugin/scripts/itworks-lint.sh" "$project"
    applied_manifest=$(manifest "$project") || rollback
    staged_manifest=$(manifest "$staging") || rollback
    [ "$applied_manifest" = "$staged_manifest" ] || rollback
    trap - ERR HUP INT TERM
    printf 'Applied; retain backup %s\n' "$backup"
    ;;
*) fail 'unknown recovery operation';;
esac
