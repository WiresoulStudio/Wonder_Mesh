#___________________________________/
#___Author:_________Vit_Prochazka___/
#___Created:________13.08.2017______/
#___Last_modified:__13.08.2017______/
#___Version:________0.1_____________/
#___________________________________/

import bpy
import bmesh
from bpy.props import (
    FloatProperty,
    IntProperty,
    PointerProperty,
    EnumProperty,
    BoolProperty
)
from mathutils import Vector, Quaternion
from math import pi
from .gen_func import bridgeLoops, create_mesh_object, subdivide
from .W_Bases import baseHedron

def primitive_UVSphere (
    radius = 1.0,
    segments = 24,
    rings = 12 ):


    verts = []
    edges = []
    faces = []

    loops = []

    #create top and bottom verts
    verts.append(Vector((0.0, 0.0, radius)))
    verts.append(Vector((0.0, 0.0, -radius)))

    #calculate angles
    UAngle = (2*pi)/segments
    VAngle = pi/rings

    #create rings
    for v in range(rings -1):
        loop = []
        quatV = Quaternion((0,-1,0), VAngle * (v +1))
        baseVect = quatV * Vector((0.0, 0.0, -radius))
        for u in range(segments):
            loop.append(len(verts))
            quatU = Quaternion((0, 0, 1), UAngle * u)
            verts.append(quatU * baseVect)
        loops.append(loop)

    #create faces
    for i in range(rings -2):
        faces.extend(bridgeLoops(loops[i], loops[i+1], True))

    #fill top
    ring = loops[-1]
    for i in range(segments):
        if (i == segments -1):
            faces.append((ring[i], ring[0], 0))
        else:
            faces.append((ring[i], ring[i+1], 0))

    #fill bottom
    ring = loops[0]
    for i in range(segments):
        if (i == segments -1):
            faces.append((ring[0], ring[i], 1))
        else:
            faces.append((ring[i+1], ring[i], 1))

    return verts, edges, faces

def primitive_polySphere (
    base = "TETRA",
    radius = 1.0,
    divisions = 2,
    tris = True):

    verts, edges, faces = baseHedron(base)

    for vert in verts:
        vert.normalize()
        vert *= radius

    if base == "CUBE":
        tris = False

    for i in range(divisions):
        verts, edges, faces = subdivide(verts, edges, faces, tris)

        #normalize
        for vert in verts:
            vert.normalize()
            vert *= radius

    return verts, edges, faces

class Make_WSphere(bpy.types.Operator):
    """Create primitive WSphere"""
    bl_idname = "mesh.make_wsphere"
    bl_label = "WSphere"
    bl_options = {'UNDO', 'REGISTER'}

    def execute(self, context):
        verts, edges, faces = primitive_UVSphere()
        create_mesh_object(context, verts, edges, faces, "WSphere")

        context.object.data.WType = 'WSPHERE'
        bpy.ops.object.shade_smooth()
        return {'FINISHED'}

def UpdateWSphere(self, context):
    WData = context.object.data.WSphere

    if WData.topo == 'UV':
        verts, edges, faces = primitive_UVSphere(
            radius = WData.radius,
            segments = WData.segments,
            rings = WData.rings
        )
    else:
        verts, edges, faces = primitive_polySphere(
            base = WData.topo,
            radius = WData.radius,
            divisions = WData.divisions,
            tris = WData.tris
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

def Update_Size(self, context):
    radius = context.object.data.WSphere.radius

    for vert in context.object.data.vertices:
        vert.co.normalize()
        vert.co *= radius

class WSphereData(bpy.types.PropertyGroup):
    radius = FloatProperty(
        name="Radius",
        description="Radius of the Sphere",
        default=1.0,
        min=0.0,
        soft_min=0.0001,
        step=1,
        precision=2,
        unit='LENGTH',
        update=Update_Size
    )

    segments = IntProperty(
        name="Segments",
        description="Segments on diametr",
        default=24,
        min=3,
        soft_min=3,
        step=1,
        subtype='NONE',
        update=UpdateWSphere
    )

    rings = IntProperty(
        name="Rings",
        description="Rings",
        default=12,
        min=2,
        soft_min=2,
        step=1,
        subtype='NONE',
        update=UpdateWSphere
    )

    divisions = IntProperty(
        name="Division",
        description="Divisions of the base mesh",
        default=2,
        min=0,
        soft_min=0,
        step=1,
        subtype='NONE',
        update=UpdateWSphere
    )

    Topos = [
        ('UV', "UV", ""),
        ('TETRA', "Tetrahedron", ""),
        ('CUBE', "Cube", ""),
        ('OCTA', "Octahedron", ""),
        ('ICOSA', "Icosahedron", "")
    ]

    topo = EnumProperty(
        items = Topos,
        name = "Topology",
        description = "Type of sphere topology",
        default = 'UV',
        update=UpdateWSphere
    )

    smooth = BoolProperty(
        name="Smooth",
        description="Smooth shading",
        default=True,
        update = UpdateWSphere
    )

    tris = BoolProperty(
        name="Tris",
        description="Triangulate divisions",
        default=False,
        update = UpdateWSphere
    )


def drawWSpherePanel(self, context):
    lay_out = self.layout
    WData = context.object.data.WSphere
    lay_out.label("Type: WSphere", icon='MESH_UVSPHERE')
    row = lay_out.row()
    col = row.column()
    col.prop(WData, "radius")
    col.prop(WData, "topo")
    col = row.column()
    if (WData.topo == 'UV'):
        col.prop(WData, "segments")
        col.prop(WData, "rings")
    elif (WData.topo != 'UV'):
        col.prop(WData, "divisions")
        col.prop(WData, "tris")

    lay_out.prop(WData, "smooth")

def registerWSphere():
    bpy.utils.register_class(Make_WSphere)
    bpy.utils.register_class(WSphereData)
    bpy.types.Mesh.WSphere = PointerProperty(type=WSphereData)

def unregisterWSphere():
    bpy.utils.unregister_class(Make_WSphere)
    bpy.utils.unregister_class(WSphereData)
    del bpy.types.Mesh.WSphere
