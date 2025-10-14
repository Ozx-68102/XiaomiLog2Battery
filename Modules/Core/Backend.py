# from Modules.Core.sha256Validator import SHA256Validator, _get_file_storage_size

# HASH_VALIDATE = SHA256Validator()



# def _save_file(file: FileStorage, specified_path: str, overwrite: bool = False) -> None:
#     filepath = os.path.join(specified_path, secure_filename(file.filename))
#     if not overwrite and os.path.exists(filepath):
#         raise FileExistsError(f"File '{file.filename}' has already exists in path '{specified_path}'.")
#
#     # 'file.save' command will automatically overwrite files with the same name by default, but I don't want it to do that.
#     try:
#         with open(filepath, "wb" if overwrite else "xb") as f:
#             file.stream.seek(0)
#             while chunk := file.stream.read(2 ** 20):
#                 f.write(chunk)
#             file.stream.seek(0)
#     except Exception:
#         if os.path.exists(filepath):
#             os.remove(filepath)
#         raise


# def _remove_duplicate_element(
#         a: list[dict[str, str | int | bool]],
#         b: list[dict[str, str | int | bool]]
# ) -> list[dict[str, str | int]]:
#     a_sha256s = {item["sha256"] for item in a}
#     b_sha256s = {item["sha256"] for item in b}
#
#     duplicate = a_sha256s & b_sha256s
#
#     filtered_a = [item for item in a if item["sha256"] not in duplicate]
#     filtered_b = [item for item in b if item["sha256"] not in duplicate]
#
#     return filtered_a + filtered_b


