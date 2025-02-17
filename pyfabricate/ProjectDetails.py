
from dataclasses import dataclass

from pathlib import Path

from semantic_version import Version as SemanticVersion


@dataclass
class ProjectDetails:
    name:        str = ''
    moduleName:  str = ''
    ownerName:   str = ''
    ownerEmail:  str = ''
    description: str = ''
    keywords:    str = ''

    baseDirectory: Path = Path('/')

    pythonVersion: SemanticVersion = SemanticVersion('0.0.0')
