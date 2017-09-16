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
    FloatProperty,
    PointerProperty
)
from mathutils import Quaternion, Vector
from .gen_func import bridgeLoops, create_mesh_object
from math import pi

def primitive_Tube(
    radius_out = 1.0,
    radius_in = 0.0,
    height = 2.0,
    use_inner = True,
    seg_perimeter = 24,
    seg_radius = 1,
    seg_height = 1,
    sector_from = 0.0,
    sector_to = 2*pi,
    centered = True):

    verts = []
    edges = []
    faces = []

    top_rings = []
    bottom_rings = []
    loops = []
    inner_loops = []
    midpoints = []

    #make sure of what is bigger
    if radius_out < radius_in:
        radius_in, radius_out = radius_out, radius_in

    if sector_from > sector_to:
        sector_to, sector_from = sector_from, sector_to

    if radius_out - radius_in < 0.0001:
        use_inner = False

    if seg_perimeter < 3:
        seg_perimeter = 3

    #sizes of chunks
    stepAngle = (sector_to - sector_from) / seg_perimeter
    stepRadius = (radius_out - radius_in) / seg_radius
    stepHeight = height / seg_height

    middlePoint = radius_in <= 0.0001
    closed = (sector_to - sector_from) >= 2*pi
    seg_number = seg_perimeter
    if not closed:
        seg_number = seg_perimeter +1
    rad_number = seg_radius
    if middlePoint:
        rad_number = seg_radius -1

    #wall around
    for z in range(seg_height +1):
        loop = []
        for s in range(seg_number):
            loop.append(len(verts))
            quat = Quaternion((0,0,1), (s * stepAngle) + sector_from)
            verts.append(quat * Vector((radius_out, 0.0, z * stepHeight)))
        loops.append(loop)

    #fill the wall around
    for i in range(len(loops) -1):
        faces.extend(bridgeLoops(loops[i], loops[i +1], closed))

    #
    if use_inner:
        #fill the caps (without the center)
        for z in range(2):
            if z == 0:
                bottom_rings.append(loops[0])
            else:
                top_rings.append(loops[-1])

            for r in range(rad_number):
                ring = []
                for s in range(seg_number):
                    ring.append(len(verts))
                    quat = Quaternion((0,0,1), (s * stepAngle) + sector_from)
                    verts.append(quat * Vector((radius_out - ((r+1) * stepRadius), 0.0, z * height)))
                if z == 0:
                    bottom_rings.append(ring)
                else:
                    top_rings.append(ring)



        for i in range(len(top_rings) -1):
            faces.extend(bridgeLoops(top_rings[i], top_rings[i +1], closed))
        for i in range(len(bottom_rings) -1):
            faces.extend(bridgeLoops(bottom_rings[-(i+1)], bottom_rings[-(i+2)], closed))

        #fill the center
        if middlePoint:
            #fill with middle point
            if closed:
                for z in range(2):
                    midpoints.append(len(verts))
                    verts.append(Vector((0.0, 0.0, z * height)))
            else:
                for z in range(seg_height +1):
                    midpoints.append(len(verts))
                    verts.append(Vector((0.0, 0.0, z * stepHeight)))

            #close the cup
            for s in range(seg_number -1):
                faces.append((bottom_rings[-1][s], midpoints[0], bottom_rings[-1][s+1]))
                faces.append((top_rings[-1][s], top_rings[-1][s+1], midpoints[-1]))
            if closed:
                faces.append((bottom_rings[-1][-1], midpoints[0], bottom_rings[-1][0]))
                faces.append((top_rings[-1][-1], top_rings[-1][0], midpoints[-1]))

        else:
            #fill with inner loops
            inner_loops.append(bottom_rings[-1])
            for z in range(seg_height-1):
                loop = []
                for s in range(seg_number):
                    loop.append(len(verts))
                    quat = Quaternion((0,0,1), (s * stepAngle) + sector_from)
                    verts.append(quat * Vector((radius_in, 0.0, (z+1) * stepHeight)))
                inner_loops.append(loop)
            inner_loops.append(top_rings[-1])
            for i in range(len(inner_loops) -1):
                faces.extend(bridgeLoops(inner_loops[-(i+1)], inner_loops[-(i+2)], closed))

        #fill the walls
        if not closed:
            wall_lines_01 = []
            wall_lines_02 = []
            if middlePoint:
                rad_number += 1
            #first wall
            quat = Quaternion((0,0,1), sector_from)
            line = []
            for loop in loops:
                line.append(loop[0])
            wall_lines_01.append(line)
            for r in range(rad_number-1):
                line = []
                line.append(bottom_rings[r+1][0])
                for h in range(seg_height -1):
                    line.append(len(verts))
                    verts.append(quat * Vector((radius_out - ((r+1) *stepRadius), 0.0, (h+1) * stepHeight)))
                line.append(top_rings[r+1][0])
                wall_lines_01.append(line)

            if middlePoint:
                wall_lines_01.append(midpoints)
            else:
                line = []
                for loop in inner_loops:
                    line.append(loop[0])
                wall_lines_01.append(line)

            #second wal
            quat = Quaternion((0,0,1), sector_to)
            line = []
            for loop in loops:
                line.append(loop[-1])
            wall_lines_02.append(line)
            for r in range(rad_number-1):
                line = []
                line.append(bottom_rings[r+1][-1])
                for h in range(seg_height -1):
                    line.append(len(verts))
                    verts.append(quat * Vector((radius_out - ((r+1) *stepRadius), 0.0, (h+1) * stepHeight)))
                line.append(top_rings[r+1][-1])
                wall_lines_02.append(line)

            if middlePoint:
                wall_lines_02.append(midpoints)
            else:
                line = []
                for loop in inner_loops:
                    line.append(loop[-1])
                wall_lines_02.append(line)

            #filling the walls
            for i in range(len(wall_lines_01) -1):
                faces.extend(bridgeLoops(wall_lines_01[i], wall_lines_01[i +1], False))
            for i in range(len(wall_lines_02) -1):
                faces.extend(bridgeLoops(wall_lines_02[-(i+1)], wall_lines_02[-(i+2)], False))


    if centered:
        for vertex in verts:
            vertex[2] -= height / 2

    return verts, edges, faces

