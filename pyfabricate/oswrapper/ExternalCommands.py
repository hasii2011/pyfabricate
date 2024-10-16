
from typing import cast
from typing import List
from typing import NewType

from logging import Logger
from logging import getLogger

from os import linesep as osLineSep
from os import sep as osSep

from pathlib import Path

from subprocess import CompletedProcess

from subprocess import run as subProcessRun

from platform import platform as osPlatform

from semantic_version import Version as SemanticVersion

from pyfabricate.oswrapper.CompletedData import CompletedData
from pyfabricate.oswrapper.CompletedData import OutputLines
from pyfabricate.oswrapper.CompletedData import StdErr
from pyfabricate.oswrapper.CompletedData import StdOut

from pyfabricate.Platform import NON_MAC_OS_PYENV_CMD
from pyfabricate.Platform import THE_GREAT_MAC_PLATFORM

SemanticVersions = NewType('SemanticVersions', List[SemanticVersion])

VIRTUAL_ENVIRONMENT_MARKER: str = 'pyenv-'

PYENV_CMD:         str = 'pyenv'
MAC_OS_PYENV_PATH: str = f'/opt/homebrew/bin'
MAC_OS_PYENV_CMD:  str = f'{MAC_OS_PYENV_PATH}/{PYENV_CMD} versions'

MAC_OS_PYENV_LOCAL_CMD:   str = f'{PYENV_CMD} local '


MAC_OS_PYTHON_SHIM: str = '.pyenv/shims/python -m venv '

NON_PYTHON_VERSION:             str = 'system'
LOCAL_PYTHON_VERSION_INDICATOR: str = '*'

CmdOutput = NewType('CmdOutput', List[str])


class UnableToRetrievePythonVersionsException(Exception):

    def __init__(self, stderr: CmdOutput):

        self._stderr: CmdOutput = stderr

    @property
    def stderr(self) -> CmdOutput:
        return self._stderr


class UnableToSetLocalPythonVersion(Exception):
    pass


class UnableToCreateVirtualEnvironment(Exception):
    def __init__(self, stderr: CmdOutput):

        self._stderr: CmdOutput = stderr

    @property
    def stderr(self) -> CmdOutput:
        return self._stderr


class ExternalCommands:
    clsLogger: Logger = getLogger(__name__)

    def __init__(self):
        pass

    @classmethod
    def createVirtualEnvironment(cls, version: SemanticVersion, projectDirectory: Path) -> str:
        """
        Special call for creating the virtual environment;  Will let the subProcessRun change to the project
        directory

        Since we are using pyenv to manage Python, this method assumes that .createApplicationSpecificPythonVersion()
        has been called so that pyenv creates the .python_version file

        Additionally, it assumes a standard homebrew pyenv install where pyenv stores it configuration in
        $HOME/.pyenv

        TODO:  This code does not execute correctly when executed from a standard Mac OS X application.

        See issue: https://github.com/hasii2011/pyfabricate/issues/5 for details.

        However, it does work when it is run from inside PyCharm

        Args:
            version:           The Python version
            projectDirectory:  Where to create the virtual environment


        Returns:  The name of the subdirectory where the we created the virtual environment

        """
        platform: str = osPlatform(terse=True)

        if platform.startswith(THE_GREAT_MAC_PLATFORM) is True:

            subdirName: str  = f'{VIRTUAL_ENVIRONMENT_MARKER}{str(version)}'
            homeDir:    Path = Path.home()
            cmd:        str  = f'{homeDir}{osSep}{MAC_OS_PYTHON_SHIM} {subdirName}'
            ExternalCommands.clsLogger.info(f'{cmd=}')

            completedProcess: CompletedProcess = subProcessRun([cmd],
                                                               shell=True,
                                                               cwd=projectDirectory,
                                                               capture_output=True,
                                                               text=True,
                                                               check=False,
                                                               timeout=9)
            ExternalCommands.clsLogger.info(f'{completedProcess.returncode=}')
            if completedProcess.returncode == 0:
                pass
            else:
                raise UnableToCreateVirtualEnvironment(stderr=CmdOutput(completedProcess.stderr))
        else:
            assert False, 'Oops, I only work on Mac OS'

        return subdirName

    @classmethod
    def getPythonVersions(cls) -> SemanticVersions:

        pythonVersions: SemanticVersions = SemanticVersions([])

        platform: str = osPlatform(terse=True)

        if platform.startswith(THE_GREAT_MAC_PLATFORM) is True:
            completedData: CompletedData = ExternalCommands.runCommandReturnOutput(MAC_OS_PYENV_CMD)
        else:
            completedData = ExternalCommands.runCommandReturnOutput(NON_MAC_OS_PYENV_CMD)

        if completedData.status == 0:
            for outputLine in completedData.stdout:
                trimmedLine: str = outputLine.strip()

                if trimmedLine != NON_PYTHON_VERSION and not trimmedLine.startswith(LOCAL_PYTHON_VERSION_INDICATOR):
                    version: SemanticVersion = SemanticVersion(trimmedLine)
                    # print(f'{version=}')
                    pythonVersions.append(version)
        else:
            raise UnableToRetrievePythonVersionsException(stderr=cast(CmdOutput, completedData.stderr))

        return pythonVersions

    @classmethod
    def checkInstallation(cls, commandToCheck) -> bool:
        ans:    bool = False
        status: int  = ExternalCommands.runCommand(commandToCheck)
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
            stdout: StdOut = ExternalCommands.toStdOut(completedProcess.stdout)
            return CompletedData(status=0, stdout=stdout)

        else:
            stderr: StdErr = ExternalCommands.toStdErr(completedProcess.stderr)
            return CompletedData(status=completedProcess.returncode, stderr=stderr)

    @classmethod
    def toStdOut(cls, cmdOutput: str) -> StdOut:
        """
        Syntactic sugar

        Args:
            cmdOutput:

        Returns: Perfectly typed list

        """
        return ExternalCommands.toList(cmdOutput)

    @classmethod
    def toStdErr(cls, cmdOutput: str) -> StdErr:
        """
        Syntactic sugar

        Args:
            cmdOutput:

        Returns: Perfectly typed list

        """
        return ExternalCommands.toList(cmdOutput)

    @classmethod
    def toList(cls, cmdOutput: str) -> OutputLines:
        """
        Does not return empty string entries

        Args:
            cmdOutput: The newline separated string that `subProcessRun` returns

        Returns:  A list of strings

        """
        strList:     List[str] = cmdOutput.split(f'{osLineSep}')
        outputLines: OutputLines = OutputLines([])

        for stuff in strList:
            if len(stuff) > 0:
                outputLines.append(stuff)

        return outputLines
