from pathlib import Path
import os
import pandas as pd
from rapidfuzz.distance.Indel import similarity
from shapely import wkt
from shapely.geometry import Point
from geopy.distance import geodesic
from scipy.spatial import cKDTree
from fuzzywuzzy import fuzz
import numpy as np

project_root = Path().resolve().parent
path = project_root.joinpath("data/health_facilities")

pharmacies_gov_it = pd.read_csv(os.path.join(path,"raw_data/dati-salute-gov-it-farmacie-trentino.csv"), quotechar='"')
for index, row in pharmacies_gov_it.iterrows():
    print(row.to_dict())
# replace non-numeric entries with NaN and use periods as decimal separators instead of commas
pharmacies_gov_it['longitudine'] = pharmacies_gov_it['longitudine'].replace('-', pd.NA).str.replace(',', '.')
pharmacies_gov_it['latitudine'] = pharmacies_gov_it['latitudine'].replace('-', pd.NA).str.replace(',', '.')
pharmacies_gov_it['longitudine'] = pd.to_numeric(pharmacies_gov_it['longitudine'], errors='coerce')
pharmacies_gov_it['latitudine'] = pd.to_numeric(pharmacies_gov_it['latitudine'], errors='coerce')
# drop rows with NaN values in longitude or latitude
pharmacies_gov_it = pharmacies_gov_it.dropna(subset=['longitudine', 'latitudine'])
# create a new 'geometry' column with Shapely Point objects
pharmacies_gov_it['geometry'] = pharmacies_gov_it.apply(lambda row: Point(row['longitudine'], row['latitudine']), axis=1)


health_facilities_osm = pd.read_csv(os.path.join(path,"processed_data/health_facilities_points_trentino.csv"))
pharmacies_osm = health_facilities_osm[(health_facilities_osm['amenity'] == 'pharmacy') & (pd.notna(health_facilities_osm['addr_street']))]
for index, row in pharmacies_osm.iterrows():
    print(row.to_dict())
# convert the 'geometry' column from WKT text to Shapely geometry objects
pharmacies_osm['geometry'] = pharmacies_osm['geometry'].apply(wkt.loads)
# filter to keep only Point geometries or convert Polygons to centroids
pharmacies_osm['geometry'] = pharmacies_osm['geometry'].apply(lambda geom: geom if geom.geom_type == 'Point' else geom.centroid)



# extract coordinates for KDTree
coords_osm = np.array([(point.x, point.y) for point in pharmacies_osm['geometry']])
coords_gov_it = np.array([(point.x, point.y) for point in pharmacies_gov_it['geometry']])

# build KDTree for fast spatial matching
tree = cKDTree(coords_gov_it)

# define a search radius
# radius = 0.00045  # Approx 50 meters in degrees
# radius = 0.00449  # Approx 500 meters in degrees
# radius = 0.0449  # Approx 5000 meters in degrees
radius = 0.0898  # Approx 10000 meters in degrees

# find pharmacies in pharmacies_osm that have a match within the radius in pharmacies_gov_it
matches = []
for idx, row in pharmacies_osm.iterrows():
    point = (row.geometry.x, row.geometry.y)
    nearby_indices = tree.query_ball_point(point, r=radius)
    for match_idx in nearby_indices:
        # get potential match from pharmacies_gov_it
        match = pharmacies_gov_it.iloc[match_idx]
        #print(row.to_dict())
        #print(match)
        #print(row['addr_street'])
        #print(match['indirizzo'])

        # calculate address similarity if both values are non-empty strings
        # (edit: non-empty strings have been filtered out)
        #addr_street = row['addr_street'] if pd.notna(row['addr_street']) else ""
        #indirizzo = match['indirizzo'] if pd.notna(match['indirizzo']) else ""
        addr_street = row['addr_street'] + ', ' + str(row['addr_housenumber'])
        indirizzo = match['indirizzo'].title() + ', ' + match['numero_civico']
        address_similarity = fuzz.ratio(addr_street, indirizzo)

        # store results if similarity is above threshold
        if address_similarity > 70:
            matches.append((idx, match_idx, address_similarity))
            print(row.to_dict())
            print(match)
            print(addr_street)
            print(indirizzo)
            print(address_similarity)


len(matches)

###
from geopy.distance import geodesic

# initialize variables to track the farthest matched pharmacies
farthest_match = None
max_distance = 0

# Loop through matches and calculate distances
for idx, match_idx, address_similarity in matches:
    # Get coordinates for pharmacies in pharmacies_osm and pharmacies_gov_it
    osm_coords = (pharmacies_osm.loc[idx, 'geometry'].y, pharmacies_osm.loc[idx, 'geometry'].x)
    gov_it_coords = (pharmacies_gov_it.loc[match_idx, 'geometry'].y, pharmacies_gov_it.loc[match_idx, 'geometry'].x)

    # calculate distance in meters between matched coordinates
    distance = geodesic(osm_coords, gov_it_coords).meters

    # check if this is the farthest match found so far
    if distance > max_distance:
        max_distance = distance
        farthest_match = (idx, match_idx, address_similarity, distance)

