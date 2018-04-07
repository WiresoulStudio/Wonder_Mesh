# __________________________________/
# __Author:_________Vit_Prochazka___/
# __Created:________16.12.2015______/
# __Last_modified:__07.04.2018______/
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
from mathutils import Quaternion, Vector
from .gen_func import bridgeLoops, create_mesh_object
from math import pi

WTube_Defaults = {
    "radius_out": 1.0,
    "radius_in": 0.0,
    "height": 2.0,
    "use_inner": True,
    "seg_perimeter": 24,
    "seg_radius": 1,
    "seg_height": 1,
    "sector_from": 0.0,
    "sector_to": 2 * pi,
    "centered": True,
    "smoothed": True
}


def primitive_Tube(
                radius_out = 1.0,
                radius_in = 0.0,
                height = 2.0,
                use_inner = True,
                seg_perimeter = 24,
                seg_radius = 1,
                seg_height = 1,
                sector_from = 0.0,
                sector_to = 2 * pi,
                centered = True,
                smoothed = True):

    verts = []
    edges = []
    faces = []

    top_rings = []
    bottom_rings = []
    loops = []
    inner_loops = []
    midpoints = []

    # make sure of what is bigger
    if radius_out < radius_in:
        radius_in, radius_out = radius_out, radius_in

    if sector_from > sector_to:
        sector_to, sector_from = sector_from, sector_to

    if radius_out - radius_in < 0.0001:
        use_inner = False

    if seg_perimeter < 3:
        seg_perimeter = 3

    # sizes of chunks
    stepAngle = (sector_to - sector_from) / seg_perimeter
    stepRadius = (radius_out - radius_in) / seg_radius
    stepHeight = height / seg_height

    middlePoint = radius_in <= 0.0001
    closed = (sector_to - sector_from) >= 2 * pi
    seg_number = seg_perimeter
    if not closed:
        seg_number = seg_perimeter + 1
    rad_number = seg_radius
    if middlePoint:
        rad_number = seg_radius - 1

    # wall around
    for z in range(seg_height + 1):
        loop = []
        for s in range(seg_number):
            loop.append(len(verts))
            quat = Quaternion((0, 0, 1), (s * stepAngle) + sector_from)
            verts.append(quat * Vector((radius_out, 0.0, z * stepHeight)))
        loops.append(loop)

    # fill the wall around
    for i in range(len(loops) - 1):
        faces.extend(bridgeLoops(loops[i], loops[i + 1], closed))

    if use_inner:
        # fill the caps (without the center)
        for z in range(2):
            if z == 0:
                bottom_rings.append(loops[0])
            else:
                top_rings.append(loops[-1])

            for r in range(rad_number):
                ring = []
                for s in range(seg_number):
                    ring.append(len(verts))
                    quat = Quaternion((0, 0, 1), (s * stepAngle) + sector_from)
                    verts.append(quat * Vector((
                        radius_out - ((r + 1) * stepRadius),
                        0.0,
                        z * height)))
                if z == 0:
                    bottom_rings.append(ring)
                else:
                    top_rings.append(ring)

        for i in range(len(top_rings) - 1):
            faces.extend(bridgeLoops(top_rings[i], top_rings[i + 1], closed))
        for i in range(len(bottom_rings) - 1):
            faces.extend(bridgeLoops(
                bottom_rings[-(i + 1)], bottom_rings[-(i + 2)], closed))

        # fill the center
        if middlePoint:
            # fill with middle point
            if closed:
                for z in range(2):
                    midpoints.append(len(verts))
                    verts.append(Vector((0.0, 0.0, z * height)))
            else:
                for z in range(seg_height + 1):
                    midpoints.append(len(verts))
                    verts.append(Vector((0.0, 0.0, z * stepHeight)))

            # close the cup
            for s in range(seg_number - 1):
                faces.append((
                    bottom_rings[-1][s],
                    midpoints[0],
                    bottom_rings[-1][s + 1]))
                faces.append((
                    top_rings[-1][s], top_rings[-1][s + 1], midpoints[-1]))
            if closed:
                faces.append((
                    bottom_rings[-1][-1], midpoints[0], bottom_rings[-1][0]))
                faces.append((
                    top_rings[-1][-1], top_rings[-1][0], midpoints[-1]))

        else:
            # fill with inner loops
            inner_loops.append(bottom_rings[-1])
            for z in range(seg_height - 1):
                loop = []
                for s in range(seg_number):
                    loop.append(len(verts))
                    quat = Quaternion((0, 0, 1), (s * stepAngle) + sector_from)
                    verts.append(quat * Vector((
                        radius_in, 0.0, (z + 1) * stepHeight)))
                inner_loops.append(loop)
            inner_loops.append(top_rings[-1])
            for i in range(len(inner_loops) - 1):
                faces.extend(bridgeLoops(
                    inner_loops[-(i + 1)], inner_loops[-(i + 2)], closed))

        # fill the walls
        if not closed:
            wall_lines_01 = []
            wall_lines_02 = []
            if middlePoint:
                rad_number += 1
            # first wall
            quat = Quaternion((0, 0, 1), sector_from)
            line = []
            for loop in loops:
                line.append(loop[0])
            wall_lines_01.append(line)
            for r in range(rad_number - 1):
                line = []
                line.append(bottom_rings[r + 1][0])
                for h in range(seg_height - 1):
                    line.append(len(verts))
                    verts.append(quat * Vector((
                        radius_out - ((r + 1) * stepRadius),
                        0.0,
                        (h + 1) * stepHeight)))
                line.append(top_rings[r + 1][0])
                wall_lines_01.append(line)

            if middlePoint:
                wall_lines_01.append(midpoints)
            else:
                line = []
                for loop in inner_loops:
                    line.append(loop[0])
                wall_lines_01.append(line)

            # second wal
            quat = Quaternion((0, 0, 1), sector_to)
            line = []
            for loop in loops:
                line.append(loop[-1])
            wall_lines_02.append(line)
            for r in range(rad_number - 1):
                line = []
                line.append(bottom_rings[r + 1][-1])
                for h in range(seg_height - 1):
                    line.append(len(verts))
                    verts.append(quat * Vector((
                        radius_out - ((r + 1) * stepRadius),
                        0.0,
                        (h + 1) * stepHeight)))
                line.append(top_rings[r + 1][-1])
                wall_lines_02.append(line)

            if middlePoint:
                wall_lines_02.append(midpoints)
            else:
                line = []
                for loop in inner_loops:
                    line.append(loop[-1])
                wall_lines_02.append(line)

            # filling the walls
            for i in range(len(wall_lines_01) - 1):
                faces.extend(
                    bridgeLoops(
                        wall_lines_01[i], wall_lines_01[i + 1], False))
            for i in range(len(wall_lines_02) - 1):
                faces.extend(
                    bridgeLoops(
                        wall_lines_02[-(i + 1)],
                        wall_lines_02[-(i + 2)],
                        False))

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
        verts, edges, faces = primitive_Tube(**WTube_Defaults)
        create_mesh_object(context, verts, edges, faces, "WTube")

        context.object.data.WType = 'WTUBE'
        context.object.data.WTube["animArgs"] = WTube_Defaults
        context.object.data.WTube["thisMesh"] = context.object.data.name
        bpy.ops.object.shade_smooth()
        context.object.data.use_auto_smooth = True
        return {'FINISHED'}


