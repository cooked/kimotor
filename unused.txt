# Copyright 2022 Stefano Cottafavi <stefano.cottafavi@gmail.com>.
# SPDX-License-Identifier: GPL-2.0-only

# bore
    #edge = pcbnew.PCB_SHAPE(self.board, pcbnew.SHAPE_T_ARC)
    #edge.SetArcGeometry( 
    #       pcbnew.wxPoint(r1,0), 
    #       pcbnew.wxPoint(-r1,0),
    #       pcbnew.wxPoint( r1, 0))
    #edge.SetLayer( pcbnew.Edge_Cuts )

# keepout
    #kko.insert_keepout(self.board, 0, 0, fs, 100)
    # a = self.board.InsertArea(-1, 0xffff, pcbnew.F_Cu, 0, 0)
    # a.SetIsKeepout(True)
    # a.SetDoNotAllowTracks(False)
    # a.SetDoNotAllowVias(False)
    # a.SetDoNotAllowCopperPour(True)
    # outline = a.Outline()
