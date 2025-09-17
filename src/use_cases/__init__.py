from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")
R = TypeVar("R")


class UseCase(ABC, Generic[T, R]):
    @abstractmethod
    def execute(self, request: T) -> R:
        pass
