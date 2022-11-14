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

# my implementation
def fillet(board, t1, t2, r):

    # any arc track?
    t1_arc = t1.GetClass() == 'PCB_ARC'
    t2_arc = t2.GetClass() == 'PCB_ARC'

    # fillet center
    if t1_arc and t2_arc:
        # TODO: both arcs
        return

    elif t1_arc:

        # center
        c = kla.line_arc_center(t1, t2, r)
        # trim point track1 (line)
        l1 = kla.line_points(t1)
        p1 = kla.circle_line_tg( l1, c, r)
        
        # trim point track1 (arc)
        c1 = t1.GetCenter()
        c1 = np.array([c1.x, c1.y])
        r1 = t1.GetRadius()
        p1 = kla.circle_circle_tg(c,r, c1, r1)
        # trim point track2 (line)
        l2 = kla.line_points(t2)
        p2 = kla.circle_line_tg( l2, c, r)
        # mid point
        m = kla.circle_arc_mid(p1,p2, c,r)


        # generate fillet track 
        # convert to wxPoints
        kp1 = pcbnew.wxPoint( int(p1[0]), int(p1[1]) )
        kp2 = pcbnew.wxPoint( int(p2[0]), int(p2[1]) )
        km = pcbnew.wxPoint( int(m[0]), int(m[1]) )
        # do arc
        t = pcbnew.PCB_ARC(board)
        t.SetLayer( t1.GetLayer() )
        t.SetWidth( t1.GetWidth() )
        t.SetStart( kp1)
        t.SetMid( km )
        t.SetEnd( kp2 )
        board.Add(t)

        # trim tracks
        t1.SetEnd( pcbnew.wxPoint(p1[0],p1[1])  )
        t2.SetStart( pcbnew.wxPoint(p2[0],p2[1])  )


    elif t2_arc:
        # center
        c = kla.line_arc_center(t1, t2, r)
        # trim point track1 (line)
        l1 = kla.line_points(t1)
        p1 = kla.circle_line_tg( l1, c, r)
        # trim point track2 (arc)
        c2 = t2.GetCenter()
        c2 = np.array([c2.x, c2.y])
        r2 = t2.GetRadius()
        p2 = kla.circle_circle_tg(c,r, c2, r2)
        # mid point
        m = kla.circle_arc_mid(p1,p2, c,r)

        # generate fillet track 
        # convert to wxPoints
        kp1 = pcbnew.wxPoint( int(p1[0]), int(p1[1]) )
        kp2 = pcbnew.wxPoint( int(p2[0]), int(p2[1]) )
        km = pcbnew.wxPoint( int(m[0]), int(m[1]) )
        # do arc
        t = pcbnew.PCB_ARC(board)
        t.SetLayer( t1.GetLayer() )
        t.SetWidth( t1.GetWidth() )
        t.SetStart( kp1)
        t.SetMid( km )
        t.SetEnd( kp2 )
        board.Add(t)

        # trim tracks
        t1.SetEnd( pcbnew.wxPoint(p1[0],p1[1])  )
        t2.SetStart( pcbnew.wxPoint(p2[0],p2[1])  )


    else:
        c = kla.line_line_center(t1,t2,r)

        # trim point track1
        l1 = kla.line_points(t1)
        p1 = kla.circle_line_tg( l1, c, r)

        # trim point track2
        l2 = kla.line_points(t2)
        p2 = kla.circle_line_tg( l2, c, r)
        
        # arc mid-point
        t1e = t1.GetEnd()
        l = np.array([c, [t1e.x, t1e.y, 0]])
        lv = kla.line_vec(l)
        m = c + np.dot(r, lv)
        
        # convert to wxPoints
        kp1 = pcbnew.wxPoint( int(p1[0]), int(p1[1]) )
        kp2 = pcbnew.wxPoint( int(p2[0]), int(p2[1]) )
        km = pcbnew.wxPoint( int(m[0]), int(m[1]) )

        # generate fillet track 
        t = pcbnew.PCB_ARC(board)
        t.SetLayer( t1.GetLayer() )
        t.SetWidth( t1.GetWidth() )
        t.SetStart( kp1)
        t.SetMid( km )
        t.SetEnd( kp2 )
        board.Add(t)

        # trim tracks
        t1.SetEnd( pcbnew.wxPoint(p1[0],p1[1])  )
        t2.SetStart( pcbnew.wxPoint(p2[0],p2[1])  )


    