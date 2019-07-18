import os
import uuid
import zipfile

from flask import (Flask,
                   request,
                   render_template,
                   jsonify,
                   send_from_directory)

from utils import get_parsed_file

app = Flask(__name__)


@app.route('/parse-file', methods=['POST'])
def parse_file():
    file = request.files['0']
    filename = str(uuid.uuid4())
    tmp_filepath = os.path.join("conversations", filename)
    file.save(tmp_filepath)
    conversation = ""
    if zipfile.is_zipfile(tmp_filepath):
        conversation = filename
        with zipfile.ZipFile(tmp_filepath) as z:
            conv_path = os.path.join("conversations", filename)
            z.extractall(conv_path)
            for p in os.listdir(conv_path):
                if p.endswith(".txt"):
                    tmp_filepath = os.path.join(conv_path, p)

    try:
        parsed_items, persons_list = get_parsed_file(tmp_filepath)
        response = {
            "identifier": conversation,
            "success": True,
            "chat": parsed_items,
            "users": persons_list
        }
    except Exception as e:
        response = {
            "success": False,
            "error_message": str(e)
        }

    os.remove(tmp_filepath)
    return jsonify(response), 200


@app.route('/', methods=['GET'])
def main():
    return render_template("index.html")

@app.route('/conversations/<path:path>')
def send_js(path):
    conversation, img = os.path.split(path)
    return send_from_directory(os.path.join('conversations', conversation), img)


@app.errorhandler(404)
def not_found(e):
    message = "404 We couldn't find the page"
    return render_template("index.html", error_message=message)


if __name__ == "__main__":
    IS_PROD = os.environ.get("IS_PROD", False)
    app.run(debug=not IS_PROD, host="0.0.0.0", threaded=True)
