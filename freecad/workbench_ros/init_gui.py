
import FreeCADGui as fcgui

from .ui import command_assembly_from_urdf
from .ui import command_box_from_bounding_box
from .ui import command_new_joint
from .ui import command_new_link
from .ui import command_new_robot
from .ui import command_new_workcell
from .ui import command_new_xacro_object
from .ui import command_reload # Developer tool.
from .ui import command_robot_from_urdf
from .ui import command_set_link_mounted_placement
from .ui import command_sphere_from_bounding_box
from .ui import command_urdf_export
from .ui import command_wb_settings
from .wb_utils import ICON_PATH


class RosWorkbench(fcgui.Workbench):
    """Class which gets initiated at startup of the GUI."""

    MenuText = 'ROS workbench'
    ToolTip = 'ROS-related workbench'
    Icon = str(ICON_PATH / 'ros_9dotslogo_color.svg')

    def GetClassName(self):
        return 'Gui::PythonWorkbench'

    def Initialize(self):
        """This function is called at the first activation of the workbench.

        This is the place to import all the commands.

        """
        # The order here defines the order of the icons in the GUI.
        commands = [
            'NewRobot',  # Defined in ./ui/command_new_robot.py.
            'NewLink',  # Defined in ./ui/command_new_link.py.
            'NewJoint',  # Defined in ./ui/command_new_joint.py.
            'NewWorkcell',  # Defined in ./ui/command_new_workcell.py.
            'NewXacroObject',  # Defined in ./ui/command_new_xacro_object.py.
            'BoxFromBoundingBox',  # Defined in ./ui/command_box_from_bounding_box.py.
            'SphereFromBoundingBox',  # Defined in ./ui/command_sphere_from_bounding_box.py.
            'UrdfImport',  # Defined in ./ui/command_robot_from_urdf.py.
            'AssemblyFromUrdf',  # Defined in ./ui/command_assembly_from_urdf.py.
            'UrdfExport',  # Defined in ./ui/command_urdf_export.py.
            'SetLinkMountedPlacement',  # Defined in ./ui/command_set_link_mounted_placement.py.
            'WbSettings',  # Defined in ./ui/command_wb_settings.py.
            'Reload',  # Comment out to disable this developer tool.
            ]
        self.appendToolbar('ROS', commands)
        self.appendMenu('ROS', commands)

        fcgui.addIconPath(str(ICON_PATH))
        # fcgui.addLanguagePath(joinDir('Resources/translations'))

    def Activated(self):
        """Code run when a user switches to this workbench."""
        pass

    def Deactivated(self):
        """Code run when this workbench is deactivated."""
        pass


fcgui.addWorkbench(RosWorkbench())
