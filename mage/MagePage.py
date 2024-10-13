
from logging import Logger
from logging import getLogger

from wx.lib.sized_controls import SizedPanel


class MagePage(SizedPanel):
    """
    """
    def __init__(self, parent: SizedPanel):

        self.logger: Logger = getLogger(__name__)

        super().__init__(parent=parent)
