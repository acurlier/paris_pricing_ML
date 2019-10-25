import pandas as pd
import folium
import requests
import json
from geopy import Nominatim
import numpy as np # library to handle data in a vectorized manner
from pandas.io.json import json_normalize
from shapely.geometry import shape, Point
import time
import seaborn as sns

class PriceAnalysis():

    #def __init__(self):

    def __check_75(self,string):
        if string[0:2]!="75" or len(string)!=5:
            return False
        else:
            return True

    def __check_paris(self,string):
        if string[0:5]!="PARIS":
            return False
        else:
            return True

    def __round_town(self,string):
        return string[0:5]


    def get_price_data(self):
        print('Retrieve transaction data from website ...')
        #getting the main dataset
        url_price = 'https://www.data.gouv.fr/fr/datasets/r/1be77ca5-dc1b-4e50-af2b-0240147e0346'
        self.df_price_original = pd.read_csv(url_price, sep = "|")
        print('Transactions data retrieved')
        #do a copy in case of screwup with the original download (large!)
        self.df_price = self.df_price_original.copy()


    def clean_dataset(self):
        #removal of unnecessary collumns
        list_todrop = ['Code service CH', 'Reference document','1 Articles CGI','Nature mutation',
            '2 Articles CGI', '3 Articles CGI', '4 Articles CGI', '5 Articles CGI',
            'No disposition', 'Prefixe de section',
            'Section', 'No plan', 'No Volume','1er lot','Code commune','Code departement','2eme lot', 'Surface Carrez du 2eme lot',
            '3eme lot', 'Surface Carrez du 3eme lot', '4eme lot',
            'Surface Carrez du 4eme lot', '5eme lot', 'Surface Carrez du 5eme lot',
            'Nombre de lots', 'Code type local', 'Type local', 'Identifiant local', 'Nature culture',
            'Nature culture speciale','Surface terrain','B/T/Q','Code voie']
        #'No voie', 'B/T/Q', 'Type de voie', 'Code voie', 'Voie', 'Code postal','Commune', 'Code departement', 'Code commune',
        self.df_price = self.df_price.drop(columns = list_todrop)
        self.df_price =self.df_price.dropna()

        #postcode doesnt need to be a float, lets turn it to a string
        self.df_price['Code postal'] = self.df_price['Code postal'].map(round)
        self.df_price['Code postal'] = self.df_price['Code postal'].astype(str)

        #generate a truth table thanks by mapping the above function, and using it to remove the unnecessary rows
        self.df_price_paris = self.df_price[self.df_price['Code postal'].map(self.__check_75)]

        #the number at which the good is doesnt need to be a float, lets turn it to a string
        self.df_price_paris['No voie'] = self.df_price_paris['No voie'].map(round)
        self.df_price_paris['No voie'] = self.df_price_paris['No voie'].astype(str)
        self.df_price_paris['Commune'].value_counts()

        #generate a truth table thanks by mapping the above function, and using it to remove the unnecessary rows
        self.df_price_paris = self.df_price_paris[self.df_price_paris['Commune'].map(self.__check_paris)]
        
        # the remainer of the dataset display the name of town as "PARIS + No of the Arrondissement", we just want to keep 'Paris' instead
        self.df_price_paris['Commune'] = self.df_price_paris['Commune'].map(self.__round_town)

        return self.df_price_paris

    
    def generate_adresses(self):
        self.depth = 10 #len(self.df_price_paris)
        #create an adress list dataSeries by combining several columns of the original dataframe
        self.df_price_paris = self.df_price_paris.reset_index().drop('index',axis=1)
        self.address = self.df_price_paris['No voie'] + ' ' \
            + self.df_price_paris['Type de voie'] + ' ' \
            + self.df_price_paris['Voie'] + ' ' \
            + self.df_price_paris['Code postal'] + ' ' \
            + self.df_price_paris['Commune']
        self.address = self.address[0:self.depth]
    
    def find_coordinates(self):
        #lookup adresses for lattitude and longitude
        longi = []
        lat = []
        success = 0
        failure_connect = 0
        failure_process = 0
        print('Running ...')
        for i,place in enumerate(self.address):
            time.sleep(0.7) # mandatory break between each nominatim request
            geolocator = Nominatim(user_agent="foursquare_agent")
            print(str(i) + ' / ' + str(self.depth))
            try:
                #get the location
                location = geolocator.geocode(place)
                try:
                    latitude = location.latitude
                    longitude = location.longitude
                    success+=1
                    #print(place + ' lat = '+ str(latitude) + ' lon = ' + str(longitude))
                    lat.append(latitude)
                    longi.append(longitude)
                except:
                    #there might be corrupted adresses, due to missing characters (typically:apostrophees)
                    # we use this little trick to try and recover some of them
                    try:
                        adresse_reform = self.df_price_paris['No voie'].iloc[i] + ' ' \
                        + self.df_price_paris['Type de voie'].iloc[i] + ' ' \
                        + self.df_price_paris['Voie'].iloc[i][0] + "'" \
                        + self.df_price_paris['Voie'].iloc[i][2:] + ' ' \
                        + self.df_price_paris['Code postal'].iloc[i] + ' ' \
                        + self.df_price_paris['Commune'].iloc[i]

                        location = geolocator.geocode(adresse_reform)
                        latitude = location.latitude
                        longitude = location.longitude
                        success+=1
                        #print('[Recovered] : ' + adresse_reform + ' lat = '+ str(latitude) + ' lon = ' + str(longitude))
                        lat.append(latitude)
                        longi.append(longitude)

                    except:
                        #if the recovery fails
                        failure_process+=1
                        #print('[Failed] Error at : ' + adresse_reform)
                        lat.append(np.nan)
                        longi.append(np.nan)
            except:
                #sometimes it is not possible to access the service, eventhough the deadtime criteria is met, we give up on these adresses
                failure_connect +=1
                #print('[Failed] Connection error at : ' + place)
                lat.append(np.nan)
                longi.append(np.nan)       

        # display a report
        print("Nominatim location import completed:")
        print("Import successful : " + str(success))
        print("Adress not found : " + str(failure_process))
        print("Service not responding : " + str(failure_connect))

        #generating the dataframe
        #we don't need these columns any longer
        list_todrop2 = ['No voie','Type de voie','Voie','Code postal','Commune','Surface reelle bati']
        self.df_price_clean = self.df_price_paris.drop(columns = list_todrop2)

        #define the number of rows to process (ultimately the whole adress dataseries)
        self.df_price_clean = self.df_price_clean.iloc[0:self.depth]

        #The cash value of the goods in the dataset is considered as a string, since it uses the french separator for decimals (, instead of .)
        #lets solve this issue
        self.df_price_clean['Valeur fonciere'] = self.df_price_clean['Valeur fonciere'].str.replace(',', '.', regex=False)
        self.df_price_clean['Valeur fonciere'] = self.df_price_clean['Valeur fonciere'].astype(float)

        #same  thing for the surface of the good
        self.df_price_clean['Surface Carrez du 1er lot'] = self.df_price_clean['Surface Carrez du 1er lot'].str.replace(',', '.', regex=False)
        self.df_price_clean['Surface Carrez du 1er lot'] = self.df_price_clean['Surface Carrez du 1er lot'].astype(float)

        # we compute a more meaningful dataseries : the price per square meters
        self.df_price_clean['Prix / m2'] = self.df_price_clean['Valeur fonciere']/self.df_price_clean['Surface Carrez du 1er lot']
        self.df_price_clean['lattitude'] = lat
        self.df_price_clean['longitude'] = longi

        #we filter out the adresses we weren't able to loacte
        self.df_price_clean = self.df_price_clean.dropna()

    def get_geospatial_data(self):
        url_quartiers = 'https://opendata.paris.fr/explore/dataset/quartier_paris/download/?format=geojson&timezone=Europe/Berlin'
        js=requests.get(url_quartiers).json()
        self.df_price_clean = self.df_price_clean.reset_index()

        # check each polygon to see if it contains the point
        quartier = []
        to_remove = []
        for j in range(len(self.df_price_clean)):
            try:
                point = Point(self.df_price_clean['longitude'].iloc[j],self.df_price_clean['lattitude'].iloc[j])
                temp_data = ""
                for i, feature in enumerate(js['features']):
                    polygon = shape(feature['geometry'])
                    if polygon.contains(point):
                        temp_data = js['features'][i]['properties']['n_sq_qu']
                        quartier.append(temp_data)
                        #print(str(j))# + '--' + ' Found containing polygon:'+ str(js['features'][i]['properties']['n_sq_qu']))
                    else:
                        pass
                if temp_data == "":
                    to_remove.append(j)
            except:
                print(str(j) + '--' + '[error]'+ str(self.df_price_clean['longitude'].iloc[j]) + ' , ' + self.df_price_clean['lattitude'].iloc[j])
                to_remove.append(j)
        
        self.df_price_clean = self.df_price_clean.drop(to_remove)
        self.df_price_clean['Quartier'] = quartier


    def save_data(self,df,name):
        # save dataframe locally
        df.to_pickle(name)
    
    def load_data(self,name):
    # load dataframe
        return pd.read_pickle(name)