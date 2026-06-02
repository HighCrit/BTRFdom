#
# BTRFdom - Rappelz BTRF Document Object Model
# By Glandu2, HighCrit
# Copyright 2013-2026
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

"""
NX3 structure:
template nx3_version_header {
    dword   version;
}
template nx3_mtl_header {
    dword   mtl_size;
    nx3_mtl mtl_array[mtl_size] {
        dword           sub_mtl_block_size;
        nx3_mtl_block   sub_mtl_block_array[sub_mtl_block_size] {
            string  mtl_name;
            string  texture_name;
            dword   mtl_id;
            dword   channel_id;
            float   power;
            float   self_illumi;
            char    smoothing;
            dword   ambient;
            dword   diffuse;
            dword   specular;
        }
    }
}
template nx3_new_mesh_header {
    dword           mesh_size;
    nx3_new_mesh    mesh_array[mesh_size] {
        string          mesh_name;
        dword           material_id;
        dword           channel_id;
        dword           mesh_block_size;
        nx3_mesh_block  mesh_block_array[mesh_block_size] {
            dword           texture_index;
            dword           mesh_frame_size;
            nx3_mesh_frame  mesh_frame_array[mesh_frame_size] {
                dword   time_value;
                dword   vertex_size;
                float   vertex_array[vertex_size];
                dword   normal_size;
                float   normal_array[normal_size];
                dword   texel_size;
                float   texel_array[texel_size];
                dword   color_size;
                dword   color_array[color_size];
                dword               bone_size;
                nx3_weight_frame    bone_block[bone_size] {
                    string  bone_name;
                    dword   weight_size;
                    float   weight_array[weight_size];
                    dword   offset_vector_size;
                    float   offset_vector_array[offset_vector_size];
                }
                float   mesh_tm[16];
            }
            dword   index_buffer_size;
            word    index_buffer_array[index_buffer_size];
            dword   lightmap_index;
        }
        dword   ani_time_size;
        dword   ani_time_array[ani_time_size];
        dword   ani_matrix_size;
        float   ani_matrix_array[ani_matrix_size];
        dword   visi_time_size;
        dword   visi_time_array[visi_time_size];
        float   visi_value_array[visi_time_size];
        dword   fx_size;
        nx3_fx  fx_array[fx_size];
        dword           mesh_children_size;
        nx3_new_mesh    mesh_children_array[mesh_children_size];
    }
    dword       mesh_tm_size;
    nx3_mesh_tm mesh_tm_array[mesh_tm_size] {
        string  name;
        float   tm[16];
    }
}
"""

import bpy
import uuid
from .btrfdom import BtrfParser, TmlFile, BtrfRootBlock, BtrfBlock
import os

nx3_version_header_guid = uuid.UUID('{81BCE021-AD76-346f-9C7D-19885FD118B6}')

nx3_mtl_header_guid = uuid.UUID('{209BBB41-681F-4b9b-9744-4D88E1413DCC}')
nx3_mtl_guid = uuid.UUID('{52BCCAA6-3C16-4286-8B9E-1A798F9D94DE}')
nx3_mtl_block_guid = uuid.UUID('{81BCE071-AC76-496f-9C7D-19885FD118B6}')

nx3_new_mesh_header_guid = uuid.UUID('{A6D25AEB-A735-1fef-C17D-EE2117498226}')
nx3_new_mesh_guid = uuid.UUID('{1718DC1B-1DB1-458a-9C7E-C3D46FC4585B}')
nx3_mesh_block_guid = uuid.UUID('{C817F7B0-E4E7-40fb-97B3-2B97CC000521}')
nx3_mesh_frame_guid = uuid.UUID('{1C77954B-CDD5-4615-B7AD-F23BD3D0C23E}')
nx3_weight_frame_guid = uuid.UUID('{B513DF30-80BE-44f4-980B-84B9D979A607}')
nx3_mesh_tm_guid = uuid.UUID('{F09C560E-7328-411e-87A3-EEB165D5F929}')


