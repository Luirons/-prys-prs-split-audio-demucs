import os
import re
from pathlib import Path
import io
import select
from shutil import rmtree
import subprocess as sp
import sys
from typing import Dict, Tuple, Optional, IO

# Customize the following options!
MODEL = "htdemucs"
extensions = ["mp3", "wav", "ogg", "flac"]  # we will look for all those file types.

# two_stems = None   # only separate one stems from the rest, for instance
TWO_STEMS = "vocals"

# Options for the output audio.

MP3 = True
MP3_RATE = 128
FLOAT32 = False  # output as float 32 wavs, unsused if 'mp3' is True.
INT24 = False    # output as int24 wavs, unused if 'mp3' is True.



# Ubicacion del archivo original
IN_ORIG_PATH = './in-file/orig-file/'
# Ubicacion del archivo original divido
OUT_ORIG_SPLIT_PATH = './in-file/orig-split/'
# Ubicacion de los archivos procesadosos
DEMUCS_PROCESSED_PATH = './out-file/'
# Ubicacion de los archivos originales procesados
ORIG_FINISHED_PROCESSED = './in-file/orig-finished-processed/'
ORIG_FINISHED_CONVERTED = './converted/'

class Files:
    """
    Clase que representa un archivo de audio y su información básica.

    Atributos:
    file (str): El nombre del archivo de audio, incluyendo la extensión.
    file_path (Path): La ruta completa del archivo de audio.
    file_name (str): El nombre del archivo de audio sin la extensión.
    file_ext (str): La extensión del archivo de audio.
    """
    def __init__(self, file):
        self.file = file
        self.file_path = Path(file)
        self.file_name = self.file_path.stem
        self.file_ext =  self.file_path.suffix


class Bcolors:
    """
    Clase que define colores para imprimir texto en la consola.

    Atributos:
    OK (str): Color verde.
    WARNING (str): Color amarillo.
    FAIL (str): Color rojo.
    RESET (str): Color por defecto.
    """
    OK = '\033[92m' #GREEN
    WARNING = '\033[93m' #YELLOW
    FAIL = '\033[91m' #RED
    WHITE = '\033[97m' #WHITE
    RESET = '\033[0m' #RESET COLOR





def original_file():
    """
    Busca un archivo de audio mp3 en la carpeta ./in-file/orig-file/
    o ./in-file/orig-file-split/ y devuelve la ruta de archivo.
    Si no se encuentra ningún archivo mp3, imprime un mensaje
    de error y devuelve None.
    """
    # Busca todos los archivos con la extensión .mp3 en la carpeta "./in-file/orig-file/"
    mp3_files = [str(file) for file in Path(IN_ORIG_PATH).glob("*.mp3")]

    # Busca todos los archivos con la extensión .mp3 en la carpeta "./in-file/orig-file-split/"
    mp3_out_split = [str(file) for file in Path(OUT_ORIG_SPLIT_PATH).glob("*.mp3")]

    if mp3_files:
        # Crea una cadena de texto que contiene la ruta de archivo del primer archivo encontrado
        file = mp3_files[0]
        return file
    elif mp3_out_split:
        # Crea una cadena de texto que contiene la ruta de
        # archivo del primer archivo encontrado en la carpeta
        # de archivos divididos
        file = mp3_out_split[0]
        return file
    else:
        print("No se encontraron archivos" + Bcolors.FAIL
              + " mp3 " + Bcolors.RESET + "en la carpeta " + Bcolors.FAIL + " orig-file" + Bcolors.RESET)
        return None


def original_split(files_obj):
    """
    Divide un archivo de audio mp3 en partes más pequeñas de
    10 minutos y las guarda en la carpeta ./in-file/orig-file-split/.
    Si el archivo ya se ha dividido anteriormente, se salta este
    paso. También se llama a la función rename_file_convert para
    renombrar los archivos divididos y marcarlos como listos para ser convertidos por Demucs.
    """

    file_ffmpeg_divide = Path(OUT_ORIG_SPLIT_PATH +
            files_obj.file_name) / Path (files_obj.file_name + '_%d' + files_obj.file_ext)

    dir_exits = check_dir_exits(files_obj)
    if dir_exits:
        if dir_exits == "convertir":
            return
    sp.run(["ffmpeg", "-hide_banner","-i",
            files_obj.file, "-nostats", "-loglevel", "verbose", "-f", "segment", "-segment_time", "600",
            file_ffmpeg_divide],check=True)




