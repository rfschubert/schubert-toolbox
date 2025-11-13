#!/bin/bash

# Helper script for detecting changes and determining which SDKs need testing
# This script can be used locally or in CI environments

set -e

# Default values
BASE_REF="origin/main"
HEAD_REF="HEAD"
VERBOSE=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --base)
      BASE_REF="$2"
      shift 2
      ;;
    --head)
      HEAD_REF="$2"
      shift 2
      ;;
    --verbose|-v)
      VERBOSE=true
      shift
      ;;
    --help|-h)
      echo "Usage: $0 [--base BASE_REF] [--head HEAD_REF] [--verbose]"
      echo "  --base: Base reference for comparison (default: origin/main)"
      echo "  --head: Head reference for comparison (default: HEAD)"
      echo "  --verbose: Enable verbose output"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Function to check if files matching pattern have changed
check_changes() {
  local pattern="$1"
  local name="$2"
  
  if git diff --name-only "$BASE_REF..$HEAD_REF" | grep -E "$pattern" > /dev/null; then
    echo "true"
    [[ "$VERBOSE" == "true" ]] && echo "  ✓ $name files changed" >&2
  else
    echo "false"
    [[ "$VERBOSE" == "true" ]] && echo "  ✗ No $name files changed" >&2
  fi
}

# Function to get changed files for a pattern
get_changed_files() {
  local pattern="$1"
  git diff --name-only "$BASE_REF..$HEAD_REF" | grep -E "$pattern" || true
}

[[ "$VERBOSE" == "true" ]] && echo "Comparing $BASE_REF..$HEAD_REF" >&2

# Check for changes in each SDK
PYTHON_CHANGED=$(check_changes "^python/" "Python")
PHP_CHANGED=$(check_changes "^php/" "PHP")
JS_CHANGED=$(check_changes "^js/" "JavaScript")

# Check for core/shared file changes
CORE_PATTERNS="^(docs/|schemas/|BUILD\.bazel|WORKSPACE|MODULE\.bazel|\.bazelrc|\.bazelignore|README\.md|AGENTS\.md)"
CORE_CHANGED=$(check_changes "$CORE_PATTERNS" "Core")

# Determine which SDKs need testing
SDKS_TO_TEST=()

if [[ "$CORE_CHANGED" == "true" ]]; then
  [[ "$VERBOSE" == "true" ]] && echo "Core files changed - testing all SDKs" >&2
  SDKS_TO_TEST=("python" "php" "js")
else
  [[ "$PYTHON_CHANGED" == "true" ]] && SDKS_TO_TEST+=("python")
  [[ "$PHP_CHANGED" == "true" ]] && SDKS_TO_TEST+=("php")
  [[ "$JS_CHANGED" == "true" ]] && SDKS_TO_TEST+=("js")
fi

# Output results
echo "PYTHON_CHANGED=$PYTHON_CHANGED"
echo "PHP_CHANGED=$PHP_CHANGED"
echo "JS_CHANGED=$JS_CHANGED"
echo "CORE_CHANGED=$CORE_CHANGED"

if [[ ${#SDKS_TO_TEST[@]} -gt 0 ]]; then
  echo "SDKS_TO_TEST=$(printf '%s,' "${SDKS_TO_TEST[@]}" | sed 's/,$//')"
  echo "TEST_MATRIX=$(printf '"%s",' "${SDKS_TO_TEST[@]}" | sed 's/,$//' | sed 's/^/[/' | sed 's/$/]/')"
else
  echo "SDKS_TO_TEST="
  echo "TEST_MATRIX=[]"
fi

[[ "$VERBOSE" == "true" ]] && echo "SDKs to test: ${SDKS_TO_TEST[*]:-none}" >&2

# Exit with appropriate code
if [[ ${#SDKS_TO_TEST[@]} -gt 0 ]]; then
  exit 0
else
  [[ "$VERBOSE" == "true" ]] && echo "No SDK changes detected - no tests needed" >&2
  exit 0
fi
