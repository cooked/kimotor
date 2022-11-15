# Copyright 2022 Stefano Cottafavi <stefano.cottafavi@gmail.com>.
# SPDX-License-Identifier: GPL-2.0-only

import os
import wx.lib.agw.persist as PM

def registerAndRestoreAllRecursive(pm, obj, base="b"):
    obj.SetName(base)
    pm.RegisterAndRestoreAll(obj)
    children = obj.GetChildren()
    for i, child in enumerate(children):
        registerAndRestoreAllRecursive(pm, child, base=base+str(i))

def init_persist(self):
    # persistence
        self.SetName("kimotor") # Important!! Do not use the default name!!
        _configFile = os.path.join( os.getcwd(), "kimotor-saved.prj" )
        self._persistMgr = PM.PersistenceManager.Get()
        self._persistMgr.SetManagerStyle(PM.PM_DEFAULT_STYLE|PM.PM_SAVE_RESTORE_TREE_LIST_SELECTIONS)
        self._persistMgr.SetPersistenceFile(_configFile)
        #self._persistMgr.RegisterAndRestoreAll(self)
        registerAndRestoreAllRecursive(self._persistMgr, self)
            # Nothing was restored, so choose the default page ourselves
        self._persistMgr.Save(self)