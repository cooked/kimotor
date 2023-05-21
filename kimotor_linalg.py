# Copyright 2022 Stefano Cottafavi <stefano.cottafavi@gmail.com>.
# SPDX-License-Identifier: GPL-2.0-only

import math
import numpy as np
import wx

# basic
def vec(t):
    # track direction
    p1 = t.GetStart()
    p2 = t.GetEnd()
    v = np.array([ p2.x-p1.x, p2.y-p1.y, 0 ])
    return v

def line_vec(l):
    # line unit vector
    p1 = l[0]   # start point [x,y]
    p2 = l[1]   # end point [x, y]
    d = np.array([ p2[0]-p1[0], p2[1]-p1[1], 0])
    v = d/np.linalg.norm(d)

    return v

def line(l):
    # find params of line equation ( y = mx + k ), given a track
    p1 = l[0]
    p2 = l[1]
    dx = p2[0]-p1[0]
    dy = p2[1]-p1[1]
    m = dy/dx
    k = p1[1] - m * p1[0]
    return m, k

def circle_to_polygon(r,n=100):
    # r: radius
    # n: nr of output segments
    p = []
    dth = 2 * math.pi / n
    for i in range(n):
        x = int(r * math.cos(i*dth))
        y = int(r * math.sin(i*dth))
        p.append( (x,y) )
    return p

def line_points(t):
    # get track start/end points
    ts = t.GetStart()
    te = t.GetEnd()
    return np.array( [[ts.x, ts.y, 0], [te.x, te.y, 0]] )

def line_offset(l, r):
    # offset a line l by distance r (+ shifts L, - shifts R)
    p1 = l[0]
    p2 = l[1]
    vl = np.array([ p2[0]-p1[0], p2[1]-p1[1], 0 ])
    vlu = vl/np.linalg.norm(vl)
    z = np.array([0,0,1])
    # ortho
    vln = np.cross( z, vlu )
    p1 = p1 + np.dot(r,vln)
    p2 = p2 + np.dot(r,vln)
    return np.array([p1, p2])

def circle_line_tg(l, c,r):

    p1 = l[0]
    p2 = l[1]
    # vectors (np arrays)
    vl = np.array([ p2[0]-p1[0], p2[1]-p1[1], 0 ])
    vc = np.array([ c[0]-p1[0], c[1]-p1[1], 0 ] )
    # unit vectors
    vlu = vl/np.linalg.norm(vl)
    vcu = vc/np.linalg.norm(vc)
    z = np.array([0,0,1])
    # side, cw or ccw
    d = np.dot(vcu,vlu)
    cc = np.cross(vcu,vlu)
    s = np.sign( np.dot(z,cc) )
    # ortho
    vln = np.cross( z, vlu )
    # trim point
    t = c + np.dot(s*r,vln)
    return t

def circle_line_sec(l, c,r):
    # https://mathworld.wolfram.com/Circle-LineIntersection.html
    p1 = l[0]
    p2 = l[1]
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    dr2 = dx**2 + dy**2
    D = p1[0]*p2[1] - p2[0]*p1[1]
    dsc = dr2 * r**2 - D**2
    #wx.LogError(f'dx {dx}, dy {dy}, c {c}, r {r}, dsc {dsc}, D {D}')
    x = ( (D*dy) + np.sign(dy)*dx*math.sqrt(dsc)) / dr2 + c[0]
    y = (-(D*dx) + np.abs(dy)*math.sqrt(dsc)) / dr2 + c[1]
    return np.array([x,y])

def circle_circle_tg(p1,r1,p2,r2):

    if r1<r2:
        dx = p1[0]-p2[0]
        dy = p1[1]-p2[1]
        d = math.sqrt(dx**2 + dy**2)
        v = np.array([ dx/d, dy/d ])
    else:
        dx = p2[0]-p1[0]
        dy = p2[1]-p1[1]
        d = math.sqrt(dx**2 + dy**2)
        v = np.array([ dx/d, dy/d ])
    # trim point
    t = p2 + np.dot(r2,v)
    return t

def track_arc_trim(t, ne):
    # takes an arc track and trims it to the given ne (new end) point
    s = t.GetStart()
    c = t.GetCenter()
    r = t.GetRadius()
    m = circle_arc_mid( [s.x, s.y], [ne.x, ne.y], [c.x, c.y, 0], r )
    return m

