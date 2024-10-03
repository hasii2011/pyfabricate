
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

from pyfabricate.PyFabricateFrame import PyFabricateFrame
from pyfabricate.Settings import Settings

from pyfabricate.MageAdapter import MageAdapter


class PyFabricateApp(App):

    JSON_LOGGING_CONFIG_FILENAME: str = "loggingConfiguration.json"
    # noinspection SpellCheckingInspection
    RESOURCES_PACKAGE_NAME: str = 'pyfabricate.resources'
    # noinspection SpellCheckingInspection
    RESOURCES_PATH:         str = f'pyfabricate{osSep}resources'

    def __init__(self):

        self.logger:    Logger   = getLogger(__name__)
        self._settings: Settings = Settings()

        self._frame: PyFabricateFrame = cast(PyFabricateFrame, None)
        self._timer: PyTimer          = cast(PyTimer, None)

        super().__init__(redirect=False)

    def OnInit(self):
        """
        """
        self._setupApplicationLogging()

        self._timer = PyTimer(self._startMage)
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

    def _startMage(self):
        self._timer.Stop()

        mageAdapter: MageAdapter = MageAdapter(parent=self._frame, completeCallback=self._frame.runOperations, cancelCallback=wxExit)
        mageAdapter.run()

if __name__ == "__main__":

    pyFabricateApp:   PyFabricateApp   = PyFabricateApp()
    pyFabricateFrame: PyFabricateFrame = PyFabricateFrame()

    pyFabricateApp.frame = pyFabricateFrame

    pyFabricateFrame.Show(True)
    pyFabricateApp.SetTopWindow(pyFabricateFrame)

    pyFabricateApp.MainLoop()
