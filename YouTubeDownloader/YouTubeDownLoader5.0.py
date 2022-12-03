import PySimpleGUI as sg
import moviepy.editor as mp
from pytube import YouTube
from pytube import Playlist
import pytube.request
import threading
import webbrowser
import time
import os

    
def playlist_download(urls_playlist, folder):
    #urls_playlist[0] = 'https://www.youtube.com/watch?v=7qEvDWoOmM8&list=PLv4jk9YvI_5APXtcVuLguRo6K44V2vkph'
    #urls_playlist[1] = 'https://www.youtube.com/watch?v=uO827X1ZZ3Q&list=PLv4jk9YvI_5CNXY341VDW8jlOXOfS14Cw'
    global stopped
    #for each playlist
    for url_playlist in urls_playlist:
        if url_playlist == '':
            continue
        #test first URL of playlist to check if playlist URL is good
        try:
            yt = YouTube(str(url_playlist.strip()))
        except:           
            print('\n<', url_playlist, '>')
            print("  Error - PlayList URL not valid or connection problems")
            print('\n=========== Task completed ===========')
            continue
        else:      
            p = Playlist(url_playlist)
            #all urls of every playlist
            urls = p.video_urls
            try:
                print('\nTotal files for this Playlist is:', len(urls)) 
                multiple_download (urls, folder)
                if stopped:
                    return
            except:
                return
            
def multiple_download (urls, folder):
    #urls[1] = 'https://www.youtube.com/watch?v=cn3ViPzV3IA'
    #urls[2] = 'https://www.youtube.com/watch?v=LiwKQdl8SQY'
    #urls[3] = 'https://www.youtube.com/watch?v=5JgRaXHdaOA'   
    global done, stopped, task_in_progress, elapsed_time
    if task_in_progress or stopped:
        return
    task_in_progress = True
    for url in urls:
        if url == '':
            continue
        try:
            yt = YouTube(str(url.strip()), on_progress_callback = progress_check, on_complete_callback=completed_download)        
        except:           
            print('\n<', url, '>')
            print("  Error - URL not valid or connection problems")
        else:
            print('\n<', yt.title, '>')
            #To avoid incompatible characters with filenames
            base = ''
            for c in yt.title:
                if c not in '\/:*?"<>|':
                    base = base + c
            file = os.path.join(folder, (base + '.' + media))                
            if os.path.exists(file):
                print('  File skipped because already downloaded')
                continue
            done = False
            print('  Download in progress... ', end='')
            thread = threading.Thread(target=download_media, args=(yt, base, folder), daemon=True)
            thread.start()
            start_time = time.time()
            while (not done):
                elapsed_time = round(time.time() - start_time)
                time.sleep(1)
                if elapsed_time <= 10:
                    progress_bar.update_bar(elapsed_time*2, 100)
            if stopped:
                print('\n  Download stopped by user')
                task_in_progress = False
                return
    print('\n=========== Task completed ===========')
    task_in_progress = False
    progress_bar.update_bar(0, 100)

def download_media(yt, base, folder):
    global done
    try:
        if media == 'mp3':            
            stream = yt.streams.filter(subtype='mp4',only_audio=True).last()
        if media == 'mp4':     
            stream = yt.streams.get_highest_resolution()
        stream.download(output_path = folder, filename = base + '.' + media)
    except:
        print('\n  Some errors in URL provided')
        progress_bar.update_bar(0, 100)
    done = True

def progress_check(stream, chunk: bytes, bytes_remaining: int):
    global elapsed_time
    download_percent = int((stream.filesize-bytes_remaining)/stream.filesize*100)
    if download_percent > 20 and  elapsed_time > 10:
        progress_bar.update_bar(download_percent, 100)

def completed_download(stream, file_path):
    done = True
    print(' Completed')
    progress_bar.update_bar(0, 100)

