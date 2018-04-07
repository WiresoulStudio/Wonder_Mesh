# __________________________________/
# __Author:_________Vit_Prochazka___/
# __Created:________15.12.2015______/
# __Last_modified:__05.04.2018______/
# __Version:________0.3_____________/
# __________________________________/

"""
This file generates and modifies a box-shaped mesh.
"""

import bpy
import bmesh
from bpy.props import (
    FloatProperty,
    IntProperty,
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

WBox_Defaults = {
    "size_x": 2.0,
    "size_y": 2.0,
    "size_z": 2.0,
    "seg_x": 1,
    "seg_y": 1,
    "seg_z": 1,
    "centered": True
}


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

    # bottom grid
    for y in range(seg_y + 1):
        line = []
        for x in range(seg_x + 1):
            line.append(len(verts))
            verts.append(Vector((x * dist_x, y * dist_y, 0.0)))
        bottom_lines.append(line)

    # top grid
    for y in range(seg_y + 1):
        line = []
        for x in range(seg_x + 1):
            line.append(len(verts))
            verts.append(Vector((x * dist_x, y * dist_y, size_z)))
        top_lines.append(line)

    # bottom loop
    loop = []
    for i in range(seg_x + 1):
        loop.append(bottom_lines[0][i])
    for i in range(seg_y - 1):
        loop.append(bottom_lines[i + 1][- 1])
    for i in range(seg_x + 1):
        loop.append(bottom_lines[- 1][-(i + 1)])
    for i in range(seg_y - 1):
        loop.append(bottom_lines[-(i + 2)][0])
    loops.append(loop)

    # z loops
    for z in range(seg_z - 1):
        loop = []
        for i in range(seg_x + 1):
            loop.append(len(verts))
            verts.append(Vector((i * dist_x, 0.0, (z + 1) * dist_z)))
        for i in range(seg_y - 1):
            loop.append(len(verts))
            verts.append(Vector((size_x, (i + 1) * dist_y, (z + 1) * dist_z)))
        for i in range(seg_x + 1):
            loop.append(len(verts))
            verts.append(Vector((
                size_x - (i * dist_x), size_y, (z + 1) * dist_z)))
        for i in range(seg_y - 1):
            loop.append(len(verts))
            verts.append(Vector((
                0.0, size_y - ((i + 1) * dist_y), (z + 1) * dist_z)))
        loops.append(loop)

    # top loop
    loop = []
    for i in range(seg_x + 1):
        loop.append(top_lines[0][i])
    for i in range(seg_y - 1):
        loop.append(top_lines[i + 1][-1])
    for i in range(seg_x + 1):
        loop.append(top_lines[-1][-(i + 1)])
    for i in range(seg_y - 1):
        loop.append(top_lines[-(i + 2)][0])
    loops.append(loop)

    # faces bottom
    for i in range(seg_y):
        faces.extend(bridgeLoops(bottom_lines[i], bottom_lines[i + 1], False))

    # faces top
    for i in range(seg_y):
        faces.extend(bridgeLoops(top_lines[i], top_lines[i + 1], False))

    # faces sides
    for i in range(seg_z):
        faces.extend(bridgeLoops(loops[i], loops[i + 1], True))

    if centered:
        half_x = size_x / 2
        half_y = size_y / 2
        half_z = size_z / 2
        for vertex in verts:
            vertex -= Vector((half_x, half_y, half_z))

    return verts, edges, faces


def UpdateWBox(Wdata):
    verts, edges, faces = primitive_Box(**Wdata["animArgs"])
    tmpMesh = bpy.data.meshes.new("TemporaryMesh")
    tmpMesh.from_pydata(verts, edges, faces)
    tmpMesh.update()

    bm = bmesh.new()
    bm.from_mesh(tmpMesh)
    bm.to_mesh(bpy.data.meshes[Wdata["thisMesh"]])
    bm.free()
    bpy.data.meshes.remove(tmpMesh)
    bpy.data.meshes[Wdata["thisMesh"]].update()


# Getters___________________________________________________________________
def getSizeX(self):
    return self["animArgs"]["size_x"]


def getSizeY(self):
    return self["animArgs"]["size_y"]


def getSizeZ(self):
    return self["animArgs"]["size_z"]


def getSegX(self):
    return self["animArgs"]["seg_x"]


def getSegY(self):
    return self["animArgs"]["seg_y"]


def getSegZ(self):
    return self["animArgs"]["seg_z"]


def getCentered(self):
    return self["animArgs"]["centered"]


# Setters_____________________________________________________________________
def setSizeX(self, val):
    self["animArgs"]["size_x"] = val
    UpdateWBox(self)


def setSizeY(self, val):
    self["animArgs"]["size_y"] = val
    UpdateWBox(self)


def setSizeZ(self, val):
    self["animArgs"]["size_z"] = val
    UpdateWBox(self)


def setSegX(self, val):
    self["animArgs"]["seg_x"] = val
    UpdateWBox(self)


def setSegY(self, val):
    self["animArgs"]["seg_y"] = val
    UpdateWBox(self)


def setSegZ(self, val):
    self["animArgs"]["seg_z"] = val
    UpdateWBox(self)


def setCentered(self, val):
    self["animArgs"]["centered"] = val
    UpdateWBox(self)


class WBoxData(bpy.types.PropertyGroup):
    size_x = FloatProperty(
        name = "X:",
        description = "Size of the WBox",
        default = 2.0,
        min = 0.0,
        soft_min = 0.0,
        step = 1,
        unit='LENGTH',
        set = setSizeX,
        get = getSizeX
    )

    size_y = FloatProperty(
        name = "Y:",
        description = "Size of the WBox",
        default = 2.0,
        min = 0.0,
        soft_min = 0.0,
        step = 1,
        unit='LENGTH',
        set = setSizeY,
        get = getSizeY
    )

    size_z = FloatProperty(
        name = "Z:",
        description = "Size of the WBox",
        default = 2.0,
        min = 0.0,
        soft_min = 0.0,
        step = 1,
        unit='LENGTH',
        set = setSizeZ,
        get = getSizeZ
    )

    seg_x = IntProperty(
        name = "X:",
        description = "Segmentation of the WBox",
        default = 1,
        min = 1,
        soft_min = 1,
        step = 1,
        set = setSegX,
        get = getSegX
    )

    seg_y = IntProperty(
        name = "Y:",
        description = "Segmentation of the WBox",
        default = 1,
        min = 1,
        soft_min = 1,
        step = 1,
        set = setSegY,
        get = getSegY
    )

    seg_z = IntProperty(
        name = "Z:",
        description = "Segmentation of the WBox",
        default = 1,
        min = 1,
        soft_min = 1,
        step = 1,
        set = setSegZ,
        get = getSegZ
    )

    centered = BoolProperty(
        name = "Centered",
        description = "Where is origin of the WBox",
        default = True,
        get = getCentered,
        set = setCentered
    )


class Make_WBox(bpy.types.Operator):
    """Create primitive WBox"""
    bl_idname = "mesh.make_wbox"
    bl_label = "WBox"
    bl_options = {'UNDO', 'REGISTER'}

    def execute(self, context):
        verts, edges, faces = primitive_Box(**WBox_Defaults)
        create_mesh_object(context, verts, edges, faces, "WBox")

        context.object.data.WType = 'WBOX'
        context.object.data.WBox["animArgs"] = WBox_Defaults
        context.object.data.WBox["thisMesh"] = context.object.data.name
        return {'FINISHED'}


def drawWBoxPanel(self, context):
    lay_out = self.layout
    WData = context.object.data.WBox
    lay_out.label("Type: WBox", icon='MESH_CUBE')
    row = lay_out.row()
    col = row.column(align = True)
    col.label("Size:")
    col.prop(WData, "size_x")
    col.prop(WData, "size_y")
    col.prop(WData, "size_z")
    col = row.column(align = True)
    col.label("Segmens:")
    col.prop(WData, "seg_x")
    col.prop(WData, "seg_y")
    col.prop(WData, "seg_z")
    lay_out.prop(WData, "centered")


def registerWBox():
    bpy.utils.register_class(Make_WBox)
    bpy.utils.register_class(WBoxData)
    bpy.types.Mesh.WBox = PointerProperty(type=WBoxData)


def unregisterWBox():
    bpy.utils.unregister_class(Make_WBox)
    bpy.utils.unregister_class(WBoxData)
    del bpy.types.Mesh.WBox
