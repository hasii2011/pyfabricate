
from typing import cast

from wx import App
from wx import DEFAULT_FRAME_STYLE
from wx import Frame
from wx import ID_ANY
from wx import Panel
from wx import StaticText

from wx.lib.agw.buttonpanel import BoxSizer

from wx.lib.sized_controls import SizedFrame
from wx.lib.sized_controls import SizedPanel

WINDOW_WIDTH:  int = 400
WINDOW_HEIGHT: int = 200


class SizedPanelApp(App):

    def __init__(self):
        super().__init__()
        self._outerFrame: SizedFrame = cast(SizedFrame, None)

    def OnInit(self) -> bool:
        title:          str        = 'Demo Sized Panel in Panel'
        frameStyle:     int        = DEFAULT_FRAME_STYLE

        self._outerFrame = Frame(parent=None, id=ID_ANY, size=(WINDOW_WIDTH, WINDOW_HEIGHT), style=frameStyle, title=title)

        # This simulates a wizard page (which is a panel)
        mainPanel: Panel = Panel(parent=self._outerFrame)
        boxSizer:  BoxSizer = BoxSizer()
        mainPanel.SetSizer(boxSizer)

        # This simulates a component that is a sized panel
        sizedPanel: SizedPanel = SizedPanel(parent=mainPanel)       # This is problematic

        boxSizer.Add(sizedPanel)                                    # Fix it by doing this first
        sizedPanel.SetSizerType('vertical')
        #
        # this will cause a:
        #   File "<redacted>/pyenv-3.12.4/lib/python3.12/site-packages/wx/lib/sized_controls.py", line 183, in SetSizerProp
        #     flag = item.GetFlag()
        # AttributeError: 'NoneType' object has no attribute 'GetFlag'
        # OnInit returned false, exiting...
        #
        sizedPanel.SetSizerProps(expand=True, proportion=1)

        # noinspection PyUnusedLocal
        topLabel:    StaticText = StaticText(sizedPanel, ID_ANY, 'Top Label')
        # noinspection PyUnusedLocal
        bottomLabel: StaticText = StaticText(sizedPanel, ID_ANY, 'Bottom Label')

        self._outerFrame.Show(True)

        return True


testApp = SizedPanelApp()

testApp.MainLoop()