# display the farthest match information
if farthest_match:
    idx, match_idx, address_similarity, distance = farthest_match
    print("Farthest matched pharmacies:")
    print("Pharmacy in pharmacies_osm:", pharmacies_osm.loc[idx].to_dict())
    print("Pharmacy in pharmacies_gov_it:", pharmacies_gov_it.loc[match_idx].to_dict())
    print("Address similarity:", address_similarity)
    print("Distance (meters):", distance)
else:
    print("No matches found.")


# Define a DataFrame to hold the matches with selected columns from pharmacies_osm
matches_selected = []

# Loop through each match and extract the desired columns
for idx, match_idx, address_similarity in matches:
    # get the matched row from pharmacies_osm
    row_osm = pharmacies_osm.loc[idx]
    # get the corresponding row from pharmacies_gov_it
    row_gov_it = pharmacies_gov_it.loc[match_idx]
    matches_selected.append({
        'gov_it_index': match_idx,
        'osm_name': row_osm['name'],
        'opening_hours': row_osm['opening_hours'],
        'osm_addr_housenumber': row_osm['addr_housenumber'],
        'osm_address': row_osm['addr_street'],
        'osm_geometry': row_osm['geometry']
    })

# convert the matches list to a DataFrame
match_df = pd.DataFrame(matches_selected)

# merge `match_df` with `pharmacies_gov_it` on `gov_it_index`
pharmacies_gov_it_matched = pharmacies_gov_it.merge(match_df, left_index=True, right_on='gov_it_index', how='left')
for index, row in pharmacies_gov_it_matched.iterrows():
    print(row.to_dict())
# replace
pharmacies_gov_it_matched['indirizzo'] = pharmacies_gov_it_matched['osm_address'].combine_first(pharmacies_gov_it_matched['indirizzo'])
pharmacies_gov_it_matched['numero_civico'] = pharmacies_gov_it_matched['osm_addr_housenumber'].combine_first(pharmacies_gov_it_matched['numero_civico'])
pharmacies_gov_it_matched['descrizione_farmacia'] = pharmacies_gov_it_matched['osm_name'].combine_first(pharmacies_gov_it_matched['descrizione_farmacia'])
pharmacies_gov_it_matched['geometry'] = pharmacies_gov_it_matched['osm_geometry'].combine_first(pharmacies_gov_it_matched['geometry'])
# drop the columns no longer needed
pharmacies_gov_it_matched = pharmacies_gov_it_matched.drop(columns=['cod_comune','frazione','regione','data_inizio_validita','data_fine_validita','osm_name','osm_address','osm_addr_housenumber','osm_geometry','gov_it_index','latitudine','longitudine'])

pharmacies_gov_it_matched = pharmacies_gov_it_matched.rename(columns={'indirizzo': 'addr_street',
                                                                      'numero_civico': 'addr_housenumber',
                                                                      'descrizione_farmacia': 'name',
                                                                      'cap': 'addr_postcode',
                                                                      'comune': 'municipality',
                                                                      'descrizione_tipologia': 'pharmacy_type'})

new_column_order = ['name', 'addr_street', 'addr_housenumber', 'addr_postcode', 'municipality', 'pharmacy_type', 'opening_hours', 'geometry']
pharmacies_gov_it_matched = pharmacies_gov_it_matched[new_column_order]

pharmacies_gov_it_matched['name'] = pharmacies_gov_it_matched['name'].str.title()
pharmacies_gov_it_matched['addr_housenumber'] = pharmacies_gov_it_matched['addr_housenumber'].str.title()
pharmacies_gov_it_matched['addr_street'] = pharmacies_gov_it_matched['addr_street'].str.title()
pharmacies_gov_it_matched['municipality'] = pharmacies_gov_it_matched['municipality'].str.title()
pharmacies_gov_it_matched['pharmacy_type'] = pharmacies_gov_it_matched['pharmacy_type'].str.title()

for index, row in pharmacies_gov_it_matched.iterrows():
    print(row.to_dict())

pharmacies_gov_it_matched.to_csv(os.path.join(path,"processed_data/dati-salute-gov-it-farmacie-trentino-clean.csv"), index=False)



###
hospitals_osm = pd.read_csv(os.path.join(path,"processed_data/health_facilities_points_trentino.csv"))
hospitals_osm = hospitals_osm[hospitals_osm['amenity'] != 'pharmacy']
for index, row in hospitals_osm.iterrows():
    print(row.to_dict())
# convert the 'geometry' column from WKT text to Shapely geometry objects
hospitals_osm['geometry'] = hospitals_osm['geometry'].apply(wkt.loads)
# filter to keep only Point geometries or convert Polygons to centroids
hospitals_osm['geometry'] = hospitals_osm['geometry'].apply(lambda geom: geom if geom.geom_type == 'Point' else geom.centroid)


hospitals_osm = hospitals_osm.rename(columns={'addr_city': 'municipality'})

new_column_order = ['name','addr_street','addr_housenumber','addr_postcode','municipality','amenity','opening_hours','osm_id','osm_type','geometry']
hospitals_osm = hospitals_osm[new_column_order]

hospitals_osm['geometry'] = hospitals_osm['geometry'].apply(lambda geom: geom.wkt)
hospitals_osm.to_csv(os.path.join(path,"processed_data/osm_health_points_trentino.csv"), index=False)