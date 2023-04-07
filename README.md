# heckscher
Blender add-ons and tools for geometry processing.

| Addon Names | Dir/Filename | Description |
| ------ | -------- | ------- |
| Select Elements | selectel.py | Selected element (vertex/face) <-> Index list |
| PLY Exporter | ply (dir) | Write PLY: preserves vertex order, select color attribute |

## Installation
### Method 1
- Create zip of the subfolder or file of the addon you would like to install.
Under Linux, use the package.sh to create zip archives under the `release` folder .
```bash
$ sudo apt install -y zip
$ bash package.sh
```
The release section in this repository may also contain packaged files you can download and install.

- Use the Blender GUI menu **Edit > Preferences > Add-ons > Install...** to install individual addons.

### Method 2
Simply copy the subfolders or files of the add-on in this repository into your script folder.

Under Linux, it is something like `/home/{username}/.config/blender/3.1/scripts/addons/`

Under Windows, it is something like `C:\Users\{username}\AppData\Roaming\Blender Foundation\Blender\3.1\scripts\addons\`, or equivalently `%AppData%\Blender Foundation\Blender\3.1\scripts\addons\`

Then find and enable them in **Edit > Preferences > Add-ons** by searching the corresponding addon names as listed above.