#!/usr/bin/env bash

set -uo pipefail

MODE="tracer"
STRICT=0
ROOT=""

usage() {
  cat <<'USAGE'
Usage:
  audit-topic.sh --mode <program|scaffold|tracer|full|audit|refresh> [--strict] <topic-or-program-dir>

The audit is read-only. Errors always fail. Warnings fail only with --strict.
USAGE
}

while (($#)); do
  case "$1" in
    --mode)
      [[ $# -ge 2 ]] || { usage >&2; exit 2; }
      MODE="$2"
      shift 2
      ;;
    --strict)
      STRICT=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --*)
      printf 'Unknown option: %s\n' "$1" >&2
      usage >&2
      exit 2
      ;;
    *)
      if [[ -n "$ROOT" ]]; then
        printf 'Only one target directory is accepted.\n' >&2
        exit 2
      fi
      ROOT="$1"
      shift
      ;;
  esac
done

case "$MODE" in
  program|scaffold|tracer|full|audit|refresh) ;;
  *)
    printf 'Invalid mode: %s\n' "$MODE" >&2
    exit 2
    ;;
esac

[[ -n "$ROOT" ]] || { usage >&2; exit 2; }
[[ -d "$ROOT" ]] || { printf 'Target is not a directory: %s\n' "$ROOT" >&2; exit 2; }
ROOT="$(cd "$ROOT" && pwd -P)"

declare -a ERRORS=()
declare -a WARNINGS=()

error() {
  ERRORS+=("$1|$2")
}

warn() {
  WARNINGS+=("$1|$2")
}

exists_file() {
  local rel="$1"
  local code="$2"
  if [[ ! -f "$ROOT/$rel" ]]; then
    if [[ "$MODE" == "audit" ]]; then
      warn "$code" "Missing recommended file: $rel"
    else
      error "$code" "Missing required file: $rel"
    fi
  fi
}

exists_dir() {
  local rel="$1"
  local code="$2"
  if [[ ! -d "$ROOT/$rel" ]]; then
    if [[ "$MODE" == "audit" ]]; then
      warn "$code" "Missing recommended directory: $rel/"
    else
      error "$code" "Missing required directory: $rel/"
    fi
  fi
}

contains() {
  local file="$1"
  local pattern="$2"
  grep -Eq "$pattern" "$file" 2>/dev/null
}

require_heading() {
  local file="$1"
  local pattern="$2"
  local code="$3"
  local label="$4"
  if ! contains "$file" "^#{1,4}[[:space:]]+(${pattern})[[:space:]]*$"; then
    if [[ "$MODE" == "audit" ]]; then
      warn "$code" "$(realpath --relative-to="$ROOT" "$file"): missing heading '$label'"
    else
      error "$code" "$(realpath --relative-to="$ROOT" "$file"): missing heading '$label'"
    fi
  fi
}

check_frontmatter() {
  local file="$1"
  local rel
  rel="$(realpath --relative-to="$ROOT" "$file")"
  if [[ "$(sed -n '1p' "$file")" != "---" ]]; then
    warn "META001" "$rel: missing YAML frontmatter"
    return
  fi
  sed -n '2,/^---$/p' "$file" | grep -Eq '^title:[[:space:]]*.+$' || warn "META002" "$rel: missing title"
  sed -n '2,/^---$/p' "$file" | grep -Eq '^type:[[:space:]]*.+$' || warn "META003" "$rel: missing type"
  sed -n '2,/^---$/p' "$file" | grep -Eq '^status:[[:space:]]*.+$' || warn "META004" "$rel: missing status"
}

