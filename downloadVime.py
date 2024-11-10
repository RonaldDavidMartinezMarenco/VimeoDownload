import sys
import requests


def get_video_id(url):

    # remove slash from the end of the url
    if url[-1] == '/':
        filtered_url = url[:-1]
    else:
        filtered_url = url

    # get video id from url
    result = filtered_url.split('/')[-1]

    return result


def get_video_config(id):
    # set video config url
    video_config_url = 'https://player.vimeo.com/video/' + id + '/config?ask_ai=0&byline=0&context=Vimeo%5CController%5CApi%5CResources%5CVideoController.&email=0&force_embed=1&h=0cefda8b9c&like=0&outro=beginning&portrait=0&share=0&title=0&transcript=1&transparent=0&watch_later=0&s=962184f23e1f14463f4e7fb71be8d3e24b82e75f_1731232760'

    # send get request to get video json config
    video_config_response = requests.get(video_config_url)

    # generate obj from json
    config = video_config_response.json()

    return config


def find_required_quality_height(video_config, required_quality):
    # Inicializar la configuración de video objetivo
    target_video_config = None
    print(video_config_json)

    # Verificar si la estructura de video_config es válida
    if 'request' not in video_config or 'files' not in video_config['request']:
        return None  # Regresar None si la estructura no es válida

    # Verificar si la clave 'progressive' está presente
    if 'streams' not in video_config['request']['files']:
        return None  # Regresar None si no hay videos progresivos disponibles

    # Iterar a través de los videos progresivos
    for video in video_config['request']['files']['streams']:
        # Si no se ha establecido aún el video objetivo, establecer el primero
        if target_video_config is None:
            target_video_config = video
            continue

        # Obtener la altura del video actual
        video_height = video['height']

        # Calcular la diferencia de altura
        video_height_diff = abs(required_quality - video_height)
        target_video_height_diff = abs(required_quality - target_video_config['height'])

        # Actualizar la configuración de video objetivo si el video actual tiene una diferencia de altura menor
        if video_height_diff < target_video_height_diff:
            target_video_config = video

    return target_video_config



def download_video(download_url, file_name):
    # download video
    video_response = requests.get(download_url)

    # open file and write content there
    video_file = open(file_name, 'wb')
    video_file.write(video_response.content)
    video_file.close()

# main sequence of the program
target_video_url = 'https://vimeo.com/388555131'
video_id = get_video_id(target_video_url)
video_config_json = get_video_config(video_id)
target_pr_config = find_required_quality_height(video_config_json, 720)
video_url = target_pr_config['url']
video_file_name = video_id + '_' + target_pr_config['quality'] + '.mp4'
download_video(video_url, video_file_name)
print('downloaded: ' + video_file_name)

#cdns