def UpdateWTube(WData):
    verts, edges, faces = primitive_Tube(**WData["animArgs"])
    tmpMesh = bpy.data.meshes.new("TemporaryMesh")
    tmpMesh.from_pydata(verts, edges, faces)
    tmpMesh.update()

    bm = bmesh.new()
    bm.from_mesh(tmpMesh)
    for f in bm.faces:
        f.smooth = WData.smoothed
    bm.to_mesh(bpy.data.meshes[WData["thisMesh"]])
    bm.free()
    bpy.data.meshes.remove(tmpMesh)
    bpy.data.meshes[WData["thisMesh"]].update()


# getters
def getRadius_out(self):
    return self["animArgs"]["radius_out"]


def getRadius_in(self):
    return self["animArgs"]["radius_in"]


def getHeight(self):
    return self["animArgs"]["height"]


def getUse_inner(self):
    return self["animArgs"]["use_inner"]


def getSeg_perimeter(self):
    return self["animArgs"]["seg_perimeter"]


def getSeg_radius(self):
    return self["animArgs"]["seg_radius"]


def getSeg_height(self):
    return self["animArgs"]["seg_height"]


def getSector_from(self):
    return self["animArgs"]["sector_from"]


def getSector_to(self):
    return self["animArgs"]["sector_to"]


def getCentered(self):
    return self["animArgs"]["centered"]


def getSmoothed(self):
    return self["animArgs"]["smoothed"]


# Setters _____________________________________________________________________
def setRadius_out(self, val):
    self["animArgs"]["radius_out"] = val
    UpdateWTube(self)


