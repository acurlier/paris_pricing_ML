
import os
#from os import listdir
#from os.path import isfile, join
import PriceAnalysis

my_analysis = PriceAnalysis.PriceAnalysis()

#detect if a processed dataset is already in the folder
if os.path.exists('df_price_clean') == True:
    print('existing processed data with geocoding detected')
    print('------')

    my_analysis.df_price_clean = my_analysis.load_data('df_price_clean')

#otherwise it either download and process the data, or start computing the location 
else:
    if os.path.exists('df_price_paris') == True:
        print('existing processed data without geocoding detected')
        print('-------')

        my_analysis.df_price_paris = my_analysis.load_data('df_price_paris')
        my_analysis.generate_adresses()
        my_analysis.find_coordinates()
        my_analysis.get_geospatial_data()
        my_analysis.save_data(my_analysis.df_price_clean,'df_price_clean')    
    else:
        if os.path.exists('df_price_original') == True:
            print('Original unprocessed dataset detected')
            print('------')
            my_analysis.df_price = my_analysis.load_data('df_price_original')

        else:
            #start from scratch
            print('No data already available')
            print('------')
            my_analysis.get_price_data()
            my_analysis.save_data(my_analysis.df_price,'df_price_original')

        my_analysis.clean_dataset()
        my_analysis.save_data(my_analysis.df_price_paris,'df_price_paris')

        my_analysis.generate_adresses()
        my_analysis.find_coordinates()
        my_analysis.get_geospatial_data()
        my_analysis.save_data(my_analysis.df_price_clean,'df_price_clean')
