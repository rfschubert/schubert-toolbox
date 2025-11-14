# Documentação Schubert Toolbox

Bem-vindo à documentação do Schubert Toolbox - um sistema modular e extensível para validação, formatação e processamento de dados com suporte multi-linguagem.

## Índice de Documentação

### Implementação Python
- **[Python Documentation](python/)** - Documentação completa da implementação Python
  - **[Contracts](python/contracts/)** - Contratos e interfaces do sistema Python
    - [Contracts Overview](python/contracts/contracts_overview.md) - Visão geral de todos os contratos
    - [Manager Contract](python/contracts/manager_contract.md) - Interface para managers
    - [Formatter Contract](python/contracts/formatter_contract.md) - Interface para formatters
    - [Validator Contract](python/contracts/validator_contract.md) - Interface para validators
  - **[Managers](python/managers/)** - Documentação dos managers Python
    - [Implemented Managers](python/managers/implemented_managers.md) - FormatterManager e PostalCodeManager
  - **[Drivers](python/drivers/)** - Documentação dos drivers Python
    - [Formatter Drivers](python/drivers/formatter_drivers.md) - Drivers de formatação de dados
    - [Postal Code Drivers](python/drivers/postal_code_drivers.md) - Drivers de busca de endereços

### Documentação Multi-Linguagem
- **[Patterns](patterns/)** - Padrões arquiteturais cross-language
  - [Manager Pattern Details](patterns/manager_pattern_details.md) - Detalhes do padrão Manager

### LLMs e Agentes
- **[LLMs](llms/)** - Instruções e guias para uso com LLMs
  - [Default LLM Instructions](llms/default_llms_instructions.md) - Instruções padrão para LLMs
- **[Agents](agents/)** - Documentação para agentes e automação

### Especificações
- **[API Contracts](api_contracts/)** - Contratos de API e especificações
- **[Patterns](patterns/)** - Padrões arquiteturais do sistema

## Quick Start (Python)

> **Nota**: Os exemplos abaixo são específicos da implementação Python. Para outras linguagens, consulte a documentação específica quando disponível.

### Usando FormatterManager
```python
from managers import FormatterManager

# Criar manager
manager = FormatterManager()

# Formatar código postal brasileiro
result = manager.format("88304053", driver="brazilian_postalcode")
print(result)  # "88304-053"
```

### Usando PostalCodeManager
```python
from managers import PostalCodeManager

# Criar manager
manager = PostalCodeManager()

# Buscar endereço
address = manager.get("88304-053", driver="viacep")
print(address.get_display_name())
# "Rua Alberto Werner, Unit até 445 - lado ímpar, Itajaí, SC, Brazil"
```

### Workflow Completo
```python
from managers import FormatterManager, PostalCodeManager

# Formatar e buscar endereço
formatter = FormatterManager()
postal = PostalCodeManager()

# Pipeline: formato -> validação -> busca
formatted_code = formatter.format("88304053", driver="brazilian_postalcode")
address = postal.get(formatted_code, driver="viacep")

print(f"{formatted_code}: {address.locality}")  # "88304-053: Itajaí"
```

### Uso Direto de Drivers (Python)

```python
# Uso direto do formatter driver
from drivers.formatter.formatter_brazilian_postalcode_driver import FormatterBrazilianPostalcodeDriver

driver = FormatterBrazilianPostalcodeDriver()
driver.configure(strict_validation=False, allow_partial=True)
result = driver.format("88304053")  # "88304-053"

# Uso direto do postal code driver
from drivers.postalcode.postalcode_viacep_driver import PostalCodeViacepDriver

driver = PostalCodeViacepDriver()
driver.configure(timeout=30, retries=5)
address = driver.get("88304-053")
print(address.get_display_name())
```

## Arquitetura

O Schubert Toolbox segue uma arquitetura baseada em contratos com três camadas principais:

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

### Princípios Arquiteturais
- **Contratos**: Interfaces padronizadas garantem consistência
- **Manager Pattern**: Orquestração centralizada de drivers
- **DRY Principle**: Reutilização de código e lógica
- **Extensibilidade**: Plugin architecture para novos drivers
- **Interoperabilidade**: Componentes trabalham juntos seamlessly

## Status de Implementação por Linguagem

