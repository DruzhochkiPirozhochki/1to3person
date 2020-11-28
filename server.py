from flask import Flask, request, jsonify

from transform import transform_text

server = Flask(__name__);

@server.route('/send', methods=['POST'])
def send():
    print("POST /send request")

    # obtaining passed args
    fname = request.json['fname']
    text = request.json['text']
    print(f"fname = {fname}\ntext = {text}")

    # updating the text
    text = f"{transform_text(text, 'Masc', fname)}"

    # sending back updated text
    return jsonify({'text': text})


if (__name__ == '__main__'):
    server.run(host='0.0.0.0', port='8080', debug=True)
