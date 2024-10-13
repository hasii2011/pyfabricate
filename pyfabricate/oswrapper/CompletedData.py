
from typing import List
from typing import NewType
from typing import cast

from dataclasses import dataclass
from dataclasses import field

OutputLines = NewType('OutputLines', List[str])
StdOut      = OutputLines
StdErr      = OutputLines

NO_OUT = cast(StdOut, None)
NO_ERR = cast(StdErr, None)


def stdoutFactory() -> StdOut:
    return StdOut([])


def stderrFactory() -> StdErr:
    return StdErr([])


@dataclass
class CompletedData:
    status: int = 0
    stdout: StdOut = field(default_factory=stdoutFactory)
    stderr: StdErr = field(default_factory=stderrFactory)
