# Copyright 2022 Stefano Cottafavi <stefano.cottafavi@gmail.com>.
# SPDX-License-Identifier: GPL-2.0-only

import os
import wx
import pcbnew

def calc_length(board):
    tot = 0
    for track in board.GetTracks():
        l = track.GetLength()
        tot += l/pcbnew.FromMM(1)

    return tot

def calc_rlc(board, w, t, temp=20):
    """ Calculate resistance, inductance and capacitance of a track
    Args:
        board (_type_): _description_
        w (_type_): track width
        t (_type_): track thickness
        temp (float): ambient temperature
    """

    # https://www.allaboutcircuits.com/tools/trace-resistance-calculator/
    # https://www.cirris.com/learning-center/general-testing/special-topics/177-temperature-coefficient-of-copper
    rho = 1.77e-8       # [ohm/m] copper resistivity @ 20C
    alpha = 3.99e-2     # [ohm/ohm/C] copper temperature coeff

    L = calc_length(board) / 1000
    A = w*t
    r = rho * L/A
    rt = r * (1+alpha*(temp-20))


    # https://resources.system-analysis.cadence.com/blog/msa2021-is-there-a-pcb-trace-inductance-rule-of-thumb


    return rt
