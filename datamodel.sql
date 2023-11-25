
create schema spotify;
 set search_path to spotify, public;

create table spotify.track (id varchar primary key, name varchar, popularity integer, url varchar, album_id varchar, artist_id varchar, user_id varchar);

create table spotify.track_features (id varchar primary key, duration numeric, danceability numeric, energy numeric, key varchar, loudness numeric, speechiness numeric, instrumentalness numeric, liveness numeric, tempo numeric);

create table spotify.spotify_user (id varchar primary key, url varchar);
create table spotify.artist (id varchar primary key, name varchar, url varchar );
create table spotify.album (id varchar primary key, name varchar, release_date date, total_tracks integer, image varchar, url varchar, artist_id varchar);
create table spotify.osm (id varchar primary key, geo_name varchar, population integer, wikipedia varchar, geom geometry);

-- add generated column to add centroid-geometrie to the osm-table
alter table osm 
add column centroid geometry generated always as (
	case 
		when st_geometrytype(geom) != 'ST_Point' then st_setsrid(st_centroid(geom), 3857)
		
	end
) stored;

-- change srid of geometry osm
update osm 
set geom = st_setsrid(geom, 3857);

-- View that merges most data of the tables
set search_path to spotify;
create materialized view mat_geo_spotify as 
select 
	t.id track_id,
	t.name track_name,
	osm.geo_name geo_name,
	osm.population population,
	artist.name artist_name,
	t.popularity popularity_song,
	track_features.key key,
	t.url track_url,
	album.release_date album_release,
	album.image,
	album.total_tracks total_tracks,
	su.id added_by,
	osm.wikipedia,
	osm.geom,
	osm.centroid
	
from track t 
join track_features on track_features.id = t.id
join album on album.id = t.album_id
join artist on artist.id = t.artist_id 
join spotify_user su on su.id = t.user_id 
join osm on osm.id = t.id;
create unique index on mat_geo_spotify (track_id);

alter schema spotify owner to geodata;
alter table album owner to geodata;
alter table artist owner to geodata;
alter table osm owner to geodata;
alter table spotify_user owner to geodata;
alter table track owner to geodata;
alter table track_features owner to geodata;
alter materialized view mat_geo_spotify owner to geodata;

