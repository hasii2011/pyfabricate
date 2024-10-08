
from typing import Optional

from logging import Logger
from logging import getLogger

from os import getenv as osGetEnv

from wx import CommandEvent
from wx import DEFAULT_FRAME_STYLE
from wx import FRAME_FLOAT_ON_PARENT
from wx import FRAME_TOOL_WINDOW
from wx import HSCROLL
from wx import ID_ANY
from wx import ID_EXIT
from wx import Menu
from wx import MenuBar
from wx import Point
from wx import EVT_MENU
from wx import Size
from wx import TE_MULTILINE

from wx.lib.sized_controls import SizedFrame
from wx.lib.sized_controls import SizedPanel

from wx.richtext import RichTextCtrl

from pyfabricate.Fabricator import Fabricator
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

        panel: SizedPanel = self.GetContentsPane()
        panel.SetSizerType('horizontal')

        self._console: RichTextCtrl = RichTextCtrl(parent=panel, size=Size(WINDOW_WIDTH, WINDOW_HEIGHT), style=TE_MULTILINE | HSCROLL)
        self._console.SetSizerProps(expand=True)

        self._lineNumber: int = 0

    def runOperations(self, projectDetails: ProjectDetails):

        self.SetSize(Size(WINDOW_WIDTH, WINDOW_HEIGHT))
        self.Layout()

        self._addLineToConsole('Operations are running')
        self._addLineToConsole(f'{projectDetails}')

        fabricator: Fabricator = Fabricator(projectDetails=projectDetails)
        fabricator.createProjectDirectory()

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

    def _addLineToConsole(self, text: str):

        self._lineNumber += 1

        self._console.BeginFontSize(14)
        self._console.BeginTextColour((255, 0, 0))
        self._console.WriteText(f'{self._lineNumber}: ')
        self._console.EndTextColour()
        self._console.EndFontSize()

        self._console.WriteText(text=f'{text}')
        self._console.Newline()
