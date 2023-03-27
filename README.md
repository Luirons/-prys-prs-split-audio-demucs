# Demucs Divide Audio

1- Instalar
2- El *archivo original* va a la carpeta `./in-file`
3- El *archivo original* es separado en partes para poder ser procesado por
demucs y se guarda en `orig-finished-processed`.Esto es por la capacidad de procesamiento de tu hardware
4- Separamos la voz del sonido de fondo y la guardamos en la carpeta `./out-file/htdemucs/nombre del archivo original/nombre archivo original_xx`
5- Eliminamos los archivos separados de la carpeta `./orig-split` y movemos el archivo *archivo original* a `./in-file/orig-finished-processed` y lo renombramos agregandole la palabra *_ok*


