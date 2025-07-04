#!/usr/bin/env python3
"""Get newalbumreleases.net list of albums and create a spotify playlist from it"""
""" Implement this: https://github.com/foobuzz/coca """
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
COOKIE = config.get(MAIN_SECTION, 'COOKIE')
USER_AGENT = config.get(MAIN_SECTION, 'USER_AGENT')
PAYLOAD = config.get(MAIN_SECTION, 'PAYLOAD')
end_date = datetime.strptime(RAW_END_DATE, '%a, %d %b %Y %H:%M:%S %z')
#headers = {"cookie":"undefined=0; cf_clearance=LZmhUoABYj1f93N_EHYMA1ZNfFiJpwK96QB73AtFIgQ-1695644757-0-1-2bfea6ac.70b19117.7cfff94c-160.0.0"}
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
                       'Ambient Rock', 'Gothic Punk', 'Blackened Heavy Metal', 'Melodic Metal', 'Rock n Roll',
                       'Blackened Metal', 'Atmospheric Progressive Metal', 'Atmosperic Dark Metal', 'Avantgarde Metal',
                       'Progressive Math Metal', 'Symphonic Gothic Metal', 'Karutrock', 'Extreme Gothic Metal',
                       'Techniacl Death Metal', 'Theatrical Metal', 'Instrumental Hard Rock', 'Blackened Power Metal',
                       'Aocustic', 'rogressive Modern Metal', 'Reggaae', 'Celtic', 'Dark Industrial',
                       'Symphonic Progressive Metal', 'Soundtrtack', 'Deutschrock', 'Symphonic Art Rock', 'Celtic Rock',
                       'Acoustic Metal', 'Melodic Punk Rock', 'Experimntal', 'Slowcore', 'A Cappella Metal',
                       'Modern Thrash Metal', 'K-Rock', 'Groove Metal', 'Downtenpo', 'Progressive Sludge Metal',
                       'Progressive Groove Metal', 'Djentcore', 'Industrial Groove Metal', 'Counry', 'Glam Hard Rock',
                       'Instrumental Thrash Metal', 'Black Metal', 'Symphonic Extreme Metal', 'Technical Groove Metal',
                       'Instrumental Guitar rock', 'Avant-Garde Death Metal', 'Modern Groove Metal',
                       'Medieval Folk Rock',  'Cyberpunk Metal', 'Melodic Thrash Metal', 'Death Rock',
                       'Melodic Dark Metal', 'Atmospehric Doom Metal', 'Groove Metalcore', 'Avanta-Garde Metal',
                       'Dark Wave', 'Neo-Soul', 'Reggae Pop', 'Neo-Medieval Metal', 'Occult Black Metal',
                       'Progressive Heavy Metal', 'Avant-Garde Doom Metal', 'Melodic Symphonic Metal',
                       'Modern Metalcore', 'Bluegarss', 'World', 'Metalic Hardcore', 'C-Pop', 'Funk Metal', 'Eurodance',
                       'Thrashcore', 'Deathgrind', 'Gypsy Punk', 'Afro', 'Violin', 'Horror Metal', 'Bossanova',
                       'Horrorcore', 'Atmosperic Sludge Metal', 'Alternative R&#038;B', 'Technical Brutal Death Metal',
                       'Goth Punk', 'Horror Punk', 'Dowmtempo', 'Sofr Rock', 'Avant-Gard Rock', 'Deutsch Rock',
                       'NDH', 'Heavyv Metal', 'Black&#8217;n&#8217;Roll', 'Atmosphwric Black Metal', 'Industrial Metalcore',
                       'Ebm', 'Modern Progressive Metal', 'Nordic Folk', 'Atmospheric Gothic Metal', 'Blues rock', 'Crust',
                       'Modern Heavy Metal', 'Deathrock', 'Progresssive Metal', 'Avant Garde', 'Retrowave', 'Indystrial Metal',
                       'Powerpop', 'Post Metal', 'Post Industrial Metal', 'Dark Cabaret Metal', 'Dark Folk Rock', 'Parody Metal',
                       'Heavy  Metal', 'Jam Rock', 'Chaotic Metalcore', 'Electroniccore', 'Avant Garde Metal', 'Glacial Apocha',
                       'Beatdown Deathcore', 'Post Black Metal', 'Dark Jazz', 'Experimental Electronica', 'Shogaze', 'Afrobeats',
                       'Gothic Doom Metal', 'Technical Grindcore', 'Dark Heavy Metal', 'Doom Rock', 'Techhouse',
                       'Satanic Pop Metal', 'Metal Crossover', 'Blackened Folk Metal', 'Noise Metal', 'Modern Punk', 'Mathncore',
                       'Rockqabilly', 'Moderm Metal', 'Yechnical Death Metal', 'Groove Death Metal', 'Experimental Doom Metal',
                       'Instrumental Death Metal', 'Oriental Metal', 'Blackened Metalcore', 'Brutal Punk', 'Latin', 'MElodic Death Metal',
                       'Samurai Metal', 'Symphonic Dark Metal', 'Blackened Post-Metal', 'Neo Soul', 'Beatdown', 'Atmospheric Post-Metal',
                       'Acid Punk', 'Norwegian Metal', ' Metalcore', 'Neo Classical Metal', 'Post-Harcore', 'Thrash Death Metal',
                       'Modern Industrial Metal', 'Melodic Grindcore', 'Deitschpunk', 'Hardcore Noise', 'Avantgarde',
                       'Electronic Metalcore', 'Acid Metal', 'Electro Avantgarde Metal', 'Dronegaze', 'THrash Metal', 'Deutschpunk',
                       'Country Punk', 'Dark Electronic', 'Dark Blues', 'Punk Metal', 'Surf Punk', 'Phonk', 'Emo Punk',
                       'Psychedelic Black Metal', 'Love Metal', 'Progressive Trance', 'Medieval Folk', 'Psych Punk', 'Doomgaze',
                       'Art Folk', 'Emocore', 'Glitchcore', 'Avant-Gard Jazz', 'Experimentaal', 'Ambient Pop', 'Ambient Folk',
                       'Psytrance', 'Noisecore', 'Technical Metalcore', 'Pogressive Metal', 'Extreme Death Metal', 'Technical Thrash Metal',
                       'Progressiva Power Metal']
