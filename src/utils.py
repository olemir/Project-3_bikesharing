import pandas as pd

def get_station_data(df, mask, cols, dec=None, drop_dups=True):
    '''
    Get station data from ride data:
        1. mask data
        2. round date to day and lat, lng to number of dec
        3. drop duplicates
    '''
    # constants
    col_renamer = {
        'ended_at':'date',
        'start_station_name':'station_name',
        'start_station_id':'station_id', 
        'start_lat' : 'lat',
        'start_lng' : 'lng',
        'ended_at':'date',
        'end_station_name':'station_name',
        'end_station_id':'station_id',
        'end_lat' : 'lat', 
        'end_lng' : 'lng'
    }
    # TODO check if cols in col_renamer.keys()
    # get data and rename cols
    stations = df.loc[mask, cols].rename(columns=col_renamer)
    # simplify date
    if hasattr(stations, 'date'):
        stations.date = stations.date.dt.date
    # round lat lng
    if dec: 
        if hasattr(stations, 'lat'):
            stations.lat = stations.lat.round(dec)
        if hasattr(stations, 'lng'):
            stations.lng = stations.lng.round(dec)
    # drop duplicates
    if drop_dups:
        stations = stations.drop_duplicates(ignore_index=True)
    return stations

def merge_values_counts(df, col):
    '''
    Get value counts of each element of data frame column.
    '''
    vcounts = df[col].value_counts()
    vcounts = pd.merge(df[col], vcounts, left_on=[col], right_index=True)
    return vcounts['count']