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
from bpy.props import StringProperty, BoolProperty, IntProperty, FloatProperty
from . import export_nx3
from . import import_nx3
import imp

classes = []

def register_class(cls):
    classes.append(cls)
    return cls

@register_class
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


@register_class
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


class nxfx:  # nxfx types
    Options = (
        ("billboard", "billboard", ""),
        ("after_image", "after_image", ""),
        ("particle", "particle", ""),
        ("reverse_particle", "reverse_particle", "")
    )
    
class BlenderNx3Panel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Nx3"
    bl_context = "objectmode"
    
@register_class
class VIEW3D_PT_BlenderNx3Main(BlenderNx3Panel): # UI BY Peakz
    """Creates a Panel in Properties(N)"""

    bl_label = "Nx3 UI by Peakz"
    bl_idname = "VIEW3D_PT_BlenderNx3Main"

    bpy.types.Object.Nxfx = bpy.props.EnumProperty(
        name="nxfx", items=nxfx.Options
    )

    def draw(self, context):
        if context.active_object.type == 'MESH':
              
            layout = self.layout
            row = layout.row(align=False, heading='Additive Value')
            row.scale_y = 1.5
            if context.active_object.active_material:
                row.prop(context.active_object.active_material, "MtlIllumi")
            else:
                row.label(text="The Active Object Has No Material")

            col = layout.column(align=True)
            col.prop(context.active_object, "FxUse")
            #col.separator()
            if context.active_object.FxUse:
                if not context.active_object.FxUseString:
                    col.label(text="Fx Settings :")
                    col.prop(context.active_object, "Nxfx")
                    nxfxType = context.active_object.Nxfx
                
                    if nxfxType == 'particle':
                        col.prop(context.active_object, "FxCreateTime")
                        col.prop(context.active_object, "FxBeginSpeed")
                        col.prop(context.active_object, "FxVelocity")
                        col.prop(context.active_object, "FxAngle")
                        col.prop(context.active_object, "FxLifeTime")
                        col.prop(context.active_object, "FxUVAni")
                        col.prop(context.active_object, "FxLoop")
                        col.prop(context.active_object, "FxRenderType")
                    if nxfxType == 'billboard':
                        col.prop(context.active_object, "FxRenderType")
                    if nxfxType == 'reverse_particle':
                        col.prop(context.active_object, "FxCreateTime")
                        col.prop(context.active_object, "FxBeginSpeed")
                        col.prop(context.active_object, "FxVelocity")
                        col.prop(context.active_object, "FxAngle")
                        col.prop(context.active_object, "FxLifeTime")
                        col.prop(context.active_object, "FxUVAni")
                        col.prop(context.active_object, "FxLoop")
                        col.prop(context.active_object, "FxRenderType")
                    if nxfxType == 'after_image':
                        col.prop(context.active_object, "FxFrameTime")
                        col.prop(context.active_object, "FxFrameNumber")
                                    
                col.separator()
                col.prop(context.active_object, "FxUseString")
                if context.active_object.FxUseString:
                    col.prop(context.active_object, "FxString")



def register():
	for cls in classes:
		#print(cls)
		bpy.utils.register_class(cls)

	bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
	bpy.types.TOPBAR_MT_file_export.append(menu_func_export)
	
	###### FX ######
	bpy.types.Object.FxCreateTime = StringProperty(
        name="CreateTime",
        description="CreateTime",
        default='',
        subtype="NONE",
    )
        
	bpy.types.Object.FxBeginSpeed = StringProperty(
        name="BeginSpeed",
        description="BeginSpeed",
        default='',
        subtype="NONE",
    )
	
	bpy.types.Object.FxVelocity = StringProperty(
        name="Velocity",
        description="Velocity",
        default='',
        subtype="NONE",
    )
	
	bpy.types.Object.FxAngle = StringProperty(
        name="Angle",
        description="Angle",
        default= '',
        subtype="NONE",
    )
	
	bpy.types.Object.FxLifeTime = StringProperty(
        name="LifeTime",
        description="LifeTime",
        default='',
        subtype="NONE",
    )
	
	bpy.types.Object.FxUVAni = StringProperty(
        name="UVAni",
        description="UVAnimation",
        default='',
        subtype="NONE",
    )

	bpy.types.Object.FxLoop = StringProperty(
        name="Loop",
        description="Loop",
        default='',
        subtype="NONE",
    )

	bpy.types.Object.FxRenderType = StringProperty(
        name="RenderType",
        description="RenderType",
        default='0',
        subtype="NONE",
    )

	bpy.types.Object.FxFrameTime = IntProperty(
        name="FrameTime",
        description="FrameTime",
        default=50,
        subtype="NONE",
    )

	bpy.types.Object.FxFrameNumber = IntProperty(
        name="FrameNumber",
        description="FrameNumber",
        default=200,
        subtype="NONE",
    )

	bpy.types.Object.FxUseString = BoolProperty(
        name="Use Text",
        description="Use Text args seperated by a dot ",
        default=False,
        subtype="NONE",
    )

	bpy.types.Object.FxUse = BoolProperty(
        name="Use Fx",
        description="Use Fx For This Object",
        default=False,
        subtype="NONE",
    )

	bpy.types.Object.FxString = StringProperty(
        name="Fx String",
        description="Fx text seperated by a dot ",
        default='',
        subtype="NONE",
    )

    ###### Material ######
	bpy.types.Material.MtlIllumi = FloatProperty(
        name="",
        description="The Additive Value of the Active Material",
        default=0,
        max=1,
        min=0,
        step=1,
        precision=1,
        subtype="NONE",
    )



def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)
	
	bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
	bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
        
    ###### FX ######
	ob = bpy.types.Object

	del ob.FxUse
	del ob.FxCreateTime
	del ob.FxBeginSpeed
	del ob.FxVelocity
	del ob.FxAngle
	del ob.FxLifeTime
	del ob.FxLoop
	del ob.FxUVAni
	del ob.FxRenderType
	del ob.FxFrameTime
	del ob.FxFrameNumber
	del ob.FxUseString
	del ob.FxString
        
    ###### Material ######
	mtl= bpy.types.Material

	del mtl.MtlIllumi

if __name__ == "__main__":
	register()