white_listed_styles = ['Indie Rock', 'Synthpop', 'Psychedelic Rock', 'Garage Rock', 'Modern Rock', 'Stoner Metal',
                       'Stoner Rock', 'Indie', 'Grunge', 'Electropop', 'Indietronica', 'Rapcore', 'Psychedelic',
                       'Psychedelic Metal', 'Synthwave', 'Glitch Pop', 'Darkwave', 'Electro Soul', 'Beats',
                       'Indie Electronic', 'Synth Pop', 'Electronic Rock', 'Heavy Rock', 'Rock&#8217;n&#8217; Roll',
                       'Surf Rock', 'Neo-Progressive Rock', 'Post-Grunge', 'Symphonic Progressive Rock',
                       'Psychedelic Pop', 'Inndie Rock', 'Electro', 'Space Rock', 'Modern Hard Rock',
                       'Progressive Hard Rock', 'Dark Electro', 'Indie rock', 'Psychedelic Stoner Rock',
                       'Symphonic Heavy Metal', 'Synthrock', 'Reggae Rock', 'Garage Punk', 'Syntthpop',
                       'Electro Industrial', 'Sythpop', 'Atmospheric Progressive Rock', 'Indiie Pop', 'AOR',
                       'Electro-Industrial', 'Symphonic Rock', 'Synth Funk', 'Rap Metal', 'Psychedelic Trance',
                       'Darksynth', 'Psychedelic Stoner Metal', 'Alternative', 'Sludge', 'Melodc Rock', 'Avant-Garde Rock',
                       'Slacker Rock', 'Gothnic Rock', 'Orchestral Rock', 'Darkpop', 'Desert Rock', 'Industrial Pop',
                       'Modern Symphonic Metal', 'Synth Rock', 'Psych Rock', 'Electro Rock', 'Dakwave', 'ALt Rock', 'Psychedellic Rock',
                       'Comedy Rock', 'Melodic Pop Rock']
