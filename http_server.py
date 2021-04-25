#!/usr/bin/env python3
import os
import requests
import hashlib
import base64
import subprocess

from flask import Flask

app = Flask(__name__)
url = "http://crazett.com"
@app.route("/")
def listen():
    username = os.environ.get("OPTIMIZEUSER", None)
    password = os.environ.get("OPTIMIZEPASS", None)
    r = requests.post(url + "/api/v1/login", allow_redirects=False,
                        json={"user": {"username": username, "password": password}})
    cookies = r.cookies
    r = requests.get(url + "/api/v1/unoptimized_traces", allow_redirects=False, cookies=cookies)
    r = r.json()
    if r is not None:
        trace_id = r.get('id')
        trace_record = requests.get(url + "/api/v1/traces/" + str(trace_id), allow_redirects=False, cookies=cookies)
        # check if file is locked
        r = requests.get(url + "/api/v1/trace_lock?id=" + str(trace_id), allow_redirects=False, cookies=cookies)
        if r.json().get('file') == "Locked":
            return "File locked\n"

        TracingTool(trace_record.json(), cookies)
    else:
        return "No traces that need optimization\n", 200
    return "Done\n"

class Blob:
    def __init__(self, blob_dict):
        direct_upload = blob_dict.get("direct_upload")
        if direct_upload is not None:
            self.url = direct_upload.get('url')
            if self.url is None:
                raise ValueError("The URL is missing from the 'direct_upload' key")

        self.headers = direct_upload.get('headers')
        if self.headers is None:
            raise ValueError("The headers are missing from the 'direct_upload' key")

        self.signed_id = blob_dict.get("signed_id")
        if self.signed_id is None:
            raise ValueError("The signed_id is from the blob-creation response")
        
        self.record_type = blob_dict.get("record_type")

    def upload(self, f):
        r = requests.put(self.url, headers=self.headers, data=f)
        r.raise_for_status()

class TracingTool:
    def __init__(self, trace_record, cookies):
        # Download and save unoptimized trace
        self.cookies = cookies
        self.id = trace_record.get("id")
        self.filename = trace_record.get("filename")
        self.trace_file = requests.get(trace_record.get("url"), cookies=cookies)
        open(self.filename, 'wb').write(self.trace_file.content)
        ext = os.path.splitext(self.filename)[1]
        if ext == ".gfxr":
            self.gfxrecon()
        elif ext == ".trace":
            self.apitrace()
        else:
            print("Don't recognize trace format")
        os.remove(self.filename)
    
    def gfxrecon(self):
        command = "zstd -T0 --ultra -22 " + self.filename
        compression = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        compression.wait()
        self.upload_file(self.filename + ".zst")
        return

    def apitrace(self):
        filename_without_ext = os.path.splitext(self.filename)[0]
        optimized_filename = filename_without_ext + ".trace-dxgi"
        command = "apitrace repack --brotli=8 " + self.filename + " " + optimized_filename
        compression = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        compression.wait()
        self.upload_file(optimized_filename)
        return

    def upload_file(self, name):
        hash_md5 = hashlib.md5()
        with open(name, "rb") as f:
            # Generate the MD5 hash for the bucket
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
            data_checksum = base64.b64encode(hash_md5.digest()).decode()
            # Check the file size
            f.seek(0, os.SEEK_END)
            file_size = f.tell()
            f.seek(0, os.SEEK_SET)
            # Ask the website for the URL of where to upload the file
            r_blob = requests.post(url + "/rails/active_storage/direct_uploads",
                                 json={"blob": {"filename": name, "byte_size": file_size,
                                           "content_type": "application/octet-stream",
                                           "checksum": data_checksum}}, cookies=self.cookies)
            blob = (Blob(r_blob.json()))
            blob.upload(f)
            # patch trace record with optimized file
            r = requests.patch(url + "/api/v1/traces/" + str(self.id),
                            json={"trace": {"optimized": blob.signed_id }}, cookies=self.cookies)
            os.remove(name)
        return
