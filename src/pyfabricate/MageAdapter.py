
from typing import Callable

from logging import Logger
from logging import getLogger

from wx import Bitmap
from wx import Window

from mage.Mage import MAGE_CANCELLED
from mage.Mage import MAGE_FINISHED
from mage.Mage import Mage
from mage.MagePage import MagePage

from pyfabricate.Settings import Settings

from pyfabricate.steps.IntroductionStep import IntroductionStep
from pyfabricate.steps.ProjectDetailsStep import ProjectDetails
from pyfabricate.steps.ProjectDetailsStep import ProjectDetailsStep
from pyfabricate.steps.ProjectsBaseDirectoryPage import ProjectsBaseDirectoryPage
from pyfabricate.steps.PythonVersionStep import PythonVersionStep

from pyfabricate.resources.images.PyFabricateLogo import embeddedImage as pyFabricateLogo

CompleteCallback = Callable[[ProjectDetails], None]
CancelCallback   = Callable[[], None]


class MageAdapter:
    """
    Moves all the details of handling the mage to a separate class
    """
    def __init__(self, parent: Window, completeCallback: CompleteCallback, cancelCallback: CancelCallback):

        self._frame:            Window           = parent
        self._completeCallback: CompleteCallback = completeCallback
        self._cancelCallback:   CancelCallback   = cancelCallback

        self.logger: Logger = getLogger(__name__)

        self._settings: Settings = Settings()

        projectDetails: ProjectDetails = self._fromSettings()

        logo: Bitmap = pyFabricateLogo.GetBitmap()
        mage: Mage   = Mage(parent=self._frame, title='PyFabricate Parameters', bitmap=logo)
        #
        introPage:          MagePage                  = IntroductionStep(parent=mage.pageContainer)
        projectDetailsStep: ProjectDetailsStep        = ProjectDetailsStep(parent=mage.pageContainer, projectDetails=projectDetails)
        projectBaseStep:    ProjectsBaseDirectoryPage = ProjectsBaseDirectoryPage(parent=mage.pageContainer, baseDirectory=projectDetails.baseDirectory)
        pythonVersion:      PythonVersionStep         = PythonVersionStep(parent=mage.pageContainer)
        #
        mage.addMage(magePage=introPage)
        mage.addMage(magePage=projectDetailsStep)
        mage.addMage(magePage=projectBaseStep)
        mage.addMage(magePage=pythonVersion)

        self._mage:               Mage                      = mage
        self._projectDetailsStep: ProjectDetailsStep        = projectDetailsStep
        self._projectBaseStep:    ProjectsBaseDirectoryPage = projectBaseStep
        self._projectDetails:     ProjectDetails            = projectDetails
        self._pythonVersion:      PythonVersionStep         = pythonVersion

    def run(self):

        status: int = self._mage.runWizard()
        if status == MAGE_CANCELLED:
            self.logger.info(f'Mage Cancelled')
            self._cancelCallback()
        elif status == MAGE_FINISHED:
            updatedProjectDetails: ProjectDetails = self._projectDetailsStep.projectDetails
            updatedProjectDetails.baseDirectory   = self._projectBaseStep.baseDirectory
            updatedProjectDetails.pythonVersion   = self._pythonVersion.selectedVersion

            self._settings = self._toSettings(updatedProjectDetails=updatedProjectDetails)

            self._completeCallback(updatedProjectDetails)

    def _fromSettings(self) -> ProjectDetails:
        """
        Extract from the setting file

        Returns:  A project details object
        """

        projectDetails: ProjectDetails = ProjectDetails()

        projectDetails.name          = self._settings.name
        projectDetails.ownerEmail    = self._settings.ownerEmail
        projectDetails.description   = self._settings.description
        projectDetails.keywords      = self._settings.keywords
        projectDetails.baseDirectory = self._settings.baseDirectory

        return projectDetails

    def _toSettings(self, updatedProjectDetails: ProjectDetails) -> Settings:
        """
        Copies back from the updated project details after the developer interacts
        with the mage

        Args:
            updatedProjectDetails:

        Returns:  The singleton settings
        """

        self._settings.name          = updatedProjectDetails.name
        self._settings.ownerEmail    = updatedProjectDetails.ownerEmail
        self._settings.description   = updatedProjectDetails.description
        self._settings.keywords      = updatedProjectDetails.keywords
        self._settings.baseDirectory = updatedProjectDetails.baseDirectory

        return self._settings
