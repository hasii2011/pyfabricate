
from logging import Logger
from logging import getLogger

from wx import ID_ANY
from wx import StaticLine
from wx import StaticText
from wx.lib.sized_controls import SizedPanel

from pyfabricate.PageBase import PageBase


class IntroductionPage(PageBase):

    TITLE_FONT_SIZE: int = 18

    TITLE: str = 'Introduction'

    INTRODUCTION_TEXT: str = """
    The purpose of this Python script is to automate the process of creating a Python project.
    
    Assumptions

        - Python is managed via pyenv
        - direnv is installed
        - You have a base directory where you store Python projects

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
        self._createLabel(label=IntroductionPage.TITLE, fontSize=IntroductionPage.TITLE_FONT_SIZE)
        StaticLine(parent=self, id=ID_ANY)

    def _createIntroductionText(self):

        StaticText(parent=self, id=ID_ANY, label=IntroductionPage.INTRODUCTION_TEXT)
