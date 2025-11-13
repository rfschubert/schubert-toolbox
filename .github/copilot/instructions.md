# GitHub Copilot Project Instructions

## Language and Communication

- **All communication must be in English**: Issues, Pull Requests, commit messages, code comments, and documentation
- **Never use emojis**: Keep all communication professional and emoji-free

## Code Quality Principles

### DRY (Don't Repeat Yourself)
- Core logic must be implemented once and reused
- Common utilities like caching and circuit breakers exist only in the SDK layer
- Avoid duplication in drivers or managers

### SOLID Principles
- **Single Responsibility Principle**: Each component should have one responsibility
  - Drivers handle communication with external services
  - Managers orchestrate drivers
  - SDK integrates advanced features (caching, rate limiting, circuit breakers)
- **Open/Closed Principle**: Open for extension, closed for modification
- **Liskov Substitution Principle**: Subtypes must be substitutable for their base types
- **Interface Segregation Principle**: Clients should not depend on interfaces they don't use
- **Dependency Inversion Principle**: Depend on abstractions, not concretions

## Architecture Guidelines

Refer to the main instructions file for detailed architecture:
**[docs/llms/default_llms_instructions.md](../../docs/llms/default_llms_instructions.md)**

### Component Responsibilities

1. **Drivers**: Pure communication with external services; minimal logic; no cache or circuit breaker
2. **Managers**: Orchestrate one or more drivers, implementing strategies (first response, priority fallback, etc.)
3. **SDK**: Integrates advanced runtime features (caching, circuit breaker, rate limiter, configuration loading)

## Code Review Guidelines

### Multi-Language Feature Parity

**CRITICAL**: When reviewing a Pull Request:

1. **Check for feature parity across languages**:
   - If a feature is added to Python but not PHP or JavaScript/TypeScript
   - If a feature is added to PHP but not Python or JavaScript/TypeScript
   - If a feature is added to JavaScript/TypeScript but not Python or PHP

2. **Action Required**: When a PR is approved that adds a feature to only one language:
   - **Automatically create an issue** after PR merge
   - Issue title format: `[Feature Parity] Implement [Feature Name] in [Missing Languages]`
   - Issue description should include:
     - Reference to the merged PR
     - List of languages where the feature needs to be implemented
     - Link to the implementation in the existing language for reference
     - Acceptance criteria for each language

3. **Issue Template**:
   ```
   ## Feature Parity Request
   
   **Source PR**: #[PR_NUMBER]
   **Feature**: [Feature Name]
   **Implemented in**: [Language(s)]
   **Needs implementation in**: [Language(s)]
   
   ### Reference Implementation
   - [Link to source code]
   
   ### Acceptance Criteria
   - [ ] Feature implemented in [Language 1]
   - [ ] Feature implemented in [Language 2]
   - [ ] Tests added for all languages
   - [ ] Documentation updated
   - [ ] API consistency verified
   ```

## Framework Agnosticism

- Drivers and Managers must be agnostic to frameworks
- Users should be able to consume drivers directly without mandatory dependencies
- No framework-specific side effects

## API Consistency

- Code organization and implementation may vary per language
- Naming and API surface must remain consistent across all languages
- Provide a unified developer experience

## Testing

- Structure tests segregated by language and type (unit, integration, BDD)
- Run only tests relevant to the affected language during CI
- Optimize resource usage

## Build System

- Use Bazel to manage builds and tests efficiently
- Run tests incrementally per language and package
- Handle dependencies explicitly
- Enable caching to increase build/test speed

