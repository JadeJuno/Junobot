from typing import Any, MutableMapping

import toml


def parse_config(path: str) -> MutableMapping[str, Any]:
	with open(path) as f:
		return toml.load(f)