def get_ready_convert(folder):
    global done, stopped, task_in_progress
    if task_in_progress or stopped:
        return
    task_in_progress = True 
    try:
        files = os.listdir(folder)
        print('Converting all MP4 files in:\n', folder, '\ncreating new MP3 files')
    except:
        files = []
    else: 
        for file in files:
            if stopped:
                print('\n  Convert stopped by user')
                task_in_progress = False
                return
            if file[-4:] == '.mp4':
                file_mp4 = os.path.join(folder, file)
                file_mp3 = os.path.join(folder, file[:-4] + '.mp3')
                print('\n<', file[:-4], '>')
                if os.path.exists(file_mp3):
                    print('  File skipped because file MP3 already present')
                    continue
                print('  Conversion in progress ', end='' )
                done = False    
                thread = threading.Thread(target=convert_to_mp3, args=(file_mp4, file_mp3), daemon=True)
                thread.start()
                file_size = os.path.getsize(file_mp4)
                coeff = 3000000  # average of file_size divide per time consumed for converting. 
                bar = 0
                inc_bar = 100/(file_size/coeff)
                while not done:
                    time.sleep(1)
                    bar += inc_bar
                    progress_bar.update_bar(bar, 100)
                    if stopped:
                        print('\n  Conversion stopped by user')
                        task_in_progress = False
                        return
    print('\n=========== Task completed ===========')
    progress_bar.update_bar(0, 100)
    task_in_progress = False
            
def convert_to_mp3(file_mp4, file_mp3):
    global done
    try:
        clip = mp.VideoFileClip(file_mp4)  
        clip.audio.write_audiofile(file_mp3, logger=None)
        clip.close()
        done = True
        print(' Completed')       
    except:
        print(' Skipped cause some errors ->\n')
    progress_bar.update_bar(0, 100)
    done = True

def progress_bar(key, iterable, *args, title='', **kwargs):
    """
    Takes your iterable and adds a progress meter onto it
    :param key: Progress Meter key
    :param iterable: your iterable
    :param args: To be shown in one line progress meter
    :param title: Title shown in meter window
    :param kwargs: Other arguments to pass to one_line_progress_meter
    :return:
    """
    sg.one_line_progress_meter(title, 0, len(iterable), key, *args, **kwargs)
    for i, val in enumerate(iterable):
        yield val
        if not sg.one_line_progress_meter(title, i+1, len(iterable), key, *args, **kwargs):
            break

def progress_bar_range(key, start, stop=None, step=1, *args, **kwargs):
    """
    Acts like the range() function but with a progress meter built-into it
    :param key: progess meter's key
    :param start: low end of the range
    :param stop: Uppder end of range
    :param step:
    :param args:
    :param kwargs:
    :return:
    """
    return progress_bar(key, range(start, stop, step), *args, **kwargs)

def how_to_use():
    webbrowser.open("https://mastermind.altervista.org/youtube-downloader/", new=0, autoraise=True)

done = False
stopped = False
task_in_progress = False
elapsed_time = 0
media = ''
pytube.request.default_range_size = (1024*1024)
radio_keys = ('-MP3 Audio-', '-MP4 Video-', '-MP3 PlayList-', '-MP4 PlayList-', '-MP4->MP3-')


my_new_theme = {'BACKGROUND': '#ffffff',
                'TEXT': '#1a1a1b',
                'INPUT': '#dae0e6',
                'TEXT_INPUT': '#222222',
                'SCROLL': '#ff0000',
                'BUTTON': ('#FFFFFF', '#ff0000'),
                'PROGRESS': ('#000000', '#000000'),
                'BORDER': 1,
                'SLIDER_DEPTH': 0,
                'PROGRESS_DEPTH': 0,
                'ACCENT1': '#ff5414',
                'ACCENT2': '#33a8ff',
                'ACCENT3': '#dbf0ff'}

# Add your dictionary to the PySimpleGUI themes
sg.theme_add_new('MyNewTheme', my_new_theme)
sg.theme('My New Theme')

