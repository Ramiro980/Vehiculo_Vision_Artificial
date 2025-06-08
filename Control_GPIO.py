import RPi.GPIO as GPIO
import time

#Declaracion de variables globales
stby = 23

Motores = 24

En_D = 17
In_D1 = 27
In_D2 = 22

Line_1 = 5
Line_2 = 6

P_M = None
P_D = None

def Config_GPIO():
    global P_D,P_M
    #Configurando canales
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    GPIO.setup(stby,GPIO.OUT)

    #Motores ruedas
    GPIO.setup(Motores,GPIO.OUT)

    #Motor direccion
    GPIO.setup(En_D,GPIO.OUT)
    GPIO.setup(In_D1,GPIO.OUT)
    GPIO.setup(In_D2,GPIO.OUT)

    #seguidor de lineas
    GPIO.setup(Line_1,GPIO.IN)
    GPIO.setup(Line_2,GPIO.IN)

    #Configuracion PWM
    P_M = GPIO.PWM(Motores,55)
    P_D = GPIO.PWM(En_D,1000)

    #Iniciar PWM con ciclo de trabajo (duty cycle) del 20%
    P_M.start(0)
    P_D.start(40)    


def Control(Ctrl):
    global P_D

    if Ctrl == 'D':
        GPIO.output(stby,GPIO.HIGH)
        print("Derecha")
        GPIO.output(In_D1,GPIO.LOW)
        GPIO.output(In_D2,GPIO.HIGH)
        time.sleep(1)
        GPIO.output(In_D2,GPIO.LOW)
        GPIO.output(stby,GPIO.LOW)

    elif Ctrl == 'I':
        GPIO.output(stby,GPIO.HIGH)
        print("Izquierda")
        GPIO.output(In_D1,GPIO.HIGH)
        GPIO.output(In_D2,GPIO.LOW)
        time.sleep(1)
        GPIO.output(In_D1,GPIO.LOW)
        GPIO.output(stby,GPIO.LOW)

    elif Ctrl == 'A':
        print("Avanza")
        P_M.ChangeDutyCycle(10.12)
        time.sleep(0.5)

    elif Ctrl == 'R':
        print("Reversa")
        P_M.ChangeDutyCycle(6.95) #6.5 #6.3
        time.sleep(0.5)

    elif Ctrl == 'S':
        print("Stop")
        P_M.ChangeDutyCycle(0)
        time.sleep(0.5)


def Seguidor():
    GPIO.output(stby,GPIO.HIGH)

    #Seguidor de lineas
    if GPIO.input(Line_1) == GPIO.HIGH:
        print("Desviacion hacia la izquierda")
        GPIO.output(In_D2, GPIO.HIGH)
        GPIO.output(In_D1,GPIO.LOW)

    elif GPIO.input(Line_2) == GPIO.HIGH:
        print("Desviacion hacia la derecha")
        GPIO.output(In_D1, GPIO.HIGH)
        GPIO.output(In_D2,GPIO.LOW)

    elif  GPIO.input(Line_1) == GPIO.LOW and GPIO.input(Line_2) == GPIO.LOW:
        print("Sin desviacion")
        GPIO.output(In_D2, GPIO.LOW)
        GPIO.output(In_D1, GPIO.LOW)

    GPIO.output(stby,GPIO.LOW)

def Fin_GPIO():
    P_M.stop()
    P_D.stop()
    GPIO.cleanup()