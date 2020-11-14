import toml
import typing


def parse_config(path: str) -> typing.Dict:
    with open(path) as f:
        data = f.read()

    return toml.loads(data)
