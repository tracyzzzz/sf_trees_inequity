import geopandas as gpd
import pandas as pd

canopy = gpd.read_file('/Users/tracy/svi_index/data/processed/canopy_census/canopy_census.shp')
canopy['GEOID']= canopy['state_fp']+canopy['county_fp']+canopy['tractce']
canopy['GEOID'] = canopy['GEOID'] .str.lstrip('0')
canopy_df = canopy.loc[:, ['canopy','GEOID']]
income = pd.read_csv('/Users/tracy/svi_index/data/processed/income_trees.csv')
income['GEOID'] = income['GEOID'].astype('str')
canopy_income = pd.merge(income,canopy_df, how='left')
viz_1 = canopy_income.loc[:,['GEOID','median_income','canopy','neighborho']]
canopy_income.to_csv('/Users/tracy/svi_index/data/viz_1.csv')
