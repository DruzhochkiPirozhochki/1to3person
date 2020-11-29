from flask import Flask, request, jsonify
from flask_cors import CORS

from transform import transform_text

server = Flask(__name__)
cors = CORS(server)
server.config['CORS_HEADERS'] = 'Content-Type'


@server.route('/send', methods=['POST'])
def send():
    print("POST /send request")

    # obtaining passed args
    fname = request.json['fname']
    text = request.json['text']
    print(f"fname = {fname}\ntext = {text}")

    # updating the text
    text, changes = transform_text(text, fname)

    # sending back updated text
    return jsonify({'text': text, "colored": changes})


if (__name__ == '__main__'):
    server.run(host='0.0.0.0', port='8080', debug=True)
