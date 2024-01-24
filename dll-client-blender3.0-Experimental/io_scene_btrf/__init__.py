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
    "author": "Glandu2/Peakz",
    "blender": (3, 0, 0),
    "version": (1, 7, 1),
    "location": "File > Import-Export",
    "description": "Export to a Rappelz NX3 file",
    "category": "Import-Export"}

import bpy
import bpy.utils.previews
from bpy_extras.io_utils import ExportHelper, ImportHelper
from bpy.props import StringProperty, BoolProperty, IntProperty, FloatProperty, CollectionProperty
from bpy.types import AddonPreferences, PropertyGroup, UIList, UILayout, Operator, Panel, Menu
from . import export_nx3
from . import import_nx3
import imp
from os import path

classes = []

def register_class(cls):
    classes.append(cls)
    return cls

@register_class
class ExportBTRF(bpy.types.Operator, ExportHelper):
    bl_idname = "export_mesh.nx3"
    bl_label = "Export NX3"
    bl_options = {'UNDO', 'PRESET'}

    filepath : StringProperty(
            subtype='FILE_PATH',
            )

    filename_ext = ".nx3"

    #peakz
    use_collection: BoolProperty(
        name="Active Collection Only",
        description="Export active Collection's objects only",
        default=False,
    )

    use_selection: BoolProperty(
        name="Selection Only",
        description="Export selected objects only",
        default=False,
    )

    use_Tanimation: BoolProperty(
        name="Export Transform Animation",
        description="Export transform animation (Location, Rotation, Scale)",
        default=False,
    )

    use_Batch: BoolProperty(
        name="Export Batch",
        description="Export each object as a separate nx3 file",
        default=False,
    )

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.label(text="Limit Export To :", icon="OBJECT_DATA")
        box.prop(self, 'use_collection')
        box.prop(self, 'use_selection')

        box = layout.box()
        box.label(text="Animation :", icon="ANIM")
        box.prop(self, 'use_Tanimation')

        box = layout.box()
        box.label(text="Batch :", icon="EXPORT")
        box.prop(self, 'use_Batch')



    def execute(self, context):
        options =[self.use_collection, self.use_selection, self.use_Tanimation, self.use_Batch]
        imp.reload(export_nx3)
        export_nx3.write(self.filepath,*options)
        return {'FINISHED'}


@register_class
class ImportBTRF(bpy.types.Operator, ImportHelper):
    bl_idname = "import_mesh.nx3"
    bl_label = "Import NX3"
    bl_options = {'UNDO', 'PRESET'}
    
    directory: StringProperty(
        subtype='DIR_PATH',
    )

    files: CollectionProperty(
        type=bpy.types.OperatorFileListElement,
    )

    filename_ext = ".nx3"


    def execute(self, context):
        imp.reload(import_nx3)
        for file in self.files:
            filepath = path.join(self.directory, file.name)
            import_nx3.read(filepath)
        return {'FINISHED'}


def menu_func_export(self, context):
    self.layout.operator(ExportBTRF.bl_idname, text="Rappelz NX3 (.nx3)", icon_value=my_icon.icon_id)


def menu_func_import(self, context):
    self.layout.operator(ImportBTRF.bl_idname, text="Rappelz NX3 (.nx3)", icon_value=my_icon.icon_id)



class nxfx:  # nxfx types
    Options = (
        ("billboard", "billboard", ""),
        ("after_image", "after_image", ""),
        ("particle", "particle", ""),
        ("reverse_particle", "reverse_particle", "")
    )
    


@register_class
class FxListItem(PropertyGroup):
    """Group of properties representing an item in the list."""

    frame: StringProperty(   
           name="StartFrame=",
           description="Put The Frame Number Here",
           default="0",
           )

    FxCreateTime: StringProperty(
        name="CreateTime",
        description="CreateTime",
        default='',
        subtype="NONE",
    )
        
    FxBeginSpeed: StringProperty(
        name="BeginSpeed",
        description="BeginSpeed",
        default='',
        subtype="NONE",
    )

    FxVelocity: StringProperty(
        name="Velocity",
        description="Velocity",
        default='',
        subtype="NONE",
    )

    FxAngle: StringProperty(
        name="Angle",
        description="Angle",
        default= '',
        subtype="NONE",
    )

    FxLifeTime: StringProperty(
        name="LifeTime",
        description="LifeTime",
        default='',
        subtype="NONE",
    )

    FxUVAni: StringProperty(
        name="UVAni",
        description="UVAnimation",
        default='',
        subtype="NONE",
    )

    FxLoop: StringProperty(
        name="Loop",
        description="Loop",
        default='',
        subtype="NONE",
    )

    FxRenderType: StringProperty(
        name="RenderType",
        description="RenderType",
        default='0',
        subtype="NONE",
    )

    FxFrameTime: IntProperty(
        name="FrameTime",
        description="FrameTime",
        default=50,
        subtype="NONE",
    )

    FxFrameNumber: IntProperty(
        name="FrameNumber",
        description="FrameNumber",
        default=200,
        subtype="NONE",
    )

    FxUseString: BoolProperty(
        name="Use Text",
        description="Use Text args seperated by a dot ",
        default=False,
        subtype="NONE",
    )


    FxString: StringProperty(
        name="Fx String",
        description="Fx text seperated by a dot ",
        default='',
        subtype="NONE",
    )
    ##### FX List ####
    
