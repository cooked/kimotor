import wx
import pcbnew
import os
#import logging
#import sys
#import time
import numpy as np
import math

class KiMotorDialog ( wx.Dialog ):
    
    def __init__( self, parent ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, 
                                title = u"KiMotor ", pos = wx.DefaultPosition, size = wx.Size( 300,500 ), 
                                style = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER )

        # Now create the Panel to put the other controls on.
        panel = wx.Panel(self)

        # and a few controls
        text = wx.StaticText(panel, -1, "Hello World!")
        text.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
        text.SetSize(text.GetBestSize())
        btn = wx.Button(panel, -1, "Close")
        funbtn = wx.Button(panel, -1, "Just for fun...")

        # bind the button events to handlers
        self.Bind(wx.EVT_BUTTON, self.OnTimeToClose, btn)
        self.Bind(wx.EVT_BUTTON, self.OnFunButton, funbtn)

        # Use a sizer to layout the controls, stacked vertically and with
        # a 10 pixel border around each
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(text, 0, wx.ALL, 10)
        sizer.Add(btn, 0, wx.ALL, 10)
        sizer.Add(funbtn, 0, wx.ALL, 10)
        panel.SetSizer(sizer)
        panel.Layout()


    def OnTimeToClose(self, evt):
        """Event handler for the button click."""
        print("See ya later!")
        self.Close()

    def OnFunButton(self, evt):
        """Event handler for the button click."""
        print("Having fun yet?")

class KiMotorPlugin(pcbnew.ActionPlugin):
    def defaults(self):
        self.name = "KiMotor - PCB motor stator design"
        self.category = "A descriptive category name"
        self.description = "KiMotor automates the design of parametric PCB motor stators used in axial-flux motors"
        self.show_toolbar_button = True # Optional, defaults to False
        self.icon_file_name = os.path.join(os.path.dirname(__file__), 'flexibility.png') # Optional, defaults to ""

    def Run( self ):
        board = pcbnew.GetBoard()
        group = pcbnew.PCB_GROUP(board)
        board.Add(group)

        poles = 6
        
        od = 100
        id = 50
        h = 40
        w = 20

        center = pcbnew.wxPointMM(50,50);


        ps = range(poles)
        for p in ps:
            
            th = 2*math.pi * p / poles;

            T0 = np.eye(3)
            T0[0] = 10 # shift it a bit

            R = np.array([
                    [math.cos(th),  -math.sin(th),  0],
                    [math.sin(th),  math.cos(th),   0],
                    [0,             0.,             1]])

            center = np.array([50, 50, 0])

            T = np.eye(3)
            T[:3, :3] = R
            T[:3] = center - np.matmul(R, center)

            T1 = np.matmul(T, T0)

            # Now draw a via at one end of the track
            via = pcbnew.PCB_VIA(board)
            via.SetPosition( pcbnew.wxPointMM(T1[0],T1[1]) )
            via.SetDrill(int(1 * 1e6))
            via.SetWidth(int(2 * 1e6))
            board.Add(via)
            group.AddItem(via)


        # Draw a track which goes from (100, 100) to (100, 110)
        #track = pcbnew.PCB_TRACK(board)
        #track.SetStart( pcbnew.wxPointMM(100,100) )
        #track.SetEnd( pcbnew.wxPointMM(100,110) )
        
        # Size here is specified as integer nanometers, so multiply mm by 1e6
        #track.SetWidth(int(0.3 * 1e6))
        #track.SetLayer(pcbnew.F_Cu)
        #board.Add(track)
        #group.AddItem(track)

        

KiMotorPlugin().register() # Instantiate and register to Pcbnew

