
from typing import List

from logging import Logger
from logging import getLogger

from wx import CB_DROPDOWN
from wx import ComboBox

from wx.lib.sized_controls import SizedPanel

from pyfabricate.PageBase import PageBase


class PythonVersionPage(PageBase):
    def __init__(self, parent: SizedPanel):

        self.logger: Logger = getLogger(__name__)

        super().__init__(parent=parent)

        self._createLabel('Python Version:')

        self._pythonVersionSelection: ComboBox = ComboBox(parent=self, value='', size=(160, -1), choices=self._getPythonVersions(), style=CB_DROPDOWN)

    def _getPythonVersions(self) -> List[str]:
        """
        TODO:  We have to query pyenv

        Returns:  A list of installed python versions

        """
        pythonVersions: List[str] = [
            'system',
            '3.9.16',
            '3.10.10',
            '3.10.13',
            '3.11.0',
            '3.11.5',
            '3.11.7',
            '3.11.9',
            '3.12.0',
            '3.12.1',
            '3.12.4',
        ]

        return pythonVersions
