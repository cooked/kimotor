# Copyright 2022 Stefano Cottafavi <stefano.cottafavi@gmail.com>
# SPDX-License-Identifier: GPL-2.0-only

import os
import shutil
import numpy as np
import math
import json

import wx
import wx.lib.agw.persist.persistencemanager as PM
import pcbnew

if __name__ == '__main__':
    import kimotor_gui
    import kimotor_linalg as kla
else:
    from . import kimotor_gui
    from . import kimotor_linalg as kla
    from . import kimotor_solver as ksolve
    from . import kimotor_persist as kpers

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

    # updated during init (0: not valid)
    SCALE = 0
    KICAD_VERSION = 0

    tl = 0
    tr = 0

    fpoint = None

    tthick = 35e-6 # [m] copper thickness (1oz layer specs)

    # fab capabilities (min)
    fc_jlcpcb_12 = {
        "track_width": 0.127, # (5mil)
        "track_space": 0.127, # (5mil)
        "via_hole": 0.15,
        "via_diameter": 0.25,
    } 

    # terminal footprint dict
    term_db = {
        "0.1"   : "SolderWire-0.1sqmm_1x01_D0.4mm_OD1mm",
        "0.15"  : "SolderWire-0.15sqmm_1x01_D0.5mm_OD1.5mm",
        "0.25"  : "SolderWire-0.25sqmm_1x01_D0.65mm_OD1.7mm",
        "0.5"   : "SolderWire-0.5sqmm_1x01_D0.9mm_OD2.1mm",
        "0.75"  : "SolderWire-0.75sqmm_1x01_D1.25mm_OD2.3mm",
        "1.0"   : "SolderWire-1sqmm_1x01_D1.4mm_OD2.7mm",
        "1.5"   : "SolderWire-1.5sqmm_1x01_D1.7mm_OD3.9mm",
        "2.0"   : "SolderWire-2sqmm_1x01_D2mm_OD3.9mm",
        "2.5"   : "SolderWire-2.5sqmm_1x01_D2.4mm_OD3.6mm"
    }

    mhole_db = {
        "M2"    : "MountingHole_2.2mm_M2_Pad",
        "M2.5"  : "MountingHole_2.7mm_M2.5_Pad",
        "M3"    : "MountingHole_3.2mm_M3_Pad",
        "M3.5"  : "MountingHole_3.7mm_M3.5_Pad",
        "M4"    : "MountingHole_4.3mm_M4_Pad",
        "M5"    : "MountingHole_5.3mm_M5_Pad",
        "M6"    : "MountingHole_6.4mm_M6_Pad",
        "M8"    : "MountingHole_8.4mm_M8_Pad",
    }

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

        # kick-off persistence
        self.pf = os.path.join(
            pcbnew.SETTINGS_MANAGER.GetUserSettingsPath(),
            "kimotor.cfg"
        )

        self.init_persist(self.pf)

        self.init_parameters(self.fc_jlcpcb_12)
       
        if os.name == 'nt':
            self.r_fill = 0
            self.m_ctrlRfill.Disable()
        self.init_path()
        self.init_nets()


    # init functions
    def init_persist(self, configFile):
        self.pm = PM.PersistenceManager.Get()
        self.pm.SetPersistenceFile(configFile)
        self.pm.RegisterAndRestoreAll(self)

    def set_capabilities(self):
        return
    
    def init_parameters(self, caps):

        # get gui values and fix units (mm converted to nm where needed)

        self.nl     = int(self.m_ctrlLayers.GetValue())
        self.phases = 1 if (self.m_cbScheme.GetStringSelection() == "1P") else 3
        self.slots  = int(self.m_ctrlSlots.GetValue())
        self.loops  = int(self.m_ctrlLoops.GetValue())

        self.trk_w = int(self.m_ctrlTrackWidth.GetValue() * self.SCALE) # track width
        self.dr = self.trk_w * 2                                        # track distance
        
        self.d_via = int(caps.get('via_diameter') * self.SCALE)   # min via size
        self.d_drill = int(caps.get('via_hole') * self.SCALE)   # min drill size


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

        

        # init buttons state
        if self.group:
            self.btn_clear.Enable(True)

    def init_path(self):

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
        gnd = pcbnew.NETINFO_ITEM(self.board, "gnd")
        coil = pcbnew.NETINFO_ITEM(self.board, "coil")
        self.board.Add(gnd)
        self.board.Add(coil)

    

    # core functions

    def generate(self):

        # TODO: improve board management
        self.group = pcbnew.PCB_GROUP( self.board )
        self.board.Add(self.group)

        # refresh parameters
        self.init_parameters(self.fc_jlcpcb_12)

        # rm: inner radial position of the mounting holes
        # roc: outer coil radius
        # rot: radial position of motor terminals
        self.rm = self.ro - self.w_mnt
        self.roc = self.rm - self.w_trm
        self.rot = (self.roc + (self.ro-self.w_mnt)) / 2

        # slot angular width
        self.th0 = 2*math.pi/self.slots

        # generate and connect coils
        strategy = self.m_cbStrategy.GetSelection()
        [coil_t, coilp ] = self.do_coils(self.nl, self.ri, self.roc, strategy)

        self.drc = max(self.dr, self.d_via)
        [cnx_seg, cnx_str, cri] = self.do_races(self.drc, self.ri)
        self.do_junctions(coilp, cnx_seg, cnx_str)
        self.do_terminals(self.rot, coil_t)

        outline = self.m_cbOutline.GetSelection()
        self.via_rows = 2

        # draw board outlines
        self.do_outline( self.rb, self.ro, outline, 8, self.o_fill)

        # create mounting holes
        self.do_mounts(outline)
        
        # apply thermal zones
        self.do_thermal(cri, outline)
        
        # draw silks
        self.do_silk( self.roc+self.trk_w, self.ri, self.th0 )

        # update board
        pcbnew.Refresh()

        self.btn_clear.Enable(True)

        # update gui stats
        self.lbl_phaseLength.SetLabel( '%.2f' % self.tl )
        self.lbl_phaseR.SetLabel( '%.2f' % self.tr )

    def update_lset(self):
        self.layset = [pcbnew.F_Cu]
        if self.nl >= 4:
            self.layset.append(pcbnew.In1_Cu)
            self.layset.append(pcbnew.In2_Cu)
        if self.nl == 6:
            self.layset.append(pcbnew.In3_Cu)
            self.layset.append(pcbnew.In4_Cu)
        self.layset.append(pcbnew.B_Cu)

    def coil_tracker(self, mpt, layer, group):
        """ Convert the points (corners and arcs mids) describing a coil layout into 
        PCB tracks

        Args:
            mpt (_type_): set of the coil corner points
            layer (_type_): layer on which the tracks are created

        Returns:
            _type_: _description_
        """

        cs = self.fpoint( int(mpt[0][0,0]), int(mpt[0][0,1]) )

        # index of current point
        ip = 0 
        t0 = None

        nseg = self.loops*4 - 1 
        for seg in range(nseg):

            # start point
            ps = self.fpoint( int(mpt[ip][0,0]), int(mpt[ip][0,1]) )
            
            # even segments (0,2,4,etc.)
            if not seg%2:
                ip += 1
                t = pcbnew.PCB_ARC(self.board)
                t.SetMid( self.fpoint(int(mpt[ip][0,0]), int(mpt[ip][0,1])) )

                # 1: outer, -1: inner
                side = -1 if not seg%4 else 1

            else:
                t = pcbnew.PCB_TRACK(self.board)

            ip += 1
            pe = self.fpoint( int(mpt[ip][0,0]), int(mpt[ip][0,1]) )

            t.SetWidth( self.trk_w )
            t.SetLayer( layer )
            t.SetStart( ps )
            t.SetEnd( pe )
            self.board.Add(t)

            # fillet
            if seg > 0 and self.r_fill > 0:
                self.fillet(self.board, group, t0, t, self.r_fill, side)

            t0 = t
            
        ce = t.GetEnd()

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
        if ln >= 6:
            laypar.append(pcbnew.In3_Cu)
            laypar.append(pcbnew.In4_Cu)
        if ln >= 8:
            laypar.append(pcbnew.In5_Cu)
            laypar.append(pcbnew.In6_Cu)
        if ln >= 10:
            laypar.append(pcbnew.In7_Cu)
            laypar.append(pcbnew.In8_Cu)
        if ln >= 12:
            laypar.append(pcbnew.In9_Cu)
            laypar.append(pcbnew.In10_Cu)
        if ln >= 14:
            laypar.append(pcbnew.In11_Cu)
            laypar.append(pcbnew.In12_Cu)
        if ln >= 16:
            laypar.append(pcbnew.In13_Cu)
            laypar.append(pcbnew.In14_Cu)
        if ln >= 18:
            laypar.append(pcbnew.In15_Cu)
            laypar.append(pcbnew.In16_Cu)
        if ln >= 20:
            laypar.append(pcbnew.In17_Cu)
            laypar.append(pcbnew.In18_Cu)   
        laypar.append(pcbnew.B_Cu)

        try:
            if ri < self.rb*1.5:
                raise ValueError()
        except ValueError:
            wx.LogWarning('Coil inner side and shaft bore are too close. Must be D_in > 1.5*D_bore')
            return

        #
        th0 = math.radians(360/self.slots)

        # limit coil base width (assume 1deg gap between coils base)
        #dth = math.radians(0.5)
        # coil base half-width
        #w2 = 10 * 1e6 #ri * math.cos(th0/2 - dth)

        # coil (corners, mid-points)
        if mode == 0:
            pcu0, pcu0m, pcu0mi = ksolve.parallel( 
                int(ri), int(ro), 2*self.trk_w, th0, self.loops, 0 )
            pcu1, pcu1m, pcu1mi = ksolve.parallel( 
                int(ri), int(ro), 2*self.trk_w, th0, self.loops, 1 )

        else:
            pcu0 = ksolve.radial(
                int(ri), int(ro), 2*self.trk_w, th0, self.loops, 0 )
            pcu1 = ksolve.radial(
                int(ri), int(ro), 2*self.trk_w, th0, self.loops, 1 )
        
        # coil terminals
        coil_t = []
        
        coilp = []
        for i in range(self.phases):
            coilp.append([])
        
        # poles
        for p in range(self.slots):

            pgroup = pcbnew.PCB_GROUP( self.board )
            pgroup.SetName("pole_"+str(p))
            self.board.Add(pgroup)

            # coil [start,end] points
            coil_se = []

            # rotation matrix
            th = th0 * p #+ math.radians(0.0001) # FIXME: tweak to make it not straight up vertical
            c = math.cos(th)
            s = math.sin(th)
            R = np.array( [[c, -s],[s, c]] )
            # rotate coil points (0: CW-coil template, 1: CCW-coil template)
            Tcw = np.matmul(R, pcu0.transpose()).transpose()
            Tccw = np.matmul(R, pcu1.transpose()).transpose()

            for idx, lyr in enumerate(laypar):

                # even, CCW
                if idx%2:
                    ct = self.coil_tracker(Tccw, lyr, pgroup)

                    # join coil layers
                    via = pcbnew.PCB_VIA(self.board)
                    if ln==2:
                        via.SetViaType(pcbnew.VIATYPE_THROUGH)
                    else:
                        via.SetViaType(pcbnew.VIATYPE_BLIND_BURIED)
                    via.SetLayerPair( laypar[idx-1], laypar[idx] )
                    via.SetPosition( ct[1] )
                    via.SetDrill( self.d_drill )
                    via.SetWidth( self.d_via )
                    self.board.Add(via)

                # odd, CW
                else:
                    ct = self.coil_tracker(Tcw, lyr, pgroup)

                    if ln>2 and idx:
                        via = pcbnew.PCB_VIA(self.board)
                        via.SetViaType(pcbnew.VIATYPE_BLIND_BURIED)
                        via.SetLayerPair( laypar[idx-1], laypar[idx] )
                        via.SetPosition( ct[0] )
                        via.SetDrill( self.d_drill )
                        via.SetWidth( self.d_via )
                        self.board.Add(via)

                # append first and last only
                if idx == 0 or idx == len(laypar)-1:
                    coil_se.append(ct[0])

                # coil_se.append(ct[1])
        
            coil_t.append(coil_se)

            # group coils by phase
            coilp[ p%self.phases ].append(coil_se)

            # stats (single pole only)
            if p==0:
                self.tl = self.stats_length(self.board)
                self.tr = self.stats_rlc(self.board, self.trk_w/self.SCALE/1000, self.tthick)

        return coil_t, coilp

    def do_races(self, dr, ri):
        """ Create the arc segments that connect the coils of the same "phase". 
        They are placed between the coils and the shaft bore.

        Args:
            r (int): radial position of the terminals
            ext_t (list): coils' termination tracks

        """

        # place the tracks a bit more spaced from the coils
        ri -= 2*dr

        phases = int(self.phases)

        # slot angular width
        th0 = 2*math.pi/self.slots
        # unit delta (shift) for race's start/end points
        thd = th0/8

        # number of distinct segments on each phase ring 
        n_rc = int(self.slots/self.phases)-1

        # all segments, of all the phase rings
        conns_t = []
        # phase-phase connection
        cnx_star = None

        # create phase tracks
        for p in range(phases):

            # radial location of the ring
            cri = ri - p*dr
            
            # segments on the same phase ring
            segs_t = []

            for i_rc in range(n_rc):
                # find directions of start, end, mid points of the arc segment
                th_s = th0*( p + i_rc*phases ) + thd
                th_e = th_s + th0*phases - 2*thd
                th_m = (th_s+th_e)/2
                # translate (r,th) to (x,y) coords
                xy_s = self.fpoint( int(cri*math.cos(th_s)), int(cri*math.sin(th_s)) )
                xy_e = self.fpoint( int(cri*math.cos(th_e)), int(cri*math.sin(th_e)) )
                xy_m = self.fpoint( int(cri*math.cos(th_m)), int(cri*math.sin(th_m)) )

                conn = pcbnew.PCB_ARC(self.board)
                conn.SetLayer(pcbnew.F_Cu)
                conn.SetWidth(self.trk_w)
                conn.SetStart( xy_s )
                conn.SetMid( xy_m )
                conn.SetEnd( xy_e )
                self.board.Add(conn)

                # track ends towards the coil (towards motor internals)
                segs_t.append([xy_s,xy_e])    

            conns_t.append(segs_t)

            # star-connection on 1st phase ring
            if p==0:
                # find directions
                ths = -3*th0
                the = -1*th0
                thm = (ths+the)/2
                # translate (r,th) to (x,y) coords
                rs = self.fpoint( int(cri*math.cos(ths)), int(cri*math.sin(ths)) )
                rm = self.fpoint( int(cri*math.cos(thm)), int(cri*math.sin(thm)) )
                re = self.fpoint( int(cri*math.cos(the)), int(cri*math.sin(the)) )
                # do track
                conn = pcbnew.PCB_ARC(self.board)
                conn.SetLayer(pcbnew.B_Cu)
                conn.SetWidth(self.trk_w)
                conn.SetStart( rs )
                conn.SetMid( rm )
                conn.SetEnd( re )
                self.board.Add(conn)

                # here append also the mid point
                cnx_star = [rs,rm,re]

        # return:
        # - ring segments coordinates
        # - star connection coordinates 
        # - radial location of the innermost ring + some (used for filling keep-out)
        return conns_t, cnx_star, cri-2*dr

    def do_junctions(self, coilp, cnx_seg, cnx_str):
        """ Create the "jumpers" segments that connect the coil terminations to the  
        They are placed between the coils and the shaft bore.

        Args:
            coilp (list): contains start and end points of each coil, grouped by phase
            cnx_seg (list): contains start and end points of each arc segment of each 
            coil connector ring
        """

        phases = int(self.phases)

        # slot angular width
        # TODO: make them to the class to avoid code duplication
        th0 = 2*math.pi/self.slots
        thd = th0/8

        ri = self.ri - self.drc

        # number of distinct segments, per each phase 
        n_rc = int(self.slots/self.phases)-1

        for p in range(phases):
                        
            for i in range(n_rc):
                
                rs = cnx_seg[p][i][0]
                re = cnx_seg[p][i][1]
                
                #c1s = coilp[p][i][0]
                c1e = coilp[p][i][1]

                c2s = coilp[p][i+1][0]
                c2e = coilp[p][i+1][1]

                if i <= n_rc:
                    j = pcbnew.PCB_TRACK(self.board)
                    j.SetLayer(pcbnew.B_Cu)
                    j.SetWidth(self.trk_w)
                    j.SetStart( c1e )
                    j.SetEnd( rs )
                    self.board.Add(j)

                    if i == 0:
                        via = pcbnew.PCB_VIA(self.board)
                        via.SetPosition( rs )
                        via.SetDrill( self.d_drill )
                        via.SetWidth( self.d_via )
                        self.board.Add(via)    

                    if p==0 or i==n_rc-1:
                        j = pcbnew.PCB_TRACK(self.board)
                        j.SetLayer(pcbnew.F_Cu)
                        j.SetWidth(self.trk_w)
                        j.SetStart( c2s )
                        j.SetEnd( re )
                        self.board.Add(j)

                    else:
                        # cross under the other phases
                        th_s = th0*( p + i*phases ) + thd
                        th_e = th_s + th0*phases - 2*thd
                        xy_a = self.fpoint(
                            int(ri*math.cos(th_e)), 
                            int(ri*math.sin(th_e)))
                        
                        j = pcbnew.PCB_TRACK(self.board)
                        j.SetLayer(pcbnew.B_Cu)
                        j.SetWidth(self.trk_w)
                        j.SetStart( re )
                        j.SetEnd( xy_a )
                        self.board.Add(j)
                        via = pcbnew.PCB_VIA(self.board)
                        via.SetPosition( re )
                        via.SetDrill( self.d_drill )
                        via.SetWidth( self.d_via )
                        self.board.Add(via)

                        j = pcbnew.PCB_TRACK(self.board)
                        j.SetLayer(pcbnew.F_Cu)
                        j.SetWidth(self.trk_w)
                        j.SetStart( xy_a )
                        j.SetEnd( c2s )
                        self.board.Add(j)
                        via = pcbnew.PCB_VIA(self.board)
                        via.SetPosition( xy_a )
                        via.SetDrill( self.d_drill )
                        via.SetWidth( self.d_via )
                        self.board.Add(via)

                if i > 0:
                    # jumper at each coil start, but the first coil, for each phase  
                    j = pcbnew.PCB_TRACK(self.board)
                    j.SetLayer(pcbnew.B_Cu)
                    j.SetWidth(self.trk_w)
                    j.SetStart( c1e )
                    j.SetEnd( rs )
                    self.board.Add(j)
                    via = pcbnew.PCB_VIA(self.board)
                    via.SetPosition( rs )
                    via.SetDrill( self.d_drill )
                    via.SetWidth( self.d_via )
                    self.board.Add(via)

                # star-connect jumper
                if i == n_rc-1:
                    j = pcbnew.PCB_TRACK(self.board)
                    j.SetLayer(pcbnew.B_Cu)
                    j.SetWidth(self.trk_w)
                    j.SetStart( c2e )
                    j.SetEnd( cnx_str[p] )
                    self.board.Add(j)

    def do_terminals(self, r_t, coils_t):
        """ Create the motor terminals, and the tracks that connect the terminals to the coils

        Args:
            r_t (int): radial position of the terminals
            coils_t (list): list of coils tracks

        """
        # locate terminal footprint
        trm_lib_name = 'Connector_Wire'
        trm_lib_path = self.fp_path + trm_lib_name + '.pretty'
        trm_fp = self.term_db.get( self.m_termSize.GetStringSelection() )
        
        # retrieve nets
        net_coil = self.board.FindNet("coil")

        # nr of terminals
        n_term = 2 if (self.m_cbScheme.GetStringSelection() == "1P") else ( 
            3 if (self.m_cbScheme.GetStringSelection() == "3P") else 4
        )

        # base angle, half (to position terminals), quarter (to locate arc track mid-point)
        th0 = 2*math.pi/self.slots
        thd = th0/2
        thr = th0/4

        Rcw = np.array([
            [math.cos(thr), -math.sin(thr)],
            [math.sin(thr), math.cos(thr)],
        ])

        for i in range(n_term):

            # radial to cartesian coords of terminal, aux corner, coil start 
            th = th0*i - thd

            ax = self.ri*math.cos(th)
            ay = self.ri*math.sin(th)
            tp = np.matmul(Rcw, np.array([ax,ay]))  

            xy_t = self.fpoint( int(r_t*math.cos(th)), int(r_t*math.sin(th)) )
            xy_a = self.fpoint( int(ax), int(ay) )
            xy_c = coils_t[i][0]

            # terminal
            m = pcbnew.FootprintLoad( trm_lib_path, trm_fp )
            m.Reference().SetVisible(False)
            m.Value().SetVisible(False)
            m.SetFPIDAsString(trm_lib_name + ":" + trm_fp)
            m.SetReference('T'+str(i+1))
            m.SetPosition(xy_t)
            m.Rotate(xy_t, pcbnew.EDA_ANGLE(-th, pcbnew.RADIANS_T))
            for p in m.Pads():
                p.SetNet(net_coil)
            self.board.Add(m)

            # track, straight part
            conn = pcbnew.PCB_TRACK(self.board)
            conn.SetLayer(pcbnew.F_Cu)
            conn.SetNet(net_coil)
            conn.SetWidth(self.trk_w)
            conn.SetStart(xy_t)
            conn.SetEnd(xy_a)
            self.board.Add(conn)
            # track, arc part
            conn = pcbnew.PCB_ARC(self.board)
            conn.SetLayer(pcbnew.F_Cu)
            conn.SetNet(net_coil)
            conn.SetWidth(self.trk_w)
            conn.SetStart(xy_a)    
            conn.SetMid( self.fpoint( int(tp[0]), int(tp[1])) )
            conn.SetEnd(xy_c)
            self.board.Add(conn) 

            # label
            pcb_txt = pcbnew.PCB_TEXT(self.board)
            pcb_txt.SetText("A" if i==0 else ("B" if i==1 else "C"))
            dth = .05
            xy_s = self.fpoint( int(r_t*math.cos(th+dth)), int(r_t*math.sin(th+dth)) )
            pcb_txt.SetPosition( xy_s )
            pcb_txt.Rotate( 
                pcb_txt.GetPosition(),
                pcbnew.EDA_ANGLE(math.pi/2-th-dth,pcbnew. RADIANS_T)
            )
            pcb_txt.SetLayer(pcbnew.F_SilkS)
            self.board.Add(pcb_txt)

    # create thermal zones
    def do_thermal(self, cri, outline=0, nvias=36):
        # see refill:
        # https://forum.kicad.info/t/python-scripting-refill-all-zones/35834
        # TODO: add cooling fingers (TBD)

        # no solder mask inner zone
        rnsi = cri #self.ri - 8*self.d_via

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
        # drv = (self.ro - self.rm) / (self.via_rows+1)
        # dth = 2*math.pi / nvias
        # dths = dth/2
        # for j in range(self.via_rows):
        #     vr = self.mhor - (j+1)*drv
        #     vri = rnsi - (j+1)*drv
        #     for i in range(nvias):
        #         via = pcbnew.PCB_VIA(self.board)
        #         via.SetPosition( self.fpoint( int(vr*math.cos(dths+i*dth)), int(vr*math.sin(dths+i*dth))) )
        #         via.SetDrill( self.d_drill )
        #         via.SetWidth( self.d_via )
        #         via.SetNet(ni_gnd)
        #         self.board.Add(via)

        #         if not i%3:
        #             via = pcbnew.PCB_VIA(self.board)
        #             via.SetPosition( self.fpoint( int(vri*math.cos(dths+i*dth)), int(vri*math.sin(dths+i*dth)) ) )
        #             via.SetDrill( self.d_drill )
        #             via.SetWidth( self.d_via )
        #             via.SetNet(ni_gnd)
        #             self.board.Add(via)


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

    def do_mounts(self, outline=0):
        # no: number of outer mount points
        # ni: number of inner shaft mount points
        # see https://forum.kicad.info/t/place-update-footprint-with-python/23103

        hs = self.m_cbMountSize.GetStringSelection()
        if hs != "None":
            fp_lib = self.fp_path + '/MountingHole.pretty'
            fp = self.mhole_db.get( hs )
        else:
            return

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
                thd = th0/2
                for p in range(nmo):
                    # (inner) concentric arc races
                    # start, end, and mid angle
                    th = th0*p + thd
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

    def do_silk(self, ro, ri, th):

        # pcb label
        #pcb_txt = pcbnew.PCB_TEXT(self.board)
        #pcb_txt.SetText("kimotor_ph" + str(self.phases) + "_s" + str(self.slots))
        #pcb_txt.SetPosition( self.fpoint( 0, int(self.ro)))
        #pcb_txt.SetLayer(pcbnew.F_SilkS)
        #self.board.Add(pcb_txt)

        # mark active coil ring
        for r in [ro,ri]:
            c = pcbnew.PCB_SHAPE(self.board)
            c.SetShape(pcbnew.SHAPE_T_CIRCLE)
            c.SetFilled(False)
            c.SetStart( self.fpoint(0,0) )
            c.SetEnd( self.fpoint(r,0) )
            c.SetCenter( self.fpoint(0,0) )
            c.SetLayer(pcbnew.F_SilkS)
            self.board.Add(c)
  
        # slot center
        th_0 = 2*math.pi/self.slots
        la = 0.05
        for p in range(self.slots):
            xy_s = self.fpoint( 
                int( (1+la)*ri*math.cos(th_0*p)), 
                int((1+la)*ri*math.sin(th_0*p))
            )
            xy_e = self.fpoint( 
                int((1-la)*ro*math.cos(th_0*p)), 
                int((1-la)*ro*math.sin(th_0*p))
            )
            c = pcbnew.PCB_SHAPE(self.board)
            c.SetShape(pcbnew.SHAPE_T_SEGMENT)
            c.SetStart(xy_s)
            c.SetEnd(xy_e)
            c.SetLayer(pcbnew.F_SilkS)
            c.SetWidth( int(0.127*1e6) )
            self.board.Add(c)
        
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


    # event handlers (buttons)
    def on_close(self, event):
        self.pm.SaveAndUnregister()
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
    def on_btn_save(self, event):
        # persist first
        self.pm.SaveAndUnregister()
        self.pm.RegisterAndRestoreAll(self)
        # file dialog
        with wx.FileDialog(self, "Save KiMotor preset", wildcard="KMT files (*.kmt)|*.kmt",
                       style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
            fileDialog.SetFilename("kimotor.kmt")
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return   
            # copy and rename the persist file
            try:
                origin = self.pf
                target = fileDialog.GetPath()
                shutil.copyfile(origin, target)
            except IOError:
                wx.LogError("Cannot save current data in file '%s'." % target)

    def on_btn_load(self, event):
        with wx.FileDialog(self, "Load KiMotor preset", wildcard="KMT files (*.kmt)|*.kmt",
                        style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            try:
                origin = fileDialog.GetPath()
                target = self.pf
                tmp = fileDialog.GetDirectory() + "/kimotor.tmp"
                
                self.pm.SetPersistenceFile(tmp)
                self.pm.SaveAndUnregister()
                shutil.copyfile(origin, target)
                self.pm.SetPersistenceFile(target)
                self.pm.RegisterAndRestoreAll(self)
                #os.remove(tmp)
                
            except IOError:
                wx.LogError("Cannot open file '%s'." % origin)


    # combobox callbacks 
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

    def on_cb_mholes(self, event):
        event.Skip()


    # other callbacks    
    def on_nr_layers(self, event):
        self.nl = int(self.m_ctrlLayers.GetValue())
        event.Skip()

    