def circle_arc_mid(p1,p2, c,r):
    # mid point of segment connecting arc end points
    m = [ (p1[0]+p2[0])/2, (p1[1]+p2[1])/2 ]
    dx = m[0]-c[0]
    dy = m[1]-c[1]
    d = math.sqrt(dx**2 + dy**2)
    v = np.array([ dx/d, dy/d, 0 ])
    return c + np.dot(r,v)


def line_line_intersect(l1,l2):
    """ Find the intersection of two lines

    Args:
        l1 (_type_): 2D array of the 1st line start and end points
        l2 (_type_): 2D array of the 2nd line start and end points

    Returns:
        _type_: coordinates of the point of intersect
    """
    # https://mathworld.wolfram.com/Line-LineIntersection.html

    p1 = l1[0]
    p2 = l1[1]
    p3 = l2[0]
    p4 = l2[1]

    a12 = np.linalg.det(np.array([[p1[0], p1[1]], [p2[0], p2[1]]]))
    a34 = np.linalg.det(np.array([[p3[0], p3[1]], [p4[0], p4[1]]]))
    x12 = p1[0] - p2[0]
    x34 = p3[0] - p4[0]
    y12 = p1[1] - p2[1]
    y34 = p3[1] - p4[1]

    nx = np.linalg.det(np.array( [[a12, x12], [a34, x34]] ))
    ny = np.linalg.det(np.array( [[a12, y12], [a34, y34]] ))
    d = np.linalg.det(np.array( [[x12, y12], [x34, y34]] ))

    return np.array([nx/d, ny/d, 0])

def circle_line_intersect(l, c,r, ref=1):
    """ Find the intersection of a line and a circle

    Args:
        l (_type_): 2D array of the line start and end points
        c (_type_): coordinates [x,y] of the circle center
        r (_type_): radius of the circle
        ref (int, optional): line point to use as reference (0=start, 1=end). Defaults to 1.

    Returns:
        _type_: coordinates of the point of intersect
    """

    # TODO: this fails for dx=0 (m=inf)
    m,k = line(l)

    xc = c[0]
    yc = c[1]

    a = 1+m**2
    b = 2 * (m*k - m*yc - xc)
    c = k**2 + xc**2 + yc**2 - r**2 - 2*k*yc

    dsc = b**2 - 4*a*c
    #wx.LogError(f'dsc {dsc}')
    #dsc = np.abs(dsc)

    # pick the intersect point closest to the selected reference
    # point (start or end) of the line
    pref = np.array(l[ref])
    x1 = (-b - math.sqrt(dsc)) / (2*a)
    p1 = np.array([x1, m*x1 + k, 0])
    x2 = (-b + math.sqrt(dsc)) / (2*a)
    p2 = np.array([x2, m*x2 + k, 0])

    d1 = np.linalg.norm(p1-pref)
    d2 = np.linalg.norm(p2-pref)

    # TODO: what if equal? we should add a check beforehand
    return p1 if d1<d2 else p2

def circle_circle_intersect(c1,r1,c2,r2):
    """ Find the intersection of two circles

    Args:
        c1 (_type_): coordinates [x,y] of the 1st circle center
        r1 (_type_): radius of the 1st circle
        c2 (_type_): coordinates [x,y] of the 2nd circle center
        r2 (_type_): radius of the 2nd circle

    Returns:
        _type_: _description_
    """

    # https://math.stackexchange.com/questions/256100/how-can-i-find-the-points-at-which-two-circles-intersect
    # https://gist.github.com/jupdike/bfe5eb23d1c395d8a0a1a4ddd94882ac
    # https://gist.github.com/jupdike/bfe5eb23d1c395d8a0a1a4ddd94882ac?permalink_comment_id=3590178#gistcomment-3590178

    x1 = c1[0]
    y1 = c1[1]
    x2 = c2[0]
    y2 = c2[1]

    R = math.sqrt( (x1-x2)**2 + (y1-y2)**2 );
    #if not ( abs(r1 - r2) <= R and R <= r1 + r2):
    #    return [] # empty list of results
    #intersection(s) should exist

    R2 = R*R;
    R4 = R2*R2;
    a = (r1*r1 - r2*r2) / (2 * R2);
    r2r2 = (r1*r1 - r2*r2);
    c = math.sqrt(2 * (r1*r1 + r2*r2) / R2 - (r2r2 * r2r2) / R4 - 1);

    fx = (x1+x2) / 2 + a * (x2 - x1);
    gx = c * (y2 - y1) / 2;

    wx.LogError(f'gx: {gx}')

    #note if gy == 0 and gx == 0 then the circles are tangent and there is only one solution
    #but that one solution will just be duplicated as the code is currently written

    ix1 = fx + gx;
    ix2 = fx - gx;

    fy = (y1+y2) / 2 + a * (y2 - y1);
    gy = c * (x1 - x2) / 2;
    iy1 = fy + gy;
    iy2 = fy - gy;

    return [ix1, iy1], [ix2, iy2];

