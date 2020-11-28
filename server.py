from flask import Flask, request, jsonify

from transform import transform_text
from flask_cors import CORS

server = Flask(__name__)
cors = CORS(server)
server.config['CORS_HEADERS'] = 'Content-Type'


@server.route('/send', methods=['POST'])
def send():
    print("POST /send request")

    # obtaining passed args
    fname = request.args['fname']
    text = request.args['text']
    print(f"fname = {fname}\ntext = {text}")

    # updating the text
    text = f"{transform_text(text, 'Masc', fname)}"

    # sending back updated text
    return jsonify({'text': text})


if (__name__ == '__main__'):
    server.run(host='0.0.0.0', port='8080', debug=True)