gray_listed_styles = ['Hip Hop', 'Funk', 'New Age', 'Trip-Hop', 'New Wave', 'Disco', 'Trip Hop', 'Industrial Hip Hop',
                      'Alternative Hip Hop', 'Dubstep', 'Jazz Hop', 'Jazz Rap', 'Trap Rap', 'Experimental Hip Hop',
                      'Hip-Hop', 'Jazz-Hop', 'Blackened Sludge Metal', 'Symphonic Metal Opera', 'Piano Rock',
                      'Roots Rock', 'Britpop', 'Futurepop', 'Orchestral Thrash Metal', 'HIp Hop', 'Dark Cabaret',
                      'Blackgaze', 'Country Rap', 'Electronicocre', 'Atmospehric Black Metal', 'Hip hop', 'Fusion Rock',
                      'Neoclassical Power Metal', 'Trap Metal', 'Dungeon Synth', 'Epic Melodic Death Metal', 'Melodic Modern Metal',
                      'Hardcore Rap', 'Rock Opera', 'Dark Punk', 'Doo Wop', 'Classical Crossover', 'Symphonic Folk Metal',
                      'Epic Symphonic Metal', 'Cyber Metal', 'Progressive Dark Metal', 'Celtic Metal', 'Horror Doom Metal',
                      'Melodic Punk', 'Horror Thrash Metal', 'Melodic Prog Rock', 'Space Opera', 'Chiptune', 'Dark Pop',
                      'Electro Punk', 'Funk Rock', 'Extreme Symphonic Metal', 'Melodic Blackened Death Metal', 'Digital Pop',
                      'Death Disco', 'Glam']
black_listed_album_words = ['Live From', 'Live At', 'Anniversary Edition', 'Remix', 'Demos', 'Best Of',
                            'Expanded Edition', 'Live in', 'Deluxe Edition', 'Remaster', 'Definitive Edition',
                            'Hits', 'Remaster', 'B-Sides', 'Live at', 'Live Session']
stream = open('config.yaml')
user_config = yaml.safe_load(stream)
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=user_config['client_id'],
                                               client_secret=user_config['client_secret'],
                                               redirect_uri=user_config['redirect_uri'],
                                               scope='playlist-modify-private,playlist-modify-public'))
whitelist_playlist = sp.user_playlist_create(user_config['username'], PLAYLIST_NAME)
singles_playlist = sp.user_playlist_create(user_config['username'], f'{PLAYLIST_NAME}-singles')
graylist_playlist = sp.user_playlist_create(user_config['username'], PLAYLIST_NAME+'-gray')


def load_xml(index=1):
    """Load the XML from a url"""
    invalid_xml = re.compile(u'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]')
    # /feed/?paged=1 redirects to /feed/ and then cloudflare kicks in making the page not load
    if index == 1:
      url = 'https://newalbumreleases.net/feed/'
    else:
      url = 'https://newalbumreleases.net/feed/?paged='+str(index)
    # Load the page manually in a browser to get the cookie_value, use the same user agent as your browser
    #cookie_value = 'undefined=0; cf_clearance=fS0fLQbGxPVA_wi9BektnGCbRPrIHfoqjE2oYLrb.PQ-1722004697-1.0.1.1-rPt6L7yST8DEhO0RIsfUJsy0nC1onTy.N8y6_QAmhygOD6SDb7PMDrzI4TGh9YMCZEOdwns3iB.YIoXj1G0T9A'
    headers = {"cookie": COOKIE,
               "user-agent": USER_AGENT}
    response = requests.post(url, headers=headers, data=PAYLOAD)
    #response = requests.get(url)
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
        if raw_date is None:
            continue
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


