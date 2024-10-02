
from logging import Logger
from logging import getLogger

from wx import FONTFAMILY_SWISS
from wx import FONTSTYLE_NORMAL
from wx import FONTWEIGHT_BOLD
from wx import Font
from wx import ID_ANY
from wx import StaticText

from wx.lib.sized_controls import SizedPanel

from mage.MagePage import MagePage

STANDARD_LABEL_FONT_SIZE: int = 12


class PageBase(MagePage):

    def __init__(self, parent: SizedPanel):

        self.logger: Logger = getLogger(__name__)

        super().__init__(parent=parent)

    def validate(self) -> bool:
        """

        Returns:  `True` if all the user entered data is good; Else `False`
        """
        return True

    def _createLabel(self, label: str, fontSize: int = STANDARD_LABEL_FONT_SIZE) -> StaticText:

        staticText: StaticText = StaticText(self, ID_ANY, label)

        staticText.SetFont(Font(fontSize, FONTFAMILY_SWISS, FONTSTYLE_NORMAL, FONTWEIGHT_BOLD))

        return staticText
