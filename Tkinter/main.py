from tkinter import *
import cv2
from PIL import Image, ImageTk
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials
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

# Configurar las credenciales de la API de Face
KEY = '86dc835fd3f244c48333c02bd918aa65'
ENDPOINT = 'https://eastus2.api.cognitive.microsoft.com/'
face_client = FaceClient(ENDPOINT, CognitiveServicesCredentials(KEY))

face_cascade = cv2.CascadeClassifier(
    'haarcascades/haarcascade_frontalface_default.xml')

# Inicializar la captura de video
cap = cv2.VideoCapture(0)

# Crear la ventana Tkinter
root = Tk()
root.title("Verificación de Identidad")
#root.iconbitmap("img/RMS.ico")  # Establecer un ícono en la ventana
root.geometry("1080x1920")  # Establecer tamaño predeterminado de la ventana WxH
root.resizable(True, True)  # No permitir la modificación de la ventana
# root.configure(bg='white')  # color de fondo de la ventana: blanco
'''
# Crear un widget Label para mostrar la imagen de RMS
imagenRMS = Image.open("img/LOGO-RMS.png")
imagen1Resize = imagenRMS.resize((210, 50), Image.LANCZOS)  # WxH
img = ImageTk.PhotoImage(imagen1Resize)
fondo = Label(root, image=img).place(x=0, y=974)
# Crear un widget Label para mostrar la imagen de MTS
imagenMTS = Image.open("img/LOGO-MTS.png")
imagen2Resize = imagenMTS.resize((210, 50), Image.LANCZOS)  # WxH
img2 = ImageTk.PhotoImage(imagen2Resize)
fondo = Label(root, image=img2).place(x=390, y=974)
'''
# Crear un widget Label para mostrar la imagen
label = Label(root)
label.pack()

# defining a function to calculate the EAR


def calculate_EAR(eye):
    # calculate the vertical distances
    y1 = dist.euclidean(eye[1], eye[5])
    y2 = dist.euclidean(eye[2], eye[4])
    # calculate the horizontal distance
    x1 = dist.euclidean(eye[0], eye[3])
    # calculate the EAR
    EAR = (y1+y2) / x1
    return EAR


# Variables
blink_thresh = 0.45
succ_frame = 2
count_frame = 0

# Eye landmarks
(L_start, L_end) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(R_start, R_end) = face_utils.FACIAL_LANDMARKS_IDXS['right_eye']

# Initializing the Models for Landmark and
# face Detection
detector = dlib.get_frontal_face_detector()
landmark_predict = dlib.shape_predictor(
    'models/shape_predictor_68_face_landmarks.dat')


# Función para actualizar la imagen mostrada en el widget Label
def update_image():
    # Capturar un fotograma del video
    ret, frame = cap.read()

    if ret:

        #
        img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # detecting the faces
        faces = detector(img_gray)
        for face in faces:
            # landmark detection
            shape = landmark_predict(img_gray, face)
            # converting the shape class directly
            # to a list of (x,y) coordinates
            shape = face_utils.shape_to_np(shape)
            # parsing the landmarks list to extract
            # lefteye and righteye landmarks--#
            lefteye = shape[L_start: L_end]
            righteye = shape[R_start:R_end]
            # Calculate the EAR
            left_EAR = calculate_EAR(lefteye)
            right_EAR = calculate_EAR(righteye)
            # Avg of left and right eye EAR
            avg = (left_EAR+right_EAR)/2
            if avg < blink_thresh:
                # cv2.waitKey(2000)
                print("Blink detected")
                # cv2.imshow("Video", frame)
                # cv2.waitKey(200)
                # count_frame += 1  # incrementing the frame count
                ret, buffer = cv2.imencode('.jpg', frame)
                image_bytes = buffer.tobytes()
                # Crear un objeto io.BytesIO a partir de los bytes de la imagen
                image_stream = io.BytesIO(image_bytes)
                # Detectar caras en la imagen
                faces = face_client.face.detect_with_stream(
                    image_stream, recognition_model='recognition_04')
                # Reconocer las caras detectadas
                for face in faces:
                    results = face_client.face.identify(
                        [face.face_id],
                        person_group_id='7eed68c8-09d9-4c11-a963-fc9305d266f8',
                        max_num_of_candidates_returned=1,
                        confidence_threshold=0.5
                    )
                    # Mostrar el nombre de la persona si se reconoce
                    if len(results) > 0:
                        try:
                            person_id = results[0].candidates[0].person_id
                            person = face_client.person_group_person.get(
                                '7eed68c8-09d9-4c11-a963-fc9305d266f8', person_id)
                            print('Persona detectada: {}'.format(person.name))
                        except:
                            print('NO TE RECONOZCO')
                            cv2.putText(frame, 'PERSONA NO RECONOCIDA', (30, 30),
                                        cv2.FONT_HERSHEY_DUPLEX, 1, (0, 200, 0), 1)
            # else:
            #     if count_frame >= succ_frame:
            #         cv2.put(frame, 'Blink Detected', (30, 30),
            #                 cv2.FONT_HERSHEY_DUPLEX, 1, (0, 200, 0), 1)
            #     else:
            #         count_frame = 0
        #

        # Convertir el fotograma en una imagen compatible con Tkinter
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)
        image = image.resize((1080, 1920))

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
