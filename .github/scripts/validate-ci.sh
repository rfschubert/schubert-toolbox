#!/bin/bash

# Validation script for the selective testing CI pipeline
# This script creates test scenarios to validate the change detection logic

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

cd "$PROJECT_ROOT"

echo -e "${BLUE}🧪 CI Pipeline Validation${NC}"
echo "=========================="

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
  echo -e "${RED}❌ Not in a git repository${NC}"
  exit 1
fi

# Function to test change detection
test_change_detection() {
  local test_name="$1"
  local files="$2"
  local expected_sdks="$3"
  
  echo ""
  echo -e "${YELLOW}🔍 Testing: $test_name${NC}"
  echo "Files: $files"
  echo "Expected SDKs: $expected_sdks"
  
  # Create a temporary branch for testing
  local test_branch="test-ci-$(date +%s)"
  git checkout -b "$test_branch" > /dev/null 2>&1
  
  # Create/modify test files
  for file in $files; do
    mkdir -p "$(dirname "$file")"
    echo "# Test change $(date)" >> "$file"
  done
  
  git add . > /dev/null 2>&1
  git commit -m "Test commit for $test_name" > /dev/null 2>&1
  
  # Run change detection
  local result
  result=$("$SCRIPT_DIR/detect-changes.sh" --base HEAD~1 --head HEAD 2>/dev/null)
  
  # Parse result
  local sdks_to_test
  sdks_to_test=$(echo "$result" | grep "SDKS_TO_TEST=" | cut -d'=' -f2)
  
  # Clean up
  git checkout - > /dev/null 2>&1
  git branch -D "$test_branch" > /dev/null 2>&1
  
  # Validate result
  if [[ "$sdks_to_test" == "$expected_sdks" ]]; then
    echo -e "${GREEN}✅ PASS: Got '$sdks_to_test'${NC}"
    return 0
  else
    echo -e "${RED}❌ FAIL: Expected '$expected_sdks', got '$sdks_to_test'${NC}"
    return 1
  fi
}

# Test scenarios
TESTS_PASSED=0
TESTS_FAILED=0

# Test 1: Python-only changes
if test_change_detection "Python-only changes" "python/src/test.py python/tests/test_example.py" "python"; then
  ((TESTS_PASSED++))
else
  ((TESTS_FAILED++))
fi

# Test 2: PHP-only changes
if test_change_detection "PHP-only changes" "php/src/Test.php php/tests/Unit/TestExample.php" "php"; then
  ((TESTS_PASSED++))
else
  ((TESTS_FAILED++))
fi

# Test 3: JavaScript-only changes
if test_change_detection "JavaScript-only changes" "js/src/index.ts js/tests/unit/example.test.ts" "js"; then
  ((TESTS_PASSED++))
else
  ((TESTS_FAILED++))
fi

# Test 4: Multiple SDK changes
if test_change_detection "Multiple SDK changes" "python/src/test.py php/src/Test.php" "python,php"; then
  ((TESTS_PASSED++))
else
  ((TESTS_FAILED++))
fi

# Test 5: Core file changes (should trigger all SDKs)
if test_change_detection "Core file changes" "BUILD.bazel docs/api.md" "python,php,js"; then
  ((TESTS_PASSED++))
else
  ((TESTS_FAILED++))
fi

# Test 6: Schema changes (should trigger all SDKs)
if test_change_detection "Schema changes" "schemas/user.json" "python,php,js"; then
  ((TESTS_PASSED++))
else
  ((TESTS_FAILED++))
fi

# Test 7: Documentation-only changes (should trigger all SDKs)
if test_change_detection "Documentation changes" "docs/llms/instructions.md" "python,php,js"; then
  ((TESTS_PASSED++))
else
  ((TESTS_FAILED++))
fi

# Test 8: All SDKs changed
if test_change_detection "All SDKs changed" "python/src/test.py php/src/Test.php js/src/index.ts" "python,php,js"; then
  ((TESTS_PASSED++))
else
  ((TESTS_FAILED++))
fi

# Summary
echo ""
echo "=========================="
echo -e "${BLUE}📊 Validation Summary${NC}"
echo "Tests passed: $TESTS_PASSED"
echo "Tests failed: $TESTS_FAILED"
echo "Total tests: $((TESTS_PASSED + TESTS_FAILED))"

if [[ $TESTS_FAILED -eq 0 ]]; then
  echo -e "${GREEN}🎉 All validation tests passed!${NC}"
  echo ""
  echo -e "${BLUE}✅ The selective testing CI pipeline is working correctly${NC}"
  exit 0
else
  echo -e "${RED}❌ Some validation tests failed${NC}"
  echo ""
  echo -e "${YELLOW}⚠️  Please review the change detection logic${NC}"
  exit 1
fi
