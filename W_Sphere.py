# __________________________________/
# __Author:_________Vit_Prochazka___/
# __Created:________13.08.2017______/
# __Last_modified:__07.04.2018______/
# __Version:________0.2_____________/
# __________________________________/

"""
This file generates and modifies a sphere-shaped mesh.
"""

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

WSphere_defaults = {
    "radius": 1.0,
    "segments": 24,
    "rings": 12,
    "base": 3,
    "divisions": 2,
    "tris": False,
    "smoothed": True
}


def primitive_UVSphere(
                radius = 1.0,
                segments = 24,
                rings = 12):

    verts = []
    edges = []
    faces = []

    loops = []

    # create top and bottom verts
    verts.append(Vector((0.0, 0.0, radius)))
    verts.append(Vector((0.0, 0.0, -radius)))

    # calculate angles
    UAngle = (2*pi)/segments
    VAngle = pi/rings

    # create rings
    for v in range(rings - 1):
        loop = []
        quatV = Quaternion((0, -1, 0), VAngle * (v + 1))
        baseVect = quatV * Vector((0.0, 0.0, -radius))
        for u in range(segments):
            loop.append(len(verts))
            quatU = Quaternion((0, 0, 1), UAngle * u)
            verts.append(quatU * baseVect)
        loops.append(loop)

    # create faces
    for i in range(rings - 2):
        faces.extend(bridgeLoops(loops[i], loops[i + 1], True))

    # fill top
    ring = loops[-1]
    for i in range(segments):
        if (i == segments - 1):
            faces.append((ring[i], ring[0], 0))
        else:
            faces.append((ring[i], ring[i + 1], 0))

    # fill bottom
    ring = loops[0]
    for i in range(segments):
        if (i == segments - 1):
            faces.append((ring[0], ring[i], 1))
        else:
            faces.append((ring[i + 1], ring[i], 1))

    return verts, edges, faces


