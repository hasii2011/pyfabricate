
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ProjectDetails:
    name:        str = ''
    ownerEmail:  str = ''
    description: str = ''
    keywords:    str = ''

    baseDirectory: Path = Path('/')
