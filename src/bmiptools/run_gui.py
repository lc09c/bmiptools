"""
Title: 'run_gui.py'
Date: 03/01/2022
Author: Curcuraci L.

Scope: Run bmiptools gui.
"""
#################
#####   LIBRARIES
#################


from bmiptools.gui.bmiptools_gui import BMIPToolsGUI


############
#####   MAIN
############


if __name__ == '__main__':

    bmip_tool_gui = BMIPToolsGUI()
    bmip_tool_gui()