class Material:
    def __init__(self, texture_id, material_id, channel_id, material):
        self.texture_id = texture_id
        self.material_id = material_id
        self.channel_id = channel_id
        self.material = material

    def equals(self, other):
        return (isinstance(other, self.__class__)
                and self.texture_id == other.texture_id
                and self.material_id == other.material_id
                and self.channel_id == other.channel_id
                and self.material == other.material)

    def __ne__(self, other):
        return not self.__eq__(other)


# Represent a vertex with its normal and UV coords.
class VertexInfo:
    def __init__(self, vertex_index, vertex, normal, texel=None):
        self.vertex_index = vertex_index
        self.vertex = vertex
        self.normal = normal
        self.texel = texel if texel is not None else [0, 0]

    def equals(self, other):
        return (isinstance(other, self.__class__)
                and abs(self.vertex[0] - other.vertex[0]) < 0.0001
                and abs(self.vertex[1] - other.vertex[1]) < 0.0001
                and abs(self.vertex[2] - other.vertex[2]) < 0.0001
                and abs(self.normal[0] - other.normal[0]) < 0.0001
                and abs(self.normal[1] - other.normal[1]) < 0.0001
                and abs(self.normal[2] - other.normal[2]) < 0.0001
                and abs(self.texel[0] - other.texel[0]) < 0.0001
                and abs(self.texel[1] - other.texel[1]) < 0.0001)

    def __ne__(self, other):
        return not self.__eq__(other)


class BoneInfo:
    __slots__ = ("name", "global_matrix")

    def __init__(self, name, global_matrix):
        self.name = name
        self.global_matrix = global_matrix


def info(msg):
    print('btrfdom: Info: ' + msg)


def warn(msg):
    print('btrfdom: Warning: ' + msg)


def error(msg):
    print('btrfdom: Error: ' + msg)
    raise Exception(msg)


def get_materials_bones_from_object(blender_object, materials_info, bones_info):
    if blender_object.type == 'MESH':
        for material_index, material in enumerate(blender_object.material_slots):
            if blender_object.name not in materials_info:
                materials_info[blender_object.name] = []
            materials_info[blender_object.name].append(
                Material(material_index, len(materials_info) - 1, 0, material.material)
            )

    if blender_object.type == 'ARMATURE':
        for bone in blender_object.pose.bones:
            # Blender 4.x: use @ for matrix multiplication instead of *
            bone_global_matrix = (bone.id_data.matrix_world.inverted() @ bone.matrix).inverted().transposed()
            tm = [val for vect in bone_global_matrix for val in vect]
            if bone.name not in bones_info:
                bones_info[bone.name] = BoneInfo(bone.name, tm)
            else:
                raise Exception(
                    "Bones names must be unique through the whole file. Several bones have the name %s" % bone.name
                )


def get_materials_bones():
    materials_info = {}
    bones_info = {}

    for obj in bpy.data.objects:
        get_materials_bones_from_object(obj, materials_info, bones_info)

    return [materials_info, bones_info]


def get_texture_filename(material):
    """
    In Blender 4.x, materials use nodes. We look for an Image Texture node
    connected to the Base Color of a Principled BSDF (or any Image Texture node).
    Falls back to legacy texture_slots if nodes are disabled.
    """
    if material is None:
        return "(null)"

    # Blender 2.80+ node-based materials
    if material.use_nodes and material.node_tree:
        for node in material.node_tree.nodes:
            if node.type == 'TEX_IMAGE' and node.image:
                return os.path.basename(node.image.filepath)

    return "(null)"


def load_btrfdom():
    script_dir = os.path.dirname(os.path.abspath(__file__))

    tmlFile = TmlFile()
    tmlFile.create()

    tmlFile.parseFile(script_dir + "/nx3.tml")
    tmlFile.parseFile(script_dir + "/nobj.tml")

    rootBlock = BtrfRootBlock()
    rootBlock.create(tmlFile)

    return (tmlFile, rootBlock)


# version
def write_version(tmlFile, rootBlock):
    fieldInfo = tmlFile.getTemplateByGuid(nx3_version_header_guid.bytes_le)

    block = BtrfBlock()
    block.create(fieldInfo, rootBlock)

    subBlockInfo = fieldInfo.getField(0)
    subBlock = BtrfBlock()
    subBlock.create(subBlockInfo, rootBlock)
    subBlock.setDataInt(0, 65536)

    block.addBlock(subBlock)
    rootBlock.addBlock(block)


