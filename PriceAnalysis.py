from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pandas.io.json import json_normalize

class PriceAnalysis():

    def __init__(self,df_toworkwith):

        self.raw_dataset = df_toworkwith

    def preprocess(self):
        #keep only what's necessary
        significant_features = ['Surface Carrez du 1er lot','Nombre pieces principales','Prix / m2','Quartier','lattitude','longitude']
        self.raw_dataset = self.raw_dataset[significant_features]        
        
        # remove outliers 
        self.raw_dataset =  self.raw_dataset[ self.raw_dataset['Prix / m2']<30000]
    
        #separate features from target values
        self.df_price_features = self.raw_dataset.drop(['Prix / m2'],axis=1)
        self.df_price_target = self.raw_dataset['Prix / m2']
        
        #we will refer only to the administrative district for loaction
        #self.df_price_features = self.df_price_features.drop(['lattitude','longitude'],axis=1)
        quartier_list = self.df_price_features[['Quartier']]
        self.df_price_features = self.df_price_features[['Surface Carrez du 1er lot','Nombre pieces principales','Prix / m2']]


        #perform hot one encoding on the district
        cat_encoder = OneHotEncoder()
        Quartier_1hot = cat_encoder.fit_transform(quartier_list)

        #concatenate the cont and onehotencoded dataframes
        self.df_ready = pd.concat([self.df_price_features, Quartier_1hot], axis=1, join='inner')
        self.df_ready.head()


