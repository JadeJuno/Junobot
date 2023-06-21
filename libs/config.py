from typing import Any, MutableMapping
import tomllib


def parse_config(path: str) -> MutableMapping[str, Any]:
	with open(path, 'rb') as f:
		return tomllib.load(f)
