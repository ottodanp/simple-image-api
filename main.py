import mimetypes
from os import mkdir, listdir
from os.path import exists, join, splitext
from typing import Dict

from flask import Flask, Response, request, jsonify, render_template

app = Flask(__name__)

FILE_EXTENSIONS = [".jpg", ".png", ".jpeg"]
BANNED_EXPRESSIONS = ["../"]


def get_all_images(filepath: str) -> Dict[str, str]:
    return {
        item.split(".")[0]: item
        for item in listdir(filepath)
        if any(item.endswith(ext) for ext in FILE_EXTENSIONS)
    }


def filesystem_setup():
    if not exists("graphs"):
        mkdir("graphs")


def sanitize_filename(filename: str) -> str:
    for expression in BANNED_EXPRESSIONS:
        filename = filename.replace(expression, "")
    return filename


@app.route("/graph")
def graph():
    args = request.args
    graph_id = args.get("graph_id")
    if graph_id is None:
        return "No graphID", 400

    images = get_all_images("graphs")
    image_name = images.get(graph_id)
    if image_name is None:
        return "Bad image name", 404

    filepath = f"graphs/{image_name}"
    mime_type = mimetypes.guess_type(filepath)[0] or "application/octet-stream"

    with open(filepath, "rb") as f:
        image_data = f.read()

    return Response(image_data, mimetype=mime_type)


@app.route("/all_graphs")
def all_graphs():
    filesystem_setup()
    return get_all_images("graphs")


@app.route("/upload_image", methods=["POST"])
def upload_image():
    # Get list of uploaded files
    files = request.files.getlist("files")

    if not files:
        return jsonify({"message": "No files uploaded"}), 400

    saved_files = []
    for file in files:
        filename = sanitize_filename(file.filename)
        ext = splitext(filename)[1].lower()

        if ext not in FILE_EXTENSIONS:
            return jsonify({"message": f"Invalid file type: {filename}"}), 400

        filepath = join("graphs", filename)
        file.save(filepath)
        saved_files.append(filename)

    return jsonify({"message": f"Uploaded {len(saved_files)} file(s): {', '.join(saved_files)}"})


@app.route("/upload")
def upload():
    return render_template("upload.html")


if __name__ == '__main__':
    filesystem_setup()
    app.run(host="0.0.0.0", port=80, debug=True)

