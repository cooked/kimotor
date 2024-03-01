# Copyright 2022 Stefano Cottafavi <stefano.cottafavi@gmail.com>
# SPDX-License-Identifier: GPL-2.0-only

import os
import shutil
import numpy as np
import math
import json
from datetime import datetime

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
        self.description = "KiMotor - Parametric PCB motor design"
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

    # parameters
    outline = None
    trmtype = None

    fpoint = None
    angle = None

    tthick = 35e-6 # [m] copper thickness (1oz layer specs)

    # fab capabilities (min)
    fc_jlcpcb_12 = {
        "track_width":  0.127, # (5mil)
        "track_space":  0.127, # (5mil)
        "via_hole":     0.15,
        "via_diameter": 0.25,
    } 

    # terminal footprint dict
    term_tht_db = {
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
    term_smd_db = {
        "1"     : "TestPoint_Pad_1.0x1.0mm",
        "1.5"   : "TestPoint_Pad_1.5x1.5mm",
        "2"     : "TestPoint_Pad_2.0x2.0mm",
        "2.5"   : "TestPoint_Pad_2.5x2.5mm",
        "3"     : "TestPoint_Pad_3.0x3.0mm",
        "4"     : "TestPoint_Pad_4.0x4.0mm",
    }
    term_db = {
        "THT"   : term_tht_db,
        "SMD"   : term_smd_db
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
            self.fsize = pcbnew.wxSize
        else:
            self.SCALE = pcbnew.FromMM(1)
            self.fpoint = pcbnew.VECTOR2I
            self.fpoint_vector = pcbnew.VECTOR_VECTOR2I
            self.fsize = pcbnew.VECTOR2I

        # kick-off persistence
        self.pf = os.path.join(
            pcbnew.SETTINGS_MANAGER.GetUserSettingsPath(),
            "kimotor.cfg"
        )

        self.init_persist(self.pf)
        self.init_path()
        self.init_nets()

        self.on_cb_outline(None)
        self.on_cb_trmtype(None)
    
    def eda_angle(self,angle):
        if self.KICAD_VERSION < 7:
            return angle *180/math.pi *100
        else:
            return pcbnew.EDA_ANGLE(angle, pcbnew.RADIANS_T)

    # init functions
    def init_persist(self, configFile):
        self.pm = PM.PersistenceManager.Get()
        self.pm.SetPersistenceFile(configFile)
        self.pm.RegisterAndRestoreAll(self)

    def get_parameters(self, caps):

        # get gui values and fix units (mm converted to nm where needed)

        self.outline = self.m_cbOutline.GetStringSelection()
        if self.outline=="Circle":
            self.n_edges = 0
        elif self.outline=="Square":
            self.n_edges = 4
        elif self.outline=="Hexagon":
            self.n_edges = 6
        elif self.outline=="Octagon":
            self.n_edges = 8
        else:
            self.n_edges = -1

        # terminals
        self.trmtype = self.m_cbTP.GetStringSelection()
        self.n_term = 2 if (self.m_cbScheme.GetStringSelection() == "1P") else ( 
            3 if (self.m_cbScheme.GetStringSelection() == "3P") else 4)
        
        self.n_layers = int(self.m_ctrlLayers.GetValue())
        self.lset = self.udpate_lset(self.n_layers)
        self.n_loops  = int(self.m_ctrlLoops.GetValue())
        self.n_phases = int(1 if (self.m_cbScheme.GetStringSelection() == "1P") else 3)
        self.n_slots  = int(self.m_ctrlSlots.GetValue())
        
        self.strategy = self.m_cbStrategy.GetSelection()

        self.trk_w = int(self.m_ctrlTrackWidth.GetValue() * self.SCALE) # track width
        self.dr = self.trk_w * 2                                        # track distance
        
        self.d_via = int(caps.get('via_diameter') * self.SCALE)   # min via size
        self.d_drill = int(caps.get('via_hole') * self.SCALE)   # min drill size

        # TODO: this to become a parameter (e.g. via grid size or something)
        self.via_rows = 2

        self.r_fill = int(self.m_ctrlRfill.GetValue() * self.SCALE)         # track fillet
        self.o_fill = int(self.m_ctrlFilletRadius.GetValue() * self.SCALE)  # outline fillet

        # various radius 
        self.r_in = int(self.m_ctrlDbore.GetValue() /2 * self.SCALE)
        self.r_out = int(self.m_ctrlDout.GetValue() /2 * self.SCALE) # board size
        self.r_coil_in = int(self.m_ctrlDin.GetValue() /2 * self.SCALE )
        self.r_coil_out = int(self.m_ctrlDend.GetValue() /2 * self.SCALE )
        
        self.w_mnt = int(self.m_ctrlWmnt.GetValue() * self.SCALE) # width of the outer no-soldermask annular zone

        # TODO: place terminals based on their size
        #self.rtrm = int(self.m_ctrlDterm.GetValue()/2 * self.SCALE)
        self.r_term = (self.r_coil_out + (self.r_coil_out + self.w_mnt)) / 2

        
        self.mhs = self.m_cbMountSize.GetStringSelection()
        self.n_mh_out = int(self.m_mhOut.GetValue())
        self.r_mh_out = int(self.m_mhOutR.GetValue() /2 * self.SCALE)
        self.n_mh_in = int(self.m_mhIn.GetValue())
        self.r_mh_in = int(self.m_mhInR.GetValue() /2 * self.SCALE)

        # text
        self.txt_size = int(0.5 * self.SCALE)
        self.txt_loc = int(self.r_out - 3*self.txt_size)

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

        # ensure only one separator
        self.fp_path = os.path.normpath(self.fp_path) + os.sep

        # no library found
        if self.fp_path is None:
            wx.LogError("Footprint library not found - Make sure the KiCad paths are properly configured.")

    def init_nets(self):
        # init paths
        gnd = pcbnew.NETINFO_ITEM(self.board, "gnd")
        coil = pcbnew.NETINFO_ITEM(self.board, "coil")
        self.board.Add(gnd)
        self.board.Add(coil)

    def udpate_lset(self, n_layers):
        lset = [pcbnew.F_Cu]
        if n_layers >= 4:
            lset.append(pcbnew.In1_Cu)
            lset.append(pcbnew.In2_Cu)
        if n_layers >= 6:
            lset.append(pcbnew.In3_Cu)
            lset.append(pcbnew.In4_Cu)
        if n_layers >= 8:
            lset.append(pcbnew.In5_Cu)
            lset.append(pcbnew.In6_Cu)
        if n_layers >= 10:
            lset.append(pcbnew.In7_Cu)
            lset.append(pcbnew.In8_Cu)
        if n_layers >= 12:
            lset.append(pcbnew.In9_Cu)
            lset.append(pcbnew.In10_Cu)
        if n_layers >= 14:
            lset.append(pcbnew.In11_Cu)
            lset.append(pcbnew.In12_Cu)
        if n_layers >= 16:
            lset.append(pcbnew.In13_Cu)
            lset.append(pcbnew.In14_Cu)
        if n_layers >= 18:
            lset.append(pcbnew.In15_Cu)
            lset.append(pcbnew.In16_Cu)
        if n_layers >= 20:
            lset.append(pcbnew.In17_Cu)
            lset.append(pcbnew.In18_Cu)   
        lset.append(pcbnew.B_Cu)

        return lset


    # core functions

    def generate(self):

        # get GUI parameters
        self.get_parameters(self.fc_jlcpcb_12)

        # generate and connect coils
        coils = self.do_windings(
            self.r_coil_in, 
            self.r_coil_out,
            self.dr,
            self.n_slots,
            self.n_phases,
            self.n_loops,
            self.lset,
            self.strategy)

        # generate phase rings
        [cnx_seg, cnx_str, cri] = self.do_rings(
            self.r_coil_in,
            max(self.dr, self.d_via),
            self.n_slots,
            self.n_phases)
        
        self.do_junctions(
            self.r_coil_in,
            self.dr,
            self.n_slots,
            self.n_phases,
            coils, 
            cnx_seg, 
            cnx_str)
        
        # terminals
        if self.trmtype != "None":
            trm_lib = self.fp_path + 'Connector_Wire.pretty' if self.trmtype=='THT' else 'TestPoint.pretty'
            trm_fp = self.term_db.get(self.trmtype).get(self.m_termSize.GetStringSelection())

            self.do_terminals(
                self.r_term,
                self.n_term,
                self.r_coil_in,
                coils,
                trm_lib, trm_fp)

        # create outline, mounting holes and thermal zones
        if self.outline != "None":
            self.do_outline(
                self.r_in, 
                self.r_out, 
                self.n_edges, 
                self.o_fill)
            
            self.do_mounting_holes(
                self.r_mh_out,
                6 if self.outline=="Circle" else self.n_edges,
                self.r_mh_in,
                self.n_mh_in,
                self.n_edges,
                hs=self.mhs)
            
            self.do_thermal_zones(
                self.r_out,
                cri)
        
        # draw silkscreen
        self.do_silkscreen(
            self.r_coil_in,
            self.r_coil_out+self.trk_w, 
            self.n_slots)

        # update board
        pcbnew.Refresh()

        # TODO: all stats shall be moved here
        # stats (single pole only)
        
        #self.board.Groups()[0].RunOnChildren(item: {item.Type()})
        #wx.LogWarning(f'{item.Type()}')
        #if p==0:
        self.tl = 0 #self.stats_length(self.board)
        self.tr = 0 #self.stats_rlc(self.board, self.trk_w/self.SCALE/1000, self.tthick)

        # update gui stats
        self.lbl_phaseLength.SetLabel( '%.2f' % self.tl )
        self.lbl_phaseR.SetLabel( '%.2f' % self.tr )

        self.btn_clear.Enable(True)

    def coil_tracker(self, waypts, layer, n_loops, group):
        """ Connnect the coil waypoints with PCB tracks on the assigned layer  

        Args:
            waypts (numpy.matrix): set of the coil waypoints
            layer (pcbnew.LAYER): layer on which the tracks are created
            n_loops (int): number of coil loops

        Returns:
            list : list of coil start and end points
        """

        net_coil = self.board.FindNet("coil")

        # index of current point
        ip = 0 
        t0 = None

        # define how many sides 
        n_side = n_loops*4 - 1 

        for side in range(n_side):

            # side start point
            side_s = self.fpoint( 
                int(waypts[ip][0,0]), 
                int(waypts[ip][0,1]))
            
            # even sides (0,2,4,etc.)
            if not side%2:
                ip += 1
                t = pcbnew.PCB_ARC(self.board)
                t.SetMid(
                    self.fpoint(
                        int(waypts[ip][0,0]),
                        int(waypts[ip][0,1])))

                # 1: outer side, -1: inner side
                side = -1 if not side%4 else 1
            
            # odd sides
            else:
                t = pcbnew.PCB_TRACK(self.board)

            ip += 1
            side_e = self.fpoint( 
                int(waypts[ip][0,0]), 
                int(waypts[ip][0,1]))
            t.SetNet(net_coil)
            t.SetWidth( self.trk_w )
            t.SetLayer( layer )
            t.SetStart( side_s )
            t.SetEnd( side_e )
            self.board.Add(t)

            # fillet
            if side > 0 and self.r_fill > 0:
                fa = self.fillet(self.board, t0, t, self.r_fill, side)
                #group.AddItem(fa)

            # add to group
            group.AddItem(t)

            t0 = t
        
        coil_se = []
        coil_se.append( self.fpoint( int(waypts[0][0,0]), int(waypts[0][0,1]) ) )
        coil_se.append( t.GetEnd() )

        return coil_se

    def do_windings(self, ri, ro, dr, n_slots, n_phases, n_loops=1, lset=None, mode=0):
        """ Generate the coil tracks (with fillet) on the given PCB layers

        Args:
            ri (int): coil inner radius
            ro (int): coil outer radius
            dr (int): min track spacing
            n_slots (int): number of motor slots
            n_loops (int): number of coil loops (per layer)
            lset (list): list of the PCB layers to use
            mode (int): 0: parallel coil sides, 1: radial coil sides

        Returns:
            list: all windings start and end points, grouped by phase 
        """
        net_coil = self.board.FindNet("coil")

        th0 = 2*math.pi/n_slots

        r_via = ri - dr
        thv = math.atan2(dr, r_via)

        r_via_o = ro - n_loops*dr
        thv_o = math.atan2(dr, r_via_o)

        n_via = len(lset)/2
        vias = range(int(-n_via/2), int(n_via/2))
        

        # generate coil waypoints
        if mode == 0:
            # TODO: update
            waypts_cw, pcu0m, pcu0mi = ksolve.parallel( ri, ro, dr, th0, n_loops, 0 )
            waypts_ccw, pcu1m, pcu1mi = ksolve.parallel( ri, ro, dr, th0, n_loops, 1 )
        else:
            waypts_cw = ksolve.coil_planner( "radial", ri, ro, dr, n_slots, n_loops, "cw" )
            waypts_ccw = ksolve.coil_planner( "radial", ri, ro, dr, n_slots, n_loops, "ccw" )

            waypts_cw1 = ksolve.coil_planner( "radial", ri, ro, dr, n_slots, n_loops, "cw", 1 )
            waypts_ccw1 = ksolve.coil_planner( "radial", ri, ro, dr, n_slots, n_loops, "ccw", 1 )

        windings = []
        for p in range(n_phases):
            windings.append([])
        

        for slot in range(n_slots):

            pgroup = pcbnew.PCB_GROUP( self.board )
            pgroup.SetName("slot_"+str(slot))
            self.board.Add(pgroup)

            # start and end points of single winding
            winding_se = []

            # rotation matrix
            th = th0 * slot 
            R = np.array([
                [math.cos(th), -math.sin(th)],
                [math.sin(th), math.cos(th)]])
            
            # rotate coil waypoints to the slot position (around PCB motor axis)
            waypts_cw_R = np.matmul(R, waypts_cw.transpose()).transpose()
            waypts_ccw_R = np.matmul(R, waypts_ccw.transpose()).transpose()
            waypts_cw1_R = np.matmul(R, waypts_cw1.transpose()).transpose()
            waypts_ccw1_R = np.matmul(R, waypts_ccw1.transpose()).transpose()

            for i, layer in enumerate(lset):
                
                # pick the right "template" of waypoints
                if i==0 or i==len(lset)-1:
                    wp = waypts_ccw_R if i%2 else waypts_cw_R
                else:
                    wp = waypts_ccw1_R if i%2 else waypts_cw1_R

                # generate coil 
                coil_se = self.coil_tracker(wp, layer, n_loops, pgroup)
                
                # connect coils across layers to create the winding
                if i%2 and i<len(lset):
                    
                    # on odd layers (coil CCW) stitch coils' end points 
                    
                    iv = int(i/2)

                    xy_v = self.fpoint( 
                        int(r_via_o*math.cos(th + thv_o*vias[iv])), 
                        int(r_via_o*math.sin(th + thv_o*vias[iv])))
                    
                    # stitch
                    via = pcbnew.PCB_VIA(self.board)
                    via.SetViaType(pcbnew.VIATYPE_THROUGH)
                    via.SetPosition( xy_v )
                    via.SetDrill( self.d_drill )
                    via.SetWidth( self.d_via )
                    self.board.Add(via)
                    a = pcbnew.PCB_ARC(self.board)
                    a.SetNet(net_coil)
                    a.SetLayer(lset[i-1])
                    a.SetWidth(self.trk_w)
                    a.SetStart( coil_se[1] )
                    a.SetEnd(
                        self.fpoint( 
                            int((r_via_o+dr)*math.cos(th + thv_o*vias[iv])), 
                            int((r_via_o+dr)*math.sin(th + thv_o*vias[iv]))))
                    a.SetMid(
                        self.fpoint( 
                            int((r_via_o+dr)*math.cos(th + thv_o*vias[iv] /2 )), 
                            int((r_via_o+dr)*math.sin(th + thv_o*vias[iv] /2 ))))
                    self.board.Add(a)
                    t = pcbnew.PCB_TRACK(self.board)
                    t.SetNet(net_coil)
                    t.SetWidth( self.trk_w )
                    t.SetLayer( lset[i] )
                    t.SetStart( a.GetEnd() )
                    t.SetEnd( xy_v )
                    self.board.Add(t)
                    t = pcbnew.PCB_TRACK(self.board)
                    a.SetNet(net_coil)
                    t.SetWidth( self.trk_w )
                    t.SetLayer( lset[i-1] )
                    t.SetStart( a.GetEnd() )
                    t.SetEnd( xy_v )
                    self.board.Add(t)


                elif len(lset)>2 and not i%2 and i>0:

                    # on even layers (coil CW), but first, stitch coils' start points 

                    iv = int(i/2)

                    xy_v = self.fpoint( 
                        int(r_via*math.cos(th + thv*vias[iv])), 
                        int(r_via*math.sin(th + thv*vias[iv])))
                    
                    # stitch
                    via = pcbnew.PCB_VIA(self.board)
                    via.SetViaType(pcbnew.VIATYPE_THROUGH)
                    via.SetPosition( xy_v)
                    via.SetDrill( self.d_drill )
                    via.SetWidth( self.d_via )
                    self.board.Add(via)
                    
                    a = pcbnew.PCB_ARC(self.board)
                    a.SetNet(net_coil)
                    a.SetLayer(lset[i-1])
                    a.SetWidth(self.trk_w)
                    a.SetStart( coil_se[0] )
                    a.SetEnd(
                        self.fpoint( 
                            int((r_via+dr)*math.cos(th + thv*vias[iv])), 
                            int((r_via+dr)*math.sin(th + thv*vias[iv]))))
                    a.SetMid(
                        self.fpoint( 
                            int((r_via+dr)*math.cos(th + thv*vias[iv] /2 )), 
                            int((r_via+dr)*math.sin(th + thv*vias[iv] /2 ))))
                    self.board.Add(a)

                    t = pcbnew.PCB_TRACK(self.board)
                    t.SetNet(net_coil)
                    t.SetWidth( self.trk_w )
                    t.SetLayer( lset[i] )
                    t.SetStart( a.GetEnd() )
                    t.SetEnd( xy_v )
                    self.board.Add(t)
                    t = pcbnew.PCB_TRACK(self.board)
                    t.SetNet(net_coil)
                    t.SetWidth( self.trk_w )
                    t.SetLayer( lset[i-1] )
                    t.SetStart( a.GetEnd() )
                    t.SetEnd( xy_v )
                    self.board.Add(t)

                # append first and last only
                if i==0 or i==len(lset)-1:
                    winding_se.append(coil_se[0])
   
            # store coils by phase
            windings[ slot % n_phases ].append(winding_se)

        return windings

    def do_rings(self, r_in, dr, n_slot, n_phase):
        """ Create the arc segments that connect the coils of the same phase

        Args:
            r_in (int): radial position of the coil inner end
            dr (int): min track spacing
            n_slot (int): number of motor slots
            n_phase (int): number of motor phases
        """

        # rings spaced from coils
        r_in -= 2*dr

        # slot angular width
        th0 = 2*math.pi/n_slot
        # segment start/end points angular shift
        th_shift_start  = th0/2
        th_shift_end    = -th0
        
        # number of distinct segments on each phase ring 
        n_rc = int(n_slot/n_phase)-1

        # all segments, of all the phase rings
        conns_t = []
        # phase-phase connection
        cnx_star = None

        # create phase tracks
        for p in range(n_phase):

            # radial location of the ring
            cri = r_in - p*dr
            
            thv = math.atan2(dr,cri)

            # segments on the same phase ring
            segs_t = []

            for i_rc in range(n_rc):
                # find directions of start, end, mid points of the arc segment
                th_s = th0*( p + i_rc*n_phase ) + th_shift_start - thv
                th_e = th_s + th0*n_phase + th_shift_end + 2*thv
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
                ths = -3*th0 + th0/2 - thv
                the = -1*th0 + th0/2 - thv
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

    def do_junctions(self, r_in, dr, n_slot, n_phase, coils, rings, cnx_str):
        """ Create the jumper segments that connect the coil terminations with the 
        race tracks of the phase connecting rings

        Args:
            r_in (int): radial position of the coil inner end
            dr (int): min track spacing
            n_slot (int): number of motor slots
            n_phase (int): number of motor phases
            coils (list): contains start and end points of each coil, by phase
            rings (list): contains start and end points of each ring segment, by phase

        """

        # slot angular width
        th0 = 2*math.pi/n_slot

        thv = math.atan2(dr,r_in)

        th_shift_start = th0/2 - thv
        th_shift_end = -2*th_shift_start
        
        r_in -= dr

        # number of segments on each phase ring 
        n_ring_seg = int(n_slot/n_phase)-1

        for phase in range(n_phase):
                        
            for seg in range(n_ring_seg):
                
                ring_seg_s = rings[phase][seg][0]
                ring_seg_e = rings[phase][seg][1]
                
                #c1s = coil_p[p][i][0]
                coil_1_e = coils[phase][seg][1]

                coil_2_s = coils[phase][seg+1][0]
                coil_2_e = coils[phase][seg+1][1]

                if seg <= n_ring_seg:
                    j = pcbnew.PCB_TRACK(self.board)
                    j.SetLayer(pcbnew.B_Cu)
                    j.SetWidth(self.trk_w)
                    j.SetStart( coil_1_e )
                    j.SetEnd( ring_seg_s )
                    self.board.Add(j)

                    if seg == 0:
                        via = pcbnew.PCB_VIA(self.board)
                        via.SetPosition( ring_seg_s )
                        via.SetDrill( self.d_drill )
                        via.SetWidth( self.d_via )
                        self.board.Add(via)    

                    if phase==0 or seg==n_ring_seg-1:
                        j = pcbnew.PCB_TRACK(self.board)
                        j.SetLayer(pcbnew.F_Cu)
                        j.SetWidth(self.trk_w)
                        j.SetStart( coil_2_s )
                        j.SetEnd( ring_seg_e )
                        self.board.Add(j)

                    else:
                        # cross under the other phases
                        th_s = th0*( phase + seg*n_phase ) + th_shift_start
                        th_e = th_s + th0*n_phase + th_shift_end
                        xy_a = self.fpoint(
                            int(r_in*math.cos(th_e)), 
                            int(r_in*math.sin(th_e)))
                        
                        j = pcbnew.PCB_TRACK(self.board)
                        j.SetLayer(pcbnew.B_Cu)
                        j.SetWidth(self.trk_w)
                        j.SetStart( ring_seg_e )
                        j.SetEnd( xy_a )
                        self.board.Add(j)
                        via = pcbnew.PCB_VIA(self.board)
                        via.SetPosition( ring_seg_e )
                        via.SetDrill( self.d_drill )
                        via.SetWidth( self.d_via )
                        self.board.Add(via)

                        j = pcbnew.PCB_TRACK(self.board)
                        j.SetLayer(pcbnew.F_Cu)
                        j.SetWidth(self.trk_w)
                        j.SetStart( xy_a )
                        j.SetEnd( coil_2_s )
                        self.board.Add(j)
                        via = pcbnew.PCB_VIA(self.board)
                        via.SetPosition( xy_a )
                        via.SetDrill( self.d_drill )
                        via.SetWidth( self.d_via )
                        self.board.Add(via)

                if seg > 0:
                    # jumper at each coil start, but the first coil, for each phase  
                    j = pcbnew.PCB_TRACK(self.board)
                    j.SetLayer(pcbnew.B_Cu)
                    j.SetWidth(self.trk_w)
                    j.SetStart( coil_1_e )
                    j.SetEnd( ring_seg_s )
                    self.board.Add(j)
                    via = pcbnew.PCB_VIA(self.board)
                    via.SetPosition( ring_seg_s )
                    via.SetDrill( self.d_drill )
                    via.SetWidth( self.d_via )
                    self.board.Add(via)

                # star-connect jumper
                if seg == n_ring_seg-1:
                    j = pcbnew.PCB_TRACK(self.board)
                    j.SetLayer(pcbnew.B_Cu)
                    j.SetWidth(self.trk_w)
                    j.SetStart( coil_2_e )
                    j.SetEnd( cnx_str[phase] )
                    self.board.Add(j)

    def do_terminals(self, r_term, n_term, r_coil_in, coils, lib='',fp=''):
        """ Create the motor terminals, and the tracks that connect the terminals to the coils

        Args:
            r_term (in): radial position of the motor terminals
            n_term (in): number of motor terminals
            r_coil_in (in): radial position of the coil inner end
            coils (list): list of coils tracks
            lib (string): footprint library absolute path
            fp (string): terminal footprint name
        """

        net_coil = self.board.FindNet("coil")

        # base angle, half (to position terminals), quarter (to locate arc track mid-point)
        th0 = 2*math.pi/self.n_slots
        thr = th0/4

        Rcw = np.array([
            [math.cos(thr), -math.sin(thr)],
            [math.sin(thr), math.cos(thr)],
        ])

        for i in range(n_term):

            # radial to cartesian coords of terminal, aux corner, coil start 
            th = th0*i - th0/2

            ax = r_coil_in*math.cos(th)
            ay = r_coil_in*math.sin(th)
            tp = np.matmul(Rcw, np.array([ax,ay]))  

            xy_t = self.fpoint( 
                int(r_term*math.cos(th)), 
                int(r_term*math.sin(th)))
            xy_a = self.fpoint( int(ax), int(ay) )
            xy_c = coils[i][0][0]

            # terminal
            if self.trmtype != "None":
                m = pcbnew.FootprintLoad(lib, fp)
                m.Value().SetVisible(False)
                lib_name= lib.split('.')[-2].split('/')[-1]
                m.SetFPIDAsString(lib_name + ":" + fp)
                m.SetPosition(xy_t)
                m.Rotate(xy_t, self.eda_angle(-th))
                for p in m.Pads():
                    p.SetNet(net_coil)
                
                # REF
                dth = 0.05 #rad
                m.Reference().SetPosition( 
                    self.fpoint( 
                        int(r_term*math.cos(th+dth)), 
                        int(r_term*math.sin(th+dth))))
                m.SetReference( "A" if i==0 else ("B" if i==1 else "C") )
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

    def do_outline(self, r_in, r_out, n_edge=0, r_fill=0):

        # r_in: inner board radius (shaft bore)
        # r_out: outer board radius (inscribed circle for polygons)
        # n_edge: number of board edges (0: circle, 4: square, 4+: polygon)
        # r_fill: outline fillet radius

        edge = pcbnew.PCB_SHAPE(self.board, pcbnew.SHAPE_T_CIRCLE)
        edge.SetCenter( self.fpoint(0,0) )
        edge.SetStart( self.fpoint(0,0) )
        edge.SetEnd( self.fpoint(r_in,0) )
        edge.SetLayer( pcbnew.Edge_Cuts )
        self.board.Add(edge)

        if n_edge == 0:
            edge = pcbnew.PCB_SHAPE(self.board, pcbnew.SHAPE_T_CIRCLE)
            edge.SetCenter( self.fpoint(0,0) )
            edge.SetStart( self.fpoint(0,0) )
            edge.SetEnd( self.fpoint(r_out,0) )
            edge.SetLayer( pcbnew.Edge_Cuts )
            self.board.Add(edge)

        elif n_edge >= 4:
            r_out /= math.cos(math.pi/n_edge) # circumscribed polygon
            #rp = r2 * math.cos(math.pi/ne) # inscribed polygon
            thp = 2*math.pi/n_edge
            tho = thp/2

            points = []
            for i in range(n_edge):
                points.append(
                    self.fpoint(
                        int(r_out * math.cos(i*thp+tho)), 
                        int(r_out * math.sin(i*thp+tho)) )
                )

            segs = {}
            for i in range(n_edge):
                seg = pcbnew.PCB_SHAPE(self.board, pcbnew.SHAPE_T_SEGMENT)
                seg.SetStart( points[i] )
                seg.SetEnd( points[(i+1)%n_edge] )
                seg.SetLayer( pcbnew.Edge_Cuts )
                self.board.Add(seg)
                segs[i] = seg
            # fillet
            #if r_fill:
            #    for i in range(n_edge):
            #        a = segs[i]
            #        b = segs[(i+1) % 4]
            #        self.fillet_outline(self.board, a, b, r_fill)

    def do_mounting_holes(self, r_mh_out=0, n_mh_out=0, r_mh_in=0, n_mh_in=0, n_edge=0, hs="None"):

        # no: number of outer mount points
        # ni: number of inner shaft mount points
        # see https://forum.kicad.info/t/place-update-footprint-with-python/23103

        if hs != "None":
            fp_lib = self.fp_path + 'MountingHole.pretty'
            fp = self.mhole_db.get(hs)
        else:
            return

        ni_gnd = self.board.FindNet("gnd")

        if n_edge>0:
            r_mh_out /= math.cos(math.pi/n_edge) 

        th0 = 2*math.pi/n_mh_out

        # outer
        for i in range(n_mh_out):
            m = pcbnew.FootprintLoad( fp_lib, fp )
            m.Reference().SetVisible(False)
            m.Value().SetVisible(False)
            m.SetReference('M'+str(i))
            m.SetPosition(
                self.fpoint( 
                    int(r_mh_out * math.cos(th0*i + th0/2)), 
                    int(r_mh_out * math.sin(th0*i + th0/2))))
            for pad in m.Pads():
                pad.SetNet(ni_gnd)
            self.board.Add(m)

        # inner
        if n_mh_in:
            th0 = 2*math.pi/n_mh_in
            for i in range(n_mh_in):
                m = pcbnew.FootprintLoad( fp_lib, fp )
                m.SetReference('')
                m.SetPosition(
                self.fpoint( 
                    int(r_mh_in * math.cos(th0*i + th0/2)), 
                    int(r_mh_in * math.sin(th0*i + th0/2))))
                for pad in m.Pads():
                    pad.SetNet(ni_gnd)
                self.board.Add(m)

    def do_thermal_zones(self, r_out, r_nosm_in, r_nosm_out=0, nvias=36):
        # see refill:
        # https://forum.kicad.info/t/python-scripting-refill-all-zones/35834
        # TODO: add cooling fingers (TBD)

        ni_gnd = self.board.FindNet("gnd")

        # get our layers right
        ls = pcbnew.LSET()
        for ly in self.lset:
            ls.addLayer(ly)

        # prepare filler
        filler = pcbnew.ZONE_FILLER(self.board)

        # outer zone
        z = pcbnew.ZONE(self.board)
        if self.n_edges == 0:
            cpl = kla.circle_to_polygon( r_out, 100 )
            cp = []
            for c in cpl:
                cp.append(self.fpoint(c[0],c[1]))
            z.AddPolygon( self.fpoint_vector(cp) )
        elif self.n_edges >= 4:
            ro = int(r_out / math.cos(math.pi/self.n_edges) )
            p = []
            p.append( self.fpoint(ro,ro) )
            p.append( self.fpoint(ro,-ro) )
            p.append( self.fpoint(-ro,-ro) )
            p.append( self.fpoint(-ro,ro) )
            z.AddPolygon( self.fpoint_vector(p) )

        # shaft zone
        cpl = kla.circle_to_polygon( self.r_coil_out + 2*self.trk_w, 100 )
        cp = []
        for c in cpl:
            cp.append(self.fpoint(c[0],c[1]))

        z.AddPolygon( self.fpoint_vector(cp) )
        z.SetLayerSet(ls)
        z.SetNet(ni_gnd)
        z.SetLocalClearance( self.trk_w )
        z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_NEVER)
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
        self.board.Add(z)

        # inner (shaft) annular
        z = pcbnew.ZONE(self.board)
        cpl = kla.circle_to_polygon( r_nosm_in, 100 )
        cp = []
        for c in cpl:
            cp.append(self.fpoint(c[0],c[1]))

        z.AddPolygon( self.fpoint_vector(cp) )
        z.SetLayerSet(ls)
        z.SetNet(ni_gnd)
        z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_NEVER)
        self.board.Add(z)



        # no solder mask
        nls = pcbnew.LSET()
        nls.addLayer(pcbnew.F_Mask)
        nls.addLayer(pcbnew.B_Mask)
        z = pcbnew.ZONE(self.board)

        if self.n_edges == 0:
            cpl = kla.circle_to_polygon( r_out, 100 )
            cp = []
            for c in cpl:
                cp.append(self.fpoint(c[0],c[1]))
            z.AddPolygon( self.fpoint_vector(cp) )
            #cpl = kla.circle_to_polygon( self.r_mholes + self.trk_w,  100 )
            cpl = kla.circle_to_polygon( r_out - self.w_mnt,  100 )
            cp = []
            for c in cpl:
                cp.append(self.fpoint(c[0],c[1]))
            z.AddPolygon( self.fpoint_vector(cp) )

        elif self.n_edges >= 4:

            r2 = int(r_out / math.cos(math.pi/self.n_edges))
            th0 = 2*math.pi/self.n_edges
            points = []
            for i in range(self.n_edges):
                points.append(
                    self.fpoint(
                        int(r2 * math.cos(th0*i+th0/2)), 
                        int(r2 * math.sin(th0*i+th0/2))))
            z.AddPolygon( self.fpoint_vector(points) )
            
            points = []
            r2 = int((r_out - self.w_mnt) / math.cos(math.pi/self.n_edges))
            for i in range(self.n_edges):
                points.append(
                    self.fpoint(
                        int(r2 * math.cos(th0*i+th0/2)), 
                        int(r2 * math.sin(th0*i+th0/2))))
            z.AddPolygon( self.fpoint_vector(points) )

        z.SetLayerSet(nls)
        z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_NEVER)
        self.board.Add(z)

        z = pcbnew.ZONE(self.board)
        cpl = kla.circle_to_polygon(r_nosm_in, 100)
        cp = []
        for c in cpl:
            cp.append(self.fpoint(c[0],c[1]))

        z.AddPolygon( self.fpoint_vector(cp) )
        z.SetLayerSet(nls)
        z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_NEVER)
        self.board.Add(z)

        filler.Fill(self.board.Zones())


        # via stitching
        # drv = (r_out - self.r_mholes) / (self.via_rows+1)
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

    def do_silkscreen(self, r_in, r_out, n_slots):

        th0 = 2*math.pi/n_slots

        # pcb label
        pcb_txt = pcbnew.PCB_TEXT(self.board)
        pcb_txt.SetText(
            datetime.today().strftime('%Y%m%d') + 
            "_ly" + str(self.n_layers) +
            "_s" + str(self.n_slots) +
            "_w" + str(self.n_loops)
        )
        pcb_txt.SetPosition( self.fpoint(0,self.txt_loc) )
        pcb_txt.SetTextSize( self.fsize(self.txt_size,self.txt_size) )
        pcb_txt.SetLayer(pcbnew.F_SilkS)
        self.board.Add(pcb_txt)

        # mark active coil ring
        for r in [r_in, r_out]:
            c = pcbnew.PCB_SHAPE(self.board)
            c.SetShape(pcbnew.SHAPE_T_CIRCLE)
            c.SetFilled(False)
            c.SetStart( self.fpoint(0,0) )
            c.SetEnd( self.fpoint(r,0) )
            c.SetCenter( self.fpoint(0,0) )
            c.SetLayer(pcbnew.F_SilkS)
            self.board.Add(c)
  
        # slot center
        la = 0.05
        for slot in range(n_slots):
            xy_s = self.fpoint( 
                int( (1+la)*r_in*math.cos(th0*slot)), 
                int((1+la)*r_in*math.sin(th0*slot))
            )
            xy_e = self.fpoint( 
                int((1-la)*r_out*math.cos(th0*slot)), 
                int((1-la)*r_out*math.sin(th0*slot))
            )
            c = pcbnew.PCB_SHAPE(self.board)
            c.SetShape(pcbnew.SHAPE_T_SEGMENT)
            c.SetStart(xy_s)
            c.SetEnd(xy_e)
            c.SetLayer(pcbnew.F_SilkS)
            c.SetWidth( int(0.127*1e6) )
            self.board.Add(c)
        
        return


    def fillet(self, board, t1, t2, r, side=1):
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
        
        # trim tracks
        t1.SetEnd( self.fpoint(int(p1[0]),int(p1[1]))  )
        t2.SetStart( self.fpoint(int(p2[0]),int(p2[1]))  )

        return t

    def fillet_outline(self, board, a, b, r):

        c = kla.line_line_center(a,b,r)
        # trim point track1
        l1 = kla.line_points(a)
        p1 = kla.circle_line_tg( l1, c, r)
        # trim point track2
        l2 = kla.line_points(b)
        p2 = kla.circle_line_tg( l2, c, r)
        # arc mid-point
        ae = a.GetEnd()
        la = np.array([c, [ae.x, ae.y, 0]])
        lv = kla.line_vec(la)
        m = c + np.dot(r, lv)


        # generate fillet track
        f = pcbnew.PCB_SHAPE(board, pcbnew.SHAPE_T_ARC)

        wx.LogWarning(f'{p1[0]} {p1[1]}')
        f.SetStart( self.fpoint(int(p1[0]),int(p1[1])) )
        #f.SetMid( self.fpoint(int(m[0]),int(m[1])) )
        f.SetEnd( self.fpoint(int(p2[0]),int(p2[1])) )

        f.SetLayer(a.GetLayer())
        f.SetWidth(a.GetWidth())
        board.Add(f)

        # trim edges
        a.SetEnd( self.fpoint(int(p1[0]),int(p1[1]))  )
        b.SetStart( self.fpoint(int(p2[0]),int(p2[1]))  )

    def fillet_outline_old(self, board, a, b, fillet_value):
        ## borrowed from fillet_helper.py
        ## https://github.com/tywtyw2002/FilletEdge/blob/master/fillet_helper.py

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

        a_v = self.fpoint(
            (a.GetEndX() - a.GetStartX()) * a_reverse,
            -(a.GetEndY() - a.GetStartY()) * a_reverse
        )
        b_v = self.fpoint(
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
        if self.m_cbOutline.GetStringSelection() == "None":
            self.m_ctrlDout.Enable(False)
            self.m_ctrlFilletRadius.Enable(False)
        elif self.m_cbOutline.GetStringSelection() == "Circle":
            self.m_ctrlDout.Enable(True)
            self.m_ctrlFilletRadius.Enable(False)
        else:
            self.m_ctrlDout.Enable(True)
            #self.m_ctrlFilletRadius.Enable(True)
            self.m_ctrlFilletRadius.Enable(False)

        if event is not None:
            event.Skip()

    def on_cb_trmtype(self, event):
        pads = self.m_cbTP.GetStringSelection()

        if pads == "None":
            self.m_termSize.Enable(False)

        elif pads == "THT" or pads == "SMD":
            keys = self.term_db.get(pads).keys()
            for i,k in enumerate(keys):
                self.m_termSize.SetString(i,k)
            while len(keys) < self.m_termSize.GetCount():
                self.m_termSize.Delete( self.m_termSize.GetCount()-1 )

            self.m_termSize.SetValue( 
                self.m_termSize.GetString(
                    self.m_termSize.GetCurrentSelection()))

            self.m_termSize.Enable(True)

        if event is not None:
            event.Skip()

    def on_cb_mholes(self, event):
        event.Skip()


    # other callbacks    
    def on_nr_layers(self, event):
        self.n_layers = int(self.m_ctrlLayers.GetValue())
        event.Skip()

    