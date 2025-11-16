from abc import ABC, abstractmethod

class AbstractWorker(ABC):
    @abstractmethod
    def getPossibleActions(self) -> list[str]:
        """Return a list of actions this worker performs."""
        pass

    @abstractmethod
    def describeBehavior(self) -> str:
        """Return a description of how to call worker."""
        pass

    @abstractmethod
    def executeAction(self, **kwargs) -> any:
        """Execute the actions."""
        pass