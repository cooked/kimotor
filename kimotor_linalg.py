# linear algebra helpers

import math
import numpy as np
import pcbnew
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
    
    dx = p2[0]-p1[0]
    dy = p2[1]-p1[1]
    d = math.sqrt(dx**2 + dy**2)
    v = np.array([ dx/d, dy/d, 0])
    
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

    vln = np.cross( z, vlu )

    p = c + np.dot(s*r,vln)

    return p

def circle_line_sec(l, c,r):
    # https://mathworld.wolfram.com/Circle-LineIntersection.html

    p1 = l[0]
    p2 = l[1]

    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    dr2 = dx**2 + dy**2
    D = p1[0]*p2[1] - p2[0]*p1[1]
    dsc = dr2 * r**2 - D**2

    wx.LogError(f'dx {dx}, dy {dy}, c {c}, r {r}, dsc {dsc}, D {D}')

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
    
    return pcbnew.wxPoint(m[0],m[1])

def circle_arc_mid(p1,p2, c,r):
    
    # mid point of segment connecting arc end points
    m = [ (p1[0]+p2[0])/2, (p1[1]+p2[1])/2 ]

    dx = m[0]-c[0]
    dy = m[1]-c[1]
    d = math.sqrt(dx**2 + dy**2)
    v = np.array([ dx/d, dy/d, 0 ])

    return c + np.dot(r,v)


def circle_line_intersect(l, c,r, ref=1):
    # l: 2D array of the line points
    # c: circle center
    # r: circle radius
    # ref: linepoint to use as reference (0=start, 1=end)

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


# line-to-line fillet
def line_line_intersect(l1,l2):
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
def line_line_center(t1,t2, f):
    # find fillet center, given two straight lines 
    # (i.e intersection of the 2 lines offset by f)

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

# line-to-arc fillet


def circle_circle_intersect(c1,r1,c2,r2):
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


def line_arc_center(t1, t2, f):

    t1_arc = t1.GetClass() == 'PCB_ARC'
    t2_arc = t2.GetClass() == 'PCB_ARC'

    if t1_arc:
        # solve unit vectors
        v1 = tangent(t1, end=True)    # use the tg to the arc at its END point
        v2 = vec(t2)

        v1u = v1/np.linalg.norm(v1)
        v2u = v2/np.linalg.norm(v2) 
        z = np.array([0,0,1])
        
        # side, cw or ccw
        x = np.cross(v2u,v1u)   # !!!IMPORTANT!!!: order inverted wrt t2_arc
        s = np.sign( np.dot(z,x) )

        v2n = np.cross( [0,0,s], v2u ) 

        # offset circle
        o = t1.GetCenter()
        o = np.array([o.x, o.y])
        r = t1.GetRadius() - f

        # offset line
        p2 = line_points(t2)
        p2 = p2 + np.dot( f, v2n )

        c = circle_line_intersect(p2, o, r, 0)


    elif t2_arc:
        # solve unit vectors
        v1 = vec(t1)
        v2 = tangent(t2)    # use the tg to the arc at its START point

        v1u = v1/np.linalg.norm(v1)
        v2u = v2/np.linalg.norm(v2) 
        z = np.array([0,0,1])

        # side, cw or ccw
        x = np.cross(v1u,v2u)
        s = np.sign( np.dot(z,x) )

        v1n = np.cross( [0,0,s], v1u ) 
        
        # offset line
        p1 = line_points(t1)
        p1 = p1 + np.dot( f, v1n )

        # offset circle
        o = t2.GetCenter()
        o = np.array([o.x, o.y])
        r = t2.GetRadius() - f

        c = circle_line_intersect(p1, o, r, 1)

    return c

