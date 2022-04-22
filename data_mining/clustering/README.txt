Files contained in this framework:

  clustering.py: This is where lloyds and kmedoids are to be implemented. DO 
                 NOT CHANGE THE FUNCTION SIGNATURES
  
  testcases.py: Provides a few test cases you can run to test your 
                implementation of lloyds and kmedoids. If you just run the 
                script it will open a (text-based) menu where you can select 
                which test case to run.
                
  colorpalette.py: Is a neat application of clustering to calculate color
                   palettes of images. If your implementation of lloyd is 
                   working correctly, you can use colorpalette.py to add 
                   a color palette to any (supported) image, or even redraw
                   the image with this new/reduced color palette. Requires
                   Pillow (pip install pillow)!
  
  testdata.csv: Is a (randomly) generated csv file, i.e. the data has no 
                meaning. Columns x1, x2 are drawn from one of three clusters 
                (recorded in cls1), columns x3, x4 from one of two clusters 
                (recorded in cls2). The categorical attributes cat1-cat4 are 
                chosen from two different probability distributions, 
                corresponding to two clusters, recorded in cls3, and similarly
                for the five binary attributes bin1-bin5, recorded in cls4. 
                
  make_csv.py: Is a script that can generate files like testdata.csv, in case 
               you are curious or want to generate more test cases.
                
  mona.jpg, flowers.jpg: These are two image files you can use with 
                         colorpalette.py to test your implementation.
                         Of course you can also use your own!
                         
Once you have lloyds implemented, try the following:

python testcases.py 01q

You should first see several points in two colors with cluster centers very far
outside the actual data. When you close the plot, your implementation of lloyds 
will be called for one step and another plot will be shown where the cluster
centers should have moved slightly closer to the data.

python testcases.py 02q

This uses the same data, but performs five steps (and only shows you the final 
result. In this plot, your cluster centers should be firmly in the top left and 
bottom right parts of the data.
Either of these tests should not take more than a second or two to run.

python colorpalette.py mona.jpg

This will run a bit longer (about 15 seconds on my machine/with my 
implementation), but when it is done you should get a window with a picture of 
Mona, with a 5-color palette at the top of the picture (one of the squared may 
be hard to see because it blends in with the background).

python colorpalette.py mona.jpg -r

Will run about the same amount of time, but instead of a picture with the 
color palette, you should get an image of Mona where the colors are replaced 
with the palette values (i.e. there will only be 5 different colors in the 
picture).

If all of these tests worked, explore the other test cases more, before you 
apply the algorithm(s) to your own data.