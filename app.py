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
    file_obj = request.files['0']
    conversation = str(uuid.uuid4())
    convo_dir = os.path.join("conversations", conversation)
    zip_filepath = convo_dir + "_zip"
    file_obj.save(zip_filepath)
    convo_transcript = None
    if zipfile.is_zipfile(zip_filepath):
        with zipfile.ZipFile(zip_filepath) as z:
            os.mkdir(convo_dir)
            z.extractall(convo_dir)
            for p in os.listdir(convo_dir):
                if p.endswith(".txt"):
                    convo_transcript = os.path.join(convo_dir, p)

    # Assumed to have a txt file at this point
    if convo_transcript is None:
        return jsonify({"success": False, "error_message": "No transcript found"})

    try:
        parsed_items, persons_list = get_parsed_file(convo_transcript)
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
