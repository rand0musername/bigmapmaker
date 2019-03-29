import math
from io import BytesIO
import os
from time import sleep

from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options 

from geo_utils import get_meters_per_px, get_distance, get_latlng_inc_for_px_inc

class Screenshotter:

    def __init__(self, start, end, zoom, out, add_transit, tile_size_px):
        self.tile_size_px = tile_size_px
        self.start_lat, self.start_lng = start
        self.end_lat, self.end_lng = end
        self.zoom = zoom
        self.out = out
        self.add_transit = add_transit

        # Creates the driver and sets viewport size.
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(chrome_options=chrome_options)
        window_size = self.driver.execute_script("""
            return [window.outerWidth - window.innerWidth + arguments[0],
            window.outerHeight - window.innerHeight + arguments[1]];
            """, self.tile_size_px, self.tile_size_px+200)
        self.driver.set_window_size(*window_size)

    # Builds the maps url for given params.
    def build_url(self, lat, lng, zoom, add_transit):
        url = 'https://www.google.com/maps/@{},{},{}z'.format(lat, lng, zoom)
        if add_transit:
            url += '/data=!5m1!1e2'
        url += '?hl=en'
        return url
    
    # Builds a tile filename for given params.
    def build_filename(self, row, col):
        filename = 'tile_({:03d},{:03d}).png'.format(row, col)
        filename = os.path.join(self.out, filename)
        return filename
    
    # Generates (lat, lng) pairs that correspond to tile centres. We are doing this as a 
    # separate step to know how many tiles there are before actually saving them.
    def generate_pairs(self):
        # (Y = row = lat decreasing, X = col = lng increasing)
        # TODO: Translate start and end so that they are exactly in the corners of the image.
        pairs = []
        curr_lng = self.start_lng
        lng_inc = get_latlng_inc_for_px_inc(self.start_lat, self.zoom, self.tile_size_px)[1]
        while True:
            # Initialize a new column.
            curr_col = []
            pairs.append(curr_col)
            curr_lat = self.start_lat
            while True:
                # Save the current (lat, lng) pair.
                curr_col.append((curr_lat, curr_lng))
                # Check if the next row is out of bounds.
                if curr_lat <= self.end_lat:
                    break
                # Go to the next row.
                lat_inc = get_latlng_inc_for_px_inc(curr_lat, self.zoom, self.tile_size_px)[0]
                curr_lat -= lat_inc
            # Check if the next column is out of bounds.
            if curr_lng >= self.end_lng:
                break
            # Go to the next column.
            curr_lng += lng_inc

        return pairs
    
    # Main screenshotter method that saves all tiles specified by input parameters.
    def fetch_tiles(self):
        print('[screenshotter] Starting the screenshotting process.')
        # Create the output directory if it doesn't exist.
        if not os.path.exists(self.out):
            os.makedirs(self.out)
        # Generate all (lat, lng) pairs.
        pairs = self.generate_pairs()
        nb_cols, nb_rows = len(pairs), len(pairs[0])
        nb_tiles = nb_cols * nb_rows
        print('[screenshotter] Done generating pairs. There will be {} tiles in total ({} x {}).'
              .format(nb_tiles, nb_rows, nb_cols))
        tiles_fetched = 0
        for col in range(nb_cols):
            for row in range(nb_rows):
                # Skip fetching if the tile is already present in the directory.
                filename = self.build_filename(row, col)
                if os.path.exists(filename):
                    print("[screenshotter] Tile {}/{}: ({},{}) already exists in the output dir, skipping."
                          .format(tiles_fetched+1, nb_tiles, row, col), end='\r')
                else:
                    # Fetch the tile, crop UI, and save.
                    latlng = pairs[col][row]
                    url = self.build_url(latlng[0], latlng[1], self.zoom, self.add_transit)
                    print("[screenshotter] Fetching tile {}/{}: ({},{}) from url {}"
                          .format(tiles_fetched+1, nb_tiles, row, col, url), end='\r')
                    self.driver.get(url)
                    png = self.driver.get_screenshot_as_png()
                    img = Image.open(BytesIO(png))
                    img = img.crop((0, 100, self.tile_size_px, self.tile_size_px + 100))
                    img.save(filename)
                    sleep(0.1)
                tiles_fetched += 1
        print("\n[screenshotter] Done fetching tiles.")
