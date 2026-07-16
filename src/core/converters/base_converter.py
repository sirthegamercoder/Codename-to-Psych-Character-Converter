from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseConverter(ABC):
    @abstractmethod
    def convert(self, content: str) -> Optional[Dict[str, Any]]:
        pass
