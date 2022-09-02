import sys
from twocaptcha import TwoCaptcha
from seleniumwire import webdriver
from seleniumwire.utils import decode
from tqdm import tqdm
import argparse
import requests
import json
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

globalCount = 0

musicPath = './spotifyFlacDL'

if not os.path.exists(musicPath):
    os.makedirs(musicPath)


# initalize parser
parser = argparse.ArgumentParser()

# add arguments
parser.add_argument("-l", action="store_true", help="Download in mp3 instead (default is flac)")
parser.add_argument("-c", "--Captcha", help="2Captcha Key")

# read arguments
args = parser.parse_args()

# handle file_type arg
if args.l:
    file_type = "mp3"
else:
    file_type = "flac"

key = "k7xoeo5zc5osjouuaee4"
cookie = "6c541eg0fv112k8p0em17of3i4"

solver = TwoCaptcha(args.Captcha)
global_captcha = ""

# request headers
headers_dict = {
    "Cookie": "PHPSESSID=" + cookie + "; alertADSfree=yes; metaFLAC=yes; maybeErr=yes",
    "Referer": "https://free-mp3-download.net/download.php?id=572554232&q=dGVzdCUyMGRyaXZl",
}


def download_track(trackId, album_id, trackName):
    # get album metadata from deezer
    album_req = requests.get("https://api.deezer.com/album/" + str(album_id))
    album = album_req.json()
    # find index of track in album
    for track in album["tracks"]["data"]:
        if track["id"] == trackId:
            track_index = album["tracks"]["data"].index(track)
    # download request params
    download_req_params = {
        "i": album["tracks"]["data"][track_index]["id"],
        "ch": key,
        "f": file_type,
        "h": global_captcha,
    }
    # start download
    download_req = requests.get(
        "https://free-mp3-download.net/dl.php",
        download_req_params,
        headers=headers_dict,
    )
    if download_req.text == "Incorrect captcha":
        print("unknown captcha error") 
        # os.remove('./captcha.json')

        resetCaptcha()
        # sys.exit()
        # globalCount += 1
        # if globalCount > 2:
        #     exit()
        # try:
        #     resetCaptcha()
        # except:
        #     exit()
    r = requests.get(download_req.content.strip(), stream=True) # create HTTP response object
    filelength = int(r.headers['Content-Length'])
  
    # send a HTTP request to the server and save
    # the HTTP response in a response object called r
    with open(f'./spotifyFlacDL/{trackName}.{file_type}','wb') as f:
        pbar = tqdm(total=int(filelength/1024))
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:                   # filter out keep-alive new chunks
                pbar.update ()
                f.write(chunk)


def get_artwork(album_data):
    try:
        cover_art_req = requests.get(
            album_data["data"][0]["album"]["cover_xl"])
        with open("cover.jpg", "wb") as f:
            f.write(cover_art_req.content)
        return True
    except:
        print('Could Not find artwork')
        return False


def track(name):
    # get deezer track data
    print(f'Downloading: {name}.{file_type}')
    search_req = requests.get(f"https://api.deezer.com/search?q={name}")
    data = search_req.json()
    # if get_artwork(data):
    #     os.remove("cover.jpg")
    try:
        download_track(data["data"][0]["id"], data["data"][0]["album"]["id"], name)
        return True
    except:
        print(f'Failed to download: {name}')
        return False
    # delete artwork file
    


def solve_captcha():
    print("solving captcha")
    captcha = solver.recaptcha(
        sitekey="6LfzIW4UAAAAAM_JBVmQuuOAw4QEA1MfXVZuiO2A",
        url="http://free-mp3-download.net/",
    )
    print("captcha solved")
    with open("captcha.json", "w") as stored_captcha:
        captcha = str(captcha).replace("'", '"')
        stored_captcha.write(captcha)
    print("stored new captcha")
    captcha = json.loads(captcha)["code"]
    validate_captcha()
    return captcha

def resetCaptcha():
    check_stored_captcha()

def validate_captcha():
    # download request params
    download_req_params = {"i": 572554232, "ch": key,
                           "f": file_type, "h": global_captcha}
    # download request
    download_req = requests.get(
        "https://free-mp3-download.net/dl.php",
        download_req_params,
        headers=headers_dict,
    )
    if download_req.text == "Incorrect captcha":
    
        print("unknown captcha error")
        # os.remove('./captcha.json')
        resetCaptcha()
        # sys.exit()
        # try:
        #     resetCaptcha()
        # except:
        #     exit()