def add_to_playlist(albums, playlist, playlist_singles):
    """Add albums to spotify playlist"""
    black_listed_albums_by_word = []
    for album in albums:
        if any(item in album['album'] for item in black_listed_album_words):
            black_listed_albums_by_word.append(album)
        else:
            query = 'album:'+album['album']+' artist:'+album['artist']
            try:
                result = sp.search(query, type='album')
            except spotipy.exceptions.SpotifyException:
                print(f'error searching for: {query}')
#             print(result)
            if result['albums']['total'] == 1:
                add_tracks_to_playlist(result['albums']['items'][0], playlist, playlist_singles, album['artist'])
            else:
                # for item in result['albums']['items']:
                #    if item['album_type'] == 'album':
                # print('query={}'.format(query))
                # print('{} not equal to {}'.format(result['albums']['items'][0]['name'], album['album']))
                # print('{} not equal to {}'.format(result['albums']['items'][0]['artists'][0]['name'], album['artist']))
                # print('Total not equal to 1, equals {}.  Checking artist and album'.format(result['albums']['total']))
                # print(result)
                # print(result['albums'])
                # print(f"There are {result['albums']['total']} results, which is not 1")
                for returned_album in result['albums']['items']:
                    # print(returned_album)
                    # Got a None in the response once
                    if returned_album is not None:
                        for artist in returned_album['artists']:
                            if returned_album['name'] == album['album'] and artist['name'] == album['artist']:
                                # print('Add artist={} album={} id={} to playlist'.format(returned_album['name'], artist['name'], returned_album['id']))
                                add_tracks_to_playlist(returned_album, playlist, playlist_singles, artist)
    print('Black listed albums by word:')
    for album in black_listed_albums_by_word:
        print(album['artist']+' - '+album['album']+' - '+album['date'])

def add_tracks_to_playlist(album, playlist, playlist_singles, artist):
    """ Add tracks to playlist """
    track_id_list = []
    tracks = sp.album_tracks(album['id'])
    tracks_to_add = 2
    singles_tracks_ids = []
    popular_track_ids = {}
    # print(f'tracks={tracks}')
    for track_to_add in range(0, tracks_to_add):
        popular_track_ids[track_to_add] = {}
        popular_track_ids[track_to_add]['track_score'] = -1 # Default to -1 so if there is not popularity score it takes first songs
        popular_track_ids[track_to_add]['track_id'] = ''
    for track in tracks['items']:
        # print(f'track={track}\n')
        if track['type'] == 'track':
            track_id_list.append(track['id'])
            track_info = sp.track(track_id=track['id'])
            current_popular_track_on_album_score = track_info['popularity']
            # print(f'track_info={track_info}')
            # print(f'current_popular_track_on_album_score={current_popular_track_on_album_score} '
            #      f'most_popular_track_on_album_score={most_popular_track_on_album_score} '
            #      f"name={track['name']}" )
            # Find X most popular songs on album
            for track_to_add in range(0, tracks_to_add):
                if current_popular_track_on_album_score > popular_track_ids[track_to_add]['track_score']:
                    popular_track_ids[track_to_add]['track_id'] = track['id']
                    popular_track_ids[track_to_add]['track_score'] = current_popular_track_on_album_score
                    break
    # Create list of track ids from the album
    for track_count in popular_track_ids:
        if popular_track_ids[track_count]['track_id'] != '':
            singles_tracks_ids.append(popular_track_ids[track_count]['track_id'])
    try:
        if singles_tracks_ids != []:
            sp.playlist_add_items(playlist_singles['id'], singles_tracks_ids)
    except (requests.exceptions.HTTPError, spotipy.exceptions.SpotifyException):
        print(f"Error adding to singles playlist {artist} - {singles_tracks_ids}")
    # Add entire album to playlist
    try:
        sp.playlist_add_items(playlist['id'], track_id_list)
    except (requests.exceptions.HTTPError, spotipy.exceptions.SpotifyException):
        print(f"Error adding {artist} - {album['album']}")


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
        add_to_playlist(artist_albums_to_add, playlist['playlist'], singles_playlist)


if __name__ == "__main__":
    main()
