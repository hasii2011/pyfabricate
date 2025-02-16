
from typing import Callable
from typing import Dict
from typing import List
from typing import cast

from logging import Logger
from logging import getLogger

from datetime import datetime

from string import Template

from dataclasses import dataclass

from os import pathsep as osPathSep

from pathlib import Path

from wx import CENTER
from wx import ICON_ERROR
from wx import OK

from wx import MessageDialog

from codeallybasic.ConfigurationLocator import ConfigurationLocator
from codeallybasic.ResourceManager import ResourceManager

from pyfabricate.Constants import APPLICATION_NAME
from pyfabricate.Constants import TEMPLATES_DIRECTORY_NAME
from pyfabricate.fabrication.FabricationError import FabricationError
from pyfabricate.oswrapper.ExternalCommands import ExternalCommands
from pyfabricate.oswrapper.ExternalCommands import UnableToCreateVirtualEnvironment

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
PYTHON_VERSION_FILENAME:     str  = '.python-version'

VERSION_PY_TEMPLATE:         Path = Path('_version.py.template')
VERSION_VARIABLE:             str  = 'from %s._version import __version__'

LOGGING_CONFIGURATION_TEMPLATE:      str = 'loggingConfiguration.json.template'
TEST_LOGGING_CONFIGURATION_TEMPLATE: str = 'testLoggingConfiguration.json.template'
CIRCLE_CI_TEMPLATE:                  str = 'config.yml.template'
VENV_CREATION_SCRIPT_TEMPLATE:       str = 'createVirtualEnv.sh.template'

NO_TOKENS_SUBSTITUTION_TEMPLATES: List[Path] = [
    Path('LICENSE.template'),
    Path('requirements.txt.template'),
]

TOKEN_SUBSTITUTION_TEMPLATES: List[Path] = [
    Path('README.md.template'),
    Path('.gitignore.template'),
    Path('pyproject.toml.template'),
    Path('.envrc.template'),
    Path('.mypi.ini.template'),
]

# These values the the string names that we substitute
TOKEN_PROJECT_NAME:   str = 'PROJECT_NAME'
TOKEN_PYTHON_VERSION: str = 'PYTHON_VERSION'
TOKEN_OWNER_NAME:     str = 'OWNER_NAME'
TOKEN_OWNER_EMAIL:    str = 'OWNER_EMAIL'
TOKEN_DESCRIPTION:    str = 'DESCRIPTION'
TOKEN_KEYWORDS:       str = 'KEYWORDS'

TOKEN_DAY:             str = 'DAY'
TOKEN_MONTH_NAME_FULL: str = 'MONTH_NAME_FULL'
TOKEN_YEAR:            str = 'YEAR'