# chequeamos si el directorio fue creado sino lo creamos
def check_dir_exits(files_obj):
    """Verifica si existe un archivo con el nombre y extensión de `files_obj` en la carpeta
    ORIG_FINISHED_PROCESSED. Si existe, muestra un mensaje
    indicando que el archivo ya fue convertido
    y devuelve False. Luego verifica si existe una carpeta
    con el nombre de `files_obj` en la carpeta
    OUT_ORIG_SPLIT_PATH. Si la carpeta existe, muestra un mensaje y devuelve la cadena "convertir".
    Si la carpeta no existe, crea la carpeta y muestra un mensaje indicando que se creó la carpeta.

    Args:
        files_obj (File): Objeto de la clase File con información del archivo.

    Returns:
        bool or str: False si el archivo ya fue convertido,
        "convertir" si la carpeta de archivos divididos existe,
        None si no hay problemas y se puede continuar con el proceso.
    """

    file_finished = Path( ORIG_FINISHED_PROCESSED
              + files_obj.file_name + "_ok" +
              files_obj.file_ext)
    file_folder_split = Path( OUT_ORIG_SPLIT_PATH  + files_obj.file_name )

    if os.path.exists(file_finished):
        print("El archivo " + Bcolors.FAIL +
              files_obj.file_name  + Bcolors.RESET +
              "ya fue convertido")
        convert = False
        return convert

    if os.path.exists(file_folder_split):
        print("\n👀 ----> Hay una carpeta  " + Bcolors.FAIL
              + str(file_folder_split)  + Bcolors.RESET +
              " de split existe\n")
        convert = "convertir"
        return convert

    os.mkdir(file_folder_split)
    # os.mkdir(_dir / files_obj.file_name)
    print("Se creo la  carpeta  " + Bcolors.FAIL + str(files_obj.file_name)  + Bcolors.RESET)


def rename_file_convert(files_obj):
    """Agrega la palabra "split" al nombre del archivo en `files_obj` y lo mueve a la carpeta
    ORIG_FINISHED_PROCESSED. Muestra un mensaje indicando que el proceso terminó.

    Args:
      files_obj (File): Objeto de la clase File con información del archivo.
    """
    mp3_out_split = [str(file) for file in Path(OUT_ORIG_SPLIT_PATH).glob("*.mp3")]

    if mp3_out_split:
        file_finished = Path( ORIG_FINISHED_PROCESSED  +
        files_obj.file_name + "_split" + files_obj.file_ext)

    else:
        file_finished = Path( ORIG_FINISHED_PROCESSED  +
        files_obj.file_name + "_split" + "converted" + files_obj.file_ext)

    old_name = files_obj.file
    new_name =  file_finished
    os.rename(old_name, new_name)
    print( "\n 👌 -->" + Bcolors.WHITE + "processo terminado"+ Bcolors.RESET + "-->"+ "Se creo el archivo final con solo la voz\n"
          + Bcolors.FAIL + str(files_obj.file_name)  + Bcolors.RESET )


######################
# demucs
######################

# You cannot set both `float32 = True` and `int24 = True` !!

def find_files(inp):
    out = []
    for file in Path(inp).iterdir():
        if file.suffix.lower().lstrip(".") in extensions:
            out.append(file)
    return out

def copy_process_streams(process: sp.Popen):
    def raw(stream: Optional[IO[bytes]]) -> IO[bytes]:
        assert stream is not None
        if isinstance(stream, io.BufferedIOBase):
            stream = stream.raw
        return stream

    p_stdout, p_stderr = raw(process.stdout), raw(process.stderr)
    stream_by_fd: Dict[int, Tuple[IO[bytes], io.StringIO, IO[str]]] = {
        p_stdout.fileno(): (p_stdout, sys.stdout),
        p_stderr.fileno(): (p_stderr, sys.stderr),
    }
    fds = list(stream_by_fd.keys())

    while fds:
        # `select` syscall will wait until one of the file descriptors has content.
        ready, _, _ = select.select(fds, [], [])
        for fd in ready:
            p_stream, std = stream_by_fd[fd]
            raw_buf = p_stream.read(2 ** 16)
            if not raw_buf:
                fds.remove(fd)
                continue
            buf = raw_buf.decode()
            std.write(buf)
            std.flush()

