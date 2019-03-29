import glob
import re
import os
from PIL import Image

class Stitcher:
    def __init__(self, dir, tile_size):
        self.tile_size = tile_size
        self.dir = dir

    def stitch(self):
        # Finds all tile files in the given dir and stitches them into a big map.
        bigmap_filename = os.path.join(self.dir, 'bigmap.jpg')
        print('[stitcher] Starting the stitching process.')
        filenames = glob.glob(os.path.join(self.dir, 'tile_*.png'))

        # Extracts (row, col) pairs from filenames.
        rows_cols = [re.search('(\d{3}),(\d{3})', f).groups(f) for f in filenames]
        nb_tiles = len(rows_cols)
        rows, cols = zip(*[(int(r), int(c)) for (r, c) in rows_cols])
        nb_rows, nb_cols = max(rows)+1, max(cols)+1
        print('[stitcher] Found {} rows and {} columns.'.format(nb_rows, nb_cols))
        if nb_tiles != nb_rows * nb_cols:
            print('[stitcher] There should therefore be exactly {} tiles, but {} tiles were found. Aborting.'
                  .format(nb_rows * nb_cols), nb_tiles)
            return
        
        # Pastes tiles onto the big map.
        bigmap = Image.new('RGB', (self.tile_size*nb_cols, self.tile_size*nb_rows))
        print('[stitcher] Starting to paste tiles onto the big map.')
        tiles_pasted = 0
        for filename, row, col in zip(filenames, rows, cols):
            with Image.open(filename) as tile:
                # box = (left, upper, right, lower)
                box = (self.tile_size* col, self.tile_size * row, 
                       self.tile_size * (col + 1), self.tile_size * (row + 1))
                bigmap.paste(tile, box)
            tiles_pasted += 1
            print('[stitcher] Pasted {}/{} tiles.'.format(tiles_pasted, nb_tiles), end='\r')

        # Saves the big map.
        print('[stitcher] Saving the big map and compressing (this can take a while).')
        bigmap.save(bigmap_filename, quality=95, optimize=True, progressive=True)
        print('[stitcher] Saved the big map to {}, done.'.format(bigmap_filename))

