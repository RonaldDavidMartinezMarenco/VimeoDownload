from yt_dlp import YoutubeDL

# URL del video que quieres descargar
url = 'https://vimeo.com/388555131'

# Configuración avanzada
ydl_opts = {
    'format': 'best',  # Selecciona la mejor calidad de video
}

# Descargar el video
with YoutubeDL(ydl_opts) as ydl:
    ydl.download([url])
