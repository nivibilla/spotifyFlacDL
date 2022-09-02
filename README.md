# spotifyFlacDL
Downloads FLAC audio files from public Spotify playlists



create file in current folder called "clientDetails.txt", in there on a seperate line copy your client id and secret. Can be made for free using a spotify account.
Follow this guide: https://developer.spotify.com/documentation/web-api/quick-start/

Place chromedriver.exe in c:/chromedriver.exe.

Then run 'py main.py' while in the folder. Saves files into ./spotifyFlacDL

Example:
py main.py -h (shows help)

py main.py (downloads flac by default)

py main.py -l (downloads mp3 versions)

while running, if the playlist is long enough, the program may ask you to complete the captcha required multiple times. Its a hacky solution but I couldnt think of any other way to do it. Unless I find a better data source to get flac files for free. 

todo:

improve searching as some songs are there but not being pulled when the name is too long eg: (The Weeknd - Save Your Tears (Remix) (with Ariana Grande) - Bonus Track) doesnt work, but (The Weeknd Ariana Grande - Save Your Tears) does.

use multiple datasources(youtube music, youtube to mp3...)

build ui(cba tbh

add failed songs to file and retry them when program is run


credit to https://github.com/microsockss/free-mp3-download-cli for initial code base

Disclaimer: This tool is for educational purposes only, I do not condone downloading content in violation of DMCA.
