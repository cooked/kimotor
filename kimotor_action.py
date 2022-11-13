import wx
import pcbnew
import os
import numpy as np
import math
import json

if __name__ == '__main__':
    import kimotor_gui
    import kimotor_fillet as kf
    import kimotor_linalg as kla
else:
    from . import kimotor_gui
    from . import kimotor_fillet as kf
    from . import kimotor_linalg as kla

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

class KiMotorDialog ( kimotor_gui.KiMotorGUI ):
    
    SCALE = 1e6

    def __init__(self,  parent, board):
        kimotor_gui.KiMotorGUI.__init__(self, parent)
        self.board = board

        self.init_parameters()

        # init library paths and other config items
        self.init_config()

        self.init_nets()


    def generate(self):

        self.group = pcbnew.PCB_GROUP( self.board )
        self.board.Add(self.group)

        ro = self.ro - self.w_mnt - self.w_trm

        # generate coils
        coil_t = self.do_coils(self.nl, ro)

        # connect coils
        ext_t, int_t = self.do_races(self.dr, ro, self.ri)
        self.do_junctions( coil_t, ext_t, int_t)
        #self.do_terminals_motor( trm_t )

        #self.do_coils_terminals(coil_t, self.dr, 3*self.dr)
        
        # place mounting holes
        self.do_mounts()
        
        # design the board edges
        self.do_outline( self.ro, self.rb )
        
        # thermal zones
        self.do_thermal()
        
        # draw silks
        #self.do_silk()

        # update board
        pcbnew.Refresh()

    # initializers
    def init_config(self):
        # init paths
        settings = pcbnew.SETTINGS_MANAGER_GetUserSettingsPath()
        with open(settings+'/kicad_common.json', 'r') as f:
            data = json.load(f)
            
            self.fp_path = data['environment']['vars']['KICAD6_FOOTPRINT_DIR']

    def init_nets(self):
        # init paths
        nitem = pcbnew.NETINFO_ITEM(self.board, "gnd")
        self.board.Add(nitem)

    def init_parameters(self):
        # get gui values and fix units (mm converted to nm where needed)
        self.nl     = int(self.m_ctrlLayers.GetValue())
        self.poles  = int(self.m_ctrlPoles.GetValue())
        self.loops  = int(self.m_ctrlLoops.GetValue())

        self.trk_w = int(self.m_ctrlTrackWidth.GetValue() * self.SCALE) # track width
        self.dr = self.trk_w * 2                                        # track distance
        self.r_fill = int(self.m_ctrlRfill.GetValue() * self.SCALE)
        
        self.ro = int(self.m_ctrlDout.GetValue() /2 * self.SCALE)
        self.w_mnt = int(self.m_ctrlWmnt.GetValue() * self.SCALE)
        self.w_trm = int(self.m_ctrlWtrm.GetValue() * self.SCALE)

        self.ri = int(self.m_ctrlDin.GetValue() /2 * self.SCALE )
        self.rb = int(self.m_ctrlDbore.GetValue() /2 * self.SCALE)

        self.mhon = int(self.m_mhOut.GetValue())
        self.mhor = int(self.m_mhOutR.GetValue() /2 * self.SCALE)
        self.mhin = int(self.m_mhIn.GetValue())
        self.mhir = int(self.m_mhInR.GetValue() /2 * self.SCALE)

        self.d_drill = int(0.2 * self.SCALE)   # min drill size


    def update_lset(self):
        self.layset = [pcbnew.F_Cu]
        if self.nl >= 4:
            self.layset.append(pcbnew.In1_Cu)
            self.layset.append(pcbnew.In2_Cu) 
        if self.nl == 6:
            self.layset.append(pcbnew.In3_Cu)
            self.layset.append(pcbnew.In4_Cu)
        self.layset.append(pcbnew.B_Cu) 

    # compute the coil points
    def coil_solver(self, r1,r2, dr0, dr,th,turns,dir):
        # r1, r2: inner radius, outer radius
        # dr0: coil-coil gap
        # dr: turn-turn gap
        # th: coil trapez angle
        # turns: nr of coil turns
        # dir: coil direction, 0: CW (normal), 1: CCW (reverse)
 
        pts = []
        mds = []

        # points 
        c = [0,0,0]
        l0 = np.array([ c, [r1*math.cos(th/2), r1*math.sin(th/2), 0] ])
        l0 = kla.line_offset(l0, -dr0)

        for l in range(turns):
            # offset line
            lr = kla.line_offset(l0, -l*dr)
            # solve corners
            pc1 = kla.circle_line_intersect(lr, c, r1+l*dr)
            pc1 = pc1[0:2]
            pc2 = kla.circle_line_intersect(lr, c, r2-l*dr)
            pc2 = pc2[0:2]
            pc3 = np.array([ pc2[0],-pc2[1] ])
            pc4 = np.array([ pc1[0],-pc1[1] ])
            # solve outer mid point
            pm = np.array([ r2-l*dr, 0 ])
            
            # coil direction
            if dir == 0:
                pts.extend([pc1, pc2, pc3, pc4])
            else:
                pts.extend([pc4, pc3, pc2, pc1])
            
            mds.extend([pm])

        pm = np.matrix(pts)   # points, excl. arc mids
        mm = np.matrix(mds) # arc mids only

        return pm, mm

    # convert coil points to tracks
    def coil_tracker(self, Tf, Tfv, layer):

        start_index = 1 if layer==0 else 0

        # draw tracks
        startf = Tf[start_index]
        iv = 0
        
        # store 1st coil terminal
        cs = pcbnew.wxPoint( int(startf[0,0]), int(startf[0,1]) )
        
        for idx, tf in enumerate(Tf[start_index+1:]):
            
            # start point, end point of track segment
            ps = pcbnew.wxPoint( int(startf[0,0]), int(startf[0,1]) )
            pe = pcbnew.wxPoint( int(tf[0,0]), int(tf[0,1]) ) 

            # use arc for the coil outer side
            idx_shift = 1 if start_index==0 else 0
            if not (idx-idx_shift)%4:
                t = pcbnew.PCB_ARC(self.board)
                tfv = Tfv[iv]
                iv += 1
                mp = pcbnew.wxPoint( tfv[0,0], tfv[0,1] )
                t.SetMid( mp )
            else:
                t = pcbnew.PCB_TRACK(self.board)    
            
            t.SetWidth( self.trk_w )
            t.SetLayer( layer )
            t.SetStart( ps )
            t.SetEnd( pe )
            self.board.Add(t)
            self.group.AddItem(t)
            
            # fillet
            if idx > 0 and self.r_fill > 0:
                kf.fillet(self.board, track0f, t, self.r_fill)

            track0f = t    
            startf = tf

            # trim coil if last outer side
            if iv == len(Tfv):
                nm = kla.track_arc_trim(t, mp)
                t.SetEnd( mp )
                t.SetMid( nm )
                track0f = t
                break
        
        ce = track0f.GetEnd()

        return [cs, ce] 

    # run the coil task
    def do_coils(self, ln, ro):
        # ln: nr of layers

        laypar = [pcbnew.F_Cu]
        if ln >= 4:
            laypar.append(pcbnew.In1_Cu)
            laypar.append(pcbnew.In2_Cu) 
        if ln == 6:
            laypar.append(pcbnew.In3_Cu)
            laypar.append(pcbnew.In4_Cu)
        laypar.append(pcbnew.B_Cu) 
        
        # coil terminals
        coil_t = []

        try:
            if self.ri < self.rb*1.5:
                raise ValueError()
        except ValueError:
            wx.LogWarning('Coil inner side and shaft bore are too close. Must be D_in > 1.5*D_bore')
            return


        dr = self.trk_w * 2
        th0 = math.radians(360/self.poles)

        # limit coil base width (assume 1deg gap between coils base)
        #dth = math.radians(0.5)
        # coil base half-width 
        #w2 = 10 * 1e6 #ri * math.cos(th0/2 - dth)

        # coil (corners, mid-points)
        pcu0, pcu0m = self.coil_solver(self.ri, int(ro), dr, dr, th0, self.loops, 0)
        pcu1, pcu1m = self.coil_solver(self.ri, int(ro), dr, dr, th0, self.loops, 1)

        # poles
        for p in range(self.poles):

            coil_se = []

            # rotation matrix
            th = th0 * p + math.radians(0.0001);
            c = math.cos(th)
            s = math.sin(th)
            R = np.array( [[c, -s],[s, c]] )
            # rotate all coil points
            # TODO: loop for all the availables layers
            T0 = np.matmul(R, pcu0.transpose()).transpose()
            T0v = np.matmul(R, pcu0m.transpose()).transpose()
            T1 = np.matmul(R, pcu1.transpose()).transpose()
            T1v = np.matmul(R, pcu1m.transpose()).transpose()

            for idx, lyr in enumerate(laypar):
                if idx%2:
                    ct0 = self.coil_tracker(T1, T1v, lyr)
                    # join 2 layers of the same coil
                    via = pcbnew.PCB_VIA(self.board)
                    via.SetPosition( ct0[1] )
                    via.SetDrill( self.d_drill )
                    via.SetWidth( self.trk_w )
                    self.board.Add(via)
                    self.group.AddItem(via)
                else:
                    ct0 = self.coil_tracker(T0, T0v, lyr)
                    
                # keep only: 1) start of first layer, 2) end of last layer
                #if idx==0:
                coil_se.append(ct0[0])
                #elif idx==len(laypar)-1:
                #    coil_se.append(ct0[1])

            coil_t.append(coil_se)

        return coil_t

    # run the connecting rings task
    def do_races(self, dr, ro, ri):
        
        ext_t = int_t = []

        # add some space fro mthe coil inner side
        ri -= 2*self.trk_w

        pp = int(self.poles/2)

        # (inner) concentric arc races
        th0 = math.radians(360/self.poles)
        for p in range(pp):
            cri = ri - (4+p)*dr
            # start, end, and mid angle
            ths = th0*p
            the = ths + pp/3*math.pi + th0/2
            thm = (ths+the)/2
            # inner races
            rs = pcbnew.wxPoint( cri*math.cos(ths), cri*math.sin(ths) )
            re = pcbnew.wxPoint( cri*math.cos(the), cri*math.sin(the) )
            rm = pcbnew.wxPoint( cri*math.cos(thm), cri*math.sin(thm) )
            conn = pcbnew.PCB_ARC(self.board)
            conn.SetLayer(pcbnew.F_Cu)
            conn.SetWidth(self.trk_w)
            conn.SetStart( rs )
            conn.SetMid( rm )
            conn.SetEnd( re )
            self.board.Add(conn)
            self.group.AddItem(conn)

            int_t.append([rs,re])    # track ends towards the coil (towards motor internals)

        # (outer) races (motor terminals are the start of these arcs)
        # align the center phase with end of one coil, so that only 
        # the other 2 arcs are needed
        ph_shift = math.pi/2
        ph_space = math.radians(5)
        cro = ro + 4*dr
        for i in [-1,0,1]:
            # start, end, and mid angle
            ths = ph_shift + i * ph_space 
            the = ths + i * (th0 - ph_space)
            thm = (ths+the)/2
            # outer races
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

             # track ends towards the coil (towards motor internals)
             # track starts at motor terminal (towards outside world)
            ext_t.append([rs,re])   
        
        # star-connection race
        # cri = ri - (4+pp)*dr
        # # TODO: generalize
        # ths = thadj
        # the = math.pi + thadj
        # thm = (the+ths)/2
        # # start, end, and mid angle
        # rs = pcbnew.wxPoint( cri*math.cos(ths), cri*math.sin(ths) )
        # rm = pcbnew.wxPoint( cri*math.cos(thm), cri*math.sin(thm) )
        # re = pcbnew.wxPoint( cri*math.cos(the), cri*math.sin(the) )
        # conn = pcbnew.PCB_ARC(self.board)
        # conn.SetLayer(pcbnew.F_Cu)
        # conn.SetWidth(self.trk_w)
        # conn.SetStart( rs )
        # conn.SetMid( rm )
        # conn.SetEnd( re )
        # self.board.Add(conn)
        # self.group.AddItem(conn)

        #  terminals tracks, inter-coils tracks (incl. star-connection as last))
        return ext_t, int_t;
    
    def do_junctions(self, coil, ext_t, int_t):
        # coil: contains start and end points of each coil
        # trm: contains terminals' races end points
        # int: internal races (3 coil-coil + 1 start connections)..all have start,mid,end points

        # junction: motor terminal bus bars (races) to coils terminals
        # for i, t in enumerate(ext_t):
        #     j = pcbnew.PCB_TRACK(self.board)
        #     j.SetLayer(pcbnew.F_Cu)
        #     j.SetWidth(self.trk_w)
        #     j.SetStart( t[0] )
        #     j.SetEnd( coil[i*2] )
        #     self.board.Add(j)
        #     #self.group.AddItem(j)

        # junction: coil to coil connections

        # how many coil are connected o nthe phase?
        for p in range(3):
    
            # get coils terminals
            # TODO: generalize (other that range(3))
            rs = int_t[p][0]
            re = int_t[p][1]
            c1s = coil[p][1]
            c2s = coil[p+3][0] 

        
            # juncion start (last layer)
            conn = pcbnew.PCB_TRACK(self.board)
            conn.SetLayer(pcbnew.B_Cu)
            conn.SetWidth(self.trk_w)
            conn.SetStart( c1s )
            conn.SetEnd( rs )
            self.board.Add(conn)
            self.group.AddItem(conn)
            # # inner juncion end (last layer)
            # conn = pcbnew.PCB_TRACK(self.board)
            # conn.SetLayer(pcbnew.B_Cu)
            # conn.SetWidth(self.trk_w)
            # conn.SetStart( re )
            # conn.SetEnd( c2s )
            # self.board.Add(conn)
            # self.group.AddItem(conn)

        return 0

    def do_terminals_motor(self, points):
        
        fp_lib = self.fp_path + '/Connector_Pin.pretty'
        fp = "Pin_D1.0mm_L10.0mm"

        rot = math.radians(360/self.poles) / 2

        for pos in points:
            # (inner) concentric arc races
            # start, end, and mid angle
            m = pcbnew.FootprintLoad( fp_lib, fp )
            m.SetPosition( pos )
            m.Rotate( pos, rot )
            self.board.Add(m)

        return 0

    def do_coils_terminals(self, coil_t, dr, dri):
        # start with a simple 6-pole, 3-phase connections
        # draw terminals 
        
        # dr: spacing between connection rings
        # dri: spacing between connection rings
        th0 = math.radians(360/self.poles)

        # coil terminals
        delta_c = []

        # rot adj (manual) to make jumper parallel to coil sides
        thadj = math.radians(10)

        for p in range(3):
            
            # concentric rings/arcs
            crb = self.rb + dri + p*dr
            cro = (self.ro + dri + p*dr)

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



            via = pcbnew.PCB_VIA(self.board)
            via.SetPosition( c1s )
            via.SetDrill( self.d_drill )
            via.SetWidth( self.trk_w )
            self.board.Add(via)
            self.group.AddItem(via)

            via = pcbnew.PCB_VIA(self.board)
            via.SetPosition( rs )
            via.SetDrill( self.d_drill )
            via.SetWidth( self.trk_w )
            self.board.Add(via)
            self.group.AddItem(via)

            

            via = pcbnew.PCB_VIA(self.board)
            via.SetPosition( re )
            via.SetDrill( self.d_drill )
            via.SetWidth( self.trk_w )
            self.board.Add(via)
            self.group.AddItem(via)

            via = pcbnew.PCB_VIA(self.board)
            via.SetPosition( c2s )
            via.SetDrill( self.d_drill )
            via.SetWidth( self.trk_w )
            self.board.Add(via)
            self.group.AddItem(via)



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
            via.SetDrill( self.d_drill )
            via.SetWidth( self.trk_w )
            self.board.Add(via)
            self.group.AddItem(via)
            via = pcbnew.PCB_VIA(self.board)
            via.SetPosition( c1e )
            via.SetDrill( self.d_drill )
            via.SetWidth( self.trk_w )
            self.board.Add(via)
            self.group.AddItem(via)
            # coil star connection terminal
            via = pcbnew.PCB_VIA(self.board)
            via.SetPosition( c2e )
            via.SetDrill( self.d_drill )
            via.SetWidth( self.trk_w )
            self.board.Add(via)
            self.group.AddItem(via)

            # store terminal for the jummper track
            delta_c.append(c2e)

            # motor terminal
            via = pcbnew.PCB_VIA(self.board)
            via.SetPosition( rs )
            via.SetDrill( self.d_drill )
            via.SetWidth( self.trk_w )
            self.board.Add(via)
            self.group.AddItem(via)


        # create delta connection
        ths = th0 * 3 + thadj
        the = th0 * 5 + thadj
        thm = (the+ths)/2

        rs = pcbnew.wxPoint( cro*math.cos(ths), cro*math.sin(ths) )
        rm = pcbnew.wxPoint( cro*math.cos(thm), cro*math.sin(thm) )
        re = pcbnew.wxPoint( cro*math.cos(the), cro*math.sin(the) )

        via = pcbnew.PCB_VIA(self.board)
        via.SetPosition( rs )
        via.SetDrill( self.d_drill )
        via.SetWidth( self.trk_w )
        self.board.Add(via)
        self.group.AddItem(via)

        via = pcbnew.PCB_VIA(self.board)
        via.SetPosition( rm )
        via.SetDrill( self.d_drill )
        via.SetWidth( self.trk_w )
        self.board.Add(via)
        self.group.AddItem(via)

        via = pcbnew.PCB_VIA(self.board)
        via.SetPosition( re )
        via.SetDrill( self.d_drill )
        via.SetWidth( self.trk_w )
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

     # run the thermal zones task
    def do_thermal(self):
        # see refill: 
        # https://forum.kicad.info/t/python-scripting-refill-all-zones/35834
        # TODO: circle copper area, circle keepout, no solder mask area, 
        # add vias, add cooling fingers (TBD)

        fs = 1.05*self.ro

        # retrieve gnd net
        ni_gnd = self.board.FindNet("gnd")

        #sps = pcbnew.SHAPE_POLY_SET(self.board)
        points = (
            pcbnew.wxPoint(fs,fs),
            pcbnew.wxPoint(-fs,fs),
            pcbnew.wxPoint(-fs,-fs),
            pcbnew.wxPoint(fs,-fs)
        )

        self.update_lset()

        z = pcbnew.ZONE(self.board)
        ls = pcbnew.LSET()
        for l in self.layset:
            ls.addLayer(l)
        z.SetLayerSet(ls)
        z.SetNet(ni_gnd)
        z.AddPolygon( pcbnew.wxPoint_Vector(points) )
        z.SetIsFilled(True)

        self.board.Add(z)

        # fill board
        filler = pcbnew.ZONE_FILLER(self.board) # create the filler provide the board as a param
        filler.Fill(self.board.Zones())

    def do_mounts(self):
        # no: number of outer mount points
        # ni: number of inner shaft mount points
        # see https://forum.kicad.info/t/place-update-footprint-with-python/23103

        fp_lib = self.fp_path + '/MountingHole.pretty'
        fp = "MountingHole_2.2mm_M2_Pad"

        # retrieve gnd net
        ni_gnd = self.board.FindNet("gnd")

        # inner/outer holes, nr and radial location
        nmo = self.mhon
        nmi = self.mhin
        rmo = int(0.95*self.mhor)
        rmi = self.mhir
        
        if nmo:
            th0 = math.radians(360/nmo)
            thadj = math.radians(0)
            for p in range(nmo):
                # (inner) concentric arc races
                # start, end, and mid angle
                th = th0*p + thadj
                m = pcbnew.FootprintLoad( fp_lib, fp )
                #m = pcbnew.MODULE(mod)
                m.SetPosition( 
                    pcbnew.wxPoint( int(rmo * math.cos(th)), int(rmo * math.sin(th))) )
                # assign net
                for pad in m.Pads():
                    pad.SetNet(ni_gnd)
                self.board.Add(m)

        if nmi:
            th0 = math.radians(360/nmi)
            thadj = math.radians(0)
            for p in range(nmi):
                # (inner) concentric arc races
                # start, end, and mid angle
                th = th0*p + thadj
                m = pcbnew.FootprintLoad( fp_lib, fp )
                m.SetPosition( 
                    pcbnew.wxPoint( int(rmi * math.cos(th)), int(rmi * math.sin(th))) )
                # assign net
                for pad in m.Pads():
                    pad.SetNet(ni_gnd)
                self.board.Add(m)

        return 0

    def do_outline(self, r1, r2):
        
        for r in [r1,r2]:
            arc = pcbnew.PCB_SHAPE(self.board, pcbnew.SHAPE_T_ARC)
            arc.SetArcGeometry( 
                pcbnew.wxPoint( r, 0),
                pcbnew.wxPoint( -r, 0),
                pcbnew.wxPoint( r,  0))
            arc.SetLayer( pcbnew.Edge_Cuts )
            self.board.Add(arc)
            self.group.AddItem(arc)

    def do_silk(self):
        # mark coil area
        for r in [self.ro, self.ri]:
            c = pcbnew.DRAWSEGMENT()
            c.SetShape(pcbnew.S_CIRCLE)
            c.SetCenter(pcbnew.wxPoint(0,0))
            c.SetArcStart( pcbnew.wxPoint(0,r) )
            c.SetLayer(pcbnew.F_Silkscreen)
            c.SetWidth( int(1*1e6) )
            self.board.Add(c)
   

    # event handlers
    def on_btn_clear(self, event):
        #self.logger.info("Cleared existing coils")
        #logging.shutdown()
        # TODO: 1) delete all groups, 2) remove nets, 3) other stuff TBD 
        event.Skip()

    def on_btn_generate(self, event):
        #self.logger.info("Generate stator coils")
        self.generate()
        event.Skip()

    def on_nr_layers(self, event):
        self.nl = int(self.m_ctrlLayers.GetValue())
        event.Skip()


    # tests
    def test(self):
        
        fill = int(self.m_ctrlRfill.GetValue() * 1e6)

        t = pcbnew.PCB_TRACK(self.board)
        t.SetStart( pcbnew.wxPointMM(-1,11) )
        t.SetEnd( pcbnew.wxPointMM(-2,57) )
        self.board.Add(t)
        t1 = pcbnew.PCB_ARC(self.board)
        t1.SetStart( pcbnew.wxPointMM(-2,57) )
        t1.SetMid( pcbnew.wxPointMM(-29,51) )
        t1.SetEnd( pcbnew.wxPointMM(-48,30) )
        self.board.Add(t1)
        t2 = pcbnew.PCB_TRACK(self.board)
        t2.SetStart( pcbnew.wxPointMM(-48,30) )
        t2.SetEnd( pcbnew.wxPointMM(-8,8) )
        self.board.Add(t2)
        kf.fillet(self.board, t,t1, fill)
        kf.fillet(self.board, t1,t2, fill)



        # t1 = pcbnew.PCB_TRACK(self.board)
        # t1.SetStart( pcbnew.wxPointMM(10,-10) )
        # t1.SetEnd( pcbnew.wxPointMM(110,-60) )
        # self.board.Add(t1)
        # t2 = pcbnew.PCB_TRACK(self.board)
        # t2.SetStart( pcbnew.wxPointMM(110,-60) )
        # t2.SetEnd( pcbnew.wxPointMM(110,60) )
        # self.board.Add(t2)
        # t3 = pcbnew.PCB_TRACK(self.board)
        # t3.SetStart( pcbnew.wxPointMM(110,60) )
        # t3.SetEnd( pcbnew.wxPointMM(10,-10) )
        # self.board.Add(t3)
        # kf.fillet(self.board, t1,t2, fill)
        # kf.fillet(self.board, t2,t3, fill)


        # ## square (pos XY, CCW)
        # t = pcbnew.PCB_TRACK(self.board)
        # t.SetStart( pcbnew.wxPointMM(10,10) )
        # t.SetEnd( pcbnew.wxPointMM(60,10) )
        # self.board.Add(t)
        # t1 = pcbnew.PCB_TRACK(self.board)
        # t1.SetStart( pcbnew.wxPointMM(60,10) )
        # t1.SetEnd( pcbnew.wxPointMM(60,60) )
        # self.board.Add(t1)
        # t2 = pcbnew.PCB_TRACK(self.board)
        # t2.SetStart( pcbnew.wxPointMM(60,60) )
        # t2.SetEnd( pcbnew.wxPointMM(10,60) )
        # self.board.Add(t2)
        # t3 = pcbnew.PCB_TRACK(self.board)
        # t3.SetStart( pcbnew.wxPointMM(10,60) )
        # t3.SetEnd( pcbnew.wxPointMM(10,10) )
        # self.board.Add(t3)
        # kf.fillet(self.board, t, t1, fill)
        # kf.fillet(self.board, t1, t2, fill)
        # kf.fillet(self.board, t2, t3, fill)

        ## square (pos XY, CW)
        # t = pcbnew.PCB_TRACK(self.board)
        # t.SetStart( pcbnew.wxPointMM(110,10) )
        # t.SetEnd( pcbnew.wxPointMM(110,60) )
        # self.board.Add(t)
        # t1 = pcbnew.PCB_TRACK(self.board)
        # t1.SetStart( pcbnew.wxPointMM(110,60) )
        # t1.SetEnd( pcbnew.wxPointMM(160,60) )
        # self.board.Add(t1)
        # t2 = pcbnew.PCB_TRACK(self.board)
        # t2.SetStart( pcbnew.wxPointMM(160,60) )
        # t2.SetEnd( pcbnew.wxPointMM(160,10) )
        # self.board.Add(t2)
        # t3 = pcbnew.PCB_TRACK(self.board)
        # t3.SetStart( pcbnew.wxPointMM(160,10) )
        # t3.SetEnd( pcbnew.wxPointMM(110,10) )
        # self.board.Add(t3)
        # kf.fillet(self.board, t, t1, fill)
        # kf.fillet(self.board, t1, t2, fill)
        # kf.fillet(self.board, t2, t3, fill)


        ## angles
        # t = pcbnew.PCB_TRACK(self.board)
        # t.SetStart( pcbnew.wxPointMM(100,0) )
        # t.SetEnd( pcbnew.wxPointMM(150,50) )
        # self.board.Add(t)
        # t1 = pcbnew.PCB_TRACK(self.board)
        # t1.SetStart( pcbnew.wxPointMM(150,50) )
        # t1.SetEnd( pcbnew.wxPointMM(200,50) )
        # self.board.Add(t1)
        # t2 = pcbnew.PCB_TRACK(self.board)
        # t2.SetStart( pcbnew.wxPointMM(200,50) )
        # t2.SetEnd( pcbnew.wxPointMM(150,0) )
        # self.board.Add(t2)
        # kf.fillet(self.board, t,t1, fill)
        # kf.fillet(self.board, t1,t2, fill)



        #track3 = pcbnew.PCB_ARC(self.board)
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

