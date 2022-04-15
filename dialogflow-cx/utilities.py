from typing import Mapping
from dataclasses import dataclass, field


@dataclass
class RequestMock:
    payload: Mapping[str, Mapping[str, str]] = field(default_factory=dict)

    def get_json(self) -> Mapping:
        return self.payload
