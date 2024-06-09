# Copyright 2022-2024 Stefano Cottafavi <stefano.cottafavi@gmail.com>.
# SPDX-License-Identifier: GPL-2.0-only

import wx 
import wx.lib.agw.persist as PM
import wx.lib.agw.persist.persist_handlers as ph
import wx.lib.agw.persist.persistencemanager as pm

class SpinCtrlDoublePersist(wx.SpinCtrlDouble, pm.PersistentObject):
    def __init__(self, parent, id=-1, value="", pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.SP_ARROW_KEYS, min=0, max=100, initial=0, inc=1, name="wxSpinCtrlDouble"):
        wx.SpinCtrlDouble.__init__(self, parent, id, value, pos, size, style, min, max, initial, inc, name)
        pm.PersistentObject.__init__(self, self, ph.SpinHandler) 