def get_mtl_block(tmlFile, rootBlock, material_info):
    fieldInfo = tmlFile.getTemplateByGuid(nx3_mtl_block_guid.bytes_le)

    block = BtrfBlock()
    block.create(fieldInfo, rootBlock)

    mtl_name = material_info.material.name
    texture_name = get_texture_filename(material_info.material)
    mtl_id = material_info.material_id
    channel_id = material_info.channel_id
    power = 0
    self_illumi = 0
    smoothing = 0
    ambient = 0
    diffuse = 0
    specular = 0

    subBlock = BtrfBlock()
    subBlock.create(fieldInfo.getField(0), rootBlock)
    subBlock.setDataString(0, mtl_name)
    block.addBlock(subBlock)

    subBlock.create(fieldInfo.getField(1), rootBlock)
    subBlock.setDataString(0, texture_name)
    block.addBlock(subBlock)

    subBlock.create(fieldInfo.getField(2), rootBlock)
    subBlock.setDataInt(0, mtl_id)
    block.addBlock(subBlock)

    subBlock.create(fieldInfo.getField(3), rootBlock)
    subBlock.setDataInt(0, channel_id)
    block.addBlock(subBlock)

    subBlock.create(fieldInfo.getField(4), rootBlock)
    subBlock.setDataFloat(0, power)
    block.addBlock(subBlock)

    subBlock.create(fieldInfo.getField(5), rootBlock)
    subBlock.setDataFloat(0, self_illumi)
    block.addBlock(subBlock)

    subBlock.create(fieldInfo.getField(6), rootBlock)
    subBlock.setDataChar(0, smoothing)
    block.addBlock(subBlock)

    subBlock.create(fieldInfo.getField(7), rootBlock)
    subBlock.setDataInt(0, ambient)
    block.addBlock(subBlock)

    subBlock.create(fieldInfo.getField(8), rootBlock)
    subBlock.setDataInt(0, diffuse)
    block.addBlock(subBlock)

    subBlock.create(fieldInfo.getField(9), rootBlock)
    subBlock.setDataInt(0, specular)
    block.addBlock(subBlock)

    return block


def get_mtl_data(tmlFile, rootBlock, materials_info):
    fieldInfo = tmlFile.getTemplateByGuid(nx3_mtl_guid.bytes_le)

    block = BtrfBlock()
    block.create(fieldInfo, rootBlock)

    arrayBlock = BtrfBlock()
    arrayBlock.create(fieldInfo.getField(0), rootBlock)

    for materials_info_per_object in list(materials_info.values()):
        for material_info in materials_info_per_object:
            subBlock = get_mtl_block(tmlFile, rootBlock, material_info)
            arrayBlock.addBlock(subBlock)

    block.addBlock(arrayBlock)
    return block


def write_mtl_header(tmlFile, rootBlock, materials_info):
    fieldInfo = tmlFile.getTemplateByGuid(nx3_mtl_header_guid.bytes_le)

    block = BtrfBlock()
    block.create(fieldInfo, rootBlock)

    arrayBlock = BtrfBlock()
    arrayBlock.create(fieldInfo.getField(0), rootBlock)
    subBlock = get_mtl_data(tmlFile, rootBlock, materials_info)
    arrayBlock.addBlock(subBlock)
    block.addBlock(arrayBlock)

    rootBlock.addBlock(block)


def get_vertex_index_weight(vertex_group, vertex_indices):
    data = []
    for rpz_index, index in enumerate(vertex_indices):
        try:
            weight = vertex_group.weight(index)
            data.append(rpz_index)
            data.append(weight)
        except RuntimeError:
            pass
    return data


