bl_info = {
    "name": "Vertex Selection",
    "blender": (3, 0, 0),
    "category": "Object",
}

import bpy
import textwrap

def get_selected_verts(obj) -> list[int]:
    indices = [v.index for v in obj.data.vertices if v.select]
    return indices

class VertexSelectionPropertyGroup(bpy.types.PropertyGroup):
    vert_2_select: bpy.props.IntProperty(name='VID to Select')

class CopySelectedVertsOperator(bpy.types.Operator):
    bl_idname = 'heckscher.sel_vert_clipboard'
    bl_label = 'Copy Selected VIDs to Clipboard'

    content: bpy.props.StringProperty(default='')
    
    def execute(self, context):
        context.window_manager.clipboard = str(self.content)
        return {'FINISHED'}

class SelectVertsByIdOperator(bpy.types.Operator):
    bl_idname = 'heckscher.sel_vert_by_id'
    bl_label = 'Select Vertices of the Given Id'

    def execute(self, context):
        obj = context.object
        selected_id = obj.vertex_selection_prop_grp.vert_2_select
        for poly in obj.data.polygons:
            poly.select = False
        for edge in obj.data.edges:
            edge.select = False
        for idx, v in enumerate(obj.data.vertices):
            v.select = True if idx == selected_id else False
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

        obj = context.object
        indices = get_selected_verts(obj)        

        enable_action = bpy.context.object.mode == 'OBJECT'

        selected_count = len(indices)
        row = layout.row()
        row.label(text='Selected: {} vertices'.format(selected_count))
        row.enabled = enable_action

        text = ' '.join([str(vid) for vid in indices])
        wrapper = textwrap.TextWrapper(width=40)
        text = wrapper.wrap(text=text)

        for idx, line in enumerate(text):
            row = layout.row(align=True)
            row.alignment = 'EXPAND'
            row.enabled = enable_action
            if idx >= 6:
                row.label(text='... (too many to display)')
                break
            else:
                row.label(text=line)

        row = layout.row()
        button = row.operator(CopySelectedVertsOperator.bl_idname,
            text='Copy to Clipboard', icon='COPYDOWN')
        button.content = str(indices)
        row.enabled = enable_action

        row = layout.row()
        row.label(text='To Select:')
        row.enabled = enable_action

        row = layout.row()
        col = row.column()
        col.label(text='VID:')
        col = row.column()
        col.prop(obj.vertex_selection_prop_grp, 'vert_2_select', text='')
        row.enabled = enable_action

        row = layout.row()
        button = row.operator(SelectVertsByIdOperator.bl_idname,
            text='Select Vertex', icon='SELECT_SET')
        row.enabled = enable_action


def register():
    bpy.utils.register_class(CopySelectedVertsOperator)
    bpy.utils.register_class(SelectVertsByIdOperator)
    bpy.utils.register_class(SelectedVertsPanel)
    bpy.utils.register_class(VertexSelectionPropertyGroup)
    bpy.types.Object.vertex_selection_prop_grp =\
        bpy.props.PointerProperty(type=VertexSelectionPropertyGroup)

def unregister():
    del bpy.types.Object.vertex_selection_prop_grp
    bpy.utils.unregister_class(CopySelectedVertsOperator)
    bpy.utils.unregister_class(SelectVertsByIdOperator)
    bpy.utils.unregister_class(SelectedVertsPanel)
    bpy.utils.unregister_class(VertexSelectionPropertyGroup)
    
if __name__ == "__main__":
    register()
