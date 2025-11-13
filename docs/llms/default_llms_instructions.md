<instructions>
  <overview>
    This document summarizes the core principles and architectural guidelines for the Schubert Toolbox ecosystem, aiming at maintaining high code quality and consistency across multiple programming languages and implementations.
  </overview>

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
      </description>
    </component>
    <component>
      <name>Managers</name>
      <description>
        Orchestrate one or more drivers, implementing strategies such as first response, priority fallback, etc. Must remain lightweight and framework agnostic.
      </description>
    </component>
    <component>
      <name>SDK</name>
      <description>
        Integrates advanced runtime features: caching, circuit breaker, rate limiter, configuration loading, and environment awareness. Handles deployment optimizations and resource management.
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
</instructions>
