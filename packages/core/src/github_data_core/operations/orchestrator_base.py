from abc import abstractmethod, ABC
from typing import List, Dict, Any


class StrategyBasedOrchestrator(ABC):
    @abstractmethod
    def execute(self, repo_name: str, path: str) -> List[Dict[str, Any]]:
        raise Exception("Unimplemented")
