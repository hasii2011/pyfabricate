
from typing import List
from typing import cast

from logging import Logger
from logging import getLogger

from wx import CENTER
from wx import ComboBox
from wx import CommandEvent
from wx import EVT_COMBOBOX
from wx import MessageDialog
from wx import OK

from wx.lib.sized_controls import SizedPanel

from semantic_version import Version as SemanticVersion

from pyfabricate.oswrapper.ExternalCommands import ExternalCommands
from pyfabricate.oswrapper.ExternalCommands import SemanticVersions

from pyfabricate.steps.PageBase import PageBase


class PythonVersionStep(PageBase):
    def __init__(self, parent: SizedPanel):

        self.logger: Logger = getLogger(__name__)

        super().__init__(parent=parent)

        self._createLabel('Python Version:')

        self._pythonVersionSelection: ComboBox = ComboBox(parent=self, value='', size=(160, -1), choices=self._getPythonVersions())

        self._pythonVersionSelection.SetSelection(-1)

        self.Bind(EVT_COMBOBOX, self._onSelectedVersion)

        self._selectedVersion: SemanticVersion = cast(SemanticVersion, None)

    def validate(self) -> bool:
        if self._selectedVersion is None:
            dlg = MessageDialog(parent=None, message=f'You must select a Python version', caption='Invalid Python Version', style=OK | CENTER)
            dlg.ShowModal()
            dlg.Destroy()

            return False
        else:
            return True

    @property
    def selectedVersion(self) -> SemanticVersion:
        return self._selectedVersion

    def _getPythonVersions(self) -> List[str]:
        """
        TODO:  We have to query pyenv

        Returns:  A list of installed python versions

        """
        pythonVersions: SemanticVersions = ExternalCommands.getPythonVersions()

        strVersions: List[str] = []

        for pythonVersion in pythonVersions:
            strVersions.append(str(pythonVersion))

        return strVersions

    def _onSelectedVersion(self, event: CommandEvent):

        versionStr: str = event.GetString()

        self._selectedVersion = SemanticVersion(versionStr)
