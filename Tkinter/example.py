import cv2
import tkinter as tk
from PIL import Image, ImageTk

face_cascade = cv2.CascadeClassifier(
    "haarcascades/haarcascade_frontalface_default.xml")

root = tk.Tk()
root.geometry("800x600")
label = tk.Label(root)
label.pack()

def process_video():
    # Capturar video desde la cámara
    cap = cv2.VideoCapture(0)

    while True:
        
        # Leer un frame del video
        ret, frame = cap.read()

        # Convertir a escala de grises
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detectar caras
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        
        # Dibujar rectángulos alrededor de las caras detectadas
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
        # Convertir la imagen procesada a un formato que Tkinter pueda mostrar
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)
        image = ImageTk.PhotoImage(image)

        # Actualizar la GUI
        label.config(image=image)
        label.image = image
        root.update()

        # Salir si se presiona la tecla "q"
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Liberar recursos
    cap.release()
    cv2.destroyAllWindows()

process_video()
