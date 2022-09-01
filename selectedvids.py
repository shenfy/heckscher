bl_info = {
    "name": "Vertex Selection",
    "blender": (3, 0, 0),
    "category": "Object",
}

import bpy, bmesh
import textwrap

def get_selected_verts(obj_data, is_edit_mode) -> list[int]:
    if is_edit_mode:
        edit_mesh = bmesh.from_edit_mesh(obj_data)
        indices = [v.index for v in edit_mesh.verts if v.select]
    else:
        indices = [v.index for v in obj_data.vertices if v.select]
    return indices

class VertexSelectionPropertyGroup(bpy.types.PropertyGroup):
    verts_2_select: bpy.props.StringProperty(name='VIDs to Select')

class CopySelectedVertsOperator(bpy.types.Operator):
    """Copy the list of selected vertex indices to clipboard."""
    bl_idname = 'heckscher.sel_vert_clipboard'
    bl_label = 'Copy Selected VIDs to Clipboard'

    content: bpy.props.StringProperty(default='')

    def execute(self, context):
        context.window_manager.clipboard = str(self.content)
        return {'FINISHED'}

class SelectVerticesByIdOperator(bpy.types.Operator):
    """Select all vertices whose index is in the given comma separated list."""

    bl_idname = 'heckscher.sel_verts_by_id'
    bl_label = 'Select Vertices in the Given Id List'

    def execute(self, context):
        obj = context.object
        vids_str = obj.vertex_selection_prop_grp.verts_2_select
        vids_str = ''.join(filter(lambda x: x not in ['[', ']', '\t'], vids_str))
        vids = set([int(v) for v in filter(lambda x: len(x) != 0, vids_str.split(','))])

        if obj.mode == 'EDIT':
            edit_mesh = bmesh.from_edit_mesh(obj.data)
            for face in edit_mesh.faces:
                face.select = False
            for edge in edit_mesh.edges:
                edge.select = False
            for idx, v in enumerate(edit_mesh.verts):
                v.select_set(True if idx in vids else False)
            edit_mesh.select_flush(True)
            bmesh.update_edit_mesh(obj.data, loop_triangles=False, destructive=False)
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.mode_set(mode='EDIT')
        else:
            for poly in obj.data.polygons:
                poly.select = False
            for edge in obj.data.edges:
                edge.select = False
            for idx, v in enumerate(obj.data.vertices):
                v.select = True if idx in vids else False
        return {'FINISHED'}

class SelectedVertsPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Selected Vertices"
    bl_idname = "heckscher.sel_vert_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def draw(self, context):
        layout = self.layout

        is_edit_mode = bpy.context.object.mode == 'EDIT'

        obj = context.object
        indices = get_selected_verts(obj.data, is_edit_mode)

        selected_count = len(indices)
        row = layout.row()
        row.label(text='Selected vertex count: {}'.format(selected_count))

        text = ' '.join([str(vid) for vid in indices])
        wrapper = textwrap.TextWrapper(width=40)
        text = wrapper.wrap(text=text)

        for idx, line in enumerate(text):
            row = layout.row(align=True)
            row.alignment = 'EXPAND'
            if idx >= 6:
                row.label(text='... (too many to display)')
                break
            else:
                row.label(text=line)

        row = layout.row()
        button = row.operator(CopySelectedVertsOperator.bl_idname,
            text='Copy to Clipboard', icon='COPYDOWN')
        button.content = str(indices)

        row = layout.row()
        row.label(text='Select Vertices by Index:')

        row = layout.row()
        row.prop(obj.vertex_selection_prop_grp, 'verts_2_select', text='')

        row = layout.row()
        button = row.operator(SelectVerticesByIdOperator.bl_idname,
            text='Select Multiple Vertices', icon='SELECT_SET')


def register():
    bpy.utils.register_class(CopySelectedVertsOperator)
    bpy.utils.register_class(SelectVerticesByIdOperator)
    bpy.utils.register_class(SelectedVertsPanel)
    bpy.utils.register_class(VertexSelectionPropertyGroup)
    bpy.types.Object.vertex_selection_prop_grp =\
        bpy.props.PointerProperty(type=VertexSelectionPropertyGroup)

def unregister():
    del bpy.types.Object.vertex_selection_prop_grp
    bpy.utils.unregister_class(CopySelectedVertsOperator)
    bpy.utils.unregister_class(SelectVerticesByIdOperator)
    bpy.utils.unregister_class(SelectedVertsPanel)
    bpy.utils.unregister_class(VertexSelectionPropertyGroup)

if __name__ == "__main__":
    register()
