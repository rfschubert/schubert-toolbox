<instructions>
  <overview>
    This document summarizes the core principles and architectural guidelines for the Schubert Toolbox ecosystem, aiming at maintaining high code quality and consistency across multiple programming languages and implementations.
  </overview>

  <required-reading>
    <document>
      <name>Code Quality and Security Rules</name>
      <path>docs/llms/code_quality_rules.md</path>
      <description>
        MANDATORY: All LLM agents must review and follow the code quality and security rules before making any code changes. This document establishes coding standards, security practices, and implementation patterns that must be adhered to across all language implementations.
      </description>
      <enforcement>high</enforcement>
    </document>
  </required-reading>

  <principles>
    <principle>
      <name>Single Responsibility Principle (SOLID)</name>
      <description>
        Each component should have one responsibility. Drivers handle communication with external services; Managers orchestrate drivers; the SDK integrates advanced features such as caching, rate limiting, and circuit breakers.
      </description>
    </principle>
    <principle>
      <name>Don't Repeat Yourself (DRY)</name>
      <description>
        Core logic must be implemented once and reused. Common utilities like caching and circuit breakers exist only in the SDK layer, avoiding duplication in drivers or managers.
      </description>
    </principle>
    <principle>
      <name>Framework Agnosticism</name>
      <description>
        Drivers and Managers must be agnostic to frameworks, enabling users to consume drivers directly if desired without any mandatory dependencies or side effects.
      </description>
    </principle>
    <principle>
      <name>Language Modularity</name>
      <description>
        Code organization and implementation vary per language; however, naming and API surface must remain consistent to provide a unified developer experience.
      </description>
    </principle>
  </principles>

  <architecture>
    <component>
      <name>Drivers</name>
      <description>
        Implement pure communication with external services; minimal logic; no cache or circuit breaker.

        Driver Requirements:
        - Follow naming convention: {type}_{provider}_driver.{ext}
        - Implement consistent interfaces within the same type
        - Accept same inputs and return same output structures
        - Handle errors uniformly using standard exception types
        - Support standard configuration options (timeout, retries, etc.)
        - Be stateless and thread-safe
        - Focus solely on data retrieval/processing, no business logic

        Example Driver Types:
        - Validation: validator_email_driver.py, validator_cpf_driver.py
        - Postal Code: postalcode_viacep_driver.py, postalcode_brasilapi_driver.py
        - Payment: payment_stripe_driver.py, payment_paypal_driver.py
        - Database: database_postgres_driver.py, database_mongodb_driver.py
      </description>
    </component>
    <component>
      <name>Managers</name>
      <description>
        Orchestrate one or more drivers, implementing strategies such as first response, priority fallback, etc. Must remain lightweight and framework agnostic.

        Manager Responsibilities:
        - Load and manage drivers of the same type
        - Provide unified interface via load() method
        - Implement driver selection strategies (priority, fallback, round-robin)
        - Handle driver registration and discovery
        - Maintain driver metadata and configuration
        - Provide convenience methods (validate_or_raise, bulk operations)
        - Cache driver instances when appropriate

        Manager Pattern:
        ```
        manager = PostalCodeManager()
        driver = manager.load("viacep")  # Returns driver instance
        result = driver.lookup("01310-100")  # Returns Address object

        # Or direct usage
        result = manager.lookup("01310-100", driver="viacep")
        ```
      </description>
    </component>
    <component>
      <name>SDK</name>
      <description>
        Integrates advanced runtime features: caching, circuit breaker, rate limiter, configuration loading, and environment awareness. Handles deployment optimizations and resource management.

        SDK Features:
        - Cross-cutting concerns (caching, circuit breakers, rate limiting)
        - Configuration management and environment detection
        - Monitoring and observability integration
        - Resource pooling and connection management
        - Deployment-specific optimizations
        - Health checks and diagnostics
      </description>
    </component>
  </architecture>

  <configuration>
    <description>
      Configuration must be centralized and accessible across languages. Use `.env` files and a shared `schubert.config.py` for parameterizing drivers, caches, and advanced SDK features.
    </description>
  </configuration>

  <testing>
    <description>
      Structure tests segregated by language and type (unit, integration, BDD), running only tests relevant to the affected language during CI to optimize resource usage.
    </description>
  </testing>

  <build_system>
    <description>
      Use Bazel to manage builds and tests efficiently. Leverage Bazel's native support for multi-language environments to:
      <ul>
        <li>Run tests incrementally per language and package</li>
        <li>Handle dependencies explicitly</li>
        <li>Enable caching and increase build/test speed</li>
      </ul>
    </description>
  </build_system>

  <usage_guidelines>
    <description>
      Users should be able to:
      <ul>
        <li>Use drivers directly for minimal dependency and simple use cases</li>
        <li>Use managers to orchestrate multiple drivers without complexity</li>
        <li>Leverage the SDK for comprehensive features and optimizations</li>
      </ul>
      All APIs must be consistent across languages, documented clearly, and respect the principles above.
    </description>
  </usage_guidelines>

  <llm_usage>
    <instruction>
      Only consult code blocks when strictly necessary to save tokens.
    </instruction>
  </llm_usage>

  <code_style>
    <rule>
      <name>No Emojis</name>
      <description>
        Do not use emojis in any code, documentation, comments, print statements, log messages, or any other text output. Keep all text professional and emoji-free.
      </description>
    </rule>
    <rule>
      <name>Use Logging Instead of Print</name>
      <description>
        Never use print() statements. Always use proper logging with appropriate log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL) to enable verbosity control. This allows users to configure log levels based on their needs.
      </description>
    </rule>
    <rule>
      <name>No Automatic Documentation Creation</name>
      <description>
        Do not create .md documentation files automatically unless explicitly requested by the user. Focus on code implementation and only create documentation when specifically asked.
      </description>
    </rule>
    <rule>
      <name>Driver File Naming Convention</name>
      <description>
        Driver files must follow the naming pattern: {type}_{name}_driver.{extension}
        Examples:
        - validator_email_driver.py
        - validator_cpf_driver.py
        - postalcode_viacep_driver.py
        - postalcode_brasilapi_driver.py
        - api_payment_driver.py
        - database_user_driver.py
        This ensures consistent naming across all driver implementations and makes the purpose of each driver immediately clear.
      </description>
    </rule>
    <rule>
      <name>Driver Interface Consistency</name>
      <description>
        All drivers of the same type must implement identical interfaces and behavior patterns to ensure interchangeability. This enables managers to load different drivers seamlessly without changing client code.

        Key principles:
        1. Same Input/Output: All drivers of the same type must accept the same input parameters and return the same data structure types
        2. Consistent Method Signatures: Method names, parameters, and return types must be identical across drivers of the same type
        3. Uniform Error Handling: All drivers must handle errors consistently using the same exception types and error codes
        4. Standardized Configuration: Configuration options should be consistent where applicable

        Example - PostalCodeManager drivers:
        - postalcode_viacep_driver.py
        - postalcode_brasilapi_driver.py
        - postalcode_widenet_driver.py

        All must:
        - Accept a postal code string as input
        - Return an Address object with the same structure
        - Handle invalid postal codes with the same error types
        - Support the same configuration options (timeout, retries, etc.)
        - Be loadable via manager.load("viacep"), manager.load("brasilapi"), etc.

        This allows users to switch between drivers without code changes and use drivers directly or through managers:
        ```
        # Direct driver usage
        driver = PostalCodeViacepDriver()
        address = driver.get("01310-100")

        # Manager-orchestrated usage
        manager = PostalCodeManager()
        address1 = manager.load("viacep").get("01310-100")
        address2 = manager.load("brasilapi").get("01310-100")

        # All return the same Address object structure
        ```

        For detailed implementation patterns, see: docs/python/managers/implemented_managers.md
      </description>
    </rule>
  </code_style>

  <implementation_reference>
    <description>
      For detailed implementation patterns, driver interface requirements, manager implementation guidelines, and comprehensive examples, refer to:

      docs/python/managers/implemented_managers.md
      docs/python/contracts/manager_contract.md

      These documents cover:
      - Direct driver usage patterns
      - Manager-orchestrated usage patterns
      - Driver interface consistency requirements
      - Method naming conventions
      - Error handling patterns
      - Configuration patterns
      - Data structure consistency
      - Testing patterns
      - Driver selection strategies
    </description>
  </implementation_reference>

  <standards_compliance>
    <critical_rule>
      ALL DRIVERS MUST USE STANDARD CLASSES FROM `standards/` DIRECTORY

      This is a CRITICAL architectural requirement that ensures:
      - Interoperability between all managers and drivers
      - Data consistency across the entire system
      - Proper validation and serialization
      - Compliance with international standards (ISO 19160 for addresses)

      REQUIRED USAGE:
      - Postal Code Drivers: MUST return `standards.address.Address` objects
      - Person Drivers: MUST return `standards.person.Person` objects
      - Any data structure: MUST use classes from `standards/` directory

      EXAMPLE - Postal Code Driver:
      ```python
      from standards.address import Address, Country

      def get(self, postal_code: str) -> Address:
          # API call logic here...

          # ALWAYS return standards.address.Address
          return Address(
              street_name=data.get('street'),
              locality=data.get('city'),
              administrative_area_1=data.get('state'),
              postal_code=formatted_postal_code,
              country=Country(code="BR", name="Brazil"),
              is_verified=True,
              verification_source="api_name"
          )
      ```

      NEVER create custom data classes when standard classes exist.
      ALWAYS import from `standards.{module}` for data structures.
    </critical_rule>
  </standards_compliance>

  <code_quality_enforcement>
    <rule>
      <name>Mandatory Code Quality Review</name>
      <description>
        Before implementing any code changes, LLM agents MUST review and apply the rules defined in docs/llms/code_quality_rules.md. This includes:

        - Control flow patterns (avoiding deep nesting, replacing long elif chains)
        - Error handling practices (EAFP principle, specific exceptions)
        - Security measures (log injection prevention, input sanitization)
        - Code organization (single responsibility, avoiding magic numbers)
        - Documentation standards (comprehensive docstrings, no emojis)

        These rules are not optional - they are mandatory for all code contributions.
      </description>
      <enforcement>mandatory</enforcement>
    </rule>
  </code_quality_enforcement>
</instructions>
