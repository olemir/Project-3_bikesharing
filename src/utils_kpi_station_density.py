import pandas as pd
import geopandas as gpd

# ----- calculate station density -----

# TODO: quite unsecure functions but who the hell cares?

def mask_active_stations(stations, date):
    return (stations.date_start<=date) & (date<=stations.date_end)

def count_active_stations(stations, date):
    return sum(mask_active_stations(stations, date))

def calc_density_in_grid(stations_proj, grid_in_dc, date=None):
    '''
    Calculate the feckin density mate
    1. sjoin of grid and stations
    2. count the stations within each cell
    3. calculate the density = count / cell area (non-clipped)
    '''
    # Use spatial join to count stations in each grid cell
    if date==None:
        stations_in_grid = gpd.sjoin(stations_proj, grid_in_dc, how="inner", predicate='intersects')
    else:
        stations_in_grid = gpd.sjoin(stations_proj[mask_active_stations(stations_proj, date)], grid_in_dc, how="inner", predicate='intersects')

    # Group by grid cell index and count stations
    station_counts = stations_in_grid.groupby('index_right').size().reset_index(name='station_count')

    # Join counts back to the grid GeoDataFrame
    grid_with_counts = grid_in_dc.merge(station_counts, left_on=grid_in_dc.index, right_on='index_right', how='left')
    grid_with_counts['station_count'] = grid_with_counts['station_count'].fillna(0).astype(int)

    # Calculate density (stations per km²)
    grid_with_counts['density'] = grid_with_counts['station_count'] / grid_with_counts['area_km2']
    return grid_with_counts, stations_in_grid


# ----- map station density with folium -----

# def transform_dataframe_to_folium_heatmap_data(gdf: gpd.GeoDataFrame, col_weight=None, crs=None):
def transform_dataframe_to_folium_heatmap_data(gdf: gpd.GeoDataFrame, intensify_factor=1, crs=None):
    '''
    Transform the Data Frame above to a shape that can be plotted on a folium map
    '''
    centroids = gdf.geometry.centroid.to_crs(crs)
    weights = gdf.density
    return [[p.y, p.x, weight*intensify_factor] for p, weight in zip(centroids, weights) if weight>0.0]

# test = transform_dataframe_to_folium_heatmap_data(data[0], crs_standard)
# test

# def normalize_values_dataframe_timeseries(data: list, col):
def normalize_weights(data: list, col):
    '''
    Normalize the values of a column across all dataframes of a time series 
    '''
    series = pd.concat([d[col] for d in data], axis=0)
    val_min = series.min()
    val_max = series.max()
    for df in data:
        df[col] = df[col].apply(lambda x: (x - val_min) / (val_max - val_min))
    return data