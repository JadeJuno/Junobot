import tomllib
from typing import Any, MutableMapping


def parse_config(path: str) -> MutableMapping[str, Any]:
	with open(path, 'rb') as f:
		return tomllib.load(f)
