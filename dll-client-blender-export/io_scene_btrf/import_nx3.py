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

""" NX3 structure:
    template nx3_version_header { dword version; }
    ... (see export_btrf.py for full structure)
"""

import bpy
import bmesh
import uuid
import mathutils
from .btrfdom import BtrfParser, TmlFile
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


def info(msg):
    print('btrfdom: Info: ' + msg)


def warn(msg):
    print('btrfdom: Warning: ' + msg)


def error(msg):
    print('btrfdom: Error: ' + msg)
    raise Exception(msg)


def check_version(rootBlock):
    block = rootBlock.getBlockByGuid(nx3_version_header_guid.bytes_le)

    if block:
        version = block.getBlock(0).getDataInt(0)
    else:
        info('there was no version information in this file')
        version = 0

    if version != 65536:
        warn('The version is not 65536, the model may not be read correctly')


def _create_node_material_with_texture(mat_name, texture_name, image):
    """Create a Blender 4.x node-based material with an image texture."""
    material = bpy.data.materials.new(mat_name)
    material.use_nodes = True

    node_tree = material.node_tree
    nodes = node_tree.nodes
    nodes.clear()

    # Output node
    output_node = nodes.new('ShaderNodeOutputMaterial')
    output_node.location = (400, 0)

    # Principled BSDF
    bsdf_node = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf_node.location = (0, 0)
    node_tree.links.new(bsdf_node.outputs['BSDF'], output_node.inputs['Surface'])

    if image:
        # Image Texture node
        tex_node = nodes.new('ShaderNodeTexImage')
        tex_node.location = (-400, 0)
        tex_node.image = image

        # UV Map node
        uv_node = nodes.new('ShaderNodeUVMap')
        uv_node.location = (-600, 0)

        node_tree.links.new(uv_node.outputs['UV'], tex_node.inputs['Vector'])
        node_tree.links.new(tex_node.outputs['Color'], bsdf_node.inputs['Base Color'])
        node_tree.links.new(tex_node.outputs['Alpha'], bsdf_node.inputs['Alpha'])

        material.blend_method = 'CLIP'

    return material


def read_materials(rootBlock, file_dir):
    nx3_mtl_header_block = rootBlock.getBlockByGuid(nx3_mtl_header_guid.bytes_le)
    mtl_template_array = nx3_mtl_header_block.getBlock(0)
    material_array = [mtl_template_array.getBlock(i)
                      for i in range(mtl_template_array.getElementNumber())]

    materials = {}

    for material_block in material_array:
        sub_mtl_block_template_array = material_block.getBlock(0)
        material_data_array = [sub_mtl_block_template_array.getBlock(i)
                                for i in range(sub_mtl_block_template_array.getElementNumber())]
        for material_data_block in material_data_array:
            mtl_name = material_data_block.getBlock(0).getDataString(0)
            texture_name = material_data_block.getBlock(1).getDataString(0)
            mtl_id = material_data_block.getBlock(2).getDataInt(0)
            channel_id = material_data_block.getBlock(3).getDataInt(0)

            texture_name = os.path.basename(texture_name.replace('\\', '/'))
            texture_file = os.path.join(file_dir, texture_name)

            try:
                image = bpy.data.images.load(texture_file)
            except Exception:
                image = None
                warn("Could not load texture file %s" % texture_file)

            material = _create_node_material_with_texture(mtl_name, texture_name, image)

            if channel_id not in materials:
                materials[channel_id] = {}
            if mtl_id not in materials[channel_id]:
                materials[channel_id][mtl_id] = []

            materials[channel_id][mtl_id].append((material, image))

    return materials


def read_bones_weight(bone_block_template_array, vertices):
    bones_weight = {}
    for i in range(bone_block_template_array.getElementNumber()):
        bone_block = bone_block_template_array.getBlock(i)
        name = bone_block.getBlock(0).getDataString(0)
        weight_array = [bone_block.getBlock(1).getDataFloat(j)
                        for j in range(bone_block.getBlock(1).getElementNumber())]
        offset_array = [bone_block.getBlock(2).getDataFloat(j)
                        for j in range(bone_block.getBlock(2).getElementNumber())]

        if int(len(offset_array) / 3) != int(len(weight_array) / 2):
            warn("Bone %s has a wrong number of offsets or weights, ignoring offsets" % name)
            offset_array = []

        bones_weight[name] = [
            [vertices[int(vertex_index)].index, weight]
            for vertex_index, weight in zip(*[iter(weight_array)] * 2)
        ]

    return bones_weight


