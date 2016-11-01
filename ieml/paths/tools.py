from ieml.paths.parser.parser import PathParser
from ieml.paths.paths import Path


def path(p):
    if isinstance(p, Path):
        return p
    if isinstance(p, str):
        return PathParser().parse(p)

    raise ValueError("Invalid argument to create a path.")