def separate(files_obj,inp=None, outp=None):

    file_folder_split = Path( OUT_ORIG_SPLIT_PATH  + files_obj.file_name )

    inp = inp or file_folder_split
    outp = outp or DEMUCS_PROCESSED_PATH

    cmd = ["python3", "-m", "demucs.separate", "-o", str(outp), "-n", MODEL]
    if MP3:
        cmd += ["--mp3", f"--mp3-bitrate={MP3_RATE}"]
    if FLOAT32:
        cmd += ["--float32"]
    if INT24:
        cmd += ["--int24"]
    if TWO_STEMS is not None:
        cmd += [f"--two-stems={TWO_STEMS}"]
    files = [str(f) for f in find_files(inp)]
    if not files:
        print(f"No valid audio files in {OUT_ORIG_SPLIT_PATH}")
        return
    print("Going to separate the files:")
    print('\n'.join(files))
    print("With command: ", " ".join(cmd))
    p = sp.Popen(cmd + files, stdout=sp.PIPE, stderr=sp.PIPE)
    copy_process_streams(p)
    p.wait()
    if p.returncode != 0:
        print("Command failed, something went wrong.")
    rmtree(file_folder_split)
    rmtree(DEMUCS_PROCESSED_PATH)

def order_demucs_out(files_obj):
    """
    Función que ordena los archivos separados por Demucs y los concatena en un solo archivo.

    La función busca todos los archivos vocales separados por Demucs,
    los ordena alfabéticamente y los concatena en un solo archivo
    llamado "output.mp3".
    """
    # Ruta al directorio que contiene los directorios a unir
    mp3_files_demucs = Path( DEMUCS_PROCESSED_PATH + "htdemucs/" )

    # Obtener la lista de nombres  directorios
    dir_list = os.listdir(mp3_files_demucs)

    # vamos a guardar una lista de la ruta completa de los archivos vocals.mp3
    files_to_concat = []

    # verificamos si existe el archivo vocals.mp3 y construimos la ruta completa
    for directorio in dir_list:
        file_list = os.path.join(mp3_files_demucs, directorio)
        if os.path.exists(os.path.join(file_list, 'vocals.mp3')):
            files_to_concat.append(os.path.join(mp3_files_demucs, directorio, 'vocals.mp3'))
    sorted_files = sorted(files_to_concat, key=extraer_numero)
    concat_ffmpeg (sorted_files,files_obj)

def extraer_numero(cadena):
    """
    Función auxiliar que extrae el número de una cadena de texto.

    La función toma una cadena de texto que contiene un número y lo extrae como entero.

    Argumentos:
    cadena (str): La cadena de texto que contiene el número.

    Retorna:
    int: El número extraído como entero.
    """
    return int(re.search(r'\d+', cadena).group())

def concat_ffmpeg(sorted_files,files_obj):
    """
    Concatena varios archivos de audio en un solo archivo de audio utilizando FFmpeg.

    Args:
    - sorted_files (list): una lista de cadenas que representan
    los nombres de archivo ordenados por orden de aparición en
    el archivo de salida concatenado.

    Returns:
    - None

    Raises:
    - subprocess.CalledProcessError: si FFmpeg devuelve un código de salida no cero.

    """
    # Unir los nombres de archivo en una sola cadena separada por |
    concat_string = '|'.join(sorted_files)

    # # Definir los argumentos del comando FFmpeg
    ffmpeg_args = [
    'ffmpeg',
    '-i', f'concat:{concat_string}',
    '-acodec', 'copy',
    str(Path(ORIG_FINISHED_CONVERTED, files_obj.file_name + "_ok" + '.mp3'))
    ]

    # # Ejecutar el comando usando subprocess.run()
    sp.run(ffmpeg_args, check=True)
    rename_file_convert(files_obj)

def init_app():

    """Comprueba si hay archivos mp3 para convertir"""
    sp.run(["clear"],check=True)
    sp.run(["toilet", "-f","future","*******"],check=True)
    sp.run(["toilet", "-f","future","Demucs"],check=True)
    sp.run(["toilet", "-f","future","*******"],check=True)

    file = original_file()

    if file:
        files_obj = Files(file)
        # original_file()
        # original_split(files_obj)
        # separate(files_obj)
        order_demucs_out(files_obj)


init_app()