# def upload_and_verify(files: list[FileStorage]) -> tuple[dict[str, bool | str | list[dict[str, str | int]] | None], int]:
#     save_path = os.path.join(current_app.instance_path, "uploads")
#     os.makedirs(name=save_path, exist_ok=True)
#
#     results = {
#         "need_confirmation": False,
#         "confirmation_id": None,
#         "success": [],  # {"filename":..., "sha256":..., "filesize":...}
#         "error": []  # {"filename":..., "reason":...}
#     }
#
#     confirm_id = str(uuid.uuid4())
#     pending_data = []
#
#     for file in files:  # TODO: batch process
#         if not file or len(file.filename) == 0:
#             results["error"].append({"filename": file.filename, "reason": "no valid filename"})
#             continue
#
#         try:
#             # calculate hash and filesize
#             file_hash = HASH_VALIDATE.generate_file_storage_hash(file=file)
#             size = _get_file_storage_size(file=file)
#
#             # check if file exists in two platform
#             if_file_exists_in_fs = os.path.exists(os.path.join(save_path, file.filename))
#             if_file_recorded_in_db = FileUploaded.query(sha256=file_hash)
#
#             if if_file_recorded_in_db:
#                 # situation 1: both exists
#                 if if_file_exists_in_fs:
#                     pending_data.append({
#                         "filename": file.filename,
#                         "sha256": file_hash,
#                         "filesize": size
#                     })
#
#                 # situation 2: file does not exist in file system, but exists in database
#                 else:
#                     _save_file(file=file, specified_path=save_path)
#                     filedict = {"filename": file.filename, "sha256": file_hash, "filesize": size}
#                     FileUploaded.overwrite(filelist=[filedict])
#                     results["success"].append(filedict)
#             else:
#                 # situation 3: file does not exist in database, but exists in file system
#                 if if_file_exists_in_fs:
#                     _save_file(file=file, specified_path=save_path, overwrite=True)
#                     FileUploaded.create(filename=file.filename, sha256=file_hash, filesize=size)
#                     results["success"].append({
#                         "filename": file.filename,
#                         "sha256": file_hash,
#                         "filesize": size
#                     })
#
#                 # situation 4: both not exists
#                 else:
#                     _save_file(file=file, specified_path=save_path)
#                     FileUploaded.create(filename=file.filename, sha256=file_hash, filesize=size)
#                     results["success"].append({
#                         "filename": file.filename,
#                         "sha256": file_hash,
#                         "filesize": size
#                     })
#         except Exception as e:
#             results["error"].append({
#                 "filename": file.filename,
#                 "reason": str(e)
#             })
#             continue
#
#     if pending_data:
#         current_app.cache.set(
#             key=f"pending:{confirm_id}",
#             value=json.dumps(pending_data),
#             expire=600    # 10 minutes
#         )
#
#         results.update({
#             "need_confirmation": True,
#             "confirmation_id": confirm_id,
#         })
#
#     status_code = 200 if results["success"] or pending_data else 400
#
#     return results, status_code
#
#
# def get_duplicate_data(cid: str) -> tuple[dict[str, str | list[dict[str, str | int]]], int]:
#     cache_key = f"pending:{cid}"  # must be similar with what I set it
#     duplicate_data_json = current_app.cache.get(key=cache_key)
#
#     if not duplicate_data_json:
#         error_text = {"error": "Invalid confirmation id, maybe the data is expired."}
#         return error_text, 404
#
#     try:
#         duplicate_data = json.loads(duplicate_data_json)
#         if not isinstance(duplicate_data, list):
#             raise ValueError("Invalid cache data format.")
#
#         sha256s = [item["sha256"] for item in duplicate_data]
#         data_info = FileUploaded.batch_query(sha256_list=sha256s)
#     except (json.JSONDecodeError, ValueError, Exception) as e:
#         error_text = {"error": str(e)}  # TODO:  maybe I can try "current_app.logger" to record log
#         return error_text, 500
#
#     if not data_info:
#         error_text = {"error": "No valid data found in database."}
#         return error_text, 404
#
#     results = {"data": data_info}
#
#     return results, 200
#
#
# def overwrite_duplicate_data(
#         selected_file_info: list[dict[str, str | int | bool]] | None,
#         cid: str
# ) -> tuple[dict[str, str | list[dict[str, str]] | dict[str, list[dict[str, str | int]]]], int]:
#     cache_key = f"pending:{cid}"
#     duplicate_data_json = current_app.cache.get(key=cache_key)
#
#     results = {
#         "success": {
#             "overwrite": [],
#             "skip": []
#         },
#         "error": []
#     }
#
#     if not duplicate_data_json:
#         error_text = {"error": "Invalid confirmation id, maybe the data is expired."}
#         return error_text, 404
#
#     try:
#         duplicate_data = json.loads(duplicate_data_json)
#         if not isinstance(duplicate_data, list):
#             raise ValueError("Invalid cache data format.")
#     except (json.JSONDecodeError, ValueError) as e:
#         error_text = {"error": str(e)}
#         return error_text, 500
#
#     if len(selected_file_info) == 0:
#         for data in duplicate_data:
#             results["success"]["skip"].append(data)
#
#         if not current_app.cache.delete(key=cache_key):
#             error_text = {f"padding:{cid}": "Program can not delete it, maybe the data doesn't exist or is expired."}
#             results["error"].append(error_text)
#     else:
#         selected_file_list = [{key: value for key, value in item.items() if key not in
#                                ["id", "selected", "upload_time", "filetype"]} for item in selected_file_info]
#         FileUploaded.overwrite(filelist=selected_file_list)
#
#
#         # len(selected_file_info) <= len(duplicate_data)
#         skip_data = _remove_duplicate_element(a=selected_file_info, b=duplicate_data)
#
#         if skip_data is not None:
#             for data in skip_data:
#                 results["success"]["skip"].append(data)
#
#         for data in selected_file_list:
#             results["success"]["overwrite"].append(data)
#
#         if not current_app.cache.delete(key=cache_key):
#             error_text = {f"padding:{cid}": "Program can not delete it, maybe the data doesn't exist or is expired."}
#             results["error"].append(error_text)
#
#     status_code = 200 if results["success"]["overwrite"] or results["success"]["skip"] else 400
#
#     return results, status_code
#
#
# def extract_specific_files():
#     target_path = os.path.join(current_app.instance_path, "uploads")
#
#     files = [
#         os.path.join(target_path, dirs) for dirs in os.listdir(target_path)
#         if dirs.startswith("bugreport") and dirs.endswith(".zip")
#     ]
#
#     ble = BatteryLoggingExtractor()
#     data, status = ble.decompress_xiaomi_log(files=files)
#     # TODO: not complete
