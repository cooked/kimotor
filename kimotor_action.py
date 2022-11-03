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
        self.generate2()
        event.Skip()

    def test_fill(self, t1,t2, fill):
 
        p = []
        p1 = []
        p2 = []

        #p, p1, p2 = kf.fillet(self.board, t1, t2, fill)
        
        kf.do_fillet(self.board, t1, t2, fill)

        via = pcbnew.PCB_VIA(self.board)
        via.SetPosition( pcbnew.wxPoint(p[0],p[1]) )
        via.SetDrill( int(self.trk_w/2) )
        via.SetWidth( int(self.trk_w) )
        self.board.Add(via)

        via = pcbnew.PCB_VIA(self.board)
        via.SetPosition( pcbnew.wxPoint(p1[0],p1[1]) )
        via.SetDrill( int(self.trk_w/2) )
        via.SetWidth( int(self.trk_w) )
        self.board.Add(via)

        via = pcbnew.PCB_VIA(self.board)
        via.SetPosition( pcbnew.wxPoint(p2[0],p2[1]) )
        via.SetDrill( int(self.trk_w/2) )
        via.SetWidth( int(self.trk_w) )
        self.board.Add(via)

    def generate2(self):
        
        shift = 150
        fill = int(10 * 1e6)

        trk_w = int( self.m_ctrlTrackWidth.GetValue() * 1e6)

        t10 = pcbnew.PCB_TRACK(self.board)
        t10.SetWidth( trk_w )
        t10.SetLayer( pcbnew.F_Cu )
        t10.SetStart( pcbnew.wxPointMM(50,50) )
        t10.SetEnd( pcbnew.wxPointMM(0,0) )
        self.board.Add(t10)

        t1 = pcbnew.PCB_TRACK(self.board)
        t1.SetWidth( trk_w )
        t1.SetLayer( pcbnew.F_Cu )
        t1.SetStart( pcbnew.wxPointMM(0,0) )
        t1.SetEnd( pcbnew.wxPointMM(100,0) )
        self.board.Add(t1)

        t12 = pcbnew.PCB_TRACK(self.board)
        t12.SetWidth( trk_w )
        t12.SetLayer( pcbnew.F_Cu )
        t12.SetStart( pcbnew.wxPointMM(100,0) )
        t12.SetEnd( pcbnew.wxPointMM(150,50) )
        self.board.Add(t12)

        self.test_fill(t10,t1, fill)
        self.test_fill(t1,t12, fill)
        


        t30 = pcbnew.PCB_TRACK(self.board)
        t30.SetWidth( trk_w )
        t30.SetLayer( pcbnew.F_Cu )
        t30.SetStart( pcbnew.wxPointMM(50,shift+10-50) )
        t30.SetEnd( pcbnew.wxPointMM(0,shift+10) )
        self.board.Add(t30)

        t3 = pcbnew.PCB_TRACK(self.board)
        t3.SetWidth( trk_w )
        t3.SetLayer( pcbnew.F_Cu )
        t3.SetStart( pcbnew.wxPointMM(0,shift+10) )
        t3.SetEnd( pcbnew.wxPointMM(100,shift+10) )
        self.board.Add(t3)

        t32 = pcbnew.PCB_TRACK(self.board)
        t32.SetWidth( trk_w )
        t32.SetLayer( pcbnew.F_Cu )
        t32.SetStart( pcbnew.wxPointMM(100,shift+10) )
        t32.SetEnd( pcbnew.wxPointMM(150,shift+10-50) )
        self.board.Add(t32)

        self.test_fill(t30,t3, fill)
        self.test_fill(t3,t32, fill)

        #p = kla.line_line_center(t30,t3, fill)
        
        #via = pcbnew.PCB_VIA(self.board)
        #via.SetPosition( pcbnew.wxPoint(p[0],p[1]) )
        #via.SetDrill( int(self.trk_w/2) )
        #via.SetWidth( int(self.trk_w) )
        #self.board.Add(via)

        #kf.fillet(self.board, t3, t32, fill)



        t2 = pcbnew.PCB_TRACK(self.board)
        t2.SetWidth( trk_w )
        t2.SetLayer( pcbnew.F_Cu )
        t2.SetStart( pcbnew.wxPointMM(shift,10) )
        t2.SetEnd( pcbnew.wxPointMM(shift+100,10) )
        self.board.Add(t2)

        t22 = pcbnew.PCB_ARC(self.board)
        t22.SetWidth( trk_w )
        t22.SetLayer( pcbnew.F_Cu )
        t22.SetStart( pcbnew.wxPointMM(shift+100,10) )
        t22.SetMid( pcbnew.wxPointMM(shift+120,50) )
        t22.SetEnd( pcbnew.wxPointMM(shift+100,100) )
        self.board.Add(t22)

        #kf.fillet(self.board, t2, t22, fill)


        #wx.LogWarning(f'angle: {math.degrees(a)}')

        #track3 = pcbnew.PCB_ARC(self.board)
        #track3.SetWidth( trk_w )
        #track3.SetLayer(pcbnew.F_Cu)
        #track3.SetStart( pcbnew.wxPointMM(0,100) )
        #track3.SetEnd( pcbnew.wxPointMM(0,50) )
        #track3.SetMid( pcbnew.wxPointMM(-25,75) )
        #self.board.Add(track3)

        #fill = self.fillet(track, track2, 10)
        #self.board.Add(fill)
        
        #kf.do_fillet(self.board, track, track2, 10*1e6)

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
        self.ro = int(self.m_ctrlDout.GetValue() * 1e6 / 2)
        self.ri = int(self.m_ctrlDin.GetValue() * 1e6 / 2)
        self.rb = int(self.m_ctrlDbore.GetValue() * 1e6 / 2)


        self.group = pcbnew.PCB_GROUP( self.board )
        self.board.Add(self.group)

        # generate coils
        coil_t = self.do_coils()
        # connect coils
        self.do_coils_terminals(coil_t)
        # place mounting holes
        self.do_mounts()
        # design the board edges
        self.do_outline()

        # update board
        pcbnew.Refresh()

        
    def do_coils(self):
        # TODO: proper implement arc, for now we split outer side in 2 segments
        use_arc = False

        rb = self.rb
        ro = self.ro
        ri = self.ri

        h = ro - ri
        
        try:
            if ri < rb*1.5:
                raise ValueError()
        except ValueError:
            wx.LogWarning('Coil inner side and shaft bore are too close. Must be D_in > 1.5*D_bore')
            return

        # TODO: set min distance depending on voltage?
        gap = self.trk_w * 4
        
        # trapez
        th0 = math.radians(360/self.poles)
        s0 = math.sin(th0/2)
        t0 = math.tan(th0/2)
        
        # limit coil base width (assume 1deg gap between coils base)
        dth = math.radians(0.5)
        # coil base half-width 
        w2 = 10 * 1e6 #ri * math.cos(th0/2 - dth)

        # coil
        fcu = []
        fcuv = []
        for l in range(self.loops):
            dw = (h-2*l*gap)*t0
            p1 = [ri + l*gap,     -w2/2]
            p2 = [ri+h - l*gap,   -w2/2 - dw]
            p3 = [ri+h - l*gap,   w2/2 + dw]
            p4 = [ri + l*gap,     w2/2]
            #p5 = [id + l*gap,  -w/2 + gap/t0]

            # fcu layer
            fcu.extend([p1,p2,p3,p4])

            # outer point (mid point of arc)
            #pv = [ri+h - l*gap + (w/2 + dw)*s0, 0]
            pv = [ri+h - l*gap + (w2 + dw)*s0 / 2, 0]
            fcuv.extend([pv])
        
        fcum = np.matrix(fcu)   # points, excl. arc mids
        fcuvm = np.matrix(fcuv) # arc mids only

        # coil terminals
        coil_t = []

        # poles
        for p in range(self.poles):

            # rotation matrix
            th = th0 * p;
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
            cs = pcbnew.wxPoint( int(start[0,0].item()), int(start[0,1].item()) )
            
            for idx, tf in enumerate(Tf[1:]):
                
                # start point, end point of track segment
                ps = pcbnew.wxPoint( int(start[0,0].item()), int(start[0,1].item()) )
                pe = pcbnew.wxPoint( int(tf[0,0].item()), int(tf[0,1].item()) ) 

                if not (idx-1)%4 :
                    # TODO: reimplement the arc at some point
                    #track = pcbnew.PCB_ARC(self.board)
                    #tfv = Tfv[iv]
                    #track.SetMid( pcbnew.wxPointMM( tfv[0,0].item(), tfv[0,1].item()) )
                    
                    tfv = Tfv[iv]
                    iv += 1
                    pm = pcbnew.wxPoint( int(tfv[0,0].item()), int(tfv[0,1].item()) )

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
                    fo = kf.do_fillet(self.board, track_p, track, self.r_flat)
                    self.board.Add(fo)
                    self.group.AddItem(fo)

                    if idx > 0:
                        f = kf.do_fillet(self.board, track0, track_p, self.r_fill)
                        self.board.Add(f)
                        self.group.AddItem(f)
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
                        f = kf.do_fillet(self.board, track0, track, self.r_fill)
                        self.board.Add(f)
                        self.group.AddItem(f)

                track0 = track
                start = tf
                
            # TODO: logic for connecting layers
            
            # store 2nd coil terminal
            ce = pcbnew.wxPoint( int(start[0,0].item()), int(start[0,1].item()) )
            coil_t.append([cs,ce])

        # pass coil terminals
        return coil_t

    def do_coils_terminals(self, coil_t):
        # start with a simple 6-pole, 3-phase connections
        # draw terminals 
        
        th0 = math.radians(360/self.poles)

        # spacing between connection rings
        dr = 4 * self.trk_w
        # spacing between bore edge and first rings
        dri = 3 * dr
        
        # coil terminals
        delta_c = []

        # rot adj (manual) to make jumper parallel to coil sides
        thadj = math.radians(10)

        for p in range(3):
            
            # concentric rings/arcs
            crb = self.rb + dri + p*dr
            cro = (self.ro + dri + p*dr) * 1.12

            # start, end, and mid angle
            ths = th0*p + thadj
            the = ths + 2/3*math.pi + thadj
            thm = (ths+the)/2

            # get coils terminals
            # TODO: generalize
            c1s, c1e = coil_t[p]
            c2s, c2e = coil_t[p+3]

            # inner rings
            rs = pcbnew.wxPoint( crb*math.cos(ths), crb*math.sin(ths) )
            re = pcbnew.wxPoint( crb*math.cos(the), crb*math.sin(the) )
            rm = pcbnew.wxPoint( crb*math.cos(thm), crb*math.sin(thm) )

            conn = pcbnew.PCB_ARC(self.board)
            conn.SetLayer(pcbnew.F_Cu)
            conn.SetWidth(self.trk_w)
            conn.SetStart( rs )
            conn.SetMid( rm )
            conn.SetEnd( re )
            self.board.Add(conn)
            self.group.AddItem(conn)

            # inner juncion start (opposite side)
            conn = pcbnew.PCB_TRACK(self.board)
            conn.SetLayer(pcbnew.B_Cu)
            conn.SetWidth(self.trk_w)
            conn.SetStart( c1s )
            conn.SetEnd( rs )
            self.board.Add(conn)
            self.group.AddItem(conn)

            via = pcbnew.PCB_VIA(self.board)
            via.SetPosition( c1s )
            via.SetDrill( int(self.trk_w/2) )
            via.SetWidth( int(self.trk_w) )
            self.board.Add(via)
            self.group.AddItem(via)

            via = pcbnew.PCB_VIA(self.board)
            via.SetPosition( rs )
            via.SetDrill( int(self.trk_w/2) )
            via.SetWidth( int(self.trk_w) )
            self.board.Add(via)
            self.group.AddItem(via)

            # inner juncion end (opposite side)
            conn = pcbnew.PCB_TRACK(self.board)
            conn.SetLayer(pcbnew.B_Cu)
            conn.SetWidth(self.trk_w)
            conn.SetStart( re )
            conn.SetEnd( c2s )
            self.board.Add(conn)
            self.group.AddItem(conn)

            via = pcbnew.PCB_VIA(self.board)
            via.SetPosition( re )
            via.SetDrill( int(self.trk_w/2) )
            via.SetWidth( int(self.trk_w) )
            self.board.Add(via)
            self.group.AddItem(via)

            via = pcbnew.PCB_VIA(self.board)
            via.SetPosition( c2s )
            via.SetDrill( int(self.trk_w/2) )
            via.SetWidth( int(self.trk_w) )
            self.board.Add(via)
            self.group.AddItem(via)


            # outer rings (motor terminals are the start of these arcs)
            the = ths + thadj
            ths = - (3-p) * math.radians(5) + thadj 
            thm = (ths+the)/2
            
            rs = pcbnew.wxPoint( cro*math.cos(ths), cro*math.sin(ths) )
            rm = pcbnew.wxPoint( cro*math.cos(thm), cro*math.sin(thm) )
            re = pcbnew.wxPoint( cro*math.cos(the), cro*math.sin(the) )

            conn = pcbnew.PCB_ARC(self.board)
            conn.SetLayer(pcbnew.F_Cu)
            conn.SetWidth(self.trk_w)
            conn.SetStart( rs )
            conn.SetMid( rm )
            conn.SetEnd( re )
            self.board.Add(conn)
            self.group.AddItem(conn)

            # inner juncion end (opposite side)
            conn = pcbnew.PCB_TRACK(self.board)
            conn.SetLayer(pcbnew.B_Cu)
            conn.SetWidth(self.trk_w)
            conn.SetStart( re )
            conn.SetEnd( c1e )
            self.board.Add(conn)
            self.group.AddItem(conn)

            via = pcbnew.PCB_VIA(self.board)
            via.SetPosition( re )
            via.SetDrill( int(self.trk_w/2) )
            via.SetWidth( int(self.trk_w) )
            self.board.Add(via)
            self.group.AddItem(via)

            via = pcbnew.PCB_VIA(self.board)
            via.SetPosition( c1e )
            via.SetDrill( int(self.trk_w/2) )
            via.SetWidth( int(self.trk_w) )
            self.board.Add(via)
            self.group.AddItem(via)


            # coil delta connection terminal
            via = pcbnew.PCB_VIA(self.board)
            via.SetPosition( c2e )
            via.SetDrill( int(self.trk_w/2) )
            via.SetWidth( int(self.trk_w) )
            self.board.Add(via)
            self.group.AddItem(via)

            # store terminal for the jummper track
            delta_c.append(c2e)

            # motor terminal
            via = pcbnew.PCB_VIA(self.board)
            via.SetPosition( rs )
            via.SetDrill( int(self.trk_w/2) )
            via.SetWidth( int(self.trk_w) )
            self.board.Add(via)
            self.group.AddItem(via)

            #wx.LogWarning(f'points: {c1s} {c2s}')

            #a_v = pcbnew.VECTOR2I(
            #   (a_e.x - a_s.x) * a_reverse,
            #    -(a_e.y - a_s.y) * a_reverse
            #)

        # create delta connection
        ths = th0 * 3 + thadj
        the = th0 * 5 + thadj
        thm = (the+ths)/2

        rs = pcbnew.wxPoint( cro*math.cos(ths), cro*math.sin(ths) )
        rm = pcbnew.wxPoint( cro*math.cos(thm), cro*math.sin(thm) )
        re = pcbnew.wxPoint( cro*math.cos(the), cro*math.sin(the) )

        conn = pcbnew.PCB_ARC(self.board)
        conn.SetLayer(pcbnew.F_Cu)
        conn.SetWidth(self.trk_w)
        conn.SetStart( rs )
        conn.SetMid( rm )
        conn.SetEnd( re )
        self.board.Add(conn)
        self.group.AddItem(conn)

        via = pcbnew.PCB_VIA(self.board)
        via.SetPosition( rs )
        via.SetDrill( int(self.trk_w/2) )
        via.SetWidth( int(self.trk_w) )
        self.board.Add(via)
        self.group.AddItem(via)

        via = pcbnew.PCB_VIA(self.board)
        via.SetPosition( rm )
        via.SetDrill( int(self.trk_w/2) )
        via.SetWidth( int(self.trk_w) )
        self.board.Add(via)
        self.group.AddItem(via)

        via = pcbnew.PCB_VIA(self.board)
        via.SetPosition( re )
        via.SetDrill( int(self.trk_w/2) )
        via.SetWidth( int(self.trk_w) )
        self.board.Add(via)
        self.group.AddItem(via)

        
        conn = pcbnew.PCB_TRACK(self.board)
        conn.SetLayer(pcbnew.B_Cu)
        conn.SetWidth(self.trk_w)
        conn.SetStart( rs )
        conn.SetEnd( delta_c[0] )
        self.board.Add(conn)
        self.group.AddItem(conn)

        conn = pcbnew.PCB_TRACK(self.board)
        conn.SetLayer(pcbnew.B_Cu)
        conn.SetWidth(self.trk_w)
        conn.SetStart( rm )
        conn.SetEnd( delta_c[1] )
        self.board.Add(conn)
        self.group.AddItem(conn)

        conn = pcbnew.PCB_TRACK(self.board)
        conn.SetLayer(pcbnew.B_Cu)
        conn.SetWidth(self.trk_w)
        conn.SetStart( re )
        conn.SetEnd( delta_c[2] )
        self.board.Add(conn)
        self.group.AddItem(conn)

        return 0

    def do_thermal(self):
        # TODO:
        return 0

    def do_mounts(self):
        # TODO:
        return 0

    def do_outline(self):
        
        ro = 1.24 * self.ro

        arc = pcbnew.PCB_SHAPE(self.board, pcbnew.SHAPE_T_ARC)
        arc.SetArcGeometry( 
            pcbnew.wxPoint( ro, 0),
            pcbnew.wxPoint( -ro, 0),
            pcbnew.wxPoint( ro,  0))
        arc.SetLayer( pcbnew.Edge_Cuts )
        self.board.Add(arc)
        self.group.AddItem(arc)
        
        arc = pcbnew.PCB_SHAPE(self.board, pcbnew.SHAPE_T_ARC)
        arc.SetArcGeometry( 
            pcbnew.wxPoint( self.rb, 0),
            pcbnew.wxPoint( -self.rb, 0),
            pcbnew.wxPoint( self.rb, 0))
        arc.SetLayer( pcbnew.Edge_Cuts )
        self.board.Add(arc)
        self.group.AddItem(arc)


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
