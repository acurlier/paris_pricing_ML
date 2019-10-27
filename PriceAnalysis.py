from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pandas.io.json import json_normalize


class PriceAnalysis:

    def __init__(self, df_toworkwith):
        self.raw_dataset = df_toworkwith[0:100]

    def preprocess(self):

        # retrieve quartier name <-> quartier code dataset
        adresse = 'https://opendata.paris.fr/explore/dataset/quartier_paris/download/?format=csv&timezone=Europe/Berlin&use_labels_for_header=true'
        new_df = pd.read_csv(adresse, sep=";")
        list_code = new_df['N_SQ_QU']
        list_noms = new_df['L_QU']

        # keep only what's necessary
        significant_features = ['Surface Carrez du 1er lot', 'Nombre pieces principales', 'Prix / m2', 'Quartier',
                                'lattitude', 'longitude']
        self.raw_dataset = self.raw_dataset[significant_features]

        # remove outliers 
        self.raw_dataset = self.raw_dataset[self.raw_dataset['Prix / m2'] < 30000]

        # separate features from target values
        df_price_features = self.raw_dataset.drop(['Prix / m2'], axis=1)
        df_price_target = self.raw_dataset['Prix / m2']

        # we will refer only to the administrative district for location
        quartier_list = df_price_features[['Quartier']]
        quartier_list.head()

        # switch the code of the quartier for the name (otherwise, onehotencoder crashes bad)
        df_price_features[['Quartier']] = df_price_features[['Quartier']].replace(list_code.to_list(),
                                                                                  list_noms.to_list())

        df_price_features = df_price_features[
            ['Surface Carrez du 1er lot', 'Nombre pieces principales']]

        # perform hot one encoding on the district
        cat_encoder = OneHotEncoder()
        quartier_1hot = cat_encoder.fit_transform(df_price_features[['Quartier']])
        quartier_1hot_df = pd.DataFrame(quartier_1hot.toarray())
        quartier_1hot_df.columns = cat_encoder.categories_

        # concatenate the cont and onehotencoded dataframes
        df_ready = pd.concat([df_price_features, quartier_1hot_df], axis=1, join='inner')
        print(df_ready.head(10))
