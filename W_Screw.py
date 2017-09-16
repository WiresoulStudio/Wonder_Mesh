#___________________________________/
#___Author:_________Vit_Prochazka___/
#___Created:________15.12.2015______/
#___Last_modified:__12.08.2017______/
#___Version:________0.2_____________/
#___________________________________/

import bpy
import bmesh
from bpy.props import (
    IntProperty,
    FloatProperty,
    FloatVectorProperty,
    PointerProperty,
    BoolProperty
)
from mathutils import Quaternion, Vector
from math import pi
from .gen_func import create_mesh_object

def bridgeLoops(loop1, loop2):
    faces = []

    if len(loop1) != len(loop2):
        return None

    for i in range(len(loop1) -1):
        face = (loop1[i], loop1[i+1], loop2[i+1], loop2[i])
        faces.append(face)

    return faces

def getHeight(j, i, layers, height, addition, segments, layerHeight):
    if j == 0:
        return 0
    elif j == layers -1:
        return height
    else:
        if j == 1:
            return (i * addition) /2
        elif j == layers -2:
            if i==0:
                return (height - (3* layerHeight))
            else:
                return height - (((segments -i) * addition) /2)
        else:
            if j == 3 or j == 4:
                if i == 0:
                    return ((j -2)*layerHeight) + (addition /2)
                else:
                    return ((j -2)*layerHeight) + (i*addition)
            elif j == layers -4 or j == layers -5:
                if i == segments -1:
                    return height -((layers -j -3) *layerHeight) -(addition /2)
                else:
                    return ((j -2)*layerHeight) + (i*addition)
            else:
                return ((j -2)*layerHeight) + (i*addition)

def getAngle(j, i, angle, layers, segments):
    if j == 1 and i == 2:
        return (angle *2.2)
    elif j == layers -2 and i == segments -2:
        return ((2*pi) -(angle *2.2))
    elif j == 3 or j == 4:
        if i == 0:
            return (angle /2)
        elif i==segments and layers==8:
            return ((2*pi) -(angle /2))
        else:
            return (angle *i)
    elif j == layers -4 or j == layers -5:
        if i == segments:
            return ((2*pi) -(angle /2))
        else:
            return (angle *i)
    else:
        return (angle *i)

def getRadius(j, i, layers, segments, radius_1, radius_2):
    if j==0 or j==layers-1 or j%4==1 or j%4==2:
        return radius_1
    elif ((j==3 or j==4) and i==0) or((j==layers-4 or j==layers-5) and i==segments):
        return ((radius_1 + radius_2) /2)
    else:
        return radius_2

def primitive_Screw(
    rounds = 5,
    segments = 12,
    height = 2.0,
    radius_1 = 0.5,
    radius_2 = 0.6):

    if rounds < 1:
        rounds = 1
    if segments < 4:
        segments = 4
    if radius_1 < 0:
        radius_1 = 0
    if radius_2 < 0:
        radius_2 < 0

    #...prepare empty lists
    verts = []
    edges = []
    faces = []

    loops = []
    closure1 = []
    closure2 = []

    #...precompute some values
    layers = (rounds +1) *4
    layerHeight = height /(layers -1)
    addition = (layerHeight *4) /segments
    angle = (2*pi) /segments

    #...creating the layers
    for j in range(layers):
        loop = []
        for i in range(segments +1):

            h = getHeight(j, i, layers, height, addition, segments, layerHeight)
            a = getAngle(j, i, angle, layers, segments)
            r = getRadius(j, i, layers, segments, radius_1, radius_2)

            #...where are vertices missing from loops
            non1 = (i==segments and not(j==(layers -4) or j==(layers -5)))
            non2 = (j==1 or j==2) and i<2
            non3 = (j==(layers-2) or j==(layers-3)) and i>(segments-2)

            if non1==False and non2==False and non3==False:
                quat = Quaternion((0,0,1), a)
                loop.append(len(verts))
                if (j==0 or (j>4 and j<(layers-1))) and i==0:
                    closure1.append(len(verts))
                elif (i==(segments-1) and j<(layers-5)):
                    closure2.append(len(verts))
                verts.append(quat * Vector((r, 0, h)))
        loops.append(loop)

    #...creating faces
    #.......basic loops
    for i in range(len(loops)-1):
        newFaces = bridgeLoops(loops[i], loops[i+1])
        if newFaces:
            faces.extend(newFaces)
    #...closure
    newFaces = bridgeLoops(closure1, closure2)
    if newFaces:
        faces.extend(newFaces)
    #...Additional faces
    faces.append((0, loops[3][0], loops[4][0], loops[5][0]))
    faces.append((0, 1, loops[3][1], loops[3][0]))
    faces.append((1, 2, loops[1][0], loops[2][0]))
    faces.append((1, loops[2][0], loops[3][2], loops[3][1]))
    faces.append((loops[-6][-1], loops[-2][0], loops[-5][-1], loops[-5][-2]))
    faces.append((loops[-5][-1], loops[-2][0], loops[-1][0], loops[-4][-1]))
    faces.append((loops[-4][-2], loops[-4][-1], loops[-1][0], loops[-1][-1]))
    faces.append((loops[-4][-3], loops[-4][-2], loops[-1][-1], loops[-3][-1]))
    faces.append((loops[-3][-1], loops[-1][-1], loops[-1][-2], loops[-2][-1]))

    #...shortenLoops
    loops[0].pop(0)
    loops[0].pop(0)
    newFaces = bridgeLoops(loops[0], loops[1])
    if newFaces:
        faces.extend(newFaces)
    loops[3].pop(0)
    loops[3].pop(0)
    newFaces = bridgeLoops(loops[2], loops[3])
    if newFaces:
        faces.extend(newFaces)
    loops[-5].pop(-1)
    newFaces = bridgeLoops(loops[-6], loops[-5])
    if newFaces:
        faces.extend(newFaces)
    loops[-4].pop(-1)
    loops[-4].pop(-1)
    newFaces = bridgeLoops(loops[-4], loops[-3])
    if newFaces:
        faces.extend(newFaces)
    loops[-1].pop(-1)
    newFaces = bridgeLoops(loops[-2], loops[-1])
    if newFaces:
        faces.extend(newFaces)

    return verts, edges, faces

