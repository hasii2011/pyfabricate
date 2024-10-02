
from typing import cast

from logging import Logger
from logging import getLogger
from logging import config


from os import sep as osSep

from json import load as jsonLoad

from wx import App
from wx import PyTimer

from wx import Exit as wxExit

from codeallybasic.ResourceManager import ResourceManager

from mage.Mage import MAGE_CANCELLED
from mage.Mage import MAGE_FINISHED
from mage.Mage import Mage
from mage.MagePage import MagePage

from tests.mage.MageIntroductionPage import MageIntroductionPage
from tests.mage.MageProjectDetailsPage import MageProjectDetailsPage
from tests.mage.MageProjectsBasePage import MageProjectsBasePage
from tests.mage.MagePythonVersionPage import MagePythonVersionPage

from tests.mage.MageTestFrame import MageTestFrame


class MageTestApp(App):

    JSON_LOGGING_CONFIG_FILENAME: str = "testLoggingConfiguration.json"
    # noinspection SpellCheckingInspection
    RESOURCES_PACKAGE_NAME: str = 'tests.resources'
    # noinspection SpellCheckingInspection
    RESOURCES_PATH:         str = f'tests{osSep}resources'

    def __init__(self):

        self.logger: Logger        = getLogger(__name__)
        self._frame: MageTestFrame = cast(MageTestFrame, None)
        self._timer: PyTimer       = cast(PyTimer, None)

        super().__init__(redirect=False)

    def OnInit(self):
        """
        """
        self._setupApplicationLogging()

        self._timer = PyTimer(self._startWizard)
        self._timer.Start(1000)

        return True

    @property
    def frame(self) -> MageTestFrame:
        return self._frame

    @frame.setter
    def frame(self, newFrame: MageTestFrame):
        self._frame = newFrame

    def _setupApplicationLogging(self):

        import logging

        configFilePath: str = ResourceManager.retrieveResourcePath(bareFileName=MageTestApp.JSON_LOGGING_CONFIG_FILENAME,
                                                                   resourcePath=MageTestApp.RESOURCES_PATH,
                                                                   packageName=MageTestApp.RESOURCES_PACKAGE_NAME)

        with open(configFilePath, 'r') as loggingConfigurationFile:
            configurationDictionary = jsonLoad(loggingConfigurationFile)

        config.dictConfig(configurationDictionary)
        logging.logProcesses = False
        logging.logThreads   = False

    def _startWizard(self):
        self._timer.Stop()

        mage: Mage = Mage(parent=self._frame, title='Test Mage')

        introPage:     MagePage              = MageIntroductionPage(parent=mage.pageContainer)
        manyCtrlsPage: MagePage              = MageProjectDetailsPage(parent=mage.pageContainer)
        projectBase:   MageProjectsBasePage  = MageProjectsBasePage(parent=mage.pageContainer)
        pythonVersion: MagePythonVersionPage = MagePythonVersionPage(parent=mage.pageContainer)

        mage.addMage(magePage=introPage)
        mage.addMage(magePage=projectBase)
        mage.addMage(magePage=manyCtrlsPage)
        mage.addMage(magePage=pythonVersion)

        status: int = mage.runWizard()
        if status == MAGE_CANCELLED:
            self.logger.info(f'Mage Cancelled')
            wxExit()
        elif status == MAGE_FINISHED:
            self._frame.runOperations()


if __name__ == "__main__":

    wxApp: MageTestApp = MageTestApp()

    demoFrame: MageTestFrame = MageTestFrame()

    wxApp.frame = demoFrame

    demoFrame.Show(True)
    wxApp.SetTopWindow(demoFrame)

    wxApp.MainLoop()
