
from playwright.sync_api import sync_playwright, TimeoutError
import time
import os
import yt_dlp
from vimeo_downloader import Vimeo
import json
import re
import vimeo_dl as vimeo

def get_id_video(url):
    # Expresión regular para encontrar el ID después de "/video/"
    match = re.search(r'\/video\/(\d+)', url)
    if match:
        return match.group(1)  # Retorna el primer grupo (el ID)
    else:
        return None  # Si no se encuentra el ID

def download_video(video_link,embedded):
    
    v = Vimeo(video_link,embedded) 
    
    try:
        stream = v.streams
        stream[-1].download(download_directory = 'VideosVimeo', filename = 'VideoCurso')
    except Exception as e:
        print(f"Hubo algun error en la descarga: {e}")
    
    '''
    if video_link:     
        if not os.path.exists("VideosVimeo"):
            os.makedirs("VideosVimeo")
        options = {
            'format': 'best',  # To obtain the best quality
            'outtmpl': 'VideosVimeo/video_curso.mp4',  # output name

        }
        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([video_link])
            print("Descarga completada")
    else:
        print("No se proporciono enlace para la descarga del video-")    
    '''
def get_link(playwright):
    # Inicia el navegador
    try:  
        
        url = input("Escriba la url del curso: ")
        download_dir = os.path.expanduser("~/DocsPython/VideosVimeo")
        os.makedirs(download_dir, exist_ok=True) 
        
        browser = playwright.chromium.launch_persistent_context(
            user_data_dir = "/home/thor_dog/DocsPython/data",
            headless = False,
            accept_downloads=True,
        )  # headless=False para ver la interacción
        
        page = browser.new_page()
       
        # Abre la primera URL (la página de login)
        page.goto('https://autismpartnershipfoundation.org/all-courses/my-account/')

        # Completa el formulario de login
        page.fill('input[name="username"]', 'rmcamad@gmail.com')  # Reemplaza 'tu_usuario' por tu nombre de usuario
        page.fill('input[name="password"]', '7214Robert_')  # Reemplaza 'tu_contraseña' por tu contraseña
        page.click('button[type="submit"]')  # Ajusta el selector si el botón de login es diferente
        page.close()
        
        # Se abre la url del embedded video
        new_page = browser.new_page()

        new_page.goto(url)
        time.sleep(2)
        
        #Se busca el src selector que contiene el vimeo.player del video
        iframe = new_page.query_selector("iframe[src*='vimeo.com']")
        if iframe:
            #Obtenemos la informacion del marco
            videoLink = iframe.get_attribute("src")
            print("Enlace del video:", videoLink)
            #Obtenemos el ID
            id = get_id_video(videoLink)
            v = Vimeo.from_video_id(video_id=id)
            meta = v.metadata
            #Obtenemos url original del video
            urlVideo = meta.url
            print("Enlace a Vimeo",urlVideo)
            download_video(urlVideo,videoLink) 
        else:
            print("No se encontró el iframe de Vimeo.")
            return None   
        
    finally:    
         browser.close()

with sync_playwright() as playwright:
    get_link(playwright)
