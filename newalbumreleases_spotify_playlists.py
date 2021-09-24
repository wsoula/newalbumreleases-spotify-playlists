#!/usr/bin/env python3
"""Get newalbumreleases.net list of albums and create a spotify playlist from it"""
import xml.etree.ElementTree as ET
from datetime import datetime
import re
import configparser
import requests
import yaml
import spotipy
from spotipy.oauth2 import SpotifyOAuth

config = configparser.ConfigParser()
config.read('config.properties')
MAIN_SECTION = 'Main_Section'
PLAYLIST_NAME = config.get(MAIN_SECTION, 'PLAYLIST_NAME')
RAW_END_DATE = config.get(MAIN_SECTION, 'RAW_END_DATE')
INDEX_START = int(config.get(MAIN_SECTION, 'INDEX_START'))
end_date = datetime.strptime(RAW_END_DATE, '%a, %d %b %Y %H:%M:%S %z')
black_listed_styles = ['Jazz', 'Soundtrack', 'Folk', 'Ambient', 'Blues', 'Indie Pop', 'Pop', 'Alt Rock', 'Pop Rock',
                       'Power Metal', 'R&#038;B', 'Progressive Metal', 'Electronic', 'Rock&#8217;n&#8217;Roll',
                       'Progressive Neoclassical Metal', 'Reggae', 'Chanson', 'Alt Rap', 'Post-Hardcore',
                       'Melodic Hard Rock', 'Post-Hardcore', 'RnB', 'Melodic Metalcore', 'Rock', 'Country',
                       'Celtic Folk Metal', 'Black Metal', 'Pagan Black Metal', 'Dance', 'House', 'Experimental',
                       'Soul', 'Indie Folk', 'Alt Metal', 'Doom Metal', 'Post-Punk', 'Instrumental', 'Metalcore',
                       'Modern Classical', 'Deathcore', 'Symphonic Black Metal', 'Blackened Death Metal',
                       'Avant-Garde Folk', 'Heavy Metal', 'Piano', 'Prog Rock', 'Blues Rock', 'Experimental Metal',
                       'Shoegaze', 'Post-Rock', 'Experimental Rock', 'Symphonic Metal', 'Progressive Metalcore',
                       'Folk Rock', 'Dream Pop', 'Classical', 'Hard &#038; Heavy', 'Art Pop', 'Americana',
                       'Techno', 'Emo', 'Alt Country', 'Thrash Metal', 'Hard Rock', 'Punk Rock', 'Death Metal',
                       'Pop Punk', 'Technical Death Metal', 'Melodic Black Metal', 'Groove Metal', 'Gothic Metal',
                       'Chamber Pop', 'Progressive Metal', 'Jazz Fusion', 'Deep House', 'Progressive Rock',
                       'Drum and Bass', 'Chaotic Hardcore', 'World Music', 'Melodic Progressive Metal', 'Cabaret',
                       'Hardcore', 'Drum And Bass', 'Melodic Death Metal', 'Noise', 'Bluegrass', 'Math Rock',
                       'J-Pop', 'Classic Rock', 'Sludge Metal', 'Progressive Death Metal', 'Deathcore', 'Acoustic',
                       'Nu Metal', 'Brutal Death Metal', 'Atmospheric Black Metal', 'Melodic Power Metal',
                       'Atmospheric Sludge Metal', 'Technical Deathcore', 'Post-Metal', 'K-Pop', 'Contemporary Jazz',
                       'Afrobeat', 'Post-Black Metal', 'Fusion', 'Industrial Metal', 'Art Rock', 'Metal Opera',
                       'Rockabilly', 'Chillout', 'Ambient Black Metal', 'J-Metal', 'Screamo', 'Epic Power Metal',
                       'Country Rock', 'Drum &#038; Bass', 'Reggaeton', 'Melodic Heavy Metal', 'Modern Metal', 'Comedy',
                       'Jazz Rock', 'Symphonic Power Metal', 'J-Rock', 'Glitch', 'Jazz Pop', 'Viking Metal',
                       'Dreampop', 'Grindcore', 'Emo Rap', 'Dark Rock', 'Grime', 'Instrumental Rock', 'Downtempo',
                       'Crust Punk', 'Avant-Garde Black Metal', 'Progressive Doom Metal', 'Melodic Hardcore',
                       'Gothic Rock', 'Tech House', 'Neosoul', 'Epic Black Metal', 'Psychedleic Metal', 'British Folk',
                       'Industrial Rock', 'Mathcore', 'Trap', 'Lo-Fi', 'Psychedelic Folk', 'New Pop', 'Classic',
                       'Soudtrack', 'Dub', 'Avant-Garde Metal', 'Video Game Metal', 'Epic Heavy Metal', 'Melodic Rock',
                       'Symphonic Deathcore', 'IDM', 'Soundrtack', 'Noise Rock', 'Chillwave', 'R?B',
                       'Experimental Black Metal', 'Hyperpop', 'Metallic Hardcore', 'Witch House', 'Krautrock',
                       'Soft Rock', 'Alt Pop', 'Industrial', 'Progressive Deathcore', 'Dark Ambient',
                       'Nu Jazz', 'Folk Metal', 'Power Pop', 'Hevay Metal', 'Chamber Folk', 'Bedroom Pop',
                       'Atmospheric Blackened Death Metal', 'Melodic Metal', 'Progressive Thrash Metal', 'Dancehall',
                       'Neo Folk', 'Blackened Deathcore', 'Cloud Rap', 'Ska', 'Glam Rock', 'Noise Pop', 'Bluesgrass',
                       'Progressive Black Metal', 'Depressive Black Metal', 'Neofolk', ' Pop Rock',
                       'Atmospheric Doom Metal', 'Melodic Groove Metal', 'Neoclassical Black Metal', 'Electric Blues',
                       'Progressive Power Metal', 'Hardcore Punk', 'Christian Rock', 'Art Punk', 'Extreme Black Metal',
                       'Dark Ambient Metal', ' Blues', 'Southern Rock', 'Extreme Metal', 'Folk Black Metal', 'Drone',
                       'Neoclassical', 'Bedroom  Pop', 'Neocrust', 'Indistrial Rock', 'Old School Death Metal',
                       'Blackened Hardcore', 'Tachno', 'Funky Jazz', 'Jazz Metal', 'Blackened Thrash Metal',
                       'Post-Metalcore', 'Future Jazz', 'Rap Rock', 'Nu-Metalcore', 'Smooth Jazz', 'Harsh Noise',
                       'Psychedeic Rock', 'Atmospheric Death Metal', 'Beatdown Hardcore', 'Atmospheric Dark Metal',
                       'Crunkcore', 'Trance', 'Nu Metalcore', 'Edm', 'Symphony', 'Progressive Electronic',
                       'Electronica', 'Melodic Deathcore', 'Dance Punk', 'Experimental Grindcore', 'Christian',
                       'Transcendent Metal', 'Post Hardcore', 'Prog Metal', 'Post Rock', 'Instrumental Metal',
                       'Melodic Doom Metal', 'Funeral Doom Metal', 'Avant-Garde', 'Easycore', 'Experimental Rap',
                       'Epic Folk Metal', 'Spoken Word', 'Nu-Metal', 'Acoustic Rock', 'Technical Black Metal',
                       'Neuropunk', 'Industrial Death Metal', 'Djent', 'Dark Folk', 'Ska Punk', 'EBM', 'Metal',
                       'Technical Brutal Metal', 'Afropop', 'Jazz Funk', 'Celtic Folk', 'Post Punk', 'Math Metal',
                       'Psychedelic Doom Metal', 'Industrial Black Metal', 'Blackened Technical Death Metal',
                       'Neofolk Metal', 'Atmospheric Rock', 'Gothic Black Metal', 'Raw Black Metal', 'Swing',
                       'Folk Punk', 'Christian Pop', 'Experimental Death Meta', 'Celtic Punk', 'Pagan Metal',
                       'Dark Metal', 'Orchestral Death Metal', 'Lo Fi', 'Avangarde Folk', 'Epic Doom Metal', 'Gospel',
                       'Medieval Folk Metal', 'Blackened Doom Metal', 'Drone Metal', 'Kawaii Metal',
                       'Deth&#8217;n&#8217;Roll', 'Occult Rock', 'Alt-Country', 'Psychedelic Progressive Metal',
                       'Neo-Psychedelia', 'Depressibe Black Metal', 'Southern Metal', 'Cinematic Metal',
                       'Modern Death Metal', 'Brutal Deathcore', 'Experimental Death Metal', 'Neo Progressive Rock',
                       'Neoclassical Metal', 'Psychobilly', 'Rocn&#8217;n&#8217;Roll', 'Modern Melodic Metal',
                       'PRogressive Metal', 'Glam Metal', 'Regggae', 'Neoclassical Darkwave', 'Southern Hard Rock',
                       'Symphonic Death Metal', 'Pagan Folk', 'Epic Metal', 'Experimental Pop', 'Atmospheric Metal',
                       'Ambient Rock', 'Gothic Punk', 'Blackened Heavy Metal', 'Melodic Metal', 'Rock n Roll']
