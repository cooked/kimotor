# Copyright 2022 Stefano Cottafavi <stefano.cottafavi@gmail.com>.
# SPDX-License-Identifier: GPL-2.0-only

import pcbnew
import math

def insert_keepout(board, center_x, center_y, radius, corners=16, layer=None, hatch_type=None, 
                    no_tracks=False, no_vias=False, no_pour=True):

    Point = pcbnew.wxPoint
    ver5 = hasattr(pcbnew, "SHAPE_POLY_SET")
    
    if corners < 3 or corners > 256:
        raise Exception("Wrong number of corners: %s" % corners)
    if hatch_type is None:
        # NO_HATCH, DIAGONAL_FULL, DIAGONAL_EDGE
        hatch_type = pcbnew.CPolyLine.DIAGONAL_EDGE
    if layer is None:
        layer = pcbnew.F_Cu

    area = board.InsertArea(-1, 0xffff, layer, 0, 0, hatch_type)
    area.SetIsKeepout(True)
    area.SetDoNotAllowTracks(no_tracks)
    area.SetDoNotAllowVias(no_vias)
    area.SetDoNotAllowCopperPour(no_pour)
    outline = area.Outline()
    if ver5:
        outline.RemoveAllContours()
        #outline.RemoveVertex(0) # since CPolyLine -> SHAPE_POLY_SET
    else:
        outline.DeleteCorner(0) # remove first element
    
    cos, sin, floor = math.cos, math.sin, math.floor
    
    thi = 0
    dthi = 2 * math.pi / corners
    
    # calculate corners
    if ver5:
        for i in range(corners):
            x = int(floor(center_x + radius * cos(thi)))
            y = int(floor(center_y + radius * sin(thi)))
            area.AppendCorner(Point(x, y), -1)
            #outline.Append(x, y) # since CPolyLine -> SHAPE_POLY_SET?
            thi += dthi
    else:
        for i in range(corners):
            x = int(floor(center_x + radius * cos(thi)))
            y = int(floor(center_y + radius * sin(thi)))
            outline.AppendCorner(x, y)
            thi += dthi
    
    if ver5:
        if hasattr(area, "BuildFilledSolidAreasPolygons"):
            # todo, do we need to call this?
            # BuildFilledSolidAreasPolygons method has been gone since 
            # "pcbnew: made zone filling algorithm thread-safe. "
            area.BuildFilledSolidAreasPolygons(board)
        else:
            pass
            #outline.Outline(0).SetClosed(True) # no SHAPE_LINE_CHAIN implemented
    else:
        outline.CloseLastContour()
    if hasattr(area, "Hatch"):
        area.Hatch()

def apply_modules(board, exp, func, type="reference"):
    """ Call func to modules which has reference match with the regular expression.
        @param board Pcbnew board
        @param exp compiled regular expression or string
        @param func function which takes a module as its argument
        @param type reference or value
    """
    import re
    exp = re.compile(exp)
    if type == "reference":
        for module in board.GetModules():
            if exp.match(module.GetReference()):
                func(module)
    elif type == "value":
        for module in board.GetModules():
            if exp.match(module.GetValue()):
                func(module)

def insert_keepout_around_mod(exp, radius, corners=16, layers=None, hatch_type=None, 
                    no_tracks=True, no_vias=True, no_pour=True):
    """ Add keepout area around specified module. 
        @param exp specifies module reference in regular expression
        @param radius radius in mm
        @param corners number of vertex
        @param layers layer or multiple layers can be specified in tuple
        @param no_tracks 
        @param no_vias
        @param no_pour 
    """
    import pcbnew
    if not isinstance(layers, (tuple, list)):
        layers = (layers,)
    
    radius_ = pcbnew.FromMM(radius)
    def func(mod):
        pos = mod.GetPosition()
        for layer in layers:
            insert_keepout_(pos.x, pos.y, radius_, corners, layer, 
                            hatch_type, no_tracks, no_vias, no_pour)
    
    board = pcbnew.GetBoard()
    apply_modules(board, exp, func)
