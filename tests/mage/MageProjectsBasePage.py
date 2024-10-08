
from logging import Logger
from logging import getLogger

from wx.lib.sized_controls import SizedPanel

from pyfabricate.components.DirectorySelector import DirectorySelector

from tests.mage.MageBase import MageBase


class MageProjectsBasePage(MageBase):

    def __init__(self, parent: SizedPanel):

        self.logger: Logger = getLogger(__name__)

        super().__init__(parent=parent)
        self.SetSizerType('horizontal')

        self._createLabel(label='Base Directory:')
        self._directorySelector: DirectorySelector = DirectorySelector(parent=self)
