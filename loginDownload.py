
from playwright.sync_api import sync_playwright, TimeoutError
import time
import os
from vimeo_downloader import Vimeo
from yt_dlp import YoutubeDL
import re
import subprocess

def get_id_video(url):
    # Expresión regular para encontrar el ID después de "/video/"
    match = re.search(r'\/video\/(\d+)', url)
    if match:
        return match.group(1)  # Retorna el primer grupo (el ID)
    else:
        return None  # Si no se encuentra el ID

def download_video(url):
        # Ruta donde se guardará el video descargado
    download_path = 'VideosVimeo/'
    os.makedirs(download_path, exist_ok=True)
    # Configuración de yt-dlp para obtener el título del video
    ydl_opts = {
        'format': 'bv+ba',
        'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),  # Usar el título original del video
        'quiet': True,  # Suprimir la salida del proceso de descarga
    }

    # Descargar el video utilizando yt-dlp
    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)  # Solo extraemos la información sin descargar aún
        video_title = info_dict.get('title', None)  # Obtener el título del video
        print(f"Video descargado con el título: {video_title}")

        # Ahora descargamos el video
        ydl.download([url])

    # Ruta del archivo descargado
    input_filename = os.path.join(download_path, f'{video_title}.mp4')

    # Ruta del archivo comprimido
    compressed_filename = os.path.join(download_path, f'{video_title}_comprimido.mp4')

    # Comando FFmpeg para comprimir el video
    ffmpeg_command = [
        'ffmpeg', 
        '-i', input_filename,                 # Archivo de entrada
        '-c:v', 'libx264',                     # Códec de video H.264
        '-crf', '23',                           # Calidad del video (ajustable)
        '-preset', 'medium',                    # Preset de velocidad de compresión
        '-c:a', 'aac',                         # Códec de audio AAC
        '-b:a', '128k',                        # Tasa de bits de audio
        compressed_filename                    # Archivo de salida comprimido
    ]

    # Ejecutar FFmpeg para comprimir el video
    subprocess.run(ffmpeg_command)

    print(f"Video comprimido guardado como: {compressed_filename}")
    
    '''
    output_dir = 'VideosVimeo'
    os.makedirs(output_dir, exist_ok=True)
    
    # Nombre del archivo de salida en la carpeta especificada
    output_filename = os.path.join(output_dir, 'video_descargado.mp4')
    compressed_filename = os.path.join(output_dir, 'video_comprimido.mp4')
    
    # Configuración de yt-dlp para descargar el mejor video y audio
    ydl_opts = {
        'format': 'bv+ba',                               # Selecciona el mejor video y mejor audio y los combina
         'outtmpl':output_filename                       
        #'outtmpl': 'VideosVimeo/%(title)s.%(ext)s',  # Guarda el archivo en la carpeta VideosVimeo
    }

    # Descargar el video con yt-dlp
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
        
    ffmpeg_command = [
    'ffmpeg',               # Llamada al ejecutable ffmpeg
    '-i', output_filename,  # Ruta del archivo de entrada
    '-c:v', 'libx264',      # Códec de video H.264
    '-crf', '23',           # Factor de calidad (cuanto más bajo, mejor calidad, 23 es estándar)
    '-preset', 'medium',    # Configuración de la velocidad de compresión (ajusta entre 'ultrafast', 'fast', 'medium', etc.)
    '-c:a', 'aac',          # Códec de audio AAC
    '-b:a', '128k',         # Tasa de bits de audio (en kbps)                      
    compressed_filename     # Ruta de salida para el video comprimido                 
                    
    ]
    subprocess.run(ffmpeg_command)
    print(f"Video descargado en '{output_filename}' y comprimido guardado como '{compressed_filename}'")
    
    '''  
def get_link(playwright):
    # Inicia el navegador
    try:  
        
        url = input("Escriba la url del curso: ")
        user=input("Escriba su usuario o correo: ")
        password=input("Escriba su contraseña: ") 
        
        browser = playwright.chromium.launch_persistent_context(
            user_data_dir = "/home/thor_dog/DocsPython/data",
            headless = False,
            accept_downloads=True,
        )  # headless=False para ver la interacción
        
        page = browser.new_page()
       
        # Abre la primera URL (la página de login)
        page.goto('https://autismpartnershipfoundation.org/all-courses/my-account/')
        

        # Completa el formulario de login
        page.fill('input[name="username"]', user)  # Reemplaza 'tu_usuario' por tu nombre de usuario
        page.fill('input[name="password"]', password)  # Reemplaza 'tu_contraseña' por tu contraseña
        remember_me_selector = 'input[type="checkbox"][name="remember"]'  # Ajusta el selector si es necesario
        
        if page.query_selector(remember_me_selector):
            page.check(remember_me_selector)
            
        page.click('button[type="submit"]')  # Ajusta el selector si el botón de login es diferente
        page.close()
        time.sleep(2)
        
        #Buscaremos el remember para guardarlo el usuario en cookies.
        
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
            download_video(urlVideo) 
        else:
            print("No se encontró el iframe de Vimeo.")
            return None   
        
    finally:    
         browser.close()

with sync_playwright() as playwright:
    get_link(playwright)
