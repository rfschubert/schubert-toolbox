# Linting and Code Quality

This document describes the linting and code quality tools configured for the Schubert Toolbox project.

## Configured Tools

### Ruff (Primary Tool)
- **Replaces**: black, flake8, isort, and several other tools
- **Features**:
  - Unused import detection
  - Automatic code formatting
  - Import sorting
  - Common bug detection
  - Code simplification
- **Configuration**: `pyproject.toml`

### MyPy (Type Checking)
- **Functionality**: Static type checking
- **Configuration**: `pyproject.toml`

### Bandit (Security)
- **Functionality**: Security vulnerability detection
- **Configuration**: Default

### Pre-commit (Automation)
- **Functionality**: Automatic checks before commits
- **Configuration**: `.pre-commit-config.yaml`

## How to Use

### Quick Commands (Makefile)

```bash
# Install dependencies
make install

# Run all checks (no fixes)
make lint

# Run with automatic fixes
make lint-fix

# Format only
make format

# Type checking only
make check

# Security checking only
make security

# Check unused imports only
make unused

# Run tests
make test

# Clean temporary files
make clean
```

### Direct Python Script

```bash
# Activate virtual environment
source venv/bin/activate

# Check unused imports
python lint.py --unused src/

# Fix automatically
python lint.py --fix src/

# Run all checks
python lint.py --all src/

# Ruff only
python lint.py --ruff src/

# MyPy only
python lint.py --mypy src/

# Security only
python lint.py --security src/
```

### Direct Ruff Commands

```bash
# Check issues
ruff check src/

# Fix automatically
ruff check src/ --fix

# Format code
ruff format src/

# Check unused imports only
ruff check src/ --select F401
```

## Configured Rules

### Active Ruff Rules
- **E, W**: pycodestyle errors and warnings
- **F**: Pyflakes (unused imports, undefined variables)
- **I**: isort (import sorting)
- **UP**: pyupgrade (Python code modernization)
- **B**: flake8-bugbear (common bugs)
- **C4**: flake8-comprehensions (list/dict comprehensions)
- **PIE**: flake8-pie (unnecessary code)
- **SIM**: flake8-simplify (code simplification)
- **RUF**: Ruff-specific rules

### Per-file Exceptions
- **`__init__.py`**: Allows unused imports (F401)
- **`tests/**/*.py`**: Allows asserts (S101)

## IDE Integration

### VS Code
Add to `settings.json`:
```json
{
    "python.linting.enabled": true,
    "python.linting.ruffEnabled": true,
    "python.formatting.provider": "ruff",
    "python.linting.mypyEnabled": true
}
```

### PyCharm
1. Install "Ruff" plugin
2. Configure External Tools to run scripts

## Pre-commit Hooks

To install automatic hooks:

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run on all files
pre-commit run --all-files
```

## Cleanup Results

### Fixed Issues
- **18 unused imports** automatically removed
- **19 files** reformatted
- **590+ style issues** fixed
- **Whitespace** cleaned up
- **Import sorting** corrected

### Statistics
- **Execution time**: ~5 seconds for entire project
- **Files checked**: 21 Python files
- **Lines of code**: ~8000 lines
- **Automatic fix rate**: ~76% of issues

## Recommended Workflow

### During Development
```bash
# Before committing
make lint-fix
make test
```

### Before Push
```bash
# Complete verification
make ci
```

### CI/CD Configuration
```yaml
# GitHub Actions example
- name: Lint
  run: |
    cd python
    make install
    make lint
```

## Troubleshooting

### Issue: "ruff: command not found"
```bash
# Solution
pip install ruff
# or
make install
```

### Issue: MyPy finds too many errors
```bash
# Run basic checks only
python lint.py --ruff src/
```

### Issue: Pre-commit too slow
```bash
# Run only on modified files
pre-commit run
```

## Customization

To adjust rules, edit `pyproject.toml`:

```toml
[tool.ruff.lint]
# Add new rules
select = ["E", "W", "F", "I", "UP", "B", "C4", "PIE", "SIM", "RUF", "N"]

# Ignore specific rules
ignore = ["E501", "W503"]
```

## Achieved Benefits

- **Cleaner code**: No unused imports
- **Consistent formatting**: Uniform style across project
- **Early bug detection**: Issues found before execution
- **Improved security**: Vulnerabilities detected automatically
- **Increased productivity**: Automatic fixes save time
- **Quality assurance**: Standards maintained automatically
