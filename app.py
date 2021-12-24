from flask import Flask, request, jsonify, render_template

from models import db, connect_db

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///cupcakes'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "p-word-here-shhhhh"

connect_db(app)

@app.route("/")
def root():
    """Homepage"""