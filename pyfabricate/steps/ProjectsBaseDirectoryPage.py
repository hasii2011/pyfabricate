
from logging import Logger
from logging import getLogger
from pathlib import Path

from wx import StaticText
from wx.lib.sized_controls import SizedPanel

from pyfabricate.steps.PageBase import PageBase

from pyfabricate.components.DirectorySelector import DirectorySelector


class ProjectsBaseDirectoryPage(PageBase):

    def __init__(self, parent: SizedPanel, baseDirectory: Path):

        self.logger:         Logger = getLogger(__name__)

        super().__init__(parent=parent)
        self.SetSizerType('horizontal')

        label: StaticText = self._createLabel(label='Base Directory:')

        label.SetSizerProps(valign='center')
        self._directorySelector: DirectorySelector = DirectorySelector(parent=self)

        self._directorySelector.directoryPath = baseDirectory

    @property
    def baseDirectory(self) -> Path:
        return self._directorySelector.directoryPath
