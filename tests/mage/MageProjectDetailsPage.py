
from logging import Logger
from logging import getLogger

from wx import TE_PROCESS_ENTER
from wx import TextCtrl

from wx.lib.sized_controls import SizedPanel

from tests.mage.MageBase import MageBase

STANDARD_LABEL_FONT_SIZE: int = 12


class MageProjectDetailsPage(MageBase):

    def __init__(self, parent: SizedPanel):

        self.logger: Logger = getLogger(__name__)

        super().__init__(parent=parent)

        self.SetSizerType('form')
        self._nameInput:        TextCtrl = self._createInputPair(label='Project Name:')
        self._ownerEmailInput:  TextCtrl = self._createInputPair(label='Project Owner EMail:', helpText='The owner email in pyproject.toml')
        self._descriptionInput: TextCtrl = self._createInputPair(label='Project Description:')
        self._keywordsInput:    TextCtrl = self._createInputPair(label='Project Keywords:')

    def _createInputPair(self, label: str, helpText: str = '') -> TextCtrl:

        self._createLabel(label)
        textInput:  TextCtrl = TextCtrl(parent=self, style=TE_PROCESS_ENTER)

        textInput.SetHelpText(helpText=helpText)

        return textInput
