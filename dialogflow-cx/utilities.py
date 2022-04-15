from dataclasses import dataclass, field
from typing import Mapping


@dataclass
class RequestMock:
    payload: Mapping[str, Mapping[str, str]] = field(default_factory=dict)

    def get_json(self) -> Mapping:
        return self.payload
