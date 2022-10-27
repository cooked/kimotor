import pcbnew
import os

class SimplePlugin(pcbnew.ActionPlugin):
    def defaults(self):
        self.name = "KiMotor - PCB motor stator design"
        self.category = "A descriptive category name"
        self.description = "KiMotor automates the design of parametric PCB motor stators used in axial-flux motors"
        self.show_toolbar_button = True # Optional, defaults to False
        self.icon_file_name = os.path.join(os.path.dirname(__file__), 'flexibility.png') # Optional, defaults to ""

    def Run(self):
        # The entry function of the plugin that is executed on user action
        print("Hello World")

SimplePlugin().register() # Instantiate and register to Pcbnew