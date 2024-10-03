
from typing import List
from typing import NewType
from typing import cast

from logging import Logger
from logging import getLogger

from wx import BORDER_THEME
from wx import Bitmap
from wx import Button
from wx import CommandEvent
from wx import ID_ANY
from wx import OK
from wx import Size
from wx import StaticBitmap
from wx import Window

from wx import CANCEL
from wx import CAPTION
from wx import CLOSE_BOX
from wx import EVT_BUTTON
from wx import ID_CANCEL
from wx import STAY_ON_TOP

from wx import NewIdRef as wxNewIdRef
from wx.lib.buttons import ThemedGenBitmapTextButton

from wx.lib.sized_controls import SizedDialog
from wx.lib.sized_controls import SizedPanel

from mage.MagePage import MagePage

from mage.resources.MageBitMap import embeddedImage as mageImage

from mage.resources.cancel16 import embeddedImage as cancelButtonImage
from mage.resources.next16 import embeddedImage as nextButtonImage
from mage.resources.back16 import embeddedImage as backButtonImage

from pyfabricate.steps.PageBase import PageBase

BUTTON_NEXT_TEXT:   str = 'Next'
BUTTON_BACK_TEXT:   str = 'Back'
BUTTON_CANCEL_TEXT: str = 'Cancel'
BUTTON_FINISH_TEXT: str = 'Finish'

MAGE_CANCELLED: int = wxNewIdRef()
MAGE_FINISHED:  int = wxNewIdRef()

MagePages = NewType('MagePages', List[MagePage])


class Mage(SizedDialog):
    """
    Peculiarities:

        * As noted below make the static image large and the dialog stays a fixed size
        * Also, the first page must be the largest for the entire dialog to display

    """

    def __init__(self, parent: Window, title: str, bitmap: Bitmap = None):

        self.logger: Logger = getLogger(__name__)

        super().__init__(parent=parent, title=title, style=CAPTION | STAY_ON_TOP | CLOSE_BOX)

        self._pages:            MagePages = MagePages([])
        self._pageNumber:       int       = 0
        self._wizardSuccessful: bool      = True
        # self._largestPageSize:  Size      = cast(Size, None)

        # Outer panel hold buttons and side by side panel
        sizedPanel: SizedPanel = self.GetContentsPane()
        sizedPanel.SetSizerType('vertical')
        sizedPanel.SetSizerProps(border=(["top", "bottom"], 10))

        self._horizontalPanel: SizedPanel = SizedPanel(parent=sizedPanel, style=BORDER_THEME)
        self._horizontalPanel.SetSizerType('horizontal')
        self._horizontalPanel.SetSizerProps(border=(["top", "bottom", "left", "right"], 20))

        self._btnCancel: Button = cast(Button, None)
        self._btnNext:   Button = cast(Button, None)
        self._btnBack:   Button = cast(Button, None)

        if bitmap is not None:
            self._bitMap: Bitmap = bitmap
        else:
            self._bitMap = mageImage.GetBitmap()

        # Making the bitmap large seems to keep the dialog a static size
        self._logo: StaticBitmap = StaticBitmap(parent=self._horizontalPanel, id=ID_ANY, bitmap=self._bitMap, size=Size(width=100, height=200))
        self._logo.SetSizerProps(proportion=1, halign='left', valign='center')

    @property
    def pageContainer(self) -> SizedPanel:
        """
        Client should parent their mage pages with this panel

        Returns:  The panel that should be the parent of all the mage's pages

        """
        return self._horizontalPanel

    def addMage(self, magePage: MagePage):
        """
        Add a page to the mage;  Add them in the order you want
        to display them

        Args:
            magePage:
        """
        self._pages.append(magePage)

        magePage.Hide()
        self.Layout()

    def runWizard(self):

        self._layoutWizardButtons(parent=self.GetContentsPane())

        self._pages[self._pageNumber].Show()

        self.GetContentsPane().Layout()
        self.Fit()
        self.SetMinSize(self.GetSize())

        self._btnBack.Disable()

        ans = self.ShowModal()
        if ans == CANCEL:
            self.logger.info('Cancel pressed')
            return MAGE_CANCELLED
        else:
            return MAGE_FINISHED

    # noinspection PyUnusedLocal
    def _onCancel(self, event: CommandEvent):
        self._wizardSuccessful = False
        self.EndModal(CANCEL)

    # noinspection PyUnusedLocal
    def _onNext(self, event: CommandEvent):
        """
        Handle setting that we are on last page
        When we go past last page end the dialog

        Args:
            event:
        """

        oldPage: PageBase = self._pages[self._pageNumber]
        if oldPage.validate() is False:
            return                  # Ugh.  short cut out

        oldPage.Hide()
        self._pageNumber += 1

        pageCount: int = len(self._pages)

        if pageCount - 1 == self._pageNumber:
            self._btnNext.SetLabel(BUTTON_FINISH_TEXT)
        elif pageCount == self._pageNumber:
            self.EndModal(OK)
            return                  # Ugh.  short cut out

        self._btnBack.SetLabel(BUTTON_BACK_TEXT)
        self._btnBack.Enable()

        newPage: PageBase = self._pages[self._pageNumber]
        newPage.Show()
        self.GetContentsPane().Layout()

    # noinspection PyUnusedLocal
    def _onBack(self, event: CommandEvent):

        oldPage: PageBase = self._pages[self._pageNumber]
        oldPage.Hide()

        self._pageNumber -= 1
        if self._pageNumber == 0:
            self._btnBack.Disable()

        newPage: PageBase = self._pages[self._pageNumber]
        newPage.Show()

        self.GetContentsPane().Layout()
        self._btnNext.SetLabel(BUTTON_NEXT_TEXT)

    def _layoutWizardButtons(self, parent: SizedPanel):

        buttonPanel: SizedPanel = SizedPanel(parent)
        buttonPanel.SetSizerType('horizontal')
        buttonPanel.SetSizerProps(expand=False, halign='right')  # expand False allows aligning right

        self._btnCancel = ThemedGenBitmapTextButton(buttonPanel, label=BUTTON_CANCEL_TEXT, bitmap=cancelButtonImage.GetBitmap(), id=ID_CANCEL)
        self._btnNext   = ThemedGenBitmapTextButton(buttonPanel, label=BUTTON_NEXT_TEXT,   bitmap=nextButtonImage.GetBitmap())
        self._btnBack   = ThemedGenBitmapTextButton(buttonPanel, label=BUTTON_BACK_TEXT,   bitmap=backButtonImage.GetBitmap(),)

        self._btnCancel.Bind(EVT_BUTTON, self._onCancel)
        self._btnNext.Bind(EVT_BUTTON,   self._onNext)
        self._btnBack.Bind(EVT_BUTTON,   self._onBack)

        self._btnNext.SetDefault()
