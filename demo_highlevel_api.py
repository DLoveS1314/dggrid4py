# -*- coding: utf-8 -*-

from pathlib import Path
import os
import sys
import uuid

import numpy as np
import pandas as pd

import fiona
from fiona.crs import from_epsg
import geopandas as gpd
import shapely
from shapely.geometry import Polygon, box, shape

from dggrid4py import DGGRIDv7, Dggs, dgselect, dggs_types


def highlevel_grid_gen_and_transform(dggrid_instance:DGGRIDv7):

    """
    - grid_cell_polygons_for_extent(): fill extent/subset with cells at resolution (clip or world)
    - grid_cell_polygons_from_cellids(): geometry_from_cellid for dggs at resolution (from id list)
    - grid_cellids_for_extent(): get_all_indexes/cell_ids for dggs at resolution (clip or world)
    - cells_for_geo_points(): poly_outline for point/centre at resolution
    """
    path = './tmp/grids'
    est_bound = shapely.geometry.box(20.2,57.00, 28.4,60.0 )

    gdf1 = dggrid_instance.grid_cell_polygons_for_extent('ISEA4T', 5, clip_geom=est_bound)
    # print(gdf1.head())
    gdf1.to_file('./tmp/out/est_shape_isea4t_5.shp')

    gdf2 = dggrid_instance.grid_cell_polygons_for_extent('ISEA7H', 5, clip_geom=est_bound)
    # print(gdf2.head())
    gdf2.to_file('./tmp/out/est_shape_isea7h_5.shp')

    gdf2_a = dggrid_instance.grid_cell_polygons_for_extent('ISEA7H', 6, clip_geom=est_bound)
    # print(gdf2_a.head())
    gdf2_a.to_file('./tmp/out/est_shape_isea7h_6.shp')

    gdf3 = dggrid_instance.grid_cell_polygons_for_extent('ISEA7H', 8, clip_geom=est_bound)
    # print(gdf3.head())
    gdf3.to_file('./tmp/out/est_shape_isea7h_8.shp')

    gdf3_a = dggrid_instance.grid_cell_polygons_for_extent('ISEA7H', 9, clip_geom=est_bound)
    # print(gdf3.head())
    gdf3_a.to_file('./tmp/out/est_shape_isea7h_9.shp')

    df1 = dggrid_instance.grid_stats_table('ISEA7H', 8)
    # print(df1.head(8))
    df1.to_csv('./tmp/out/eisea7h_8_stats.csv', index=False)

    df2 = dggrid_instance.grid_cellids_for_extent('ISEA7H', 5, clip_geom=est_bound)
    # print(df2)
    df2.to_csv('./tmp/out/est_isea7h_5_gridgen_from_seqnums.csv', index=False, header=None)

    cell_list_est = df2[0].values
    # # print(cell_list_est)
    # # print(cell_list_est.shape)

    gdf4 = dggrid_instance.grid_cell_polygons_from_cellids(cell_list_est, 'ISEA7H', 5)
    # print(gdf4.head())
    gdf4.to_file('./tmp/out/from_seqnums_isea7h_5.shp')

    gdf4['centroid_geo'] = gdf4['geometry'].centroid

    tgeo = gdf4.copy()
    tgeo = tgeo.rename(columns={'geometry': 'old_geo', 'centroid_geo': 'geometry' }).drop(columns=['old_geo'])
    geodf_points_wgs84 = gpd.GeoDataFrame(tgeo, geometry='geometry', crs=from_epsg(4326))

    gdf5 = dggrid_instance.cells_for_geo_points(geodf_points_wgs84, False, 'ISEA7H', 5)
    print(gdf5.head())
    gdf5.to_file('./tmp/out/polycells_from_points_isea7h_5.shp')

    gdf6 = dggrid_instance.cells_for_geo_points(geodf_points_wgs84, True, 'ISEA7H', 5)
    print(gdf6.head())
    gdf6.to_file('./tmp/out/geopoint_cellids_from_points_isea7h_5.shp')


def highlevel_grid_stats(dggrid_instance):
    # generate grid_stats for all predefined DGGS types (except CUSTOM, PLANETGRID will not complete either at higher resolutions)
    for gridtype in filter(lambda x: x.startswith('CUSTOM') == False, dggs_types):

        mixed_aperture_level=None
        # for mixed aperture eg ISEA34H define the level of switch, see dggrid manual
        if '43' in gridtype:
            mixed_aperture_level = 7

        try:
            print(f"{gridtype} - {15}")
            df = dggrid_instance.grid_stats_table(dggs_type=gridtype, resolution=15, mixed_aperture_level=mixed_aperture_level, )
            df.to_csv( './tmp/out/stats.csv', index=False)
        except ValueError as ex:
            print(ex)
            pass

def test_grids_from_ids(dggrid_instance:DGGRIDv7):
    list= np.array(['51303', '51401', '51450', '51499', '51500', '51548', '51597',
       '51598', '51646', '51647', '51695', '51696', '51744', '51745',
       '51793', '51794', '51842', '51843', '51891', '51892', '51940',
       '51941', '51989', '51990', '52037', '52038', '52039', '52087',
       '52088', '52136', '52137', '52185', '52186', '52234', '52235',
       '52283', '52284', '52332', '52333', '52380', '52381', '52382',
       '52430', '52431', '52479', '52480', '52528', '52529', '52577',
       '52578', '52626', '52627', '52676', '52724', '52725', '52774',
       '52823', '52921', '67272', '67273', '67274', '67275', '67321',
       '67322', '67323', '67370', '67371', '67372', '67421', '67422'],
      dtype=object)
    gdf4 = dggrid_instance.grid_cell_polygons_from_cellids(list, 'ISEA7H', 5)
if __name__ == '__main__':
    
    executable = '/home/dls/data/openmmlab/DGGRID/build/src/apps/dggrid/dggrid'

    dggrid = DGGRIDv7(executable= executable, working_dir='./tmp/grids', capture_logs=False, silent=False)
    test_grids_from_ids(dggrid)
    # highlevel_grid_gen_and_transform(dggrid)

    # highlevel_grid_stats(dggrid)

    """
    TODO:

    - get parent_for_cell_id at coarser resolution
    - get children_for_cell_id at finer resolution

    - sample raster values into s2 dggs cells
    - sample vector values into s2 dggs cells
    """
