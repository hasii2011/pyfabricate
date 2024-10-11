from string import Template
from typing import Callable
from typing import Dict
from typing import cast

from logging import Logger
from logging import getLogger

from dataclasses import dataclass

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


ProgressCallback   = Callable[[str], None]
SkeletonDictionary = Dict[str, Path]

NO_PATH:        Path = cast(Path, None)

CIRCLECI_PATH:  Path = Path('.circleci')
SRC_PATH:       Path = Path('src')
TESTS_PATH:     Path = Path('tests')
RESOURCES_PATH: Path = Path('resources')

PACKAGE_DEFINITION_FILENAME: str  = '__init__.py'
VERSION_PY_TEMPLATE:         Path = Path('_version.py.template')
VERSION_VARIABLE:             str  = 'from %s._version import __version__'

LOGGING_CONFIGURATION_TEMPLATE:      str = 'loggingConfiguration.json.template'
TEST_LOGGING_CONFIGURATION_TEMPLATE: str = 'testLoggingConfiguration.json.template'
CIRCLE_CI_TEMPLATE:                  str = 'config.yml.template'

# These values the the string names that we substitute
TOKEN_PROJECT_NAME: str = 'PROJECT_NAME'


@dataclass
class SkeletonDirectories:
    """
    Hold the directory path names for the skeleton of a project
    These are fully qualified  paths
    The individual variables describe examples of the values
    """
    projectPath:        Path = NO_PATH              # $HOME/tmp/DemoProject
    circleCIPath:       Path = NO_PATH              # projectPath/.circleci
    srcPath:            Path = NO_PATH              # projectPath/src
    srcModulePath:      Path = NO_PATH              # projectPath/src/demoproject
    srcModuleResources: Path = NO_PATH              # projectPath/src/demoproject/resources
    testsPath:          Path = NO_PATH              # projectPath/tests
    testsModulePath:    Path = NO_PATH              # projectPath/tests/demoproject
    testsResourcesPath: Path = NO_PATH              # projectPath/tests/resources