def line_arc_center_old(t1, t2, f):
    # Find fillet center, which is the intersection of the line track shifted by "fillet" 
    # and the arc line with reduced radius "r - fillet"

    # returns: 1) the center, 2) the trim point on arc

    # t1: track 1 (linear)
    # t2: track 2 (arc)
    # f: fillet radius (int)

    # TODO: must offset line in the perp direction 
    m, k = line(t1)
    a, b = angle_and_bisect(t1,t2)
    if a > 0:
        k += f
    else:
        k -= f

    o = t2.GetCenter()
    r = t2.GetRadius()

    a = 1 + m**2
    b = 2 * (m*k - o.x)
    c = (k-o.y)**2 - 2*m*o.y + o.x**2 - (r-f)**2

    x1 = (-b + math.sqrt( b**2 - 4*a*c )) / (2*a)
    x2 = (-b - math.sqrt( b**2 - 4*a*c )) / (2*a)

    fc1 = [ x1, m*x1 + k ]
    fc2 = [ x2, m*x2 + k ]

    # TODO: algo to pick the right point p
    p = fc1
    # circle1: center = p, radius = f
    # circle2: center = c, radius = r

    # find the intersection of the track circle and fillet circle
        # cm = -(c.x - p[0]) / (c.y - p[1])
        # ck = -((r**2 - f**2) - (c.x**2 - p[0]**2) - (c.y**2 - p[1]**2)) / (2*(p[1]-c.y))
        
        # a = 1 + cm
        # b = 2*(cm*ck-c.x)
        # c = (ck - c.y)**2 - 2*cm*c.y + c.x**2 + r**2 

        # x1 = (-b + math.sqrt( b**2 - 4*a*c )) / (2*a)
        # x2 = (-b - math.sqrt( b**2 - 4*a*c )) / (2*a)

    fe1, fe2 = circle_circle_intersect(o.x,o.y,r, p[0],p[1],f)
    
    wx.LogWarning(f'circle intercepts: {fe1}, {fe2}')

    return p, fe1

def arc_arc_center(t1, t2, f):
    return

def normalize(t):
    # returns (unit vector) direction of the track
    n = np.array([ t.GetEndX()-t.GetX(), t.GetEndY()-t.GetY() ])
    return n / t.GetLength()

def tangent(t, end = False):
    
    # find direction of tangent at start (or end) of arc track
    to = t.GetCenter()
    s = t.GetStart()
    e = t.GetEnd()
    
    tp1 = e if end else s
    tp2 = s if end else e

    # radius direction
    rv = np.array([ tp1.x-to.x, tp1.y-to.y, 0]) / t.GetRadius()
    # p1 to p2 direction
    dx = tp2.x-tp1.x
    dy = tp2.y-tp1.y
    n = math.sqrt(dx**2+dy**2)
    pv = np.array([ dx/n, dy/n, 0])
    
    x = np.cross(rv,pv)
    z = np.array([0,0,1])
    s = np.sign( np.dot(z,x) )

    return np.cross([0,0,s], rv)

def angle_and_bisect(t1, t2):
    # find angle and bisect vector between tracks, using tangent if track is arc
    # (assumes track1_end == track2_start)
    
    if t1.GetClass() == 'PCB_ARC':
        v1 = tangent(t1, True)
    else:
        t1s = t1.GetStart()
        t1e = t1.GetEnd()
        v1 = np.array([ t1e.x-t1s.x, t1e.y-t1s.y, 0 ])
        v1 = v1 / t1.GetLength()
    
    if t2.GetClass() == 'PCB_ARC':
        v2 = tangent(t2)
    else:
        v2 = np.array([ t2.GetEndX()-t2.GetX(), t2.GetEndY()-t2.GetY(), 0 ])
        v2 = v2 / t2.GetLength()

    z = np.array([0,0,1])

    
    d = np.dot(v1,v2)
    c = np.cross(v1,v2)
    # +/- rotation?
    s = np.sign( np.dot(z,c) )
    
    # angle 
    a = s * math.acos(d)
    
    # normalized bisect 
    b = (v1+v2) / np.linalg.norm(v1+v2)
    b = np.cross(b,-z)
    b = b / np.linalg.norm(b)

    return a, b

def angle2(t1, t2):
    # t1: first track
    # t2: next track

    # if arc, use tangent
    if t2.GetClass() == 'PCB_ARC':
        t2c = t2.GetCenter()
        t2s = t2.GetStart()
        # radial vector (from center to starting point)
        t2rv = pcbnew.VECTOR2I( t2s.x-t2c.x, t2s.y-t2c.y )
        #  vector normal to radius (i.e. tangent to arc at starting point)
        t2v = - t2rv.Perpendicular()
    else:
        t2s = t2.GetStart()
        t2e = t2.GetEnd()
        t2v = pcbnew.VECTOR2I( t2e.x-t2s.x, t2e.y-t2s.y )

    t1s = t1.GetStart()
    t1e = t1.GetEnd()
    t1v = pcbnew.VECTOR2I( t1e.x-t1s.x, t1e.y-t1s.y )
    
    return t2v.Angle() - t1v.Angle()