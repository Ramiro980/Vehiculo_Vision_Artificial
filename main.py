from flask import Flask, render_template, Response, jsonify
import Control_GPIO
import Vision_Cam

app = Flask(__name__)

Video = Vision_Cam.Camara()
Control_GPIO.Config_GPIO()

def Imagen():
    return Vision_Cam.Procesamiento_Im(Video)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/vide_feed")
def video_feed():
    return Response(Imagen(),mimetype = "multipart/x-mixed-replace; boundary=frame")

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0',port=5000)
    finally:
        Control_GPIO.Fin_GPIO()
        Vision_Cam.fin_Vision(Video)