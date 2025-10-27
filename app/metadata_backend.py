from flask import Flask, render_template
import jwt, time

app = Flask(__name__)

@app.route("/")
def reporte():
    payload = {
        "resource": {"question": 38},
        "params": {},
        "exp": round(time.time()) + (60 * 10)
    }
    token = jwt.encode(payload, "tu_clave_secreta", algorithm="HS256")
    iframe_url = f"http://localhost:3000/embed/question/{token}#bordered=true&titled=true"
    return render_template("../templates/reporte.html", iframe_url=iframe_url)