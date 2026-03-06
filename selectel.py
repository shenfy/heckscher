bl_info = {
    "name": "Element Selection",
    "author": "Fangyang Shen",
    "version": (0, 1, 0),
    "blender": (3, 0, 0),
    "description": "Show selected or select vertices and faces",
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

def get_selected_faces(obj_data, is_edit_mode) -> list[int]:
    if is_edit_mode:
        edit_mesh = bmesh.from_edit_mesh(obj_data)
        indices = [f.index for f in edit_mesh.faces if f.select]
    else:
        indices = [f.index for f in obj_data.polygons if f.select]
    return indices

class ElementSelectionPropertyGroup(bpy.types.PropertyGroup):
    elements_2_select: bpy.props.StringProperty(name='Elements to Select')

class CopySelectedElementsOperator(bpy.types.Operator):
    """Copy the list of selected vertex indices to clipboard."""
    bl_idname = 'heckscher.sel_elements_clipboard'
    bl_label = 'Copy Selected Element Ids to Clipboard'

    content: bpy.props.StringProperty(default='')

    def execute(self, context):
        context.window_manager.clipboard = str(self.content)
        return {'FINISHED'}

def parse_ids_str(ids_str: str) -> set[int]:
    """Parse string to set of integer ids."""
    for char in ['[', ']', ',', '\t', '\n']:
        ids_str = ids_str.replace(char, ' ')
    return {int(v) for v in ids_str.split()}

def select_elements_by_ids(context, ids_str: str) -> bool:
    """Select elements based on parsed ids_str."""
    try:
        id_set = parse_ids_str(ids_str)
    except ValueError:
        return False
    
    select_mode = tuple(bpy.context.scene.tool_settings.mesh_select_mode)  # (v, e, f)
    obj = context.object

    if obj.mode == 'EDIT':
        edit_mesh = bmesh.from_edit_mesh(obj.data)
        for edge in edit_mesh.edges:
            edge.select = False
        if select_mode[2]:  # select face
            for v in edit_mesh.verts:
                v.select = False
            for idx, face in enumerate(edit_mesh.faces):
                face.select_set(True if idx in id_set else False)
        else:  # select verts
            for face in edit_mesh.faces:
                face.select = False
            for idx, v in enumerate(edit_mesh.verts):
                v.select_set(True if idx in id_set else False)

        edit_mesh.select_flush(True)
        bmesh.update_edit_mesh(obj.data, loop_triangles=False, destructive=False)
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode='EDIT')
    else:
        for edge in obj.data.edges:
            edge.select = False
        if select_mode[2]:  # select face
            for v in obj.data.vertices:
                v.select = False
            for idx, poly in enumerate(obj.data.polygons):
                poly.select = True if idx in id_set else False
        else:  # select vertex
            for poly in obj.data.polygons:
                poly.select = False
            for idx, v in enumerate(obj.data.vertices):
                v.select = True if idx in id_set else False
    return True

class SelectElementsByIdOperator(bpy.types.Operator):
    """Select all vertices whose index is in the given comma separated list."""

    bl_idname = 'heckscher.sel_verts_by_id'
    bl_label = 'Select Vertices in the Given Id List'

    def execute(self, context):
        obj = context.object
        ids_str = obj.vertex_selection_prop_grp.elements_2_select
        if not select_elements_by_ids(context, ids_str):
            self.report({'ERROR'}, "Input does not contain valid integer indices.")
            return {'CANCELLED'}
        return {'FINISHED'}

class SelectElementsByClipboardOperator(bpy.types.Operator):
    """Select all vertices whose index is in the clipboard."""

    bl_idname = 'heckscher.sel_verts_by_clipboard'
    bl_label = 'Select Vertices from Clipboard'

    def execute(self, context):
        ids_str = context.window_manager.clipboard
        if not select_elements_by_ids(context, ids_str):
            self.report({'ERROR'}, "Clipboard does not contain valid integer indices.")
            return {'CANCELLED'}
        return {'FINISHED'}

class selectedElementsPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Selected Elements"
    bl_idname = "heckscher.sel_vert_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def draw(self, context):
        layout = self.layout

        is_edit_mode = bpy.context.object.mode == 'EDIT'
        select_mode = tuple(bpy.context.scene.tool_settings.mesh_select_mode)  # (v, e, f)
        select_mode_text = 'faces' if select_mode[2] else 'vertices'

        obj = context.object
        if select_mode[2]:
            indices = get_selected_faces(obj.data, is_edit_mode)
        else:
            indices = get_selected_verts(obj.data, is_edit_mode)

        selected_count = len(indices)
        row = layout.row()
        row.label(text='Selected {} count: {}'.format(select_mode_text, selected_count))

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
        button = row.operator(CopySelectedElementsOperator.bl_idname,
            text='Copy to Clipboard', icon='COPYDOWN')
        button.content = str(indices)

        row = layout.row()
        row.label(text='Select Elements by Index:')

        row = layout.row()
        row.prop(obj.vertex_selection_prop_grp, 'elements_2_select', text='')

        row = layout.row()
        button = row.operator(SelectElementsByIdOperator.bl_idname,
            text='Select {}'.format(select_mode_text), icon='SELECT_SET')

        row = layout.row()
        button = row.operator(SelectElementsByClipboardOperator.bl_idname,
            text='Select {} from Clipboard'.format(select_mode_text), icon='PASTEDOWN')


def register():
    bpy.utils.register_class(CopySelectedElementsOperator)
    bpy.utils.register_class(SelectElementsByIdOperator)
    bpy.utils.register_class(SelectElementsByClipboardOperator)
    bpy.utils.register_class(selectedElementsPanel)
    bpy.utils.register_class(ElementSelectionPropertyGroup)
    bpy.types.Object.vertex_selection_prop_grp =\
        bpy.props.PointerProperty(type=ElementSelectionPropertyGroup)

def unregister():
    del bpy.types.Object.vertex_selection_prop_grp
    bpy.utils.unregister_class(CopySelectedElementsOperator)
    bpy.utils.unregister_class(SelectElementsByIdOperator)
    bpy.utils.unregister_class(SelectElementsByClipboardOperator)
    bpy.utils.unregister_class(selectedElementsPanel)
    bpy.utils.unregister_class(ElementSelectionPropertyGroup)

if __name__ == "__main__":
    register()
