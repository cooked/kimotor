import wx
import pcbnew
import os
import numpy as np
import math

if __name__ == '__main__':
    import kimotor_gui
else:
    from . import kimotor_gui

class KiMotorDialog ( kimotor_gui.KiMotorGUI ):
     
    def __init__(self,  parent, board):
        kimotor_gui.KiMotorGUI.__init__(self, parent)
        self.board = board
    
    # event handlers
    def on_btn_generate(self, event):
        #self.logger.info("Generate stator coils")
        self.generate(self.board)
        event.Skip()

    def on_btn_clear(self, event):
        #self.logger.info("Cleared existing coils")
        #logging.shutdown()
        #self.Close()
        event.Skip()

    def generate2(self, board):
        
        trk_w = self.m_ctrlTrackWidth.GetValue()

        track = pcbnew.PCB_ARC(board)
        track.SetWidth(int(trk_w * 1e6)) # Size here is specified as integer nanometers, so multiply mm by 1e6
        track.SetLayer(pcbnew.F_Cu)
        track.SetStart( pcbnew.wxPointMM(0,0) )
        track.SetMid( pcbnew.wxPointMM(50,50) )
        track.SetEnd( pcbnew.wxPointMM(100,0) )
        board.Add(track)

        # update board
        pcbnew.Refresh()


    def generate(self, board):

        self.group = pcbnew.PCB_GROUP( self.board )
        self.board.Add(self.group)
        
        # units [mm]
        poles = self.m_ctrlPoles.GetValue()
        loops = self.m_ctrlLoops.GetValue()
        trk_w = self.m_ctrlTrackWidth.GetValue()

        do = self.m_ctrlDout.GetValue()
        di = self.m_ctrlDin.GetValue()
        db = self.m_ctrlDbore.GetValue()
        ro = do
        ri = di
        h = (ro - ri)/2
        w = 20
        
        try:
            if di < db*1.5:
                raise ValueError()
        except ValueError:
            wx.LogWarning('Coil inner side and shaft bore are too close. Must be D_in > 1.5*D_bore')
            return
            
        gap = trk_w * 4
        
        ps = range(poles)
        ls = range(loops)

        # trapez
        th0 = math.radians(360 / poles)
        s0 = math.sin(th0/2)
        t0 = math.tan(th0/2)
        
        # coil
        fcu = []
        fcuv = []
        for l in ls:
            dw = (h-2*l*gap)*t0
            p1 = [ri + l*gap,     -w/2]
            p2 = [ri+h - l*gap,   -w/2 - dw]
            p3 = [ri+h - l*gap,   w/2 + dw]
            p4 = [ri + l*gap,     w/2]
            #p5 = [id + l*gap,  -w/2 + gap/t0]

            # fcu layer
            fcu.extend([p1,p2,p3,p4])

            # outer point (mid point of arc)
            #pv = [ri+h - l*gap + (w/2 + dw)*s0, 0]
            pv = [ri+h - l*gap + (w/2 + dw)*s0 / 2, 0]
            fcuv.extend([pv])
        
        fcum = np.matrix(fcu)   # points, excl. arc mids
        fcuvm = np.matrix(fcuv) # arc mids only

        # rotate pole
        for p in ps:

            # rotation matrix
            th = math.radians(360 / poles * p);
            c = math.cos(th)
            s = math.sin(th)
            R = np.array( [[c, -s],[s, c]] )

            Tf = np.matmul(R, fcum.transpose())
            Tf = Tf.transpose()

            Tfv = np.matmul(R, fcuvm.transpose())
            Tfv = Tfv.transpose()

            # draw traces
            start = Tf[0]
            iv = 0
            for idx, tf in enumerate(Tf[1:]):
                
                if not (idx-1)%4 :
                    track = pcbnew.PCB_ARC(board)
                    tfv = Tfv[iv]
                    track.SetMid( pcbnew.wxPointMM( tfv[0,0].item(), tfv[0,1].item()) )
                    iv += 1
                else:
                    track = pcbnew.PCB_TRACK(board)    
                
                track.SetWidth(int(trk_w * 1e6)) # Size here is specified as integer nanometers, so multiply mm by 1e6
                track.SetLayer(pcbnew.F_Cu)
                track.SetStart( pcbnew.wxPointMM( start[0,0].item(), start[0,1].item()) )
                track.SetEnd( pcbnew.wxPointMM( tf[0,0].item(), tf[0,1].item()) )
                board.Add(track)
                self.group.AddItem(track)
                start = tf



            # TODO: logic for connecting layers
            # draw terminals 
            for t in [Tf[0],Tf[-1]]:
                via = pcbnew.PCB_VIA(board)
                via.SetPosition( pcbnew.wxPointMM( t[0,0].item(), t[0,1].item()) )
                via.SetDrill(int(trk_w / 2 * 1e6))
                via.SetWidth(int(trk_w * 1e6))
                board.Add(via)
                self.group.AddItem(via)


        # board outline
        arc = pcbnew.PCB_SHAPE(board, pcbnew.SHAPE_T_ARC)
        arc.SetArcGeometry( 
            pcbnew.wxPointMM(do, 0.0),
            pcbnew.wxPointMM(-do,0.0),
            pcbnew.wxPointMM(do, 0.0))
        arc.SetLayer( pcbnew.Edge_Cuts )
        board.Add(arc)
        self.group.AddItem(arc)
        
        arc = pcbnew.PCB_SHAPE(board, pcbnew.SHAPE_T_ARC)
        arc.SetArcGeometry( 
            pcbnew.wxPointMM(db, 0.0),
            pcbnew.wxPointMM(-db,0.0),
            pcbnew.wxPointMM(db, 0.0))
        arc.SetLayer( pcbnew.Edge_Cuts )
        board.Add(arc)
        self.group.AddItem(arc)

        # update board
        pcbnew.Refresh()


class KiMotor(pcbnew.ActionPlugin):
    def defaults(self):
        self.name = "KiMotor"
        self.category = "Modify Drawing PCB"
        self.description = "KiMotor - Design of parametric axial-flux motor stators"
        self.show_toolbar_button = True # Optional, defaults to False
        self.icon_file_name = os.path.join(os.path.dirname(__file__), 'flexibility.png') # Optional, defaults to ""

    def Run( self ):
        # grab editor frame and board
        self.frame = wx.FindWindowByName("PcbFrame")
        self.board = pcbnew.GetBoard()
        
        dlg = KiMotorDialog(self.frame, self.board)
        dlg.Show()
