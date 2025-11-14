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
    - [Company Drivers](python/drivers/company_drivers.md) - Drivers de busca de empresas

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

### Usando CompanyManager
```python
from managers import CompanyManager

# Criar manager
manager = CompanyManager()

# Buscar empresa por CNPJ
company = manager.get("15.280.995/0001-69", driver_name="brasilapi")
print(f"{company.get_display_name()} - {company.status}")
# "DIGITALBANKS TECNOLOGIA LTDA - Inapta"

# First-to-respond (mais rápido disponível)
company = manager.get_first_response_sync("15.280.995/0001-69", timeout=5.0)
print(f"Driver vencedor: {company.verification_source}")
# "Driver vencedor: opencnpj"
```

### Workflow Completo
```python
from managers import FormatterManager, PostalCodeManager, CompanyManager

# Formatar e buscar endereço
formatter = FormatterManager()
postal = PostalCodeManager()
company = CompanyManager()

# Pipeline: formato -> validação -> busca
formatted_code = formatter.format("88304053", driver="brazilian_postalcode")
address = postal.get(formatted_code, driver="viacep")

print(f"{formatted_code}: {address.locality}")  # "88304-053: Itajaí"

# Pipeline: CNPJ -> validação -> busca de empresa
formatted_cnpj = formatter.format("15280995000169", driver="brazilian_cnpj")
company_data = company.get(formatted_cnpj, driver_name="brasilapi")

print(f"{formatted_cnpj}: {company_data.get_display_name()}")
# "15.280.995/0001-69: DIGITALBANKS TECNOLOGIA LTDA"
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

# Uso direto do company driver
from drivers.company.company_brasilapi_driver import CompanyBrasilapiDriver

driver = CompanyBrasilapiDriver()
driver.configure(timeout=10, retries=3)
company = driver.get("15.280.995/0001-69")
print(f"{company.get_display_name()} - {company.status}")
```

## Arquitetura

O Schubert Toolbox segue uma arquitetura baseada em contratos com três camadas principais:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Managers      │    │   Formatters    │    │ Postal Drivers  │    │ Company Drivers │
│                 │    │                 │    │                 │    │                 │
│ ManagerContract │    │FormatterContract│    │ Address Lookup  │    │ Company Lookup  │
│                 │    │                 │    │                 │    │                 │
│ - load()        │    │ - format()      │    │ - get()         │    │ - get()         │
│ - list_drivers()│    │ - clean()       │    │ - configure()   │    │ - configure()   │
│ - has_driver()  │    │ - is_valid()    │    │ - get_config()  │    │ - get_config()  │
│ - get()         │    │ - configure()   │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
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
| **CompanyManager** | DONE | PLANNED | PLANNED | Python completo |
| **Brazilian CEP Formatter** | DONE | PLANNED | PLANNED | Python completo |
| **Brazilian CNPJ Formatter** | DONE | PLANNED | PLANNED | Python completo |
| **ViaCEP Driver** | DONE | PLANNED | PLANNED | Python completo |
| **WideNet Driver** | DONE | PLANNED | PLANNED | Python completo |
| **BrasilAPI Postal Driver** | DONE | PLANNED | PLANNED | Python completo |
| **BrasilAPI Company Driver** | DONE | PLANNED | PLANNED | Python completo |
| **OpenCNPJ Driver** | DONE | PLANNED | PLANNED | Python completo |
| **CNPJA Driver** | DONE | PLANNED | PLANNED | Python completo |
| **CNPJ.ws Driver** | DONE | PLANNED | PLANNED | Python completo |

**Legenda**: DONE = Implementado | PLANNED = Planejado | NOT_PLANNED = Não planejado

## Managers Implementados (Python)

