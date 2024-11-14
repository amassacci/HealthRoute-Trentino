from pathlib import Path
import os
import geopandas as gpd

project_root = Path().resolve().parent
path = project_root.joinpath("data/health_facilities")

# Read the GeoJSON file with polygons
gdf = gpd.read_file(os.path.join(path,'raw_data/limits_R_4_municipalities.geojson'))
print(gdf)
municipalities = gdf['name'].unique()
print(municipalities)
len(municipalities)

if 'name' in gdf.columns:
    # Update the 'name' column to keep only the part before '/'
    gdf['name'] = gdf['name'].apply(lambda x: x.split('/')[0] if isinstance(x, str) and '/' in x else x)
gdf['name'] = gdf['name'].replace("San Giovanni di Fassa-Sèn Jan", "San Giovanni di Fassa")
municipalities = gdf['name'].unique()
print(municipalities)
len(municipalities) #282

trentino_municipalities = ['Ala', 'Albiano', 'Aldeno', 'Altavalle', 'Altopiano della Vigolana', 'Amblar-Don', 'Andalo', 'Arco', 'Avio', 'Baselga di Pinè', 'Bedollo', 'Besenello', 'Bieno', 'Bleggio Superiore', 'Bocenago', 'Bondone', 'Borgo Chiese', 'Borgo Lares', 'Borgo Valsugana', 'Brentonico', 'Bresimo', 'Brez', 'Caderzone Terme', 'Cagnò', 'Calceranica al Lago', 'Caldes', 'Caldonazzo', 'Calliano', 'Campitello di Fassa', 'Campodenno', 'Canal San Bovo', 'Canazei', 'Capriana', 'Carisolo', 'Carzano', 'Castel Condino', 'Castel Ivano', 'Castelfondo', 'Castello-Molina di Fiemme', 'Castello Tesino', 'Castelnuovo', 'Cavalese', 'Cavareno', 'Cavedago', 'Cavedine', 'Cavizzana', 'Cembra Lisignago', 'Cimone', 'Cinte Tesino', 'Cis', 'Civezzano', 'Cles', 'Cloz', 'Comano Terme', 'Commezzadura', 'Contà', 'Croviana', 'Dambel', 'Denno', 'Dimaro Folgarida', 'Drena', 'Dro', 'Faedo', 'Fai della Paganella', 'Fiavè', 'Fierozzo', 'Folgaria', 'Fondo', 'Fornace', 'Frassilongo', 'Garniga Terme', 'Giovo', 'Giustino', 'Grigno', 'Imer', 'Isera', 'Lavarone', 'Lavis', 'Ledro', 'Levico Terme', 'Livo', 'Lona-Lases', 'Luserna', 'Madruzzo', 'Malé', 'Malosco', 'Massimeno', 'Mazzin', 'Mezzana', 'Mezzano', 'Mezzocorona', 'Mezzolombardo', 'Moena', 'Molveno', 'Mori', 'Nago-Torbole', 'Nave San Rocco', 'Nogaredo', 'Nomi', 'Novaledo', 'Ospedaletto', 'Ossana', 'Palù del Fersina', 'Panchià', 'Peio', 'Pellizzano', 'Pelugo', 'Pergine Valsugana', 'Pieve di Bono-Prezzo', 'Pieve Tesino', 'Pinzolo', 'Pomarolo', 'Porte di Rendena', 'Predaia', 'Predazzo', 'Primiero San Martino di Castrozza', 'Rabbi', 'Revò', 'Riva del Garda', 'Romallo', 'Romeno', 'Roncegno Terme', 'Ronchi Valsugana', 'Ronzo-Chienis', 'Ronzone', 'Roverè della Luna', 'Rovereto', 'Ruffrè-Mendola', 'Rumo', 'Sagron Mis', 'Samone', 'San Lorenzo Dorsino', "San Michele all'Adige", "Sant'Orsola Terme", 'Sanzeno', 'Sarnonico', 'Scurelle', 'Segonzano', 'Sella Giudicarie', 'San Giovanni di Fassa', 'Sfruz', 'Soraga di Fassa', 'Sover', 'Spiazzo', 'Spormaggiore', 'Sporminore', 'Stenico', 'Storo', 'Strembo', 'Telve', 'Telve di Sopra', 'Tenna', 'Tenno', 'Terragnolo', 'Terzolas', 'Tesero', 'Tione di Trento', 'Ton', 'Torcegno', 'Trambileno', 'Tre Ville', 'Trento', 'Valdaone', 'Valfloriana', 'Vallarsa', 'Vallelaghi', 'Vermiglio', 'Vignola-Falesina', 'Villa Lagarina', "Ville d'Anaunia", 'Ville di Fiemme', 'Volano', 'Zambana', 'Ziano di Fiemme']
len(trentino_municipalities) #174

trentino_gdf = gdf[gdf['name'].isin(trentino_municipalities)]
selected_municipalities = trentino_gdf['name'].unique()
print(selected_municipalities)
len(selected_municipalities) #163

# municipalities in trentino_municipalities but not in selected_municipalities
not_in_selected = [municipality for municipality in trentino_municipalities if municipality not in selected_municipalities]
len(not_in_selected) #11



gdf_health_sites = gpd.read_file(os.path.join(path,'raw_data/italy_health_facilities_points.geojson'))
print(gdf_health_sites)
len(gdf_health_sites) #24227

# Ensure both GeoDataFrames use the same coordinate reference system (CRS)
gdf_health_sites.crs == trentino_gdf.crs
# gdf_health_sites = gdf_health_sites.to_crs(trentino_gdf.crs)
# Filter to keep only the features within the Provincia Autonoma di Trento
trentino_gdf_health_sites = gdf_health_sites[gdf_health_sites.within(trentino_gdf.unary_union)]
print(trentino_gdf_health_sites)
len(trentino_gdf_health_sites) #436
sites = trentino_gdf_health_sites['name'].unique()
print(sites)
len(sites)

# Convert first 5 rows to dictionaries for a clear view of columns and data
data_dict = trentino_gdf_health_sites.head().to_dict(orient='records')
for row in data_dict:
    print(row)

# Drop useless columns
final_gdf = trentino_gdf_health_sites.drop(columns=['completeness','healthcare','operator','operator_type','source','speciality',
                                                    'operational_status','beds','staff_doctors','staff_nurses',
                                                    'health_amenity_type','dispensing','wheelchair','emergency',
                                                    'insurance','water_source','electricity','is_in_health_area',
                                                    'is_in_health_zone','url','changeset_id','changeset_version',
                                                    'changeset_timestamp','uuid'])
final_gdf['name'] = final_gdf['name'].str.title()
final_gdf['addr_housenumber'] = final_gdf['addr_housenumber'].str.title()
final_gdf['addr_street'] = final_gdf['addr_street'].str.title()
final_gdf['addr_city'] = final_gdf['addr_city'].str.title()

new_column_order = ['name', 'addr_street', 'addr_housenumber', 'addr_postcode', 'addr_city', 'geometry', 'amenity', 'opening_hours', 'osm_id','osm_type']
final_gdf = final_gdf[new_column_order]

#final_gdf.drop(columns='geometry').to_csv(os.path.join(path,"health_facilities_points_trentino.csv"), index=False)
final_gdf['geometry'] = final_gdf['geometry'].apply(lambda geom: geom.wkt)
final_gdf.to_csv(os.path.join(path,"processed_data/health_facilities_points_trentino.csv"), index=False)