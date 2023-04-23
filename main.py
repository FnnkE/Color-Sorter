#Code by FnkE
from dotenv import load_dotenv
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from PIL import Image
import requests

#Get client tokens
load_dotenv()
clientID = os.getenv("CLIENT_ID")
clientSecret = os.getenv("CLIENT_SECRET")

scope = "playlist-read-private, playlist-read-collaborative, playlist-modify-public, user-follow-read, user-library-modify, user-library-read, user-read-private"
auth_manager = SpotifyOAuth(client_id=clientID, client_secret=clientSecret, redirect_uri='http://colorsorterspotify.com/', scope=scope)
sp = spotipy.Spotify(auth_manager=auth_manager)


###############
###Functions###
###############

#Get all songs from a playlist given the ID
#Returns list of song URIs
def getPlaylistSongs(playlistID):
    flag = True
    songs = []
    offset = 0
    while flag:
        tracks = sp.playlist_tracks(playlistID, limit=100, offset=offset)['items']
        if (len(tracks)!=100):
            flag = False
        offset += 100
        songs.extend(tracks)
    return songs

#Adds songs to a playlist given the playlist ID and song URIs
#Returns nothing
def addSongs(playlistID, uris):
    inRange = True
    offset = 0
    range = len(uris)
    while inRange:
        limit = offset + 100
        if limit > range:
            limit = range
        sp.playlist_add_items(playlistID, uris[offset:limit])
        print("adding songs", offset, limit)
        offset += 100
        if offset > range:
            inRange = False

#Removes all songs from a given playlist
#Returns nothing
def removeSongs(playlistID):
    songs = getPlaylistSongs(playlistID=playlistID)
    uris = []
    for idx, song in enumerate(songs):
        if idx%50 == 0 and idx != 0:
            print("Progress: ", idx)
            sp.playlist_remove_all_occurrences_of_items(playlistID, uris)
            uris = []
        newSong = song['track']['uri']
        uris.append(newSong)
    if len(uris) != 0:
        sp.playlist_remove_all_occurrences_of_items(playlistID, uris)

def getImages(songs):
    print("Getting Images")
    images = []
    for i, s in enumerate(songs):
        try:
            print(s['track']['album']['images'],end=" ")
            url = s['track']['album']['images'][0]['url']
            print(url,end=" ")
            img = Image.open(requests.get(url, stream=True).raw)
            print('img opened',end=" ")
            img = img.convert("HSV")
            print('img converted',end=" ")
            img = img.resize((1, 1), resample=0)
            images.append(img.getpixel((0, 0))[0])
            print(i, images[i])
        except:
            print("image unavailable... skipping", i)
    return images

def sortImages(hues, uris):
    print("Sorting Images")
    sortedUris = [uris[0]]
    sortedImages = [hues[0]]
    for i, hue in enumerate(hues[1:]):
        flag = False
        for index, other in enumerate(sortedImages):
            if hue <= other:
                sortedImages.insert(index, hue)
                sortedUris.insert(index, uris[i+1])
                flag = True
                break
        if flag == False:
            sortedImages.append(hue)
            sortedUris.append(uris[i])
    for i, im in enumerate(sortedImages):
        print(im, sortedUris[i])
    return sortedUris

def updateOrder():
    return 0

##########
###Body###
##########

#Get user data
username = sp.current_user()['id']
playlistURL = input("Playlist: ")
playlistID = playlistURL[playlistURL.find('playlist/')+9:playlistURL.find('?')]
songs = getPlaylistSongs(playlistID)
songURIs = []
for idx, song in enumerate(songs):
    if idx%100 == 0:
        print("Progress: ", idx)
    newSong = song['track']['uri']
    songURIs.append(newSong)
images = getImages(songs)
sortedURIS = sortImages(images, songURIs)
print(sortedURIS)

removeSongs(playlistID)
addSongs(playlistID,sortedURIS)


print('DONE!')
