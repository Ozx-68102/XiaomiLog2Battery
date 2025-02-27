from flask import Blueprint, redirect, request, render_template, url_for, Response, jsonify

from Modules.Core.ApplicationCore import upload_zip_files

bp = Blueprint("WebPanel", __name__)


@bp.route("/")
def root() -> Response:
    return redirect(url_for("WebPanel.home"))


@bp.route("/home")
def home() -> str:
    return render_template("home.html")


@bp.route("/upload-zip-file", methods=["POST"])
def upload_zip_file() -> tuple[Response, int]:
    if "files" not in request.files:
        error_text = {
            "msg": "Failed to upload zip file.",
            "ErrorType": "Empty File List",
            "reason": "No files uploaded."
        }
        return jsonify(error_text), 400

    files = request.files.getlist("files")  # get files from uploading
    return upload_zip_files(files=files)
#
#
# @bp.route("/initialize-data", methods=["POST"])
# def initialize_data() -> tuple[Response, int]:
#     files = request.files.getlist("files")
#     return initialize(files=files)
