try:
    # relative path import, instantiation and register to Pcbnew
    from .kicad_pcb_stator_action import KiMotorPlugin
    KiMotorPlugin().register()

except Exception as e:
    import os
    plugin_dir = os.path.dirname(os.path.realpath(__file__))
    log_file = os.path.join(plugin_dir, 'pcb_stator_error.log')
    with open(log_file, 'w') as f:
        f.write(repr(e))
    #from .no_wxpython import NoWxpython as SimplePlugin
    KiMotorPlugin().register()
