
from typing import Optional

from logging import Logger
from logging import getLogger

from os import getenv as osGetEnv

from wx import ClientDC
from wx import CommandEvent
from wx import DEFAULT_FRAME_STYLE
from wx import FRAME_FLOAT_ON_PARENT
from wx import FRAME_TOOL_WINDOW
from wx import HSCROLL
from wx import ID_ABOUT
from wx import ID_ANY
from wx import ID_EXIT
from wx import Icon
from wx import Menu
from wx import MenuBar
from wx import Point
from wx import EVT_MENU
from wx import Size
from wx import TE_MULTILINE

from wx import Yield as wxYield

from wx.adv import AboutBox
from wx.adv import AboutDialogInfo

from wx.lib.sized_controls import SizedFrame
from wx.lib.sized_controls import SizedPanel

from wx.lib.wordwrap import wordwrap

from wx.richtext import RichTextCtrl

from codeallybasic.SecureConversions import SecureConversions

from pyfabricate.fabrication.Fabricator import Fabricator
from pyfabricate.ProjectDetails import ProjectDetails

from pyfabricate import __version__ as pyFabricateVersion

from pyfabricate.resources.images.AppLogo import embeddedImage as appLogo

WINDOW_WIDTH:  int = 800
WINDOW_HEIGHT: int = 400

MINI_WINDOW_WIDTH:  int = 100
MINI_WINDOW_HEIGHT: int = 50

APP_MODE: str = 'APP_MODE'

DESCRIPTION: str = """
PyFabricate is a Mac OS X application that 
simplifies the creation of Python projects.  

Since I authored it, obviously it is an 
opinionated version of what I think a Python 
project should look like. 
"""

DESCRIPTION_WIDTH: int = 400


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
        wxYield()

        self._addLineToConsole('Operations are running')
        self._addLineToConsole(f'{projectDetails}')

        fabricator: Fabricator = Fabricator(projectDetails=projectDetails, progressCallback=self._addLineToConsole)
        fabricator.fabricate()

    def _makeMenus(self):
        fileMenu: Menu = Menu()

        fileMenu.Append(ID_EXIT, "E&xit\tAlt+Q", "Exit the program")
        fileMenu.Append(ID_ABOUT, '&About', 'Tell you about me')

        menuBar: MenuBar = MenuBar()
        menuBar.Append(fileMenu, "&File")

        self.Bind(EVT_MENU, self._onFileExit, id=ID_EXIT)
        self.Bind(EVT_MENU, self._onAbout,    id=ID_ABOUT)

        self.SetMenuBar(menuBar)

    # noinspection PyUnusedLocal
    def _onFileExit(self, event: CommandEvent):
        self.Close(True)

    # noinspection PyUnusedLocal
    def _onAbout(self, event: CommandEvent):

        icon:         Icon   = Icon()
        icon.CopyFromBitmap(bmp=appLogo.GetBitmap())

        # First we create and fill the info object
        info: AboutDialogInfo = AboutDialogInfo()

        info.Name = 'PyFabricate'
        info.Version = pyFabricateVersion
        info.Copyright = '(C) 2024 Humberto A. Sanchez II <humberto.a.sanchez.ii@gmail.com>'
        info.Description = wordwrap(DESCRIPTION, DESCRIPTION_WIDTH, ClientDC(self))
        info.WebSite = ("https://github.com/hasii2011/pyfabricate", "PyFabricate")
        info.Developers = ['Humberto A. Sanchez II']
        info.SetIcon(icon)

        AboutBox(info)

    def _addLineToConsole(self, text: str):
        """
        Adds a line to our pseudo operations console.  Scrolls to end
        so last line is always visible

        Args:
            text:  The line to append
        """

        self._lineNumber += 1

        self._console.BeginFontSize(14)
        self._console.BeginTextColour((255, 0, 0))
        self._console.WriteText(f'{self._lineNumber}: ')
        self._console.EndTextColour()
        self._console.EndFontSize()

        self._console.WriteText(text=f'{text}')
        self._console.Newline()
        carrotPosition: float = self._console.GetCaretPosition()        # Hee, hee
        self._console.ShowPosition(carrotPosition)
        wxYield()