white_listed_styles = ['Indie Rock', 'Synthpop', 'Psychedelic Rock', 'Garage Rock', 'Modern Rock', 'Stoner Metal',
                       'Stoner Rock', 'Indie', 'Grunge', 'Electropop', 'Indietronica', 'Rapcore', 'Psychedelic',
                       'Psychedelic Metal', 'Synthwave', 'Glitch Pop', 'Darkwave', 'Electro Soul', 'Beats',
                       'Indie Electronic', 'Synth Pop', 'Electronic Rock', 'Heavy Rock', 'Rock&#8217;n&#8217; Roll',
                       'Surf Rock', 'Neo-Progressive Rock', 'Post-Grunge', 'Symphonic Progressive Rock',
                       'Psychedelic Pop', 'Inndie Rock', 'Electro', 'Space Rock']
gray_listed_styles = ['Hip Hop', 'Funk', 'New Age', 'Trip-Hop', 'New Wave', 'Disco', 'Trip Hop', 'Industrial Hip Hop',
                      'Alternative Hip Hop', 'Dubstep', 'Jazz Hop', 'Jazz Rap', 'Trap Rap', 'Experimental Hip Hop',
                      'Hip-Hop', 'Jazz-Hop', 'Blackened Sludge Metal', 'Symphonic Metal Opera', 'Piano Rock',
                      'Roots Rock', 'Britpop']
