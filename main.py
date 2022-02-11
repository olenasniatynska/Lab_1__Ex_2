"""Web map programm"""

import argparse
import folium
from geopy.geocoders import Nominatim
import math

parser = argparse.ArgumentParser()
parser.add_argument("year", default = '2015')
parser.add_argument("latitude", default = 49.83826)
parser.add_argument("longitude", default = 24.02324)
parser.add_argument("path", default = r'C:\Users\Оленка\Music\locations.list')
args = parser.parse_args()

def read_file(file_path,year):
    """
    Return names and cities for films of the year
    >>> 

    """
    loclist = []
    with open(file_path,'r',encoding='unicode_escape') as file:
        for line in file:
            if '\n' in line:
                line = line.replace('\n','')

            if f'{year}' in line:
                film_name = line.split('(')[0]
                if line[-1] == ')':
                    address = line.split('\t')[-2]
                else:
                    address = line.split('\t')[-1]
                loclist.append([film_name, address.split(',')])
    return loclist


def get_location_of_films(loclist):
    """
    Return coordinates of cities where films were made
    """
    coordlist = dict()
    for elem in loclist:
        try:
            geolocator = Nominatim(user_agent="MyApp")
            location = geolocator.geocode(elem[1][1])
            coordlist[elem[0]] = (round(location.latitude,5), round(location.longitude,5))
        except IndexError:
            geolocator = Nominatim(user_agent="MyApp")
            location = geolocator.geocode(elem[1][0])
            coordlist[elem[0]] = (round(location.latitude,5), round(location.longitude,5))
        except AttributeError:
            pass
    return coordlist


def find_distance(coord1, coord2):
    """
    Return distance between 2 points
    """
    earth_radius = 6372800
    
    phi1 = math.radians(coord1[0])
    phi2 = math.radians(coord2[0])
    dphi = math.radians(coord2[0] - coord1[0])
    dlambda = math.radians(coord2[1] - coord1[1])
    
    a = math.sin(dphi/2)**2 + \
        math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    
    distance = 2*earth_radius*math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(distance,5)


def find_near_points(latitude, longitude):
    distan_dict = dict()
    all_films = get_location_of_films(read_file(args.path,args.year))
    for i in all_films:
        distan_dict[i] = find_distance(all_films[i], (args.latitude,args.longitude))
    nearest = []
    for i in range(9):
        try:
            nearest.append(min(distan_dict, key=distan_dict.get))
            del distan_dict[min(distan_dict, key=distan_dict.get)]
        except IndexError:
            pass
    last = []
    for i in nearest:
        for j in all_films:
            if j == i:
                last.append([i,all_films[j]])
    return last


def make_film_map():
    all_coord = find_near_points(args.latitude, args.longitude)
    map = folium.Map(location=[60.25, 24.8], zoom_start=5, control_scale=True)
    output = "film_map.html"
    for i in all_coord:
        folium.Marker(location=[i[1][0],i[1][1]],popup=i[0],icon=folium.Icon(color='darkpurple', icon='ok-sign'),).add_to(map)
    map.save(output)

make_film_map()
