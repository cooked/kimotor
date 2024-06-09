# Copyright 2022-2024 Stefano Cottafavi <stefano.cottafavi@gmail.com>.
# SPDX-License-Identifier: GPL-2.0-only

import math
import numpy as np
from . import kimotor_linalg as kla
import wx

def coil_planner(type, r_in, r_out, dr, n_slot, n_loop, dir, start=0):
    if type == "radial":
        return radial(r_in, r_out, dr, n_slot, n_loop, dir, start)

def parallel(r1, r2, dr, th, turns, dir):
        """ Compute layout points for coil with sides always aligned to radius

        Args:
            r1 (int): coil inner radius
            r2 (int): coil outer radius
            dr (int): spacing between coil loops (and also adj. coils)
            th (float): coil trapezoid angle 
            turns (int): number of coil loops (windings)
            dir (int): coil direction, from larger to smaller loop (0:CW normal, 1:CCW rverse)

        Returns:
            matrix, matrix, matrix: corners (excl. arc mids), outer arc mids, inner arc mids
        """

        pts = []
        mds = []
        mdsi = []

        # points 
        c = [0,0,0]
        l0 = np.array([ c, [r1*math.cos(th/2), r1*math.sin(th/2), 0] ])
        l0 = kla.line_offset(l0, -dr)
        
        for turn in range(turns):
            # offset line
            lr = kla.line_offset(l0, -turn*dr)
            # solve corners and order them
            pc1 = kla.circle_line_intersect(lr, c, r1+turn*dr)
            pc1 = pc1[0:2]
            pc2 = kla.circle_line_intersect(lr, c, r2-turn*dr)
            pc2 = pc2[0:2]
            pc3 = np.array([ pc2[0],-pc2[1] ])
            pc4 = np.array([ pc1[0],-pc1[1] ])
            if dir == 0:
                pts.extend([pc1, pc2, pc3, pc4])
            else:
                pts.extend([pc4, pc3, pc2, pc1])
            
            # solve outer and inner mid-points
            pm = np.array([ r2-turn*dr, 0 ])
            pmi = np.array([ r1+turn*dr, 0 ])
            mds.extend([pm])
            mdsi.extend([pmi])

        pm = np.matrix(pts)     # points, excl. arc mids
        mm = np.matrix(mds)     # arc (outer) mids only
        mmi = np.matrix(mdsi)    # arc (inner) mids only

        return pm, mm, mmi

