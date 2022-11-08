
def M(arr,i,j):
        # minor of a matrix (ith row, jth column removed)
        # https://stackoverflow.com/questions/3858213/numpy-routine-for-computing-matrix-minors

        return arr[np.array(list(range(i))+list(range(i+1,arr.shape[0])))[:,np.newaxis],
                np.array(list(range(j))+list(range(j+1,arr.shape[1])))]

def center_radius(self, t1):
    # finds center and radius of a 3-points PCB_ARC track
    #
    # https://math.stackexchange.com/questions/2836274/3-point-to-circle-and-get-radius
    # TODO: implement one of these:
    # https://en.wikipedia.org/wiki/Circumscribed_circle#Circumcircle_equations

    ### NOTE: not needed, PCB_ARC does have GetCenter() method
    p1 = t1.GetStart() 
    p2 = t1.GetMid() 
    p3 = t1.GetEnd()

    #m1, k1 = self.line(p1,p2)
    #m2, k2 = self.line(p2,p3)

    # perpendiculars
    #l1p
    
    # center
    c = pcbnew.wxPoint(0,0)

    return c


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

def unused_loop():
        if not (idx-1)%4 :
                # TODO: reimplement the arc at some point
                #track = pcbnew.PCB_ARC(self.board)
                #tfv = Tfv[iv]
                #track.SetMid( pcbnew.wxPointMM( tfv[0,0].item(), tfv[0,1].item()) )
                
                tfv = Tfv[iv]
                iv += 1
                pm = pcbnew.wxPoint( int(tfv[0,0].item()), int(tfv[0,1].item()) )

                # first segment of outer side of coil
                track_p = pcbnew.PCB_TRACK(self.board)
                track_p.SetWidth( self.trk_w )
                track_p.SetLayer(pcbnew.F_Cu)
                track_p.SetStart( ps )
                track_p.SetEnd( pm )
                self.board.Add(track_p)
                self.group.AddItem(track_p)

                track = pcbnew.PCB_TRACK(self.board)
                track.SetWidth( self.trk_w )
                track.SetLayer(pcbnew.F_Cu)
                track.SetStart( pm )
                track.SetEnd( pe )
                self.board.Add(track)
                self.group.AddItem(track)

                # fillet (outer coil corner)
                #kf.fillet(self.board, track0, track, self.r_flat)
                #fo = kf.do_fillet(self.board, track_p, track, self.r_flat)
                #self.board.Add(fo)
                #self.group.AddItem(fo)

                #if idx > 0:
                #    kf.do_fillet(self.board, track0, track, self.r_fill)

                #f = kf.do_fillet(self.board, track0, track_p, self.r_fill)
                #self.board.Add(f)
                #self.group.AddItem(f)
        else:
                track = pcbnew.PCB_TRACK(self.board)    
                track.SetWidth( self.trk_w )
                track.SetLayer(pcbnew.F_Cu)
                track.SetStart( ps )
                track.SetEnd( pe )
                self.board.Add(track)
                self.group.AddItem(track)
                
                # fillet (all coil corners, but outer)
                if idx > 0:
                #kf.fillet(self.board, track0, track, self.r_fill)
                #f = kf.do_fillet(self.board, track0, track, self.r_fill)
                #self.board.Add(f)
                #self.group.AddItem(f)