def read_mesh_block(mesh_block_template, mesh_object, bm, mtl_textures):
    texture_index = mesh_block_template.getBlock(0).getDataInt(0)
    if mesh_block_template.getBlock(1).getElementNumber() == 0:
        print("Empty mesh block, ignoring")
        return {}

    if mesh_block_template.getBlock(1).getElementNumber() > 1:
        print("Mesh block has multiple mesh frames; using first frame only")

    mesh_data = mesh_block_template.getBlock(1).getBlock(0)
    vertex_array = [mesh_data.getBlock(1).getDataFloat(i)
                    for i in range(mesh_data.getBlock(1).getElementNumber())]
    normal_array = [mesh_data.getBlock(2).getDataFloat(i)
                    for i in range(mesh_data.getBlock(2).getElementNumber())]
    texel_array = [mesh_data.getBlock(3).getDataFloat(i)
                   for i in range(mesh_data.getBlock(3).getElementNumber())]

    bone_block_template_array = mesh_data.getBlock(5)

    tm = [mesh_data.getBlock(6).getDataFloat(i) for i in range(16)]

    matrix = mathutils.Matrix((
        (tm[0], tm[4], tm[8],  tm[12]),
        (tm[1], tm[5], tm[9],  tm[13]),
        (tm[2], tm[6], tm[10], tm[14]),
        (tm[3], tm[7], tm[11], tm[15]),
    ))

    face_array_template = mesh_block_template.getBlock(2)
    face_array_raw = face_array_template.getDataShortPtr()

    vertex_data = [
        (vertex_array[int(i * 3)], vertex_array[int(i * 3 + 1)], vertex_array[int(i * 3 + 2)])
        for i in range(int(mesh_data.getBlock(1).getElementNumber() / 3))
    ]
    normal_data = [
        (-normal_array[int(i * 3)], -normal_array[int(i * 3 + 1)], -normal_array[int(i * 3 + 2)])
        for i in range(int(mesh_data.getBlock(2).getElementNumber() / 3))
    ]
    texel_data = [
        (texel_array[int(i * 2)], 1 - texel_array[int(i * 2 + 1)])
        for i in range(int(mesh_data.getBlock(3).getElementNumber() / 2))
    ]
    face_array = [
        (face_array_raw[int(i * 3 + 2)], face_array_raw[int(i * 3 + 1)], face_array_raw[int(i * 3)])
        for i in range(int(mesh_block_template.getBlock(2).getElementNumber() / 3))
    ]

    has_texture = len(texel_data) > 0 and mtl_textures is not None
    material = None
    material_image = None
    material_id = 0

    if has_texture:
        try:
            material, material_image = mtl_textures[texture_index]
        except Exception:
            warn("Material %d not found for object %s" % (texture_index, mesh_object.name))
            has_texture = False

    if has_texture:
        try:
            material_names = [m.name for m in mesh_object.data.materials]
            material_id = material_names.index(material.name)
        except ValueError:
            mesh_object.data.materials.append(bpy.data.materials[material.name])
            material_id = len(mesh_object.data.materials) - 1

    vertices = []
    for vertex in vertex_data:
        vert = bm.verts.new(vertex)
        vert.normal = normal_data[vert.index]
        vertices.append(vert)

    bm.verts.index_update()

    if has_texture:
        uv_layer = bm.loops.layers.uv.verify()
        # Blender 4.x: bm.faces.layers.tex no longer exists; we use material slots
        # and UV coords only — face image assignment is handled via materials.

    for face_indices in face_array:
        try:
            face = bm.faces.new([vertices[i] for i in face_indices])
        except Exception:
            continue
        if has_texture:
            face.material_index = material_id
            # Assign UV coords (loop order matches face_indices)
            face.loops[0][uv_layer].uv = texel_data[face_indices[1]]
            face.loops[1][uv_layer].uv = texel_data[face_indices[2]]
            face.loops[2][uv_layer].uv = texel_data[face_indices[0]]

    mesh_object.matrix_world = matrix

    return read_bones_weight(bone_block_template_array, vertices)