def get_nx3_weight_frame(tmlFile, rootBlock, vertex_group, vertex_indices):
    fieldInfo = tmlFile.getTemplateByGuid(nx3_weight_frame_guid.bytes_le)
    block = BtrfBlock()
    block.create(fieldInfo, rootBlock)

    weight_list = get_vertex_index_weight(vertex_group, vertex_indices)

    bone_name = vertex_group.name
    weight_size = len(weight_list)
    weight_array = weight_list
    offset_vector_size = int(len(weight_list) / 2 * 3)

    subBlock = BtrfBlock()
    subBlock.create(fieldInfo.getField(0), rootBlock)
    subBlock.setDataString(0, bone_name)
    block.addBlock(subBlock)

    subBlock.create(fieldInfo.getField(1), rootBlock)
    subBlock.setElementNumber(weight_size)
    for i in range(weight_size):
        subBlock.setDataFloat(i, weight_array[i])
    block.addBlock(subBlock)

    subBlock.create(fieldInfo.getField(2), rootBlock)
    subBlock.setElementNumber(offset_vector_size)
    for i in range(offset_vector_size):
        subBlock.setDataFloat(i, 0)
    block.addBlock(subBlock)

    return block


def index_of_vertex_info(vertex_info_array, vertex_info):
    for i, v in enumerate(vertex_info_array):
        if vertex_info.equals(v):
            return i
    return -1


def get_nx3_mesh_frame(tmlFile, rootBlock, mesh_matrix, vertex_info_array, vertex_groups, has_texel):
    fieldInfo = tmlFile.getTemplateByGuid(nx3_mesh_frame_guid.bytes_le)

    block = BtrfBlock()
    block.create(fieldInfo, rootBlock)

    time_value = 0
    vertex_array = [coord for vertex_info in vertex_info_array for coord in vertex_info.vertex]
    normal_array = [coord for vertex_info in vertex_info_array for coord in vertex_info.normal]

    if has_texel:
        texel_array = [(vertex_info.texel[0], 1 - vertex_info.texel[1]) for vertex_info in vertex_info_array]
    else:
        texel_array = []

    color_array = []

    vertex_indices = [vertex_info.vertex_index for vertex_info in vertex_info_array]
    bone_block = [get_nx3_weight_frame(tmlFile, rootBlock, vertex_group, vertex_indices)
                  for vertex_group in vertex_groups]
    mesh_tm = [val for vect in mesh_matrix.transposed() for val in vect]

    subBlock = BtrfBlock()
    subBlock.create(fieldInfo.getField(0), rootBlock)
    subBlock.setDataInt(0, time_value)
    block.addBlock(subBlock)

    subBlock.create(fieldInfo.getField(1), rootBlock)
    subBlock.setElementNumber(len(vertex_array))
    for i in range(len(vertex_array)):
        subBlock.setDataFloat(i, vertex_array[i])
    block.addBlock(subBlock)

    subBlock.create(fieldInfo.getField(2), rootBlock)
    subBlock.setElementNumber(len(normal_array))
    for i in range(len(normal_array)):
        subBlock.setDataFloat(i, normal_array[i])
    block.addBlock(subBlock)

    subBlock.create(fieldInfo.getField(3), rootBlock)
    subBlock.setElementNumber(int(len(texel_array) * 2))
    for i in range(len(texel_array)):
        subBlock.setDataFloat(int(i * 2), texel_array[i][0])
        subBlock.setDataFloat(int(i * 2 + 1), texel_array[i][1])
    block.addBlock(subBlock)

    subBlock.create(fieldInfo.getField(4), rootBlock)
    subBlock.setElementNumber(len(color_array))
    for i in range(len(color_array)):
        subBlock.setDataInt(i, color_array[i])
    block.addBlock(subBlock)

    subBlock.create(fieldInfo.getField(5), rootBlock)
    for bone in bone_block:
        subBlock.addBlock(bone)
    block.addBlock(subBlock)

    subBlock.create(fieldInfo.getField(6), rootBlock)
    for i in range(16):
        subBlock.setDataFloat(i, mesh_tm[i])
    block.addBlock(subBlock)

    return block