def radial(r_in, r_out, dr, n_slot, n_loop, dir, start=0):
        """ Compute layout points for coil with sides aligned to the local radial direction

        Args:
            r_in (int): coil inner radius
            r_out (int): coil outer radius
            dr (int): spacing between coil loops (as well as adjacent coils)
            n_slot (in): number of slots
            n_loop (int): number of coil loops
            start (int): where does the coil start (0: wedge start, 1: wedge mid )
            dir (string): coil direction, from larger to smaller loop ("cw" or "ccw" from an  observer looking down from Z+ axis)

        Returns:
            numpy.matrix: list of coil waypoints
        """

        # coil trapezoid angle
        th = 2*math.pi/n_slot

        waypts = []

        # center
        c = [0,0,0]
        
        # angular shift of first arc and last arc mid-mid-points
        Rcw = np.array([
            [math.cos(th/4), -math.sin(th/4)],
            [math.sin(th/4), math.cos(th/4)],
        ])

        # reference radial line
        l0 = np.array([ c, [r_in*math.cos(th/2), r_in*math.sin(th/2), 0] ])

        for loop in range(n_loop):
            
            # solve corner waypoint
            lr = kla.line_offset(l0, -dr)
            wp1 = kla.circle_line_intersect(lr, c, r_in + loop*dr)
            wp1 = wp1[0:2]
            lr = [c, [wp1[0], wp1[1], 0]]
            wp2 = kla.circle_line_intersect(lr, c, r_out - loop*dr)
            wp2 = wp2[0:2]
            wp3 = np.array([ wp2[0], -wp2[1] ])
            wp4 = np.array([ wp1[0], -wp1[1] ])
            
            # solve outer and inner arcs mid waypoints
            wpo = np.array([ r_out - loop*dr, 0 ])
            wpi = np.array([ r_in + loop*dr, 0 ])

            # rearrange waypoints
            if dir == "cw":
                if loop == 0:
                    if start == 0:
                        tp = wpi 
                        waypts.extend([wp4, tp[0:2], wp1, wp2, wpo, wp3])
                    elif start == 1:
                        tp = np.matmul(Rcw, wpi)
                        waypts.extend([wpi, tp[0:2], wp1, wp2, wpo, wp3])
                elif loop == n_loop-1:
                    tp = np.matmul(Rcw, wpo)
                    waypts.extend([wp4, wpi, wp1, wp2, tp[0:2], wpo])
                else:
                    waypts.extend([wp4, wpi, wp1, wp2, wpo, wp3])

            else:
                if loop == 0:
                    if start == 0:
                        tp = wpi
                        waypts.extend([wp1, tp[0:2], wp4, wp3, wpo, wp2])
                    elif start == 1:
                        tp = np.matmul(Rcw, wpi)
                        waypts.extend([wpi, tp[0:2], wp4, wp3, wpo, wp2])
                elif loop == n_loop-1:
                    tp = np.matmul(Rcw, wpo)
                    waypts.extend([wp1, wpi, wp4, wp3, tp[0:2], wpo])
                else:
                    waypts.extend([wp1, wpi, wp4, wp3, wpo, wp2])
            
            # move to the next radial
            l0 = [ [wp1[0], wp1[1], 0], [wp2[0], wp2[1], 0] ] 

        waypts_m = np.matrix(waypts)

        return waypts_m

def radial_old(r1,r2, dr,th,turns,dir):
        """ Compute layout points for coil with sides aligned to the local radial direction

        Args:
            r1 (int): coil inner radius
            r2 (int): coil outer radius
            dr (int): spacing between coil loops (and also adj. coils)
            th (float): coil trapezoid angle 
            turns (int): number of coil loops (windings)
            dir (int): coil direction, from larger to smaller loop (0:CW normal, 1:CCW rverse)

        Returns:
            matrix, matrix, matrix: corners (excl. arc mids), outer arc mids, inner arc mids
        """
 
        pts = []
        mds = []
        mdsi = []

        # center
        c = [0,0,0]
        
        # first line
        l0 = np.array([ c, [r1*math.cos(th/2), r1*math.sin(th/2), 0] ])

        for turn in range(turns):
            # offset previous line
            lr = kla.line_offset(l0, -dr)
            
            # solve corners and order them
            pc1 = kla.circle_line_intersect(lr, c, r1+turn*dr)
            pc1 = pc1[0:2]

            lr = [c, [pc1[0], pc1[1], 0]]

            pc2 = kla.circle_line_intersect(lr, c, r2-turn*dr)
            pc2 = pc2[0:2]
            pc3 = np.array([ pc2[0],-pc2[1] ])
            pc4 = np.array([ pc1[0],-pc1[1] ])
            if dir == 0:
                pts.extend([pc1, pc2, pc3, pc4])
            else:
                pts.extend([pc4, pc3, pc2, pc1])
            
            # solve outer and inner mid-points
            pm = np.array([ r2-turn*dr, 0 ])
            pmi = np.array([ r1+turn*dr, 0 ])
            mds.extend([pm])
            mdsi.extend([pmi])

            #
            l0 = [ [pc1[0], pc1[1], 0], [pc2[0], pc2[1], 0] ] 

        pm = np.matrix(pts)     # points, excl. arc mids
        mm = np.matrix(mds)     # arc (outer) mids only
        mmi = np.matrix(mdsi)    # arc (inner) mids only

        return pm, mm, mmi
