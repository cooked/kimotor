# fillet helpers

import math
import numpy as np
import pcbnew
import wx

if __name__ == '__main__':
    import kimotor_linalg as kla
else:
    from . import kimotor_linalg as kla

def test_angle(t1, t2):
    rev = 1
    kla.angle_and_bisect(t1,t2)

    

# my implementation
def fillet(board, t1, t2, r):

    # r: fillet radius [nm] 
    
    # any arc track?
    t1_arc = t1.GetClass() == 'PCB_ARC'
    t2_arc = t2.GetClass() == 'PCB_ARC'

    t1e = t1.GetEnd()
    t2s = t2.GetStart()

    # angle and bisect vector between 2 tracks
    # a, b = kla.angle_and_bisect(t1,t2)
    
    # fillet center
    c = kla.line_line_center(t1,t2,r)
    wx.LogWarning(f'c: {c}')

    # trim point on track1
    l1 = kla.line_points(t1)
    p1 = kla.circle_line_intersect(l1, c[0],c[1],r)
    wx.LogWarning(f'p1: {p1}')

    # trim point on track2
    l2 = kla.line_points(t2)
    p2 = kla.circle_line_intersect(l2, c[0],c[1],r)
    wx.LogWarning(f'p2: {p2}')

    return c, p1, p2

    # if t2_arc:
    #     c1, t2s = kla.line_arc_center(t1, t2, r)
    #     t2.SetStart( pcbnew.wxPoint(t2s[0],t2s[1]) )
    # else:    
    #     # circle/track2  intersect
        

    #     dt2 = dt * kla.normalize(t2)
    #     t2.SetStart( pcbnew.wxPoint(
    #         t2s.x + int(dt2[0]),
    #         t2s.y + int(dt2[1]) )
    #     )

    # # solve fillet arc mid-point
    # #
    # # find t1e, endpoint of track1
    # t1e = np.array([ t1.GetEndX(), t1.GetEndY(), 0 ])
    # # find direction ortho to track
    # t1n = kla.normalize(t1)
    # z = np.array([0,0,1])
    # dc = np.cross(t1n, z)
    # oc = t1e + dc*r
    
    # #  move from track 1 end to center, then along bisect direction  
    # mp = oc - b*r

    


# see https://github.com/tywtyw2002/FilletEdge/blob/master/fillet_helper.py
# this as been hacked to work with PCB_TRACKS on top of PCB_SHAPES
def do_fillet(board, a, b, fillet_value):
    # must be cw rotate
    # swap if ccw rotate
    theta = 0

    is_track = b.GetClass() == 'PCB_ARC' or b.GetClass() == 'PCB_TRACK'

    # TODO: implement fillet of ARCs
    #if b.GetClass() == 'PCB_ARC':
    #    n1 = kla.tangent(b)
    #    b_s = b.GetStart()
    #    b_e = b.GetEnd()
    #else:
    b_s = b.GetStart()
    b_e = b.GetEnd()

    a_s = a.GetStart()
    a_e = a.GetEnd()

    a_reverse = 1
    b_reverse = 1
    a_set = a.SetStart
    b_set = b.SetStart
    co_point = pcbnew.wxPoint(a_s.x, a_s.y)

    if a_e == b_s or a_e == b_e:
        co_point = pcbnew.wxPoint(a_e.x, a_e.y)
        a_set = a.SetEnd
        a_reverse = -1
    elif a_s != b_s and a_s != b_e:
        wx.LogWarning('Unable to Fillet, 2 lines not share any point.')
        return

    if b_e == co_point:
        b_reverse = -1
        b_set = b.SetEnd

    # TODO: add support for arcs here, after reorientation of tracks 
    # has been done (see above)

    a_v = pcbnew.VECTOR2I(
        (a_e.x - a_s.x) * a_reverse,
        -(a_e.y - a_s.y) * a_reverse
    )
    b_v = pcbnew.VECTOR2I(
        (b_e.x - b_s.x) * b_reverse,
        -(b_e.y - b_s.y) * b_reverse
    )

    theta = a_v.Angle() - b_v.Angle()
    
    if theta < -math.pi:
        theta += math.pi * 2
    elif theta > math.pi:
        theta -= math.pi * 2

    deg = math.degrees(theta)

    c_v = a_v.Resize(1000000) + b_v.Resize(1000000)
    c_angle = c_v.Angle()

    # TODO: for arcs the offset has to be done differently

    offset = fillet_value
    if int(deg) != 90 and int(deg) != -90:
        offset = abs(offset * math.tan((math.pi - theta) / 2))

    a_point = pcbnew.wxPoint(
        int(co_point.x + offset * math.cos(a_v.Angle())),
        int(co_point.y - offset * math.sin(a_v.Angle()))
    )
    b_point = pcbnew.wxPoint(
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
    s_arc.SetWidth(a.GetWidth())
    if is_track:
        f = pcbnew.PCB_ARC(board)
        f.SetWidth( a.GetWidth() )
        f.SetLayer( a.GetLayer() )

    
    # set center
    if offset == fillet_value:
        # 90 or -90
        s_arc.SetCenter(pcbnew.wxPoint(
            a_point.x + b_point.x - co_point.x,
            a_point.y + b_point.y - co_point.y
        ))
    else:
        coffset = abs(fillet_value / math.cos((math.pi - theta) / 2))
        s_arc.SetCenter(pcbnew.wxPoint(
            co_point.x + int(coffset * math.cos(c_angle)),
            co_point.y - int(coffset * math.sin(c_angle))
        ))

    if deg < 0:
        s_arc.SetStart(a_point)
    else:
        s_arc.SetStart(b_point)
    if is_track:
        f.SetStart( s_arc.GetStart() )

    # hack for mid point
    s_arc.SetArcAngleAndEnd(1800 - abs(deg/2 * 10))
    mid = s_arc.GetEnd()
    if is_track:
        f.SetMid( mid )

    s_arc.SetArcAngleAndEnd(1800 - abs(deg * 10))
    end = s_arc.GetEnd()
    if is_track:
        f.SetEnd( end )
    
    # if track, disregard the "shape" arc and add track only
    if is_track:
        return f
    else:
        return s_arc