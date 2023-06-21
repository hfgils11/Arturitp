from tkinter import *
import cv2
from PIL import Image, ImageTk
import io
import dlib
import imutils
from scipy.spatial import distance as dist
from imutils import face_utils

'''
Dimensiones de la ventana Tkinter
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 1024
'''

face_cascade = cv2.CascadeClassifier(
    'haarcascades/haarcascade_frontalface_default.xml')

# Inicializar la captura de video
cap = cv2.VideoCapture(0)

# Crear la ventana Tkinter
root = Tk()
root.title("Verificación de Identidad")
#root.iconbitmap("img/RMS.ico")  # Establecer un ícono en la ventana
root.geometry("600x800")  # Establecer tamaño predeterminado de la ventana WxH
root.resizable(True, True)  # No permitir la modificación de la ventana
# root.configure(bg='white')  # color de fondo de la ventana: blanco

# Crear un widget Label para mostrar la imagen de RMS
imagenRMS = Image.open("img/LOGO-RMS.png")
imagen1Resize = imagenRMS.resize((230, 124), Image.LANCZOS)  # WxH
img = ImageTk.PhotoImage(imagen1Resize)
fondo = Label(root, image=img).place(x=0, y=610)
# Crear un widget Label para mostrar la imagen de MTS
imagenMTS = Image.open("img/LOGO-MTS.png")
imagen2Resize = imagenMTS.resize((230, 124), Image.LANCZOS)  # WxH
img2 = ImageTk.PhotoImage(imagen2Resize)
fondo = Label(root, image=img2).place(x=378, y=610)

# Crear un widget Label para mostrar la imagen
label = Label(root)
label.pack()

# Función para actualizar la imagen mostrada en el widget Label
def update_image():
    # Capturar un fotograma del video
    ret, frame = cap.read()
    if ret:
        # Convertir el fotograma en una imagen compatible con Tkinter
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)
        image = image.resize((600, 616)) #W x H

        # Convertir a escala de grises
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detectar caras
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        # Dibujar rectángulos alrededor de las caras detectadas
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        # Actualizar la imagen en el widget Label
        photo = ImageTk.PhotoImage(image)
        label.config(image=photo)
        label.image = photo

    # Llamar a esta función de nuevo después de 1 milisegundo
    root.after(1, update_image)

# Llamar a la función para actualizar la imagen
update_image()

# Iniciar el bucle principal de la ventana Tkinter
root.mainloop()

# Detener la captura de video
cap.release()