def read_mesh(mesh_template, materials, armature):
    name = mesh_template.getBlock(0).getDataString(0)
    material_id = mesh_template.getBlock(1).getDataInt(0)
    channel_id = mesh_template.getBlock(2).getDataInt(0)

    try:
        mtl_textures = materials[channel_id][material_id]
    except Exception:
        mtl_textures = None
        if material_id != -1:
            warn("Unable to find material for mesh %s: channel_id %d, mtl_id %d"
                 % (name, channel_id, material_id))

    mesh_block_array = mesh_template.getBlock(3)

    mesh = bpy.data.meshes.new(name)
    mesh_object = bpy.data.objects.new(name, mesh)

    # Blender 4.x: use collection.objects.link instead of scene.objects.link
    bpy.context.collection.objects.link(mesh_object)
    mesh_object.parent = armature

    armature_modifier = mesh_object.modifiers.new(armature.name, 'ARMATURE')
    armature_modifier.object = armature

    bm = bmesh.new()
    bones_weight = []

    mesh_blocks = [mesh_block_array.getBlock(i)
                   for i in range(mesh_block_array.getElementNumber())]
    for mesh_block in mesh_blocks:
        bones_weight.append(read_mesh_block(mesh_block, mesh_object, bm, mtl_textures))

    bm.to_mesh(mesh)
    bm.free()
    del bm

    # Switch to edit mode on the armature to add bones
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='EDIT')

    for bone_weights in bones_weight:
        if not bone_weights:
            continue
        for bone_name, weight_infos in list(bone_weights.items()):
            if bone_name not in list(armature.data.edit_bones.keys()):
                bone = armature.data.edit_bones.new(bone_name)
                bone.head = (0, 0, 0)
                bone.tail = (0, 1, 0)

            if bone_name not in list(mesh_object.vertex_groups.keys()):
                vertex_group = mesh_object.vertex_groups.new(name=bone_name)
            else:
                vertex_group = mesh_object.vertex_groups[bone_name]

            for vertex_index, weight in weight_infos:
                vertex_group.add([vertex_index], weight, 'ADD')

    armature.data.update_tag()
    bpy.ops.object.mode_set(mode='OBJECT')


def read_bones_tm_matrix(bone_tm, armature):
    name = bone_tm.getBlock(0).getDataString(0)

    tm = [bone_tm.getBlock(1).getDataFloat(i) for i in range(16)]

    matrix = mathutils.Matrix((
        (tm[0], tm[4], tm[8],  tm[12]),
        (tm[1], tm[5], tm[9],  tm[13]),
        (tm[2], tm[6], tm[10], tm[14]),
        (tm[3], tm[7], tm[11], tm[15]),
    ))

    rotation = matrix.inverted().to_3x3()
    translation = matrix.inverted().to_translation()

    if name in armature.data.edit_bones:
        armature.data.edit_bones[name].transform(rotation)
        armature.data.edit_bones[name].translate(translation)
    else:
        warn("Bone %s not found in armature %s" % (name, armature.name))


def read_mesh_header(rootBlock, materials, filename):
    nx3_mesh_header_block = rootBlock.getBlockByGuid(nx3_new_mesh_header_guid.bytes_le)
    mesh_template_array = nx3_mesh_header_block.getBlock(0)
    bones_tm_template_array = nx3_mesh_header_block.getBlock(1)

    mesh_array = [mesh_template_array.getBlock(i)
                  for i in range(mesh_template_array.getElementNumber())]

    if mesh_template_array.getElementNumber() == 0:
        print("No mesh in the file!")
        return

    armature_data = bpy.data.armatures.new(filename)
    armature = bpy.data.objects.new(filename, armature_data)

    # Blender 4.x: link to active collection, set active via view_layer
    bpy.context.collection.objects.link(armature)
    bpy.context.view_layer.objects.active = armature

    # Blender 4.x: use .select_set() instead of .select attribute
    armature.select_set(True)

    for mesh in mesh_array:
        read_mesh(mesh, materials, armature)

    bones_tm_array = [bones_tm_template_array.getBlock(i)
                      for i in range(bones_tm_template_array.getElementNumber())]

    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='EDIT')
    for bone_tm in bones_tm_array:
        read_bones_tm_matrix(bone_tm, armature)
    bpy.ops.object.mode_set(mode='OBJECT')


def read(nx3_filename):
    info("Reading file %s" % nx3_filename)

    script_dir = os.path.dirname(os.path.abspath(__file__))

    tmlFile = TmlFile()
    tmlFile.create()
    tmlFile.parseFile(script_dir + "/nx3.tml")
    tmlFile.parseFile(script_dir + "/nobj.tml")

    parser = BtrfParser()
    parser.create(tmlFile)
    rootBlock = parser.readFile(nx3_filename)

    if rootBlock is None:
        error("Could not read nx3 file")
        return

    materials = read_materials(rootBlock, os.path.dirname(nx3_filename))
    read_mesh_header(rootBlock, materials, os.path.basename(nx3_filename))
