#___________________________________/
#___Author:_________Vit_Prochazka___/
#___Created:________15.12.2015______/
#___Last_modified:__17.08.2017______/
#___Version:________0.3_____________/
#___________________________________/

import bpy
from mathutils import Vector

def create_mesh_object(context, verts, edges, faces, name):

    # Create new mesh
    mesh = bpy.data.meshes.new(name)

    # Make a mesh from a list of verts/edges/faces.
    mesh.from_pydata(verts, edges, faces)

    # Update mesh geometry after adding stuff.
    mesh.update()

    from bpy_extras import object_utils
    return object_utils.object_data_add(context, mesh, operator=None)

def bridgeLoops(loop1, loop2, close):
    faces = []

    if len(loop1) != len(loop2):
        return None

    for i in range(len(loop1) -1):
        face = (loop1[i], loop1[i+1], loop2[i+1], loop2[i])
        faces.append(face)

    if close:
        faces.append((loop1[-1], loop1[0], loop2[0], loop2[-1]))

    return faces

#subsurf
def findEdges(faces):
    edges = [] #edge(vertsIDs)
    borders = [] #border(edgesIDs)

    for face in faces:
        polys = len(face)
        border = []
        for i in range(polys):
            if i == polys -1:
                edgeA, edgeB = face[i], face[0]
            else:
                edgeA, edgeB = face[i], face[i+1]
            #sort indexes
            if edgeA > edgeB:
                edgeA, edgeB = edgeB, edgeA
            newEdge = (edgeA, edgeB)
            #is it a really NEW edge?
            if newEdge not in edges:
                border.append(len(edges))
                edges.append(newEdge)
            else:
                border.append(edges.index(newEdge))

        borders.append(border)

    return edges, borders

def VectorMedian (IDs, verts):
    outVec = Vector((0,0,0))
    for IDX in IDs:
        outVec += verts[IDX]
    outVec /= len(IDs)
    return outVec

def subdivide(verts, edges, faces, tris):
    Sedges, borders = findEdges(faces)
    NewFaces = []
    vertIDsOffset = len(verts)
    #midpoints
    midVerts = []
    for line in Sedges:
        midVerts.append((verts[line[0]] + verts[line[1]]) / 2)

    verts.extend(midVerts)

    i = 0
    for border in borders:
        face = faces[i]
        i += 1

        if not tris:
            centerVec = VectorMedian(face, verts)
            centerVecID = len(verts)
            verts.append(centerVec)

            for b in range(len(border)):
                NewFaces.append((
                    face[b],
                    border[b] + vertIDsOffset,
                    centerVecID,
                    border[b-1] + vertIDsOffset
                ))
        else:
            for b in range(len(border)):
                NewFaces.append((
                    face[b],
                    border[b] + vertIDsOffset,
                    border[b-1] + vertIDsOffset
                ))
            NewFaces.append((
                border[0] + vertIDsOffset,
                border[1] + vertIDsOffset,
                border[2] + vertIDsOffset
            ))

    return verts, edges, NewFaces
