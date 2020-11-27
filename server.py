from flask import Flask, request, jsonify

server = Flask(__name__);

@server.route('/send', methods=['POST'])
def send():
    print("POST /send request")

    # obtaining passed args
    fname = request.json['fname']
    text = request.json['text']
    print(f"fname = {fname}\ntext = {text}")

    # updating the text
    text += "\n\nTHIS TEXT WAS UPDATED"

    # sending back updated text
    return jsonify({'text': text})


if (__name__ == '__main__'):
    server.run(debug=True)
