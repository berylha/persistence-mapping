import os
import numpy as np
from astropy.io import fits
import sunpy.visualization.colormaps as cm
import matplotlib.pyplot as plt
import imageio

# EDIT THIS SECTION ###########################################################
# enter directory to data here
folder = 'path/to/files/goes/here/'
# choose date in format 'YYYYMMDD'
date = '20120422'
# choose wavelength in Angstroms (e.g. 193, 304)
wv = '304'
# x and y limits
x0 = 2048
x1 = 4096
y0 = 2048
y1 = 4096
# enter minimum and maximum values for scaling here
# enter None to choose the minimum or maximum value in the array
MN = 0
MX = 60
# choose colormap
cmap_name = 'viridis'
###############################################################################

def bytscl(arr, mn=None, mx=None):
    # Scales values between mn<x<mx to 0.0<x<1.0
    scarr = np.zeros(arr.shape)
    if mn==None:
        mn = np.min(arr)
    if mx==None:
        mx = np.max(arr)
    zz = (arr < mn)
    aa = (arr > mx)
    scarr[zz] = 0.0
    scarr[aa] = 1.0
    scarr[(~aa)*(~zz)] = (arr[(~aa)*(~zz)] - mn) / (mx - mn)
    return scarr

# choose files in folder
filenames = sorted([f for f in os.listdir(folder) if f.endswith('.fits')])

# select colormap
cmap = plt.get_cmap(cmap_name)
# define color array with one colormap value for each timestep
carr = np.array([cmap(i, bytes=True) for i in np.linspace(0, 1, len(filenames))])

# start with first file
with fits.open(folder + filenames[0]) as f:
    npmap = f[1].data[::-1]
    exptime = f[1].header['EXPTIME']
# crop to submap
smap1 = npmap[y0:y1, x0:x1]
# normalize
smap1 = smap1/exptime
smap1 = bytscl(smap1, mn=MN, mx=MX)

# initialize array in which to store persistence data
plist = np.zeros((len(filenames), y1-y0, x1-x0, 4), dtype='uint8')
# color first image by first color in colormap
plist[0] = np.array([[idx*carr[0] for idx in row] for row in smap1])
# reset opacity to full
plist[0,:,:,3] = 255

# iterate through files
for i, filename in enumerate(filenames[1:]):
    if i % 10 == 0:
        print(f'Progress: {i}/{len(filenames)} images')
    smap0 = smap1
    # open file as numpy array
    with fits.open(folder + filename) as f:
        npmap = f[1].data[::-1]
        exptime = f[1].header['EXPTIME']
    # use defined limits to create submap
    smap1 = npmap[y0:y1, x0:x1]
    # normalize
    smap1 = smap1/exptime
    smap1 = bytscl(smap1, mn=MN, mx=MX)
    # perform persistence mapping operation
    gmap = (smap1 > smap0)
    smap1[~gmap] = smap0[~gmap]
    # color pixels which have not increased in value by previous color
    plist[i+1][~gmap] = plist[i][~gmap]
    # color pixels which have increased in brightness by ith color in colormap
    plist[i+1][gmap] = np.array([idx*carr[i+1] for idx in smap1[gmap]])
    # reset opacity to full
    plist[i+1,:,:,3] = 255

# save final image and full movie
imageio.imwrite(f'{date}_{wv}_color_{cmap_name}.png', plist[-1])
imageio.mimwrite(f'{date}_{wv}_color_{cmap_name}.mp4', plist, fps=12)
