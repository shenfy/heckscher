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

    use_ascii: bpy.props.BoolProperty(
        name="ASCII",
        description="Export ASCII instead of binary",
        default=False
    )

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

    use_color_source: bpy.props.EnumProperty(
        items=(('color', 'Color', 'Vertex Color'),
               ('weight', 'Weight', 'Vertex Weight')),
        name='Source',
        description='Source of vertex color'
    )

    use_color_attr: bpy.props.StringProperty(
        name='Name',
        description='Name of the color attribute/vertex group to export',
        default=''
    )

    use_uvs: bpy.props.BoolProperty(
        name='Tex Coords',
        description='Export texture coordinates',
        default=False
    )

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
        use_colors = False
        if self.use_colors:
            if self.use_color_source == 'color':
                if self.use_color_attr in tmp_mesh.color_attributes:
                    use_colors = True

                    col_attr = tmp_mesh.color_attributes[self.use_color_attr]
                    col_domain = col_attr.domain
                    C = [[0, 0, 0] for _ in range(num_verts)]

                    if col_domain == 'POINT':
                        for vid in range(num_verts):
                            C[vid] = [int(c * 255) for c in col_attr.data[vid].color[:-1]]

            elif self.use_color_source == 'weight':
                if self.use_color_attr in ob.vertex_groups:
                    use_colors = True

                    vg = ob.vertex_groups[self.use_color_attr]
                    col_domain = 'POINT'

                    C = [[0, 0, 0] for _ in range(num_verts)]
                    for vid in range(num_verts):
                        try:
                            weight = vg.weight(vid)
                            C[vid] = [int(weight * 255), 0, 0]
                        except:
                            pass

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

                if use_colors and col_domain == 'CORNER':
                    C[vid] = [int(c * 255) for c in col_attr.data[lid].color[:-1]]

                if use_uvs:
                    ST[vid] = [st for st in uv_layer.data[lid].uv]

            F.append(fvids)

        saveply.write_ply(self.filepath, V, F, C, N, ST, self.use_ascii)

        return {'FINISHED'}

def menu_export(self, context):
    default_path = os.path.splitext(bpy.data.filepath)[0] + '.ply'
    self.layout.operator(HeckscherPLYExport.bl_idname, text='PLY (Heckscher)')

if __name__ == '__main__':
    pass
