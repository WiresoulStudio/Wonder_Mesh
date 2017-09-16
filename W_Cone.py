#___________________________________/
#___Author:_________Vit_Prochazka___/
#___Created:________18.12.2015______/
#___Last_modified:__20.12.2015______/
#___Version:________0.2_____________/
#___________________________________/

import bpy
from bpy.props import *
from mathutils import *
from W_Primitives.gen_func import *
from math import *

def primitive_Cone(radius_bottom=1.0, radius_top=0.0, height=2.0, seg_perimeter=24,
                   seg_radius=1, seg_height=1, sector_from=0.0, sector_to=2*pi,
                   orientation='Z', centered=False):

    verts = []
    edges = []
    faces = []

    #set the proper vars
    if seg_perimeter < 3:
        seg_perimeter = 3
    if sector_from > sector_to:
        tmp = sector_to
        sector_to = sector_from
        sector_from = tmp

    point_top = radius_top <= 0.0001
    point_bottom = radius_bottom <= 0.0001
    closed = sector_to - sector_from >= 2*pi
    step_height = height / seg_height

    if point_top and point_bottom:
        #create just line
        for h in range(seg_height +1):
            verts.append(Vector((0.0, 0.0, h * step_height)))
        for v in range(len(verts) -1):
            edges.append((v, v+1))

        if centered:
            for v in verts:
                v.z -= height /2
        if orientation == 'X':
            for v in verts:
                v.x = v.z
                v.z = 0.0
        elif orientation == 'Y':
            for v in verts:
                v.y = v.z
                v.z = 0.0
        return verts, edges, faces

    step_angle = (sector_to - sector_from) / seg_perimeter
    step_rad_bottom = radius_bottom / seg_radius
    step_rad_top = radius_top / seg_radius
    radius_growth = (radius_bottom - radius_top) / seg_height
    seg_number = seg_perimeter +1
    if closed:
        seg_number = seg_perimeter

    #creation itself
    vert_bottom = len(verts)
    verts.append(Vector((0.0, 0.0, 0.0)))
    vert_top = len(verts)
    verts.append(Vector((0.0, 0.0, height)))

    lines = []
    for s in range(seg_number):
        quat = Quaternion((0, 0, 1), (s * step_angle) + sector_from)
        line = []
        #bottom line
        #line.append(vert_bottom)
        if not point_bottom:
            for r in range(seg_radius):
                line.append(len(verts))
                verts.append(quat * Vector(((r+1) * step_rad_bottom, 0.0, 0.0)))

        #outside
        if seg_height > 1:
            for h in range(seg_height -1):
                line.append(len(verts))
                verts.append(quat * Vector((radius_bottom - ((h+1)*radius_growth), 0.0, (h+1)*step_height)))

        #top line
        if not point_top:
            for r in range(seg_radius):
                line.append(len(verts))
                verts.append(quat * Vector((radius_top - (r*step_rad_top), 0.0, height)))

        #line.append(vert_top)
        lines.append(line)

    #fill the surface
    for i in range(len(lines) -1):
        faces.extend(bridgeLoops(lines[-(i+1)], lines[-(i+2)], False))
    #close cups
    for i in range(len(lines) -1):
        faces.append((lines[i][-1], lines[i+1][-1], vert_top))
        faces.append((lines[-(i+1)][0], lines[-(i+2)][0], vert_bottom))

    if closed:
        faces.extend(bridgeLoops(lines[0], lines[-1], False))
        faces.append((lines[-1][-1], lines[0][-1], vert_top))
        faces.append((lines[0][0], lines[-1][0], vert_bottom))

    #fill the walls if not closed
    if not closed:
        pass

    if centered:
        for v in verts:
            v.z -= height /2
    if orientation == 'X':
        for v in verts:
            tmp = v.x
            v.x = v.z
            v.z = -tmp
    elif orientation == 'Y':
        for v in verts:
            tmp = v.y
            v.y = v.z
            v.z = -tmp

    return verts, edges, faces

class MakePrimitive_cone(bpy.types.Operator):
    """Edit object as primitive cone"""
    bl_idname = "mesh.primitive_cone"
    bl_label = "Cone"
    bl_options = {'UNDO', 'REGISTER'}

    orientations_list = [
        ('Z', "Z-axis", ""),
        ('X', "X-axis", ""),
        ('Y', "Y-axis", "")]

    radiuses = FloatVectorProperty(
        name="Radiuses",
        description="Top and bottom radiuses",
        default=(0.0, 1.0),
        min=0.0,
        soft_min=0.0,
        step=1,
        precision=2,
        subtype='NONE',
        unit='LENGTH',
        size=2)

    height = FloatProperty(
        name="Height",
        description="Height of the cone",
        default=2.0,
        min=0.0,
        soft_min=0.0,
        step=1,
        precision=2,
        subtype='DISTANCE',
        unit='LENGTH')

    segmentation = IntVectorProperty(
        name="Segmentation",
        description="Subdivision of the cone",
        default=(24, 1, 1),
        min=1,
        soft_min=1,
        step=1,
        subtype='NONE',
        size=3)

    section = FloatVectorProperty(
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
        size=2)

    orientation = EnumProperty(
        items=orientations_list,
        name="Orientation",
        description="Facing of the cone",
        default='Z')

    centered = BoolProperty(
        name="Centered",
        description="Center the cone",
        default=False)

    def execute(self, context):

        verts, edges, faces = primitive_Cone(
            radius_bottom=self.radiuses[1],
            radius_top=self.radiuses[0],
            height=self.height,
            seg_perimeter=self.segmentation[0],
            seg_radius=self.segmentation[1],
            seg_height=self.segmentation[2],
            sector_from=self.section[0],
            sector_to=self.section[1],
            orientation=self.orientation,
            centered=self.centered)

        updateMesh(context, verts, edges, faces)

        cone_data = {
            "radius_bottom":self.radiuses[1],
            "radius_top":self.radiuses[0],
            "height":self.height,
            "seg_perimeter":self.segmentation[0],
            "seg_radius":self.segmentation[1],
            "seg_height":self.segmentation[2],
            "sector_from":self.section[0],
            "sector_to":self.section[1],
            "orientation":self.orientation,
            "centered":self.centered}
        context.object["isCone"] = cone_data

        return {'FINISHED'}

    def invoke(self, context, event):
        if "isCone" in context.object:
            cone_data = context.object["isCone"]
            self.radiuses[1] = cone_data["radius_bottom"]
            self.radiuses[0] = cone_data["radius_top"]
            self.height = cone_data["height"]
            self.segmentation[0] = cone_data["seg_perimeter"]
            self.segmentation[1] = cone_data["seg_radius"]
            self.segmentation[2] = cone_data["seg_height"]
            self.section[0] = cone_data["sector_from"]
            self.section[1] = cone_data["sector_to"]
            self.orientation  = cone_data["orientation"]
            self.centered = cone_data["centered"]
        else:
            self.radiuses[1] = 1.0
            self.radiuses[0] = 0.0
            self.height = 2.0
            self.segmentation[0] = 24
            self.segmentation[1] = 1
            self.segmentation[2] = 1
            self.section[0] = 0.0
            self.section[1] = 2*pi
            self.orientation  = 'Z'
            self.centered = False
        return self.execute(context)
