import os
import struct

def write_ply(fn, V, F, C, N, ST, ascii):
    n = len(V)
    m = len(F)
    has_vcolor = C is not None
    has_normal = N is not None
    has_texcoord = ST is not None
    encoding = 'ascii' if ascii else 'binary_little_endian'

    with open(fn, 'wb') as outfile:

        # write header
        outfile.write(b'ply\n')
        outfile.write('format {} 1.0\n'.format(encoding).encode('utf-8'))
        outfile.write(b'comment Exported from Blender using Heckscher addon\n')

        outfile.write('element vertex {}\n'.format(n).encode('utf-8'))
        outfile.write(b'property float x\nproperty float y\nproperty float z\n')
        if has_normal:
            outfile.write(b'property float nx\nproperty float ny\nproperty float nz\n')
        if has_texcoord:
            outfile.write(b'property float u\nproperty float v\n')
        if has_vcolor:
            outfile.write(b'property uint8 red\nproperty uint8 green\nproperty uint8 blue\n')

        outfile.write('element face {}\n'.format(m).encode('utf-8'))
        outfile.write(b'property list uchar int vertex_indices\n')
        outfile.write(b'end_header\n')

        if ascii:  # ascii
            # write vertex data
            for idx, v in enumerate(V):
                outfile.write('{:.7f} {:.7f} {:.7f}'.format(*v).encode('utf-8'))
                if has_normal:
                    outfile.write(' {:.7f} {:.7f} {:.7f}'.format(*N[idx]).encode('utf-8'))
                if has_texcoord:
                    outfile.write(' {:.7f} {:.7f}'.format(*ST[idx]).encode('utf-8'))
                if has_vcolor:
                    outfile.write(' {} {} {}'.format(*C[idx]).encode('utf-8'))
                outfile.write(b'\n')

            # write faces
            for face in F:
                v_count = len(face)
                format_str = ' '.join(['{}'] * (v_count + 1)) + '\n'
                outfile.write(format_str.format(v_count, *face).encode('utf-8'))

        else:  # binary
            # write vertex data
            for idx, v in enumerate(V):
                outfile.write(struct.pack('<3f', *v))
                if has_normal:
                    outfile.write(struct.pack('<3f', *N[idx]))
                if has_texcoord:
                    outfile.write(struct.pack('<2f', *ST[idx]))
                if has_vcolor:
                    outfile.write(struct.pack('<3B', *C[idx]))

            # write faces
            for face in F:
                v_count = len(face)
                outfile.write(struct.pack('<B{}I'.format(v_count), v_count, *face))