class Make_WScrew(bpy.types.Operator):
    """Create primitive WScrew"""
    bl_idname = "mesh.make_wscrew"
    bl_label = "WScrew"
    bl_options = {'UNDO', 'REGISTER'}

    def execute(self, context):

        verts, edges, faces = primitive_Screw()
        create_mesh_object(context, verts, edges, faces, "WScrew")

        context.object.data.WType = 'WSCREW'
        bpy.ops.object.shade_smooth()
        return {'FINISHED'}

def UpdateWScrew(self, context):
    WData = context.object.data.WScrew
    verts, edges, faces = primitive_Screw(
        rounds = WData.rounds,
        segments = WData.segments,
        height = WData.height,
        radius_1 = WData.rads[0],
        radius_2 = WData.rads[1]
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

class WScrewData(bpy.types.PropertyGroup):
    rounds = IntProperty(
        name="Rounds",
        description="Iterations of the screw",
        default=5,
        min=1,
        soft_min=1,
        update=UpdateWScrew
    )

    segments = IntProperty(
        name="Segments",
        description="Perimetr segments",
        default=12,
        min=3,
        soft_min=3,
        update=UpdateWScrew
    )

    height = FloatProperty(
        name="Height",
        description="Height of the screw",
        default=2.0,
        min=0.0,
        soft_min=0.0,
        step=1,
        precision=2,
        unit='LENGTH',
        update=UpdateWScrew
    )

    rads = FloatVectorProperty(
        name="Radiuses",
        description="Inner and outer radius",
        default=(0.5, 0.6,),
        min=0.0,
        soft_min=0.0,
        step=1,
        precision=2,
        unit='LENGTH',
        size=2,
        update = UpdateWScrew
    )

    smooth = BoolProperty(
        name="Smooth",
        description="Smooth shading",
        default=True,
        update = UpdateWScrew
    )

def drawWScrewPanel(self, context):
    lay_out = self.layout
    WData = context.object.data.WScrew
    lay_out.label("Type: WScrew", icon='MOD_SCREW')
    row = lay_out.row()
    column = row.column()
    column.prop(WData, "rounds")
    column.prop(WData, "segments")
    column.prop(WData, "height")
    column = row.column()
    column.prop(WData, "rads")
    lay_out.prop(WData, "smooth")

def registerWScrew():
    bpy.utils.register_class(Make_WScrew)
    bpy.utils.register_class(WScrewData)
    bpy.types.Mesh.WScrew = PointerProperty(type=WScrewData)

def unregisterWScrew():
    bpy.utils.unregister_class(Make_WScrew)
    bpy.utils.unregister_class(WScrewData)
    del bpy.types.Mesh.WScrew