def get_nx3_mesh_block(tmlFile, rootBlock, mesh_object, mesh_data, mesh_block_faces, tex_index):
    fieldInfo = tmlFile.getTemplateByGuid(nx3_mesh_block_guid.bytes_le)

    block = BtrfBlock()
    block.create(fieldInfo, rootBlock)

    has_texture = tex_index is not None
    texture_index = tex_index if has_texture else 0

    vertex_groups = mesh_object.vertex_groups
    vertex_info_array = []
    index_array = []

    # Blender 4.x: use uv_layers instead of removed tessface_uv_textures
    uv_layer = mesh_data.uv_layers.active.data if (has_texture and mesh_data.uv_layers.active) else None

    for poly in mesh_block_faces:
        loop_indices = list(poly.loop_indices)
        # Reverse to match original winding order
        for loop_pos in reversed(range(len(loop_indices))):
            loop_index = loop_indices[loop_pos]
            vertex_index = mesh_data.loops[loop_index].vertex_index

            if has_texture and uv_layer:
                uv = uv_layer[loop_index].uv
                vertex_info = VertexInfo(
                    vertex_index,
                    mesh_data.vertices[vertex_index].co,
                    mesh_data.vertices[vertex_index].normal,
                    uv
                )
            else:
                vertex_info = VertexInfo(
                    vertex_index,
                    mesh_data.vertices[vertex_index].co,
                    mesh_data.vertices[vertex_index].normal
                )

            index = index_of_vertex_info(vertex_info_array, vertex_info)
            if index == -1:
                index = vertex_info.vertex_index
                vertex_info_array.append(vertex_info)
            index_array.append(index)

    mesh_frame = get_nx3_mesh_frame(tmlFile, rootBlock, mesh_object.matrix_world,
                                    vertex_info_array, vertex_groups, has_texture)

    subBlock = BtrfBlock()
    subBlock.create(fieldInfo.getField(0), rootBlock)
    subBlock.setDataInt(0, texture_index)
    block.addBlock(subBlock)

    subBlock.create(fieldInfo.getField(1), rootBlock)
    subBlock.addBlock(mesh_frame)
    block.addBlock(subBlock)

    subBlock.create(fieldInfo.getField(2), rootBlock)
    subBlock.setElementNumber(len(index_array))
    for i in range(len(index_array)):
        subBlock.setDataShort(i, index_array[i])
    block.addBlock(subBlock)

    return block


def get_nx3_new_mesh(tmlFile, rootBlock, mesh_object, materials_info):
    fieldInfo = tmlFile.getTemplateByGuid(nx3_new_mesh_guid.bytes_le)
    block = BtrfBlock()
    block.create(fieldInfo, rootBlock)

    # Blender 4.x: to_mesh() no longer takes scene/apply_modifiers args the old way.
    # Use evaluated object instead.
    depsgraph = bpy.context.evaluated_depsgraph_get()
    eval_object = mesh_object.evaluated_get(depsgraph)
    mesh_data = eval_object.to_mesh()

    has_uv = len(mesh_data.uv_layers) > 0
    has_material = (
        mesh_object.name in materials_info
        and len(materials_info[mesh_object.name]) > 0
        and has_uv
    )

    mesh_name = mesh_object.name

    if has_material:
        material_id = materials_info[mesh_object.name][0].material_id
        channel_id = 0
    else:
        material_id = -1
        channel_id = 0

    if has_material:
        mesh_blocks_faces = [[] for _ in range(len(materials_info[mesh_object.name]))]
        for poly in mesh_data.polygons:
            if poly.material_index < len(mesh_blocks_faces):
                mesh_blocks_faces[poly.material_index].append(poly)
        mesh_block_array = [
            get_nx3_mesh_block(tmlFile, rootBlock, mesh_object, mesh_data, faces, tex_idx)
            for tex_idx, faces in enumerate(mesh_blocks_faces)
        ]
    else:
        mesh_block_array = [
            get_nx3_mesh_block(tmlFile, rootBlock, mesh_object, mesh_data, list(mesh_data.polygons), None)
        ]

    ani_time_array = []
    ani_matrix_array = []
    visi_time_array = []
    visi_value_array = []

    subBlock = BtrfBlock()
    subBlock.create(fieldInfo.getField(0), rootBlock)
    subBlock.setDataString(0, mesh_name)
    block.addBlock(subBlock)

    subBlock.create(fieldInfo.getField(1), rootBlock)
    subBlock.setDataInt(0, material_id)
    block.addBlock(subBlock)

    subBlock.create(fieldInfo.getField(2), rootBlock)
    subBlock.setDataInt(0, channel_id)
    block.addBlock(subBlock)

    subBlock.create(fieldInfo.getField(3), rootBlock)
    for mb in mesh_block_array:
        subBlock.addBlock(mb)
    block.addBlock(subBlock)

    subBlock.create(fieldInfo.getField(4), rootBlock)
    subBlock.setElementNumber(len(ani_time_array))
    for i in range(len(ani_time_array)):
        subBlock.setDataInt(i, ani_time_array[i])
    block.addBlock(subBlock)

    subBlock.create(fieldInfo.getField(5), rootBlock)
    subBlock.setElementNumber(len(ani_matrix_array))
    for i in range(len(ani_matrix_array)):
        subBlock.setDataFloat(i, ani_matrix_array[i])
    block.addBlock(subBlock)

    subBlock.create(fieldInfo.getField(6), rootBlock)
    subBlock.setElementNumber(len(visi_time_array))
    for i in range(len(visi_time_array)):
        subBlock.setDataInt(i, visi_time_array[i])
    block.addBlock(subBlock)

    subBlock.create(fieldInfo.getField(7), rootBlock)
    subBlock.setElementNumber(len(visi_value_array))
    for i in range(len(visi_value_array)):
        subBlock.setDataFloat(i, visi_value_array[i])
    block.addBlock(subBlock)

    subBlock.create(fieldInfo.getField(8), rootBlock)
    block.addBlock(subBlock)

    subBlock.create(fieldInfo.getField(9), rootBlock)
    block.addBlock(subBlock)

    eval_object.to_mesh_clear()

    return block


