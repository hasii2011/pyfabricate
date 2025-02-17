
from typing import Callable

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

from pyfabricate.ProjectDetails import ProjectDetails
from pyfabricate.steps.PageBase import PageBase
from pyfabricate.steps.Validator import validateEmail

STANDARD_LABEL_FONT_SIZE: int = 12


class ProjectDetailsStep(PageBase):

    def __init__(self, parent: SizedPanel, projectDetails: ProjectDetails):
        """

        Args:
            parent:           A parent panel
            projectDetails:   Some starter details
        """

        self.logger: Logger = getLogger(__name__)

        self._projectDetails: ProjectDetails = projectDetails

        super().__init__(parent=parent)

        self.SetSizerType('form')
        self._nameInput:        TextCtrl = self._createInputPair(label='Project Name:',        toolTip='The project name')
        self._moduleNameInput:  TextCtrl = self._createInputPair(label='Module Name:',         toolTip='The module name')
        self._ownerNameInput:   TextCtrl = self._createInputPair(label='Project Owner Name:',  toolTip='The boss')
        self._ownerEmailInput:  TextCtrl = self._createInputPair(label='Project Owner EMail:', toolTip='The owner email in pyproject.toml')
        self._descriptionInput: TextCtrl = self._createInputPair(label='Project Description:', toolTip='The project description')
        self._keywordsInput:    TextCtrl = self._createInputPair(label='Project Keywords:',    toolTip='Comma separated list of keywords')

        self._setControlValues()
        self._bindControls()

    @property
    def projectDetails(self) -> ProjectDetails:
        """
        This is only valid when ProjectDetailsStep.validate() return True

        Returns:  The control data
        """
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
                validateField(self._projectDetails.ownerName, 'owner name') is False or
                validateField(self._projectDetails.ownerEmail, 'eMail') is False or
                validateField(self._projectDetails.description, 'description') is False or
                validateField(self._projectDetails.keywords, 'Keywords') is False):
            valid = False
        elif validateEmail(self._projectDetails.ownerEmail) is False:
            eDlg = MessageDialog(parent=None, message=f'Incorrectly formatted email', caption='Invalid', style=OK | CENTER)
            eDlg.ShowModal()
            eDlg.Destroy()
            valid = False

        return valid

    def _createInputPair(self, label: str, toolTip: str = '') -> TextCtrl:

        staticText: StaticText = self._createLabel(label)
        textInput:  TextCtrl   = TextCtrl(parent=self, style=TE_PROCESS_ENTER, size=Size(width=275, height=-1))

        staticText.SetSizerProps(valign='center')
        textInput.SetSizerProps(halign='center', expand=True)

        textInput.SetToolTip(toolTip)

        return textInput

    def _bindControls(self):

        self._bindTextControl(textControl=self._nameInput,        callback=self._onValueChanged)
        self._bindTextControl(textControl=self._moduleNameInput,  callback=self._onValueChanged)
        self._bindTextControl(textControl=self._ownerNameInput,   callback=self._onValueChanged)
        self._bindTextControl(textControl=self._ownerEmailInput,  callback=self._onValueChanged)
        self._bindTextControl(textControl=self._descriptionInput, callback=self._onValueChanged)
        self._bindTextControl(textControl=self._keywordsInput,    callback=self._onValueChanged)

    def _setControlValues(self):

        self._nameInput.SetValue(self._projectDetails.name)
        self._moduleNameInput.SetValue(self._projectDetails.moduleName)
        self._ownerNameInput.SetValue(self._projectDetails.ownerName)
        self._ownerEmailInput.SetValue(self._projectDetails.ownerEmail)
        self._descriptionInput.SetValue(self._projectDetails.description)
        self._keywordsInput.SetValue(self._projectDetails.keywords)

    def _bindTextControl(self, textControl: TextCtrl, callback: Callable):

        parent = self.GetParent()

        parent.Bind(EVT_TEXT,       callback, textControl)
        parent.Bind(EVT_TEXT_ENTER, callback, textControl)

    def _onValueChanged(self, event: CommandEvent):

        eventObject: TextCtrl = event.GetEventObject()
        value:       str      = event.GetString()
        if eventObject is self._nameInput:
            self._projectDetails.name = value
            # Want them the same
            self._projectDetails.moduleName = value
            self._moduleNameInput.SetValue(value)
        elif eventObject is self._moduleNameInput:
            self._projectDetails.moduleName = value
        elif eventObject is self._ownerNameInput:
            self._projectDetails.ownerName = value
        elif eventObject is self._ownerEmailInput:
            self._projectDetails.ownerEmail = value
        elif eventObject is self._descriptionInput:
            self._projectDetails.description = value
        elif eventObject is self._keywordsInput:
            self._projectDetails.keywords = value
        else:
            assert False, 'Unknown event object'

        eventType  = event.GetEventType()
        self.logger.debug(f'{eventType=}')
        if eventType == wxEVT_TEXT_ENTER:
            focusMove: bool = self.NavigateIn()
            self.logger.debug(f'{focusMove=}')
