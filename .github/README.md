# CI/CD Configuration

This directory contains the CI/CD configuration for the Schubert Toolbox project, implementing selective testing based on changed files.

## Overview

The selective testing system analyzes which files have changed in a pull request and runs tests only for the affected SDKs, optimizing build times and resource usage.

## Workflow Structure

### Main Workflow: `selective-tests.yml`

The main CI workflow consists of three jobs:

1. **detect-changes**: Analyzes changed files and determines which SDKs need testing
2. **test-sdks**: Runs tests for affected SDKs in parallel using a matrix strategy
3. **summary**: Provides a comprehensive summary of test results

### Change Detection Logic

The workflow detects changes in the following categories:

- **Python SDK**: Changes in `python/` directory
- **PHP SDK**: Changes in `php/` directory  
- **JavaScript SDK**: Changes in `js/` directory
- **Core/Shared files**: Changes in `docs/`, `schemas/`, root-level configuration files

### Testing Strategy

- **Single SDK changes**: Run tests only for the affected SDK
- **Multiple SDK changes**: Run tests for all affected SDKs in parallel
- **Core file changes**: Run tests for all SDKs (Python, PHP, JavaScript)
- **No relevant changes**: Skip testing entirely

## Helper Scripts

### `.github/scripts/detect-changes.sh`

Core script for detecting file changes and determining which SDKs need testing.

**Usage:**
```bash
# Basic usage
./detect-changes.sh

# Compare specific refs
./detect-changes.sh --base origin/main --head feature-branch

# Verbose output
./detect-changes.sh --verbose
```

### `.github/scripts/test-locally.sh`

Local testing script that allows developers to test the selective testing logic on their machine.

**Usage:**
```bash
# Test changes vs origin/main
./.github/scripts/test-locally.sh

# Dry run to see what would be tested
./.github/scripts/test-locally.sh --dry-run

# Test specific commit range
./.github/scripts/test-locally.sh --base HEAD~2 --head HEAD

# Force test all SDKs
./.github/scripts/test-locally.sh --force-all
```

## Bazel Integration

### Test Targets

Each SDK has the following Bazel test targets:

- `//python/tests:run_unit_tests` - Python unit tests
- `//python/tests:run_integration_tests` - Python integration tests  
- `//python/tests:run_bdd_tests` - Python BDD tests
- `//python/tests:run_all_tests` - All Python tests

- `//php/tests:run_unit_tests` - PHP unit tests
- `//php/tests:run_integration_tests` - PHP integration tests
- `//php/tests:run_all_tests` - All PHP tests

- `//js/tests:run_unit_tests` - JavaScript unit tests
- `//js/tests:run_integration_tests` - JavaScript integration tests
- `//js/tests:run_all_tests` - All JavaScript tests

### Root Targets

- `//:run_python_tests` - Run all Python tests
- `//:run_php_tests` - Run all PHP tests  
- `//:run_js_tests` - Run all JavaScript tests
- `//:run_all_sdk_tests` - Run tests for all SDKs

## Configuration Files

### `.bazelrc`

Bazel configuration optimized for both local development and CI environments:

- **CI config**: `--config=ci` for GitHub Actions
- **Dev config**: `--config=dev` for local development
- **Release config**: `--config=release` for production builds

## Optimization Features

### Caching

- **Bazel cache**: Persistent caching of build artifacts
- **Language-specific caches**: pip, composer, npm caches
- **GitHub Actions cache**: Repository and disk caches

### Parallel Execution

- Multiple SDKs are tested in parallel when affected
- Matrix strategy allows independent SDK test execution
- Fail-fast disabled to see all SDK results

### Resource Management

- Optimized resource allocation for CI environments
- Configurable CPU and memory limits
- Efficient dependency installation only for affected SDKs

## Monitoring and Reporting

### Test Results

- Detailed test output with `--test_output=all`
- Test artifacts uploaded for failed builds
- Comprehensive summary in GitHub Actions UI

### Change Detection Results

The workflow provides detailed information about:
- Which files changed
- Which SDKs were affected
- Why certain SDKs were selected for testing

## Local Development

Developers can use the local testing script to:
- Validate changes before pushing
- Test the selective testing logic
- Debug CI issues locally
- Optimize their development workflow

## Troubleshooting

### Common Issues

1. **Tests not running**: Check if changes match the file patterns
2. **All tests running**: Core files may have changed
3. **Build failures**: Ensure dependencies are installed correctly
4. **Cache issues**: Clear Bazel cache with `bazel clean --expunge`

### Debug Commands

```bash
# Check what files changed
git diff --name-only origin/main..HEAD

# Test change detection locally
./.github/scripts/detect-changes.sh --verbose

# Run specific SDK tests
bazel test //python/tests:run_all_tests --test_output=all
```
