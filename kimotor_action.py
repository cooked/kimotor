# Copyright 2022 Stefano Cottafavi <stefano.cottafavi@gmail.com>
# SPDX-License-Identifier: GPL-2.0-only

import wx
#import wx.lib.agw.persist as PM
import pcbnew
import os
import numpy as np
import math
import json

if __name__ == '__main__':
    import kimotor_gui
    import kimotor_linalg as kla
else:
    from . import kimotor_gui
    from . import kimotor_linalg as kla
    from . import kimotor_solver as ksolve

class KiMotor(pcbnew.ActionPlugin):
    def defaults(self):
        self.name = "KiMotor"
        self.category = "Modify Drawing PCB"
        self.description = "KiMotor - Parametric PCB stator design"
        self.show_toolbar_button = True
        self.icon_file_name = os.path.join(os.path.dirname(__file__), 'kimotor_24x24.png')
    def Run( self ):
        # grab editor frame and board
        self.frame = wx.FindWindowByName("PcbFrame")
        self.board = pcbnew.GetBoard()
        dlg = KiMotorDialog(self.frame, self.board)
        dlg.SetIcon( wx.Icon(self.icon_file_name) )
        dlg.Show()

class KiMotorDialog ( kimotor_gui.KiMotorGUI ):

    group = None

    # updated during init (0=not valid)
    SCALE = 0
    KICAD_VERSION = 0

    tl = 0
    tr = 0

    fpoint = None

    tthick = 35e-6 # [m] copper thickness (1oz layer specs)

    def __init__(self,  parent, board):
        kimotor_gui.KiMotorGUI.__init__(self, parent)

        self.board = board
        self.KICAD_VERSION = int(pcbnew.Version().split(".")[0])
        if self.KICAD_VERSION < 7:
            self.SCALE = pcbnew.IU_PER_MM
            self.fpoint = pcbnew.wxPoint
            self.fpoint_vector = pcbnew.wxPoint_Vector
        else:
            self.SCALE = pcbnew.FromMM(1)
            self.fpoint = pcbnew.VECTOR2I
            self.fpoint_vector = pcbnew.VECTOR_VECTOR2I

        #TODO:
        #self.init_persist()

        self.init_parameters()

        # disable fillet on windows
        if os.name == 'nt':
            self.r_fill = 0
            self.m_ctrlRfill.Disable()

        # init library paths and other config items
        self.init_config()
        self.init_nets()

    def generate(self):

        # TODO: improve board management
        self.group = pcbnew.PCB_GROUP( self.board )
        self.board.Add(self.group)

        # refresh parameters
        self.init_parameters()

        # rm: inner radial position of the mounting holes
        # roc: outer coil radius
        # rot: radial position of motor terminals
        self.rm = self.ro - self.w_mnt
        self.roc = self.rm - self.w_trm
        self.rot = (self.roc + (self.ro-self.w_mnt)) / 2

        # generate and connect coils
        coil_t = self.do_coils(self.nl, self.ri, self.roc)

        drc = max(self.dr, self.d_via)
        ext_t, int_t = self.do_races(drc, self.roc, self.ri)
        self.do_junctions( coil_t, ext_t, int_t)
        self.do_terminals_motor( self.rot, ext_t )

        outline = self.m_cbOutline.GetSelection()
        self.via_rows = 2

        # draw board outlines
        self.do_outline( self.rb, self.ro, outline, 8, self.o_fill)
        # create mounting holes
        self.do_mounts_footprint( outline )
        # apply thermal zones
        self.do_thermal(outline)
        # draw silks
        self.do_silk( self.roc+self.trk_w, self.ri )

        # update board
        pcbnew.Refresh()

        self.btn_clear.Enable(True)

        # update gui stats
        self.lbl_phaseLength.SetLabel( '%.2f' % self.tl )
        self.lbl_phaseR.SetLabel( '%.2f' % self.tr )

    # initializers
    def init_config(self):

        self.fp_path = None

        # check modified paths
        settings = pcbnew.SETTINGS_MANAGER.GetUserSettingsPath()
        try:
            with open(settings+'/kicad_common.json', 'r') as f:
                data = json.load(f)
                if not (data["environment"]["vars"] is None) and "KICAD6_FOOTPRINT_DIR" in data["environment"]["vars"]:
                    self.fp_path = data["environment"]["vars"]["KICAD6_FOOTPRINT_DIR"]
        except IOError:
            # catch missing file on first Kicad run
            wx.LogError("Settings file not found. This might happen, the first time you run the program. Please restart Kicad")
            return

        # check default paths
        if self.fp_path is None:
            self.fp_path = os.getenv("KICAD"+str(self.KICAD_VERSION)+"_FOOTPRINT_DIR", default=None)

        # no library found
        if self.fp_path is None:
            wx.LogError("Footprint library not found - Make sure the KiCad paths are properly configured.")

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
        
        self.r_fill = int(self.m_ctrlRfill.GetValue() * self.SCALE)         # track fillet
        self.o_fill = int(self.m_ctrlFilletRadius.GetValue() * self.SCALE)  # outline fillet

        self.ro = int(self.m_ctrlDout.GetValue() /2 * self.SCALE)
        self.w_mnt = int(self.m_ctrlWmnt.GetValue() * self.SCALE)
        self.w_trm = int(self.m_ctrlWtrm.GetValue() * self.SCALE)

        self.ri = int(self.m_ctrlDin.GetValue() /2 * self.SCALE )
        self.rb = int(self.m_ctrlDbore.GetValue() /2 * self.SCALE)

        self.mhon = int(self.m_mhOut.GetValue())
        self.mhor = int(self.m_mhOutR.GetValue() /2 * self.SCALE)
        self.mhin = int(self.m_mhIn.GetValue())
        self.mhir = int(self.m_mhInR.GetValue() /2 * self.SCALE)

        self.d_via = int(0.4 * self.SCALE)   # min via size
        self.d_drill = int(0.2 * self.SCALE)   # min drill size

        # init buttons state
        if self.group:
            self.btn_clear.Enable(True)

    def update_lset(self):
        self.layset = [pcbnew.F_Cu]
        if self.nl >= 4:
            self.layset.append(pcbnew.In1_Cu)
            self.layset.append(pcbnew.In2_Cu)
        if self.nl == 6:
            self.layset.append(pcbnew.In3_Cu)
            self.layset.append(pcbnew.In4_Cu)
        self.layset.append(pcbnew.B_Cu)

    def coil_tracker(self, Tf, Tfv, Tfvi, layer, group):
        """ Convert the points (corners and arcs mids) describing a coil layout into PCB tracks

        Args:
            Tf (_type_): set of the coil corner points
            Tfv (_type_): set of the coil outer-arcs mid-points
            Tfvi (_type_): set of the coil inner-arcs mid-points
            layer (_type_): layer on which the tracks are created

        Returns:
            _type_: _description_
        """

        # 0: no arcs, 1: outer-arc only, 2: outer and inner arc
        arc_mode = 2
        if arc_mode == 1:
            skip = 4
        elif arc_mode == 2:
            skip = 2

        start_index = 1 if layer==0 else 0
        startf = Tf[start_index]

        # keep track of the outer and inner vertexes (arcs mids)
        iv = 0
        ivi = 0

        # 1st coil point
        if layer != 0:
            #mps = pcbnew.wxPoint( int(Tfvi[ivi][0,0]), int(Tfvi[ivi][0,1]) )
            #ivi += 1
            cs = self.fpoint( int(Tfvi[ivi][0,0]), int(Tfvi[ivi][0,1]) )
            ivi += 1
            t = pcbnew.PCB_TRACK(self.board)
            t.SetWidth( self.trk_w )
            t.SetLayer( layer )
            t.SetStart( cs )
            #t.SetMid( mps )
            t.SetEnd( self.fpoint( int(startf[0,0]), int(startf[0,1]) ) )
            self.board.Add(t)
            group.AddItem(t)
        else:
            cs = self.fpoint( int(startf[0,0]), int(startf[0,1]) )


        for idx, tf in enumerate(Tf[start_index+1:]):

            # start point (p1), end point (p2) of track segment
            p1 = self.fpoint( int(startf[0,0]), int(startf[0,1]) )
            p2 = self.fpoint( int(tf[0,0]), int(tf[0,1]) )

            idx_shift = 1 if start_index==0 else 0
            if not (idx-idx_shift)%skip:

                t = pcbnew.PCB_ARC(self.board)

                # outer
                if not (idx-idx_shift)%4:
                    tfv = Tfv[iv]
                    iv += 1
                    side = 1
                # inner
                else:
                    tfv = Tfvi[ivi]
                    ivi += 1
                    side = -1

                pm = self.fpoint( int(tfv[0,0]), int(tfv[0,1]) )

                t.SetMid( pm )

            else:
                t = pcbnew.PCB_TRACK(self.board)

            t.SetWidth( self.trk_w )
            t.SetLayer( layer )
            t.SetStart( p1 )
            t.SetEnd( p2 )
            self.board.Add(t)
            group.AddItem(t)

            # fillet
            if idx > start_index and self.r_fill > 0:
                self.fillet(self.board, group, track0f, t, self.r_fill, side)

            track0f = t
            startf = tf

            # TODO: trim inner

            # trim coil if last outer side
            if iv == len(Tfv):
                m = kla.track_arc_trim(t, pm)
                pmt = self.fpoint(int(m[0]),int(m[1]))
                t.SetEnd( pm )
                t.SetMid( pmt )
                track0f = t
                break

        ce = track0f.GetEnd()

        return [cs, ce]

    def do_coils(self, ln, ri, ro, mode=0):
        """ Generate the coil tracks (with fillet) over the given PCB layers

        Args:
            ln (int): number of layer used by the coil
            ri (int): coil inner diameter
            ro (int): coil outer diameter
            mode (int): 0: parallel coil sides, 1: radial coil sides
        Raises:
            ValueError: error

        Returns:
            list: list of the coil terminals
        """

        laypar = [pcbnew.F_Cu]
        if ln >= 4:
            laypar.append(pcbnew.In1_Cu)
            laypar.append(pcbnew.In2_Cu)
        if ln == 6:
            laypar.append(pcbnew.In3_Cu)
            laypar.append(pcbnew.In4_Cu)
        laypar.append(pcbnew.B_Cu)

        try:
            if ri < self.rb*1.5:
                raise ValueError()
        except ValueError:
            wx.LogWarning('Coil inner side and shaft bore are too close. Must be D_in > 1.5*D_bore')
            return


        th0 = math.radians(360/self.poles)

        # limit coil base width (assume 1deg gap between coils base)
        #dth = math.radians(0.5)
        # coil base half-width
        #w2 = 10 * 1e6 #ri * math.cos(th0/2 - dth)

        # coil (corners, mid-points)
        pcu0, pcu0m, pcu0mi = ksolve.parallel( int(ri), int(ro), 2*self.trk_w, th0, self.loops, 0 )
        pcu1, pcu1m, pcu1mi = ksolve.parallel( int(ri), int(ro), 2*self.trk_w, th0, self.loops, 1 )

        # coil terminals
        coil_t = []
        # poles
        for p in range(self.poles):

            pgroup = pcbnew.PCB_GROUP( self.board )
            pgroup.SetName("pole_"+str(p))
            self.board.Add(pgroup)

            # coil [start,end] points
            coil_se = []

            # rotation matrix
            th = th0 * p + math.radians(0.0001); # FIXME: tweak to make it not straight up vertical
            c = math.cos(th)
            s = math.sin(th)
            R = np.array( [[c, -s],[s, c]] )
            # rotate coil points (0: CW-coil template, 1: CCW-coil template)
            T0 = np.matmul(R, pcu0.transpose()).transpose()
            T0v = np.matmul(R, pcu0m.transpose()).transpose()
            T0vi = np.matmul(R, pcu0mi.transpose()).transpose()
            T1 = np.matmul(R, pcu1.transpose()).transpose()
            T1v = np.matmul(R, pcu1m.transpose()).transpose()
            T1vi = np.matmul(R, pcu1mi.transpose()).transpose()

            for idx, lyr in enumerate(laypar):

                # EVEN layers use CCW
                if idx%2:
                    ct = self.coil_tracker(T1, T1v, T1vi, lyr, pgroup)

                    # join coil layers
                    via = pcbnew.PCB_VIA(self.board)
                    if ln==2:
                        via.SetViaType(pcbnew.VIATYPE_THROUGH)
                    else:
                        via.SetViaType(pcbnew.VIATYPE_BLIND_BURIED)
                    via.SetLayerPair( laypar[idx-1], laypar[idx] )
                    via.SetPosition( ct[1] )
                    via.SetDrill( self.d_drill )
                    via.SetWidth( self.trk_w )
                    self.board.Add(via)
                    pgroup.AddItem(via)

                # ODD layers use CW
                else:
                    ct = self.coil_tracker(T0, T0v, T0vi, lyr, pgroup)

                    if ln>2 and idx:
                        via = pcbnew.PCB_VIA(self.board)
                        via.SetViaType(pcbnew.VIATYPE_BLIND_BURIED)
                        via.SetLayerPair( laypar[idx-1], laypar[idx] )
                        via.SetPosition( ct[0] )
                        via.SetDrill( self.d_drill )
                        via.SetWidth( self.trk_w )
                        self.board.Add(via)
                        pgroup.AddItem(via)

                coil_se.append(ct[0])
            coil_t.append(coil_se)

            # stats (single pole only)
            if p==0:
                self.tl = self.stats_length(self.board)
                self.tr = self.stats_rlc(self.board, self.trk_w/self.SCALE/1000, self.tthick)

        return coil_t

    # run the connecting rings task
    def do_races(self, dr, ro, ri):

        ext_t = []
        int_t = []

        # add some space fro mthe coil inner side
        ri -= dr

        pp = int(self.poles/2)

        # (inner) concentric arc races
        th0 = math.radians(360/self.poles)
        for p in range(pp):
            cri = ri - p*dr
            # start, end, and mid angle
            ths = th0*p
            the = ths + pp/3*math.pi + th0/2
            thm = (ths+the)/2
            # inner races
            rs = self.fpoint( int(cri*math.cos(ths)), int(cri*math.sin(ths)) )
            re = self.fpoint( int(cri*math.cos(the)), int(cri*math.sin(the)) )
            rm = self.fpoint( int(cri*math.cos(thm)), int(cri*math.sin(thm)) )
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
        cro = ro + 2.5*dr
        for i in [-1,0,1]:
            # start, end, and mid angle
            ths = ph_shift + i * ph_space
            the = ths + i * (th0 - ph_space)
            thm = (ths+the)/2
            # outer races
            rs = self.fpoint( int(cro*math.cos(ths)), int(cro*math.sin(ths)) )
            rm = self.fpoint( int(cro*math.cos(thm)), int(cro*math.sin(thm)) )
            re = self.fpoint( int(cro*math.cos(the)), int(cro*math.sin(the)) )
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
        cri = ri - pp*dr
        ths = pp*th0 #- th0/2
        the = ths + (pp-1)*th0
        thm = (the+ths)/2
        # start, end, and mid angle
        rs = self.fpoint( int(cri*math.cos(ths)), int(cri*math.sin(ths)) )
        rm = self.fpoint( int(cri*math.cos(thm)), int(cri*math.sin(thm)) )
        re = self.fpoint( int(cri*math.cos(the)), int(cri*math.sin(the)) )
        conn = pcbnew.PCB_ARC(self.board)
        conn.SetLayer(pcbnew.F_Cu)
        conn.SetWidth(self.trk_w)
        conn.SetStart( rs )
        conn.SetMid( rm )
        conn.SetEnd( re )
        self.board.Add(conn)
        self.group.AddItem(conn)
        # here append also the mid point
        int_t.append([rs,rm,re])

        #  terminals tracks, inter-coils tracks (incl. star-connection as last of int_t))
        return ext_t, int_t;

    def do_junctions(self, coil, ext_t, int_t):
        # coil: contains start and end points of each coil
        # trm: contains terminals' races end points
        # int: internal races (3 coil-coil + 1 start connections)..all have start,mid,end points

        # junction: motor terminal bus bars (races) to coils terminals
        for i, et in enumerate(ext_t):
            j = pcbnew.PCB_TRACK(self.board)
            j.SetLayer(pcbnew.F_Cu)
            j.SetWidth(self.trk_w)
            j.SetStart( et[1] )
            j.SetEnd( coil[i][0] )
            self.board.Add(j)
            #self.group.AddItem(j)

        # TODO: generalize (other than 3)
        n = 3

        # junction: coil to coil connections
        # how many coil are connected on the phase?
        for p in range(n):
            # prep points
            rs = int_t[p][0]
            re = int_t[p][1]
            c1s = coil[p][1]
            c2s = coil[p+n][0]
            cd = coil[p+n][1]

            # jumper 1 (last layer)
            j = pcbnew.PCB_TRACK(self.board)
            j.SetLayer(pcbnew.B_Cu)
            j.SetWidth(self.trk_w)
            j.SetStart( c1s )
            j.SetEnd( rs )
            self.board.Add(j)
            self.group.AddItem(j)
            via = pcbnew.PCB_VIA(self.board)
            via.SetPosition( j.GetEnd() )
            via.SetDrill( self.d_drill )
            via.SetWidth( self.d_via )
            self.board.Add(via)
            self.group.AddItem(via)
            # jumper 2 (last layer)
            j = pcbnew.PCB_TRACK(self.board)
            j.SetLayer(pcbnew.F_Cu)
            j.SetWidth(self.trk_w)
            j.SetStart( re )
            j.SetEnd( c2s )
            self.board.Add(j)
            self.group.AddItem(j)

            # start-connect jumper
            j = pcbnew.PCB_TRACK(self.board)
            j.SetLayer(pcbnew.B_Cu)
            j.SetWidth(self.trk_w)
            j.SetStart( cd )
            j.SetEnd( int_t[3][p] )
            self.board.Add(j)
            self.group.AddItem(j)
            via = pcbnew.PCB_VIA(self.board)
            via.SetPosition( j.GetEnd() )
            via.SetDrill( self.d_drill )
            via.SetWidth( self.d_via )
            self.board.Add(via)
            self.group.AddItem(via)

    def do_terminals_motor(self, r, ext_t):
        """ Create motor terminal contacts and connect them to the coil terminations

        Args:
            r (int): radial position of the terminals
            ext_t (list): coils' termination tracks

        """

        fp_lib = self.fp_path + '/Connector_Pin.pretty'
        fp = "Pin_D1.0mm_L10.0mm"

        rot = math.radians(360/self.poles) / 2
        if self.KICAD_VERSION >= 7:
            rot = pcbnew.EDA_ANGLE(rot, pcbnew.RADIANS_T)

        ph_shift = math.pi/2
        ph_space = math.radians(5)

        #for t in ext_t:
        for idx, i in enumerate([-1,0,1]):

            th = ph_shift + i * ph_space
            rs = self.fpoint( int(r*math.cos(th)), int(r*math.sin(th)) )

            m = pcbnew.FootprintLoad( fp_lib, fp )
            m.SetReference('')
            m.SetPosition( rs )
            m.Rotate( rs, rot )
            self.board.Add(m)
            self.group.AddItem(m)

            # link it
            conn = pcbnew.PCB_TRACK(self.board)
            conn.SetLayer(pcbnew.F_Cu)
            conn.SetWidth(self.trk_w)
            conn.SetStart( rs )
            conn.SetEnd( ext_t[idx][0] )
            self.board.Add(conn)
            self.group.AddItem(conn)

     # run the thermal zones task
    def do_thermal(self, outline=0, nvias=36):
        # see refill:
        # https://forum.kicad.info/t/python-scripting-refill-all-zones/35834
        # TODO: add cooling fingers (TBD)

        # no solder mask inner zone
        rnsi = self.ri - 6*self.d_via

        # retrieve gnd net
        ni_gnd = self.board.FindNet("gnd")

        # get our layers right
        self.update_lset()
        ls = pcbnew.LSET()
        for l in self.layset:
            ls.addLayer(l)

        # prepare filler
        filler = pcbnew.ZONE_FILLER(self.board)

        # outer zone
        z = pcbnew.ZONE(self.board)
        if outline==0:
            # circle
            roz = 1.01*self.ro # r of the outer zone (1% larger than board outline)
            cpl = kla.circle_to_polygon( roz, 100 )
            cp = []
            for c in cpl:
                cp.append(self.fpoint(c[0],c[1]))
            z.AddPolygon( self.fpoint_vector(cp) )

        elif outline==1:
            # square
            r2 = 1.01*self.ro
            p = []
            p.append( self.fpoint(r2,r2) )
            p.append( self.fpoint(r2,-r2) )
            p.append( self.fpoint(-r2,-r2) )
            p.append( self.fpoint(-r2,r2) )
            z.AddPolygon( self.fpoint_vector(p) )

        cpl = kla.circle_to_polygon( self.roc + 2*self.trk_w, 100 )
        cp = []
        for c in cpl:
            cp.append(self.fpoint(c[0],c[1]))

        z.AddPolygon( self.fpoint_vector(cp) )
        z.SetLayerSet(ls)
        z.SetNet(ni_gnd)
        z.SetLocalClearance( self.trk_w )
        z.SetIslandRemovalMode( pcbnew.ISLAND_REMOVAL_MODE_NEVER )
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
        self.board.Add(z)



        # inner (shaft) annular
        z = pcbnew.ZONE(self.board)
        cpl = kla.circle_to_polygon( rnsi, 100 )
        cp = []
        for c in cpl:
            cp.append(self.fpoint(c[0],c[1]))

        z.AddPolygon( self.fpoint_vector(cp) )
        z.SetLayerSet(ls)
        z.SetNet(ni_gnd)
        z.SetIslandRemovalMode( pcbnew.ISLAND_REMOVAL_MODE_NEVER )
        self.board.Add(z)


        # stitching
        drv = (self.ro - self.rm) / (self.via_rows+1)
        dth = 2*math.pi / nvias
        dths = dth/2
        for j in range(self.via_rows):
            vr = self.mhor - (j+1)*drv
            vri = rnsi - (j+1)*drv
            for i in range(nvias):
                via = pcbnew.PCB_VIA(self.board)
                via.SetPosition( self.fpoint( int(vr*math.cos(dths+i*dth)), int(vr*math.sin(dths+i*dth))) )
                via.SetDrill( self.d_drill )
                via.SetWidth( self.d_via )
                via.SetNet(ni_gnd)
                self.board.Add(via)

                if not i%3:
                    via = pcbnew.PCB_VIA(self.board)
                    via.SetPosition( self.fpoint( int(vri*math.cos(dths+i*dth)), int(vri*math.sin(dths+i*dth)) ) )
                    via.SetDrill( self.d_drill )
                    via.SetWidth( self.d_via )
                    via.SetNet(ni_gnd)
                    self.board.Add(via)


        # no solder mask
        nls = pcbnew.LSET()
        nls.addLayer(pcbnew.F_Mask)
        nls.addLayer(pcbnew.B_Mask)
        z = pcbnew.ZONE(self.board)

        if outline==0:
            # circle
            cpl = kla.circle_to_polygon( self.ro, 100 )
            cp = []
            for c in cpl:
                cp.append(self.fpoint(c[0],c[1]))
            z.AddPolygon( self.fpoint_vector(cp) )
            cpl = kla.circle_to_polygon( self.rm + self.trk_w,  100 )
            cp = []
            for c in cpl:
                cp.append(self.fpoint(c[0],c[1]))
            z.AddPolygon( self.fpoint_vector(cp) )

        elif outline==1:
            # square
            r2 = 1.01*self.ro
            p = []
            p.append( self.fpoint(r2,r2) )
            p.append( self.fpoint(r2,-r2) )
            p.append( self.fpoint(-r2,-r2) )
            p.append( self.fpoint(-r2,r2) )
            z.AddPolygon( self.fpoint_vector(p) )
            p = []
            r2 = self.rm + self.trk_w
            p.append( self.fpoint(r2,r2) )
            p.append( self.fpoint(r2,-r2) )
            p.append( self.fpoint(-r2,-r2) )
            p.append( self.fpoint(-r2,r2) )
            z.AddPolygon( self.fpoint_vector(p) )

        z.SetLayerSet(nls)
        z.SetIslandRemovalMode( pcbnew.ISLAND_REMOVAL_MODE_NEVER )
        self.board.Add(z)

        z = pcbnew.ZONE(self.board)
        cpl = kla.circle_to_polygon( rnsi, 100 )
        cp = []
        for c in cpl:
            cp.append(self.fpoint(c[0],c[1]))

        z.AddPolygon( self.fpoint_vector(cp) )
        z.SetLayerSet(nls)
        z.SetIslandRemovalMode( pcbnew.ISLAND_REMOVAL_MODE_NEVER )
        self.board.Add(z)


        filler.Fill(self.board.Zones())

    def do_mounts_footprint(self, outline=0):
        # no: number of outer mount points
        # ni: number of inner shaft mount points
        # see https://forum.kicad.info/t/place-update-footprint-with-python/23103

        fp_lib = self.fp_path + '/MountingHole.pretty'
        fp = "MountingHole_3.2mm_M3_Pad"

        # retrieve gnd net
        ni_gnd = self.board.FindNet("gnd")

        # inner/outer holes, nr and radial location
        nmo = self.mhon
        nmi = self.mhin
        rmo = int(0.95*self.mhor)
        rmi = self.mhir

        if nmo:
            if outline==0:
                # circle
                th0 = math.radians(360/nmo)
                thadj = math.radians(0)
                for p in range(nmo):
                    # (inner) concentric arc races
                    # start, end, and mid angle
                    th = th0*p + thadj
                    m = pcbnew.FootprintLoad( fp_lib, fp )
                    m.SetReference('')
                    m.SetPosition(
                        self.fpoint( int(rmo * math.cos(th)), int(rmo * math.sin(th))) )
                    for pad in m.Pads():
                        pad.SetNet(ni_gnd)
                    self.board.Add(m)

            elif outline==1:
                # square
                nmo = 8
                th0 = math.radians(360/nmo)
                for p in range(nmo):
                    th = th0*p + math.pi/nmo
                    c = int( 0.98 * rmo * np.sign( math.cos(th) ))
                    s = int( 0.98 * rmo * np.sign( math.sin(th) ))

                    m = pcbnew.FootprintLoad( fp_lib, fp )
                    m.SetReference('')
                    m.SetPosition( self.fpoint(c,s) )
                    for pad in m.Pads():
                        pad.SetNet(ni_gnd)

                    self.board.Add(m)

            else:
                # polygon
                # TODO:
                return 0

        if nmi:
            th0 = math.radians(360/nmi)
            thadj = math.radians(0)
            for p in range(nmi):
                # (inner) concentric arc races
                # start, end, and mid angle
                th = th0*p + thadj
                m = pcbnew.FootprintLoad( fp_lib, fp )
                m.SetReference('')
                m.SetPosition(
                    self.fpoint( int(rmi * math.cos(th)), int(rmi * math.sin(th))) )
                # assign net
                for pad in m.Pads():
                    pad.SetNet(ni_gnd)
                self.board.Add(m)

        return 0

    def do_mounts(self, outline=0, df=3):
        # no: number of outer mount points
        # ni: number of inner shaft mount points
        # see https://forum.kicad.info/t/place-update-footprint-with-python/23103


        # inner/outer holes, nr and radial location
        nmo = self.mhon
        rmo = self.mhor

        d = df*self.SCALE

        if nmo:
            if outline==0:
                # circle
                th0 = math.radians(360/nmo)
                thadj = math.radians(0)
                for p in range(nmo):
                    th = th0*p + thadj
                    xc = int( (rmo-d) * math.cos(th))
                    yc = int( (rmo-d) * math.sin(th))
                    edge = pcbnew.PCB_SHAPE(self.board, pcbnew.SHAPE_T_CIRCLE)
                    edge.SetCenter( self.fpoint( xc,yc ) )
                    edge.SetStart( self.fpoint( xc,yc ) )
                    edge.SetEnd( self.fpoint( xc+d/2,yc ) )
                    edge.SetLayer( pcbnew.Edge_Cuts )
                    self.board.Add(edge)

            elif outline==1:
                # square
                nmo = 8
                th0 = math.radians(360/nmo)
                for p in range(nmo):
                    th = th0*p + math.pi/nmo
                    xc = int( (rmo-d) * np.sign( math.cos(th) ))
                    yc = int( (rmo-d) * np.sign( math.sin(th) ))

                    edge = pcbnew.PCB_SHAPE(self.board, pcbnew.SHAPE_T_CIRCLE)
                    edge.SetCenter( self.fpoint( xc,yc ) )
                    edge.SetStart( self.fpoint( xc,yc ) )
                    edge.SetEnd( self.fpoint( xc+d/2,yc ) )
                    edge.SetLayer( pcbnew.Edge_Cuts )
                    self.board.Add(edge)


            else:
                # polygon
                # TODO:
                return 0

    def do_outline(self, r1, r2, outline=0, edges=6, rf=0):

        # r1: bore radius
        # r2: outer radius
        # type: outline shape
        # edges: polygon edges (only if type=="Polygon")
        # rf: fillet radius

        edge = pcbnew.PCB_SHAPE(self.board, pcbnew.SHAPE_T_CIRCLE)
        edge.SetCenter( self.fpoint(0,0) )
        edge.SetStart( self.fpoint(0,0) )
        edge.SetEnd( self.fpoint(r1,0) )
        edge.SetLayer( pcbnew.Edge_Cuts )
        self.board.Add(edge)

        # circle
        if outline==0:
            edge = pcbnew.PCB_SHAPE(self.board, pcbnew.SHAPE_T_CIRCLE)
            edge.SetCenter( self.fpoint(0,0) )
            edge.SetStart( self.fpoint(0,0) )
            edge.SetEnd( self.fpoint(r2,0) )
            edge.SetLayer( pcbnew.Edge_Cuts )
            self.board.Add(edge)

        # square
        elif outline==1:
            rect = pcbnew.PCB_SHAPE(self.board, pcbnew.SHAPE_T_RECT)
            rect.SetStart( self.fpoint( -r2,-r2 ) )
            rect.SetEnd( self.fpoint( r2,r2 ) )
            points = list(rect.GetRectCorners())
            points.append(points[0])
            segs = {}
            for idx in range(4):
                seg = pcbnew.PCB_SHAPE(self.board, pcbnew.SHAPE_T_SEGMENT)
                seg.SetStart( points[idx] )
                seg.SetEnd( points[idx+1] )
                seg.SetLayer( pcbnew.Edge_Cuts )
                self.board.Add(seg)
                segs[idx] = seg
            # fillet
            if rf:
                for idx in range(4):
                    a = segs[idx]
                    b = segs[(idx + 1) % 4]
                    self.fillet_outline(self.board, a, b, rf)

        else:
            # polygon
            # TODO: fillet (see above)
            cpl = kla.circle_to_polygon(r2,edges)
            cp = []
            for c in cpl:
                cp.append(self.fpoint(c[0],c[1]))
            edge = pcbnew.PCB_SHAPE(self.board, pcbnew.SHAPE_T_POLY)
            edge.SetPolyPoints( cp )
            edge.SetLayer( pcbnew.Edge_Cuts )
            self.board.Add(edge)

    def do_silk(self, ro, ri):

        # mark active coil ring
        for r in [ro,ri]:
            c = pcbnew.PCB_SHAPE(self.board)
            c.SetShape(pcbnew.SHAPE_T_CIRCLE)
            c.SetFilled(False)
            c.SetStart( self.fpoint(0,0) )
            c.SetEnd( self.fpoint(r,0) )
            c.SetCenter( self.fpoint(0,0) )
            #c.SetWidth(int(0.1 * self.SCALE))
            c.SetLayer(pcbnew.F_SilkS)
            self.board.Add(c)

        # pcb_txt = pcbnew.PCB_TEXT(self.board)
        # pcb_txt.SetText("kimotor_p" + self.poles + "s0")
        # pcb_txt.SetPosition( pcbnew.wxPoint( 0, int(self.ro*0.95)))
        # pcb_txt.SetHorizJustify(pcbnew.GR_TEXT_HJUSTIFY_CENTER)
        # pcb_txt.Rotate( pcb_txt.GetPosition(), math.radians(0) )
        # pcb_txt.SetTextSize( pcbnew.wxSizeMM(8, 8) )
        # pcb_txt.SetLayer(pcbnew.F_SilkS)
        # self.board.Add(pcb_txt)

        # mark coil area
        # for r in [self.ro, self.ri]:
        #     c = pcbnew.DRAWSEGMENT()
        #     c.SetShape(pcbnew.S_CIRCLE)
        #     c.SetCenter(pcbnew.wxPoint(0,0))
        #     c.SetArcStart( pcbnew.wxPoint(0,r) )
        #     c.SetLayer(pcbnew.F_Silkscreen)
        #     c.SetWidth( int(1*1e6) )
        #     self.board.Add(c)
        return

    def fillet(self, board, group, t1, t2, r, side=1):
        """ Generate fillet between two tracks

        Args:
            board (_type_): board object the tracks belong to
            t1 (_type_): first track
            t2 (_type_): second track
            r (_type_): fillet radius
            side (_type_): side of the arc to offeset (1:R, -1:L)
        """

        t1_arc = t1.GetClass() == 'PCB_ARC'
        t2_arc = t2.GetClass() == 'PCB_ARC'

        ## find center and trim points

        if t1_arc and t2_arc:
            # TODO: both arcs
            return
        elif t1_arc or t2_arc:
            c = kla.line_arc_center(t1,t2,r,side)
        else:
            c = kla.line_line_center(t1,t2,r)
            # trim point track1
            l1 = kla.line_points(t1)
            p1 = kla.circle_line_tg( l1, c, r)
            # trim point track2
            l2 = kla.line_points(t2)
            p2 = kla.circle_line_tg( l2, c, r)


        if t1_arc:
            # trim point track1 (arc)
            c1 = t1.GetCenter()
            c1 = np.array([c1.x, c1.y])
            r1 = t1.GetRadius()
            p1 = kla.circle_circle_tg(c,r,c1,r1)
            # trim point track2 (line)
            l2 = kla.line_points(t2)
            p2 = kla.circle_line_tg(l2,c,r)
            # mid point
            m = kla.circle_arc_mid(p1,p2,c,r)
        elif t2_arc:
            # trim point track1 (line)
            l1 = kla.line_points(t1)
            p1 = kla.circle_line_tg(l1,c,r)
            # trim point track2 (arc)
            c2 = t2.GetCenter()
            c2 = np.array([c2.x, c2.y])
            r2 = t2.GetRadius()
            p2 = kla.circle_circle_tg(c,r, c2, r2)
            # mid point
            m = kla.circle_arc_mid(p1,p2, c,r)
        else:
            # arc mid-point
            t1e = t1.GetEnd()
            l = np.array([c, [t1e.x, t1e.y, 0]])
            lv = kla.line_vec(l)
            m = c + np.dot(r, lv)


        # generate fillet track
        t = pcbnew.PCB_ARC(board)
        t.SetLayer( t1.GetLayer() )
        t.SetWidth( t1.GetWidth() )
        t.SetStart( self.fpoint(int(p1[0]),int(p1[1])) )
        t.SetMid( self.fpoint(int(m[0]),int(m[1])) )
        t.SetEnd( self.fpoint(int(p2[0]),int(p2[1])) )
        board.Add(t)
        group.AddItem(t)
        # trim tracks
        t1.SetEnd( self.fpoint(int(p1[0]),int(p1[1]))  )
        t2.SetStart( self.fpoint(int(p2[0]),int(p2[1]))  )

    ## borrowed from fillet_helper.py
    ## https://github.com/tywtyw2002/FilletEdge/blob/master/fillet_helper.py
    def fillet_outline(self, board, a, b, fillet_value):
        # must be cw rotate, swap if ccw rotate
        theta = 0
        a_s = a.GetStart()
        a_e = a.GetEnd()
        b_s = b.GetStart()
        b_e = b.GetEnd()
        a_reverse = 1
        b_reverse = 1
        a_set = a.SetStart
        b_set = b.SetStart
        co_point = self.fpoint(a_s.x, a_s.y)

        if a_e == b_s or a_e == b_e:
            co_point = self.fpoint(a_e.x, a_e.y)
            a_set = a.SetEnd
            a_reverse = -1
        elif a_s != b_s and a_s != b_e:
            wx.LogWarning('Unable to Fillet, 2 lines not share any point.')
            return

        if b_e == co_point:
            b_reverse = -1
            b_set = b.SetEnd

        a_v = pcbnew.VECTOR2I(
            (a.GetEndX() - a.GetStartX()) * a_reverse,
            -(a.GetEndY() - a.GetStartY()) * a_reverse
        )
        b_v = pcbnew.VECTOR2I(
            (b.GetEndX() - b.GetStartX()) * b_reverse,
            -(b.GetEndY() - b.GetStartY()) * b_reverse
        )

        theta = a_v.Angle() - b_v.Angle()

        if theta < -math.pi:
            theta += math.pi * 2
        elif theta > math.pi:
            theta -= math.pi * 2

        deg = math.degrees(theta)

        offset = fillet_value
        if int(deg) != 90 and int(deg) != -90:
            offset = abs(offset * math.tan((math.pi - theta) / 2))

        a_point = self.fpoint(
            int(co_point.x + offset * math.cos(a_v.Angle())),
            int(co_point.y - offset * math.sin(a_v.Angle()))
        )
        b_point = self.fpoint(
            int(co_point.x + offset * math.cos(b_v.Angle())),
            int(co_point.y - offset * math.sin(b_v.Angle()))
        )

        a_set(a_point)
        b_set(b_point)

        # check length
        if a.GetLength() == 0:
            board.Remove(a)

        if b.GetLength() == 0:
            board.Remove(b)

        # set arc
        s_arc = pcbnew.PCB_SHAPE()
        s_arc.SetShape(pcbnew.SHAPE_T_ARC)

        c_v = a_v.Resize(1000000) + b_v.Resize(1000000)
        c_angle = c_v.Angle()

        if offset == fillet_value:
            # 90 or -90
            s_arc.SetCenter(self.fpoint(
                a_point.x + b_point.x - co_point.x,
                a_point.y + b_point.y - co_point.y
            ))
        else:
            coffset = abs(fillet_value / math.cos((math.pi - theta) / 2))
            s_arc.SetCenter(self.fpoint(
                co_point.x + int(coffset * math.cos(c_angle)),
                co_point.y - int(coffset * math.sin(c_angle))
            ))

        if deg < 0:
            s_arc.SetStart(a_point)
        else:
            s_arc.SetStart(b_point)

        s_arc.SetArcAngleAndEnd(1800 - abs(deg * 10))

        s_arc.SetLayer(a.GetLayer())
        s_arc.SetWidth(a.GetWidth())

        board.Add(s_arc)

    ## stats 
    def stats_length(self, board):
        tot = 0
        for track in board.GetTracks():
            l = track.GetLength()
            tot += l/self.SCALE

        return tot

    def stats_rlc(self, board, w, t, temp=20):
        """ Calculate resistance, inductance and capacitance of a track
        Args:
            board (_type_): _description_
            w (_type_): track width
            t (_type_): track thickness
            temp (float): ambient temperature
        """

        # https://www.allaboutcircuits.com/tools/trace-resistance-calculator/
        # https://www.cirris.com/learning-center/general-testing/special-topics/177-temperature-coefficient-of-copper
        rho = 1.77e-8       # [ohm/m] copper resistivity @ 20C
        alpha = 3.99e-2     # [ohm/ohm/C] copper temperature coeff

        L = self.stats_length(board) / 1000
        A = w*t
        r = rho * L/A
        rt = r * (1+alpha*(temp-20))

        # https://resources.system-analysis.cadence.com/blog/msa2021-is-there-a-pcb-trace-inductance-rule-of-thumb

        return rt


    # file utils
    def import_json(self, file):
        # TODO:
        return 0

    def export_json(self, file):
        # TODO:
        return 0


    # event handlers (buttons)
    def on_close(self, event):
        #self._persistMgr.SaveAndUnregister()
        event.Skip()

    def on_btn_clear(self, event):
        #self.logger.info("Cleared existing coils")
        #logging.shutdown()
        # TODO: 1) delete all groups, 2) remove nets, 3) other stuff TBD
        # init buttons state
        if self.group:
            self.group.RemoveAll()
            self.group = None
            self.btn_clear.Enable(False)

        event.Skip()

    def on_btn_generate(self, event):
        #self.logger.info("Generate stator coils")
        self.generate()
        event.Skip()

    # https://docs.wxpython.org/wx.FileDialog.html
    def on_btn_load(self, event):
        #if self.contentNotSaved:
        #    if wx.MessageBox("Current content has not been saved! Proceed?", "Please confirm",
        #                    wx.ICON_QUESTION | wx.YES_NO, self) == wx.NO:
        #        return
        # otherwise ask the user what new file to open
        with wx.FileDialog(self, "Open XYZ file", wildcard="XYZ files (*.xyz)|*.xyz",
                        style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            # Proceed loading the file chosen by the user
            pathname = fileDialog.GetPath()
            try:
                with open(pathname, 'r') as file:
                    self.import_json(file)
            except IOError:
                wx.LogError("Cannot open file '%s'." % pathname)

    def on_btn_save(self, event):
        with wx.FileDialog(self, "Save XYZ file", wildcard="XYZ files (*.xyz)|*.xyz",
                       style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            # save the current contents in the file
            pathname = fileDialog.GetPath()
            try:
                with open(pathname, 'w') as file:
                    self.export_json(file)
            except IOError:
                wx.LogError("Cannot save current data in file '%s'." % pathname)


    def on_cb_preset(self, event):
        preset = self.m_cbPreset.GetSelection()
        #val = self.m_cbPreset.GetStringSelection()
        if preset == 0:
            self.m_ctrlTrackWidth.SetValue(0.3)

        # JLCPCB 1-2 layers 5mil(0.127mm)
        elif preset == 1:
            self.m_ctrlTrackWidth.SetValue(0.127)

        # JLCPCB 4-6 layers
        elif preset == 1:
            self.m_ctrlTrackWidth.SetValue(0.127)

        event.Skip()

    def on_cb_outline(self, event):

        event.Skip()

    # event handlers (parameters)
    def on_nr_layers(self, event):
        self.nl = int(self.m_ctrlLayers.GetValue())
        event.Skip()
