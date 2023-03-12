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

def fillet(board, group, t1, t2, r, side=1):
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
    t.SetStart( pcbnew.VECTOR2I(int(p1[0]),int(p1[1])) )
    t.SetMid( pcbnew.VECTOR2I(int(m[0]),int(m[1])) )
    t.SetEnd( pcbnew.VECTOR2I(int(p2[0]),int(p2[1])) )
    board.Add(t)
    group.AddItem(t)
    # trim tracks
    t1.SetEnd( pcbnew.VECTOR2I(int(p1[0]),int(p1[1]))  )
    t2.SetStart( pcbnew.VECTOR2I(int(p2[0]),int(p2[1]))  )

## borrowed from fillet_helper.py
## https://github.com/tywtyw2002/FilletEdge/blob/master/fillet_helper.py
def fillet_outline(board, a, b, fillet_value):
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
        co_point = pcbnew.VECTOR2I(a_s.x, a_s.y)

        if a_e == b_s or a_e == b_e:
            co_point = pcbnew.VECTOR2I(a_e.x, a_e.y)
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

        a_point = pcbnew.VECTOR2I(
            int(co_point.x + offset * math.cos(a_v.Angle())),
            int(co_point.y - offset * math.sin(a_v.Angle()))
        )
        b_point = pcbnew.VECTOR2I(
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
            s_arc.SetCenter(pcbnew.VECTOR2I(
                a_point.x + b_point.x - co_point.x,
                a_point.y + b_point.y - co_point.y
            ))
        else:
            coffset = abs(fillet_value / math.cos((math.pi - theta) / 2))
            s_arc.SetCenter(pcbnew.VECTOR2I(
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
