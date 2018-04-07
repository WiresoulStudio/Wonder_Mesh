# __________________________________/
# __Author:_________Vit_Prochazka___/
# __Created:________03.04.2018______/
# __Last_modified:__03.04.2018______/
# __Version:________0.1_____________/
# __________________________________/

"""
This file generates and modifies a torus-shaped mesh.
"""

import bpy
import bmesh
from mathutils import (
                    Vector,
                    Quaternion
)
from math import pi as PI
from bpy.props import (
                    BoolProperty,
                    IntProperty,
                    FloatProperty,
                    PointerProperty
)
from .gen_func import (
                    circleVerts as circ_V,
                    moveVerts as move_V,
                    rotateVerts as rot_V,
                    fanClose,
                    bridgeLoops,
                    create_mesh_object as c_mesh
)

WTorus_Defaults = {
    "radius_main": 2.0,
    "radius_minor": 0.5,
    "seg_main": 24,
    "seg_minor": 12,
    "sec_from": 0.0,
    "sec_to": 2 * PI,
    "smoothed": True
}


# Generating the vertices and polygons
def primitive_Torus_ME(
        radius_main = 2.0,
        radius_minor = 0.5,
        seg_main = 24,
        seg_minor = 12,
        sec_from = 0.0,
        sec_to = 2 * PI,
        smoothed = True):

    # Prepare empty lists
    verts = []
    edges = []
    faces = []

    loops = []

    # Set minimums
    if seg_main < 3:
        seg_main = 3
    if seg_minor < 3:
        seg_minor = 3
    if sec_from > sec_to:
        sec_from, sec_to = sec_to, sec_from

    # Create the loops
    seg_angle = (sec_to - sec_from) / seg_main
    quatRight = Quaternion((-1, 0, 0), PI / 2)
    vecOffset = Vector((radius_main, 0, 0))
    for i in range(seg_main):
        quat = Quaternion((0, 0, 1), (i * seg_angle) + sec_from)
        newVerts, loop = circ_V(radius_minor, seg_minor, len(verts))
        rot_V(newVerts, quatRight)
        move_V(newVerts, vecOffset)
        rot_V(newVerts, quat)
        verts.extend(newVerts)
        loops.append(loop)

    # Close the shape
    if sec_to - sec_from < 2 * PI:
        quat = Quaternion((0, 0, 1), sec_to)
        newVerts, loop = circ_V(radius_minor, seg_minor, len(verts))
        rot_V(newVerts, quatRight)
        move_V(newVerts, vecOffset)
        rot_V(newVerts, quat)
        verts.extend(newVerts)
        loops.append(loop)

        verts.append(quat * vecOffset)
        quat = Quaternion((0, 0, 1), sec_from)
        verts.append(quat * vecOffset)

        # Close caps
        faces.extend(fanClose(loops[0], len(verts) - 1, flipped = True))
        faces.extend(fanClose(loops[-1], len(verts) - 2))
    else:
        faces.extend(bridgeLoops(loops[-1], loops[0], True))

    # Bridge all loops
    for i in range(1, len(loops)):
        faces.extend(bridgeLoops(loops[i - 1], loops[i], True))

    return verts, edges, faces


# Update functions
def update_WTorus_GEO(Wdata):
    v, e, f = primitive_Torus_ME(**Wdata["animArgs"])
    tmpMesh = bpy.data.meshes.new("TemporaryMesh")
    tmpMesh.from_pydata(v, e, f)
    tmpMesh.update()

    bm = bmesh.new()
    bm.from_mesh(tmpMesh)
    for fa in bm.faces:
        fa.smooth = Wdata.smoothed
    bm.to_mesh(bpy.data.meshes[Wdata["thisMesh"]])
    bm.free()
    bpy.data.meshes.remove(tmpMesh)
    bpy.data.meshes[Wdata["thisMesh"]].update()


# getters
def getRadMain(self):
    return self["animArgs"]["radius_main"]


def getRadMin(self):
    return self["animArgs"]["radius_minor"]


def getRadIn(self):
    a = self["animArgs"]
    return a["radius_main"] - a["radius_minor"]


def getRadOut(self):
    a = self["animArgs"]
    return a["radius_main"] + a["radius_minor"]


def getSegMain(self):
    return self["animArgs"]["seg_main"]


def getSegMin(self):
    return self["animArgs"]["seg_minor"]


def getSecFrom(self):
    return self["animArgs"]["sec_from"]


def getSecTo(self):
    return self["animArgs"]["sec_to"]


def getSmoothed(self):
    return self["animArgs"]["smoothed"]


# Setters _____________________________________________________________________
def setRadMain(self, val):
    self["animArgs"]["radius_main"] = val
    if val < self["animArgs"]["radius_minor"]:
        self["animArgs"]["radius_minor"] = val
    update_WTorus_GEO(self)


def setRadMin(self, val):
    self["animArgs"]["radius_minor"] = val
    if val > self["animArgs"]["radius_main"]:
        self["animArgs"]["radius_main"] = val
    update_WTorus_GEO(self)


def setRadIn(self, val):
    self["animArgs"]["radius_main"] = (val + self.radius_out) / 2
    self["animArgs"]["radius_minor"] = self["animArgs"]["radius_main"] - val
    update_WTorus_GEO(self)


