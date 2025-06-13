from abc import ABC, abstractmethod
from typing import Literal


class Item(ABC):
    @property
    @abstractmethod
    def bookmarked(self) -> bool:
        raise NotImplementedError

    @bookmarked.setter
    @abstractmethod
    def bookmarked(self, value: bool) -> None:
        raise NotImplementedError

    @property
    @abstractmethod
    def cached(self) -> bool:
        raise NotImplementedError

    @property
    @abstractmethod
    def kind(self) -> Literal["resources", "providers"]:
        raise NotImplementedError

    @property
    @abstractmethod
    def display_name(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def identifying_name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def clear_from_cache(self) -> None:
        raise NotImplementedError
