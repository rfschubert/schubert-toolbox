# CI/CD Selective Testing Setup Guide

This guide explains how to set up and use the selective testing CI/CD pipeline for the Schubert Toolbox project.

## Overview

The selective testing system optimizes CI/CD by running tests only for SDKs that have been modified, significantly reducing build times and resource usage while maintaining comprehensive test coverage.

## Features

- **Intelligent Change Detection**: Analyzes file changes to determine which SDKs need testing
- **Parallel Execution**: Runs tests for multiple affected SDKs simultaneously
- **Core File Handling**: Automatically tests all SDKs when shared/core files change
- **Local Testing**: Provides scripts for local validation before pushing
- **Comprehensive Reporting**: Detailed test results and change analysis

## Quick Start

### 1. Validate the Setup

Run the validation script to ensure everything is working correctly:

```bash
./.github/scripts/validate-ci.sh
```

### 2. Test Locally

Before pushing changes, test the selective logic locally:

```bash
# See what would be tested
./.github/scripts/test-locally.sh --dry-run

# Run tests for changed SDKs
./.github/scripts/test-locally.sh
```

### 3. Push Changes

The CI pipeline will automatically:
1. Detect which files changed
2. Determine affected SDKs
3. Run tests only for those SDKs
4. Provide detailed results

## Change Detection Rules

### SDK-Specific Changes

- **Python SDK**: Changes in `python/` → Run Python tests only
- **PHP SDK**: Changes in `php/` → Run PHP tests only  
- **JavaScript SDK**: Changes in `js/` → Run JavaScript tests only

### Core/Shared File Changes

These files trigger tests for ALL SDKs:
- `docs/` - Documentation changes
- `schemas/` - Schema definitions
- `BUILD.bazel` - Root build configuration
- `WORKSPACE` - Bazel workspace configuration
- `MODULE.bazel` - Bazel module configuration
- `.bazelrc` - Bazel configuration
- `.bazelignore` - Bazel ignore patterns
- `README.md` - Project documentation
- `AGENTS.md` - Agent instructions

### Multiple SDK Changes

When multiple SDKs are modified, tests run in parallel for all affected SDKs.

## Bazel Test Targets

### Individual SDK Tests

```bash
# Python tests
bazel test //python/tests:run_unit_tests
bazel test //python/tests:run_integration_tests
bazel test //python/tests:run_bdd_tests
bazel test //python/tests:run_all_tests

# PHP tests
bazel test //php/tests:run_unit_tests
bazel test //php/tests:run_integration_tests
bazel test //php/tests:run_all_tests

# JavaScript tests
bazel test //js/tests:run_unit_tests
bazel test //js/tests:run_integration_tests
bazel test //js/tests:run_all_tests
```

### Aggregated Tests

```bash
# Run all tests for a specific SDK
bazel test //:run_python_tests
bazel test //:run_php_tests
bazel test //:run_js_tests

# Run all SDK tests
bazel test //:run_all_sdk_tests
```

## Configuration

### Bazel Configuration

The `.bazelrc` file provides optimized configurations:

```bash
# For CI environments
bazel test --config=ci //python/tests:run_all_tests

# For local development
bazel test --config=dev //python/tests:run_all_tests

# For release builds
bazel build --config=release //:all_sdks
```

### GitHub Actions

The workflow is triggered on:
- Pull requests to `main` or `develop` branches
- Pushes to `main` branch

## Local Development Workflow

### 1. Make Changes

Edit files in any SDK directory or core files.

### 2. Test Locally

```bash
# Quick check - see what would be tested
./.github/scripts/test-locally.sh --dry-run

# Run tests for changed SDKs
./.github/scripts/test-locally.sh

# Force test all SDKs (useful for major changes)
./.github/scripts/test-locally.sh --force-all
```

### 3. Validate CI Logic

```bash
# Test the change detection logic
./.github/scripts/validate-ci.sh
```

### 4. Push Changes

The CI pipeline will automatically handle selective testing.

## Troubleshooting

### Common Issues

1. **No tests running**: 
   - Check if your changes match the file patterns
   - Use `--verbose` flag to see detailed change detection

2. **All tests running unexpectedly**:
   - Core files may have been modified
   - Check the change detection output

3. **Tests failing locally but not in CI**:
   - Ensure dependencies are installed
   - Check Bazel cache: `bazel clean --expunge`

### Debug Commands

```bash
# Check what files changed
git diff --name-only origin/main..HEAD

# Test change detection with verbose output
./.github/scripts/detect-changes.sh --verbose

# Run specific tests manually
bazel test //python/tests:run_all_tests --test_output=all
```

## Performance Benefits

### Before Selective Testing
- All SDK tests run on every change
- ~15-20 minutes per CI run
- High resource usage

### After Selective Testing
- Only affected SDK tests run
- ~5-8 minutes for single SDK changes
- 60-70% reduction in resource usage
- Parallel execution for multiple SDKs

## Monitoring

The CI pipeline provides:
- Detailed change detection results
- Test execution summaries
- Artifact uploads for failed tests
- Performance metrics

## Best Practices

1. **Test locally first**: Use the local testing script before pushing
2. **Validate major changes**: Run `--force-all` for architectural changes
3. **Monitor CI results**: Check the detailed summaries in GitHub Actions
4. **Keep core files minimal**: Changes to core files trigger all tests
5. **Use appropriate commit messages**: Help reviewers understand the scope of changes