| Manager | Propósito | Drivers Disponíveis | Documentação |
|---------|-----------|-------------------|--------------|
| **FormatterManager** | Formatação de dados | `brazilian_postalcode`, `brazilian_cnpj` | [Docs](python/managers/implemented_managers.md#formattermanager) |
| **PostalCodeManager** | Busca de endereços | `viacep`, `widenet`, `brasilapi` | [Docs](python/managers/implemented_managers.md#postalcodemanager) |
| **CompanyManager** | Busca de empresas | `brasilapi`, `opencnpj`, `cnpja`, `cnpjws` | [Docs](python/managers/implemented_managers.md#companymanager) |


## Drivers Implementados (Python)

| Driver | Tipo | Propósito | Documentação |
|--------|------|-----------|--------------|
| **FormatterBrazilianPostalcodeDriver** | Formatter | Formatação de CEP brasileiro | [Docs](python/drivers/formatter_drivers.md) |
| **FormatterBrazilianCnpjDriver** | Formatter | Formatação e validação de CNPJ brasileiro | [Docs](python/drivers/formatter_drivers.md) |
| **PostalCodeViacepDriver** | Postal Code | API ViaCEP (viacep.com.br) | [Docs](python/drivers/postal_code_drivers.md#viacep-driver) |
| **PostalCodeWidenetDriver** | Postal Code | API WideNet (cdn.apicep.com) | [Docs](python/drivers/postal_code_drivers.md#widenet-driver) |
| **PostalCodeBrasilApiDriver** | Postal Code | API BrasilAPI (brasilapi.com.br) | [Docs](python/drivers/postal_code_drivers.md#brasilapi-driver) |
| **CompanyBrasilapiDriver** | Company | API BrasilAPI CNPJ (brasilapi.com.br) | [Docs](python/drivers/company_drivers.md#brasilapi-driver) |
| **CompanyOpencnpjDriver** | Company | API OpenCNPJ (api.opencnpj.org) | [Docs](python/drivers/company_drivers.md#opencnpj-driver) |
| **CompanyCnpjaDriver** | Company | API CNPJA (open.cnpja.com) | [Docs](python/drivers/company_drivers.md#cnpja-driver) |
| **CompanyCnpjwsDriver** | Company | API CNPJ.ws (cnpj.ws) | [Docs](python/drivers/company_drivers.md#cnpjws-driver) |

## Recursos Principais

### Formatação de Dados
- **Drivers Disponíveis**: Brazilian Postal Code, Brazilian CNPJ
- **Tipos de Entrada**: String, Integer, formatos variados
- **Configuração**: Validação estrita/flexível, formatos parciais
- **Funcionalidades**: format(), clean(), is_valid()
- **Operações**: Individuais e em lote
- **Uso**: Direto ou via FormatterManager

### Busca de Endereços
- **Drivers Disponíveis**: ViaCEP, WideNet, BrasilAPI
- **Integração DRY**: Usa FormatterManager para formatação
- **Fallback**: Automático entre múltiplos drivers
- **Cache**: Para performance em operações repetidas
- **Objetos**: Address padronizados (ISO 19160)
- **Uso**: Direto ou via PostalCodeManager

### Busca de Empresas
- **Drivers Disponíveis**: BrasilAPI, OpenCNPJ, CNPJA, CNPJ.ws
- **Integração DRY**: Usa FormatterManager para validação de CNPJ
- **First-to-Respond**: Consulta paralela com o driver mais rápido
- **Rate Limiting**: Controle automático de requisições
- **SSL Handling**: Configuração automática para APIs com problemas de certificado
- **Objetos**: Company padronizados com dados completos
- **Uso**: Direto ou via CompanyManager



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

#### Company Driver
```python
from standards.company import Company, Country
from managers.formatter_manager import FormatterManager

class MyCompanyDriver:
    def __init__(self):
        self._formatter_manager = FormatterManager()  # DRY integration

    def get(self, cnpj: str) -> Company:
        # Clean and validate CNPJ using FormatterManager
        formatter = self._formatter_manager.load("brazilian_cnpj")
        clean_cnpj = formatter.clean(cnpj)
        formatted_cnpj = formatter.format(cnpj)

        # API call logic here
        # Return standardized Company object
        return Company(
            cnpj=formatted_cnpj,
            legal_name="My Company LTDA",
            status="Ativa",
            country=Country(code="BR", name="Brazil"),
            verification_source="my_api",
            is_verified=True
        )
```



## Melhorias Recentes

### CompanyManager e Drivers de Empresa (v2024.11)
- **4 Drivers Implementados**: BrasilAPI, OpenCNPJ, CNPJA, CNPJ.ws
- **First-to-Respond**: Consulta paralela retornando o resultado mais rápido
- **Rate Limiting**: Controle automático de requisições por driver
- **SSL Handling**: Configuração automática para APIs com certificados problemáticos
- **23 Testes de Integração**: Cobertura completa com cassetes VCR
- **Dados Reais**: Testes com empresas reais (AMBEV S.A., DIGITALBANKS TECNOLOGIA LTDA)

### CNPJ Formatter Integrado (v2024.11)
- **Funcionalidade CNPJParser Integrada**: Lógica centralizada no formatter
- **Método clean()**: Remove caracteres especiais e valida CNPJ
- **Método is_valid()**: Validação sem exceções
- **Suporte Robusto**: Aceita formatos variados (pontos, barras, espaços, texto)
- **DRY Implementation**: Eliminação de código duplicado nos drivers
- **Validação Consistente**: Mesma lógica em todos os drivers de empresa

### Arquitetura Aprimorada
- **Manager Pattern**: Orquestração centralizada com fallback automático
- **Driver Abstraction**: Interface consistente entre diferentes APIs
- **Error Handling**: Tratamento robusto de falhas de rede e API
- **Configuration Management**: Configuração flexível por driver
- **Standards Compliance**: Objetos padronizados (Company, Address, Country)

## Links Úteis

- [README Principal](../README.md) - Informações gerais do projeto
- [Schemas](../schemas/) - Esquemas de dados
- [CI/CD Setup](ci-cd-setup.md) - Configuração de integração contínua

---

*Esta documentação é mantida atualizada com as implementações do sistema Schubert Toolbox.*

