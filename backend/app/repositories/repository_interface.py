"""
Repository Interface

Defines the contract for repository implementations.

Author: Aman Maurya
Project: 3R Analyzer Intelligence
"""

from abc import ABC
from abc import abstractmethod


class RepositoryInterface(ABC):
    """
    Base repository contract.
    """

    @abstractmethod
    def save(self, data) -> None:
        """
        Persist data.
        """
        pass