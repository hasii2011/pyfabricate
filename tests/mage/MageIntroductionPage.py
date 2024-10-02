
from logging import Logger
from logging import getLogger

from wx import FONTFAMILY_SWISS
from wx import FONTSTYLE_NORMAL
from wx import FONTWEIGHT_BOLD
from wx import ID_ANY

from wx import Font

from wx import StaticLine
from wx import StaticText

from wx.lib.sized_controls import SizedPanel

from tests.mage.MageBase import MageBase


class MageIntroductionPage(MageBase):

    TITLE: str = 'Introduction'

    INTRODUCTION_TEXT: str = """
    The purpose of this demonstration is to:


        - Test a many paged mage (aka wizard)
        - Test multiple sized mage pages
        - Test to ensure correct status returned from running wizard
        - Test that the mage generates appropriate `Cancel` and `Finish` events

    """

    def __init__(self, parent: SizedPanel):

        self.logger: Logger = getLogger(__name__)
        super().__init__(parent=parent)

        self.SetSizerType('vertical')

        self._createPageTitle()
        self._createIntroductionText()

    def _createPageTitle(self):
        """
        """
        title: StaticText = StaticText(self, ID_ANY, MageIntroductionPage.TITLE)
        title.SetFont(Font(18, FONTFAMILY_SWISS, FONTSTYLE_NORMAL, FONTWEIGHT_BOLD))

        StaticLine(parent=self, id=ID_ANY)

    def _createIntroductionText(self):

        StaticText(parent=self, id=ID_ANY, label=MageIntroductionPage.INTRODUCTION_TEXT)
