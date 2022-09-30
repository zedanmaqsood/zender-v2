# from importlib.resources import path
# from email.quoprimime import unquote
# from turtle import down
from flask import Flask, redirect, request, render_template, send_file, send_from_directory
import werkzeug
import os
from flask_restful import reqparse, Api, Resource
from flask_cors import CORS


DATABASE = "./database" # Default path for uploaded files
HOME_PATH = "E:" # Default front page path. Is that how we describe it?


if not os.path.exists(DATABASE):
    os.makedirs(DATABASE)


app = Flask(__name__)
api = Api(app, prefix="/api/")

CORS(app)


def format_dir(raw_dir):

    # this function basically just takes the dir path in the format 'path/to/dir' and change it to 'path\\to\\dir', changing '/' to '\\'.
    
    split_dir = raw_dir.split('/')

    return  "\\".join(split_dir) # returns joining the items in split_dir with '//' in between


def change_path(current_path, to_path):

    #This function is called from the jinja HTML thing from index.html when path change is required.
    
    if to_path == "..": # It means go back.
        
        redirect = current_path.split('\\')

        redirect = "\\".join(redirect[:-1])

    else:

        redirect = current_path + "\\" + to_path

    return redirect


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
def hello_world():

    return redirect(f"/{HOME_PATH}") #Go above to change HOME_PATH


@app.route("/<path:dir>")
def get_directory(dir):

        dir = format_dir(dir) #Perhaps this is useless. I'm too lazy to try. Atleast for now. Using dir as variable is bad btw. Must change.. but later.
        
        try:

            pathWalker = "//".join(dir.split('\\')) + "//" 
            #what a weird name.

            # the below is for that thing were the path doesn't actually change to the required. Happens mostly for F:
            try:
                os.chdir(pathWalker)
            except:
                print("this is no. one bullshit")

            files = [f for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f)) and not os.path.islink(os.path.join(dir, f))]
            dirs = [f for f in os.listdir(dir) if os.path.isdir(os.path.join(dir, f)) and not os.path.islink(os.path.join(dir, f))]

            return render_template('./index.html', files=files, dirs=dirs, dir=dir, change_path=change_path, get_path_of_dir=get_path_of_dir, enumerate=enumerate)

        except FileNotFoundError:
            return 404 # that's sad.


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
    # @auth.login_required
    # def get(self):
    #     return 201

    def post(self):

        parse = reqparse.RequestParser()
        parse.add_argument('file', type=werkzeug.datastructures.FileStorage, required=True, location='files')
        args = parse.parse_args()

        file = args['file']
        file.save(os.path.join(DATABASE, file.filename))

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

    