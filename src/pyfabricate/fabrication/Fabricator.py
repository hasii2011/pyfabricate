
from logging import Logger
from logging import getLogger

from importlib.abc import Traversable

from importlib.resources import files

from os import pathsep as osPathSep

from pathlib import Path

from codeallybasic.ConfigurationLocator import ConfigurationLocator
from codeallybasic.ResourceManager import ResourceManager

from pyfabricate.Constants import APPLICATION_NAME
from pyfabricate.Constants import TEMPLATES_DIRECTORY_NAME

from pyfabricate.ProjectDetails import ProjectDetails


TEMPLATE_RESOURCE_PATH: str = f'pyfabricate{osPathSep}resources{osPathSep}templates'
TEMPLATE_PACKAGE_NAME:  str = 'pyfabricate.resources.templates'


class Fabricator:
    def __init__(self, projectDetails: ProjectDetails):

        self.logger: Logger = getLogger(__name__)

        self._projectDetails: ProjectDetails = projectDetails

        self._copyTemplatesToConfiguration()

    def createProjectDirectory(self):

        projectPath: Path = self._projectDetails.baseDirectory / self._projectDetails.name

        projectPath.mkdir(parents=True, exist_ok=True)

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

                destinationPath: Path = configurationTemplatePath / fqFileName.stem

                destinationPath.write_bytes(fqFileName.read_bytes())

    def _computeResourcePath(self, resourcePath: str, packageName: str) -> Path:
        """
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
