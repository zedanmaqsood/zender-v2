import os
import urllib.parse
import string
import ctypes

from flask import Flask, redirect, render_template, send_file
import werkzeug
from flask_restful import reqparse, Api, Resource
from flask_cors import CORS


DATABASE = "./database" # Default path for uploaded files
HOME_PATH = "E:" # Default front page path. Is that how we describe it?


if not os.path.exists(DATABASE):
    os.makedirs(DATABASE)


app = Flask(__name__)
api = Api(app, prefix="/api/")

CORS(app)


def get_drives():
    """Get all available drives in Windows."""
    drives = []
    bitmask = ctypes.windll.kernel32.GetLogicalDrives()
    for letter in string.ascii_uppercase:
        if bitmask & 1:
            drive = f"{letter}:"
            try:
                if os.path.exists(drive):
                    drives.append(drive)
            except:
                pass
        bitmask >>= 1
    return drives


def format_dir(raw_dir):
    """
    This function basically just takes the dir path in the format 'path/to/dir',
    and change it to 'path\\to\\dir', changing '/' to '\\'.
    """
    split_dir = raw_dir.split('/')
    return "\\".join(split_dir)


def change_path(current_path, to_path):
    """This function is called from the jinja HTML thing from index.html when path change is required."""
    if not current_path:
        return to_path
    if to_path == "..": # It means go back.
        redirect = current_path.split('\\')
        return "\\".join(redirect[:-1])
    else:
        to_path_encoded = urllib.parse.quote(to_path)
        return current_path + "\\" + to_path_encoded


def get_path_of_dir(i, dir_name):
    dir_list = dir_name.split('\\')[0:i]
    dir_path = "\\".join(dir_list[:i])
    return dir_path


def separate_file_and_dir(path_to_file):
    path_split = path_to_file.split('/')
    dir_path = "\\".join(path_split[:-1])
    file_name = path_split[-1]
    return dir_path, file_name


#APP call endpoints starts here
@app.route("/")
def home():
    drives = get_drives()
    return render_template('./index.html', files=[], dirs=drives, dir="", change_path=change_path, get_path_of_dir=get_path_of_dir, enumerate=enumerate)


@app.route("/<path:dir>")
def get_directory(dir):
    try:
        dir = format_dir(dir)
        
        try:
            pathWalker = "//".join(dir.split('\\')) + "//" 
            os.chdir(pathWalker)
        except:
            print("Directory change failed")

        files = [f for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f)) and not os.path.islink(os.path.join(dir, f))]
        dirs = [f for f in os.listdir(dir) if os.path.isdir(os.path.join(dir, f)) and not os.path.islink(os.path.join(dir, f))]

        return render_template('./index.html', files=files, dirs=dirs, dir=dir, change_path=change_path, get_path_of_dir=get_path_of_dir, enumerate=enumerate)

    except FileNotFoundError:
        return 404


@app.route("/download/<path:path_to_file>", methods=['GET'])
def download(path_to_file):
    dir_path, file_name = separate_file_and_dir(path_to_file)
    # print(f"\nPath - {dir_path}\nFile - {file_name}\n")
    try:
        return send_file(path_to_file, download_name=file_name)
        # return send_from_directory(dir_path, file_name, as_attachment=True)
    except FileNotFoundError:
        return 404



#REst API classes
class UploadFiles(Resource):
    def post(self):
        parse = reqparse.RequestParser()
        parse.add_argument('files', type=werkzeug.datastructures.FileStorage, required=True, location='files', action='append')
        parse.add_argument('current_dir', type=str, location='form')
        args = parse.parse_args()

        files = args['files']
        current_dir_encoded = args.get('current_dir', DATABASE)

        current_dir = urllib.parse.unquote(current_dir_encoded)

        if not os.path.exists(current_dir):
            return {"error": "Directory does not exist"}, 400

        uploaded_files = []
        for file in files:
            try:
                file_path = os.path.join(current_dir, file.filename)
                file.save(file_path)
                uploaded_files.append(file.filename)
            except Exception as e:
                return {"error": f"Failed to upload {file.filename}: {str(e)}"}, 500

        return f"{file.filename} sent successfully", 201


# class DownloadFile(Resource):

#     # I don't know why this is still here. 
#     def get(self, dir):
#         filename = f"{dir}"
#         try:
#             return send_from_directory(DATABASE, filename, as_attachment=True)
#         except FileNotFoundError:
#             return 404



# Add the class UploadFiles and return its functions for ep /api/upload. This comment seems useless.
api.add_resource(UploadFiles, '/upload')

# api.add_resource(DownloadFile, '/download') #Useless.. for now atleast.


# run the app only if __name__ == '__main__'. If you don't know this, please leave. You have no business here. I'm jk ;). This is how we learn.
if __name__ == '__main__':
    # app.run()  # For LocalHost. Only for debugging. And perhaps for copying files from your own computer. Now, why would you do that?
    app.run(host="0.0.0.0") #For Local Network

    