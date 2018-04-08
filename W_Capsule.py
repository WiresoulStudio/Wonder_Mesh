# __________________________________/
# __Author:_________Vit_Prochazka___/
# __Created:________03.04.2018______/
# __Last_modified:__03.04.2018______/
# __Version:________0.1_____________/
# __________________________________/

"""
This file generates and modifies a capsule-shaped mesh.
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
                    fanClose,
                    bridgeLoops,
                    create_mesh_object as c_mesh
)

WCapsule_Defaults = {
    "radius": 0.5,
    "height": 2.0,
    "seg_perimeter": 24,
    "seg_height": 1,
    "seg_caps": 8,
    "centered": True,
    "smoothed": True
}


# Generating the vertices and polygons
def primitive_Capsule_ME(
        radius = 0.5,
        height = 2.0,
        seg_perimeter = 24,
        seg_height = 1,
        seg_caps = 8,
        centered = True,
        smoothed = True):

    # Prepare empty lists
    verts = []
    edges = []
    faces = []

    loops = []

    # Set minimums
    if seg_perimeter < 3:
        seg_perimeter = 3
    if seg_height < 1:
        seg_height = 1
    if seg_caps < 1:
        seg_caps = 1
    if radius > height / 2:
        radius = height / 2

    # Add top and bottom center vertices
    verts.append(Vector((0, 0, 0)))
    verts.append(Vector((0, 0, height)))

    # Create bootom cap segmentation loops
    if seg_caps > 1:
        angleStep = PI / (2 * seg_caps)
        for i in range(1, seg_caps):
            # find the radius and height
            quat = Quaternion((0, -1, 0), i * angleStep)
            helperVect = quat * Vector((0, 0, -radius))
            segmentRadius = helperVect.x
            segmentHeight = radius + helperVect.z
            # create the ring
            newVerts, loop = circ_V(segmentRadius, seg_perimeter, len(verts))
            move_V(newVerts, Vector((0, 0, segmentHeight)))
            verts.extend(newVerts)
            loops.append(loop)

    # Create the base corner circle
    newVerts, loop = circ_V(radius, seg_perimeter, len(verts))
    move_V(newVerts, Vector((0, 0, radius)))
    verts.extend(newVerts)
    loops.append(loop)

    # Create the side segmentation loops
    if height > 2 * radius:
        if seg_height > 1:
            heightStep = (height - (2 * radius)) / seg_height
            for i in range(1, seg_height):
                newHeight = (i * heightStep) + radius
                newVerts, loop = circ_V(radius, seg_perimeter, len(verts))
                move_V(newVerts, Vector((0, 0, newHeight)))
                verts.extend(newVerts)
                loops.append(loop)

    # Create top corner circle
        newVerts, loop = circ_V(radius, seg_perimeter, len(verts))
        move_V(newVerts, Vector((0, 0, height - radius)))
        verts.extend(newVerts)
        loops.append(loop)

    # Create top cap segmentation loops
    if seg_caps > 1:
        angleStep = PI / (2 * seg_caps)
        for i in range(1, seg_caps):
            # find the radius and height
            quat = Quaternion((0, -1, 0), i * angleStep)
            helperVect = quat * Vector((radius, 0, 0))
            segmentRadius = helperVect.x
            segmentHeight = height - radius + helperVect.z
            # create the ring
            newVerts, loop = circ_V(segmentRadius, seg_perimeter, len(verts))
            move_V(newVerts, Vector((0, 0, segmentHeight)))
            verts.extend(newVerts)
            loops.append(loop)

    # Close caps
    faces.extend(fanClose(loops[0], 0, flipped = True))
    faces.extend(fanClose(loops[-1], 1))

    # Bridge all loops
    for i in range(1, len(loops)):
        faces.extend(bridgeLoops(loops[i - 1], loops[i], True))

    if centered:
        move_V(verts, Vector((0, 0, -height / 2)))

    return verts, edges, faces


# Update functions
def update_WCapsule_GEO(Wdata):
    v, e, f = primitive_Capsule_ME(**Wdata["animArgs"])
    tmpMesh = bpy.data.meshes.new("TemporaryMesh")
    tmpMesh.from_pydata(v, e, f)
    tmpMesh.update()

    bm = bmesh.new()
    bm.from_mesh(tmpMesh)
    for fa in bm.faces:
        fa.smooth = Wdata.smoothed
    bm.to_mesh(Wdata.id_data)
    bm.free()
    bpy.data.meshes.remove(tmpMesh)
    Wdata.id_data.update()


# getters
def getRadius(self):
    return min(self["animArgs"]["radius"], self["animArgs"]["height"] / 2)


def getHeight(self):
    return max(self["animArgs"]["radius"] * 2, self["animArgs"]["height"])


def getSegPerim(self):
    return self["animArgs"]["seg_perimeter"]


def getSegHeight(self):
    return self["animArgs"]["seg_height"]


def getSegCaps(self):
    return self["animArgs"]["seg_caps"]


def getCentered(self):
    return self["animArgs"]["centered"]


def getSmoothed(self):
    return self["animArgs"]["smoothed"]


# Setters _____________________________________________________________________
def setRadius(self, val):
    self["animArgs"]["radius"] = val
    if val > self["animArgs"]["height"] / 2:
        self["animArgs"]["height"] = 2 * val
    update_WCapsule_GEO(self)


def setHeight(self, val):
    self["animArgs"]["height"] = val
    if val < self["animArgs"]["radius"] * 2:
        self["animArgs"]["radius"] = val / 2
    update_WCapsule_GEO(self)


def setSegPerim(self, val):
    self["animArgs"]["seg_perimeter"] = val
    update_WCapsule_GEO(self)


def setSegHeight(self, val):
    self["animArgs"]["seg_height"] = val
    update_WCapsule_GEO(self)


def setSegCaps(self, val):
    self["animArgs"]["seg_caps"] = val
    update_WCapsule_GEO(self)


def setCentered(self, val):
    self["animArgs"]["centered"] = val
    update_WCapsule_GEO(self)


def setSmoothed(self, val):
    self["animArgs"]["smoothed"] = val
    update_WCapsule_GEO(self)


class WCapsuleData(bpy.types.PropertyGroup):

    radius = FloatProperty(
        name = "Radius",
        description = "Radius",
        default = 0.5,
        min = 0.0,
        soft_min = 0.0,
        step = 1,
        unit = "LENGTH",
        set = setRadius,
        get = getRadius
    )

    height = FloatProperty(
        name = "Height",
        description = "Height of the capsule",
        default = 2.0,
        min = 0.0,
        soft_min = 0.0,
        step = 1,
        unit = "LENGTH",
        set = setHeight,
        get = getHeight
    )

    seg_perimeter = IntProperty(
        name = "Perim Segments",
        description = "Subdivision on perimeter",
        default = 24,
        min = 3,
        soft_min = 3,
        step = 1,
        subtype = 'NONE',
        get = getSegPerim,
        set = setSegPerim
    )

    seg_height = IntProperty(
        name = "Height Segments",
        description = "Subdivision of the height",
        default = 1,
        min = 1,
        soft_min = 1,
        step = 1,
        subtype = 'NONE',
        get = getSegHeight,
        set = setSegHeight
    )

    seg_caps = IntProperty(
        name = "Caps Segments",
        description = "Subdivision of the caps",
        default = 6,
        min = 1,
        soft_min = 1,
        step = 1,
        subtype = 'NONE',
        get = getSegCaps,
        set = setSegCaps
    )

    centered = BoolProperty(
        name = "Centered",
        description = "Set origin of the cone",
        default = False,
        get = getCentered,
        set = setCentered
    )

    smoothed = BoolProperty(
        name = "Smooth",
        description = "Set smooth shading",
        default = True,
        get = getSmoothed,
        set = setSmoothed
    )


class Make_WCapsule(bpy.types.Operator):
    """Create primitive WCapsule mesh"""
    bl_idname = "mesh.make_wcapsule"
    bl_label = "WCapsule"
    bl_options = {'UNDO', 'REGISTER'}

    def execute(self, context):
        verts, edges, faces = primitive_Capsule_ME(**WCapsule_Defaults)
        c_mesh(context, verts, edges, faces, "WCapsule")

        context.object.data.WType = 'WCAPSULE'
        context.object.data.WCapsule["animArgs"] = WCapsule_Defaults
        bpy.ops.object.shade_smooth()
        context.object.data.use_auto_smooth = True
        return {'FINISHED'}


# Drawing panels ______________________________________________________________
def drawWCapsulePanel(self, context):
    lOut = self.layout
    WData = context.object.data.WCapsule

    lOut.label("Type: WCapsule", icon="MESH_CAPSULE")

    row = lOut.row()
    col = row.column(align = True)
    col.prop(WData, "radius")
    col.prop(WData, "height")

    col = row.column(align = True)
    col.prop(WData, "seg_perimeter")
    col.prop(WData, "seg_height")
    col.prop(WData, "seg_caps")

    row = lOut.row(align = True)
    row.prop(WData, "centered")
    row.prop(WData, "smoothed")


# Register and unregister _____________________________________________________
def registerWCapsule():
    bpy.utils.register_class(Make_WCapsule)
    bpy.utils.register_class(WCapsuleData)
    bpy.types.Mesh.WCapsule = PointerProperty(type = WCapsuleData)


def unregisterWCapsule():
    bpy.utils.unregister_class(Make_WCapsule)
    bpy.utils.unregister_class(WCapsuleData)
    del bpy.types.Mesh.WCapsule