def primitive_polySphere(
                    base = "CUBE",
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

        # normalize
        for vert in verts:
            vert.normalize()
            vert *= radius

    return verts, edges, faces


def UpdateWSphere(Wdata):
    WData = Wdata["animArgs"]

    if WData["base"] == 1:
        verts, edges, faces = primitive_UVSphere(
            radius = WData["radius"],
            segments = WData["segments"],
            rings = WData["rings"]
        )
    else:
        bases = ["TETRA", "CUBE", "OCTA", "ICOSA"]
        verts, edges, faces = primitive_polySphere(
            base = bases[WData["base"] - 2],
            radius = WData["radius"],
            divisions = WData["divisions"],
            tris = WData["tris"]
        )
    tmpMesh = bpy.data.meshes.new("TemporaryMesh")
    tmpMesh.from_pydata(verts, edges, faces)
    tmpMesh.update()

    bm = bmesh.new()
    bm.from_mesh(tmpMesh)
    for fa in bm.faces:
        fa.smooth = Wdata.smoothed
    bm.to_mesh(Wdata.id_data)
    bm.free()
    bpy.data.meshes.remove(tmpMesh)
    Wdata.id_data.update()


def Update_Size(Wdata):
    radius = Wdata["animArgs"]["radius"]

    for vert in Wdata.id_data.vertices:
        vert.co.normalize()
        vert.co *= radius


class Make_WSphere(bpy.types.Operator):
    """Create primitive WSphere"""
    bl_idname = "mesh.make_wsphere"
    bl_label = "WSphere"
    bl_options = {'UNDO', 'REGISTER'}

    def execute(self, context):
        verts, edges, faces = primitive_polySphere()
        create_mesh_object(context, verts, edges, faces, "WSphere")

        context.object.data.WSphere["animArgs"] = WSphere_defaults

        context.object.data.WType = 'WSPHERE'
        bpy.ops.object.shade_smooth()
        return {'FINISHED'}


# getters_____________________________________________________________________
def getRadius(self):
    return self["animArgs"]["radius"]


def getSegments(self):
    return self["animArgs"]["segments"]


def getRing(self):
    return self["animArgs"]["rings"]


def getDivisions(self):
    return self["animArgs"]["divisions"]


def getBase(self):
    return self["animArgs"]["base"]


def getSmoothed(self):
    return self["animArgs"]["smoothed"]


def getTris(self):
    return self["animArgs"]["tris"]


# setters_____________________________________________________________________
def setRadius(self, val):
    self["animArgs"]["radius"] = val
    Update_Size(self)


def setSegments(self, val):
    self["animArgs"]["segments"] = val
    UpdateWSphere(self)


def setRing(self, val):
    self["animArgs"]["rings"] = val
    UpdateWSphere(self)


def setDivisions(self, val):
    self["animArgs"]["divisions"] = val
    UpdateWSphere(self)


def setBase(self, val):
    self["animArgs"]["base"] = val
    UpdateWSphere(self)


def setSmoothed(self, val):
    self["animArgs"]["smoothed"] = val
    UpdateWSphere(self)


def setTris(self, val):
    self["animArgs"]["tris"] = val
    UpdateWSphere(self)


class WSphereData(bpy.types.PropertyGroup):
    radius = FloatProperty(
        name="Radius",
        description="Radius of the Sphere",
        default=1.0,
        min=0.0,
        soft_min=0.0001,
        step=1,
        unit='LENGTH',
        set = setRadius,
        get = getRadius
    )

    segments = IntProperty(
        name="Segments",
        description="Segments on diametr",
        default=24,
        min=3,
        soft_min=3,
        step=1,
        subtype='NONE',
        set = setSegments,
        get = getSegments
    )

    rings = IntProperty(
        name="Rings",
        description="Rings",
        default=12,
        min=2,
        soft_min=2,
        step=1,
        subtype='NONE',
        set = setRing,
        get = getRing
    )

    divisions = IntProperty(
        name="Division",
        description="Divisions of the base mesh",
        default=2,
        min=0,
        soft_min=0,
        step=1,
        subtype='NONE',
        set = setDivisions,
        get = getDivisions
    )

    Topos = [
        ('UV', "UV", "", 1),
        ('TETRA', "Tetrahedron", "", 2),
        ('CUBE', "Cube", "", 3),
        ('OCTA', "Octahedron", "", 4),
        ('ICOSA', "Icosahedron", "", 5)
    ]

    base = EnumProperty(
        items = Topos,
        name = "Topology",
        description = "Type of sphere topology",
        default = 'CUBE',
        set = setBase,
        get = getBase
    )

    smoothed = BoolProperty(
        name="Smooth",
        description="Smooth shading",
        default=True,
        set = setSmoothed,
        get = getSmoothed
    )

    tris = BoolProperty(
        name="Tris",
        description="Triangulate divisions",
        default=False,
        set = setTris,
        get = getTris
    )


def drawWSpherePanel(self, context):
    lay_out = self.layout
    WData = context.object.data.WSphere
    lay_out.label("Type: WSphere", icon='MESH_UVSPHERE')
    row = lay_out.row()
    col = row.column()
    col.prop(WData, "radius")
    col.prop(WData, "base")
    col = row.column()
    if (WData.base == 'UV'):
        col.prop(WData, "segments")
        col.prop(WData, "rings")
    elif (WData.base != 'UV'):
        col.prop(WData, "divisions")
        col.prop(WData, "tris")

    lay_out.prop(WData, "smoothed")


def registerWSphere():
    bpy.utils.register_class(Make_WSphere)
    bpy.utils.register_class(WSphereData)
    bpy.types.Mesh.WSphere = PointerProperty(type=WSphereData)


def unregisterWSphere():
    bpy.utils.unregister_class(Make_WSphere)
    bpy.utils.unregister_class(WSphereData)
    del bpy.types.Mesh.WSphere
