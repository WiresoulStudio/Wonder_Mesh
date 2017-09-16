#___________________________________/
#___Author:_________Vit_Prochazka___/
#___Created:________15.12.2015______/
#___Last_modified:__12.08.2017______/
#___Version:________0.2_____________/
#___________________________________/

import bpy
import bmesh
from bpy.props import (
    FloatVectorProperty,
    IntVectorProperty,
    BoolProperty,
    PointerProperty
)
from mathutils import (
    Vector
)
from .gen_func import (
    bridgeLoops,
    create_mesh_object
)

def primitive_Box(
    size_x = 2.0,
    size_y = 2.0,
    size_z = 2.0,
    seg_x = 1,
    seg_y = 1,
    seg_z = 1,
    centered = True):

    verts = []
    edges = []
    faces = []

    bottom_lines = []
    top_lines = []
    loops = []

    dist_x = size_x / seg_x
    dist_y = size_y / seg_y
    dist_z = size_z / seg_z

    #bottom grid
    for y in range(seg_y +1):
        line = []
        for x in range(seg_x +1):
            line.append(len(verts))
            verts.append(Vector((x * dist_x, y * dist_y, 0.0)))
        bottom_lines.append(line)

    #top grid
    for y in range(seg_y +1):
        line = []
        for x in range(seg_x +1):
            line.append(len(verts))
            verts.append(Vector((x * dist_x, y * dist_y, size_z)))
        top_lines.append(line)

    #bottom loop
    loop = []
    for i in range(seg_x +1):
        loop.append(bottom_lines[0][i])
    for i in range(seg_y -1):
        loop.append(bottom_lines[i+1][-1])
    for i in range(seg_x +1):
        loop.append(bottom_lines[-1][-(i+1)])
    for i in range(seg_y -1):
        loop.append(bottom_lines[-(i+2)][0])
    loops.append(loop)

    #z loops
    for z in range(seg_z -1):
        loop = []
        for i in range(seg_x +1):
            loop.append(len(verts))
            verts.append(Vector((i * dist_x, 0.0, (z +1) * dist_z)))
        for i in range(seg_y -1):
            loop.append(len(verts))
            verts.append(Vector((size_x, (i +1) * dist_y, (z +1) * dist_z)))
        for i in range(seg_x +1):
            loop.append(len(verts))
            verts.append(Vector((size_x - (i * dist_x), size_y, (z +1) * dist_z)))
        for i in range(seg_y -1):
            loop.append(len(verts))
            verts.append(Vector((0.0, size_y - ((i +1) * dist_y), (z +1) * dist_z)))
        loops.append(loop)

    #top loop
    loop = []
    for i in range(seg_x +1):
        loop.append(top_lines[0][i])
    for i in range(seg_y -1):
        loop.append(top_lines[i+1][-1])
    for i in range(seg_x +1):
        loop.append(top_lines[-1][-(i+1)])
    for i in range(seg_y -1):
        loop.append(top_lines[-(i+2)][0])
    loops.append(loop)

    #faces bottom
    for i in range(seg_y):
        faces.extend(bridgeLoops(bottom_lines[i], bottom_lines[i +1], False))

    #faces top
    for i in range(seg_y):
        faces.extend(bridgeLoops(top_lines[i], top_lines[i +1], False))

    #faces sides
    for i in range(seg_z):
        faces.extend(bridgeLoops(loops[i], loops[i+1], True))

    if centered:
        half_x = size_x /2
        half_y = size_y /2
        half_z = size_z /2
        for vertex in verts:
            vertex -= Vector((half_x, half_y, half_z))

    return verts, edges, faces

class Make_WBox(bpy.types.Operator):
    """Create primitive WBox"""
    bl_idname = "mesh.make_wbox"
    bl_label = "WBox"
    bl_options = {'UNDO', 'REGISTER'}

    def execute(self, context):
        verts, edges, faces = primitive_Box()
        create_mesh_object(context, verts, edges, faces, "WBox")

        context.object.data.WType = 'WBOX'
        return {'FINISHED'}

def UpdateWBox(self, context):
    WData = context.object.data.WBox
    verts, edges, faces = primitive_Box(
        size_x = WData.size.x,
        size_y = WData.size.y,
        size_z = WData.size.z,
        seg_x = WData.segments[0],
        seg_y = WData.segments[1],
        seg_z = WData.segments[2],
        centered = WData.centered
    )
    tmpMesh = bpy.data.meshes.new("TemporaryMesh")
    tmpMesh.from_pydata(verts, edges, faces)
    tmpMesh.update()

    bm = bmesh.new()
    bm.from_mesh(tmpMesh)
    bm.to_mesh(context.object.data)
    bm.free()
    bpy.data.meshes.remove(tmpMesh)

class WBoxData(bpy.types.PropertyGroup):
    size = FloatVectorProperty (
        name="Size",
        description="Size of the WBox",
        default=(2.0, 2.0, 2.0),
        min=0.0,
        soft_min=0.0,
        step=1,
        precision=2,
        subtype='XYZ',
        unit='LENGTH',
        size=3,
        update = UpdateWBox
    )

    segments = IntVectorProperty (
        name="Segments",
        description="Segmentation of the WBox",
        default=(1, 1, 1),
        min=1,
        soft_min=1,
        step=1,
        subtype='XYZ',
        size=3,
        update = UpdateWBox
    )

    centered = BoolProperty (
        name="Centered",
        description="Where is origin of the WBox",
        default=True,
        update = UpdateWBox
    )

def drawWBoxPanel(self, context):
    lay_out = self.layout
    WData = context.object.data.WBox
    lay_out.label("Type: WBox", icon='MESH_CUBE')
    row = lay_out.row()
    row.column().prop(WData, "size")
    row.column().prop(WData, "segments")
    lay_out.prop(WData, "centered")

def registerWBox():
    bpy.utils.register_class(Make_WBox)
    bpy.utils.register_class(WBoxData)
    bpy.types.Mesh.WBox = PointerProperty(type=WBoxData)

def unregisterWBox():
    bpy.utils.unregister_class(Make_WBox)
    bpy.utils.unregister_class(WBoxData)
    del bpy.types.Mesh.WBox
