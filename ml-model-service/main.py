from flask import Flask
from routes import register_routes

app = Flask(__name__)

app = register_routes(app)

if __name__ == "__main__":
    # app.run(port=5001, debug=True)
    app.run(host="0.0.0.0", port=5001, debug=True)
