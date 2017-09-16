#___________________________________/
#___Author:_________Vit_Prochazka___/
#___Created:________15.12.2015______/
#___Last_modified:__11.08.2017______/
#___Version:________0.2_____________/
#___________________________________/

bl_info = {
        "name": "Wonder_Mesh",
        "category": "Object",
        "author": "Vit Prochazka",
        "version": (0, 2),
        "blender": (2, 76),
        "description": "Modify primitives after creation.",
        "warning": "Unexpected bugs can be expected!"
        }

import bpy
from bpy.props import (
    EnumProperty
)
#from mathutils import *
from .W_Plane import registerWPlane, unregisterWPlane, drawWPlanePanel
from .W_Box import registerWBox, unregisterWBox, drawWBoxPanel
from .W_Ring import registerWRing, unregisterWRing, drawWRingPanel
from .W_Tube import registerWTube, unregisterWTube, drawWTubePanel
from .W_Sphere import registerWSphere, unregisterWSphere, drawWSpherePanel
from .W_Screw import registerWScrew, unregisterWScrew, drawWScrewPanel

class WAddMenu(bpy.types.Menu):
    bl_label = "W_Primitives"
    bl_idname = "OBJECT_MT_W_Primitives_menu"

    def draw(self,context):
        lay_out = self.layout
        lay_out.operator(operator="mesh.make_wplane", icon='MESH_PLANE')
        lay_out.operator(operator="mesh.make_wbox", icon='MESH_CUBE')
        lay_out.operator(operator="mesh.make_wring", icon='MESH_CIRCLE')
        lay_out.operator(operator="mesh.make_wtube", icon='MESH_CYLINDER')
        lay_out.operator(operator="mesh.make_wsphere", icon='MESH_UVSPHERE')
        lay_out.operator(operator="mesh.make_wscrew", icon='MOD_SCREW')

def draw_addMenu(self, context):
    lay_out = self.layout
    lay_out.menu(WAddMenu.bl_idname)

class WAddPanel(bpy.types.Panel):
    """Creates a Panel in the Toolbar"""
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'Create'
    bl_label = "W_Primitives"
    bl_context = "objectmode"
    bl_options = {'DEFAULT_CLOSED'}


    def draw(self, context):
        lay_out = self.layout.column(align=True)
        lay_out.operator(operator="mesh.make_wplane", icon='MESH_PLANE')
        lay_out.operator(operator="mesh.make_wbox", icon='MESH_CUBE')
        lay_out.operator(operator="mesh.make_wring", icon='MESH_CIRCLE')
        lay_out.operator(operator="mesh.make_wtube", icon='MESH_CYLINDER')
        lay_out.operator(operator="mesh.make_wsphere", icon='MESH_UVSPHERE')
        lay_out.operator(operator="mesh.make_wscrew", icon='MOD_SCREW')

class ConvertWMesh(bpy.types.Operator):
    """Convert WMesh to mesh"""
    bl_idname = "mesh.convert_w_mesh"
    bl_label = "Convert WMesh"
    bl_options = {'UNDO', 'REGISTER'}

    def execute(self, context):
        context.object.data.WType = 'NONE'
        return {'FINISHED'}

class WEditPanel(bpy.types.Panel):
    """Creates a Panel in the data context of the properties editor"""
    bl_label = "WMesh data"
    bl_idname = "DATA_PT_Wlayout"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        return (context.object.type == 'MESH')

    def draw(self, context):
        lay_out = self.layout
        obj = context.object
        WType = obj.data.WType

        if WType == 'NONE':
            lay_out.label("This is regular Mesh")
        else:
            if WType == 'WPLANE':
                drawWPlanePanel(self, context)
            elif WType == 'WBOX':
                drawWBoxPanel(self, context)
            elif WType == 'WSCREW':
                drawWScrewPanel(self, context)
            elif WType == 'WRING':
                drawWRingPanel(self, context)
            elif WType == 'WTUBE':
                drawWTubePanel(self, context)
            elif WType == 'WSPHERE':
                drawWSpherePanel(self, context)
            lay_out.separator()
            lay_out.operator(operator="mesh.convert_w_mesh", icon='RECOVER_AUTO')
            lay_out.separator()

def register():
    registerWPlane()
    registerWBox()
    registerWScrew()
    registerWRing()
    registerWTube()
    registerWSphere()

    bpy.utils.register_class(WAddPanel)
    bpy.utils.register_class(WAddMenu)
    bpy.utils.register_class(ConvertWMesh)
    bpy.utils.register_class(WEditPanel)

    bpy.types.INFO_MT_mesh_add.prepend(draw_addMenu)

    WTypes = [
        ('NONE', "None", ""),
        ('WPLANE', "WPlane", ""),
        ('WBOX', "WBox", ""),
        ('WSCREW', "WScrew", ""),
        ('WRING', "WRing", ""),
        ('WTUBE', "WTube", ""),
        ('WSPHERE', "WSphere", "")
    ]

    bpy.types.Mesh.WType = EnumProperty(
        items = WTypes,
        name = "WType",
        description = "Type of WMesh",
        default = 'NONE'
    )

def unregister():
    unregisterWPlane()
    unregisterWBox()
    unregisterWScrew()
    unregisterWRing()
    unregisterWTube()
    unregisterWSphere()

    bpy.utils.unregister_class(WAddPanel)
    bpy.utils.unregister_class(WAddMenu)
    bpy.utils.unregister_class(ConvertWMesh)
    bpy.utils.unregister_class(WEditPanel)

    bpy.types.INFO_MT_mesh_add.remove(draw_addMenu)

    del bpy.types.Mesh.WType

if __name__ == "__main__":
    register()
