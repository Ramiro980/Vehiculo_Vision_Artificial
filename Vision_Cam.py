from picamera2 import Picamera2
import Control_GPIO
import numpy as np
import cv2

#DEFINIMOS RANGOS DE COLOR EN HSV
"Verde --- AVANZAR"
V_bajo = np.array([45,120,120],np.uint8)
V_alto = np.array([75,255,255],np.uint8)

"Rojo ---DETENER"
Rj_bajo1 = np.array([0,190,200],np.uint8)
Rj_alto1 = np.array([8,255,255],np.uint8)

Rj_bajo2 = np.array([172,190,200],np.uint8)
Rj_alto2 = np.array([180,255,255],np.uint8)

"Amarillo --- RETROCEDER"
Am_bajo = np.array([30,100,100],np.uint8)
Am_alto = np.array([45,255,255],np.uint8)

"Azul --- GIRO (IZQUIERDA)"
Az_bajo = np.array([100,150,120],np.uint8)
Az_alto = np.array([130,255,255],np.uint8)

"Naranja --- GIRO (DERECHA)"
Nar_bajo = np.array([10,170,150],np.uint8)
Nar_alto = np.array([20,255,255],np.uint8)

#FUNCION PARA INICIALIZAR LA CAMARA
def Camara():
    Im = Picamera2()
    Im.configure(Im.create_preview_configuration(main={"format": 'XRGB8888', "size":(800,450)}))
    Im.start()
    return Im

#FUNCION PARA EL PROCESAMIENTO DE LA IMAGEN
def Procesamiento_Im(cam):
    while True:
        frame = cam.capture_array()
        frame2 = frame.copy()

        #Cambiamos a BGR mas puro
        frame2 = cv2.cvtColor(frame2,cv2.COLOR_BGRA2BGR)

        #Suavizando la imagen y reduciendo el ruido en la imagen
        Suavizado = cv2.GaussianBlur(frame2,(5,5),0)

        #Conversion de hsv y escala de grises
        HSV = cv2.cvtColor(Suavizado,cv2.COLOR_BGR2HSV)

        #Mascaras binarias de colores definidos
        mask_V = cv2.inRange(HSV,V_bajo,V_alto)
        mask_Rj = cv2.add(cv2.inRange(HSV,Rj_bajo1,Rj_alto1),cv2.inRange(HSV,Rj_bajo2,Rj_alto2))
        mask_Am = cv2.inRange(HSV,Am_bajo,Am_alto)
        mask_Az = cv2.inRange(HSV,Az_bajo,Az_alto)
        mask_Nar = cv2.inRange(HSV,Nar_bajo,Nar_alto)

        mask_final = cv2.add(mask_V,cv2.add(mask_Rj,cv2.add(mask_Am,cv2.add(mask_Az,mask_Nar))))

        #Deteccion de bordes en la mascra final (colores)
        Canny_fig = cv2.Canny(mask_final,75,200)
        Canny_fig = cv2.dilate(Canny_fig,None,iterations=2)
        Canny_fig = cv2.erode(Canny_fig,None,iterations=2)

        Cont,_ = cv2.findContours(Canny_fig,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

        for c in Cont:
            Area = cv2.contourArea(c)

            if Area > 2500:
                epsilon = 0.008 * cv2.arcLength(c,True)
                approx = cv2.approxPolyDP(c,epsilon*2,True)

                x,y,w,h = cv2.boundingRect(approx)

                # MASCARA DEL CONTORNO ACTUAL
                mask_cont = np.zeros(mask_final.shape,dtype=np.uint8)
                cv2.drawContours(mask_cont,[c],-1,255,-1)

                # Cantida de cada color dentro de la figura
                Verde = cv2.countNonZero(cv2.bitwise_and(mask_V,mask_cont))
                Rojo = cv2.countNonZero(cv2.bitwise_and(mask_Rj,mask_cont))
                Amar = cv2.countNonZero(cv2.bitwise_and(mask_Am,mask_cont))
                Azul = cv2.countNonZero(cv2.bitwise_and(mask_Az,mask_cont))
                Nar = cv2.countNonZero(cv2.bitwise_and(mask_Nar,mask_cont))

                umbral_color = 75

                #--- CIRCULOS ---
                if len(approx) > 6:
                    if Verde > umbral_color and Verde > Rojo and Verde > Amar and Verde > Azul and Verde > Nar:
                        print("Circulo verde: Avanza")
                        cv2.putText(frame,'Avanzar',(x,y-5),1,2,(0,255,0),3)
                        cv2.drawContours(frame,[approx],0,(0,255,0),3)
                        Control_GPIO.Control('A')

                    elif Rojo > umbral_color:
                        print("Circulo Rojo: Detente")
                        cv2.putText(frame,'Detener',(x,y-5),1,2,(0,0,255),3)
                        cv2.drawContours(frame,[approx],0,(0,0,255),3)
                        Control_GPIO.Control('S')

                #--- RECTANGULOS Y CUADRADO ---
                if len(approx) == 4:
                    if h != 0:
                        aspect_ratio = float(w)/h

                        if 0.5 <= aspect_ratio <= 2:
                            if Amar > umbral_color:
                                print("Rectangulo Amarillo: Retrocede")
                                cv2.putText(frame,'Retroceder',(x,y-5),1,2,(0,255,255),3)
                                cv2.drawContours(frame,[approx],0,(0,255,255),3)
                                Control_GPIO.Control('R')

                            elif Azul > umbral_color:
                                print("Rectangulo Azul: izquierda")
                                cv2.putText(frame,'Gira a la izquierda',(x,y-5),1,2,(0,255,255),3)
                                cv2.drawContours(frame,[approx],0,(255,0,0),3)
                                Control_GPIO.Control('I')

                        if 0.9 <=aspect_ratio <=1.1:
                            if Nar > umbral_color:
                                print("Cuadrado Naranja: Derecha")
                                cv2.putText(frame,'Gira a la derecha',(x,y-5),1,2,(0,165,255),3)
                                cv2.drawContours(frame,[approx],0,(0,165,255),3)
                                Control_GPIO.Control('D')

        Control_GPIO.Seguidor()
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def fin_Vision(Im):
    Im.stop()
    cv2.destroyAllWindows()