class Make_WTube(bpy.types.Operator):
    """Create primitive WTube"""
    bl_idname = "mesh.make_wtube"
    bl_label = "WTube"
    bl_options = {'UNDO', 'REGISTER'}



    def execute(self, context):
        verts, edges, faces = primitive_Tube()
        create_mesh_object(context, verts, edges, faces, "WBox")

        context.object.data.WType = 'WTUBE'
        bpy.ops.object.shade_smooth()
        context.object.data.use_auto_smooth = True
        return {'FINISHED'}

def UpdateWTube(self, context):
    WData = context.object.data.WTube
    verts, edges, faces = primitive_Tube(
        radius_out = WData.rads[0],
        radius_in = WData.rads[1],
        height = WData.height,
        use_inner = WData.inner,
        seg_perimeter = WData.seg[0],
        seg_radius = WData.seg[1],
        seg_height = WData.seg[2],
        sector_from = WData.sec[0],
        sector_to = WData.sec[1],
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

    if WData.smooth:
        bpy.ops.object.shade_smooth()

class WTubeData(bpy.types.PropertyGroup):

    rads = FloatVectorProperty(
        name="Radiuses",
        description="Inner and outer radiuses",
        default=(1.0, 0.0),
        min=0.0,
        soft_min=0.0,
        step=1,
        precision=2,
        subtype='NONE',
        unit='LENGTH',
        size=2,
        update = UpdateWTube
    )

    height = FloatProperty(
        name="Height",
        description="Height of the Tube",
        default=2.0,
        min=0.0,
        soft_min=0.0,
        step=1,
        precision=2,
        unit='LENGTH',
        update=UpdateWTube
    )

    inner = BoolProperty(
        name="Use inner",
        description="use inner radius",
        default=True,
        update = UpdateWTube
    )

    smooth = BoolProperty(
        name="Smooth",
        description="Smooth shading",
        default=True,
        update = UpdateWTube
    )

    seg = IntVectorProperty(
        name="Segmentation",
        description="Subdivision of the cylinder",
        default=(24, 1, 1),
        min=1,
        soft_min=1,
        step=1,
        subtype='NONE',
        size=3,
        update = UpdateWTube
    )

    sec = FloatVectorProperty(
        name="Section",
        description="Section of the cylinder",
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
        update = UpdateWTube
    )

    centered = BoolProperty(
        name="Centered",
        description="Set origin of the cylinder",
        default=True,
        update = UpdateWTube
    )

def drawWTubePanel(self, context):
    lay_out = self.layout
    WData = context.object.data.WTube
    lay_out.label("Type: WTube", icon='MESH_CYLINDER')
    row = lay_out.row()
    column = row.column()
    column.prop(WData, "rads")
    column.prop(WData, "height")
    column = row.column()
    column.prop(WData, "seg")
    column = row.column()
    column.prop(WData, "sec")
    row = lay_out.row()
    row.prop(WData, "inner")
    row.prop(WData, "centered")
    row.prop(WData, "smooth")

def registerWTube():
    bpy.utils.register_class(Make_WTube)
    bpy.utils.register_class(WTubeData)
    bpy.types.Mesh.WTube = PointerProperty(type=WTubeData)

def unregisterWTube():
    bpy.utils.unregister_class(Make_WTube)
    bpy.utils.unregister_class(WTubeData)
    del bpy.types.Mesh.WTube