check_relative_links() {
  local file target clean base resolved rel
  if ! command -v perl >/dev/null 2>&1; then
    warn "TOOL001" "perl is unavailable; skipped Markdown link extraction"
    return
  fi
  while IFS=$'\t' read -r file target; do
    [[ -n "$file" && -n "$target" ]] || continue
    clean="$target"
    clean="${clean#<}"
    clean="${clean%>}"
    case "$clean" in
      http://*|https://*|mailto:*|data:*|\#*) continue ;;
    esac
    clean="${clean%%#*}"
    clean="$(perl -e '$s=shift; $s =~ s/%([0-9A-Fa-f]{2})/chr(hex($1))/eg; print $s' "$clean")"
    clean="$(printf '%s' "$clean" | sed -E 's/:[0-9]+$//')"
    [[ -n "$clean" ]] || continue
    base="$(dirname "$file")"
    if [[ "$clean" = /* ]]; then
      resolved="$clean"
    else
      resolved="$base/$clean"
    fi
    if [[ ! -e "$resolved" ]]; then
      rel="$(realpath --relative-to="$ROOT" "$file")"
      warn "LINK001" "$rel: broken local link '$target'"
    fi
  done < <(find "$ROOT" -type f -name '*.md' -print0 | xargs -0 -r perl -ne 'while (/\]\(([^)]+)\)/g) { print "$ARGV\t$1\n" }')
}

check_program() {
  exists_file "research-program.yaml" "PROG001"
  exists_dir "00-index" "PROG002"
  exists_dir "topics" "PROG003"
  exists_file "00-index/topic-registry.md" "PROG004"
  exists_file "00-index/component-registry.md" "PROG005"
  exists_file "00-index/baseline-registry.md" "PROG006"
  exists_file "00-index/concept-registry.md" "PROG007"
  exists_file "00-index/cross-topic-claims.md" "PROG008"
  exists_file "00-index/coverage-matrix.md" "PROG009"
  exists_file "00-index/visual-registry.md" "PROG010"
  exists_dir "labs" "PROG011"
  exists_file "labs/README.md" "PROG015"

  if [[ -f "$ROOT/research-program.yaml" ]]; then
    for key in schema_version program_id title status topic_registry component_registry baseline_registry concept_registry visual_registry; do
      grep -Eq "^${key}:[[:space:]]*.+$" "$ROOT/research-program.yaml" || error "PROG012" "research-program.yaml: missing key '$key'"
    done
  fi

  local registry
  for registry in "$ROOT"/00-index/*.md; do
    [[ -f "$registry" ]] && check_frontmatter "$registry"
  done
  [[ -f "$ROOT/labs/README.md" ]] && check_frontmatter "$ROOT/labs/README.md"

  if [[ -f "$ROOT/00-index/topic-registry.md" ]]; then
    grep -Eq 'D[0-5]' "$ROOT/00-index/topic-registry.md" || warn "PROG013" "topic-registry.md: no D0-D5 target depth found"
  fi
  if [[ -f "$ROOT/00-index/baseline-registry.md" ]]; then
    grep -Eqi 'commit|version|tag' "$ROOT/00-index/baseline-registry.md" || warn "PROG014" "baseline-registry.md: no version/commit columns found"
  fi
  check_relative_links
}

check_topic_scaffold() {
  exists_file "research-manifest.yaml" "TOPIC001"
  exists_file "CONTEXT.md" "TOPIC002"
  exists_file "大纲.md" "TOPIC003"
  exists_dir "claims" "TOPIC004"
  exists_file "claims/claim-ledger.md" "TOPIC005"
  exists_file "claims/conflicts.md" "TOPIC006"
  exists_dir "source-maps" "TOPIC007"
  exists_file "source-maps/README.md" "TOPIC008"
  exists_dir "experiments" "TOPIC009"
  exists_file "experiments/README.md" "TOPIC010"
  exists_dir "Q&A" "TOPIC011"
  exists_file "Q&A/README.md" "TOPIC012"

  if [[ -f "$ROOT/research-manifest.yaml" ]]; then
    local key
    for key in schema_version topic_id title mode status primary_archetype primary_baselines experiment_baselines; do
      grep -Eq "^${key}:[[:space:]]*.*$" "$ROOT/research-manifest.yaml" || warn "TOPIC013" "research-manifest.yaml: missing key '$key'"
    done
  fi

  [[ -f "$ROOT/CONTEXT.md" ]] && {
    require_heading "$ROOT/CONTEXT.md" "Total Question" "CTX001" "Total Question"
    require_heading "$ROOT/CONTEXT.md" "Scope" "CTX002" "Scope"
    require_heading "$ROOT/CONTEXT.md" "Evidence Baselines" "CTX003" "Evidence Baselines"
    require_heading "$ROOT/CONTEXT.md" "Source–Experiment Boundary|Source-Experiment Boundary" "CTX004" "Source–Experiment Boundary"
    require_heading "$ROOT/CONTEXT.md" "Core Terms" "CTX005" "Core Terms"
  }

  [[ -f "$ROOT/大纲.md" ]] && {
    require_heading "$ROOT/大纲.md" "Question And Coverage Ledger|Question And Coverage|Question Ledger|问题账本" "OUT001" "Question/Coverage Ledger"
    require_heading "$ROOT/大纲.md" "Archetype Selection" "OUT002" "Archetype Selection"
    require_heading "$ROOT/大纲.md" "Article Dependency Graph|文章树" "OUT003" "Article Dependency Graph"
  }
}

check_claims() {
  local ledger="$ROOT/claims/claim-ledger.md"
  [[ -f "$ledger" ]] || return

  local ids_file all_ids_file rows_file id count dup
  ids_file="$(mktemp)"
  all_ids_file="$(mktemp)"
  rows_file="$(mktemp)"

  awk '
    /^##[[:space:]]+Claims[[:space:]]*$/ {in_claims=1; next}
    /^##[[:space:]]+/ && in_claims {in_claims=0}
    in_claims && /^[[:space:]]*\|[[:space:]]*CLM-[A-Z0-9-]+[[:space:]]*\|/ {print}
  ' "$ledger" > "$rows_file"

  awk -F'|' '{
    id=$2; gsub(/^[[:space:]]+|[[:space:]]+$/, "", id); print id
  }' "$rows_file" > "$ids_file"

  if [[ ! -s "$ids_file" ]]; then
    if [[ "$MODE" == "scaffold" ]]; then
      rm -f "$ids_file" "$all_ids_file" "$rows_file"
      return
    elif [[ "$MODE" == "audit" ]]; then
      warn "CLM001" "Claim Ledger contains no primary Claim rows"
    else
      error "CLM001" "Claim Ledger contains no primary Claim rows"
    fi
    rm -f "$ids_file" "$all_ids_file" "$rows_file"
    return
  fi

  dup="$(sort "$ids_file" | uniq -d | head -n 1)"
  [[ -z "$dup" ]] || error "CLM002" "Duplicate primary Claim row: $dup"

  find "$ROOT" -type f -name '*.md' -print0 | xargs -0 -r grep -Eho 'CLM-[A-Z0-9][A-Z0-9-]*-[0-9]{3}' | sort -u > "$all_ids_file"
  while IFS= read -r id; do
    grep -Fxq "$id" "$ids_file" || error "CLM003" "Claim used outside Ledger but not defined: $id"
  done < "$all_ids_file"

  while IFS= read -r id; do
    count="$(find "$ROOT" -type f -name '*.md' -print0 | xargs -0 -r grep -Fho "$id" | wc -l)"
    if [[ "$MODE" == "tracer" || "$MODE" == "full" || "$MODE" == "refresh" ]]; then
      ((count >= 4)) || error "CLM004" "$id has only $count occurrence(s); expected Ledger + source-map + experiment + reader consumer"
    elif ((count < 2)); then
      warn "CLM004" "$id has no consumer outside its primary Ledger row"
    fi
  done < "$ids_file"

  while IFS= read -r line; do
    [[ "$line" =~ \|[[:space:]]*(contract|implementation|observation|performance|historical|portability|security)[[:space:]]*\| ]] || warn "CLM005" "Claim row has an unknown or missing Claim Type: $line"
    [[ "$line" =~ \|[[:space:]]*(open|supported|bounded|contradicted|superseded|stale)[[:space:]]*\| ]] || warn "CLM006" "Claim row has an unknown or missing status: $line"
    [[ "$line" =~ G[0-3][[:space:]]*\[PE[0-2][[:space:]]+EX[0-2][[:space:]]+VA[0-2][[:space:]]+AC[0-2][[:space:]]+RR[0-2][[:space:]]+TS=(local|implementation|family|standard)\] ]] || warn "CLM007" "Claim row has no valid evidence vector: $line"
  done < "$rows_file"
  rm -f "$ids_file" "$all_ids_file" "$rows_file"
}

check_source_maps() {
  local count=0 file
  if [[ -d "$ROOT/source-maps" ]]; then
    count="$(find "$ROOT/source-maps" -maxdepth 1 -type f -name '*.md' ! -name 'README.md' | wc -l)"
  fi
  if [[ "$MODE" == "tracer" || "$MODE" == "full" || "$MODE" == "refresh" ]]; then
    ((count > 0)) || error "SRC001" "No source-map record found"
  fi
  while IFS= read -r -d '' file; do
    if [[ "$MODE" == "audit" ]] && ! grep -Eq '(^##[[:space:]]+Claim Scope|CLM-[A-Z0-9][A-Z0-9-]*-[0-9]{3})' "$file"; then
      warn "SRC000" "$(realpath --relative-to="$ROOT" "$file"): legacy source-map schema; migrate to Claim IDs before strict tracer/full audit"
      continue
    fi
    require_heading "$file" "Claim Scope" "SRC002" "Claim Scope"
    require_heading "$file" "Evidence Boundary" "SRC003" "Evidence Boundary"
    require_heading "$file" "Dispatch And Build Selection|Dispatch / Build Selection" "SRC004" "Dispatch And Build Selection"
    require_heading "$file" "Competing Models" "SRC005" "Competing Models"
    require_heading "$file" "Core Claims" "SRC006" "Core Claims"
    require_heading "$file" "Object Classification" "SRC007" "Object Classification"
    require_heading "$file" "Archetype Chain|Call / State Chains" "SRC008" "Archetype Chain"
    require_heading "$file" "Experiment Alignment" "SRC009" "Experiment Alignment"
    require_heading "$file" "Open Questions" "SRC010" "Open Questions"
    grep -Eq 'CLM-[A-Z0-9][A-Z0-9-]*-[0-9]{3}' "$file" || warn "SRC011" "$(realpath --relative-to="$ROOT" "$file"): no Claim ID"
  done < <(find "$ROOT/source-maps" -maxdepth 1 -type f -name '*.md' ! -name 'README.md' -print0 2>/dev/null)
}

check_experiments() {
  local count=0 file
  if [[ -d "$ROOT/experiments" ]]; then
    count="$(find "$ROOT/experiments" -maxdepth 1 -type f -name '*.md' ! -name 'README.md' | wc -l)"
  fi
  if [[ "$MODE" == "tracer" || "$MODE" == "full" || "$MODE" == "refresh" ]]; then
    ((count > 0)) || error "EXP001" "No experiment record found"
  fi
  while IFS= read -r -d '' file; do
    if [[ "$MODE" == "audit" ]] && ! grep -Eq '(^##[[:space:]]+Identity|EXP-[A-Z0-9][A-Z0-9-]*-(MECH|BENCH|CONC|FAULT|CROSS)-[0-9]{3})' "$file"; then
      warn "EXP000" "$(realpath --relative-to="$ROOT" "$file"): legacy experiment schema; migrate identity, hypotheses, safety, OBS and cleanup fields"
      continue
    fi
    require_heading "$file" "Identity" "EXP002" "Identity"
    require_heading "$file" "Safety And Isolation" "EXP003" "Safety And Isolation"
    require_heading "$file" "Environment And Provenance|Environment" "EXP004" "Environment And Provenance"
    require_heading "$file" "Hypotheses Before Running" "EXP005" "Hypotheses Before Running"
    require_heading "$file" "Commands" "EXP006" "Commands"
    require_heading "$file" "Raw Output" "EXP007" "Raw Output"
    require_heading "$file" "Observations" "EXP008" "Observations"
    require_heading "$file" "Conclusions" "EXP009" "Conclusions"
    require_heading "$file" "Cannot Prove" "EXP010" "Cannot Prove"
    require_heading "$file" "Source Closure" "EXP011" "Source Closure"
    require_heading "$file" "Cleanup Verification" "EXP012" "Cleanup Verification"
    grep -Eq 'EXP-[A-Z0-9][A-Z0-9-]*-(MECH|BENCH|CONC|FAULT|CROSS)-[0-9]{3}' "$file" || warn "EXP013" "$(realpath --relative-to="$ROOT" "$file"): no valid Experiment ID"
    grep -Eq 'OBS-[A-Z0-9][A-Z0-9-]*-[0-9]{3}' "$file" || warn "EXP014" "$(realpath --relative-to="$ROOT" "$file"): no Observation ID"
    grep -Eq 'SAFE-[0-4]' "$file" || warn "EXP015" "$(realpath --relative-to="$ROOT" "$file"): no safety level"
  done < <(find "$ROOT/experiments" -maxdepth 1 -type f -name '*.md' ! -name 'README.md' -print0 2>/dev/null)
}

check_reader_docs() {
  local count=0 file
  if [[ -d "$ROOT/Q&A" ]]; then
    count="$(find "$ROOT/Q&A" -maxdepth 1 -type f -name '*.md' ! -name 'README.md' | wc -l)"
  fi
  if [[ "$MODE" == "tracer" || "$MODE" == "full" || "$MODE" == "refresh" ]]; then
    ((count > 0)) || error "QA001" "No reader-facing Q&A article found"
  fi
  while IFS= read -r -d '' file; do
    if [[ "$MODE" == "audit" ]] && ! grep -Eq '(^##[[:space:]]+Prerequisites|CLM-[A-Z0-9][A-Z0-9-]*-[0-9]{3})' "$file"; then
      warn "QA000" "$(realpath --relative-to="$ROOT" "$file"): legacy reader schema; migrate prerequisites, Claim index, diagnostic questions and final mental model"
      continue
    fi
    require_heading "$file" "Prerequisites" "QA002" "Prerequisites"
    require_heading "$file" "最短结论|先给结论|先给锐评结论" "QA003" "最短结论"
    require_heading "$file" "术语和分层坐标|术语与分层坐标" "QA004" "术语和分层坐标"
    require_heading "$file" "关键对象" "QA005" "关键对象"
    require_heading "$file" "主原型链路" "QA006" "主原型链路"
    require_heading "$file" "什么变了，什么没变|哪些没有切换|本文不能证明什么" "QA007" "不变量/负结论"
    require_heading "$file" "诊断问题" "QA008" "诊断问题"
    require_heading "$file" "Claim 与证据索引|证据索引" "QA009" "Claim 与证据索引"
    require_heading "$file" "最终心智模型|最终固定心智模型|小结" "QA010" "最终心智模型"
    grep -Eq 'CLM-[A-Z0-9][A-Z0-9-]*-[0-9]{3}' "$file" || warn "QA011" "$(realpath --relative-to="$ROOT" "$file"): no Claim ID"
    if grep -En 'TODO|TBD|待生成|正文需要|后续再写|待补充' "$file" >/dev/null; then
      warn "QA012" "$(realpath --relative-to="$ROOT" "$file"): possible construction language"
    fi
    if awk '
      /^##[[:space:]]+(最短结论|最终心智模型|最终固定心智模型|小结)/ {inside=1; next}
      /^##[[:space:]]+/ {inside=0}
      inside && /(G3|stale|status:[[:space:]]*open)/ {found=1}
      END {exit(found ? 0 : 1)}
    ' "$file"; then
      warn "QA013" "$(realpath --relative-to="$ROOT" "$file"): G3/stale/open marker appears in a definitive summary section"
    fi
  done < <(find "$ROOT/Q&A" -maxdepth 1 -type f -name '*.md' ! -name 'README.md' -print0 2>/dev/null)
}

check_visuals() {
  [[ -d "$ROOT/images" ]] || return
  exists_file "images/README.md" "FIG001"
  local image base refs spec

  while IFS= read -r -d '' spec; do
    require_heading "$spec" "Generation Policy And Provenance|生成政策与溯源" "FIG006" "Generation Policy And Provenance"
    grep -Eq '(Chosen method|选定方式)' "$spec" || warn "FIG007" "$(realpath --relative-to="$ROOT" "$spec"): no chosen generation method"
    grep -Eq '(Image Gen prompt/candidate|Prompt|Image Gen)' "$spec" || warn "FIG008" "$(realpath --relative-to="$ROOT" "$spec"): no Image Gen attempt/prompt record"
    grep -Eq '(Deterministic exception|Deterministic exception/overlay|确定性例外)' "$spec" || warn "FIG009" "$(realpath --relative-to="$ROOT" "$spec"): no deterministic-exception decision"
  done < <(find "$ROOT/images/specs" -maxdepth 1 -type f -name '*.md' -print0 2>/dev/null)

  while IFS= read -r -d '' image; do
    base="$(basename "$image")"
    refs=0
    if [[ -d "$ROOT/Q&A" ]]; then
      refs="$(grep -RFl --include='*.md' "$base" "$ROOT/Q&A" 2>/dev/null | wc -l)"
    fi
    if [[ "$base" == *rejected* ]]; then
      ((refs == 0)) || error "FIG002" "Rejected image is referenced by reader-facing text: $base"
    elif ((refs == 0)); then
      warn "FIG003" "Orphan image has no Q&A consumer: $base"
    fi
    if [[ -f "$ROOT/images/README.md" ]]; then
      grep -Fq "$base" "$ROOT/images/README.md" || warn "FIG004" "Image is missing from visual registry: $base"
    fi
  done < <(find "$ROOT/images" -maxdepth 1 -type f \( -iname '*.png' -o -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.webp' -o -iname '*.svg' \) -print0)

  if find "$ROOT/images" -maxdepth 1 -type f \( -iname '*.png' -o -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.webp' -o -iname '*.svg' \) | grep -q .; then
    grep -Eq 'FIG-[A-Z0-9][A-Z0-9-]*-[0-9]{3}' "$ROOT/images/README.md" 2>/dev/null || warn "FIG005" "Visual registry contains no FIG IDs"
  fi
}

check_full_or_refresh() {
  if [[ "$MODE" == "full" ]]; then
    exists_file "封版矩阵.md" "FULL001"
    exists_dir "reviews" "FULL002"
    local reviews=0
    [[ -d "$ROOT/reviews" ]] && reviews="$(find "$ROOT/reviews" -maxdepth 1 -type f -name '*.md' | wc -l)"
    ((reviews > 0)) || error "FULL003" "No review record found"
    [[ -d "$ROOT/experiments/raw" ]] || warn "FULL004" "No experiments/raw directory; acceptable only if all experiments are source-only or raw artifacts are explicitly external"
  fi
  if [[ "$MODE" == "refresh" ]]; then
    exists_dir "refresh" "REF001"
    local refreshes=0
    [[ -d "$ROOT/refresh" ]] && refreshes="$(find "$ROOT/refresh" -maxdepth 1 -type f -name '*.md' | wc -l)"
    ((refreshes > 0)) || error "REF002" "No refresh record found"
    if [[ -f "$ROOT/claims/claim-ledger.md" ]] && grep -Eq '\|[[:space:]]*stale[[:space:]]*\|' "$ROOT/claims/claim-ledger.md"; then
      warn "REF003" "Claim Ledger still contains stale claims after refresh"
    fi
  fi
}

check_all_frontmatter() {
  local file
  while IFS= read -r -d '' file; do
    check_frontmatter "$file"
  done < <(find "$ROOT" -type f -name '*.md' \
    ! -path '*/experiments/raw/*' \
    ! -path '*/origin-reference/*' -print0)
}

if [[ "$MODE" == "program" ]]; then
  check_program
else
  check_topic_scaffold
  check_claims
  check_source_maps
  check_experiments
  check_reader_docs
  check_visuals
  check_full_or_refresh
  check_all_frontmatter
  check_relative_links
fi

printf 'Audit target: %s\n' "$ROOT"
printf 'Mode: %s%s\n' "$MODE" "$([[ $STRICT -eq 1 ]] && printf ' (strict)')"

if ((${#ERRORS[@]})); then
  printf '\nErrors (%d):\n' "${#ERRORS[@]}"
  for item in "${ERRORS[@]}"; do
    printf '  [%s] %s\n' "${item%%|*}" "${item#*|}"
  done
fi

if ((${#WARNINGS[@]})); then
  printf '\nWarnings (%d):\n' "${#WARNINGS[@]}"
  for item in "${WARNINGS[@]}"; do
    printf '  [%s] %s\n' "${item%%|*}" "${item#*|}"
  done
fi

printf '\nSummary: %d error(s), %d warning(s).\n' "${#ERRORS[@]}" "${#WARNINGS[@]}"

if ((${#ERRORS[@]})); then
  exit 1
fi
if ((STRICT == 1 && ${#WARNINGS[@]})); then
  exit 1
fi
exit 0
