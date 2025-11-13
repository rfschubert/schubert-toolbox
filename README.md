# Schubert Toolbox

## Overview

Schubert Toolbox is a multi-language SDK collection that provides standardized tools and utilities for development.

## Project Structure

```
schubert-toolbox/
├── docs/              # General documentation and instructions for LLMs, AI, agents
├── schemas/           # JSON schemas for standardized entities
├── python/            # Python SDK
├── php/               # PHP SDK
└── js/                # JavaScript/TypeScript SDK
```

## Available SDKs

- **Python**: Complete SDK for Python
- **PHP**: Complete SDK for PHP
- **JavaScript/TypeScript**: Complete SDK for JavaScript/TypeScript

## Language Versions (LTS)

This project uses Long Term Support (LTS) versions for stability and long-term maintenance:

### Python LTS

- **Version**: Python 3.11.9
- **Support**: Until October 2027
- **Note**: Python 3.12 does not have official LTS status yet

### PHP LTS

- **Version**: PHP 8.2.20
- **Support**: Until December 2025
- **Note**: Each PHP version has approximately 2 years of active support

### Node.js LTS

- **Version**: Node.js 20.15.0
- **Codename**: "Iron"
- **Support**: Until April 2026

## Installation

### Python
```bash
pip install schubert-toolbox
```

### PHP
```bash
composer require schubert/toolbox
```

### JavaScript/TypeScript
```bash
npm install schubert-toolbox
```

## Development

This project uses Bazel for multi-language builds and testing.

### Prerequisites

- Bazel 8.4.2 or later
- JDK 11 or later (required by Bazel)
- Python 3.11+ (LTS - for Python SDK)
- PHP 8.2+ (LTS - for PHP SDK)
- Node.js 20+ (LTS Iron - for JavaScript/TypeScript SDK)

### Bazel Commands

#### Basic Commands

```bash
# List all available targets
bazel query //...

# Build a specific target
bazel build //:hello

# Build all SDKs
bazel build //python:all //php:all //js:all

# Build aggregated target
bazel build //:all_sdks
```

#### Testing

```bash
# Run all tests
bazel test //...

# Run tests for a specific SDK
bazel test //python/tests:all
bazel test //php/tests:all
bazel test //js/tests:all

# Run aggregated tests
bazel test //:all_tests
```

#### Information and Queries

```bash
# Get workspace information
bazel info

# Get workspace path
bazel info workspace

# Query specific targets
bazel query //python:all
bazel query //php:all
bazel query //js:all

# Query dependencies
bazel query "deps(//:all_sdks)"
```

#### Cleanup

```bash
# Clean build artifacts
bazel clean

# Clean and remove all cached files
bazel clean --expunge
```

#### Target Structure

- `//:hello` - Basic verification target
- `//:all_sdks` - Aggregated target for all SDKs
- `//:all_tests` - Aggregated target for all tests
- `//python:all` - All Python SDK files
- `//php:all` - All PHP SDK files
- `//js:all` - All JavaScript/TypeScript SDK files

### Setting Up JAVA_HOME

Bazel requires JDK (not JRE). Configure JAVA_HOME:

```bash
# Find JDK path
readlink -f $(which javac)

# Set JAVA_HOME (add to ~/.bashrc or ~/.zshrc)
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64

# Verify
echo $JAVA_HOME
$JAVA_HOME/bin/javac -version
```

## Documentation

See the `docs/` folder for detailed documentation about:
- Instructions for LLMs and agents
- API contracts
- Usage guides

## License

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
