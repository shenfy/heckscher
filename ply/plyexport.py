import os
import bpy, bpy_extras
import bmesh
from . import saveply

class HeckscherPLYExport(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    """Export triangular mesh to PLY while preserving vertex order."""

    bl_idname = 'heckscher.export_ply'
    bl_label = 'Export'

    filename_ext = '.ply'

    filter_glob: bpy.props.StringProperty(default='*.ply', options={'HIDDEN'})

    use_normals: bpy.props.BoolProperty(
        name="Normals",
        description="Export vertex normals",
        default=False
    )

    use_colors: bpy.props.BoolProperty(
        name='Vertex Colors',
        description="Export the active vertex color layer",
        default=False
    )

    use_uvs: bpy.props.BoolProperty(
        name='Tex Coords',
        description='Export texture coordinates',
        default=False)

    def execute(self, context):
        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode='OBJECT')

        if len(context.selected_objects) == 0:
            return {'FINISHED'}

        ob = context.selected_objects[0]
        me = ob.to_mesh()
        me.transform(ob.matrix_world)

        bm = bmesh.new()
        bm.from_mesh(me)

        if self.use_normals:
            bm.normal_update()

        tmp_mesh = bpy.data.meshes.new('heckscher_export_ply_data')
        bm.to_mesh(tmp_mesh)
        bm.free()

        V = []
        for v in tmp_mesh.vertices:
            V.append([v.co.x, v.co.y, v.co.z])
        num_verts = len(V)

        N = None
        if self.use_normals:
            N = []
            for n in tmp_mesh.vertex_normals:
                N.append([n.vector.x, n.vector.y, n.vector.z])

        C = None
        use_colors = self.use_colors and len(tmp_mesh.vertex_colors) > 0
        if use_colors:
            col_layer = tmp_mesh.vertex_colors.active
            C = [[0, 0, 0] for _ in range(num_verts)]

        ST = None
        use_uvs = self.use_uvs and len(tmp_mesh.uv_layers) > 0
        if use_uvs:
            uv_layer = tmp_mesh.uv_layers.active
            ST = [[0.0, 0.0] for _ in range(num_verts)]

        F = []
        for poly in tmp_mesh.polygons:
            fvids = []
            for lid in poly.loop_indices:
                vid = tmp_mesh.loops[lid].vertex_index
                fvids.append(vid)

                if use_colors:
                    C[vid] = [int(c * 255) for c in col_layer.data[lid].color[:-1]]

                if use_uvs:
                    ST[vid] = [st for st in uv_layer.data[lid].uv]

            F.append(fvids)

        saveply.write_ply(self.filepath, V, F, C, N, ST)

        return {'FINISHED'}

def menu_export(self, context):
    default_path = os.path.splitext(bpy.data.filepath)[0] + '.ply'
    self.layout.operator(HeckscherPLYExport.bl_idname, text='PLY (Heckscher)')

if __name__ == '__main__':
    pass
