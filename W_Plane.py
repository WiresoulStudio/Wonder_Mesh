#___________________________________/
#___Author:_________Vit_Prochazka___/
#___Created:________15.12.2015______/
#___Last_modified:__11.08.2017______/
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
from mathutils import Vector
from .gen_func import bridgeLoops, create_mesh_object

def WPlane_mesh(
    x = 2.0,
    y = 2.0,
    seg_x = 1,
    seg_y = 1,
    centered = True):

    verts = []
    edges = []
    faces = []

    lines = []

    dist_x = x / seg_x
    dist_y = y / seg_y

    for i in range(seg_y +1):
        line = []
        for j in range(seg_x +1):
            line.append(len(verts))
            verts.append(Vector((j*dist_x, i*dist_y, 0.0)))
        lines.append(line)

    for i in range(len(lines) -1):
        faces.extend(bridgeLoops(lines[i], lines[i+1], False))

    if centered:
        half_x = x /2
        half_y = y /2
        for vertex in verts:
            vertex[0] -= half_x
            vertex[1] -= half_y

    return verts, edges, faces


class Make_WPlane(bpy.types.Operator):
    """Create primitive WPlane"""
    bl_idname = "mesh.make_wplane"
    bl_label = "WPlane"
    bl_options = {'UNDO', 'REGISTER'}

    def execute(self, context):
        verts, edges, faces = WPlane_mesh()
        create_mesh_object(context, verts, edges, faces, "WPlane")

        context.object.data.WType = 'WPLANE'
        return {'FINISHED'}

def UpdateWPlane(self, context):
    WData = context.object.data.WPlane
    verts, edges, faces = WPlane_mesh(
        x = WData.size.x,
        y = WData.size.y,
        seg_x = WData.segments[0],
        seg_y = WData.segments[1],
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

class WPlaneData(bpy.types.PropertyGroup):
    size = FloatVectorProperty (
        name="Size",
        description="Size of the WPlane",
        default=(2.0, 2.0),
        min=0.0,
        soft_min=0.0,
        step=1,
        precision=2,
        subtype='XYZ',
        unit='LENGTH',
        size=2,
        update = UpdateWPlane
    )

    segments = IntVectorProperty (
        name="Segments",
        description="Segmentation of the WPlane",
        default=(1, 1),
        min=1,
        soft_min=1,
        step=1,
        subtype='XYZ',
        size=2,
        update = UpdateWPlane
    )

    centered = BoolProperty (
        name="Centered",
        description="Where is origin of the WPlane",
        default=True,
        update = UpdateWPlane
    )

def drawWPlanePanel(self, context):
    lay_out = self.layout
    WData = context.object.data.WPlane
    lay_out.label("Type: WPlane", icon='MESH_PLANE')
    row = lay_out.row()
    row.column().prop(WData, "size")
    row.column().prop(WData, "segments")
    lay_out.prop(WData, "centered")

def registerWPlane():
    bpy.utils.register_class(Make_WPlane)
    bpy.utils.register_class(WPlaneData)
    bpy.types.Mesh.WPlane = PointerProperty(type=WPlaneData)

def unregisterWPlane():
    bpy.utils.unregister_class(Make_WPlane)
    bpy.utils.unregister_class(WPlaneData)
    del bpy.types.Mesh.WPlane