def setRadOut(self, val):
    self["animArgs"]["radius_main"] = (self.radius_in + val) / 2
    self["animArgs"]["radius_minor"] = val - self["animArgs"]["radius_main"]
    update_WTorus_GEO(self)


def setSegMain(self, val):
    self["animArgs"]["seg_main"] = val
    update_WTorus_GEO(self)


def setSegMin(self, val):
    self["animArgs"]["seg_minor"] = val
    update_WTorus_GEO(self)


def setSecFrom(self, val):
    self["animArgs"]["sec_from"] = val
    update_WTorus_GEO(self)


def setSecTo(self, val):
    self["animArgs"]["sec_to"] = val
    update_WTorus_GEO(self)


def setSmoothed(self, val):
    self["animArgs"]["smoothed"] = val
    update_WTorus_GEO(self)


class WTorusData(bpy.types.PropertyGroup):

    radius_main = FloatProperty(
        name = "Major",
        description = "Main Radius",
        default = 1.0,
        min = 0.0,
        soft_min = 0.0,
        step = 1,
        unit = "LENGTH",
        set = setRadMain,
        get = getRadMain
    )

    radius_minor = FloatProperty(
        name = "Minor",
        description = "Minor Radius",
        default = 0.5,
        min = 0.0,
        soft_min = 0.0,
        step = 1,
        unit = "LENGTH",
        set = setRadMin,
        get = getRadMin
    )

    radius_in = FloatProperty(
        name = "Inner",
        description = "Inner Radius",
        default = 0.5,
        min = 0.0,
        soft_min = 0.0,
        step = 1,
        unit = "LENGTH",
        set = setRadIn,
        get = getRadIn
    )

    radius_out = FloatProperty(
        name = "Outer",
        description = "Outer Radius",
        default = 1.5,
        min = 0.0,
        soft_min = 0.0,
        step = 1,
        unit = "LENGTH",
        set = setRadOut,
        get = getRadOut
    )

    seg_main = IntProperty(
        name = "Main",
        description = "Segmentation on main perimeter",
        default = 24,
        min = 3,
        soft_min = 3,
        step = 1,
        subtype = 'NONE',
        get = getSegMain,
        set = setSegMain
    )

    seg_minor = IntProperty(
        name = "Minor",
        description = "Segmentation of the minor perimeter",
        default = 12,
        min = 3,
        soft_min = 3,
        step = 1,
        subtype = 'NONE',
        get = getSegMin,
        set = setSegMin
    )

    sec_from = FloatProperty(
        name = "From",
        description = "Start angle of the section",
        default = 0.0,
        min = 0.0,
        max = 2 * PI,
        soft_min = 0.0,
        soft_max = 2 * PI,
        step = 10,
        unit = "ROTATION",
        set = setSecFrom,
        get = getSecFrom
    )

    sec_to = FloatProperty(
        name = "To",
        description = "End angle of the section",
        default = 2 * PI,
        min = 0.0,
        max = 2 * PI,
        soft_min = 0.0,
        soft_max = 2 * PI,
        step = 10,
        unit = "ROTATION",
        set = setSecTo,
        get = getSecTo
    )

    smoothed = BoolProperty(
        name = "Smooth",
        description = "Set smooth shading",
        default = True,
        get = getSmoothed,
        set = setSmoothed
    )


class Make_WTorus(bpy.types.Operator):
    """Create primitive WTorus mesh"""
    bl_idname = "mesh.make_wtorus"
    bl_label = "WTorus"
    bl_options = {'UNDO', 'REGISTER'}

    def execute(self, context):
        verts, edges, faces = primitive_Torus_ME(**WTorus_Defaults)
        c_mesh(context, verts, edges, faces, "WTorus")

        context.object.data.WType = 'WTORUS'
        context.object.data.WTorus["animArgs"] = WTorus_Defaults
        context.object.data.WTorus["thisMesh"] = context.object.data.name
        bpy.ops.object.shade_smooth()
        context.object.data.use_auto_smooth = True
        context.object.data.auto_smooth_angle = PI / 3
        return {'FINISHED'}


# Drawing panels ______________________________________________________________
def drawWTorusPanel(self, context):
    lOut = self.layout
    WData = context.object.data.WTorus

    lOut.label("Type: WTorus", icon="MESH_TORUS")

    row = lOut.row()
    col = row.column(align = True)
    col.label("Radiuses")
    col.prop(WData, "radius_main")
    col.prop(WData, "radius_minor")
    col.separator()
    col.prop(WData, "radius_in")
    col.prop(WData, "radius_out")

    col = row.column(align = True)
    col.label("Segments")
    col.prop(WData, "seg_main")
    col.prop(WData, "seg_minor")
    col.label("Section")
    col.prop(WData, "sec_from")
    col.prop(WData, "sec_to")

    row = lOut.row()
    row.prop(WData, "smoothed")


# Register and unregister _____________________________________________________
def registerWTorus():
    bpy.utils.register_class(Make_WTorus)
    bpy.utils.register_class(WTorusData)
    bpy.types.Mesh.WTorus = PointerProperty(type = WTorusData)


def unregisterWTorus():
    bpy.utils.unregister_class(Make_WTorus)
    bpy.utils.unregister_class(WTorusData)
    del bpy.types.Mesh.WTorus
