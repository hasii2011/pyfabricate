
from typing import cast
from typing import List
from typing import NewType

from logging import Logger
from logging import getLogger

from platform import platform as osPlatform

from semantic_version import Version as SemanticVersion

from pyfabricate.oswrapper.InstallationChecker import CompletedData
from pyfabricate.oswrapper.InstallationChecker import InstallationChecker

from pyfabricate.Platform import NON_MAC_OS_PYENV_CMD
from pyfabricate.Platform import THE_GREAT_MAC_PLATFORM

SemanticVersions = NewType('SemanticVersions', List[SemanticVersion])

VIRTUAL_ENVIRONMENT_MARKER: str = 'pyenv-'

PYENV_CMD:         str = 'pyenv'
MAC_OS_PYENV_PATH: str = f'/opt/homebrew/bin'
MAC_OS_PYENV_CMD:  str = f'{MAC_OS_PYENV_PATH}/{PYENV_CMD} versions'

MAC_OS_PYENV_LOCAL_CMD:   str = 'pyenv local '

MAC_OS_CREATE_VIRTUAL_ENV_CMD: str = '/opt/homebrew/bin/python3 -m venv'

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
    def __init__(self):
        self.logger: Logger = getLogger(__name__)

    @classmethod
    def createVirtualEnvironment(cls, version: SemanticVersion) -> str:
        """
        Assumes the caller has appropriately set the current directory

        Args:
            version: The Python version

        Returns:  The name of the subdirectory where the we created the virtual environment

        """
        platform: str = osPlatform(terse=True)

        if platform.startswith(THE_GREAT_MAC_PLATFORM) is True:

            subdirName:    str           = f'{VIRTUAL_ENVIRONMENT_MARKER}{str(version)}'
            cmd:           str           = f'{MAC_OS_CREATE_VIRTUAL_ENV_CMD} {subdirName}'
            completedData: CompletedData = InstallationChecker.runCommandReturnOutput(cmd)
            if completedData.status == 0:
                pass
            else:
                raise UnableToCreateVirtualEnvironment(stderr=CmdOutput(completedData.stderr))
        else:
            assert False, 'Oops, I only work on Mac OS'

        return subdirName

    @classmethod
    def createApplicationSpecificPythonVersion(cls, version: SemanticVersion):
        """
        Assumes the caller has appropriately set the current directory

        Args:
            version: The Python version

        """

        platform: str = osPlatform(terse=True)

        if platform.startswith(THE_GREAT_MAC_PLATFORM) is True:
            cmd: str = f'{MAC_OS_PYENV_LOCAL_CMD} {str(version)}'
            completedData: CompletedData = InstallationChecker.runCommandReturnOutput(cmd)
            if completedData.status == 0:
                pass
            else:
                raise UnableToSetLocalPythonVersion
        else:
            assert False, 'Oops, I only work on Mac OS'

    @classmethod
    def getPythonVersions(cls) -> SemanticVersions:

        pythonVersions: SemanticVersions = SemanticVersions([])

        platform: str = osPlatform(terse=True)

        if platform.startswith(THE_GREAT_MAC_PLATFORM) is True:
            completedData: CompletedData = InstallationChecker.runCommandReturnOutput(MAC_OS_PYENV_CMD)
        else:
            completedData = InstallationChecker.runCommandReturnOutput(NON_MAC_OS_PYENV_CMD)

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
