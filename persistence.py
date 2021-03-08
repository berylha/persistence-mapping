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
# choose telescope & instrument: either 'sdoaia' or 'euvi' (stereo a/b)
ti = 'sdoaia'
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

# choose folder and files based on input date
filenames = sorted([f for f in os.listdir(folder) if f.endswith('.fits')])

# select colormap
cmap = plt.get_cmap(f'{ti}{wv}')

# start with first file
with fits.open(f'{folder}{filenames[0]}') as f:
    npmap = f[1].data[::-1]
    exptime = f[1].header['EXPTIME']
# crop to submap
smap1 = npmap[y0:y1, x0:x1]
# normalize
smap1 = smap1/exptime
smap1 = bytscl(smap1, mn=MN, mx=MX)

# initialize array in which to store persistence data
plist = np.zeros((len(filenames), y1-y0, x1-x0, 4), dtype='uint8')
plist[0] = cmap(smap1, bytes=True)

# iterate through files
for i, filename in enumerate(filenames[1:]):
    if i % 10 == 0:
        print(f'Progress: {i}/{len(filenames)} images')
    smap0 = smap1
    # open file as numpy array
    with fits.open(f'{folder}{filename}') as f:
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
    # apply colormap
    plist[i+1] = cmap(smap1, bytes=True)

# save final image and full image
imageio.imwrite(f'{date}_{wv}.png', plist[-1])
imageio.mimwrite(f'{date}_{wv}.mp4', plist, fps=12)