def setRadius_in(self, val):
    self["animArgs"]["radius_in"] = val
    UpdateWTube(self)


def setHeight(self, val):
    self["animArgs"]["height"] = val
    UpdateWTube(self)


def setUse_inner(self, val):
    self["animArgs"]["use_inner"] = val
    UpdateWTube(self)


def setSeg_perimeter(self, val):
    self["animArgs"]["seg_perimeter"] = val
    UpdateWTube(self)


def setSeg_radius(self, val):
    self["animArgs"]["seg_radius"] = val
    UpdateWTube(self)


def setSeg_height(self, val):
    self["animArgs"]["seg_height"] = val
    UpdateWTube(self)


def setSector_from(self, val):
    self["animArgs"]["sector_from"] = val
    UpdateWTube(self)


def setSector_to(self, val):
    self["animArgs"]["sector_to"] = val
    UpdateWTube(self)


def setCentered(self, val):
    self["animArgs"]["centered"] = val
    UpdateWTube(self)


def setSmoothed(self, val):
    self["animArgs"]["smoothed"] = val
    UpdateWTube(self)


class WTubeData(bpy.types.PropertyGroup):

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

    height = FloatProperty(
        name="Height",
        description="Height of the tube",
        default=2.0,
        min=0.0,
        soft_min=0.0,
        step=1,
        unit='LENGTH',
        set = setHeight,
        get = getHeight
    )

    use_inner = BoolProperty(
        name="Use inner",
        description="use inner radius",
        default=True,
        set = setUse_inner,
        get = getUse_inner
    )

    seg_perimeter = IntProperty(
        name="Perimeter",
        description="Periimeter segmentation",
        default=24,
        min=3,
        soft_min=3,
        step=1,
        set = setSeg_perimeter,
        get = getSeg_perimeter
    )

    seg_radius = IntProperty(
        name="Radius",
        description="Radius segmentation",
        default=1,
        min=1,
        soft_min=1,
        step=1,
        set = setSeg_radius,
        get = getSeg_radius
    )

    seg_height = IntProperty(
        name="Height",
        description="Height segmentation",
        default=1,
        min=1,
        soft_min=1,
        step=1,
        set = setSeg_height,
        get = getSeg_height
    )

    sector_from = FloatProperty(
        name="From",
        description="Section of the cylinder",
        default=0.0,
        min=0.0,
        max=2 * pi,
        soft_min=0.0,
        soft_max=2 * pi,
        step=10,
        unit='ROTATION',
        set = setSector_from,
        get = getSector_from
    )

    sector_to = FloatProperty(
        name="To",
        description="Section of the cylinder",
        default=2 * pi,
        min=0.0,
        max=2 * pi,
        soft_min=0.0,
        soft_max=2 * pi,
        step=10,
        unit='ROTATION',
        set = setSector_to,
        get = getSector_to
    )

    centered = BoolProperty(
        name="Centered",
        description="Set origin of the cylinder",
        default=True,
        set = setCentered,
        get = getCentered
    )

    smoothed = BoolProperty(
        name="Smooth",
        description="Set origin of the cylinder",
        default=True,
        set = setSmoothed,
        get = getSmoothed
    )


def drawWTubePanel(self, context):
    lay_out = self.layout
    WData = context.object.data.WTube
    lay_out.label("Type: WTube", icon='MESH_CYLINDER')

    row = lay_out.row()
    column = row.column(align=True)
    column.label("Radiuses:")
    column.prop(WData, "radius_out")
    column.prop(WData, "radius_in")
    column.separator()
    column.prop(WData, "height")

    column = row.column(align=True)
    column.label("Segmentation:")
    column.prop(WData, "seg_perimeter")
    column.prop(WData, "seg_radius")
    column.prop(WData, "seg_height")

    column = row.column(align=True)
    column.label("Section:")
    column.prop(WData, "sector_from")
    column.prop(WData, "sector_to")

    row = lay_out.row()
    row.prop(WData, "use_inner")
    row.prop(WData, "centered")
    row.prop(WData, "smoothed")


def registerWTube():
    bpy.utils.register_class(Make_WTube)
    bpy.utils.register_class(WTubeData)
    bpy.types.Mesh.WTube = PointerProperty(type=WTubeData)


def unregisterWTube():
    bpy.utils.unregister_class(Make_WTube)
    bpy.utils.unregister_class(WTubeData)
    del bpy.types.Mesh.WTube
