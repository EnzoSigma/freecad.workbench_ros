from __future__ import annotations

import copy
from pathlib import Path
import tempfile
from typing import Optional
import xml.etree.ElementTree as et
from xml.dom import minidom

import FreeCAD as fc
import FreeCADGui as fcgui

from PySide import QtGui  # FreeCAD's PySide!
from PySide import QtCore  # FreeCAD's PySide!

from ..freecad_utils import is_box
from ..freecad_utils import is_cylinder
from ..freecad_utils import is_sphere
from ..freecadgui_utils import get_subobjects_and_placements
from ..gui_utils import tr
from ..urdf_utils import urdf_collision_from_box
from ..urdf_utils import urdf_collision_from_cylinder
from ..urdf_utils import urdf_collision_from_object
from ..urdf_utils import urdf_collision_from_sphere
from ..wb_utils import is_joint
from ..wb_utils import is_link
from ..wb_utils import is_robot
from ..wb_utils import is_workcell
from ..wb_utils import is_xacro_object


# Typing hints.
DO = fc.DocumentObject
SO = 'FreeCADGui.SelectionObject'  # Could not get the class from Python.

# Otherwise et.tostring uses xlmns:ns0 as xacro namespace.
et.register_namespace('xacro', 'http://ros.org/wiki/xacro')

# Generated temporary directories.
# Implementation note: will be deleted when closing FreeCAD.
_temp_dirs: list[tempfile.TemporaryDirectory] = []


def _supported_object_selected():
    for obj in fcgui.Selection.getSelection():
        if hasattr(obj, 'Placement'):
            return True
        if is_robot(obj):
            return True
        if is_xacro_object(obj):
            return True
        if is_workcell(obj):
            return True
    return False


class _UrdfExportCommand:
    """Command to export the selected objects to URDF."""

    def GetResources(self):
        return {'Pixmap': 'urdf_export.svg',
                'MenuText': tr('Export to URDF'),
                'ToolTip': tr('Export selected elements to URDF'),
                }

    def Activated(self):
        def set_package_name() -> None:
            nonlocal txt
            txt = original_txt.replace('$package_name$',
                                       package_name_lineedit.text())
            txt_view.setPlainText(txt)

        selection = fcgui.Selection.getSelectionEx('', 0)
        if not selection:
            fc.Console.PrintWarning('Nothing selected, nothing to do\n')
            return
        txt = ''
        has_mesh = False
        show_xml = True
        exported_objects: list[fc.DocumentObject] = []
        for obj, placement in get_subobjects_and_placements(selection):
            if not hasattr(obj, 'TypeId'):
                # For now, only objects with 'TypeId' are supported.
                continue
            if obj in exported_objects:
                # Object already exported.
                continue
            exported_objects.append(obj)
            xmls: list[et.ElementTree] = []
            if is_box(obj):
                xmls.append(urdf_collision_from_box(
                    obj, placement, ignore_obj_placement=True))
            elif is_sphere(obj):
                xmls.append(urdf_collision_from_sphere(
                    obj, placement, ignore_obj_placement=True))
            elif is_cylinder(obj):
                xmls.append(urdf_collision_from_cylinder(
                    obj, placement, ignore_obj_placement=True))
            elif (is_robot(obj)
                  or is_workcell(obj)):
                if hasattr(obj, 'Proxy'):
                    xmls.append(obj.Proxy.export_urdf())
                    show_xml = False
            elif (is_xacro_object(obj)
                  or is_joint(obj)):
                if hasattr(obj, 'Proxy'):
                    xmls.append(obj.Proxy.export_urdf())
            elif is_link(obj):
                if hasattr(obj, 'Proxy'):
                    temp_dir = tempfile.TemporaryDirectory(prefix='workbench_ros-')
                    package_path = Path(temp_dir.name)
                    xmls.append(obj.Proxy.export_urdf(package_path, 'package_name'))
                    if list(package_path.iterdir()):
                        # Non empty directory.
                        xmls.append(et.Comment(f'Exported mesh files in "{package_path}"'
                                               ' will be deleted when'
                                               ' closing FreeCAD!'))
                        _temp_dirs.append(temp_dir)
            elif hasattr(obj, 'Placement'):
                has_mesh = True
                package_name = '$package_name$'  # Will be replaced later by the GUI.
                xmls += urdf_collision_from_object(
                        obj,
                        package_name=package_name,
                        placement=placement,
                        )
            if xmls:
                txt += f'  <!-- {obj.Label} -->\n'
                for xml in xmls:
                    txt += et.tostring(xml).decode('utf-8')
                    txt += '\n'
        if txt and show_xml:
            if 'dummy>' in txt:
                fc.Console.PrintError('Object labels cannot contain '
                                      '"<dummy>" or "</dummy>"')
            txt = f'<dummy>{txt}</dummy>'  # xml cannot have multiple root tags
            txt = (minidom.parseString(txt)
                   .toprettyxml(indent='  ', encoding='utf-8')
                   .decode('utf-8'))
            # Maybe see
            # http://www.ronrothman.com/public/leftbraned/xml-dom-minidom-toprettyxml-and-silly-whitespace/#best-solution
            # if whitespace problems.
            txt = txt.replace('<dummy>', '').replace('</dummy>', '')
            original_txt = copy.copy(txt)
            main_win = fcgui.getMainWindow()
            dialog = QtGui.QDialog(main_win, QtCore.Qt.Tool)
            layout = QtGui.QVBoxLayout(dialog)
            if has_mesh:
                package_name_lineedit = QtGui.QLineEdit('$package_name$')
                package_name_lineedit.editingFinished.connect(lambda: set_package_name())
                layout.addWidget(package_name_lineedit)
            txt_view = QtGui.QPlainTextEdit(txt)
            txt_view.setReadOnly(True)
            txt_view.setMinimumWidth(main_win.width() // 2)
            txt_view.setMinimumHeight(main_win.height() // 2)
            txt_view.setLineWrapMode(QtGui.QPlainTextEdit.NoWrap)
            layout.addWidget(txt_view)
            dialog.exec_()

    def IsActive(self):
        return _supported_object_selected()


fcgui.addCommand('UrdfExport', _UrdfExportCommand())
