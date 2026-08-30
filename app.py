from flask import Flask, jsonify
import os

app = Flask(__name__)
VERSION = os.getenv("APP_VERSION", "v1")
COLOR   = os.getenv("APP_COLOR", "blue")

@app.route("/")
def home():
    return f"""
    <body style="font-family:sans-serif;text-align:center;padding-top:80px">
      <h1 style="color:{COLOR}">Healthcare Portal</h1>
      <h2>Version: {VERSION} | Environment: {COLOR.upper()}</h2>
    </body>"""

@app.route("/health")
def health():
    return jsonify(status="ok", version=VERSION, env=COLOR)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)  
