# linear algebra helpers

import math
import numpy as np
import pcbnew
import wx

def line(self, t):
    # find params of line equation ( y = mx + k ), given a track
    ts = t.GetStart()
    te = t.GetEnd()
    m = (te.y-ts.y)/(te.x-ts.x)
    k = ts.y - m*ts.x
    return m, k

def line(self, ts, te):
    # find params of line equation ( y = mx + k ), given start and end wxPoints  
    m = (te.y-ts.y)/(te.x-ts.x)
    k = ts.y - m*ts.x
    return m, k

def circles_intercept(self, x1,y1,r1, x2,y2,r2):
    # https://math.stackexchange.com/questions/256100/how-can-i-find-the-points-at-which-two-circles-intersect
    # https://gist.github.com/jupdike/bfe5eb23d1c395d8a0a1a4ddd94882ac
    # https://gist.github.com/jupdike/bfe5eb23d1c395d8a0a1a4ddd94882ac?permalink_comment_id=3590178#gistcomment-3590178

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
    ix1 = fx + gx;
    ix2 = fx - gx;

    fy = (y1+y2) / 2 + a * (y2 - y1);
    gy = c * (x1 - x2) / 2;
    iy1 = fy + gy;
    iy2 = fy - gy;

    #note if gy == 0 and gx == 0 then the circles are tangent and there is only one solution
    #but that one solution will just be duplicated as the code is currently written
    return [ix1, iy1], [ix2, iy2];

def line_arc_center(self, t1, t2, f):
    # Find fillet center, which is the intersection of the line track shifted by "fillet" 
    # and the arc line with reduced radius "r - fillet"

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

    fe1, fe2 = circles_intercept(o.x,o.y,r, p[0],p[1],f)
    
    return p, fe1

def normalize(self, t):
    # returns (unit vector) direction of the track
    n = np.array([ t.GetEndX()-t.GetX(), t.GetEndY()-t.GetY() ])
    return n / t.GetLength()

def tangent(self, t, end = False):
    # find direction of tangent at start (or end) of arc track
    to = t.GetCenter()
    tp = t.GetEnd() if end else t.GetStart()
    rd = np.array([ tp.x-to.x, tp.y-to.y, 0]) / t.GetRadius()
    z = np.array([0,0,-1])
    return np.cross(rd, z)

def angle_and_bisect(self, t1, t2):
    # find angle and bisect vector between tracks, using tangent if track is arc
    # (assumes track1_end == track2_start)
    
    if t1.GetClass() == 'PCB_ARC':
        v1 = tangent(t1, True)
    else:
        v1 = np.array([ t1.GetX()-t1.GetEndX(), t1.GetY()-t1.GetEndY(), 0 ])
        v1 = v1/t1.GetLength()
    
    if t2.GetClass() == 'PCB_ARC':
        v2 = tangent(t2)
    else:
        v2 = np.array([ t2.GetEndX()-t2.GetX(), t2.GetEndY()-t2.GetY(), 0 ])
        v2 = v2 / t2.GetLength()

    # angle 
    a = math.acos( np.dot(v1,v2) )
    # normalized bisect 
    b = (v1+v2) / np.linalg.norm(v1+v2)

    return a, b 

def angle2(self, t1, t2):
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