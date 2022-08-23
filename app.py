from flask import Flask
import os
import socket

app = Flask(__name__)

@app.route("/")
def hello():
  html = "<h3>Hello MOMOSUKE!</h3>"
  return html.format()

if __name__ == "__main__":
  app.run(host='0.0.0.0', port=80)