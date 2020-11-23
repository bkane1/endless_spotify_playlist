#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import spotipy
import pandas as pd
import numpy as np
from spotipy import oauth2

SPOTIPY_CLIENT_ID = 'YOUR CLIENT ID'
SPOTIPY_CLIENT_SECRET = 'YOUR CLIENT SECRET'
SCOPE = ('user-read-recently-played,user-library-read,user-read-currently-playing,playlist-read-private,playlist-modify-private,playlist-modify-public,user-read-email,user-modify-playback-state,streaming,app-remote-control,user-read-private,user-read-playback-state')
SPOTIPY_REDIRECT_URI = 'YOUR REDIRECT URI'
SPOTIFY_USER_ID = 'YOUR SPOTIFY USER ID'
sp_oauth = oauth2.SpotifyOAuth( SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET,SPOTIPY_REDIRECT_URI,scope=SCOPE )

refresh_token = 'YOUR REFRESH TOKEN'
token_info = sp_oauth.refresh_access_token(refresh_token)
sp = spotipy.Spotify(auth=token_info['access_token'])
username = sp.current_user()['id']
pl_id = 'YOUR ENDLESS PLAYLIST ID'


#add these lines if using SeekWell to automate your code (and map those Parameters to correct Google Sheet)
# album_df = {{allAlbums}}
# last_tracks_added = {{lastTracksAdded}}

#make lists of playlist track id's and names to check against your recently played tracks
this_pl = sp.playlist_items(pl_id)['items']
this_pl_ids = [track['track']['id'] for track in this_pl]
this_pl_names = [re.sub('[^0-9a-zA-Z]+', '',track['track']['name']+track['track']['artists'][0]['name']) for track in this_pl]

#make a "to_delete" list of the index and URI of songs you in your playlist that you just listened to
to_delete = []
recents = sp.current_user_recently_played(50)['items']
for track in recents:
    context = track['context']
    name_artist = re.sub('[^0-9a-zA-Z]+', '',track['track']['name']+track['track']['artists'][0]['name'])
    if context and 'playlist' in context['uri']:
        this_pl_id = context['uri'].split('playlist:')[1]
        if track['track']['id'] in this_pl_ids and this_pl_id == pl_id :
            idx = this_pl_ids.index(track['track']['id'])
            uri = track['track']['uri']
            to_delete.append([idx,uri])
        #including a second if statement in case that track id isn't in the playlist but that track+artist is.
        elif this_pl_id == pl_id  and name_artist in this_pl_names:
            idx = this_pl_names.index(name_artist)
            uri = 'spotify:track:' + this_pl_ids[idx]
            to_delete.append([idx,uri]) 


if len(to_delete) > 0:
    #use that list to create a list of track dictionaries (which have track uri and position in the playlist)
    tracks = [{'uri': track[1], 'positions': track[0]} for track in to_delete]

    #use that list of tracks and delete them from your playlist
    sp.user_playlist_remove_specific_occurrences_of_tracks(username,pl_id,tracks)


    #make a 'tracks_to_add' DataFrame that is the same length as the "to_delete" list
    to_add = len(to_delete)
    last_index = last_tracks_added['idx'].astype(int).max()
    tracks_to_add = album_df.loc[last_index+1:last_index+to_add]
    tracks_to_add_ls = tracks_to_add.track_id.tolist()

    #add those songs to your playlist 
    sp.playlist_add_items(pl_id,tracks_to_add_ls)
    
    #add this code if using SeekWell to automate your Python so you can send the "tracks_to_add" DataFrame somewhere
    #tracks_to_add
    #seekwell = {'df': tracks_to_add}
    