def get_nx3_bone_tm(tmlFile, rootBlock, bone_info):
    fieldInfo = tmlFile.getTemplateByGuid(nx3_mesh_tm_guid.bytes_le)
    block = BtrfBlock()
    block.create(fieldInfo, rootBlock)

    subBlock = BtrfBlock()
    subBlock.create(fieldInfo.getField(0), rootBlock)
    subBlock.setDataString(0, bone_info.name)
    block.addBlock(subBlock)

    subBlock.create(fieldInfo.getField(1), rootBlock)
    for i in range(16):
        subBlock.setDataFloat(i, bone_info.global_matrix[i])
    block.addBlock(subBlock)

    return block


def write_nx3_new_mesh_header(tmlFile, rootBlock, bones_info, materials_info):
    fieldInfo = tmlFile.getTemplateByGuid(nx3_new_mesh_header_guid.bytes_le)
    block = BtrfBlock()
    block.create(fieldInfo, rootBlock)

    objects = [obj for obj in bpy.data.objects if obj.type == 'MESH']

    mesh_array = [get_nx3_new_mesh(tmlFile, rootBlock, mesh_object, materials_info)
                  for mesh_object in objects]
    bone_tm_array = [get_nx3_bone_tm(tmlFile, rootBlock, bone_info)
                     for bone_info in list(bones_info.values())]

    subBlock = BtrfBlock()
    subBlock.create(fieldInfo.getField(0), rootBlock)
    for mesh in mesh_array:
        subBlock.addBlock(mesh)
    block.addBlock(subBlock)

    subBlock.create(fieldInfo.getField(1), rootBlock)
    for bone_tm in bone_tm_array:
        subBlock.addBlock(bone_tm)
    block.addBlock(subBlock)

    rootBlock.addBlock(block)


def write(filename):
    (tmlFile, rootBlock) = load_btrfdom()

    (materials_info, bones_info) = get_materials_bones()

    write_version(tmlFile, rootBlock)
    write_mtl_header(tmlFile, rootBlock, materials_info)
    write_nx3_new_mesh_header(tmlFile, rootBlock, bones_info, materials_info)

    info("Writing file %s" % filename)
    writer = BtrfParser()
    writer.create(tmlFile)
    writer.writeFile(filename, rootBlock)
