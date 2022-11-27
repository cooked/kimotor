# Copyright 2022 Stefano Cottafavi <stefano.cottafavi@gmail.com>.
# SPDX-License-Identifier: GPL-2.0-only

import math
import numpy as np
import pcbnew
import wx

if __name__ == '__main__':
    import kimotor_linalg as kla
else:
    from . import kimotor_linalg as kla

def test_via(board, pos):
    via = pcbnew.PCB_VIA(board)
    via.SetPosition( pcbnew.wxPoint(pos[0],pos[1]) )
    via.SetDrill( int(0.1*1e6) )
    via.SetWidth( int(0.2*1e6) )
    board.Add(via)

def fillet(board, t1, t2, r, side=1):
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
    t.SetStart( pcbnew.wxPoint(int(p1[0]),int(p1[1])) )
    t.SetMid( pcbnew.wxPoint(int(m[0]),int(m[1])) )
    t.SetEnd( pcbnew.wxPoint(int(p2[0]),int(p2[1])) )
    board.Add(t)
    # trim tracks
    t1.SetEnd( pcbnew.wxPoint(p1[0],p1[1])  )
    t2.SetStart( pcbnew.wxPoint(p2[0],p2[1])  )


    