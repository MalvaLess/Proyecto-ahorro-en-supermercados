import os 
from flask import Flask, jsonify
from dotenv import load_dotenv
from models import db

load_dotenv()

app = Flask(__name__)

app.config('DEBUG') = True
app.config('SQLALCHEMY_DATABASE_URI') = os.getenv('DATABASE_URL')
app.confit('SQLALCHEMY_TRACK_MODIFICATIONS') = False

db.init_app(app) # Vinculo las entidades a la app

@app.route('/')
def main():
    return jsonify({
        "status": "connected to postgres"
    }), 200


if __name__ == '__main__':
    app.run()