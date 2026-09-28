from flask import Flask
from database import db

from layered_architecture.routes.Lista_canchas import Canchas_bp


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"]=("mysql+mysqlconnector://user:password@localhost:3306/proyectobackend")

db.init_app(app)

BASE_URL='/api/v1'


app.register_blueprint(Canchas_bp, url_prefix=BASE_URL)

if __name__=='__main__':
    app.run(debug=True, port=5000) 


