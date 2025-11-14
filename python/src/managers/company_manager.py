"""
Company Manager for Brazilian legal entity (CNPJ) lookups.

This manager provides unified access to multiple company data providers,
supporting both individual lookups and first-to-respond patterns for
optimal performance and reliability.
"""

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional, Tuple

from contracts.manager_contract import AbstractManagerContract
from standards.company import Company
from standards.core.base import ValidationError
from .async_driver_wrapper import AsyncDriverWrapper

logger = logging.getLogger(__name__)


class CompanyManager(AbstractManagerContract):
    """
    Manager for Brazilian company (CNPJ) data lookups.
    
    Provides unified access to multiple company data providers with support for:
    - Individual driver usage
    - First-to-respond pattern for optimal performance
    - Automatic address resolution using postal code lookup
    - Rate limiting and error handling
    
    Example:
        manager = CompanyManager()
        
        # Basic usage
        company = manager.get("11.222.333/0001-81")
        
        # First-to-respond for maximum speed
        company = manager.get_first_response_sync("11.222.333/0001-81")
        
        # Async usage
        company = await manager.get_first_response("11.222.333/0001-81")
    """
    
    def __init__(self):
        """Initialize CompanyManager with default configuration."""
        super().__init__()
        
        # Thread pool for async operations (first-to-respond functionality)
        self._thread_pool = ThreadPoolExecutor(
            max_workers=5, 
            thread_name_prefix="company-driver"
        )
        
        # Register available drivers
        self._register_drivers()
        
        logger.info("CompanyManager initialized with %d drivers", len(self._drivers))
    
    def __del__(self):
        """Cleanup thread pool on destruction."""
        if hasattr(self, '_thread_pool'):
            self._thread_pool.shutdown(wait=False)
    
    def _register_drivers(self):
        """Register all available company drivers."""
        # Register BrasilAPI driver
        try:
            from drivers.company.company_brasilapi_driver import CompanyBrasilApiDriver

            self.register_driver(
                "brasilapi",
                CompanyBrasilApiDriver,
                description="BrasilAPI Brazilian company data service",
                version="1.0.0",
                country="BR",
            )
            logger.debug("Registered BrasilAPI company driver")
        except ImportError as e:
            logger.warning("Failed to register BrasilAPI company driver: %s", e)

        # Register CNPJA driver
        try:
            from drivers.company.company_cnpja_driver import CompanyCnpjaDriver

            self.register_driver(
                "cnpja",
                CompanyCnpjaDriver,
                description="CNPJA.com Brazilian company data service with rate limiting",
                version="1.0.0",
                country="BR",
            )
            logger.debug("Registered CNPJA company driver")
        except ImportError as e:
            logger.warning("Failed to register CNPJA company driver: %s", e)

        # Register OpenCNPJ driver
        try:
            from drivers.company.company_opencnpj_driver import CompanyOpencnpjDriver

            self.register_driver(
                "opencnpj",
                CompanyOpencnpjDriver,
                description="OpenCNPJ.org Brazilian company data service",
                version="1.0.0",
                country="BR",
            )
            logger.debug("Registered OpenCNPJ company driver")
        except ImportError as e:
            logger.warning("Failed to register OpenCNPJ company driver: %s", e)

        # Register CNPJ.ws driver
        try:
            from drivers.company.company_cnpjws_driver import CompanyCnpjwsDriver

            self.register_driver(
                "cnpjws",
                CompanyCnpjwsDriver,
                description="CNPJ.ws Brazilian company data service with comprehensive information",
                version="1.0.0",
                country="BR",
            )
            logger.debug("Registered CNPJ.ws company driver")
        except ImportError as e:
            logger.warning("Failed to register CNPJ.ws company driver: %s", e)
    
    def get(self, cnpj: str, driver_name: Optional[str] = None) -> Company:
        """
        Get company data using specified or default driver.
        
        Args:
            cnpj: CNPJ number (formatted or unformatted)
            driver_name: Optional driver name. If None, uses first available driver
            
        Returns:
            Company: Company data object
            
        Raises:
            ValidationError: If CNPJ is invalid or lookup fails
            
        Example:
            manager = CompanyManager()
            company = manager.get("11.222.333/0001-81")
            print(f"Company: {company.get_display_name()}")
        """
        if driver_name is None:
            available_drivers = self.list_drivers()
            if not available_drivers:
                raise ValidationError("No company drivers available")
            driver_name = available_drivers[0]
        
        driver = self.load(driver_name)
        return driver.get(cnpj)
    
    def list_drivers(self) -> List[str]:
        """
        List all available company driver names.
        
        Returns:
            List of driver names
        """
        return list(self._drivers.keys())
    
    def get_driver_info(self, driver_name: str) -> Dict[str, str]:
        """
        Get information about a specific driver.
        
        Args:
            driver_name: Name of the driver
            
        Returns:
            Dictionary with driver information
        """
        if driver_name not in self._drivers:
            raise ValidationError(f"Driver '{driver_name}' not found")
        
        driver_info = self._drivers[driver_name]
        metadata = driver_info.get("metadata", {})
        return {
            "name": driver_name,
            "description": metadata.get("description", ""),
            "version": metadata.get("version", ""),
            "country": metadata.get("country", ""),
        }

    def load(self, driver_name: str, **config):
        """
        Load and configure a company driver.

        Args:
            driver_name: Name of the driver to load
            **config: Configuration options for the driver

        Returns:
            Configured driver instance

        Raises:
            ValidationError: If driver not found or cannot be loaded
        """
        if driver_name not in self._drivers:
            raise ValidationError(f"Driver '{driver_name}' not found")

        try:
            driver_class = self._drivers[driver_name]["class"]
            driver_instance = driver_class()

            # Apply configuration if provided
            if config:
                driver_instance.configure(**config)

            return driver_instance

        except Exception as e:
            raise ValidationError(f"Failed to load driver '{driver_name}': {e}")

    async def get_first_response(
        self,
        cnpj: str,
        drivers: Optional[List[str]] = None,
        timeout: float = 10.0
    ) -> Company:
        """
        Get company data from the first driver to respond successfully.

        Executes multiple drivers concurrently and returns the first successful
        response, automatically cancelling remaining requests for optimal performance.

        Args:
            cnpj: CNPJ number (formatted or unformatted)
            drivers: Optional list of driver names to use. If None, uses all available
            timeout: Maximum time to wait for response in seconds

        Returns:
            Company: Company data from the first successful driver

        Raises:
            ValidationError: If all drivers fail or timeout occurs

        Example:
            manager = CompanyManager()
            company = await manager.get_first_response("11.222.333/0001-81")
            print(f"Fastest driver: {company.verification_source}")
        """
        # Get list of drivers to use
        if drivers is None:
            drivers = self.list_drivers()

        if not drivers:
            raise ValidationError("No company drivers available")

        # Create async wrappers for all drivers
        async_drivers = []
        for driver_name in drivers:
            try:
                sync_driver = self.load(driver_name)
                async_wrapper = AsyncDriverWrapper(sync_driver, self._thread_pool)
                async_drivers.append((driver_name, async_wrapper))
            except Exception as e:
                logger.warning(f"Failed to load driver {driver_name}: {e}")
                continue

        if not async_drivers:
            raise ValidationError("No company drivers could be loaded")

        # Create tasks for all drivers
        tasks = []
        for driver_name, async_driver in async_drivers:
            task = asyncio.create_task(
                self._safe_driver_call(async_driver, cnpj),
                name=f"company-{driver_name}"
            )
            tasks.append(task)

        try:
            # Wait for first successful response
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
                        company, successful_driver = result
                        logger.info(
                            f"First response from {successful_driver} for CNPJ: {cnpj}"
                        )
                        return company
                except asyncio.CancelledError:
                    # Task was cancelled, skip it
                    logger.debug(f"Task {task.get_name()} was cancelled")
                    continue
                except Exception as e:
                    logger.debug(f"Task {task.get_name()} failed: {e}")
                    continue

            # If we have pending tasks, wait a bit more for them
            if pending:
                try:
                    additional_done, still_pending = await asyncio.wait(
                        pending, timeout=min(2.0, timeout * 0.2)
                    )

                    # Check additional completed tasks
                    for task in additional_done:
                        try:
                            result = await task
                            if result[0] is not None:
                                company, successful_driver = result
                                logger.info(
                                    f"Late response from {successful_driver} for CNPJ: {cnpj}"
                                )
                                return company
                        except asyncio.CancelledError:
                            # Task was cancelled, skip it
                            continue
                        except Exception:
                            continue

                    # Cancel any remaining tasks
                    for task in still_pending:
                        if not task.done():
                            task.cancel()

                except asyncio.TimeoutError:
                    pass

            # All drivers failed
            raise ValidationError(f"All drivers failed for CNPJ: {cnpj}")

        except asyncio.TimeoutError:
            # Cancel all tasks on timeout
            for task in tasks:
                if not task.done():
                    task.cancel()

            raise ValidationError(f"Timeout waiting for company data: {cnpj}")

    async def _safe_driver_call(self, async_driver: AsyncDriverWrapper, cnpj: str) -> Tuple[Optional[Company], str]:
        """
        Safely call a driver and return result with driver name.

        Args:
            async_driver: Async wrapper for the driver
            cnpj: CNPJ to lookup

        Returns:
            Tuple of (Company or None, driver_name)
        """
        try:
            company = await async_driver.get_async(cnpj)
            return company, async_driver.name
        except Exception as e:
            logger.debug(f"Driver {async_driver.name} failed for CNPJ {cnpj}: {e}")
            return None, async_driver.name

    def get_first_response_sync(
        self,
        cnpj: str,
        drivers: Optional[List[str]] = None,
        timeout: float = 10.0
    ) -> Company:
        """
        Synchronous wrapper for get_first_response.

        Executes multiple drivers concurrently and returns the first successful
        response. This is a convenience method for synchronous code.

        Args:
            cnpj: CNPJ number (formatted or unformatted)
            drivers: Optional list of driver names to use. If None, uses all available
            timeout: Maximum time to wait for response in seconds

        Returns:
            Company: Company data from the first successful driver

        Example:
            manager = CompanyManager()
            company = manager.get_first_response_sync("11.222.333/0001-81")
            print(f"Company: {company.get_display_name()}")
            print(f"Driver: {company.verification_source}")
        """
        try:
            # Create new event loop for this operation
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(
                    self.get_first_response(cnpj, drivers, timeout)
                )
            finally:
                loop.close()
        except Exception:
            # Fallback: try to use existing event loop
            try:
                return asyncio.run(self.get_first_response(cnpj, drivers, timeout))
            except RuntimeError:
                # If we're already in an event loop, create a task
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        asyncio.run,
                        self.get_first_response(cnpj, drivers, timeout)
                    )
                    return future.result(timeout=timeout + 5)