def line_line_center(t1,t2, f):
    """ Center of the arc fillet, given two straight tracks. The point is the intersection
    of the track lines both offset by the fillet radius

    Args:
        t1 (_type_): track 1
        t2 (_type_): track 2
        f (_type_): fillet radius

    Returns:
        _type_: _description_
    """

    # solve unit vectors
    v1 = vec(t1)
    v2 = vec(t2)
    v1u = v1/np.linalg.norm(v1)
    v2u = v2/np.linalg.norm(v2)
    z = np.array([0,0,1])

    # side, cw or ccw
    d = np.dot(v1u,v2u)
    c = np.cross(v1u,v2u)
    s = np.sign( np.dot(z,c) )

    v1n = np.cross( z, v1u )
    v2n = np.cross( z, v2u )

    # offset lines
    p1 = line_points(t1)
    p2 = line_points(t2)
    p1 = p1 + np.dot(s*f, v1n)
    p2 = p2 + np.dot(s*f, v2n)

    # line intersection (i.e. fillet center)
    c = line_line_intersect(p1,p2)

    return c

def line_arc_center(t1, t2, f, side=1):
    """ Center of the arc fillet, given one straight and one arc track. The point is the intersection
    of the track lines offset by the fillet radius

    Args:
        t1 (_type_): track 1
        t2 (_type_): track 2
        f (_type_): fillet radius

    Returns:
        _type_: _description_
    """

    t1_arc = t1.GetClass() == 'PCB_ARC'
    t2_arc = t2.GetClass() == 'PCB_ARC'

    z = np.array([0,0,1])

    if t1_arc:
        # solve unit vectors
        v1 = tangent(t1, end=True)    # use the tg to the arc at its END point
        v2 = vec(t2)

        v1u = v1/np.linalg.norm(v1)
        v2u = v2/np.linalg.norm(v2)
        
        # side, cw or ccw
        x = np.cross(v2u,v1u)   # !!!IMPORTANT!!!: order inverted wrt t2_arc
        s = np.sign( np.dot(z,x) )

        v2n = np.cross( [0,0,s], v2u )

        # offset circle
        ot = t1.GetCenter()
        o = np.array([ot.x, ot.y])
        rt = t1.GetRadius()
        r = rt - side*f
        
        wx.LogError(f'o {o}, r {r}, get rad {rt}')

        # offset line
        l = line_points(t2)
        l = l + np.dot( f, v2n )

        c = circle_line_intersect(l, o, r, 0)

    elif t2_arc:
        # solve unit vectors
        v1 = vec(t1)
        v2 = tangent(t2)    # use the tg to the arc at its START point

        v1u = v1/np.linalg.norm(v1)
        v2u = v2/np.linalg.norm(v2)

        # side, cw or ccw
        x = np.cross(v1u,v2u)
        s = np.sign( np.dot(z,x) )

        v1n = np.cross( [0,0,s], v1u )

        # offset line
        l = line_points(t1)
        l = l + np.dot( f, v1n )

        # offset circle
        ot = t2.GetCenter()
        o = np.array([ot.x, ot.y])
        rt = t2.GetRadius()
        r = rt - side*f

        wx.LogError(f'o {o}, r {r}, get rad {rt}')

        c = circle_line_intersect(l, o, r, 1)

    #wx.LogError(f'c {c}, o {o}, r {r}')

    return c, o, r, int(rt)

# TODO: implement
def arc_arc_center(t1, t2, f):
    return

def tangent(t, end = False):

    # find direction of tangent at start (or end) of arc track
    to = t.GetCenter()
    s = t.GetStart()
    e = t.GetEnd()

    tp1 = e if end else s
    tp2 = s if end else e

    # radius direction
    ro = np.array([ tp1.x-to.x, tp1.y-to.y, 0])
    rv = ro/np.linalg.norm(ro)
    
    # p1 (arc start) to p2 (arc end) direction
    rp = np.array([ tp2.x-tp1.x, tp2.y-tp1.y, 0])
    pv = rp/np.linalg.norm(rp)

    x = np.cross(rv,pv)
    z = np.array([0,0,1])
    s = np.sign( np.dot(z,x) )

    return np.cross([0,0,s], rv)
