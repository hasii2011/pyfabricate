
from typing import cast
from typing import List
from typing import NewType

from logging import Logger
from logging import getLogger

from platform import platform as osPlatform

from semantic_version import Version as SemanticVersion

from pyfabricate.InstallationChecker import CompletedData
from pyfabricate.InstallationChecker import InstallationChecker

from pyfabricate.Platform import NON_MAC_OS_PYENV_CMD
from pyfabricate.Platform import THE_GREAT_MAC_PLATFORM

SemanticVersions = NewType('SemanticVersions', List[SemanticVersion])

PYENV_CMD:         str = 'pyenv'
MAC_OS_PYENV_PATH: str = f'/opt/homebrew/bin'
MAC_OS_PYENV_CMD:  str = f'{MAC_OS_PYENV_PATH}/{PYENV_CMD} versions'


CmdOutput = NewType('CmdOutput', List[str])

# noinspection SpellCheckingInspection

NON_PYTHON_VERSION:             str = 'system'
LOCAL_PYTHON_VERSION_INDICATOR: str = '*'


class UnableToRetrievePythonVersionsException(Exception):

    def __init__(self, stderr: CmdOutput):

        self._stderr: CmdOutput = stderr

    @property
    def stderr(self) -> CmdOutput:
        return self._stderr


class ExternalCommands:
    def __init__(self):
        self.logger: Logger = getLogger(__name__)

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
