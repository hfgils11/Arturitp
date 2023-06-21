import cv2 as cv

# Cargar el clasificador pre-entrenado para detección de caras
face_cascade = cv.CascadeClassifier(
    '/home/clarita/Desktop/CV2/haarcascades/haarcascade_frontalface_default.xml')

# Iniciar la cámara
cap = cv.VideoCapture(0)
width = 600
height = 720

while True:
    # Leer la imagen desde la cámara
    ret, frame = cap.read()

    # Convertir la imagen a escala de grises
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

    # Detectar caras en la imagen
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    # Dibujar un rectángulo alrededor de cada cara detectada
    for (x, y, w, h) in faces:
        cv.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
    
    # crear una ventana con nombre
    cv.namedWindow('MiVentana', cv.WINDOW_NORMAL)
    
    # establecer el tamaño de la ventana
    cv.resizeWindow('MiVentana', 600, 720)
    
    resized_frame = cv.resize(frame, (width, height))
    # Mostrar la imagen resultante 
    cv.imshow('MiVentana', resized_frame)

    # Si se detecta una cara, tomar una foto
    # if len(faces) > 0:
    #     for face in enumerate(faces):
    #         roi = frame[y:y+h, x:x+w]
    #         cv2.imwrite('foto.png', roi)
    #     break

    # Salir del bucle si se presiona la tecla 'q'
    if cv.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar la cámara y cerrar todas las ventanas abiertas
cap.release()
cv.destroyAllWindows()
