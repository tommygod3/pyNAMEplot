import os
from . import namemap
from . import util


def drawMap(n, column, projection=False, lon_bounds=(), lat_bounds=(), lon_axis=[], lat_axis=[],
            scale=(), autoscale=True, caption=None, solid=False, color1='', colormap='', station=(),
            outdir='', outfile='', logos=True, boarder_col='black', sea_col='white', land_col='#D1D1D1',
            grid_col='black'):
    """
    Function will draw a footprint map, most values will not need to be set as defaults are okay.
    :param n: Name obj
    :param column: Column obj
    :param projection: string, 'cyl' by default
    :param lon_bounds: tuple longitudinal boundary
    :param lat_bounds: tuple latitude boundary
    :param lon_axis: tuple longitude axis
    :param lat_axis: tuple latitude axis
    :param scale: tuple
    :param autoscale: bool
    :param caption: string
    :param solid: bool
    :param color1: string
    :param colormap: string
    :param station: tuple
    :param outdir: string
    :param outfile: string
    :param logos: bool
    :param boarder_col: string
    :param sea_col: string
    :param land_col: string
    :param grid_col: string
    :return:
    """
    # Create Map object from NAME data
    m = namemap.Map(n, column=column)

    # Set projection if defined, otherwise cylindrical
    if projection:
        m.setProjection(projection)

    # Set map bounds from config file, otherwise scale by grid file
    if lon_bounds and lat_bounds:
        m.setBounds(lon_bounds, lat_bounds)
    elif lon_bounds:
        m.setBounds(lon_bounds, n.lat_bounds)
    elif lat_bounds:
        m.setBounds(n.lon_bounds, lat_bounds)
    else:
        m.setBounds(n.lon_bounds, n.lat_bounds)

    # Set map axes from config file, else scale by grid file
    if lon_axis and lat_axis:
        lon = [float(i) for i in lon_axis]
        lat = [float(i) for i in lat_axis]
        m.setAxes(lon, lat)
    elif lon_bounds or lat_bounds:
        # The boundaries have been reset so need a sensible grid
        if lon_bounds:
            lon = util.get_axisticks(lon_bounds)
        else:
            lon = n.lon_grid
        if lat_bounds:
            lat = util.get_axisticks(lat_bounds)
        else:
            lat = n.lat_grid
        m.setAxes(lon, lat)
    else:
        m.setAxes(n.lon_grid, n.lat_grid)

    # Set scale if defined, otherwise standard scale
    if scale:
        m.setFixedScale(conc=scale)
    elif autoscale:
        m.setAutoScale(column)

    # Set up data grid
    if caption:
        m.drawBase(caption, fontsize=8, boarder_col=boarder_col, sea_col=sea_col, land_col=land_col, grid_col=grid_col)
    else:
        m.drawBase(m.caption, fontsize=8, boarder_col=boarder_col, sea_col=sea_col, land_col=land_col, grid_col=grid_col)

    # Check for solid colouring flag
    if solid:
        m.solid = True
        if color1:
            m.drawSolid(column, color=color1)
        else:
            m.drawSolid(column)
    elif colormap:  # Plot using colormap
        m.setColormap(colormap)
        m.drawMesh(column)
    else:
        m.setColormap()
        m.drawMesh(column)

    # Add station marker if defined
    if station:
        (station_lon, station_lat) = station
        m.addMarker(float(station_lon), float(station_lat))

    # Add logos
    if logos:
        m.addlogo(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logos/MO_cropped.png'), 250)
        m.addlogo(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logos/CEDA.png'), 700)
        #m.addlogo(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logos/NCAS_med.png'), 905)
        m.addlogo(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logos/UoL.png'), 1150)

    # If output directory does not exist, create it
    if len(outdir) > 0:
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        m.outdir = outdir

    # Save output to disk
    if outfile:
        m.saveFile(filename=outfile)
    else:
        m.saveFile()

    m.free()
    return


def draw_shape_map(n, column, shapelist, shapelines=True, shapecolors=True):

    m = drawMap(n, column)

    files = []
    colors = []
    with open(shapelist, 'r') as f:
        for line in f:
            if ',' in line:
                (filename, colorname) = line.split(',', 1)
                filename = filename.strip()
                colorname = colorname.strip()

                files.append(filename)
                colors.append(colorname)

    # Load zones into map object
    m.zoneLoad(files)

    #        print m.patches # DEBUG

    # Draw lines at zone boundaries
    if shapelines:
        print('Plotting zone lines...')
        m.zoneLines()

    # Draw solid colours for zones
    if shapecolors:
        print('Plotting zone colours...')
        m.zoneColour(colors)
