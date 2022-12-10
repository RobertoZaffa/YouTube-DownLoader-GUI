# YouTube-DownLoader-GUI
An application to download Videos and Music from Youtube

Python libraries requested: PySimpleGUI, moviepy, pytube, threading, webbrowser,  time, os


![YouTube Downloader Screnshot](https://user-images.githubusercontent.com/76481108/206858111-faf493e5-b4c4-4263-9907-76772c2278d7.PNG)

A PyInstall package is available at: https://mastermind.altervista.org/youtube-downloader/

How to use:

To download, copy the video links (URLs) from YouTube and paste them into the appropriate fields. Choose the format you want (MP3 or MP4) and click “GO”.
Before making the first download, it is important to select the work folder and save it with the “Store” button. In this way, the setting will also be kept for the next launches of the App. If you don’t choose the work folder, the file will be saved to application folder.
It is also possible to paste Playlist URLs and choose to download MP3 or Mp4 Playlist, in this case all the files contained in the playlist will be downloaded.
Up to six Playlist URLs can be entered.
The app also includes an MP4 to MP3 conversion function.
This feature converts all MP4 files in the working folder and creates as many MP3s.
The conversion function is required if downloaded MP3 files are not recognized by the device used. For example the old MP3 players of some cars.
Both the download and convert functions skip the download/conversion if the destination file already exists.
The “Stop” button lets the current write/conversion to complete and interrupts the task right after.
The “Check files” button opens an Explorer window to check the files in the working directory.
