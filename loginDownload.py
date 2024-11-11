
from playwright.sync_api import sync_playwright, TimeoutError
import time
import os
from vimeo_downloader import Vimeo
from yt_dlp import YoutubeDL
import re
import subprocess

def get_id_video(url):
    # Regular expression to find the ID after "/video/"
    match = re.search(r'\/video\/(\d+)', url)
    if match:
        return match.group(1)  # Returns the first group (the ID)
    else:
        return None  # If the ID is not found

def download_video(url):
    #Path where the downloaded video will be saved
    download_path = 'VideosVimeo/'
    os.makedirs(download_path, exist_ok=True)
    
    #Setting yt-dlp to get video title
    ydl_opts = {
        'format': 'bv+ba',
        'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'), #Use the original title of the video
        'quiet': True,  #Suppress output of download process
    }

    #Download the video using yt-dlp
    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)  # We only extract the information without downloading it yet
        video_title = info_dict.get('title', None)  #get the video title
        print(f"Video descargado con el título: {video_title}")

        #Download the video now
        ydl.download([url])

    # path of the downloaded video
    input_filename = os.path.join(download_path, f'{video_title}.mp4')

    # path of the compressed file
    compressed_filename = os.path.join(download_path, f'{video_title}_comprimido.mp4')

    # ffmpeg settings to download the compressed video
    ffmpeg_command = [
        'ffmpeg',
        '-i', input_filename,                 # input file
        '-c:v', 'libx264',                    # H.264 video codec
        '-crf', '23',                         # Video quality (adjustable)
        '-preset', 'medium',                  # Compression speed preset
        '-c:a', 'aac',                        # AAC audio codec
        '-b:a', '128k',                       # Audio bit rate
        compressed_filename                   # compressed output file
    ]

    #Run FFmpeg to compress the video
    subprocess.run(ffmpeg_command)
    print(f"Video comprimido guardado como: {compressed_filename}")
      
def get_link(playwright):
    
    #Start the browser      
    url = input("Escriba la url del curso: ") # Example URL: https://autismpartnershipfoundation.org/lessons/module-1a-introduction/
    user=input("Escriba su usuario: ") #Here you set the user without input
    password=input("Escriba su contraseña: ") #Here you set the password without input
        
    #Settings to save information like cookies.(Is faster than default settings). 
    browser = playwright.chromium.launch_persistent_context(
        user_data_dir = "/home/thor_dog/DocsPython/data",
        headless = False,# headless=False para ver la interacción
        )  
    page = browser.new_page()
    '''
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    '''
    #the first URL (the login page)
    page.goto('https://autismpartnershipfoundation.org/all-courses/my-account/')
        
    #Complete the login form
        
    page.fill('input[name="username"]', user)  
    page.fill('input[name="password"]', password)  
    page.click('button[type="submit"]')  
             
    page.goto(url)
          
    #Search for the src selector that contains the vimeo.player of the video
    iframe = page.query_selector("iframe[src*='vimeo.com']")
    if iframe:
        #We get the information from the frame
        videoLink = iframe.get_attribute("src")
        print("Enlace del video:", videoLink)
        browser.close()
        #get id of the video that we use to get the real URL 
        id = get_id_video(videoLink)
        v = Vimeo.from_video_id(video_id=id)
        meta = v.metadata
        #get the url video vimeo.com/{id}
        urlVideo = meta.url
        print("Enlace a Vimeo",urlVideo)
        download_video(urlVideo) 
    else:
        print("No se encontró el iframe de Vimeo.")
        return None         
    
with sync_playwright() as playwright:
    get_link(playwright)
