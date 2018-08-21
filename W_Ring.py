# __________________________________/
# __Author:_________Vit_Prochazka___/
# __Created:________16.12.2015______/
# __Last_modified:__21.08.2018______/
# __Version:________0.3_____________/
# __________________________________/

"""
This file generates and modifies a ring-shaped mesh.
"""

import bpy
import bmesh
from bpy.props import (
                FloatProperty,
                IntProperty,
                BoolProperty,
                PointerProperty
)
from mathutils import Quaternion, Vector
from .gen_func import bridgeLoops, create_mesh_object
from math import pi

WRing_Defaults = {
    "radius_out": 1.0,
    "use_inner": True,
    "radius_in": 0.0,
    "seg_perimeter": 24,
    "seg_radius": 1,
    "sector_from": 0.0,
    "sector_to": 2 * pi
}


def primitive_Ring(
                radius_out = 1.0,
                use_inner = True,
                radius_in = 0.0,
                seg_perimeter = 24,
                seg_radius = 1,
                sector_from = 0.0,
                sector_to = 2 * pi):

    verts = []
    edges = []
    faces = []

    loops = []

    # make sure of what is bigger
    if radius_out < radius_in:
        radius_in, radius_out = radius_out, radius_in

    if sector_from > sector_to:
        sector_to, sector_from = sector_from, sector_to

    if (radius_out - radius_in) < 0.0001:
        use_inner = False

    if seg_perimeter < 3:
        seg_perimeter = 3

    stepAngle = (sector_to - sector_from) / seg_perimeter
    stepRadius = (radius_out - radius_in) / seg_radius

    loop_number = seg_radius
    if radius_in > 0.0001:
        loop_number = seg_radius + 1

    seg_number = seg_perimeter
    closed = True
    if sector_to - sector_from < (2 * pi):
        seg_number = seg_perimeter + 1
        closed = False

    if use_inner:
        for r in range(loop_number):
            loop = []
            for s in range(seg_number):
                loop.append(len(verts))
                quat = Quaternion((0, 0, 1), (s * stepAngle) + sector_from)
                verts.append(quat * Vector((
                    radius_out - (r * stepRadius), 0.0, 0.0)))
            loops.append(loop)

        # fill the loops
        for i in range(len(loops) - 1):
            faces.extend(bridgeLoops(loops[i], loops[i + 1], closed))

        # one point in the middle
        if loop_number == seg_radius:
            verts.append(Vector((0.0, 0.0, 0.0)))
            for s in range(seg_number - 1):
                faces.append((loops[-1][s], loops[-1][s+1], len(verts) - 1))
            if seg_number == seg_perimeter:
                faces.append((loops[-1][-1], loops[-1][0], len(verts) - 1))

    else:
        for s in range(seg_number):
            quat = Quaternion((0, 0, 1), (s * stepAngle) + sector_from)
            verts.append(quat * Vector((radius_out, 0.0, 0.0)))

        for v in range(len(verts) - 1):
            edges.append((v, v + 1))
        if closed:
            edges.append((len(verts) - 1, 0))

    return verts, edges, faces


def UpdateWRing(WData):
    verts, edges, faces = primitive_Ring(**WData["animArgs"])
    tmpMesh = bpy.data.meshes.new("TemporaryMesh")
    tmpMesh.from_pydata(verts, edges, faces)
    tmpMesh.update()

    bm = bmesh.new()
    bm.from_mesh(tmpMesh)
    bm.to_mesh(WData.id_data)
    bm.free()
    bpy.data.meshes.remove(tmpMesh)
    WData.id_data.update()


# Getters______________________________________________________________________
def getRadius_out(self):
    return self["animArgs"]["radius_out"]


def getUse_inner(self):
    return self["animArgs"]["use_inner"]


def getRadius_in(self):
    return self["animArgs"]["radius_in"]


def getSeg_perimeter(self):
    return self["animArgs"]["seg_perimeter"]


def getSeg_radius(self):
    return self["animArgs"]["seg_radius"]


def getSector_from(self):
    return self["animArgs"]["sector_from"]


def getSector_to(self):
    return self["animArgs"]["sector_to"]


# Setters______________________________________________________________________
def setRadius_out(self, val):
    self["animArgs"]["radius_out"] = val
    UpdateWRing(self)


def setUse_inner(self, val):
    self["animArgs"]["use_inner"] = val
    UpdateWRing(self)


def setRadius_in(self, val):
    self["animArgs"]["radius_in"] = val
    UpdateWRing(self)


def setSeg_perimeter(self, val):
    self["animArgs"]["seg_perimeter"] = val
    UpdateWRing(self)


def setSeg_radius(self, val):
    self["animArgs"]["seg_radius"] = val
    UpdateWRing(self)


def setSector_from(self, val):
    self["animArgs"]["sector_from"] = val
    UpdateWRing(self)


def setSector_to(self, val):
    self["animArgs"]["sector_to"] = val
    UpdateWRing(self)


