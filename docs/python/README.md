# Python Implementation Documentation

This directory contains comprehensive documentation for the Python implementation of the Schubert Toolbox system.

## Overview

The Python implementation provides a complete, production-ready version of the Schubert Toolbox with all core features implemented and tested. It serves as the reference implementation for other language ports.

## Key Features

- **Driver Pattern**: Modular, extensible architecture
- **Manager Pattern**: Centralized driver management and configuration
- **First-to-Respond**: Concurrent driver execution for maximum performance (4-5x faster)
- **Standards Compliance**: Consistent data structures and interfaces
- **Type Safety**: Full type hints and validation
- **Error Handling**: Comprehensive error management
- **Async Support**: Both synchronous and asynchronous APIs
- **Logging**: Detailed logging for debugging and monitoring

## Quick Start

```python
from managers.postalcode_manager import PostalCodeManager
from managers.company_manager import CompanyManager

# High-performance first-to-respond pattern for addresses
postal_manager = PostalCodeManager()
address = postal_manager.get_first_response_sync("88304-053")
print(f"Fastest driver: {address.verification_source}")
print(f"Address: {address.get_display_name()}")

# High-performance company lookups
company_manager = CompanyManager()
company = company_manager.get_first_response_sync("11.222.333/0001-81")
print(f"Company: {company.get_display_name()}")
print(f"Status: {company.status}")
```

## Documentation Structure

### [Contracts](contracts/)
Interface specifications and contracts that ensure consistency across all components.

- **[Contracts Overview](contracts/contracts_overview.md)** - Complete contract system overview
- **[Manager Contract](contracts/manager_contract.md)** - Manager interface specification
- **[Formatter Contract](contracts/formatter_contract.md)** - Formatter interface specification


### [Managers](managers/)
Orchestrator classes that provide unified interfaces for driver management.

- **[Implemented Managers](managers/implemented_managers.md)** - FormatterManager & PostalCodeManager
- **[CompanyManager](managers/company_manager.md)** - Brazilian company (CNPJ) data lookup manager

### [Drivers](drivers/)
Core implementation components that perform specific tasks.

- **[Formatter Drivers](drivers/formatter_drivers.md)** - Data formatting drivers
- **[Postal Code Drivers](drivers/postal_code_drivers.md)** - Address lookup drivers
- **[Company Drivers](drivers/company_drivers.md)** - Brazilian company (CNPJ) data drivers

### Development Tools
Documentation for development and code quality tools.

- **[LINTING.md](LINTING.md)** - Complete guide for code quality tools (Ruff, MyPy, Bandit, Pre-commit)

## Quick Start

### Installation

```bash
cd python
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Basic Usage

```python
from managers import FormatterManager, PostalCodeManager, CompanyManager

# Format postal code
formatter = FormatterManager()
formatted = formatter.format("88304053", driver="brazilian_postalcode")
print(formatted)  # "88304-053"

# Lookup address
postal = PostalCodeManager()
address = postal.get(formatted, driver="viacep")
print(address.get_display_name())

# Lookup company data
company_manager = CompanyManager()
company = company_manager.get_first_response_sync("11.222.333/0001-81")
print(f"Company: {company.get_display_name()}")
print(f"Status: {company.status}")
```

### Direct Driver Usage

```python
# Direct formatter usage
from drivers.formatter.formatter_brazilian_postalcode_driver import FormatterBrazilianPostalcodeDriver

driver = FormatterBrazilianPostalcodeDriver()
driver.configure(strict_validation=False, allow_partial=True)
result = driver.format("88304053")  # "88304-053"

# Direct postal code usage
from drivers.postalcode.postalcode_viacep_driver import PostalCodeViacepDriver

driver = PostalCodeViacepDriver()
driver.configure(timeout=30, retries=5)
address = driver.get("88304-053")
```

## Implementation Status

### Fully Implemented

| Component | Status | Drivers/Features |
|-----------|--------|------------------|
| **FormatterManager** | Complete | Brazilian Postal Code, Brazilian CNPJ |
| **PostalCodeManager** | Complete | ViaCEP, WideNet, BrasilAPI |
| **CompanyManager** | Complete | BrasilAPI, CNPJA, OpenCNPJ, CNPJ.ws |
| **Contracts System** | Complete | Manager, Formatter, Validator |
| **DRY Integration** | Complete | Cross-manager integration |
| **Testing Suite** | Complete | Unit tests, integration tests |

### Available Drivers

#### Formatter Drivers
- **FormatterBrazilianPostalcodeDriver**: Brazilian postal code formatting (XXXXX-XXX)
- **FormatterBrazilianCnpjDriver**: Brazilian CNPJ formatting (XX.XXX.XXX/XXXX-XX)

#### Postal Code Drivers
- **PostalCodeViacepDriver**: ViaCEP service integration (viacep.com.br)
- **PostalCodeWidenetDriver**: WideNet API integration (cdn.apicep.com)
- **PostalCodeBrasilApiDriver**: BrasilAPI service integration (brasilapi.com.br)

#### Company Drivers
- **CompanyBrasilApiDriver**: BrasilAPI company data service (fast, reliable)
- **CompanyCnpjaDriver**: CNPJA.com company data service (rate limited)
- **CompanyOpencnpjDriver**: OpenCNPJ.org company data service (community-driven)
- **CompanyCnpjwsDriver**: CNPJ.ws company data service (comprehensive data)



## Architecture

The Python implementation follows a three-layer architecture:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Managers      │    │   Formatters    │    │ Postal Drivers  │
│                 │    │                 │    │                 │
│ ManagerContract │    │FormatterContract│    │ Address Lookup  │
│                 │    │                 │    │                 │
│ - load()        │    │ - format()      │    │ - get()         │
│ - list_drivers()│    │ - configure()   │    │ - configure()   │
│ - has_driver()  │    │ - get_config()  │    │ - get_config()  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Key Principles

- **Contract-Based**: All components implement standardized interfaces
- **DRY Principle**: No code duplication across drivers
- **Manager Pattern**: Centralized orchestration of drivers
- **Extensibility**: Easy to add new drivers and managers
- **Testability**: Comprehensive test coverage

## Testing

```bash
# Run all tests
cd python
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html

# Run specific test categories
python -m pytest tests/unit/ -v          # Unit tests
python -m pytest tests/integration/ -v   # Integration tests
```

## Development

### Adding New Drivers

Follow the established patterns documented in each section:

1. **Implement the appropriate contract** (FormatterContract, etc.)
2. **Follow naming conventions** (e.g., `FormatterXxxDriver`, `ValidatorXxxDriver`)
3. **Add comprehensive tests** including contract compliance tests
4. **Register with the appropriate manager** in the manager's `_register_default_drivers()` method
5. **Update documentation** with examples and usage patterns

### Project Structure

```
python/
├── src/
│   ├── contracts/          # Interface definitions
│   ├── managers/           # Manager implementations
│   ├── drivers/            # Driver implementations
│   │   ├── formatter/      # Formatter drivers
│   │   ├── postalcode/     # Postal code drivers
│   │   └── validator/      # Validator drivers
│   └── standards/          # Standard data structures
├── tests/
│   ├── unit/              # Unit tests
│   └── integration/       # Integration tests
└── requirements.txt       # Dependencies
```

## See Also

- **[Main Documentation](../)** - System overview and multi-language documentation
- **[LLM Instructions](../llms/default_llms_instructions.md)** - Guidelines for AI development
- **[Patterns](../patterns/)** - Architectural patterns
- **[API Contracts](../api_contracts/)** - API specifications

---

*This documentation covers the complete Python implementation of the Schubert Toolbox system.*
