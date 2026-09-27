import os
from flask import Flask
from source.rutas.canchas import canchas_bp

app = Flask(__name__)

app.register_blueprint(canchas_bp)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
