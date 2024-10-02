
from typing import cast

from logging import Logger
from logging import getLogger
from logging import config

from os import sep as osSep

from json import load as jsonLoad

from wx import App
from wx import Bitmap
from wx import PyTimer

from wx import Exit as wxExit

from codeallybasic.ResourceManager import ResourceManager

from mage.Mage import MAGE_CANCELLED
from mage.Mage import MAGE_FINISHED
from mage.Mage import Mage
from mage.MagePage import MagePage

from pyfabricate.ProjectDetailsPage import ProjectDetailsPage
from pyfabricate.ProjectsBasePage import ProjectsBasePage
from pyfabricate.PyFabricateFrame import PyFabricateFrame
from pyfabricate.IntroductionPage import IntroductionPage
from pyfabricate.PythonVersionPage import PythonVersionPage

from pyfabricate.resources.images.PyFabricateLogo import embeddedImage as pyFabricateLogo


class PyFabricateApp(App):

    JSON_LOGGING_CONFIG_FILENAME: str = "loggingConfiguration.json"
    # noinspection SpellCheckingInspection
    RESOURCES_PACKAGE_NAME: str = 'pyfabricate.resources'
    # noinspection SpellCheckingInspection
    RESOURCES_PATH:         str = f'pyfabricate{osSep}resources'

    def __init__(self):

        self.logger: Logger           = getLogger(__name__)
        self._frame: PyFabricateFrame = cast(PyFabricateFrame, None)
        self._timer: PyTimer          = cast(PyTimer, None)

        super().__init__(redirect=False)

    def OnInit(self):
        """
        """
        self._setupApplicationLogging()

        self._timer = PyTimer(self._startWizard)
        self._timer.Start(1000)

        return True

    @property
    def frame(self) -> PyFabricateFrame:
        return self._frame

    @frame.setter
    def frame(self, newFrame: PyFabricateFrame):
        self._frame = newFrame

    def _setupApplicationLogging(self):

        import logging

        configFilePath: str = ResourceManager.retrieveResourcePath(bareFileName=PyFabricateApp.JSON_LOGGING_CONFIG_FILENAME,
                                                                   resourcePath=PyFabricateApp.RESOURCES_PATH,
                                                                   packageName=PyFabricateApp.RESOURCES_PACKAGE_NAME)

        with open(configFilePath, 'r') as loggingConfigurationFile:
            configurationDictionary = jsonLoad(loggingConfigurationFile)

        config.dictConfig(configurationDictionary)
        logging.logProcesses = False
        logging.logThreads   = False

    def _startWizard(self):
        self._timer.Stop()

        logo: Bitmap = pyFabricateLogo.GetBitmap()
        mage: Mage   = Mage(parent=self._frame, title='PyFabricate Parameters', bitmap=logo)
        #
        introPage:          MagePage = IntroductionPage(parent=mage.pageContainer)
        projectDetailsPage: MagePage = ProjectDetailsPage(parent=mage.pageContainer)
        projectBase:        MagePage = ProjectsBasePage(parent=mage.pageContainer)
        pythonVersion:      MagePage = PythonVersionPage(parent=mage.pageContainer)
        #
        mage.addMage(magePage=introPage)
        mage.addMage(magePage=projectDetailsPage)
        mage.addMage(magePage=projectBase)
        mage.addMage(magePage=pythonVersion)
        #
        status: int = mage.runWizard()
        if status == MAGE_CANCELLED:
            self.logger.info(f'Mage Cancelled')
            wxExit()
        elif status == MAGE_FINISHED:
            self._frame.runOperations()


if __name__ == "__main__":

    pyFabricateApp:   PyFabricateApp   = PyFabricateApp()
    pyFabricateFrame: PyFabricateFrame = PyFabricateFrame()

    pyFabricateApp.frame = pyFabricateFrame

    pyFabricateFrame.Show(True)
    pyFabricateApp.SetTopWindow(pyFabricateFrame)

    pyFabricateApp.MainLoop()
