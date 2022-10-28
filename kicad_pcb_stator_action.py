import wx
#import tkinter as tk
import threading

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
        self.category = "Modify Drawing PCB"
        self.description = "KiMotor automates the design of parametric PCB motor stators used in axial-flux motors"
        self.show_toolbar_button = True # Optional, defaults to False
        self.icon_file_name = os.path.join(os.path.dirname(__file__), 'flexibility.png') # Optional, defaults to ""

    def Run( self ):
        board = pcbnew.GetBoard()
        group = pcbnew.PCB_GROUP(board)
        board.Add(group)

        # units [mm]
        poles = 6
        loops = 2
        trk_w = 1

        od = 100
        id = 30
        h = 40
        w = 20

        gap = 2 

        ps = range(poles)
        ls = range(loops)

        # trapez
        th0 = math.radians(360 / poles)
        dw = (h+id) * math.sin(th0) 

        # pole
        for p in ps:

            # rotation matrix
            th = math.radians(360 / poles * p);
            c = math.cos(th)
            s = math.sin(th)
            R = np.array( [[c, -s],[s, c]] )

            # coil
            pa = []
            for l in ls:
                p1 = [id + l*gap,   -w/2 + l*gap]
                p2 = [id+h - l*gap, -w/2 + l*gap]
                p3 = [id+h - l*gap, w/2 - dw - l*gap]
                p4 = [id + l*gap,   w/2 + dw - l*gap]
                p5 = [id + l*gap,   -w/2 + (l+1) * gap]
                pa.extend([p1,p2,p3,p4,p5])

            pm = np.matrix(pa)

            # rotate
            T = np.matmul(R, pm.transpose())
            T = T.transpose()

            # draw track
            start = T[0]
            for t in T[1:]:
                track = pcbnew.PCB_TRACK(board)
                track.SetWidth(int(1 * 1e6)) # Size here is specified as integer nanometers, so multiply mm by 1e6
                track.SetLayer(pcbnew.F_Cu)
                track.SetStart( pcbnew.wxPointMM( start[0,0].item(), start[0,1].item()) )
                track.SetEnd( pcbnew.wxPointMM( t[0,0].item(), t[0,1].item()) )
                board.Add(track)
                #group.AddItem(track)
                start = t
            
            # draw terminals 
            for t in [T[0],T[-1]]:
                via = pcbnew.PCB_VIA(board)
                via.SetPosition( pcbnew.wxPointMM( t[0,0].item(), t[0,1].item()) )
                via.SetDrill(int(trk_w / 2 * 1e6))
                via.SetWidth(int(trk_w * 1e6))
                board.Add(via)
                #group.AddItem(via)

# class KiMotorTk(pcbnew.ActionPlugin):
#     def defaults(self):
#         self.name = "KiMotor - PCB motor stator design"
#         self.category = "Modify Drawing PCB"
#         self.description = ""
#         self.show_toolbar_button = True # Optional, defaults to False
#         self.icon_file_name = os.path.join(os.path.dirname(__file__), 'flexibility.png') # Optional, defaults to ""

#     def Run(self):
#         root = tk.Tk()
#         root.wm_attributes("-topmost", "true")
#         #root.withdraw()
#         #root.update_idletasks()
#         #root.grab_set()
#         greeting = tk.Label(text="Hello, Tkinter")
#         greeting.pack()

#         root.mainloop()

#             #mb = tkMessageBox.showerror("Replicate layout", "Error while registering plugin.\nMost likely Wxpython is not supported with this KiCad build.")
#             #root.destroy()
#         #t = threading.Thread(target=messagebox_task)
#         #t.start()
#         #t.join()


KiMotorPlugin().register() # Instantiate and register to Pcbnew