@register_class
class FX_UL_List(UIList):
    """FX UIList."""

    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):

        
        custom_icon = 'DECORATE_KEYFRAME'

        # Make sure your code supports all 3 layout types
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            #layout.label(text=item.name, icon = custom_icon)
            layout.label(text=f'{item.frame}', icon = custom_icon)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon = custom_icon)

@register_class
class FXLIST_OT_AddFrame(Operator):
    """Add a new frame to the list."""

    bl_idname = "fx_list.add_frame"
    bl_label = "Add a new frame"

    def execute(self, context):
        context.active_object.Fx_list.add()

        return{'FINISHED'}

@register_class
class FXLIST_OT_DeleteFrame(Operator):
    """Delete the selected frame from the list."""

    bl_idname = "fx_list.delete_frame"
    bl_label = "Deletes a frame"

    @classmethod
    def poll(cls, context):
        return context.active_object.Fx_list

    def execute(self, context):
        Fx_list = context.active_object.Fx_list
        Fxindex = context.active_object.Fxlist_index

        Fx_list.remove(Fxindex)
        context.active_object.Fxlist_index = min(max(0, Fxindex - 1), len(Fx_list) - 1)

        return{'FINISHED'}


class BlenderNx3Panel(Panel):
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
                row.prop(context.active_object.active_material, "MtlIllumi", text="")
            else:
                row.label(text="The Active Object Has No Material")
            
            row0 = layout.row(align=False, heading='Visibility Value')
            row0.prop(context.active_object, "OBJVisi", text="")
            row0.scale_y = 1.5
            row1 = layout.row(align=False)
            row1.prop(context.active_object, "UseNewVertexOrder", text="Use New Vertex Order Export For This Object")
            #row1.scale_y = 1.5
            row11 = layout.row(align=False)
            row11.prop(context.active_object, "OBJVertAni", text="Use Vertex Animation For This Object")
            #row11.scale_y = 1.5
            col = layout.column(align=True)
            col.separator()
            col.prop(context.active_object, "FxUse")
            
            #col.separator()
            if context.active_object.FxUse:
                
                col.label(text="Frames:")
                row = layout.row()
                row.template_list("FX_UL_List", "FX_UL_List", context.active_object,"Fx_list", context.active_object, "Fxlist_index")
                
                col = row.column(align=True)
                col.operator("fx_list.add_frame", icon='ADD', text="")
                col.operator("fx_list.delete_frame", icon='REMOVE', text="")

                if context.active_object.Fxlist_index >= 0 and context.active_object.Fx_list:
                    item = context.active_object.Fx_list[context.active_object.Fxlist_index]
                    row2 = layout.row()
                    col2 = row2.column(align=True)

                    col2.prop(item, "frame")
                    #col2.separator()

                    col2.label(text="Fx Settings :")
                    if not item.FxUseString and context.active_object.Fxlist_index == 0:
                        col2.prop(context.active_object, "Nxfx")
                        nxfxType = context.active_object.Nxfx
                        
                        if nxfxType == 'particle':
                            col2.prop(item, "FxCreateTime")
                            col2.prop(item, "FxBeginSpeed")
                            col2.prop(item, "FxVelocity")
                            col2.prop(item, "FxAngle")
                            col2.prop(item, "FxLifeTime")
                            col2.prop(item, "FxUVAni")
                            col2.prop(item, "FxLoop")
                            col2.prop(item, "FxRenderType")
                        if nxfxType == 'billboard':
                            col2.prop(item, "FxRenderType")
                        if nxfxType == 'reverse_particle':
                            col2.prop(item, "FxCreateTime")
                            col2.prop(item, "FxBeginSpeed")
                            col2.prop(item, "FxVelocity")
                            col2.prop(item, "FxAngle")
                            col2.prop(item, "FxLifeTime")
                            col2.prop(item, "FxUVAni")
                            col2.prop(item, "FxLoop")
                            col2.prop(item, "FxRenderType")
                        if nxfxType == 'after_image':
                            col2.prop(item, "FxFrameTime")
                            col2.prop(item, "FxFrameNumber")

                    if context.active_object.Fxlist_index == 0:
                        col2.separator()
                        col2.prop(item, "FxUseString")
                        if item.FxUseString:
                            col2.prop(item, "FxString")
                    else:
                        col2.prop(item, "FxString")
                    col.separator()

