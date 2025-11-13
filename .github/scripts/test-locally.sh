#!/bin/bash

# Local testing script for selective SDK testing
# This script allows developers to test the selective testing logic locally

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
BASE_REF="origin/main"
HEAD_REF="HEAD"
DRY_RUN=false
VERBOSE=false
FORCE_ALL=false

print_usage() {
  echo "Usage: $0 [OPTIONS]"
  echo ""
  echo "Options:"
  echo "  --base REF        Base reference for comparison (default: origin/main)"
  echo "  --head REF        Head reference for comparison (default: HEAD)"
  echo "  --dry-run         Show what would be tested without running tests"
  echo "  --verbose         Enable verbose output"
  echo "  --force-all       Force testing of all SDKs regardless of changes"
  echo "  --help            Show this help message"
  echo ""
  echo "Examples:"
  echo "  $0                                    # Test changed SDKs vs origin/main"
  echo "  $0 --dry-run                         # Show what would be tested"
  echo "  $0 --base HEAD~1 --head HEAD         # Test changes in last commit"
  echo "  $0 --force-all                       # Test all SDKs"
}

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
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    --verbose)
      VERBOSE=true
      shift
      ;;
    --force-all)
      FORCE_ALL=true
      shift
      ;;
    --help|-h)
      print_usage
      exit 0
      ;;
    *)
      echo -e "${RED}Unknown option: $1${NC}"
      print_usage
      exit 1
      ;;
  esac
done

cd "$PROJECT_ROOT"

echo -e "${BLUE}🔍 Schubert Toolbox - Local Selective Testing${NC}"
echo "=================================================="

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
  echo -e "${RED}❌ Not in a git repository${NC}"
  exit 1
fi

# Detect changes using our helper script
echo -e "${YELLOW}📊 Detecting changes...${NC}"
if [[ "$VERBOSE" == "true" ]]; then
  CHANGE_OUTPUT=$("$SCRIPT_DIR/detect-changes.sh" --base "$BASE_REF" --head "$HEAD_REF" --verbose)
else
  CHANGE_OUTPUT=$("$SCRIPT_DIR/detect-changes.sh" --base "$BASE_REF" --head "$HEAD_REF")
fi

# Parse the output
eval "$CHANGE_OUTPUT"

echo ""
echo -e "${BLUE}📋 Change Detection Results:${NC}"
echo "  Python SDK: $([[ "$PYTHON_CHANGED" == "true" ]] && echo -e "${GREEN}✓${NC}" || echo -e "${RED}✗${NC}")"
echo "  PHP SDK: $([[ "$PHP_CHANGED" == "true" ]] && echo -e "${GREEN}✓${NC}" || echo -e "${RED}✗${NC}")"
echo "  JavaScript SDK: $([[ "$JS_CHANGED" == "true" ]] && echo -e "${GREEN}✓${NC}" || echo -e "${RED}✗${NC}")"
echo "  Core/Shared: $([[ "$CORE_CHANGED" == "true" ]] && echo -e "${GREEN}✓${NC}" || echo -e "${RED}✗${NC}")"

# Determine SDKs to test
if [[ "$FORCE_ALL" == "true" ]]; then
  SDKS_TO_TEST="python,php,js"
  echo -e "${YELLOW}⚠️  Force all mode enabled - testing all SDKs${NC}"
elif [[ -z "$SDKS_TO_TEST" ]]; then
  echo -e "${GREEN}✅ No changes detected - no tests needed${NC}"
  exit 0
fi

IFS=',' read -ra SDK_ARRAY <<< "$SDKS_TO_TEST"

echo ""
echo -e "${BLUE}🎯 SDKs to test: ${SDK_ARRAY[*]}${NC}"

if [[ "$DRY_RUN" == "true" ]]; then
  echo -e "${YELLOW}🔍 Dry run mode - showing what would be executed:${NC}"
  for sdk in "${SDK_ARRAY[@]}"; do
    echo "  - bazel test //${sdk}/tests:run_all_tests --test_output=all"
  done
  exit 0
fi

# Run tests for each affected SDK
echo ""
echo -e "${BLUE}🧪 Running tests...${NC}"

FAILED_SDKS=()
for sdk in "${SDK_ARRAY[@]}"; do
  echo ""
  echo -e "${YELLOW}Testing ${sdk} SDK...${NC}"
  
  if bazel test "//${sdk}/tests:run_all_tests" --test_output=all; then
    echo -e "${GREEN}✅ ${sdk} tests passed${NC}"
  else
    echo -e "${RED}❌ ${sdk} tests failed${NC}"
    FAILED_SDKS+=("$sdk")
  fi
done

# Summary
echo ""
echo "=================================================="
if [[ ${#FAILED_SDKS[@]} -eq 0 ]]; then
  echo -e "${GREEN}🎉 All tests passed!${NC}"
  exit 0
else
  echo -e "${RED}❌ Tests failed for: ${FAILED_SDKS[*]}${NC}"
  exit 1
fi
