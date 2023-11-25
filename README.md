# Spotify
This demo is made up of three files, an SQL-script and two Python scripts. 

The SQL-script contains all relevant SQL-queries to create the corresponding datamodel. 

## Dependancies
The demo is based of multiple sources. These are the following:

- [Spotify API](https://developer.spotify.com/dashboard/login): Necessary to make a client ID and client secret.
- [SpotiPy](https://spotipy.readthedocs.io/en/2.22.1/): A Python library that provides functions to get easy access to the Spotify data.
- [Nominatim](https://nominatim.org/release-docs/develop/): OpenStreetMap Geocoder for georeferencing track names.
- [Spacy](https://spacy.io/api): API for linguistic referencing. This is used to recognise geographic entities in a string. Two trained pipelines are used for now, these are: 
    - en_core_web_sm (English):  `python -m spacy download en_core_web_sm`
    - nl_core_news_sm (Dutch): `python -m spacy download nl_core_news_sm`

Some common Python libraries
- [Psyocopg2](https://pypi.org/project/psycopg2/): Python library for connecting with a PostgreSQL database.
- [Requests](https://pypi.org/project/requests/): Python library for requesting HTTP requests
- [Ogr and osr](https://gdal.org/api/python_bindings.html): GDAL Drivers for working with geospatial data, you can download the driver using [this link](https://www.lfd.uci.edu/~gohlke/pythonlibs/#gdal).