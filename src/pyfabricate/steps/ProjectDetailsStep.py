
from typing import Callable

from dataclasses import dataclass
from logging import Logger
from logging import getLogger

from wx import CENTER
from wx import CommandEvent
from wx import EVT_TEXT
from wx import EVT_TEXT_ENTER
from wx import MessageDialog
from wx import OK
from wx import Size
from wx import StaticText
from wx import TE_PROCESS_ENTER
from wx import TextCtrl
from wx import wxEVT_TEXT_ENTER

from wx.lib.sized_controls import SizedPanel

from pyfabricate.steps.PageBase import PageBase

STANDARD_LABEL_FONT_SIZE: int = 12


@dataclass
class ProjectDetails:
    name:        str = ''
    ownerEmail:  str = ''
    description: str = ''
    keywords:    str = ''


class ProjectDetailsStep(PageBase):

    def __init__(self, parent: SizedPanel):

        self.logger: Logger = getLogger(__name__)

        super().__init__(parent=parent)

        self.SetSizerType('form')
        self._nameInput:        TextCtrl = self._createInputPair(label='Project Name:',        helpText='The project name')
        self._ownerEmailInput:  TextCtrl = self._createInputPair(label='Project Owner EMail:', helpText='The owner email in pyproject.toml')
        self._descriptionInput: TextCtrl = self._createInputPair(label='Project Description:', helpText='The project description')
        self._keywordsInput:    TextCtrl = self._createInputPair(label='Project Keywords:',    helpText='Comma separated list of keywords')

        self._projectDetails: ProjectDetails = ProjectDetails()

        self._bindControls()

    @property
    def projectDetails(self) -> ProjectDetails:
        return self._projectDetails

    def validate(self) -> bool:

        def validateField(field: str, errorMessage: str) -> bool:

            validField: bool = True
            if len(field) == 0:
                validField = False
                dlg = MessageDialog(parent=None, message=f'Invalid {errorMessage}', caption='Invalid Input', style=OK | CENTER)
                dlg.ShowModal()
                dlg.Destroy()

            return validField

        valid: bool = True
        if (validateField(self._projectDetails.name, 'Project Name') is False or
                validateField(self._projectDetails.ownerEmail, 'eMail') is False or
                validateField(self._projectDetails.description, 'description') is False or
                validateField(self._projectDetails.keywords, 'Keywords') is False):
            valid = False

        return valid

    def _createInputPair(self, label: str, helpText: str = '') -> TextCtrl:

        staticText: StaticText = self._createLabel(label)
        textInput:  TextCtrl   = TextCtrl(parent=self, style=TE_PROCESS_ENTER, size=Size(width=275, height=-1))

        staticText.SetSizerProps(halign='center')
        textInput.SetSizerProps(halign='center', expand=True)

        textInput.SetHelpText(helpText=helpText)

        return textInput

    def _bindControls(self):

        self._bindTextControl(textControl=self._nameInput,        callback=self._onValueChanged)
        self._bindTextControl(textControl=self._ownerEmailInput,  callback=self._onValueChanged)
        self._bindTextControl(textControl=self._descriptionInput, callback=self._onValueChanged)
        self._bindTextControl(textControl=self._keywordsInput,    callback=self._onValueChanged)

    def _bindTextControl(self, textControl: TextCtrl, callback: Callable):

        parent = self.GetParent()

        parent.Bind(EVT_TEXT,       callback, textControl)
        parent.Bind(EVT_TEXT_ENTER, callback, textControl)

    def _onValueChanged(self, event: CommandEvent):

        eventObject: TextCtrl = event.GetEventObject()
        value:       str      = event.GetString()
        if eventObject is self._nameInput:
            self._projectDetails.name = value
        elif eventObject is self._ownerEmailInput:
            self._projectDetails.ownerEmail = value
        elif eventObject is self._descriptionInput:
            self._projectDetails.description = value
        elif eventObject is self._keywordsInput:
            self._projectDetails.keywords = value
        else:
            assert False, 'Unknown event object'

        eventType  = event.GetEventType()
        self.logger.warning(f'{eventType=}')
        if eventType == wxEVT_TEXT_ENTER:
            focusMove: bool = self.NavigateIn()
            self.logger.warning(f'{focusMove=}')
