bl_info = {
    "name": "Heckscher PLY Exporter",
    "author": "Fangyang Shen",
    "version": (0, 1, 0),
    "blender": (3, 0, 0),
    "location": "File > Export",
    "description": "Export PLY mesh while preserving vertex order",
    "category": "Import-Export",
}

if "bpy" in locals():
    import importlib
    if "plyexport" in locals():
        importlib.reload(plyexport)
else:
    import bpy
    from . import plyexport

classes = (plyexport.HeckscherPLYExport,)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_file_export.append(plyexport.menu_export)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    bpy.types.TOPBAR_MT_file_export.remove(plyexport.menu_export)

if __name__ == '__main__':
    register()
