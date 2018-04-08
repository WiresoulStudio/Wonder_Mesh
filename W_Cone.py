# __________________________________/
# __Author:_________Vit_Prochazka___/
# __Created:________16.12.2015______/
# __Last_modified:__13.08.2017______/
# __Version:________0.2_____________/
# __________________________________/

"""
This file generates and modifies a cone-shaped mesh.
"""

import bpy
import bmesh
from mathutils import Vector
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

WCone_Defaults = {
    "radius_main": 1.0,
    "radius_top": 0.0,
    "height": 2.0,
    "seg_perimeter": 24,
    "seg_height": 1,
    "seg_radius": 1,
    "centered": False,
    "smoothed": True
}


# Generating the vertices and polygons
def primitive_Cone_ME(
        radius_main = 1.0,
        radius_top = 0.0,
        height = 2.0,
        seg_perimeter = 24,
        seg_height = 1,
        seg_radius = 1,
        centered = False,
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
    if seg_radius < 1:
        seg_radius = 1

    # Add top and bottom center vertices
    verts.append(Vector((0, 0, 0)))
    verts.append(Vector((0, 0, height)))

    if radius_top == 0 and radius_main == 0:
        edges.append((0, 1))
        return verts, edges, faces

    # Create base segmentation loops
    if radius_main > 0:
        if seg_radius > 1:
            step = radius_main / seg_radius
            for i in range(1, seg_radius):
                newVerts, loop = circ_V(i * step, seg_perimeter, len(verts))
                verts.extend(newVerts)
                loops.append(loop)

        # Create the base corner circle
        newVerts, loop = circ_V(radius_main, seg_perimeter, len(verts))
        verts.extend(newVerts)
        loops.append(loop)

    # Create the side segmentation loops
    if seg_height > 1:
        heightStep = height / seg_height
        radiusStep = (radius_top - radius_main) / seg_height
        for i in range(1, seg_height):
            newRadius = radius_main + (i * radiusStep)
            newVerts, loop = circ_V(newRadius, seg_perimeter, len(verts))
            move_V(newVerts, Vector((0, 0, heightStep * i)))
            verts.extend(newVerts)
            loops.append(loop)

    # Create top corner circle
    if radius_top > 0:
        newVerts, loop = circ_V(radius_top, seg_perimeter, len(verts))
        move_V(newVerts, Vector((0, 0, height)))
        verts.extend(newVerts)
        loops.append(loop)

        # Create the top segmentation loops
        if seg_radius > 1:
            step = radius_top / seg_radius
            for i in range(1, seg_radius):
                newRadius = radius_top - (i * step)
                newVerts, loop = circ_V(newRadius, seg_perimeter, len(verts))
                move_V(newVerts, Vector((0, 0, height)))
                verts.extend(newVerts)
                loops.append(loop)

    # Close caps
    faces.extend(fanClose(loops[0], 0, closed = True, flipped = True))
    faces.extend(fanClose(loops[-1], 1))

    # Bridge all loops
    for i in range(1, len(loops)):
        faces.extend(bridgeLoops(loops[i - 1], loops[i], True))

    if centered:
        move_V(verts, Vector((0, 0, -height / 2)))

    return verts, edges, faces


# Update functions
def update_WCone_GEO(Wdata):
    v, e, f = primitive_Cone_ME(**Wdata["animArgs"])
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
def getRadTop(self):
    return self["animArgs"]["radius_top"]


def getRadMain(self):
    return self["animArgs"]["radius_main"]


def getHeight(self):
    return self["animArgs"]["height"]


def getSegPerim(self):
    return self["animArgs"]["seg_perimeter"]


def getSegHeight(self):
    return self["animArgs"]["seg_height"]


def getSegRad(self):
    return self["animArgs"]["seg_radius"]


def getCentered(self):
    return self["animArgs"]["centered"]


def getSmoothed(self):
    return self["animArgs"]["smoothed"]


# Setters _____________________________________________________________________
def setRadTop(self, val):
    self["animArgs"]["radius_top"] = val
    update_WCone_GEO(self)


def setRadMain(self, val):
    self["animArgs"]["radius_main"] = val
    update_WCone_GEO(self)


def setHeight(self, val):
    self["animArgs"]["height"] = val
    update_WCone_GEO(self)


def setSegPerim(self, val):
    self["animArgs"]["seg_perimeter"] = val
    update_WCone_GEO(self)


def setSegHeight(self, val):
    self["animArgs"]["seg_height"] = val
    update_WCone_GEO(self)


def setSegRad(self, val):
    self["animArgs"]["seg_radius"] = val
    update_WCone_GEO(self)


def setCentered(self, val):
    self["animArgs"]["centered"] = val
    update_WCone_GEO(self)


def setSmoothed(self, val):
    self["animArgs"]["smoothed"] = val
    update_WCone_GEO(self)


class WConeData(bpy.types.PropertyGroup):

    rad_top = FloatProperty(
        name = "Radius top",
        description = "Top Radius",
        default = 0.0,
        min = 0.0,
        soft_min = 0.0,
        step = 1,
        precision = 2,
        unit = "LENGTH",
        set = setRadTop,
        get = getRadTop
    )

    rad_main = FloatProperty(
        name = "Radius bottom",
        description = "Bottom Radius",
        default = 1.0,
        min = 0.0,
        soft_min = 0.0,
        step = 1,
        precision = 2,
        unit = "LENGTH",
        set = setRadMain,
        get = getRadMain
    )

    height = FloatProperty(
        name = "Height",
        description = "Height of the cone",
        default = 2.0,
        min = 0.0,
        soft_min = 0.0,
        step = 1,
        precision = 2,
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

    seg_radius = IntProperty(
        name = "Radius Segments",
        description = "Subdivision of the radius",
        default = 1,
        min = 1,
        soft_min = 1,
        step = 1,
        subtype = 'NONE',
        get = getSegRad,
        set = setSegRad
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


class Make_WCone(bpy.types.Operator):
    """Create primitive WCone mesh"""
    bl_idname = "mesh.make_wcone"
    bl_label = "WCone"
    bl_options = {'UNDO', 'REGISTER'}

    def execute(self, context):
        verts, edges, faces = primitive_Cone_ME(**WCone_Defaults)
        c_mesh(context, verts, edges, faces, "WCone")

        context.object.data.WType = 'WCONE'
        context.object.data.WCone["animArgs"] = WCone_Defaults
        bpy.ops.object.shade_smooth()
        context.object.data.use_auto_smooth = True
        return {'FINISHED'}


# Drawing panels ______________________________________________________________
def drawWConePanel(self, context):
    lOut = self.layout
    WData = context.object.data.WCone

    lOut.label("Type: WCone", icon="MESH_CONE")

    row = lOut.row()
    col = row.column(align = True)
    col.prop(WData, "rad_top")
    col.prop(WData, "rad_main")
    col.prop(WData, "height")

    col = row.column(align = True)
    col.prop(WData, "seg_perimeter")
    col.prop(WData, "seg_height")
    col.prop(WData, "seg_radius")

    row = lOut.row()
    row.prop(WData, "centered")
    row.prop(WData, "smoothed")


# Register and unregister _____________________________________________________
def registerWCone():
    bpy.utils.register_class(Make_WCone)
    bpy.utils.register_class(WConeData)
    bpy.types.Mesh.WCone = PointerProperty(type = WConeData)


def unregisterWCone():
    bpy.utils.unregister_class(Make_WCone)
    bpy.utils.unregister_class(WConeData)
    del bpy.types.Mesh.WCone
