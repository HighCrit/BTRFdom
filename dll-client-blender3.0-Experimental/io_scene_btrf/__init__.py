#
# BTRFdom - Rappelz BTRF Document Object Model
# By Glandu2/Ldxngx/Peakz
# Copyright 2013 Glandu2
# Updated to 3.0 by Andrej Tetkic
#
# This file is part of BTRFdom.
# BTRFdom is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BTRFdom is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with BTRFdom.  If not, see <http://www.gnu.org/licenses/>.
#

bl_info = {
	"name": "Rappelz NX3 format",
	"author": "Glandu2/Ldxngx, Updated to 3.0 by Andrej Tetkic",
	"blender": (3, 0, 0),
	"version": (0, 2, 0),
	"location": "File > Import-Export",
	"description": "Export to a Rappelz NX3 file",
	"category": "Import-Export"}

import bpy
from bpy_extras.io_utils import ExportHelper, ImportHelper
from bpy.props import StringProperty, BoolProperty, IntProperty
from . import export_nx3
from . import import_nx3
import imp


class ExportBTRF(bpy.types.Operator, ExportHelper):
	bl_idname = "export_mesh.nx3"
	bl_label = "Export NX3"
	bl_options = {'PRESET'}

	filepath : StringProperty(
			subtype='FILE_PATH',
			)

	filename_ext = ".nx3"

	#peakz
	use_collection: BoolProperty(
        name="Active Collection Only",
        description="Export Active Collection's objects only",
        default=False,
    )

	use_selection: BoolProperty(
        name="Selection Only",
        description="Export Selected objects only",
        default=False,
    )

	use_Tanimation: BoolProperty(
        name="Export Transform Animation",
        description="Export Transform Animation (Location, Rotation, Scale)",
        default=False,
    )


	def execute(self, context):
		options =[self.use_collection, self.use_selection, self.use_Tanimation]
		imp.reload(export_nx3)
		export_nx3.write(self.filepath,*options)
		return {'FINISHED'}


class ImportBTRF(bpy.types.Operator, ImportHelper):
	bl_idname = "import_mesh.nx3"
	bl_label = "Import NX3"
	bl_options = {'PRESET'}

	filepath : StringProperty(
			subtype='FILE_PATH',
			)

	filename_ext = ".nx3"


	def execute(self, context):
		imp.reload(import_nx3)
		import_nx3.read(self.filepath)
		return {'FINISHED'}


def menu_func_export(self, context):
	self.layout.operator(ExportBTRF.bl_idname, text="Rappelz NX3 (.nx3)")


def menu_func_import(self, context):
	self.layout.operator(ImportBTRF.bl_idname, text="Rappelz NX3 (.nx3)")

classes = [
	ExportBTRF,
	ImportBTRF,
	]

def register():
	for cls in classes:
		bpy.utils.register_class(cls)

	bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
	bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)
	
	bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
	bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)

if __name__ == "__main__":
	register()
