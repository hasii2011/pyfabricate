
from typing import Callable
from typing import Dict
from typing import List
from typing import cast

from logging import Logger
from logging import getLogger

from string import Template

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

NO_TOKENS_SUBSTITUTION_TEMPLATES: List[Path] = [
    Path('LICENSE.template'),
    Path('.mypi.ini.template'),
    Path('requirements.txt.template'),
]

TOKEN_SUBSTITUTION_TEMPLATES: List[Path] = [
    Path('README.md.template'),
    Path('.gitignore.template'),
    Path('pyproject.toml.template'),
    Path('.envrc.template'),
]

# These values the the string names that we substitute
TOKEN_PROJECT_NAME:   str = 'PROJECT_NAME'
TOKEN_PYTHON_VERSION: str = 'PYTHON_VERSION'
TOKEN_OWNER_NAME:     str = 'OWNER_NAME'
TOKEN_OWNER_EMAIL:    str = 'OWNER_EMAIL'
TOKEN_DESCRIPTION:    str = 'DESCRIPTION'
TOKEN_KEYWORDS:       str = 'KEYWORDS'


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
    def __init__(self, projectDetails: ProjectDetails, progressCallback: ProgressCallback):
        """

        Args:
            projectDetails:         The details about the project we are creating
            progressCallback:       Somewhere to report our progress as we go along
        """

        self.logger: Logger = getLogger(__name__)

        self._projectDetails:   ProjectDetails   = projectDetails
        self._progressCallback: ProgressCallback = progressCallback

        self._projectPath:    Path                 = self._createProjectDirectory()
        configurationLocator: ConfigurationLocator = ConfigurationLocator()

        configPath:                      Path                = configurationLocator.applicationPath(applicationName=APPLICATION_NAME)
        self._configurationTemplatePath: Path                = configPath / TEMPLATES_DIRECTORY_NAME
        self._directories:               SkeletonDirectories = self._computeSkeletonDirectories(self._projectPath)

        self._copyTemplatesToConfiguration(configurationTemplatePath=self._configurationTemplatePath)

    def fabricate(self):

        self._createSkeletonDirectories()
        self._createPythonPackageFiles()
        self._createVersioningCapabilities()
        self._createLoggingConfigurationFiles()
        self._createCircleCIFile()
        self._createProjectRootNoSubstitutionFiles()
        self._createProjectRootSubstitutionFiles()

    def _createProjectDirectory(self) -> Path:

        projectPath: Path = self._projectDetails.baseDirectory / self._projectDetails.name

        projectPath.mkdir(parents=True, exist_ok=True)

        self._progressCallback(f'Created: {projectPath}')

        return projectPath

    def _computeSkeletonDirectories(self, projectPath: Path) -> SkeletonDirectories:

        self._progressCallback('Computing project skeleton')

        moduleNamePath: Path = Path(f'{self._projectDetails.name.lower()}')

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

    def _createSkeletonDirectories(self):

        skeletonDictionary: SkeletonDictionary = vars(self._directories)

        for varName, directoryPath in skeletonDictionary.items():

            if varName != 'projectPath':

                directoryPath.mkdir(parents=True, exist_ok=True)
                self._progressCallback(f'Created: {directoryPath}')

    def _createPythonPackageFiles(self):

        skeletonDictionary: SkeletonDictionary = vars(self._directories)

        for varName, directoryPath in skeletonDictionary.items():
            if varName == 'projectPath' or varName == 'srcPath' or varName == 'circleCIPath':
                pass
            else:
                fullPath: Path = self._directories.projectPath / directoryPath / PACKAGE_DEFINITION_FILENAME
                fullPath.touch()
                self._progressCallback(f'Created: {fullPath}')

    def _createVersioningCapabilities(self):
        """
        Moves the _version.py.template file in place
        Updates the module __init__.py file to make the module version number available
        """
        templateVersionFile: Path = self._configurationTemplatePath / VERSION_PY_TEMPLATE
        destinationPath:     Path = self._directories.srcModulePath / VERSION_PY_TEMPLATE.stem

        destinationPath.write_bytes(templateVersionFile.read_bytes())
        self._progressCallback(f'Created: {destinationPath}')

        updatedVersionVariable: str = VERSION_VARIABLE % self._projectDetails.name.lower()
        self._progressCallback(f'Updated version variable: `{updatedVersionVariable}`')

        moduleInitPath: Path = self._directories.srcModulePath / PACKAGE_DEFINITION_FILENAME

        moduleInitPath.write_text(updatedVersionVariable)
        self._progressCallback(f'Updated {moduleInitPath}')

    def _createLoggingConfigurationFiles(self):

        # Move the module template
        #
        templateLoggingConfigurationFile: Path = self._configurationTemplatePath / LOGGING_CONFIGURATION_TEMPLATE
        destinationPath:                  Path = self._directories.srcModuleResources / Path(LOGGING_CONFIGURATION_TEMPLATE).stem

        destinationPath.write_bytes(templateLoggingConfigurationFile.read_bytes())
        self._progressCallback(f'Created: {destinationPath}')

        subDict = {
            TOKEN_PROJECT_NAME: self._projectDetails.name.lower(),
        }
        # Make the substitutions
        #
        template: Template = Template(destinationPath.read_text())
        result:   str      = template.substitute(subDict)

        # Write the result back
        #
        destinationPath.write_text(result)

        # move the test module template
        templateTestLoggingConfigurationFile: Path = self._configurationTemplatePath / TEST_LOGGING_CONFIGURATION_TEMPLATE
        destinationTestPath:                  Path = self._directories.testsResourcesPath / Path(TEST_LOGGING_CONFIGURATION_TEMPLATE).stem

        destinationTestPath.write_bytes(templateTestLoggingConfigurationFile.read_bytes())
        self._progressCallback(f'Created: {destinationTestPath}')

    def _createCircleCIFile(self):

        templateCIFile:  Path = self._configurationTemplatePath / CIRCLE_CI_TEMPLATE
        destinationPath: Path = self._directories.circleCIPath / Path(CIRCLE_CI_TEMPLATE).stem

        destinationPath.write_bytes(templateCIFile.read_bytes())

        self._progressCallback(f'Created {destinationPath}')

    def _createProjectRootNoSubstitutionFiles(self):
        """
        These are files that we do no token substitution
        """

        for templateFile in NO_TOKENS_SUBSTITUTION_TEMPLATES:

            templatePath:    Path = self._configurationTemplatePath / templateFile
            destinationPath: Path = self._directories.projectPath / templateFile.stem

            destinationPath.write_bytes(templatePath.read_bytes())

            self._progressCallback(f'Created: {destinationPath}')

    def _createProjectRootSubstitutionFiles(self):
        """

        """
        tokenDict = {
            TOKEN_PYTHON_VERSION: self._projectDetails.pythonVersion,
            TOKEN_PROJECT_NAME:   self._projectDetails.name.lower(),
            TOKEN_OWNER_NAME:     self._projectDetails.ownerName,
            TOKEN_OWNER_EMAIL:    self._projectDetails.ownerEmail,
            TOKEN_DESCRIPTION:    self._projectDetails.description,
            TOKEN_KEYWORDS:       self._projectDetails.keywords,
        }
        for templateFile in TOKEN_SUBSTITUTION_TEMPLATES:
            templatePath:    Path = self._configurationTemplatePath / templateFile
            destinationPath: Path = self._directories.projectPath / templateFile.stem
            # Copy the template
            destinationPath.write_bytes(templatePath.read_bytes())
            #
            # Make the substitutions

            template: Template = Template(destinationPath.read_text())
            result:   str      = template.substitute(tokenDict)

            # Write the result back
            #
            destinationPath.write_text(result)
            self._progressCallback(f'Created {destinationPath}')

    def _copyTemplatesToConfiguration(self, configurationTemplatePath: Path):
        """
        Copy the templates to our configuration directory.  This allows end user/developer
        customization, of a sort.

        Only copied if the template directory does not exist

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
