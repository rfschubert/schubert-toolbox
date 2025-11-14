"""
PostalCode Manager for orchestrating postal code lookup drivers.

This manager provides a unified interface for managing postal code lookup drivers
following the Manager Pattern documented in docs/patterns/manager_pattern_details.md.
"""

import asyncio
import logging
import time
from typing import Any, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor

from contracts.manager_contract import (
    AbstractManagerContract,
    DriverLoadError,
    DriverNotFoundError,
)
from standards.address import Address
from utils.logging_security import sanitize_cache_key, sanitize_error_message, sanitize_user_input
from .async_driver_wrapper import AsyncDriverWrapper

# Import ValidationError
try:
    from validation_base import ValidationError
except ImportError:
    # Fallback for testing
    class ValidationError(Exception):
        """Custom exception for validation errors."""

        def __init__(self, message: str, error_code: str = None):
            super().__init__(message)
            self.error_code = error_code


logger = logging.getLogger(__name__)


class PostalCodeManager(AbstractManagerContract):
    """
    Manager for postal code lookup drivers.

    Provides unified interface for loading and using postal code drivers
    that return Address objects. All drivers must implement the same interface:
    - get(postal_code: str) -> Address
    - configure(**kwargs) -> Self
    - get_config() -> Dict[str, Any]

    Example usage:
        # Manager-orchestrated usage
        manager = PostalCodeManager()
        driver = manager.load("viacep")
        address = driver.get("01310-100")

        # Direct manager method
        address = manager.get("01310-100", driver="viacep")
    """

    def __init__(self):
        """Initialize PostalCodeManager with empty driver registry and async capabilities."""
        super().__init__()
        self._drivers: dict[str, dict[str, Any]] = {}
        self._default_driver: str | None = None
        self._cache: dict[str, Any] = {}
        self._cache_enabled: bool = False

        # Thread pool for async operations (first-to-respond functionality)
        self._thread_pool = ThreadPoolExecutor(
            max_workers=5,
            thread_name_prefix="postal-driver"
        )

        # Register default drivers
        self._register_default_drivers()

        logger.debug("PostalCodeManager initialized")

    def __del__(self):
        """Cleanup thread pool on destruction."""
        if hasattr(self, '_thread_pool'):
            self._thread_pool.shutdown(wait=False)

    def _register_default_drivers(self) -> None:
        """Register default postal code drivers."""
        # Register ViaCEP driver
        try:
            from drivers.postalcode.postalcode_viacep_driver import PostalCodeViacepDriver

            self.register_driver(
                "viacep",
                PostalCodeViacepDriver,
                description="ViaCEP Brazilian postal code service",
                version="1.0.0",
                country="BR",
            )
            logger.debug("Registered ViaCEP driver")
        except ImportError as e:
            logger.warning("Failed to register ViaCEP driver: %s", e)

        # Register WideNet driver
        try:
            from drivers.postalcode.postalcode_widenet_driver import PostalCodeWidenetDriver

            self.register_driver(
                "widenet",
                PostalCodeWidenetDriver,
                description="WideNet Brazilian postal code service",
                version="1.0.0",
                country="BR",
            )
            logger.debug("Registered WideNet driver")
        except ImportError as e:
            logger.warning("Failed to register WideNet driver: %s", e)

        # Register BrasilAPI driver
        try:
            from drivers.postalcode.postalcode_brasilapi_driver import PostalCodeBrasilApiDriver

            self.register_driver(
                "brasilapi",
                PostalCodeBrasilApiDriver,
                description="BrasilAPI Brazilian postal code service",
                version="1.0.0",
                country="BR",
            )
            logger.debug("Registered BrasilAPI driver")
        except ImportError as e:
            logger.warning("Failed to register BrasilAPI driver: %s", e)

        # Correios drivers removed due to API authentication issues
        # The official Correios SOAP API requires authentication
        # The alternative Correios API requires captcha validation
        # These are not suitable for automated postal code lookup

    def load(self, driver_name: str, **config) -> Any:
        """
        Load and configure a postal code driver.

        Args:
            driver_name: Name of the driver to load
            **config: Configuration options for the driver

        Returns:
            Configured driver instance that implements postal code interface

        Raises:
            DriverNotFoundError: If driver is not available
            DriverLoadError: If driver fails to load
        """
        if not self.has_driver(driver_name):
            raise DriverNotFoundError(driver_name, self.list_drivers())

        try:
            driver_info = self._drivers[driver_name]
            driver_class = driver_info["class"]

            # Instantiate driver
            driver_instance = driver_class()

            # Apply configuration if provided
            if config:
                driver_instance.configure(**config)

            logger.debug("Loaded postal code driver: %s", driver_name)
            return driver_instance

        except Exception as e:
            logger.error("Failed to load driver %s: %s", driver_name, e)
            raise DriverLoadError(driver_name, str(e))

    def get(self, postal_code: str, driver: str = "default") -> Address:
        """
        Get address for postal code using specified driver.

        Args:
            postal_code: Postal code to lookup
            driver: Driver name to use (defaults to default driver)

        Returns:
            Address object with postal code information

        Raises:
            DriverNotFoundError: If driver is not available
            PostalCodeError: If postal code lookup fails
        """
        if driver == "default":
            if not self._default_driver:
                available = self.list_drivers()
                if not available:
                    raise DriverNotFoundError("default", available)
                driver = available[0]  # Use first available driver
            else:
                driver = self._default_driver

        # Check cache first
        cache_key = f"{driver}:{postal_code}"
        if self._cache_enabled and cache_key in self._cache:
            # Security: Sanitize cache key to prevent log injection
            safe_cache_key = sanitize_cache_key(cache_key)
            logger.debug("Returning cached result for %s", safe_cache_key)
            return self._cache[cache_key]

        # Load driver and get address
        driver_instance = self.load(driver)
        address = driver_instance.get(postal_code)

        # Cache result
        if self._cache_enabled:
            self._cache[cache_key] = address
            # Security: Sanitize cache key to prevent log injection
            safe_cache_key = sanitize_cache_key(cache_key)
            logger.debug("Cached result for %s", safe_cache_key)

        return address

    def get_or_raise(self, postal_code: str, driver: str = "default") -> Address:
        """
        Get address or raise exception on failure.

        Args:
            postal_code: Postal code to lookup
            driver: Driver name to use

        Returns:
            Address object

        Raises:
            PostalCodeError: If postal code is invalid or lookup fails
        """
        address = self.get(postal_code, driver)

        # Validate address completeness
        if not address.is_complete():
            from validation_base import ValidationError

            raise ValidationError(
                f"Incomplete address returned for postal code: {postal_code}",
                error_code="POSTAL_CODE_INCOMPLETE_ADDRESS",
            )

        return address

    def bulk_get(self, postal_codes: list[str], driver: str = "default") -> list[Address]:
        """
        Get addresses for multiple postal codes.

        Args:
            postal_codes: List of postal codes to lookup
            driver: Driver name to use

        Returns:
            List of Address objects
        """
        addresses = []
        for postal_code in postal_codes:
            try:
                address = self.get(postal_code, driver)
                addresses.append(address)
            except Exception as e:
                # Security: Sanitize user input and error message to prevent log injection
                safe_postal_code = sanitize_user_input(postal_code)
                safe_error = sanitize_error_message(e)
                logger.warning("Failed to get address for %s: %s", safe_postal_code, safe_error)
                # Create empty address with error info
                error_address = Address(postal_code=postal_code, formatted_address=f"Error: {e!s}")
                addresses.append(error_address)

        return addresses

    def set_default_driver(self, driver_name: str) -> None:
        """
        Set default driver for postal code lookups.

        Args:
            driver_name: Name of driver to set as default

        Raises:
            DriverNotFoundError: If driver is not available
        """
        if not self.has_driver(driver_name):
            raise DriverNotFoundError(driver_name, self.list_drivers())

        self._default_driver = driver_name
        logger.info("Default driver set to: %s", driver_name)

    def get_default_driver(self) -> str | None:
        """Get current default driver name."""
        return self._default_driver

    def enable_cache(self, enabled: bool = True) -> "PostalCodeManager":
        """
        Enable or disable result caching.

        Args:
            enabled: Whether to enable caching

        Returns:
            Self for method chaining
        """
        self._cache_enabled = enabled
        if not enabled:
            self._cache.clear()
            logger.debug("Cache disabled and cleared")
        else:
            logger.debug("Cache enabled")

        return self

    def clear_cache(self) -> "PostalCodeManager":
        """
        Clear cached results.

        Returns:
            Self for method chaining
        """
        self._cache.clear()
        logger.debug("Cache cleared")
        return self

    def get_cache_stats(self) -> dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        return {
            "enabled": self._cache_enabled,
            "size": len(self._cache),
            "keys": list(self._cache.keys()),
        }

    async def get_first_response(
        self,
        postal_code: str,
        drivers: Optional[List[str]] = None,
        timeout: float = 10.0
    ) -> Address:
        """
        Get postal code using first-to-respond pattern.

        Executes multiple drivers concurrently and returns the first successful response.
        Automatically cancels remaining requests when one succeeds.

        Args:
            postal_code: Brazilian postal code (CEP) to lookup
            drivers: Optional list of driver names to use (default: all available)
            timeout: Maximum time to wait for any response in seconds

        Returns:
            Address: Address object from the first successful driver

        Raises:
            ValidationError: If all drivers fail or timeout occurs

        Example:
            manager = PostalCodeManager()
            address = await manager.get_first_response("88304-053")
            print(f"Got address from {address.verification_source}: {address.locality}")
        """
        # Use all available drivers if none specified
        if drivers is None:
            drivers = self.list_drivers()

        if not drivers:
            raise ValidationError(
                "No drivers available for postal code lookup",
                error_code="POSTAL_CODE_NO_DRIVERS"
            )

        # Sanitize input
        clean_postal_code = sanitize_user_input(postal_code)
        logger.info(f"Starting first-to-respond lookup for CEP: {clean_postal_code}")

        # Create async wrappers for all drivers
        async_drivers = []
        for driver_name in drivers:
            try:
                sync_driver = self.load(driver_name)
                async_driver = AsyncDriverWrapper(sync_driver, self._thread_pool)
                async_drivers.append((async_driver, driver_name))
            except Exception as e:
                logger.warning(f"Failed to load driver {driver_name}: {e}")
                continue

        if not async_drivers:
            raise ValidationError(
                "No drivers could be loaded",
                error_code="POSTAL_CODE_NO_DRIVERS_LOADED"
            )

        # Create tasks for all drivers
        tasks = []
        for async_driver, driver_name in async_drivers:
            task = asyncio.create_task(
                self._safe_driver_call(async_driver, driver_name, clean_postal_code),
                name=f"driver-{driver_name}"
            )
            tasks.append(task)

        try:
            # Wait for first successful completion
            done, pending = await asyncio.wait(
                tasks,
                timeout=timeout,
                return_when=asyncio.FIRST_COMPLETED
            )

            # Cancel all pending tasks immediately
            for task in pending:
                if not task.done():
                    task.cancel()
                    logger.debug(f"Cancelled pending task: {task.get_name()}")

            # Wait for cancelled tasks to finish cancelling
            if pending:
                try:
                    await asyncio.wait(pending, timeout=0.1)
                except asyncio.TimeoutError:
                    pass

            # Check completed tasks for success
            for task in done:
                try:
                    result = await task
                    if result[0] is not None:  # Successful result
                        address, successful_driver = result
                        logger.info(
                            f"First response from {successful_driver} for CEP: {clean_postal_code}"
                        )
                        return address
                except asyncio.CancelledError:
                    # Task was cancelled, skip it
                    logger.debug(f"Task {task.get_name()} was cancelled")
                    continue
                except Exception as e:
                    logger.debug(f"Task {task.get_name()} failed: {e}")
                    continue

            # If we get here, all completed tasks failed
            # Wait a bit more for any remaining tasks
            if pending:
                try:
                    additional_done, still_pending = await asyncio.wait(
                        pending,
                        timeout=1.0,  # Short additional timeout
                        return_when=asyncio.FIRST_COMPLETED
                    )

                    # Cancel any still pending
                    for task in still_pending:
                        task.cancel()

                    # Check additional completed tasks
                    for task in additional_done:
                        try:
                            result = await task
                            if result[0] is not None:
                                address, successful_driver = result
                                logger.info(
                                    f"Late response from {successful_driver} for CEP: {clean_postal_code}"
                                )
                                return address
                        except asyncio.CancelledError:
                            # Task was cancelled, skip it
                            continue
                        except Exception:
                            continue

                except asyncio.TimeoutError:
                    pass

        except asyncio.TimeoutError:
            # Cancel all tasks on timeout
            for task in tasks:
                task.cancel()

            logger.warning(f"All drivers timed out for CEP: {clean_postal_code}")
            raise ValidationError(
                f"Request timed out after {timeout} seconds",
                error_code="POSTAL_CODE_TIMEOUT"
            )

        # All drivers failed
        logger.error(f"All drivers failed for CEP: {clean_postal_code}")
        raise ValidationError(
            f"All drivers failed for postal code: {clean_postal_code}",
            error_code="POSTAL_CODE_ALL_DRIVERS_FAILED"
        )

    async def _safe_driver_call(
        self,
        async_driver: AsyncDriverWrapper,
        driver_name: str,
        postal_code: str
    ) -> Tuple[Optional[Address], str]:
        """
        Safely execute async driver call with error handling.

        Args:
            async_driver: Async wrapper for driver
            driver_name: Name of the driver
            postal_code: CEP to lookup

        Returns:
            Tuple[Optional[Address], str]: Address (None if failed) and driver name
        """
        try:
            start_time = time.time()
            address = await async_driver.get_async(postal_code)
            response_time = time.time() - start_time

            logger.debug(
                f"Driver {driver_name} completed in {response_time:.2f}s for CEP: {postal_code}"
            )
            return address, driver_name

        except Exception as e:
            error_msg = sanitize_error_message(str(e))
            logger.debug(f"Driver {driver_name} failed for CEP {postal_code}: {error_msg}")
            return None, driver_name

    def get_first_response_sync(
        self,
        postal_code: str,
        drivers: Optional[List[str]] = None,
        timeout: float = 10.0
    ) -> Address:
        """
        Synchronous wrapper for get_first_response.

        This allows using the first-to-respond pattern in synchronous code.

        Args:
            postal_code: Brazilian postal code (CEP) to lookup
            drivers: Optional list of driver names to use
            timeout: Maximum time to wait for any response

        Returns:
            Address: Address object from the first successful driver

        Example:
            manager = PostalCodeManager()
            address = manager.get_first_response_sync("88304-053")
            print(f"Got address from {address.verification_source}")
        """
        try:
            # Get or create event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, we need to use a different approach
                # This can happen in Jupyter notebooks or other async contexts
                import nest_asyncio
                nest_asyncio.apply()
        except RuntimeError:
            # No event loop in current thread, create new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        try:
            return loop.run_until_complete(
                self.get_first_response(postal_code, drivers, timeout)
            )
        except Exception as e:
            # If nest_asyncio is not available, try alternative approach
            if "nest_asyncio" in str(e):
                # Fallback: run in new thread
                import threading
                import queue

                result_queue = queue.Queue()
                exception_queue = queue.Queue()

                def run_async():
                    try:
                        new_loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(new_loop)
                        result = new_loop.run_until_complete(
                            self.get_first_response(postal_code, drivers, timeout)
                        )
                        result_queue.put(result)
                    except Exception as ex:
                        exception_queue.put(ex)
                    finally:
                        new_loop.close()

                thread = threading.Thread(target=run_async)
                thread.start()
                thread.join()

                if not exception_queue.empty():
                    raise exception_queue.get()

                return result_queue.get()
            else:
                raise
