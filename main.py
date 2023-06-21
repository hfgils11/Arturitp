from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials
import cv2
import json
import io
import dlib
import imutils
from scipy.spatial import distance as dist
from imutils import face_utils
import requests
import serial

#import RPi.GPIO as GPIO
import time

frameWidth = 640
frameHeight = 480

#GPIO.setwarnings(False)
# Configurar Numeración de los pines
#GPIO.setmode(GPIO.BOARD)

# Cofigurar pin de salida. Set initial state
#GPIO.setup(7, GPIO.OUT, initial=GPIO.LOW)
#GPIO.setup(5, GPIO.OUT, initial=GPIO.LOW)
person_id = ""


# Configurar las credenciales de la API de Face
KEY = '86dc835fd3f244c48333c02bd918aa65'
ENDPOINT = 'https://eastus2.api.cognitive.microsoft.com/'

ENDPOINT_CLARITA = 'https://obapicorev120230126192930.azurewebsites.net/Clarita/api/InvitacionPorAprobar'

face_client = FaceClient(ENDPOINT, CognitiveServicesCredentials(KEY))

# Configurar la fuente de video


cap = cv2.VideoCapture(0) 
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
#blink_thresh = 0.45
blink_thresh = 0.35
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

while 1:
    #time.sleep(0.2)
    ret, frame = cap.read()
    # # If the video is finished then reset it
    # # to the start
    # if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(
    #         cv2.CAP_PROP_FRAME_COUNT):
    #     cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    # else:
    #     _, frame = cap.read()
    if ret:
        frame = imutils.resize(frame, width=640)

        # converting frame to gray scale to
        # pass to detector
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
                #print("Blink detected")
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
                            person = face_client.person_group_person.get('7eed68c8-09d9-4c11-a963-fc9305d266f8', person_id)
                            #print('Persona detectada: {}'.format(person.name))
                            params = {
                                    'documento': format(person.name),
                                    'estado': 1,
                                    'rol':2,
                                    'usuario':32
                                    }
                            response = requests.get(ENDPOINT_CLARITA, params=params).json()
                        
                            json_response = json.loads(response)
                            
                           # GPIO.output(7, GPIO.LOW)
                            #GPIO.output(5, GPIO.LOW)
                                 
                            if(json_response[0]['Error_Desc']==''):
                                with serial.Serial("/dev/ttyUSB0", 9600, timeout=1) as arduino:
                                    time.sleep(0.1) #wait for serial to open
                                    cv2.putText(frame, 'Bienvenido'+json_response[0]['INV_NOMBRE']+' '+json_response[0]['INV_APELLIDO'], (30, 30),cv2.FONT_HERSHEY_DUPLEX, 1, (0, 200, 0), 1)
                                    #GPIO.output(7,GPIO.HIGH)
                                    
                                    print(json_response[0]['INV_NOMBRE']+' '+json_response[0]['INV_APELLIDO']+' '+ json_response[0]['INV_FECHA'])
                                    #time.sleep(0.5)
                                    #GPIO.output(7,GPIO.LOW)
                                    #time.sleep(1)
                                    if arduino.isOpen():
                                        datos = "1"
                                        arduino.write(datos.encode())
                                
                            else:
                                #GPIO.output(7, GPIO.LOW)
                                #GPIO.output(5, GPIO.LOW)
                                #print(json_response[0]['Error_Desc'])
                                print('No se reconoce la persona')
                                cv2.putText(frame, 'PERSONA NO RECONOCIDA', (30, 30),cv2.FONT_HERSHEY_DUPLEX, 1, (255, 0, 0), 1)
                          
                        except:
                            print('NO TE RECONOZCO')
                            #GPIO.output(7, GPIO.LOW)
                            #GPIO.output(5, GPIO.LOW)
                            cv2.putText(frame, 'PERSONA NO RECONOCIDA', (30, 30),cv2.FONT_HERSHEY_DUPLEX, 1, (200, 0, 0), 1)
            else:
                if count_frame >= succ_frame:
                    cv2.put(frame, 'Blink Detected', (30, 30),
                            cv2.FONT_HERSHEY_DUPLEX, 1, (0, 200, 0), 1)
                else:
                    count_frame = 0
        #cv2.namedWindow('Video', cv2.WINDOW_NORMAL)
        #cv2.resizeWindow('Video', 800, 600)

        cv2.imshow("Video", frame)
        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

# Liberar la fuente de video y cerrar la ventana
cap.release()
cv2.destroyAllWindows()
