from PIL import Image
import clustering
import sys
import argparse
import math

PALETTE_SIZE = 30

TOP = 0
LEFT = 1

# Calculate the distance between two colors
def diff3(a,b):
    return (a[0]-b[0])**2 + (a[1] - b[1])**2 + (a[2] - b[2])**2

def main(fname, k=5, width=256, height=256, location=TOP, redraw=True):
    # Open given file
    with Image.open(fname) as im:
        # resize, preserving aspect ratio
        im.thumbnail((width,height))
        data = im.getdata()
        # calculate clusters: which pixels are the most similar, and what is the mean value of each cluster
        centers = clustering.lloyds(data, k, [0,1,2], n=20)
        if not redraw:
            # Show cluster centers as color palette
            for i,c in enumerate(centers):
                pal = Image.new("RGB", (PALETTE_SIZE,PALETTE_SIZE), tuple(map(lambda x: int(round(x)), c)))
                if location == TOP:
                    im.paste(pal, box=(i*PALETTE_SIZE,0))
                else:
                    im.paste(pal, box=(0,i*PALETTE_SIZE))
        else:
            # Calculate new pixel values based on which center each (old) pixel value is closest to
            newdata = []
            for d in data:
                mind = None 
                val = None 
                for c in centers:
                    delta = diff3(d,c)
                    if mind is None or delta < mind:
                        mind = delta 
                        val = c
                newdata.append(tuple(map(lambda x: int(round(x)), val)))
            im.putdata(newdata)
        im.show()
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    parser.add_argument("-k", "--clusters", type=int,
                         help="How many clusters to calculate.", default=5)
    parser.add_argument("-w", "--width", type=int,
                         help="Rescale image to width (aspect ratio will be preserved)", default=256)
    parser.add_argument("-e", "--height", type=int,
                         help="Rescale image to height (aspect ratio will be preserved)", default=256)
    parser.add_argument("-l", "--left", action="store_const", const=LEFT, default=TOP,
                         help="Put the palette along the left edge of the image rather than at the top")
    parser.add_argument("-r", "--redraw", action="store_true",
                         help="Redraw image with calculated palette instead of just showing palette.", default=False)
    args = parser.parse_args()

    main(args.filename, k=args.clusters, width=args.width, height=args.height, location=args.left, redraw=args.redraw)
