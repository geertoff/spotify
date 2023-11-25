# docs: https://nominatim.org/release-docs/develop/api/Search/
import requests
from osgeo import ogr, osr
import spacy

def geocodeTrack(track_name, georeference_counter) :
    # georeference track again with different name
    georeference_counter  += 1
    url = 'https://nominatim.openstreetmap.org/search'
    params = dict(
        adressdetails = '1',
        extratags = '1',
        namedetails = '1',
        limit = '1',
        polygon_geojson= '1',
        q = track_name,
        format = 'geojson'
    )

    req = requests.get(url, params=params)
    if req.status_code == 200 : 
        features = req.json()['features']
        # if the sons is georeferenced
        if len(features) > 0 :
            # declaring variables
            geo_name = ''
            population = None
            year = None, 
            wikipedia_url = ''
            geometry = None 
            feature = features[0]
            print('found song: %s' % track_name)        
            try:
                geo_name = feature['properties']['namedetails']['name']
                print('track name: %s corresponds to the geographical name: %s' % (track_name, geo_name))
            except :
                geo_name = feature['properties']['display_name']
                print('track name: %s corresponds to the geographical name: %s' % (track_name, geo_name))

            extratags = feature['properties']['extratags']
            try :
                population_year = extratags['census:population'].split(';')
                population = population_year[0]
                year = population_year[1]
            except Exception as e :
                population = None
                year = None
            
            try :
                population = extratags['population']
                year = extratags['population:date']
            except Exception as e : 
                e

            try :
                wikicode = extratags['wikipedia']
                if ' ' in wikicode :
                    array = wikicode.split(' ')
                    wikicode = ''
                    for i in array :
                        wikicode = wikicode + i + '%20'

                wikipedia_url = 'https://nl.wikipedia.org/wiki/' + wikicode
            except Exception as e :
                wikipedia_url = ''
                
            geometry = ogr.CreateGeometryFromJson(str(feature['geometry']))
            print('found geometrytype %s' % geometry.GetGeometryName())
            # reproject geometry
            source = geometry.GetSpatialReference()

            # target crs
            crs = 3857
            target = osr.SpatialReference()
            target.ImportFromEPSG(crs)

            transform = osr.CoordinateTransformation(source, target)
            geometry.Transform(transform)
    
            return geo_name, population, year, wikipedia_url, geometry
        else : 
            # no features are found with the given track name
            print('no features found for track', track_name)

            # if it is the first retry of georeferencing
            if georeference_counter == 1 :
                track_name = linguisticReferencing(track_name, 'en')

            # if it is the second retry of georeferencing
            elif georeference_counter == 2 :
                track_name = linguisticReferencing(track_name, 'nl')

            """
            # has yet to be build...
                           
               elif georeference_counter == 3 :

                # split the track name in enitities and give it straight to the nominaatim API
                nlp = spacy.load('en_core_web_sm')
                doc = nlp(track_name)
                for ent in doc.ents :
                    track_name = str(ent)       
                # if track name has numbers 
                # if True in [char.isdigit() for char in track_name] :
                #     #  do not append numbers to the string
                #     track_name = ''.join([i for i in track_name if not i.isdigit()])
                # track_name = linguisticReferencing(track_name, 'en+')
            
            """
         

                            
            return track_name, georeference_counter
    else :
        print('bad request: %s' % req.status_code)
            
def linguisticReferencing(track_name, language) :
    if language == 'en' :
        nlp = spacy.load('en_core_web_sm')
        print('search language is English')
    elif language == 'nl' :
        nlp = spacy.load('nl_core_news_sm')
        print('\nsearch language is Dutch')

    doc = nlp(track_name)
    for ent in doc.ents :
        # check if the entity is a GPE or LOC
        track_name = checkGeographicName(ent)
        if track_name is not None :
            return track_name
            break
    # if no entities can be made from the string or the label is not a GPE or LOC 
    else :
        for i in str(doc).split():
            doc = nlp(i)
            for ent in doc.ents :
                track_name = checkGeographicName(ent)
                return track_name

def checkGeographicName(ent) :
    print('entity: %s (%s) for substring %s' % (ent.label_, spacy.explain(ent.label_), ent.text))
    # check for these three entitites
    """
    FAC : Buildings, airports, highways, bridges, etc.
    GPE : Countries, cities, states
    NORP : Nationalities or religious or political groups
    """
    entities = ['GPE', 'LOC', 'NORP']
    print('checking if entity is a GPE, LOC or NORP')
    for entity in entities :
        track_name = checkEntityLabel(ent, entity)
        if track_name is not None :
            return track_name

def checkEntityLabel(ent, ent_label) :
    if ent.label_ == ent_label :
        # make the entity of the text the name of the song
        track_name = ent.text
        print('found entity %s - geocoding track with "%s"' % (ent.label_, track_name))
        return track_name

def removeNumbers(track_name) :
    name = []
    for char in track_name :
        if not char.isdigit() :
            name.append(char)
    return ''.join(char)


def matchKey(key) :
    match key :
        case -1 :
            return ''
        case 0 :
            return 'C'
        case 1 :
            return 'C#'
        case 2 :
            return 'D'
        case 3 :
            return 'D#'
        case 4 :
            return 'E'
        case 5 :
            return 'F'
        case 6 :
            return 'F#'
        case 7 :
            return 'G'
        case 8 :
            return 'G#'
        case 9 :
            return 'A'
        case 10 :
            return 'A#'
        case 11 :
            return 'B'
        