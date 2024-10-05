
from typing import cast
from typing import List
from typing import NewType

from logging import Logger
from logging import getLogger

from os import linesep as osLineSep

from dataclasses import dataclass
from dataclasses import field

from subprocess import CompletedProcess
from subprocess import run as subProcessRun

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


class InstallationChecker:
    """
    Runs a version of a command line interface (CLI) to ensure
    that it executes.  If the command returns a zero status, we assume
    it is correctly installed.

    Examples are:

        pyenv --version
        jq    --version
        curl  --version

    Most of the methods here are `class methods`, so you do not have to actually
    instantiate a version of this class

    TODO:  Move this to the codeallybasic module.  Remove the duplicated code in the
    latestversions Python script CLI
    """
    def __init__(self):
        self.logger: Logger = getLogger(__name__)

    @classmethod
    def checkInstallation(cls, commandToCheck) -> bool:
        ans:    bool = False
        status: int  = InstallationChecker.runCommand(commandToCheck)
        if status == 0:
            ans = True
        return ans

    @classmethod
    def runCommand(cls, programToRun: str) -> int:
        """

        Args:
            programToRun:  What must be executed

        Returns:  The status return of the executed program
        """
        completedProcess: CompletedProcess = subProcessRun([programToRun], shell=True, capture_output=True, text=True, check=False)
        return completedProcess.returncode

    @classmethod
    def runCommandReturnOutput(cls, programToRun: str) -> CompletedData:

        completedProcess: CompletedProcess = subProcessRun([programToRun], shell=True, capture_output=True, text=True, check=False)
        if completedProcess.returncode == 0:
            stdout: StdOut = InstallationChecker.toStdOut(completedProcess.stdout)
            return CompletedData(status=0, stdout=stdout)

        else:
            stderr: StdErr = InstallationChecker.toStdErr(completedProcess.stderr)
            return CompletedData(status=completedProcess.returncode, stderr=stderr)

    @classmethod
    def toStdOut(cls, cmdOutput: str) -> StdOut:
        """
        Syntactic sugar

        Args:
            cmdOutput:

        Returns: Perfectly typed list

        """
        return InstallationChecker.toList(cmdOutput)

    @classmethod
    def toStdErr(cls, cmdOutput: str) -> StdErr:
        """
        Syntactic sugar

        Args:
            cmdOutput:

        Returns: Perfectly typed list

        """
        return InstallationChecker.toList(cmdOutput)

    @classmethod
    def toList(cls, cmdOutput: str) -> OutputLines:
        """
        Does not return empty string entries

        Args:
            cmdOutput: The newline separated string that `subProcessRun` returns

        Returns:  A list of strings

        """
        strList: List[str] = cmdOutput.split(f'{osLineSep}')
        outputLines: OutputLines = OutputLines([])

        for stuff in strList:
            if len(stuff) > 0:
                outputLines.append(stuff)

        return outputLines
