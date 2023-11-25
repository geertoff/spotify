import spotipy 
from spotipy.oauth2 import SpotifyClientCredentials
import psycopg2
import geocodeTrack as geocodeTrack
from datetime import datetime
import config
# connection db
conn = psycopg2.connect("host=localhost dbname=geodata user=geodata password=geodata")
cur = conn.cursor()

# docs: https://spotipy.readthedocs.io/en/2.22.1/#authorization-code-flow
# GitHub page: https://github.com/spotipy-dev/spotipy
# client credentials from spotify dashboard: https://developer.spotify.com/dashboard/applications/5bd54e6a508c45539a0e58aeddf789c5/users

client_id = config.client_id
client_secret = config.client_secret

# authenticate spotify
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id,
                                                           client_secret=client_secret))

# iterate geo playlist
playlist = 'https://open.spotify.com/playlist/7bbs7oX6GGB7qutre3LevO?si=c0e587a220b64c12'

j = 0
k = 1
i = 0

while k > 0 :
    result = []
    data = sp.playlist_tracks(playlist, limit=100, offset=j)
    features = data['items']
    if len(features) > 0 :
        for feature in features :
            print('\n#%d' % (i + 1))
            e = None
            # user which added the song to the playlist\
            user = feature['added_by']
            user_id = user['id']
            url = user['external_urls']['spotify']

            try :
                sql = 'insert into spotify.spotify_user (id, url) values (%s, %s)'
                cur.execute(sql, (user_id, url))
                conn.commit()
            except Exception:
                conn.rollback()

            artist = feature['track']['artists'][0]
            artist_name = artist['name']
            artist_id = artist['id']
            url = artist['external_urls']['spotify']
    
            try :
                sql = 'insert into spotify.artist (id, name, url) values (%s, %s, %s)'
                cur.execute(sql, (artist_id, artist_name, url))
                conn.commit()
            except Exception :
                conn.rollback()
                
            
            album = feature['track']['album']
            album_id = album['id']
            album_name = album['name']

            release_year = album['release_date']
            # somtimes a date only has a format %m-%y
            try : 
                if '-' in release_year :
                    release_date_obj = datetime.strptime(release_year, '%Y-%m-%d')
                else :
                    release_date_obj = datetime.strptime(release_year, '%Y')
                release_date = datetime.strftime(release_date_obj, '%Y-%m-%d')
            except Exception as exception  : 
                print('Date is not supported yet; %s' % exception)    
            total_tracks = album['total_tracks']

            # pick the highest quality image (640 x 640)
            image = album['images'][0]['url']
            url = album['external_urls']['spotify']
       
            try :
                sql = 'insert into spotify.album (id, name, release_date, total_tracks, image, url, artist_id) values (%s, %s, %s, %s, %s, %s, %s)'
                cur.execute(sql, (album_id, album_name, release_date, total_tracks, image, url, artist_id))
                conn.commit()
            except Exception :
                conn.rollback()

            track = feature['track']
            track_id = track['id']
            track_name = track['name']
            popularity = track['popularity']
            duration = track['duration_ms']
            url = track['external_urls']['spotify']

            try :
                sql = 'insert into spotify.track(id, name, popularity, url, album_id, artist_id, user_id) values (%s, %s, %s, %s, %s, %s, %s)'
                cur.execute(sql, (track_id, track_name, popularity, url, album_id, artist_id, user_id )) 
                conn.commit()
            except Exception as exception :
                conn.rollback()
                e = exception

            if e is None :
                # fetch features of track
                try :
                    track_features = sp.audio_features(track_id)
                    for track_feature in track_features :
                        danceability = track_feature['danceability']
                        energy = track_feature['energy']
                        key = geocodeTrack.matchKey(track_feature['key'])
                        loudness = track_feature['loudness']
                        speechiness = track_feature['speechiness']
                        acousticness = track_feature['acousticness']
                        instrumentalness = track_feature['instrumentalness']
                        liveness = track_feature['liveness']
                        tempo = track_feature['tempo']
                        duration_ms = track_feature['duration_ms']
                        duration = float(duration_ms / 1000.0)
            
                        try :
                            sql = 'insert into spotify.track_features(id, duration, danceability, energy, key, loudness, speechiness, instrumentalness, liveness, tempo) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
                            cur.execute(sql, (track_id, duration, danceability, energy, key, loudness, speechiness, instrumentalness, liveness, tempo))
                            conn.commit()
                        except Exception :
                            conn.rollback()
                except Exception as e:
                    print(e)
                
                georeference_counter = 0
                # georeference track_name
                geo = geocodeTrack.geocodeTrack(track_name, georeference_counter)
                
                # if there is no new geographical name generated
                try :
                    while geo[0] is None and georeference_counter < 2:
                        # if the initial georeference has failed, but a new geographical name has been generated
                        if isinstance(geo[0], str) :
                            # georeference track again with different name
                            geo = geocodeTrack.geocodeTrack(geo[0], georeference_counter)

                        # track_name will be linquisitc referenced in the Dutch language 
                        georeference_counter = geo[1]
                        geo = geocodeTrack.geocodeTrack(track_name, georeference_counter)
                        # if the second georeference has failed, but a new geographical name has been generated 
                        # -> split the whole entry and give it to Nominaatim

                        if isinstance(geo[0], str) :
                            geo = geocodeTrack.geocodeTrack(geo[0], georeference_counter)
                except Exception as e :
                    print(e)        

                try :
                    geo_name = geo[0]
                except:
                    geo_name = None
                try :
                    population = geo[1]
                except:
                    population = None
                try :
                    year = geo[2]
                except:
                    year = None
                try :
                    wikipedia = geo[3]
                except:
                    wikipedia = None
                try :
                    geometry = geo[4]
                except:
                    print('no geometry added for song %s' % track_name)
                    geometry = None
                try :
                    sql = 'insert into spotify.osm (id, geo_name, population, wikipedia, geom) values (%s, %s, %s, %s, ST_SETSRID(ST_GeomFromText(%s), 3857))'
                    cur.execute(sql, (track_id, geo_name, population, wikipedia, str(geometry)))
                    conn.commit()
                    print('inserted song %s in database' % (track_name))
                except :
                    print('did not insert into osm table')
            # next iteration
            i += 1
            print('searching for next song...')
        # the first page (100 tracks) is iterated the next page should be iterated
        j = j + 100
    elif len(features) == 0 :
        break
    