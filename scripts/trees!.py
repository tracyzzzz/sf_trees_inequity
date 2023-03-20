import geopandas as gpd
import pandas as pd 
import matplotlib.pyplot as plt
import pandas as pd 
from pyproj import CRS
import numpy as np
import altair as alt

#TREES
trees = gpd.read_file('/Users/tracy/sf_trees/data/raw/StreetTreeMapDataAndPotentialSites_02242023.gdb')
tree_species = trees.groupby('COMMON').size().reset_index(name='tree_species')
tree_species.sort_values(by='tree_species',ascending=False)
species = tree_species.sort_values(by='tree_species',ascending=False).head(51)
species.to_csv('/Users/tracy/sf_trees/data/processed/species.csv')

#CENSUS TRACTS
census_tracts = gpd.read_file("/Users/tracy/sf_trees/data/raw/tract/tl_rd22_06_tract.shp",attribute=True)
print(census_tracts.columns)

#ASSIGNING TREES TO CENSUS TRACTS
print(trees.crs)
print(census_tracts.crs)
crs = CRS("EPSG:4326")
census_tracts.crs = crs
joined = gpd.sjoin(trees,census_tracts, how='left', predicate='within')
joined.to_file('/Users/tracy/svi_index/data/processed/tree_census.geojson', driver='GeoJSON')
joined.to_file('/Users/tracy/svi_index/data/processed/tree_census.shp', driver='ESRI Shapefile')

#SVI
columns = ['FIPS','E_TOTPOP','SPL_THEMES','AREA_SQMI','EP_POV150','EP_HBURD','EP_LIMENG','EP_MINRTY',
           'EP_MOBILE','EP_CROWD']
svi_2020 = pd.read_csv('California_2020.csv',usecols=columns)
svi_2020 = svi_2020.rename(columns={'FIPS': 'GEOID','E_TOTPOP':'POPULATION',
                                    'SPL_THEMES': 'SVI',
                                    'EP_POV150':'POVERTY_RATE',
                                    'EP_HBURD':'HOUSING_BURDEN',
                                    'EP_LIMENG':'LIMITED_ENGLISH',
                                    'EP_MINRTY':'MINORITY',
                                    'EP_MOBILE':'MOBILE_HOMES',
                                    'EP_CROWD':'CROWDED_HH'})
svi_2020['GEOID']= svi_2020['GEOID'].astype('string')
sf_regex = '^6075.*'
sf_fips = svi_2020['GEOID'].str.match(sf_regex)
svi_sf = svi_2020[sf_fips]
metrics = ['SVI','POVERTY_RATE','HOUSING_BURDEN','LIMITED_ENGLISH','MINORITY','MOBILE_HOMES','CROWDED_HH']
for metric in metrics:
    svi_sf.loc[svi_sf[metric] == -999, metric] = pd.NaT
    svi_sf.loc[:, metric+'_rank'] = svi_sf[metric].astype('object').rank(pct=True).round(decimals=4)

# JOIN WITH NEIGHBORHO
neighborhoods = gpd.read_file('/Users/tracy/sf_trees/data/raw/Analysis Neighborhoods - 2020 census tracts assigned to neighborhoods')
print(neighborhoods.columns)
neighborhoods = neighborhoods[['geoid', 'neighborho']].rename(columns={'geoid':'GEOID'})
neighborhoods['GEOID'] = neighborhoods['GEOID'].str.lstrip('0')
sf_svi = pd.merge(svi_sf,neighborhoods,on = 'GEOID', how='left')

# ANALYSIS
# Scatterplot: Planted & SVI
joined['GEOID'] = joined['GEOID'].str.lstrip('0')
# joined.to_csv('/Users/tracy/svi_index/for_ozge/trees!.csv',index=False)
existing = joined.loc[trees['PlantType'] == 'Tree']
existing_counts = existing.groupby(['bos','GEOID']).size().reset_index(name='tree_counts')
existing_counts = existing_counts.rename(columns={'bos':'district'})
existing = pd.merge(existing_counts,sf_svi, on='GEOID',how = 'left')
existing.to_csv('/Users/tracy/sf_trees/data/processed/existing_trees.csv',index=False)


