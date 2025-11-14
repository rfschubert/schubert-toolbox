# Code Quality and Security Rules

This document establishes coding standards for LLM agents working on the Schubert Toolbox project. These rules ensure consistent, secure, and maintainable code across all language implementations.

## Table of Contents

- [Control Flow Rules](#control-flow-rules)
- [Error Handling Rules](#error-handling-rules)
- [Security Rules](#security-rules)
- [Performance Rules](#performance-rules)
- [Code Organization Rules](#code-organization-rules)
- [Documentation Rules](#documentation-rules)

---

## Control Flow Rules

<rule id="avoid-deep-if-else" severity="high">
<description>Avoid excessive if-else nesting (more than 3-4 levels). Use early returns, guard clauses, or refactor into separate functions.</description>
<rationale>Deep nesting reduces readability, increases cognitive load, and makes code harder to test and maintain. Early returns and guard clauses improve code clarity.</rationale>
<examples>

<bad-example language="python">
```python
def process_user_data(user):
    if user is not None:
        if user.is_active:
            if user.has_permission('read'):
                if user.profile is not None:
                    if user.profile.is_complete:
                        return user.profile.data
                    else:
                        return "Profile incomplete"
                else:
                    return "No profile found"
            else:
                return "No permission"
        else:
            return "User inactive"
    else:
        return "User not found"
```
</bad-example>

<good-example language="python">
```python
def process_user_data(user):
    if user is None:
        return "User not found"
    
    if not user.is_active:
        return "User inactive"
    
    if not user.has_permission('read'):
        return "No permission"
    
    if user.profile is None:
        return "No profile found"
    
    if not user.profile.is_complete:
        return "Profile incomplete"
    
    return user.profile.data
```
</good-example>

</examples>
</rule>

<rule id="replace-long-elif-chains" severity="medium">
<description>Replace long elif chains (more than 5 conditions) with dictionary mappings, match-case statements (Python 3.10+), or factory patterns.</description>
<rationale>Long elif chains are hard to maintain and extend. Dictionary mappings and pattern matching provide cleaner, more maintainable alternatives.</rationale>
<examples>

<bad-example language="python">
```python
def get_driver_class(driver_name):
    if driver_name == 'viacep':
        return PostalCodeViacepDriver
    elif driver_name == 'widenet':
        return PostalCodeWidenetDriver
    elif driver_name == 'brasilapi':
        return PostalCodeBrasilApiDriver
    elif driver_name == 'correios':
        return PostalCodeCorreiosDriver
    elif driver_name == 'postmon':
        return PostalCodePostmonDriver
    elif driver_name == 'cepaberto':
        return PostalCodeCepabertoDriver
    else:
        raise ValueError(f"Unknown driver: {driver_name}")
```
</bad-example>

<good-example language="python">
```python
# Dictionary mapping approach
DRIVER_REGISTRY = {
    'viacep': PostalCodeViacepDriver,
    'widenet': PostalCodeWidenetDriver,
    'brasilapi': PostalCodeBrasilApiDriver,
    'correios': PostalCodeCorreiosDriver,
    'postmon': PostalCodePostmonDriver,
    'cepaberto': PostalCodeCepabertoDriver,
}

def get_driver_class(driver_name):
    if driver_name not in DRIVER_REGISTRY:
        raise ValueError(f"Unknown driver: {driver_name}")
    return DRIVER_REGISTRY[driver_name]

# Python 3.10+ match-case approach
def get_driver_class_modern(driver_name):
    match driver_name:
        case 'viacep':
            return PostalCodeViacepDriver
        case 'widenet':
            return PostalCodeWidenetDriver
        case 'brasilapi':
            return PostalCodeBrasilApiDriver
        case _:
            raise ValueError(f"Unknown driver: {driver_name}")
```
</good-example>

</examples>
</rule>

<rule id="use-switch-case-patterns" severity="medium">
<description>Use switch-case statements or equivalent patterns when available in the language for multiple discrete value comparisons.</description>
<rationale>Switch-case statements are more efficient and readable than long if-elif chains for discrete value comparisons.</rationale>
<examples>

<bad-example language="javascript">
```javascript
function getStatusMessage(status) {
    if (status === 'pending') {
        return 'Request is pending';
    } else if (status === 'approved') {
        return 'Request approved';
    } else if (status === 'rejected') {
        return 'Request rejected';
    } else if (status === 'cancelled') {
        return 'Request cancelled';
    } else {
        return 'Unknown status';
    }
}
```
</bad-example>

<good-example language="javascript">
```javascript
function getStatusMessage(status) {
    switch (status) {
        case 'pending':
            return 'Request is pending';
        case 'approved':
            return 'Request approved';
        case 'rejected':
            return 'Request rejected';
        case 'cancelled':
            return 'Request cancelled';
        default:
            return 'Unknown status';
    }
}
```
</good-example>

</examples>
</rule>

---

## Error Handling Rules

<rule id="eafp-principle" severity="high">
<description>Follow the EAFP (Easier to Ask for Forgiveness than Permission) principle. Use try-except blocks instead of pre-validation checks when appropriate.</description>
<rationale>EAFP reduces race conditions, improves performance in the common case, and leads to more robust code. It's particularly important in Python and other dynamic languages.</rationale>
<examples>

<bad-example language="python">
```python
def get_user_data(user_id):
    # LBYL (Look Before You Leap) - not recommended
    if user_id in user_cache:
        if hasattr(user_cache[user_id], 'data'):
            if user_cache[user_id].data is not None:
                return user_cache[user_id].data
    
    # Fetch from database
    user = database.get_user(user_id)
    if user is not None:
        return user.data
    
    return None
```
</bad-example>

<good-example language="python">
```python
def get_user_data(user_id):
    # EAFP (Easier to Ask for Forgiveness than Permission)
    try:
        return user_cache[user_id].data
    except (KeyError, AttributeError):
        pass

    try:
        user = database.get_user(user_id)
        return user.data
    except (DatabaseError, AttributeError):
        return None
```
</good-example>

</examples>
</rule>

<rule id="specific-exception-handling" severity="high">
<description>Use specific exception types rather than broad catches. Avoid bare except clauses or catching Exception unless absolutely necessary.</description>
<rationale>Specific exception handling prevents masking unexpected errors, makes debugging easier, and allows for appropriate error recovery strategies.</rationale>
<examples>

<bad-example language="python">
```python
def load_config_file(filename):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except:  # Too broad - catches everything
        return {}

def process_data(data):
    try:
        result = complex_operation(data)
        return result
    except Exception:  # Too broad for most cases
        logger.error("Something went wrong")
        return None
```
</bad-example>

<good-example language="python">
```python
def load_config_file(filename):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"Config file {filename} not found, using defaults")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in config file {filename}: {e}")
        return {}
    except PermissionError:
        logger.error(f"Permission denied reading config file {filename}")
        raise

def process_data(data):
    try:
        result = complex_operation(data)
        return result
    except ValidationError as e:
        logger.error(f"Data validation failed: {e}")
        return None
    except NetworkError as e:
        logger.warning(f"Network error, retrying: {e}")
        # Implement retry logic
        raise
```
</good-example>

</examples>
</rule>

---

## Security Rules

<rule id="prevent-log-injection" severity="high">
<description>Always sanitize and escape values before logging to prevent log injection attacks. Never log user input directly without validation.</description>
<rationale>Log injection attacks can manipulate log files, inject malicious content, or exploit log processing systems. Proper sanitization prevents these security vulnerabilities.</rationale>
<examples>

<bad-example language="python">
```python
def authenticate_user(username, password):
    # Dangerous - user input logged directly
    logger.info(f"Login attempt for user: {username}")

    if not validate_credentials(username, password):
        # Dangerous - could contain malicious content
        logger.warning(f"Failed login for user: {username}")
        return False

    logger.info(f"Successful login for user: {username}")
    return True

def process_request(request_data):
    # Dangerous - logging raw request data
    logger.debug(f"Processing request: {request_data}")
```
</bad-example>

<good-example language="python">
```python
import re

def sanitize_for_logging(value, max_length=100):
    """Sanitize value for safe logging."""
    if value is None:
        return "None"

    # Convert to string and limit length
    safe_value = str(value)[:max_length]

    # Remove control characters and newlines
    safe_value = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', safe_value)

    # Replace newlines and carriage returns
    safe_value = safe_value.replace('\n', '\\n').replace('\r', '\\r')

    return safe_value

def authenticate_user(username, password):
    safe_username = sanitize_for_logging(username)
    logger.info(f"Login attempt for user: {safe_username}")

    if not validate_credentials(username, password):
        logger.warning(f"Failed login for user: {safe_username}")
        return False

    logger.info(f"Successful login for user: {safe_username}")
    return True

def process_request(request_data):
    # Log only safe, relevant information
    request_id = request_data.get('id', 'unknown')
    safe_request_id = sanitize_for_logging(request_id)
    logger.debug(f"Processing request ID: {safe_request_id}")
```
</good-example>

</examples>
</rule>

<rule id="input-validation-logging" severity="high">
<description>Sanitize user inputs in logs and error messages. Never expose sensitive information or allow format string attacks.</description>
<rationale>User inputs can contain malicious content, sensitive data, or format string exploits. Proper validation and sanitization protect against various attack vectors.</rationale>
<examples>

<bad-example language="python">
```python
def validate_postal_code(postal_code):
    if not postal_code:
        # Dangerous - could log sensitive or malicious content
        raise ValidationError(f"Invalid postal code: {postal_code}")

    # Dangerous - format string vulnerability
    logger.error("Validation failed for: " + postal_code)

def handle_api_error(user_input, error):
    # Dangerous - exposing raw user input and error details
    logger.error(f"API error for input '{user_input}': {error}")
    return f"Error processing {user_input}: {error}"
```
</bad-example>

<good-example language="python">
```python
def validate_postal_code(postal_code):
    if not postal_code:
        # Safe - no user input in exception message
        raise ValidationError("Postal code is required")

    # Safe - sanitized logging
    safe_code = sanitize_for_logging(postal_code, max_length=20)
    logger.error(f"Validation failed for postal code: {safe_code}")

def handle_api_error(user_input, error):
    # Safe - sanitized input, generic error message
    safe_input = sanitize_for_logging(user_input, max_length=50)
    logger.error(f"API error for sanitized input: {safe_input}")

    # Safe - generic user-facing message
    return "Error processing request. Please check your input and try again."
```
</bad-example>

</examples>
</rule>

---

## Performance Rules

<rule id="avoid-nested-recursion-in-loops" severity="high">
<description>Prohibit recursive function calls inside loop structures (for, while, foreach) as this can lead to exponential time complexity O(n^k) where n is the loop iterations and k is the recursion depth.</description>
<rationale>Nested recursion within loops can cause performance degradation from O(n) or O(log n) to exponential complexity, leading to system slowdowns, timeouts, or stack overflow errors. This pattern should be avoided in favor of pre-computation, memoization, or iterative solutions.</rationale>
<examples>

<bad-example language="python">
```python
def process_data_list(data_list):
    """BAD: Recursive calls inside loop - O(n * 2^k) complexity"""
    results = []

    for item in data_list:  # O(n)
        # Recursive fibonacci inside loop - O(2^k) for each iteration
        fib_result = fibonacci_recursive(item.value)
        results.append(fib_result)

    return results

def fibonacci_recursive(n):
    """Exponential time complexity O(2^n)"""
    if n <= 1:
        return n
    return fibonacci_recursive(n - 1) + fibonacci_recursive(n - 2)

def validate_nested_structure(items):
    """BAD: Recursive validation inside loop"""
    for item in items:
        # Recursive tree traversal for each item
        if not validate_tree_recursive(item.tree_data):
            return False
    return True

def validate_tree_recursive(node):
    """Recursive tree validation"""
    if not node:
        return True

    if not node.is_valid():
        return False

    # Recursively validate children
    for child in node.children:
        if not validate_tree_recursive(child):
            return False

    return True
```
</bad-example>

<good-example language="python">
```python
def process_data_list(data_list):
    """GOOD: Pre-compute or use memoization to avoid nested recursion"""
    results = []

    # Approach 1: Pre-compute all needed fibonacci values
    max_value = max(item.value for item in data_list)
    fib_cache = compute_fibonacci_iterative(max_value)

    for item in data_list:  # O(n)
        # O(1) lookup instead of O(2^k) recursive call
        fib_result = fib_cache[item.value]
        results.append(fib_result)

    return results

def compute_fibonacci_iterative(max_n):
    """Iterative fibonacci computation with caching - O(n)"""
    if max_n < 0:
        return {}

    cache = {0: 0, 1: 1}

    for i in range(2, max_n + 1):
        cache[i] = cache[i - 1] + cache[i - 2]

    return cache

# Alternative: Memoization decorator
from functools import lru_cache

@lru_cache(maxsize=None)
def fibonacci_memoized(n):
    """Memoized fibonacci - O(n) with caching"""
    if n <= 1:
        return n
    return fibonacci_memoized(n - 1) + fibonacci_memoized(n - 2)

def process_data_list_memoized(data_list):
    """GOOD: Using memoization to cache recursive results"""
    results = []

    for item in data_list:
        # First call computes, subsequent calls use cache
        fib_result = fibonacci_memoized(item.value)
        results.append(fib_result)

    return results

def validate_nested_structure(items):
    """GOOD: Separate validation phases"""
    # Phase 1: Collect all trees to validate
    trees_to_validate = [item.tree_data for item in items]

    # Phase 2: Batch validate trees (can be optimized further)
    return all(validate_tree_iterative(tree) for tree in trees_to_validate)

def validate_tree_iterative(root):
    """GOOD: Iterative tree validation using stack"""
    if not root:
        return True

    stack = [root]

    while stack:
        node = stack.pop()

        if not node.is_valid():
            return False

        # Add children to stack for processing
        stack.extend(node.children)

    return True
```
</good-example>

</examples>
</rule>

---

## Code Organization Rules

<rule id="single-responsibility" severity="medium">
<description>Each function and class should have a single, well-defined responsibility. Functions should be small and focused.</description>
<rationale>Single responsibility principle improves code maintainability, testability, and reusability. It makes code easier to understand and modify.</rationale>
<examples>

<bad-example language="python">
```python
def process_user_registration(user_data):
    # Too many responsibilities in one function

    # Validate email
    if '@' not in user_data['email']:
        raise ValueError("Invalid email")

    # Hash password
    import hashlib
    hashed_password = hashlib.sha256(user_data['password'].encode()).hexdigest()

    # Save to database
    db.execute("INSERT INTO users (email, password) VALUES (?, ?)",
               user_data['email'], hashed_password)

    # Send welcome email
    smtp_server = smtplib.SMTP('smtp.example.com', 587)
    smtp_server.send_email(user_data['email'], "Welcome!", "Welcome to our service!")

    # Log registration
    logger.info(f"User registered: {user_data['email']}")

    return True
```
</bad-example>

<good-example language="python">
```python
def validate_email(email):
    """Validate email format."""
    if '@' not in email:
        raise ValueError("Invalid email format")

def hash_password(password):
    """Hash password securely."""
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()

def save_user_to_database(email, hashed_password):
    """Save user to database."""
    db.execute("INSERT INTO users (email, password) VALUES (?, ?)",
               email, hashed_password)

def send_welcome_email(email):
    """Send welcome email to new user."""
    smtp_server = smtplib.SMTP('smtp.example.com', 587)
    smtp_server.send_email(email, "Welcome!", "Welcome to our service!")

def process_user_registration(user_data):
    """Process user registration with proper separation of concerns."""
    validate_email(user_data['email'])
    hashed_password = hash_password(user_data['password'])
    save_user_to_database(user_data['email'], hashed_password)
    send_welcome_email(user_data['email'])

    safe_email = sanitize_for_logging(user_data['email'])
    logger.info(f"User registered: {safe_email}")

    return True
```
</good-example>

</examples>
</rule>

<rule id="avoid-magic-numbers" severity="medium">
<description>Replace magic numbers and strings with named constants. Use configuration files or environment variables for configurable values.</description>
<rationale>Magic numbers make code harder to understand and maintain. Named constants provide context and make values easier to change.</rationale>
<examples>

<bad-example language="python">
```python
def validate_postal_code(code):
    if len(code) != 8:  # Magic number
        return False

    # Magic timeout value
    response = requests.get(url, timeout=30)

    # Magic status codes
    if response.status_code == 429:
        time.sleep(60)  # Magic sleep duration

def retry_operation(func, *args):
    for i in range(3):  # Magic retry count
        try:
            return func(*args)
        except Exception:
            time.sleep(2 ** i)  # Magic backoff
```
</bad-example>

<good-example language="python">
```python
# Constants at module level
BRAZILIAN_POSTAL_CODE_LENGTH = 8
DEFAULT_REQUEST_TIMEOUT = 30
HTTP_TOO_MANY_REQUESTS = 429
RATE_LIMIT_SLEEP_DURATION = 60
DEFAULT_RETRY_COUNT = 3
BASE_BACKOFF_SECONDS = 2

def validate_postal_code(code):
    if len(code) != BRAZILIAN_POSTAL_CODE_LENGTH:
        return False

    response = requests.get(url, timeout=DEFAULT_REQUEST_TIMEOUT)

    if response.status_code == HTTP_TOO_MANY_REQUESTS:
        time.sleep(RATE_LIMIT_SLEEP_DURATION)

def retry_operation(func, *args, max_retries=DEFAULT_RETRY_COUNT):
    for attempt in range(max_retries):
        try:
            return func(*args)
        except Exception:
            if attempt < max_retries - 1:
                time.sleep(BASE_BACKOFF_SECONDS ** attempt)
            else:
                raise
```
</good-example>

</examples>
</rule>

---

## Documentation Rules

<rule id="docstring-requirements" severity="medium">
<description>All public functions, classes, and modules must have comprehensive docstrings following the project's documentation standards.</description>
<rationale>Good documentation improves code maintainability, helps other developers understand the codebase, and serves as a contract for the API.</rationale>
<examples>

<bad-example language="python">
```python
def get(self, postal_code):
    # No docstring
    formatted_cep = self._formatter_manager.format(postal_code, driver="brazilian_postalcode")
    url = f"{self._base_url}/{formatted_cep}/json/"
    response = requests.get(url, timeout=self._config['timeout'])
    return self._convert_to_address(response.json(), formatted_cep)

class PostalCodeManager:
    # No class docstring
    def __init__(self):
        self._drivers = {}
```
</bad-example>

<good-example language="python">
```python
def get(self, postal_code: str) -> Address:
    """
    Get address information for Brazilian postal code (CEP).

    Args:
        postal_code: Brazilian postal code (CEP) in format XXXXX-XXX or XXXXXXXX

    Returns:
        Address object with postal code information

    Raises:
        ValidationError: If postal code is invalid or not found
        NetworkError: If API request fails
    """
    formatted_cep = self._formatter_manager.format(postal_code, driver="brazilian_postalcode")
    url = f"{self._base_url}/{formatted_cep}/json/"
    response = requests.get(url, timeout=self._config['timeout'])
    return self._convert_to_address(response.json(), formatted_cep)

class PostalCodeManager:
    """
    Manager for postal code lookup operations.

    Provides a unified interface for multiple postal code lookup drivers,
    with automatic driver selection, caching, and error handling.

    Example:
        manager = PostalCodeManager()
        address = manager.get("88304-053", driver="viacep")
    """

    def __init__(self):
        """Initialize the postal code manager with empty driver registry."""
        self._drivers = {}
```
</good-example>

</examples>
</rule>

<rule id="no-emojis-in-code" severity="high">
<description>Never use emojis in source code, logs, error messages, or documentation. Use clear, professional text instead.</description>
<rationale>Emojis can cause encoding issues, are not universally supported across all systems, and reduce the professional appearance of code and logs.</rationale>
<examples>

<bad-example language="python">
```python
def validate_data(data):
    if not data:
        logger.error("❌ Validation failed: No data provided")
        return False

    logger.info("✅ Data validation successful")
    return True

# Bad documentation
def process_request():
    """
    Process user request 🚀

    Returns:
        Success status ✅ or failure ❌
    """
    pass
```
</bad-example>

<good-example language="python">
```python
def validate_data(data):
    if not data:
        logger.error("VALIDATION_FAILED: No data provided")
        return False

    logger.info("VALIDATION_SUCCESS: Data validation completed")
    return True

# Good documentation
def process_request():
    """
    Process user request.

    Returns:
        bool: True if successful, False if failed
    """
    pass
```
</good-example>

</examples>
</rule>

---

## Language-Specific Examples

### JavaScript

<rule id="js-avoid-nested-recursion-loops" severity="high">
<description>Avoid recursive function calls within JavaScript loops to prevent exponential time complexity.</description>
<rationale>JavaScript's single-threaded nature makes exponential complexity particularly problematic, potentially freezing the browser or Node.js process.</rationale>
<examples>

<bad-example language="javascript">
```javascript
// BAD: Recursive calls inside loop
function processUserData(users) {
    const results = [];

    for (const user of users) {
        // Recursive tree processing for each user - exponential complexity
        const processedData = processUserTreeRecursive(user.dataTree);
        results.push(processedData);
    }

    return results;
}

function processUserTreeRecursive(node) {
    if (!node) return null;

    const processed = {
        id: node.id,
        value: computeExpensiveValue(node.data),
        children: []
    };

    // Recursive calls for each child
    for (const child of node.children) {
        processed.children.push(processUserTreeRecursive(child));
    }

    return processed;
}
```
</bad-example>

<good-example language="javascript">
```javascript
// GOOD: Iterative approach with queue
function processUserData(users) {
    const results = [];

    for (const user of users) {
        // Process each tree iteratively
        const processedData = processUserTreeIterative(user.dataTree);
        results.push(processedData);
    }

    return results;
}

function processUserTreeIterative(root) {
    if (!root) return null;

    const result = { id: root.id, value: computeExpensiveValue(root.data), children: [] };
    const queue = [{ node: root, parent: result }];

    while (queue.length > 0) {
        const { node, parent } = queue.shift();

        for (const child of node.children) {
            const processedChild = {
                id: child.id,
                value: computeExpensiveValue(child.data),
                children: []
            };

            parent.children.push(processedChild);
            queue.push({ node: child, parent: processedChild });
        }
    }

    return result;
}

// Alternative: Memoization with Map
const memoCache = new Map();

function processUserDataMemoized(users) {
    const results = [];

    for (const user of users) {
        const cacheKey = generateTreeCacheKey(user.dataTree);

        if (memoCache.has(cacheKey)) {
            results.push(memoCache.get(cacheKey));
        } else {
            const processedData = processUserTreeIterative(user.dataTree);
            memoCache.set(cacheKey, processedData);
            results.push(processedData);
        }
    }

    return results;
}
```
</good-example>

</examples>
</rule>

<rule id="js-async-await" severity="medium">
<description>Prefer async/await over Promise chains for better readability and error handling.</description>
<rationale>Async/await syntax is more readable, easier to debug, and provides better stack traces than Promise chains.</rationale>
<examples>

<bad-example language="javascript">
```javascript
function fetchUserData(userId) {
    return fetch(`/api/users/${userId}`)
        .then(response => response.json())
        .then(user => {
            return fetch(`/api/profiles/${user.profileId}`)
                .then(response => response.json())
                .then(profile => {
                    return { user, profile };
                });
        })
        .catch(error => {
            console.error('Error fetching user data:', error);
            throw error;
        });
}
```
</bad-example>

<good-example language="javascript">
```javascript
async function fetchUserData(userId) {
    try {
        const userResponse = await fetch(`/api/users/${userId}`);
        const user = await userResponse.json();

        const profileResponse = await fetch(`/api/profiles/${user.profileId}`);
        const profile = await profileResponse.json();

        return { user, profile };
    } catch (error) {
        console.error('Error fetching user data:', error);
        throw error;
    }
}
```
</good-example>

</examples>
</rule>

### PHP

<rule id="php-avoid-nested-recursion-loops" severity="high">
<description>Avoid recursive function calls within PHP loops to prevent exponential time complexity and potential memory exhaustion.</description>
<rationale>PHP's memory limits and execution time limits make exponential complexity particularly dangerous, often resulting in fatal errors or script timeouts.</rationale>
<examples>

<bad-example language="php">
```php
<?php
// BAD: Recursive calls inside loop
class DataProcessor {
    public function processItems(array $items): array {
        $results = [];

        foreach ($items as $item) {
            // Recursive processing for each item - exponential complexity
            $processed = $this->processItemRecursive($item->getData());
            $results[] = $processed;
        }

        return $results;
    }

    private function processItemRecursive(array $data, int $depth = 0): array {
        if ($depth > 10) {
            return $data; // Base case
        }

        $processed = [];

        foreach ($data as $key => $value) {
            if (is_array($value)) {
                // Recursive call for nested arrays
                $processed[$key] = $this->processItemRecursive($value, $depth + 1);
            } else {
                $processed[$key] = $this->expensiveTransformation($value);
            }
        }

        return $processed;
    }

    private function expensiveTransformation($value) {
        // Simulate expensive operation
        return strtoupper($value);
    }
}
```
</bad-example>

<good-example language="php">
```php
<?php
// GOOD: Iterative approach with SplStack
class DataProcessor {
    private array $cache = [];

    public function processItems(array $items): array {
        $results = [];

        foreach ($items as $item) {
            $cacheKey = $this->generateCacheKey($item->getData());

            if (isset($this->cache[$cacheKey])) {
                $results[] = $this->cache[$cacheKey];
            } else {
                // Process iteratively instead of recursively
                $processed = $this->processItemIterative($item->getData());
                $this->cache[$cacheKey] = $processed;
                $results[] = $processed;
            }
        }

        return $results;
    }

    private function processItemIterative(array $data): array {
        $stack = new \SplStack();
        $result = [];

        // Initialize stack with root level data
        foreach ($data as $key => $value) {
            $stack->push([
                'key' => $key,
                'value' => $value,
                'path' => [$key],
                'parent' => &$result
            ]);
        }

        while (!$stack->isEmpty()) {
            $item = $stack->pop();
            $key = $item['key'];
            $value = $item['value'];
            $parent = &$item['parent'];

            if (is_array($value)) {
                $parent[$key] = [];

                // Add children to stack for processing
                foreach ($value as $childKey => $childValue) {
                    $stack->push([
                        'key' => $childKey,
                        'value' => $childValue,
                        'path' => array_merge($item['path'], [$childKey]),
                        'parent' => &$parent[$key]
                    ]);
                }
            } else {
                $parent[$key] = $this->expensiveTransformation($value);
            }
        }

        return $result;
    }

    private function generateCacheKey(array $data): string {
        return md5(serialize($data));
    }

    private function expensiveTransformation($value): string {
        return strtoupper($value);
    }
}

// Alternative: Pre-computation approach
class OptimizedDataProcessor {
    public function processItems(array $items): array {
        // Phase 1: Collect all values that need transformation
        $allValues = $this->collectAllValues($items);

        // Phase 2: Batch process transformations
        $transformedValues = $this->batchTransform($allValues);

        // Phase 3: Apply transformations to original structure
        return $this->applyTransformations($items, $transformedValues);
    }

    private function collectAllValues(array $items): array {
        $values = [];

        foreach ($items as $item) {
            $this->extractValues($item->getData(), $values);
        }

        return array_unique($values);
    }

    private function extractValues(array $data, array &$values): void {
        foreach ($data as $value) {
            if (is_array($value)) {
                $this->extractValues($value, $values);
            } else {
                $values[] = $value;
            }
        }
    }

    private function batchTransform(array $values): array {
        $transformed = [];

        foreach ($values as $value) {
            $transformed[$value] = $this->expensiveTransformation($value);
        }

        return $transformed;
    }

    private function applyTransformations(array $items, array $transformedValues): array {
        $results = [];

        foreach ($items as $item) {
            $results[] = $this->applyToStructure($item->getData(), $transformedValues);
        }

        return $results;
    }

    private function applyToStructure(array $data, array $transformedValues): array {
        $result = [];

        foreach ($data as $key => $value) {
            if (is_array($value)) {
                $result[$key] = $this->applyToStructure($value, $transformedValues);
            } else {
                $result[$key] = $transformedValues[$value];
            }
        }

        return $result;
    }

    private function expensiveTransformation($value): string {
        return strtoupper($value);
    }
}
```
</good-example>

</examples>
</rule>

<rule id="php-type-declarations" severity="medium">
<description>Use type declarations for function parameters and return types in PHP 7.0+.</description>
<rationale>Type declarations improve code reliability, catch errors early, and provide better IDE support and documentation.</rationale>
<examples>

<bad-example language="php">
```php
function validatePostalCode($code) {
    if (strlen($code) !== 8) {
        return false;
    }
    return true;
}

function getDriverClass($driverName) {
    $drivers = [
        'viacep' => PostalCodeViacepDriver::class,
        'widenet' => PostalCodeWidenetDriver::class,
    ];

    return $drivers[$driverName] ?? null;
}
```
</bad-example>

<good-example language="php">
```php
function validatePostalCode(string $code): bool {
    if (strlen($code) !== 8) {
        return false;
    }
    return true;
}

function getDriverClass(string $driverName): ?string {
    $drivers = [
        'viacep' => PostalCodeViacepDriver::class,
        'widenet' => PostalCodeWidenetDriver::class,
    ];

    return $drivers[$driverName] ?? null;
}
```
</good-example>

</examples>
</rule>

---

## Enforcement

These rules should be enforced through:

1. **Code Review**: All code changes must be reviewed against these standards
2. **Automated Tools**: Use linters and static analysis tools where available
3. **Documentation**: Reference this document in all LLM instructions
4. **Training**: Ensure all team members and LLM agents understand these rules

## Updates

This document should be updated as the project evolves and new patterns emerge. All updates must be reviewed and approved by the project maintainers.

