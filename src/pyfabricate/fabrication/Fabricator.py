
from logging import Logger
from logging import getLogger

from importlib.abc import Traversable

from importlib.resources import files

from os import pathsep as osPathSep

from pathlib import Path
from typing import Callable
from typing import List

from codeallybasic.ConfigurationLocator import ConfigurationLocator
from codeallybasic.ResourceManager import ResourceManager

from pyfabricate.Constants import APPLICATION_NAME
from pyfabricate.Constants import TEMPLATES_DIRECTORY_NAME

from pyfabricate.ProjectDetails import ProjectDetails


TEMPLATE_RESOURCE_PATH: str = f'pyfabricate{osPathSep}resources{osPathSep}templates'
TEMPLATE_PACKAGE_NAME:  str = 'pyfabricate.resources.templates'


ProgressCallback = Callable[[str], None]

SRC_PATH:       Path = Path('src')
TESTS_PATH:     Path = Path('tests')
RESOURCES_PATH: Path = Path('resources')

DIRECTORY_PATHS: List[Path] = [
    Path('.circleci'),
    SRC_PATH,
    TESTS_PATH,
    TESTS_PATH / RESOURCES_PATH,
]


class Fabricator:
    def __init__(self, projectDetails: ProjectDetails):

        self.logger: Logger = getLogger(__name__)

        self._projectDetails: ProjectDetails = projectDetails

        self._copyTemplatesToConfiguration()

    def fabricate(self, progressCallback: ProgressCallback):

        projectPath: Path = self._createProjectDirectory()
        progressCallback(f'Created: {projectPath}')
        self._createProjectSkeletonDirectories(projectPath, progressCallback)

    def _createProjectDirectory(self) -> Path:

        projectPath: Path = self._projectDetails.baseDirectory / self._projectDetails.name

        projectPath.mkdir(parents=True, exist_ok=True)

        return projectPath

    def _createProjectSkeletonDirectories(self, projectPath: Path, progressCallback: ProgressCallback):

        progressCallback('Creating project skeleton')

        for directoryPath in DIRECTORY_PATHS:
            fullPath: Path = projectPath / directoryPath
            fullPath.mkdir(parents=True, exist_ok=True)
            progressCallback(f'Created: {fullPath}')

        moduleNamePath:      Path = Path(f'{self._projectDetails.name}')
        srcModuleDir:         Path = projectPath / SRC_PATH / moduleNamePath
        testsModuleDir:       Path = projectPath / TESTS_PATH / moduleNamePath
        srcModuleResouresDir: Path = srcModuleDir / RESOURCES_PATH

        srcModuleDir.mkdir(parents=True, exist_ok=True)
        testsModuleDir.mkdir(parents=True, exist_ok=True)
        srcModuleResouresDir.mkdir(parents=True, exist_ok=True)

        progressCallback(f'Created: {srcModuleDir}')
        progressCallback(f'Created: {testsModuleDir}')
        progressCallback(f'Created: {srcModuleResouresDir}')

    def _copyTemplatesToConfiguration(self):
        """
        Copy the templates to our configuration directory.  This allows end user/developer
        customization, of a sort.

        Only copied if they are not there already

        """
        configurationLocator: ConfigurationLocator = ConfigurationLocator()

        configPath:                Path = configurationLocator.applicationPath(applicationName=APPLICATION_NAME)
        configurationTemplatePath: Path = configPath / TEMPLATES_DIRECTORY_NAME

        self.logger.info(f'{configurationTemplatePath}')

        if configurationTemplatePath.exists() is False:

            configurationTemplatePath.mkdir(parents=True, exist_ok=True)

            resourcePath: Path = self._computeResourcePath(resourcePath=TEMPLATE_RESOURCE_PATH, packageName=TEMPLATE_PACKAGE_NAME)

            for fqFileName in resourcePath.rglob('*.template'):

                destinationPath: Path = configurationTemplatePath / fqFileName.name

                destinationPath.write_bytes(fqFileName.read_bytes())

    def _computeResourcePath(self, resourcePath: str, packageName: str) -> Path:
        """
        TODO:  This belongs in codeallybasic as part of the ResourceManager

        Assume we are in an app;  If not, then we are in development
        Args:
            resourcePath:  OS Path that matches the package name
            packageName:   The package from which to retrieve the resource

        Returns:  The fully qualified path
        """
        try:
            from os import environ
            pathToResources: str = environ[f'{ResourceManager.RESOURCE_ENV_VAR}']
            fqFileName:      Path = Path(f'{pathToResources}/{resourcePath}/')
        except KeyError:
            traversable: Traversable = files(packageName)
            fqFileName = Path(str(traversable))

        return fqFileName