EXECUTION_PERMISSIONS: int = 0o555      # equivalent to gou+rx


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
        self._createApplicationSpecificPythonVersion()
        # self._createProjectVirtualEnvironment()
        self._createVirtualEnvironmentScript()

    def _createProjectDirectory(self) -> Path:

        projectPath: Path = self._projectDetails.baseDirectory / self._projectDetails.name

        try:
            projectPath.mkdir(parents=True, exist_ok=False)
        except FileExistsError:
            booBoo: MessageDialog = MessageDialog(parent=None,
                                                  message='We do not want to overwrite a potential project',
                                                  caption='Project path already exists',
                                                  style=OK | ICON_ERROR)
            booBoo.ShowModal()
            raise FabricationError(message=f'Project path already exists. {projectPath}')

        self._progressCallback(f'Created: {projectPath}')

        self.logger.info(f'Project path created: {projectPath}')
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

        self.logger.info(f'Skeleton directories computed')
        return directories

    def _createSkeletonDirectories(self):

        skeletonDictionary: SkeletonDictionary = vars(self._directories)

        for varName, directoryPath in skeletonDictionary.items():

            if varName != 'projectPath':

                directoryPath.mkdir(parents=True, exist_ok=True)
                self._progressCallback(f'Created: {directoryPath}')

        self.logger.info(f'Skeleton directories created')

    def _createPythonPackageFiles(self):

        skeletonDictionary: SkeletonDictionary = vars(self._directories)

        for varName, directoryPath in skeletonDictionary.items():
            if varName == 'projectPath' or varName == 'srcPath' or varName == 'circleCIPath':
                pass
            else:
                fullPath: Path = self._directories.projectPath / directoryPath / PACKAGE_DEFINITION_FILENAME
                fullPath.touch()
                self._progressCallback(f'Created: {fullPath}')

        self.logger.info(f'Python package files created')

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
        self.logger.info(f'Project versioning capability creation complete')

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
        self.logger.info(f'Logging configuration files created')

    def _createCircleCIFile(self):

        templateCIFile:  Path = self._configurationTemplatePath / CIRCLE_CI_TEMPLATE
        destinationPath: Path = self._directories.circleCIPath / Path(CIRCLE_CI_TEMPLATE).stem

        destinationPath.write_bytes(templateCIFile.read_bytes())

        self._progressCallback(f'Created {destinationPath}')
        self.logger.info(f'Circle CI configuration created')

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

    def _createApplicationSpecificPythonVersion(self):
        """
        Manually create .python-version

        """

        self.logger.info('Creating application specific version - Start')

        pythonVersionPath: Path = self._directories.projectPath / Path(PYTHON_VERSION_FILENAME)
        pythonVersionPath.write_text(str(self._projectDetails.pythonVersion))

        self._progressCallback(f'Application specific version set to {self._projectDetails.pythonVersion}')

        self.logger.info(f'Creating application specific version - Complete')

    def _createProjectVirtualEnvironment(self):
        """
        Currently unused see issue - https://github.com/hasii2011/pyfabricate/issues/5 for details.
        """
        try:
            self._progressCallback(f'Attempting creation of virtual environment for {self._projectDetails.pythonVersion}')
            virtualEnv: str = ExternalCommands.createVirtualEnvironment(version=self._projectDetails.pythonVersion, projectDirectory=self._projectPath)

            self._progressCallback(f'Created virtual environment for {self._projectDetails.pythonVersion}')
            self._progressCallback(f'{virtualEnv}')
        except UnableToCreateVirtualEnvironment as e:
            self.logger.error(f'Error in virtual environment creation')
            self.logger.error(f'{e.stderr}')
            dlg = MessageDialog(parent=None, message=f'{e.stderr}', caption='Venv Creation Error ', style=OK | CENTER)
            dlg.ShowModal()
            dlg.Destroy()

    def _createVirtualEnvironmentScript(self):
        """
        Modifies the createVirtualEnv.sh.template
        Moves it to the project directory
        Fixes the script permissions

        """
        templateScript:  Path = self._configurationTemplatePath / VENV_CREATION_SCRIPT_TEMPLATE
        destinationPath: Path = self._directories.projectPath   / Path(VENV_CREATION_SCRIPT_TEMPLATE).stem

        destinationPath.write_bytes(templateScript.read_bytes())
        self._progressCallback(f'Created {destinationPath}')

        today = datetime.now()

        tokenDict = {
            TOKEN_PYTHON_VERSION:  self._projectDetails.pythonVersion,
            TOKEN_DAY:             today.day,
            TOKEN_MONTH_NAME_FULL: today.strftime("%B"),
            TOKEN_YEAR:            today.year,
        }
        template: Template = Template(destinationPath.read_text())
        result:   str = template.substitute(tokenDict)
        #
        # Write the result back
        #
        destinationPath.write_text(result)

        self._progressCallback(f'Do not forget to execute: {destinationPath}')

        destinationPath.chmod(mode=EXECUTION_PERMISSIONS)
        self._progressCallback(f'Fixed permissions.')

    def _copyTemplatesToConfiguration(self, configurationTemplatePath: Path):
        """
        Copy the templates to our configuration directory.  This allows end user/developer
        customization, of a sort.

        Only copied if the template directory does not exist

        """
        self.logger.info(f'{configurationTemplatePath}')

        if configurationTemplatePath.exists() is False:

            configurationTemplatePath.mkdir(parents=True, exist_ok=True)

            resourcePath: Path = ResourceManager.computeResourcePath(resourcePath=TEMPLATE_RESOURCE_PATH, packageName=TEMPLATE_PACKAGE_NAME)

            for fqFileName in resourcePath.rglob('*.template'):

                destinationPath: Path = configurationTemplatePath / fqFileName.name

                destinationPath.write_bytes(fqFileName.read_bytes())
