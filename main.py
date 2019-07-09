import os
from itertools import product
import rasterio as rio
from rasterio import windows

in_path = 'resources'
input_filename = 'marbles.tif'

out_path = 'out'
output_filename = 'tile_{}-{}.tif'

def get_tiles(ds, width, height, overlap, total_width, total_height):
    nols, nrows = ds.meta['width'], ds.meta['height']
    offsets = product(range(0, nols, width), range(0, nrows, height))
    col_offsets = []
    row_offsets = []
    new_offsets_row = []
    new_offsets_col = []
    overlap_off = width - overlap
    for col, row in offsets:
        col_offsets.append(col)
        row_offsets.append(row)

    row_mem = 0
    for row in row_offsets:

        if row == 0:
            new_offsets_row.append(row_mem)
        else:
            row_mem += overlap_off
            if row_mem > total_width:
                break
            new_offsets_row.append(row_mem)
    print(new_offsets_row)
    print(total_width)


    col_mem = 0
    for col in list(set(col_offsets)):
        if col == 0:
            new_offsets_col.append(col_mem)
        else:
            col_mem += overlap_off
            if col_mem > total_width:
                break
            new_offsets_col.append(col_mem)
    print(new_offsets_col)
    print(total_height)

    big_window = windows.Window(col_off=0, row_off=0, width=nols, height=nrows)
    for col_off, row_off in  offsets:
        window =windows.Window(col_off=col_off, row_off=row_off, width=width, height=height).intersection(big_window)
        transform = windows.transform(window, ds.transform)
        yield window, transform


with rio.open(os.path.join(in_path, input_filename)) as inds:
    dim = 100
    overlap = 10
    tile_width, tile_height = dim, dim

    meta = inds.meta.copy()

    for window, transform in get_tiles(inds, dim, dim, overlap, inds.width, inds.height ):
        print(window)
        meta['transform'] = transform
        meta['width'], meta['height'] = window.width, window.height
        outpath = os.path.join(out_path,output_filename.format(int(window.col_off), int(window.row_off)))
        with rio.open(outpath, 'w', **meta) as outds:
            outds.write(inds.read(window=window))