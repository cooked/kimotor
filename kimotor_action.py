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


    # solver
    def generate(self, board):

        # TODO: group stuff together
        #self.group = pcbnew.PCB_GROUP( self.board )
        #self.board.Add(self.group)
        
        # units [mm]
        poles = self.m_ctrlPoles.GetValue()
        loops = self.m_ctrlLoops.GetValue()
        trk_w = self.m_ctrlTrackWidth.GetValue()

        od = self.m_ctrlDout.GetValue()
        id = self.m_ctrlDin.GetValue()
        h = od*0.65 - id*0.65
        w = 20

        gap = trk_w * 4
        
        ps = range(poles)
        ls = range(loops)

        # trapez
        th0 = math.radians(360 / poles)
        s0 = math.sin(th0/2)
        t0 = math.tan(th0/2)

        # pole
        for p in ps:

            # coil
            fcu = []
            for l in ls:
                dw = (h-2*l*gap)*t0
                p1 = [id + l*gap,     -w/2]
                p2 = [id+h - l*gap,   -w/2 - dw]
                p3 = [id+h - l*gap,   w/2 + dw]
                p4 = [id + l*gap,     w/2]
                p5 = [id + l*gap,     -w/2 + gap/t0]

                # fcu layer
                fcu.extend([p1,p2])
                if 1:
                    pv = [id+h - l*gap + (w/2 + dw)*s0, 0]
                    fcu.extend([pv])
                fcu.extend([p3,p4,p5])

            # rotation matrix
            th = math.radians(360 / poles * p);
            c = math.cos(th)
            s = math.sin(th)
            R = np.array( [[c, -s],[s, c]] )

            fcum = np.matrix(fcu)

            # rotate
            Tf = np.matmul(R, fcum.transpose())
            Tf = Tf.transpose()

            # draw traces
            start = Tf[0]
            for tf in Tf[1:]:
                track = pcbnew.PCB_TRACK(board)
                track.SetWidth(int(trk_w * 1e6)) # Size here is specified as integer nanometers, so multiply mm by 1e6
                track.SetLayer(pcbnew.F_Cu)
                track.SetStart( pcbnew.wxPointMM( start[0,0].item(), start[0,1].item()) )
                track.SetEnd( pcbnew.wxPointMM( tf[0,0].item(), tf[0,1].item()) )
                board.Add(track)
                start = tf
            
            # TODO: logic for connecting layers
            # draw terminals 
            for t in [Tf[0],Tf[-1]]:
                via = pcbnew.PCB_VIA(board)
                via.SetPosition( pcbnew.wxPointMM( t[0,0].item(), t[0,1].item()) )
                via.SetDrill(int(trk_w / 2 * 1e6))
                via.SetWidth(int(trk_w * 1e6))
                board.Add(via)
                #group.AddItem(via)


        # board outline
        arc = pcbnew.PCB_SHAPE(board, pcbnew.SHAPE_T_ARC)
        arc.SetArcGeometry( 
            pcbnew.wxPointMM(od, 0.0),
            pcbnew.wxPointMM(-od,0.0),
            pcbnew.wxPointMM(od, 0.0))
        arc.SetLayer( pcbnew.Edge_Cuts )
        board.Add(arc)
        
        arc = pcbnew.PCB_SHAPE(board, pcbnew.SHAPE_T_ARC)
        arc.SetArcGeometry( 
            pcbnew.wxPointMM(id, 0.0),
            pcbnew.wxPointMM(-id,0.0),
            pcbnew.wxPointMM(id, 0.0))
        arc.SetLayer( pcbnew.Edge_Cuts )
        board.Add(arc)

        # update board
        pcbnew.Refresh()


class KiMotor(pcbnew.ActionPlugin):
    def defaults(self):
        self.name = "KiMotor - PCB motor stator design"
        self.category = "Modify Drawing PCB"
        self.description = "KiMotor automates the design of parametric PCB motor stators used in axial-flux motors"
        self.show_toolbar_button = True # Optional, defaults to False
        self.icon_file_name = os.path.join(os.path.dirname(__file__), 'flexibility.png') # Optional, defaults to ""

    def Run( self ):
        # grab editor frame and board
        self.frame = wx.FindWindowByName("PcbFrame")
        self.board = pcbnew.GetBoard()
        
        dlg = KiMotorDialog(self.frame, self.board)
        dlg.Show()
