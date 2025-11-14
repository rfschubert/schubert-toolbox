"""
Async wrapper for synchronous postal code drivers.

Enables first-to-respond pattern without changing existing driver implementations.
This wrapper allows existing synchronous drivers to work in async contexts.
"""

import asyncio
import logging
from typing import Optional
from concurrent.futures import ThreadPoolExecutor

from standards.address import Address

logger = logging.getLogger(__name__)


class AsyncDriverWrapper:
    """
    Wrapper to make synchronous drivers async-compatible.
    
    This allows existing drivers to work in async contexts without modification.
    The wrapper runs synchronous driver methods in a thread pool to avoid
    blocking the async event loop.
    """
    
    def __init__(self, sync_driver, executor: Optional[ThreadPoolExecutor] = None):
        """
        Initialize async wrapper.
        
        Args:
            sync_driver: Synchronous driver instance
            executor: Optional thread pool executor for running sync operations
        """
        self.sync_driver = sync_driver
        self.name = sync_driver.name
        self.executor = executor
        
    async def get_async(self, postal_code: str) -> Address:
        """
        Async version of driver's get method.
        
        Runs the synchronous get method in a thread pool to avoid blocking
        the event loop while maintaining compatibility with existing drivers.
        
        Args:
            postal_code: CEP to lookup
            
        Returns:
            Address object from the driver
            
        Raises:
            ValidationError: If lookup fails (propagated from sync driver)
        """
        loop = asyncio.get_event_loop()
        
        try:
            # Run sync method in thread pool to avoid blocking event loop
            address = await loop.run_in_executor(
                self.executor,
                self.sync_driver.get,
                postal_code
            )
            
            logger.debug(f"Driver {self.name} succeeded for CEP: {postal_code}")
            return address
            
        except Exception as e:
            logger.debug(f"Driver {self.name} failed for CEP {postal_code}: {e}")
            raise  # Re-raise the original exception
    
    def __str__(self) -> str:
        """String representation of the wrapper."""
        return f"AsyncDriverWrapper({self.name})"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"AsyncDriverWrapper(sync_driver={self.sync_driver}, name='{self.name}')"