| Componente | Python | JavaScript | PHP | Status |
|------------|--------|------------|-----|--------|
| **Contracts System** | DONE | PLANNED | PLANNED | Python completo |
| **FormatterManager** | DONE | PLANNED | PLANNED | Python completo |
| **PostalCodeManager** | DONE | PLANNED | PLANNED | Python completo |
| **Brazilian CEP Formatter** | DONE | PLANNED | PLANNED | Python completo |
| **ViaCEP Driver** | DONE | PLANNED | PLANNED | Python completo |
| **WideNet Driver** | DONE | PLANNED | PLANNED | Python completo |
| **BrasilAPI Driver** | DONE | PLANNED | PLANNED | Python completo |

**Legenda**: DONE = Implementado | PLANNED = Planejado | NOT_PLANNED = Não planejado

## Managers Implementados (Python)

| Manager | Propósito | Drivers Disponíveis | Documentação |
|---------|-----------|-------------------|--------------|
| **FormatterManager** | Formatação de dados | `brazilian_postalcode` | [Docs](python/managers/implemented_managers.md#formattermanager) |
| **PostalCodeManager** | Busca de endereços | `viacep`, `widenet`, `brasilapi` | [Docs](python/managers/implemented_managers.md#postalcodemanager) |


## Drivers Implementados (Python)

| Driver | Tipo | Propósito | Documentação |
|--------|------|-----------|--------------|
| **FormatterBrazilianPostalcodeDriver** | Formatter | Formatação de CEP brasileiro | [Docs](python/drivers/formatter_drivers.md) |
| **PostalCodeViacepDriver** | Postal Code | API ViaCEP (viacep.com.br) | [Docs](python/drivers/postal_code_drivers.md#viacep-driver) |
| **PostalCodeWidenetDriver** | Postal Code | API WideNet (cdn.apicep.com) | [Docs](python/drivers/postal_code_drivers.md#widenet-driver) |
| **PostalCodeBrasilApiDriver** | Postal Code | API BrasilAPI (brasilapi.com.br) | [Docs](python/drivers/postal_code_drivers.md#brasilapi-driver) |

## Recursos Principais

### Formatação de Dados
- **Drivers Disponíveis**: Brazilian Postal Code Formatter
- **Tipos de Entrada**: String, Integer, formatos variados
- **Configuração**: Validação estrita/flexível, formatos parciais
- **Operações**: Individuais e em lote
- **Uso**: Direto ou via FormatterManager

### Busca de Endereços
- **Drivers Disponíveis**: ViaCEP, WideNet, BrasilAPI
- **Integração DRY**: Usa FormatterManager para formatação
- **Fallback**: Automático entre múltiplos drivers
- **Cache**: Para performance em operações repetidas
- **Objetos**: Address padronizados (ISO 19160)
- **Uso**: Direto ou via PostalCodeManager



## Desenvolvimento (Python)

> **Nota**: Os exemplos de desenvolvimento abaixo são específicos da implementação Python. Para outras linguagens, consulte a documentação específica quando disponível.

### Adicionando Novos Drivers

#### Formatter Driver
```python
from contracts.formatter_contract import AbstractFormatterContract

class MyFormatterDriver(AbstractFormatterContract):
    @property
    def name(self) -> str:
        return "My Formatter"

    def format(self, value):
        return str(value).upper()
```

#### Postal Code Driver
```python
from standards.address import Address, Country

class MyPostalCodeDriver:
    def __init__(self):
        self._formatter_manager = FormatterManager()  # DRY integration

    def get(self, postal_code: str) -> Address:
        # Format postal code using FormatterManager
        formatted_code = self._formatter_manager.format(
            postal_code, driver="my_postalcode_formatter"
        )

        # API call logic here
        # Return standardized Address object
        return Address(
            postal_code=formatted_code,
            locality="My City",
            administrative_area_1="My State",
            country=Country(code="BR", name="Brazil")
        )
```



## Links Úteis

- [README Principal](../README.md) - Informações gerais do projeto
- [Schemas](../schemas/) - Esquemas de dados
- [CI/CD Setup](ci-cd-setup.md) - Configuração de integração contínua

---

*Esta documentação é mantida atualizada com as implementações do sistema Schubert Toolbox.*