# icons #
@register_class                
class NX3Preferences(AddonPreferences): 
    bl_idname = __package__

    Dumppath: StringProperty(
        name="Dump Path",
        description="Path To Search For Missing Textures",
        subtype='FILE_PATH',
        default=""
    )

    def draw(self, context: bpy.types.Context):
        layout: UILayout = self.layout
        layout.prop(self, "Dumppath")
        fp = context.preferences.addons[__package__].preferences.get("Dumppath")
        if fp is not None and fp != "" and not path.exists(fp):
            layout.label(text="Path doesn't exist", icon='ERROR')

preview_collections = {}
########

# pie menu #
@register_class
class VIEW3D_MT_PIE_NX3(Menu):
    bl_label = "NX3 PIE MENU"

    def draw(self, context):
        layout = self.layout

        pie = layout.menu_pie()
        pie.operator(ImportBTRF.bl_idname, text="Import", icon_value=my_icon.icon_id)
        pie.operator(ExportBTRF.bl_idname, text="Export", icon_value=my_icon.icon_id)
############

# keymaps #
global_nx3_keymaps = []
###########
def register():
    for cls in classes:
        #print(cls)
        bpy.utils.register_class(cls)

    # icons #
    global my_icon
    pcoll = bpy.utils.previews.new() 
    my_icons_dir = path.join(path.dirname(__file__), "icons")
    pcoll.load("my_icon", path.join(my_icons_dir, "nx3.png"), 'IMAGE')
    my_icon = pcoll["my_icon"]
    preview_collections["main"] = pcoll
    #########

    # keymaps #
    window_manager = bpy.context.window_manager
    if window_manager.keyconfigs.addon:
        keymap = window_manager.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
        
        keymap_item = keymap.keymap_items.new('wm.call_menu_pie', 'A', "PRESS", shift=True, alt=True)
        keymap_item.properties.name = "VIEW3D_MT_PIE_NX3"

        global_nx3_keymaps.append((keymap, keymap_item))
    ###########



    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

    
    bpy.types.Object.FxUse = BoolProperty(
        name="Use Fx",
        description="Use Fx For This Object",
        default=False,
        subtype="NONE",
    )
        
    bpy.types.Object.OBJVisi = FloatProperty(
        name="Visibilty Value",
        description="The Visibilty Value of the Active Object",
        default=1,
        max=1,
        min=0,
        step=0.01,
        precision=2,
        subtype="FACTOR",
    )

    bpy.types.Object.OBJVertAni = BoolProperty(
        name="Use Vertex Animation",
        description="Use Vertex Animation For This Object",
        default=False,
        subtype="NONE",
    )

    bpy.types.Object.UseNewVertexOrder = BoolProperty(
        name="Use New Vertex Order Export",
        description="Use New Vertex Order Export For This Object (Try this if the mesh is broken on export)",
        default=False,
        subtype="NONE",
    )

    bpy.types.Object.Fx_list = CollectionProperty(type = FxListItem)
    bpy.types.Object.Fxlist_index = IntProperty(name = "Index for Fx_list", default = 0)

    ###### Material ######
    bpy.types.Material.MtlIllumi = FloatProperty(
        name="Additive Value",
        description="The Additive Value of the Active Material",
        default=0,
        max=1,
        min=0,
        step=1,
        precision=1,
        subtype="FACTOR",
    )
        
    



def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    # icons #
    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()
    ########

    # keymaps #
    window_manager = bpy.context.window_manager
    if window_manager and window_manager.keyconfigs and window_manager.keyconfigs.addon:
        
        for keymap, keymap_item in global_nx3_keymaps:
            keymap.keymap_items.remove(keymap_item)

    global_nx3_keymaps.clear()
    ###########

    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
    
    ob = bpy.types.Object

    del ob.OBJVisi
    del ob.OBJVertAni
    del ob.UseNewVertexOrder

    ##### FX List ####
    del ob.FxUse
    del ob.Fx_list
    del ob.Fxlist_index
    ###### Material ######
    mtl= bpy.types.Material

    del mtl.MtlIllumi

if __name__ == "__main__":
    register()