class WRingData(bpy.types.PropertyGroup):
    radius_out = FloatProperty(
        name="Outer",
        description="Outer radius",
        default=1.0,
        min=0.0,
        soft_min=0.0,
        step=1,
        unit='LENGTH',
        set = setRadius_out,
        get = getRadius_out
    )

    use_inner = BoolProperty(
        name="Use inner",
        description="use inner radius",
        default=True,
        set = setUse_inner,
        get = getUse_inner
    )

    radius_in = FloatProperty(
        name="Inner",
        description="Inner radius",
        default=0.0,
        min=0.0,
        soft_min=0.0,
        step=1,
        unit='LENGTH',
        set = setRadius_in,
        get = getRadius_in
    )

    seg_perimeter = IntProperty(
        name="Perimeter",
        description="Subdivision of the perimeter",
        default=24,
        min=3,
        soft_min=3,
        step=1,
        set = setSeg_perimeter,
        get = getSeg_perimeter
        )

    seg_radius = IntProperty(
        name="Radius",
        description="Subdivision of the radius",
        default=1,
        min=1,
        soft_min=1,
        step=1,
        set = setSeg_radius,
        get = getSeg_radius
        )

    sector_from = FloatProperty(
        name="From",
        description="Setor from",
        default=0.0,
        min=0.0,
        soft_min=0.0,
        max = 2 * pi,
        soft_max = 2 * pi,
        step=10,
        unit='ROTATION',
        set = setSector_from,
        get = getSector_from
    )

    sector_to = FloatProperty(
        name="From",
        description="Setor from",
        default=2 * pi,
        min=0.0,
        soft_min=0.0,
        max = 2 * pi,
        soft_max = 2 * pi,
        step=10,
        unit='ROTATION',
        set = setSector_to,
        get = getSector_to
    )


class Make_WRing(bpy.types.Operator):
    """Create primitive WRing"""
    bl_idname = "mesh.make_wring"
    bl_label = "WRing"
    bl_options = {'UNDO', 'REGISTER'}

    radius_out = FloatProperty(
        name="Outer",
        description="Outer radius",
        default=1.0,
        min=0.0,
        soft_min=0.0,
        step=1,
        unit='LENGTH'
    )

    use_inner = BoolProperty(
        name="Use inner",
        description="use inner radius",
        default=True
    )

    radius_in = FloatProperty(
        name="Inner",
        description="Inner radius",
        default=0.0,
        min=0.0,
        soft_min=0.0,
        step=1,
        unit='LENGTH'
    )

    seg_perimeter = IntProperty(
        name="Perimeter",
        description="Subdivision of the perimeter",
        default=24,
        min=3,
        soft_min=3,
        step=1
        )

    seg_radius = IntProperty(
        name="Radius",
        description="Subdivision of the radius",
        default=1,
        min=1,
        soft_min=1,
        step=1
        )

    sector_from = FloatProperty(
        name="From",
        description="Setor from",
        default=0.0,
        min=0.0,
        soft_min=0.0,
        max = 2 * pi,
        soft_max = 2 * pi,
        step=10,
        unit='ROTATION'
    )

    sector_to = FloatProperty(
        name="From",
        description="Setor from",
        default=2 * pi,
        min=0.0,
        soft_min=0.0,
        max = 2 * pi,
        soft_max = 2 * pi,
        step=10,
        unit='ROTATION'
    )

    def execute(self, context):

        """
        WRing_Defaults
        "radius_out": 1.0,
        "use_inner": True,
        "radius_in": 0.0,
        "seg_perimeter": 24,
        "seg_radius": 1,
        "sector_from": 0.0,
        "sector_to": 2 * pi
        """

        WRing_Defaults["radius_out"] = self.radius_out
        WRing_Defaults["use_inner"] = self.use_inner
        WRing_Defaults["radius_in"] = self.radius_in
        WRing_Defaults["seg_perimeter"] = self.seg_perimeter
        WRing_Defaults["seg_radius"] = self.seg_radius
        WRing_Defaults["sector_from"] = self.sector_from
        WRing_Defaults["sector_to"] = self.sector_to

        verts, edges, faces = primitive_Ring(**WRing_Defaults)
        create_mesh_object(context, verts, edges, faces, "WRing")

        context.object.data.WType = 'WRING'
        context.object.data.WRing["animArgs"] = WRing_Defaults

        return {'FINISHED'}


def drawWRingPanel(self, context):
    lay_out = self.layout
    WData = context.object.data.WRing
    lay_out.label("Type: WRing", icon='MESH_CIRCLE')
    row = lay_out.row()

    col = row.column(align = True)
    col.label("Radiuses:")
    col.prop(WData, "radius_out")
    col.prop(WData, "radius_in")

    col = row.column(align = True)
    col.label("Segmentation:")
    col.prop(WData, "seg_perimeter")
    col.prop(WData, "seg_radius")

    col = row.column(align = True)
    col.label("Section:")
    col.prop(WData, "sector_from")
    col.prop(WData, "sector_to")

    lay_out.prop(WData, "use_inner")


def registerWRing():
    bpy.utils.register_class(Make_WRing)
    bpy.utils.register_class(WRingData)
    bpy.types.Mesh.WRing = PointerProperty(type=WRingData)


def unregisterWRing():
    bpy.utils.unregister_class(Make_WRing)
    bpy.utils.unregister_class(WRingData)
    del bpy.types.Mesh.WRing
