# Persistence Mapping for Solar Imagery

Persistence Mapping is a tool for tracking the evolution of solar prominences. When a pixel reaches a maximum value, that value "persists" into subsequent frames until it is exceeded, resulting in a final image which traces out the full motion of the prominence.

## Files

`persistence.py`
Generates a persistence map, in the form of a movie and the final image. Map will be in the colormap associated with the data.

`persistence_color.py`
Generates a persistence map, but where each pixel is colored according to the time it reaches its maximum value.

## Required Selections

The following selections will need to be set manually, by editing the top section of the file.

### Required for both files:
- `folder`: enter the path to the data here
- `date`: enter the date of the event, in the format 'YYYYMMDD'
- wavelength: for colormap selection and file naming
- x and y limits: the limits (in pixels) to which the data will be cropped
- scaling minimum and maximum values: all data between these values will be scaled according to the [bytscl](https://www.l3harrisgeospatial.com/docs/BYTSCL.html) procedure. Adjustment of these values may be necessary to achieve optimal results.

### Required for only `persistence.py`:
- telescope & instrument: this will enable correct selection of colormap

### Required for only `persistence_color.py`:
- colormap: recommended perceptually uniform colormaps include `viridis`, `plasma`, and`magma`. `jet` is a commonly used rainbow map.