layout = [  [sg.Image(r'YouTubeDownloader.PNG')],
            [sg.Text(' '*40)],
            
            [sg.Text('Working folder:'), sg.Combo(sg.user_settings_get_entry('-folder-', []), default_value=sg.user_settings_get_entry('-last folder-', ''), size=(65, 1), key='-FOLDER-'),
             sg.FolderBrowse(),sg.Button('Store'), sg.B('Clear')],
            [sg.Text(' '*40)],
            
            [
             sg.Frame(layout=[[sg.Radio('MP3 Audio', "RADIO1", k='-MP3 Audio-', enable_events=True), sg.Radio('MP4 Video', "RADIO1", k='-MP4 Video-', enable_events=True), 
             sg.Radio('MP3 PlayList', "RADIO1", k='-MP3 PlayList-', enable_events=True), sg.Radio('MP4 PlayList', "RADIO1", k='-MP4 PlayList-', enable_events=True)]],title=' Download '),
             sg.Frame(layout=[[sg.Radio('From MP4 to MP3', "RADIO1", k='-MP4->MP3-', enable_events=True)]],title=' Convert '),
             sg.Push(), sg.Button('   GO   '), sg.Button('  Stop  ')
             ],
            [sg.Text(' '*40)],

            [sg.Frame(layout=[
            [sg.Text('URL', size=(3, 1)), sg.InputText(), sg.Text('URL', size=(3, 1)), sg.InputText()],
            [sg.Text('URL', size=(3, 1)), sg.InputText(), sg.Text('URL', size=(3, 1)), sg.InputText()],
            [sg.Text('URL', size=(3, 1)), sg.InputText(), sg.Text('URL', size=(3, 1)), sg.InputText()]], title=' Paste YouTube Video or Playlist URLs ')],
            [sg.Text(' '*40)],
            
            [sg.Push(), sg.ProgressBar(1, orientation='h', size=(40, 20), key='progress'),  sg.Push()],
            
            [sg.Text('Activities Log:')],
            [sg.Output(size=(102,12), key='-OUTPUT-')],
            
            [sg.Push(), sg.FileBrowse(button_text = "Check files", initial_folder='-FOLDER-' ),
             sg.Button('Clear Log'), sg.Button('How to use'), sg.Exit('Exit'),sg.Push()]]

window = sg.Window('Made by Roby Zaffa', layout)


while True:     # Event Loop
    event, values = window.read()
    urls = [values[1], values[2], values[3], values[4], values[5], values[6]]
    if event == sg.WIN_CLOSED or event == 'Exit':
        break
    if event == 'Clear Log':
        window['-OUTPUT-'].update('')
    if event == 'Store':
        sg.user_settings_set_entry('-folder-', list(set(sg.user_settings_get_entry('-folder-', []) + [values['-FOLDER-'], ])))
        sg.user_settings_set_entry('-last folder-', values['-FOLDER-'])
        window['-FOLDER-'].update(values=list(set(sg.user_settings_get_entry('-folder-', []))))
    if event == 'Clear':
        sg.user_settings_set_entry('-folder-', [])
        sg.user_settings_set_entry('-last folder-', '')
        window['-FOLDER-'].update(values=[], value='')
    progress_bar = window['progress']
    progress_bar.update_bar(0, 100)
    folder = values['-FOLDER-']
    folder = folder.replace("/", "\\")
    done, stopped = False, False
    if event in radio_keys:
        # Reset all Radio text to original color
        for key in radio_keys:
            window[key].update(text_color=sg.theme_element_text_color())
        # Set the Radio button text selected to red
        window[event].update(text_color='red')
    if event == '   GO   ' and not task_in_progress:
        window['-OUTPUT-'].update('')
        if values["-MP3 Audio-"] == True:
            media = 'mp3'
            thread = threading.Thread(target=multiple_download, args=(urls, folder), daemon=True)
            thread.start()
        if values["-MP4 Video-"] == True:
            media = 'mp4'
            thread = threading.Thread(target=multiple_download, args=(urls, folder), daemon=True)
            thread.start()
        if values["-MP3 PlayList-"] == True:
            media = 'mp3'
            thread = threading.Thread(target=playlist_download, args=(urls, folder), daemon=True)
            thread.start()
        if values["-MP4 PlayList-"] == True:
            media = 'mp4'
            thread = threading.Thread(target=playlist_download, args=(urls, folder), daemon=True)
            thread.start()
        if values["-MP4->MP3-"] == True:
            thread = threading.Thread(target=get_ready_convert, args=(folder,), daemon=True)
            thread.start()        
    if event == '  Stop  ':
        stopped = True
    if event == 'How to use':
        thread = threading.Thread(target=how_to_use, daemon=True)
        thread.start()   
            
window.close()

