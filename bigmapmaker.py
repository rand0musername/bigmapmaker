import argparse
from screenshotter import Screenshotter
from stitcher import Stitcher 

def main():
    parser = argparse.ArgumentParser(description='A small utility that creates a big map.')

    parser.add_argument('--start', required=True, help='top-left point of the region of interest (comma-separated lat/lng pair)')
    parser.add_argument('--end', required=True, help='bottom-right point of the region of interest (comma-separated lat/lng pair)')
    parser.add_argument('--zoom', type=int, required=True, help='zoom level')
    parser.add_argument('--out', required=True, help='output directory')
    parser.add_argument('--transit', help='enable transit layer', action='store_true')

    args = parser.parse_args()
    start = map(float, args.start.split(','))
    end = map(float, args.end.split(','))
    tile_size_px = 500

    print('[bigmapmaker] Starting.')
    screenshotter = Screenshotter(start, end, args.zoom, args.out, args.transit, tile_size_px)
    screenshotter.fetch_tiles() 
    print('[bigmapmaker] Done with fetching, moving on to stitching.')
    stitcher = Stitcher(args.out, tile_size_px)
    stitcher.stitch() 
    print('[bigmapmaker] Done.')

if __name__ == '__main__':   
        main()