#___________________________________/
#___Author:_________Vit_Prochazka___/
#___Created:________16.12.2015______/
#___Last_modified:__13.08.2017______/
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
from mathutils import Quaternion, Vector
from .gen_func import bridgeLoops, create_mesh_object
from math import pi

def primitive_Ring(
    radius_out = 1.0,
    use_inner = True,
    radius_in = 0.0,
    seg_perimeter = 24,
    seg_radius = 1,
    sector_from = 0.0,
    sector_to = 2*pi):

    verts = []
    edges = []
    faces = []

    loops = []

    #make sure of what is bigger
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
        loop_number = seg_radius +1

    seg_number = seg_perimeter
    closed = True
    if sector_to - sector_from < (2 * pi):
        seg_number = seg_perimeter +1
        closed = False

    if use_inner:
        for r in range(loop_number):
            loop = []
            for s in range(seg_number):
                loop.append(len(verts))
                quat = Quaternion((0,0,1), (s * stepAngle) + sector_from)
                verts.append(quat * Vector((radius_out - (r * stepRadius), 0.0, 0.0)))
            loops.append(loop)

        #fill the loops
        for i in range(len(loops) -1):
            faces.extend(bridgeLoops(loops[i], loops[i +1], closed))

        #one point in the middle
        if loop_number == seg_radius:
            verts.append(Vector((0.0, 0.0, 0.0)))
            for s in range(seg_number -1):
                faces.append((loops[-1][s], loops[-1][s+1], len(verts) -1))
            if seg_number == seg_perimeter:
                faces.append((loops[-1][-1], loops[-1][0], len(verts) -1))

    else:
        for s in range(seg_number):
            quat = Quaternion((0,0,1), (s * stepAngle) + sector_from)
            verts.append(quat * Vector((radius_out, 0.0, 0.0)))

        for v in range(len(verts) -1):
            edges.append((v, v+1))
        if closed:
            edges.append((len(verts) -1, 0))

    return verts, edges, faces


class Make_WRing(bpy.types.Operator):
    """Create primitive WRing"""
    bl_idname = "mesh.make_wring"
    bl_label = "WRing"
    bl_options = {'UNDO', 'REGISTER'}

    def execute(self, context):

        verts, edges, faces = primitive_Ring()
        create_mesh_object(context, verts, edges, faces, "WRing")

        context.object.data.WType = 'WRING'
        return {'FINISHED'}

def UpdateWRing(self, context):
    WData = context.object.data.WRing
    verts, edges, faces = primitive_Ring(
        radius_out = WData.rads[0],
        use_inner = WData.inner,
        radius_in = WData.rads[1],
        seg_perimeter = WData.seg[0],
        seg_radius = WData.seg[1],
        sector_from = WData.sec[0],
        sector_to = WData.sec[1]
    )
    tmpMesh = bpy.data.meshes.new("TemporaryMesh")
    tmpMesh.from_pydata(verts, edges, faces)
    tmpMesh.update()

    bm = bmesh.new()
    bm.from_mesh(tmpMesh)
    bm.to_mesh(context.object.data)
    bm.free()
    bpy.data.meshes.remove(tmpMesh)


class WRingData(bpy.types.PropertyGroup):
    rads = FloatVectorProperty(
        name="Radiuses",
        description="Outer and inner radiuses",
        default=(1.0, 0.0),
        min=0.0,
        soft_min=0.0,
        step=1,
        precision=2,
        subtype='NONE',
        unit='LENGTH',
        size=2,
        update=UpdateWRing
    )

    inner = BoolProperty(
        name="Use inner",
        description="use inner radius",
        default=True,
        update=UpdateWRing
    )

    seg = IntVectorProperty(
        name="Segmentation",
        description="Subdivision of the ring",
        default=(24, 1),
        min=1,
        soft_min=1,
        step=1,
        subtype='NONE',
        size=2,
        update=UpdateWRing
        )

    sec = FloatVectorProperty(
        name="Section",
        description="Section of the ring",
        default=(0.0, 2*pi),
        min=0.0,
        max=2*pi,
        soft_min=0.0,
        soft_max=2*pi,
        step=10,
        precision=2,
        subtype='NONE',
        unit='ROTATION',
        size=2,
        update=UpdateWRing
        )

def drawWRingPanel(self, context):
    lay_out = self.layout
    WData = context.object.data.WRing
    lay_out.label("Type: WRing", icon='MESH_CIRCLE')
    row = lay_out.row()
    row.column().prop(WData, "rads")
    row.column().prop(WData, "seg")
    row.column().prop(WData, "sec")
    lay_out.prop(WData, "inner")

def registerWRing():
    bpy.utils.register_class(Make_WRing)
    bpy.utils.register_class(WRingData)
    bpy.types.Mesh.WRing = PointerProperty(type=WRingData)

def unregisterWRing():
    bpy.utils.unregister_class(Make_WRing)
    bpy.utils.unregister_class(WRingData)
    del bpy.types.Mesh.WRing
