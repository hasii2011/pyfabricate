
from typing import Optional

from logging import Logger
from logging import getLogger

from os import getenv as osGetEnv

from wx import CommandEvent
from wx import DEFAULT_FRAME_STYLE
from wx import FRAME_FLOAT_ON_PARENT
from wx import FRAME_TOOL_WINDOW
from wx import ID_ANY
from wx import ID_EXIT
from wx import Menu
from wx import MenuBar
from wx import Point
from wx import EVT_MENU
from wx import Size
from wx import StaticText

from wx.lib.sized_controls import SizedFrame

from wx.lib.sized_controls import SizedPanel

from pyfabricate.ProjectDetails import ProjectDetails

from codeallybasic.SecureConversions import SecureConversions

WINDOW_WIDTH:  int = 800
WINDOW_HEIGHT: int = 400

MINI_WINDOW_WIDTH:  int = 100
MINI_WINDOW_HEIGHT: int = 50

APP_MODE: str = 'APP_MODE'


class PyFabricateFrame(SizedFrame):
    def __init__(self):

        self.logger: Logger = getLogger(__name__)

        title:          str           = 'PyFabricate'
        frameStyle:     int           = DEFAULT_FRAME_STYLE | FRAME_FLOAT_ON_PARENT
        appModeStr:     Optional[str] = osGetEnv(APP_MODE)

        if appModeStr is None:
            appMode: bool = False
        else:
            appMode = SecureConversions.secureBoolean(appModeStr)

        if appMode is True:
            frameStyle = frameStyle | FRAME_TOOL_WINDOW

        super().__init__(parent=None, id=ID_ANY,
                         size=(MINI_WINDOW_WIDTH, MINI_WINDOW_HEIGHT),
                         pos=Point(20, 40),
                         style=frameStyle, title=title)

        self._makeMenus()

    def runOperations(self, projectDetails: ProjectDetails):

        panel: SizedPanel = self.GetContentsPane()
        panel.SetSizerType('vertical')

        StaticText(parent=panel, label='Operations are running')
        StaticText(parent=panel, label=f'{projectDetails}')

        self.SetSize(Size(800, 600))

    def _makeMenus(self):
        fileMenu: Menu = Menu()

        fileMenu.Append(ID_EXIT, "E&xit\tAlt+Q", "Exit the program")

        menuBar: MenuBar = MenuBar()
        menuBar.Append(fileMenu, "&File")

        self.Bind(EVT_MENU, self._onFileExit, id=ID_EXIT)

        self.SetMenuBar(menuBar)

    # noinspection PyUnusedLocal
    def _onFileExit(self, event: CommandEvent):
        self.Close(True)