class Fabricator:
    def __init__(self, projectDetails: ProjectDetails):

        self.logger: Logger = getLogger(__name__)

        self._projectDetails: ProjectDetails = projectDetails
        self._projectPath:    Path           = cast(Path, None)

        configurationLocator: ConfigurationLocator = ConfigurationLocator()

        configPath:                      Path = configurationLocator.applicationPath(applicationName=APPLICATION_NAME)
        self._configurationTemplatePath: Path = configPath / TEMPLATES_DIRECTORY_NAME

        self._copyTemplatesToConfiguration(configurationTemplatePath=self._configurationTemplatePath)

    def fabricate(self, progressCallback: ProgressCallback):

        self._projectPath = self._createProjectDirectory()
        progressCallback(f'Created: {self._projectPath}')

        directories: SkeletonDirectories = self._computeSkeletonDirectories(self._projectPath, progressCallback)

        self._createSkeletonDirectories(directories=directories, progressCallback=progressCallback)
        self._createPythonPackageFiles(directories=directories, progressCallback=progressCallback)
        self._createVersioningCapabilities(directories=directories, progressCallback=progressCallback)
        self._createLoggingConfigurationFiles(directories=directories, progressCallback=progressCallback)
        self._createCircleCIFile(directories=directories, progressCallback=progressCallback)

    def _createProjectDirectory(self) -> Path:

        projectPath: Path = self._projectDetails.baseDirectory / self._projectDetails.name

        projectPath.mkdir(parents=True, exist_ok=True)

        return projectPath

    def _computeSkeletonDirectories(self, projectPath: Path, progressCallback: ProgressCallback) -> SkeletonDirectories:

        progressCallback('Computing project skeleton')

        moduleNamePath:        Path = Path(f'{self._projectDetails.name.lower()}')

        directories: SkeletonDirectories = SkeletonDirectories()

        directories.projectPath         = projectPath
        directories.circleCIPath        = directories.projectPath / CIRCLECI_PATH
        directories.srcPath             = directories.projectPath / SRC_PATH
        directories.testsPath           = directories.projectPath / TESTS_PATH
        directories.srcModulePath       = directories.projectPath / SRC_PATH / moduleNamePath
        directories.srcModuleResources  = directories.projectPath / SRC_PATH / moduleNamePath / RESOURCES_PATH
        directories.testsPath           = directories.projectPath / TESTS_PATH
        directories.testsModulePath     = directories.projectPath / TESTS_PATH / moduleNamePath
        directories.testsResourcesPath  = directories.projectPath / TESTS_PATH / RESOURCES_PATH

        return directories

    def _createSkeletonDirectories(self, directories: SkeletonDirectories, progressCallback: ProgressCallback):

        skeletonDictionary: SkeletonDictionary = vars(directories)

        for varName, directoryPath in skeletonDictionary.items():

            if varName != 'projectPath':

                directoryPath.mkdir(parents=True, exist_ok=True)
                progressCallback(f'Created: {directoryPath}')

    def _createPythonPackageFiles(self, directories: SkeletonDirectories, progressCallback: ProgressCallback):

        skeletonDictionary: SkeletonDictionary = vars(directories)

        for varName, directoryPath in skeletonDictionary.items():
            if varName == 'projectPath' or varName == 'srcPath' or varName == 'circleCIPath':
                pass
            else:
                fullPath: Path = directories.projectPath / directoryPath / PACKAGE_DEFINITION_FILENAME
                fullPath.touch()
                progressCallback(f'Created: {fullPath}')

    def _createVersioningCapabilities(self, directories: SkeletonDirectories, progressCallback: ProgressCallback):
        """
        Moves the _version.py.template file in place
        Updates module __init__.py file to make the module version number available

        Args:
            directories:
            progressCallback:
        """
        templateVersionFile: Path = self._configurationTemplatePath / VERSION_PY_TEMPLATE
        destinationPath:     Path = directories.srcModulePath / VERSION_PY_TEMPLATE.stem

        destinationPath.write_bytes(templateVersionFile.read_bytes())
        progressCallback(f'Created: {destinationPath}')

        updatedVersionVariable: str = VERSION_VARIABLE % self._projectDetails.name.lower()
        progressCallback(f'Updated version variable: `{updatedVersionVariable}`')

        moduleInitPath: Path = directories.srcModulePath / PACKAGE_DEFINITION_FILENAME

        moduleInitPath.write_text(updatedVersionVariable)
        progressCallback(f'Updated {moduleInitPath}')

    def _createLoggingConfigurationFiles(self, directories: SkeletonDirectories, progressCallback: ProgressCallback):

        # Move the module template
        #
        templateLoggingConfigurationFile: Path = self._configurationTemplatePath / LOGGING_CONFIGURATION_TEMPLATE
        destinationPath:                  Path = directories.srcModuleResources / Path(LOGGING_CONFIGURATION_TEMPLATE).stem

        destinationPath.write_bytes(templateLoggingConfigurationFile.read_bytes())
        progressCallback(f'Created: {destinationPath}')

        subDict = {
            'PROJECT_NAME': self._projectDetails.name.lower(),
        }
        # Make the substitutions
        #
        src:    Template = Template(destinationPath.read_text())
        result: str      = src.substitute(subDict)

        # Write the result back
        #
        destinationPath.write_text(result)

        # move the test module template
        templateTestLoggingConfigurationFile: Path = self._configurationTemplatePath / TEST_LOGGING_CONFIGURATION_TEMPLATE
        destinationTestPath:                  Path = directories.testsResourcesPath / Path(TEST_LOGGING_CONFIGURATION_TEMPLATE).stem

        destinationTestPath.write_bytes(templateTestLoggingConfigurationFile.read_bytes())
        progressCallback(f'Created: {destinationTestPath}')

    def _createCircleCIFile(self, directories: SkeletonDirectories, progressCallback: ProgressCallback):

        templateCIFile:  Path = self._configurationTemplatePath / CIRCLE_CI_TEMPLATE
        destinationPath: Path = directories.circleCIPath / Path(CIRCLE_CI_TEMPLATE).stem

        destinationPath.write_bytes(templateCIFile.read_bytes())

        progressCallback(f'Created {destinationPath}')

    def _copyTemplatesToConfiguration(self, configurationTemplatePath: Path):
        """
        Copy the templates to our configuration directory.  This allows end user/developer
        customization, of a sort.

        Only copied if they are not there already

        """
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
