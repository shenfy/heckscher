bl_info = {
    "name": "Selected Vertices",
    "blender": (3, 0, 0),
    "category": "Object",
}

import bpy
import textwrap

def get_selected_verts(obj) -> list[int]:
    indices = [v.index for v in obj.data.vertices if v.select]
    return indices

class CopySelectedVertsOperator(bpy.types.Operator):
    bl_idname = 'heckscher.sel_vert_clipboard'
    bl_label = 'Copy Selected VIDs to Clipboard'

    content: bpy.props.StringProperty(default='')
    
    def execute(self, context):
        context.window_manager.clipboard = str(self.content)
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

        row = layout.row()
        row.label(text="Count: {}".format(len(indices)))
        
        text = ' '.join([str(vid) for vid in indices])
        wrapper = textwrap.TextWrapper(width=40)
        text = wrapper.wrap(text=text)

        for line in text:
            row = layout.row(align=True)
            row.alignment = 'EXPAND'
            row.label(text=line)

        row = layout.row()
        button = row.operator(CopySelectedVertsOperator.bl_idname, text='Copy to Clipboard', icon='COPYDOWN')
        button.content = str(indices)


def register():
    bpy.utils.register_class(CopySelectedVertsOperator)
    bpy.utils.register_class(SelectedVertsPanel)

def unregister():
    bpy.utils.unregister_class(CopySelectedVertsOperator)
    bpy.utils.unregister_class(SelectedVertsPanel)
    
if __name__ == "__main__":
    register()