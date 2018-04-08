# __________________________________/
# __Author:_________Vit_Prochazka___/
# __Created:________15.12.2015______/
# __Last_modified:__05.04.2018______/
# __Version:________0.3_____________/
# __________________________________/

import bpy
import bmesh
from bpy.props import (
    FloatProperty,
    IntProperty,
    BoolProperty,
    PointerProperty
)
from mathutils import Vector
from .gen_func import bridgeLoops, create_mesh_object

WPlane_Defaults = {
    "size_x": 2.0,
    "size_y": 2.0,
    "seg_x": 1,
    "seg_y": 1,
    "centered": True
}


def WPlane_mesh(
        size_x = 2.0,
        size_y = 2.0,
        seg_x = 1,
        seg_y = 1,
        centered = True):

    verts = []
    edges = []
    faces = []

    lines = []

    dist_x = size_x / seg_x
    dist_y = size_y / seg_y

    for i in range(seg_y + 1):
        line = []
        for j in range(seg_x + 1):
            line.append(len(verts))
            verts.append(Vector((j * dist_x, i * dist_y, 0.0)))
        lines.append(line)

    for i in range(len(lines) - 1):
        faces.extend(bridgeLoops(lines[i], lines[i + 1], False))

    if centered:
        half_x = size_x / 2
        half_y = size_y / 2
        for vertex in verts:
            vertex[0] -= half_x
            vertex[1] -= half_y

    return verts, edges, faces


def UpdateWPlane(Wdata):
    verts, edges, faces = WPlane_mesh(**Wdata["animArgs"])
    tmpMesh = bpy.data.meshes.new("TemporaryMesh")
    tmpMesh.from_pydata(verts, edges, faces)
    tmpMesh.update()

    bm = bmesh.new()
    bm.from_mesh(tmpMesh)
    bm.to_mesh(Wdata.id_data)
    bm.free()
    bpy.data.meshes.remove(tmpMesh)
    Wdata.id_data.update()


# Getters______________________________________________________________________
def getX(self):
    return self["animArgs"]["size_x"]


def getY(self):
    return self["animArgs"]["size_y"]


def getSegX(self):
    return self["animArgs"]["seg_x"]


def getSegY(self):
    return self["animArgs"]["seg_y"]


def getCentered(self):
    return self["animArgs"]["centered"]


# Setters______________________________________________________________________
def setX(self, val):
    self["animArgs"]["size_x"] = val
    UpdateWPlane(self)


def setY(self, val):
    self["animArgs"]["size_y"] = val
    UpdateWPlane(self)


def setSegX(self, val):
    self["animArgs"]["seg_x"] = val
    UpdateWPlane(self)


def setSegY(self, val):
    self["animArgs"]["seg_y"] = val
    UpdateWPlane(self)


def setCentered(self, val):
    self["animArgs"]["centered"] = val
    UpdateWPlane(self)


class WPlaneData(bpy.types.PropertyGroup):
    size_x = FloatProperty(
        name = "X:",
        description = "Size of the WPlane",
        default = 2.0,
        min = 0.0,
        soft_min = 0.0,
        step = 1,
        unit='LENGTH',
        set = setX,
        get = getX
    )

    size_y = FloatProperty(
        name = "Y:",
        description = "Size of the WPlane",
        default = 2.0,
        min = 0.0,
        soft_min = 0.0,
        step = 1,
        unit='LENGTH',
        set = setY,
        get = getY
    )

    seg_x = IntProperty(
        name = "X:",
        description = "Segmentation of the WPlane",
        default = 1,
        min = 1,
        soft_min = 1,
        step = 1,
        set = setSegX,
        get = getSegX
    )

    seg_y = IntProperty(
        name = "Y:",
        description = "Segmentation of the WPlane",
        default = 1,
        min = 1,
        soft_min = 1,
        step = 1,
        set = setSegY,
        get = getSegY
    )

    centered = BoolProperty(
        name = "Centered",
        description = "Where is origin of the WPlane",
        default = True,
        get = getCentered,
        set = setCentered
    )


class Make_WPlane(bpy.types.Operator):
    """Create primitive WPlane"""
    bl_idname = "mesh.make_wplane"
    bl_label = "WPlane"
    bl_options = {'UNDO', 'REGISTER'}

    def execute(self, context):
        verts, edges, faces = WPlane_mesh(**WPlane_Defaults)
        create_mesh_object(context, verts, edges, faces, "WPlane")

        context.object.data.WType = 'WPLANE'
        context.object.data.WPlane["animArgs"] = WPlane_Defaults
        return {'FINISHED'}


def drawWPlanePanel(self, context):
    lay_out = self.layout
    WData = context.object.data.WPlane
    lay_out.label("Type: WPlane", icon='MESH_PLANE')
    row = lay_out.row()
    col = row.column(align = True)
    col.label("Size:")
    col.prop(WData, "size_x")
    col.prop(WData, "size_y")
    col = row.column(align = True)
    col.label("Segmens:")
    col.prop(WData, "seg_x")
    col.prop(WData, "seg_y")
    lay_out.prop(WData, "centered")


def registerWPlane():
    bpy.utils.register_class(Make_WPlane)
    bpy.utils.register_class(WPlaneData)
    bpy.types.Mesh.WPlane = PointerProperty(type=WPlaneData)


def unregisterWPlane():
    bpy.utils.unregister_class(Make_WPlane)
    bpy.utils.unregister_class(WPlaneData)
    del bpy.types.Mesh.WPlane
