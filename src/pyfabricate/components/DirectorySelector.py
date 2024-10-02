
from logging import Logger
from logging import getLogger

from wx import ALIGN_CENTER
from wx import BoxSizer
from wx import CommandEvent
from wx import DD_DEFAULT_STYLE
from wx import DirDialog
from wx import EVT_BUTTON

from wx import HORIZONTAL
from wx import ID_ANY
from wx import ID_OK
from wx import Panel
from wx import TextCtrl

from wx.lib.buttons import GenBitmapButton

# from wx.lib.sized_controls import SizedPanel

from pyfabricate.resources.images import folder as ImgFolder


# class DirectorySelector(SizedPanel):
class DirectorySelector(Panel):
    """
    I have to use a traditional sizer because WizardPageSimple
    is a panel, not a SizedPanel and Wizard is a Dialog, not a SizedDialg
    """
    def __init__(self, *args, **kwargs):

        self.logger: Logger = getLogger(__name__)
        super().__init__(*args, **kwargs)

        boxSizer:  BoxSizer = BoxSizer()
        boxSizer.SetOrientation(HORIZONTAL)
        self.SetSizer(boxSizer)

        textCtrl: TextCtrl = TextCtrl(self)

        selectButton: GenBitmapButton = GenBitmapButton(self, ID_ANY, ImgFolder.embeddedImage.GetBitmap())

        textCtrl.SetValue('')
        textCtrl.SetEditable(False)

        boxSizer.Add(textCtrl,     proportion=5, flag=ALIGN_CENTER)
        boxSizer.AddSpacer(2)
        boxSizer.Add(selectButton, proportion=1)

        self._textDiagramsDirectory = textCtrl
        self._directoryPath: str = ''

        self.Bind(EVT_BUTTON, self._onSelectDiagramsDirectory, selectButton)

    @property
    def directoryPath(self):
        return self._directoryPath

    @directoryPath.setter
    def directoryPath(self, value: str):
        self._directoryPath = value

    # noinspection PyUnusedLocal
    def _onSelectDiagramsDirectory(self, event: CommandEvent):

        with DirDialog(None, 'Choose the Diagrams Directory', style=DD_DEFAULT_STYLE) as dlg:

            if dlg.ShowModal() == ID_OK:
                self._directoryPath = dlg.GetPath()
                self._textDiagramsDirectory.SetValue(self._directoryPath)
