import geopandas as gpd
import pandas as pd

"""
The starting dataframe 'trees!' is a processed dataset of street trees in San Francisco: each row is an unique census tract,
and the dataset contains info about the individual tract's number of street trees, neighborhood, district...

Finding:
neighborhoods that are more vulnerable (e.g. have lower income, higher crime rates, or fewer resources) 
tend to have lower tree densities than neighborhoods that are less vulnerable. This could contribute to a larger issue of 
environmental inequity, where communities that are already facing social and economic challenges are also facing 
a lack of access to the benefits of urban nature, such as shade, air quality improvements, and aesthetic beauty.
"""
# Load trees data
trees = pd.read_csv('/Users/tracy/sf_trees/data/processed/existing_trees.csv')

# Tree per acre
trees['area'] = trees['AREA_SQMI'] * 640
trees['trees_per_acre'] = trees['tree_counts'] / trees['area']
trees['GEOID'] = trees['GEOID'].astype('str')


# Combine with Canopy
canopy = gpd.read_file('/Users/tracy/sf_trees/data/processed/canopy_census/canopy_census.shp')
canopy['GEOID']= canopy['state_fp']+canopy['county_fp']+canopy['tractce']
canopy['GEOID'] = canopy['GEOID'].str.lstrip('0')
canopy_df = canopy.loc[:, ['canopy','HISTO_1','HISTO_NODA','GEOID']]
all_trees = pd.merge(trees,canopy_df,on='GEOID',how = 'left')

# Combine with Income
income = pd.read_csv('/Users/tracy/sf_trees/data/processed/viz_1.csv')
income['GEOID'] = income['GEOID'].astype('str')
income['SF Census Tract'] = income['SF Census Tract'].astype(str)
income.loc[income['SF Census Tract'].str.endswith('.0'), 'SF Census Tract'] = income['SF Census Tract'].str.slice(stop=-2)
all_trees = pd.merge(all_trees,income,on='GEOID',how = 'left')
all_trees.keys()
analysis = all_trees.drop(columns=['AREA_SQMI','POVERTY_RATE','LIMITED_ENGLISH','MOBILE_HOMES',
                        'CROWDED_HH','POVERTY_RATE_rank','LIMITED_ENGLISH_rank','MOBILE_HOMES_rank',
                        'CROWDED_HH_rank','neighborho_x','Unnamed: 0','canopy_x'])
analysis = analysis.rename(columns = {'canopy_y':'canopy','neighborho_y':'neighborhood'})

income_number = pd.read_csv('/Users/tracy/sf_trees/data/processed/median_income.csv')
income_number['GEOID'] = income_number['GEOID'].astype('str')
analysis = pd.merge(analysis,income_number,on='GEOID',how='left')

analysis.to_csv('/Users/tracy/sf_trees/data/processed/analysis.csv')

# income - canopy
rich = analysis[analysis['median_income_y'] > 200000]
poor = analysis[analysis['median_income_y'] < 100000]
rich.keys()
rich_canopy = rich['canopy'].mean()
print(rich_canopy)
poor_canopy = poor['canopy'].mean()
print(poor_canopy)

analysis.keys()
# Minority - street trees
minority = analysis[analysis['MINORITY'] > 70]
mi_tree = minority['trees_per_acre'].mean()
white = analysis[analysis['MINORITY'] < 30 ]
whi_tree = white['trees_per_acre'].mean()
