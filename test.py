import pcbnew

def pcbpoint(p):
    return pcbnew.wxPointMM(float(p[0]), float(p[1]))

class TestPlugin(pcbnew.ActionPlugin):
    """Draw a track and via
    """
    def defaults( self ):
        self.name = "Test Plugin"
        self.category = "Modify PCB"
        self.description = "Draws a track and a via"
        self.show_toolbar_button = True
        #self.icon_file_name = os.path.join(os.path.dirname(__file__), 'simple_plugin.png') # Optional, defaults to ""

    def Run( self ):
        board = pcbnew.GetBoard()
        group = pcbnew.PCB_GROUP(self.board)
        board.Add(group)

        # Draw a track which goes from (100, 100) to (100, 110)
        track = pcbnew.PCB_TRACK(board)
        track.SetStart(pcbpoint((100, 100)))
        track.SetEnd(pcbpoint((100, 110)))
        # Size here is specified as integer nanometers, so multiply mm by 1e6
        track.SetWidth(int(0.3 * 1e6))
        track.SetLayer(pcbnew.F_Cu)
        board.Add(track)
        group.AddItem(track)

        # Now draw a via at one end of the track
        via = pcbnew.PCB_VIA(board)
        via.SetPosition(pcbpoint((100, 110)))
        via.SetDrill(int(0.3 * 1e6))
        via.SetWidth(int(0.6 * 1e6))
        board.Add(via)
        group.AddItem(via)

TestPlugin().register()