black_listed_album_words = ['Live From', 'Live At', 'Anniversary Edition', 'Remix', 'Demos', 'Best Of',
                            'Expanded Edition', 'Live in', 'Deluxe Edition', 'Remastered']
stream = open('config.yaml')
user_config = yaml.load(stream)
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=user_config['client_id'],
                                               client_secret=user_config['client_secret'],
                                               redirect_uri=user_config['redirect_uri'],
                                               scope='playlist-modify-private,playlist-modify-public'))
whitelist_playlist = sp.user_playlist_create(user_config['username'], PLAYLIST_NAME)
graylist_playlist = sp.user_playlist_create(user_config['username'], PLAYLIST_NAME+'-gray')


def load_xml(index=1):
    """Load the XML from a url"""
    invalid_xml = re.compile(u'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]')
    url = 'https://newalbumreleases.net/feed/?paged='+str(index)
    response = requests.get(url)
    data = response.content.decode('utf-8')
    with open('content.xml', 'wb') as fil:
        newdata, count = invalid_xml.subn('', data)
        # if count > 0:
        #   print('Removed %s illegal characters' % count
        fil.write(newdata.encode('utf-8'))


def parse_xml(xmlfile, style_whitelist):
    """Parse the XML"""
    reached_end_date = False
    artist_albums_to_add = []
    tree = ET.parse(xmlfile)
    root = tree.getroot()
    for item in root.findall('./channel/item'):
        raw_date = item.find('pubDate').text
        # Tue, 22 Dec 2020 09:37:15 +0000
        date = datetime.strptime(raw_date, '%a, %d %b %Y %H:%M:%S %z')
        description = item.find('description').text
        style_regex_match = re.search(r'^Style: (.+)', description, re.MULTILINE).group(1)
        if date >= end_date:
            if re.search(r'^Artist: (.+)', description, re.MULTILINE) is None:
                print('description has no artist: ' + description)
                break
            artist_regex_match = re.search(r'^Artist: (.+)', description, re.MULTILINE).group(1)
            album_regex_match = re.search(r'^Album: (.+)', description, re.MULTILINE).group(1)
            if style_regex_match in style_whitelist:
                if artist_regex_match is not None and album_regex_match is not None:
                    artist_albums_to_add.append({'artist': artist_regex_match,
                                                 'album': album_regex_match,
                                                 'date': raw_date})
            elif (style_regex_match not in black_listed_styles and style_regex_match not in white_listed_styles and
                  style_regex_match not in gray_listed_styles):
                print(artist_regex_match+' - '+album_regex_match+' style of '+style_regex_match +
                      ' is an unknown style')
        else:
            reached_end_date = True
    return {'artist_albums_to_add': artist_albums_to_add, 'reached_end_date': reached_end_date}


def add_to_playlist(albums, playlist):
    """Add albums to spotify playlist"""
    black_listed_albums_by_word = []
    for album in albums:
        if any(item in album['album'] for item in black_listed_album_words):
            black_listed_albums_by_word.append(album)
        else:
            result = sp.search('album:'+album['album']+' artist:'+album['artist'], type='album')
            track_id_list = []
            if result['albums']['total'] == 1:
                tracks = sp.album_tracks(result['albums']['items'][0]['id'])
                for track in tracks['items']:
                    if track['type'] == 'track':
                        track_id_list.append(track['id'])
                sp.playlist_add_items(playlist['id'], track_id_list)
    print('Black listed albums by word:')
    for album in black_listed_albums_by_word:
        print(album['artist']+' - '+album['album']+' - '+album['date'])


def main():
    """Main function"""
    playlists = [{'styles': white_listed_styles, 'playlist': whitelist_playlist},
                 {'styles': gray_listed_styles, 'playlist': graylist_playlist}]
    for playlist in playlists:
        artist_albums_to_add = []
        index = INDEX_START
        reached_end_date = False
        while not reached_end_date:
            print(index)
            load_xml(index)
            results = parse_xml('content.xml', playlist['styles'])
            artist_albums_to_add.extend(results['artist_albums_to_add'])
            if results['reached_end_date']:
                break
            index = index + 1
        print('Playlist '+str(playlist['styles']))
        add_to_playlist(artist_albums_to_add, playlist['playlist'])


if __name__ == "__main__":
    main()
