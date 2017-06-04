# articles are of format json
# example {"content" : "The house price in London is expected to decrease further ...", "url": "www.abc.com", "title" : "dropping house price in london"}

import spacy
import geocoder as gc
import pandas as pd
import json
import os
import time

nlp = spacy.load('en')

def add_entities(file_name):
    article=pd.read_json(file_name, typ='series')
    processed_content = nlp(article.title + ". " + article.content)
    gpe_list = []
    org_list = []
    person_list = []

    for ent in processed_content.ents:
        if ent.label_ =='GPE' and str(ent) not in gpe_list:
            gpe_list.append(str(ent))
        elif ent.label_ == 'ORG' and str(ent) not in org_list:
            org_list.append(str(ent))
        elif ent.label_ == 'PERSON'and str(ent) not in person_list:
            person_list.append(str(ent))

    article = article.append(pd.Series( {"geo_locations": gpe_list}))
    article = article.append(pd.Series( {"organisations": org_list}))
    article = article.append(pd.Series( {"personal_ents": person_list}))
    return article


def update_geolocation(file_name):
    article = add_entities(file_name)
    print(file_name)
    for item in article.geo_locations:
        g = geocoder.google(item)
        time.sleep(1)
        #print("{} -{}".format(item, g))
        if g.status != 'ZERO_RESULTS':
            article.set_value( 'geo_locations', {"name": item, "location" : {"lat" :g.latlng[0] , "lng": g.latlng[1]}})
    return article

# Call this to process the files
def update_articles(source_folder, dest_folder):
    for filename in os.listdir(source_folder):
        article = update_geolocation(source_folder+filename)
        artcile_json = article.to_json()
        fd = open(dest_folder+filename, 'w')
        fd.write(artcile_json)
        fd.close()
    return 