def prompt_captcha():
    driver = webdriver.Chrome(executable_path='C:/chromedriver.exe')
    # create a request interceptor

    def interceptor(request):
        # replacee referer header
        del request.headers['Referer']
        request.headers['Referer'] = 'https://free-mp3-download.net/'
    # set request interceptor
    driver.request_interceptor = interceptor
    driver.get(
        'https://free-mp3-download.net/download.php?id=572554232&q=dGVzdCUyMGRyaXZl')
    # show only captcha box
    driver.execute_script(
        "var saved = document.getElementById('captcha'); var elms = document.body.childNodes; while (elms.length) elms[0].parentNode.removeChild(elms[0]); document.body.appendChild(saved);")
    # set window to smallest size
    driver.set_window_size(1, 625)
    # search for captcha response
    found = False
    while found == False:
        try:
            for request in driver.requests:
                if request.response:
                    if "https://www.google.com/recaptcha/api2/userverify" in request.url:
                        found = True
                        # parse captcha token
                        captcha = decode(request.response.body, request.response.headers.get(
                            'Content-Encoding', 'identity'))
                        captcha = json.loads(captcha[5:].decode('utf-8'))[1]
                        # detect incorrect request
                        if len(captcha) > 600:
                            continue
                        print("grabbed captcha")
                        with open("captcha.json", "w") as stored_captcha:
                            stored_captcha.write(
                                '{"captchaId": "", "code": "' + captcha + '"}')
                        print("stored new captcha")
                        return captcha
        except:
            continue


def handle_captcha():
    if args.Captcha == None:
        return prompt_captcha()
    else:
        return solve_captcha()


def check_stored_captcha():
    # validate stored captcha
    if os.path.exists("captcha.json"):
        stored_captcha = open("captcha.json", "r")
        global_captcha = stored_captcha.read()
        global_captcha = json.loads(global_captcha)["code"]
        stored_captcha.close()
        # test stored captcha
        print("testing stored captcha")
        # download request params
        download_req_params = {"i": 572554232,
                               "ch": key, "f": "mp3", "h": global_captcha}
        # download request
        download_req = requests.get(
            "https://free-mp3-download.net/dl.php",
            download_req_params,
            headers=headers_dict,
        )
        if download_req.text == "Incorrect captcha":
            global_captcha = handle_captcha()
        else:
            print("stored captcha is valid")
    else:
        global_captcha = handle_captcha()


def downloadTracks():

    check_stored_captcha()

    try:
        with open('./clientDetails.txt') as f:
            clientDetails = [line.strip() for line in f.readlines()]
            print(clientDetails)
    except FileNotFoundError:
        print('Please Create "clientDetails.txt" file as described in readme.md')

    CLIENT_ID = clientDetails[0]
    CLIENT_SECRET = clientDetails[1]
    PLAYLIST_LINK = input("Please enter PUBLIC playlist: ").strip()


    CLIENT_CREDENTIALS_MANAGER = SpotifyClientCredentials(
        client_id=CLIENT_ID, client_secret=CLIENT_SECRET
    )
    SP = spotipy.Spotify(client_credentials_manager=CLIENT_CREDENTIALS_MANAGER)


    def get_playlist_uri(playlist_link):
        return playlist_link.split("/")[-1].split("?")[0]


    def get_tracks(tracks, page):
        try:
            page = max(0, (page*100)-1)
            playlist_uri = get_playlist_uri(PLAYLIST_LINK)
            for track in SP.playlist_tracks(playlist_uri, offset=page)["items"]:
                # track_uri = track["track"]["uri"]
                # track_name = track["track"]["name"]
                # result = track_name, SP.audio_features(track_uri)
                item = track['track']
                tracks.append(item['album']['artists'][0]['name'] + ' - ' + item['name'])
        except:
            print("Oops something has gone wrong, please make sure the playlist is public and the link is correct. Otherwise submit an issue in the github repo. Sorry!")

        if len(SP.playlist_tracks(playlist_uri, offset=page)["items"]) == 0:
            return False
        else:
            return True

    print('Getting Tracks')
    allTracks = []
    page = 0
    while get_tracks(allTracks, page):
        page += 1

    allTracks = list(set(allTracks))

    print(f'Found {len(allTracks)} unique tracks')

    if len(allTracks) == 0:
        print('No tracks in playlist')
        exit()

    failedTracks = []
    # handle download type arg
    for eachTrack in tqdm(allTracks):
        if os.path.isfile(f'{musicPath}/{eachTrack}.{file_type}'):
            print(f'File already exists: {eachTrack}.{file_type}')
        elif not track(eachTrack):
            failedTracks.append(eachTrack)
        print()

    print()
    print(f'{len(allTracks)-len(failedTracks)}/{len(allTracks)} downloaded')
    print()
    print('Failed Tracks:')
    print(failedTracks)

downloadTracks()