import os
# from os import listdir
# from os.path import isfile, join
import DatasetBuilder
import PriceAnalysis

my_dataset = DatasetBuilder.DatasetBuilder()

# detect if a processed dataset is already in the folder
if os.path.exists('df_price_clean') == True:
    print('existing processed data with geocoding detected')
    print('------')

    df_to_analyse = my_dataset.df_price_clean = my_dataset.load_data('df_price_clean')

# otherwise it either download and process the data, or start computing the location
else:
    if os.path.exists('df_price_paris') == True:
        print('existing processed data without geocoding detected')
        print('-------')

        my_dataset.df_price_paris = my_dataset.load_data('df_price_paris')
        my_dataset.generate_adresses()
        my_dataset.find_coordinates()
        my_dataset.get_geospatial_data()
        my_dataset.save_data(my_dataset.df_price_clean, 'df_price_clean')
    else:
        if os.path.exists('df_price_original') == True:
            print('Original unprocessed dataset detected')
            print('------')
            my_dataset.df_price = my_dataset.load_data('df_price_original')

        else:
            # start from scratch
            print('No data already available')
            print('------')
            my_dataset.get_price_data()
            my_dataset.save_data(my_dataset.df_price, 'df_price_original')

        my_dataset.clean_dataset()
        my_dataset.save_data(my_dataset.df_price_paris, 'df_price_paris')

        my_dataset.generate_adresses()
        my_dataset.find_coordinates()
        my_dataset.get_geospatial_data()
        my_dataset.save_data(my_dataset.df_price_clean, 'df_price_clean')

print('Starting dataset analysis')
my_analysis = PriceAnalysis.PriceAnalysis(df_to_analyse)
my_analysis.preprocess()
