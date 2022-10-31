import wx
import pcbnew
import os
import numpy as np
import math

if __name__ == '__main__':
    import kimotor_gui
    import kimotor_fillet as kf
    import kimotor_linalg as kla
else:
    from . import kimotor_gui
    from . import kimotor_fillet as kf
    from . import kimotor_linalg as kla

class KiMotorDialog ( kimotor_gui.KiMotorGUI ):
     
    def __init__(self,  parent, board):
        kimotor_gui.KiMotorGUI.__init__(self, parent)
        self.board = board

        self.poles = 0
        self.loops = 0
        self.trk_w = 0
        self.r_fill = 0
        self.r_flat = 0
        self.do = 0
        self.di = 0
        self.db = 0

    # event handlers
    def on_btn_clear(self, event):
        #self.logger.info("Cleared existing coils")
        #logging.shutdown()
        #self.Close()
        event.Skip()

    def on_btn_generate(self, event):
        #self.logger.info("Generate stator coils")
        self.generate()
        event.Skip()

    def generate2(self):
        
        trk_w = self.m_ctrlTrackWidth.GetValue()
        fillet = 10

        track = pcbnew.PCB_TRACK(self.board)
        track.SetWidth( int(trk_w * 1e6) )
        track.SetLayer( pcbnew.F_Cu )
        track.SetStart( pcbnew.wxPointMM(0,0) )
        track.SetEnd( pcbnew.wxPointMM(100,0) )
        self.board.Add(track)

        #track2 = pcbnew.PCB_ARC(self.board)
        track2 = pcbnew.PCB_TRACK(self.board)
        track2.SetWidth(int(trk_w * 1e6))
        track2.SetLayer(pcbnew.F_Cu)
        track2.SetStart( pcbnew.wxPointMM(100,0) )
        #track2.SetEnd( pcbnew.wxPointMM(100,-100) )
        #track2.SetMid( pcbnew.wxPointMM(120,-50) )
        track2.SetEnd( pcbnew.wxPointMM(100,100) )
        #track2.SetMid( pcbnew.wxPointMM(120,50) )
        self.board.Add(track2)

        #wx.LogWarning(f'angle: {math.degrees(a)}')

        #track3 = pcbnew.PCB_ARC(self.board)
        #track3.SetWidth(int(trk_w * 1e6))
        #track3.SetLayer(pcbnew.F_Cu)
        #track3.SetStart( pcbnew.wxPointMM(0,100) )
        #track3.SetEnd( pcbnew.wxPointMM(0,50) )
        #track3.SetMid( pcbnew.wxPointMM(-25,75) )
        #self.board.Add(track3)

        #fill = self.fillet(track, track2, 10)
        #self.board.Add(fill)
        
        kf.do_fillet(self.board, track, track2, 10*1e6)

        #fill2 = self.fillet(track2, track3, 10)
        #self.board.Add(fill2)
        #self.do_fillet(track2, track3, 10*1e6)

        # update board
        pcbnew.Refresh()

    def generate(self):

        # get gui values
        # units (mm converted to nm sometimes)
        self.poles = int(self.m_ctrlPoles.GetValue())
        self.loops = int(self.m_ctrlLoops.GetValue())
        self.trk_w = int(self.m_ctrlTrackWidth.GetValue() * 1e6)
        self.r_fill = int(self.m_ctrlRfill.GetValue() * 1e6)
        self.r_flat = int(self.m_ctrlRflatt.GetValue() * 1e6)

        self.do = self.m_ctrlDout.GetValue()
        self.di = self.m_ctrlDin.GetValue()
        self.db = self.m_ctrlDbore.GetValue()


        # generate coils
        coil_t = self.do_coils()
        # connect coils
        self.do_coils_terminals(coil_t)
        # connect motor terminals
        self.do_motor_terminals()
        # place mounting holes
        self.do_mounts()

        #wx.LogWarning(f'Coils: \n {coils_t}')
        
    def do_coils(self):
        # TODO: proper implement arc, for now we split outer side in 2 segments
        use_arc = False

        self.group = pcbnew.PCB_GROUP( self.board )
        self.board.Add(self.group)
        
        ro = self.do
        ri = self.di
        h = (ro - ri)/2
        w = 20
        
        try:
            if self.di < self.db*1.5:
                raise ValueError()
        except ValueError:
            wx.LogWarning('Coil inner side and shaft bore are too close. Must be D_in > 1.5*D_bore')
            return

        # TODO: set min distance depending on voltage?
        gap = self.m_ctrlTrackWidth.GetValue() * 4
        
        ps = range(self.poles)
        ls = range(self.loops)

        # trapez
        th0 = math.radians(360/self.poles)
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

        # coil terminals
        coil_t = []

        # poles
        for p in ps:

            # rotation matrix
            th = math.radians(360 / self.poles * p);
            c = math.cos(th)
            s = math.sin(th)
            R = np.array( [[c, -s],[s, c]] )

            Tf = np.matmul(R, fcum.transpose())
            Tf = Tf.transpose()

            Tfv = np.matmul(R, fcuvm.transpose())
            Tfv = Tfv.transpose()

            # draw tracks
            start = Tf[0]
            iv = 0
            
            # store 1st coil terminal
            cs = pcbnew.wxPointMM( start[0,0].item(), start[0,1].item())
            
            for idx, tf in enumerate(Tf[1:]):
                
                # points
                ps = pcbnew.wxPointMM( start[0,0].item(), start[0,1].item())
                pe = pcbnew.wxPointMM( tf[0,0].item(), tf[0,1].item()) 

                if not (idx-1)%4 :
                    # TODO: reimplement the arc at some point
                    #track = pcbnew.PCB_ARC(self.board)
                    #tfv = Tfv[iv]
                    #track.SetMid( pcbnew.wxPointMM( tfv[0,0].item(), tfv[0,1].item()) )
                    
                    tfv = Tfv[iv]
                    iv += 1
                    pm = pcbnew.wxPointMM( tfv[0,0].item(), tfv[0,1].item())

                    # first segment of outer side of coil
                    track_p = pcbnew.PCB_TRACK(self.board)
                    track_p.SetWidth( self.trk_w )
                    track_p.SetLayer(pcbnew.F_Cu)
                    track_p.SetStart( ps )
                    track_p.SetEnd( pm )
                    self.board.Add(track_p)
                    self.group.AddItem(track_p)

                    track = pcbnew.PCB_TRACK(self.board)
                    track.SetWidth( self.trk_w )
                    track.SetLayer(pcbnew.F_Cu)
                    track.SetStart( pm )
                    track.SetEnd( pe )
                    self.board.Add(track)
                    self.group.AddItem(track)

                    # fillet (outer coil corner)
                    kf.do_fillet(self.board, track_p, track, self.r_flat)

                    if idx > 0:
                        kf.do_fillet(self.board, track0, track_p, self.r_fill)

                else:
                    track = pcbnew.PCB_TRACK(self.board)    
                    track.SetWidth( self.trk_w )
                    track.SetLayer(pcbnew.F_Cu)
                    track.SetStart( ps )
                    track.SetEnd( pe )
                    self.board.Add(track)
                    self.group.AddItem(track)
                    
                    # fillet (all coil corners, but outer)
                    if idx > 0:
                        kf.do_fillet(self.board, track0, track, self.r_fill)
                
                track0 = track
                start = tf
                
            # TODO: logic for connecting layers
            

            # store 2nd coil terminal
            ce = pcbnew.wxPointMM( start[0,0].item(), start[0,1].item())
            coil_t.append([cs,ce])

        #
        # board edges
        #
        # create the stator outline
        #arc = pcbnew.PCB_SHAPE(board)
        #arc.SetShape(pcbnew.SHAPE_T_ARC)
        cx = 0
        cy = 0

        #arc = pcbnew.PCB_SHAPE(self.board, pcbnew.SHAPE_T_CIRCLE)
        #arc.SetFilled(False)
        #arc.SetStart( pcbnew.wxPointMM( cx,cy) )
        #arc.SetEnd( pcbnew.wxPointMM( cx+do/2,cy ))
        #arc.SetCenter(pcbnew.wxPointMM(CENTER_X, CENTER_Y))
        
        arc = pcbnew.PCB_SHAPE(self.board, pcbnew.SHAPE_T_ARC)
        arc.SetArcGeometry( 
            pcbnew.wxPointMM(self.do/2,  0.0),
            pcbnew.wxPointMM(-self.do/2, 0.0),
            pcbnew.wxPointMM(self.do/2,  0.0))
        arc.SetLayer( pcbnew.Edge_Cuts )
        self.board.Add(arc)
        self.group.AddItem(arc)
        
        arc = pcbnew.PCB_SHAPE(self.board, pcbnew.SHAPE_T_ARC)
        arc.SetArcGeometry( 
            pcbnew.wxPointMM(self.db, 0.0),
            pcbnew.wxPointMM(-self.db,0.0),
            pcbnew.wxPointMM(self.db, 0.0))
        arc.SetLayer( pcbnew.Edge_Cuts )
        self.board.Add(arc)
        self.group.AddItem(arc)

        # update board
        pcbnew.Refresh()

        # pass coil terminals
        return coil_t

    def do_coils_terminals(self, coil_t):
        # start with a simple 6-pole, 3-phase connections
        # draw terminals 
        #for t in [Tf[0],Tf[-1]]:
        #    via = pcbnew.PCB_VIA(self.board)
        #    via.SetPosition( pcbnew.wxPointMM( t[0,0].item(), t[0,1].item()) )
        #    via.SetDrill( int(trk_w/2) )
        #    via.SetWidth( int(trk_w) )
        #    self.board.Add(via)
        #    self.group.AddItem(via)
        
        #wx.LogWarning(f'coil: {coil_t}')
        ps = range(p)

        for p in ps:

            # rotation matrix
            th = math.radians(360 / self.poles * p);
            c = math.cos(th)
            s = math.sin(th)
            R = np.array( [[c, -s],[s, c]] )

            #Tf = np.matmul(R, fcum.transpose())
            #Tf = Tf.transpose()

            #Tfv = np.matmul(R, fcuvm.transpose())
            #Tfv = Tfv.transpose()

            # draw tracks
            #start = Tf[0]
            #iv = 0

        return 0

    def do_motor_terminals(self):
        return 0

    def do_mounts(self):
        return 0

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
