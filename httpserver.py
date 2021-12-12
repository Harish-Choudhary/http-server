from socket import *
import threading
from wsgiref.handlers import format_date_time
from datetime import datetime, timedelta
from time import *
import os
import stat
import mimetypes
import json
import random
import string
import gzip
import zlib
import config
import sys
#import brotli


class HttpRequest:

    def __init__(self, data):
        self.raw_byte_data = data
        print('Raw data:')

        print(data)
        self.url = None
        self.method = None
        self.http_version = None
        self.headers = None
        self.body = None
      
        self.split_request(data)

    def split_request(self, data):
        new_request = data.decode('utf-8').split("\r\n")

        index = 0
        for i in new_request:
            if(i == ''):
                break
            index = index+1

        self.body = "".join(new_request[index+1:])
        headers = new_request[1:index]
        print(self.body)
        newheaders = {}

        for i in headers:
            arr = i.split(':', 1)
            newheaders[arr[0]] = arr[1].strip()

        self.headers = newheaders
        print(self.headers)

        request_line = new_request[0].split(' ')
        print(new_request[0])
        self.method = request_line[0]

        self.url = request_line[1]
        self.http_version = request_line[2]
        print(self.method)

        # print(self.url)
        # print(self.http_version)
        # print(self.url)
        print('Above is parsing')
        return


class HttpResponse:

    def __init__(self, formatted_request):

        self.status_codes_list = {
            "100": "Continue",
            "101": "Switching Protocols",
            "200": "OK",
            "201": "Created",
            "202": "Accepted",
            "203": "Non-Authoritative Information",
            "204": "No Content",
            "205": "Reset Content",
            "206": "Partial Content",
            "300": "Multiple Choices",
            "301": "Moved Permanently",
            "302": "Found",
            "303": "See Other",
            "304": "Not Modified",
            "305": "Use Proxy",
            "307": "Temporary Redirect",
            "400": "Bad Request",
            "401": "Unauthorized",
            "402": "Payment Required",
            "403": "Forbidden",
            "404": "Not Found",
            "405": "Method Not Allowed",
            "406": "Not Acceptable",
            "407": 'Proxy Authentication Required',
            "408": 'Request Timeout',
            "409": 'Conflict',
            "410": 'Gone',
            "411": 'Length Required',
            "412": 'Precondition Failed',
            "413": 'Payload Too Large',
            "414": 'URI Too Long',
            "415": 'Unsupported Media Type',
            "416": 'Range Not Satisfiable',
            "417": 'Expectation Failed',
            "426": 'Upgrade Required',
            "501": 'Not Implemented',
            "505": 'HTTP Version not supported'
        }
        self.http_version = 'HTTP/1.1'
        self.status_code = None
        self.phrase = None
        self.headers = None
        self.body = None
        self.date = None
        self.server_name = 'Spidy/1.0'
        self.response_headers = {
        }

        self.last_modified = None
        self.filename = ''
        if(len(formatted_request.url) > 20):
            self.status_code = '414'
            self.phrase = self.status_codes_list[self.status_code]
            self.body = b'<html><body>Request URL Too Long</body></html>'
            self.handle_headers(formatted_request)
            return
        if(formatted_request.url == '/'):
            self.filename = config.ROOT+'index.html'
            print(self.filename)
        else:
            self.filename = ''.join(formatted_request.url.split('/', 1))
            self.filename = config.ROOT+self.filename
            print(self.filename)

        self.generate_response(formatted_request)

    def generate_response(self, formatted_request):

        if float(formatted_request.http_version.split('/')[1]) < 1.1:
            self.http_version = formatted_request.http_version
            self.status_code = '426'
            self.phrase = self.status_codes_list[self.status_code]
            self.response_headers['Upgrade'] = 'HTTP/1.1'
            self.response_headers['Connection'] = 'Upgrade'
            self.body = b'This service requires HTTP Version 1.1'
            self.headers = '\r\n'.join(': '.join((key, val)) for (
                key, val) in self.response_headers.items())
            self.headers += '\r\n\r\n'
            self.headers = self.headers.encode()

        else:
            self.handle_status_line(formatted_request)
            self.handle_headers(formatted_request)

        return

    def handle_status_line(self, formatted_request):
        if(formatted_request.method == 'GET'):
            self.handle_get_method(formatted_request)

        elif(formatted_request.method == 'HEAD'):
            self.handle_head_method(formatted_request)
        elif(formatted_request.method == 'DELETE'):
            self.handle_delete_method(formatted_request)
        elif(formatted_request.method == 'PUT'):
            self.handle_put_method(formatted_request)
        elif(formatted_request.method == 'POST'):
            self.handle_post_method(formatted_request)
        else:
            self.body = b'Server does not support this method'
            self.status_code = '501'
            self.phrase = self.status_codes_list[self.status_code]

    def handle_headers(self, formatted_request):

        now = datetime.now()
        stamp = mktime(now.timetuple())
        self.date = str(format_date_time(stamp))
        self.response_headers["Date"] = self.date

        try:
            self.response_headers["Connection"] = formatted_request.headers["Connection"]
        except KeyError:
            self.response_headers["Connection"] = "keep-alive"
        self.response_headers["Keep-Alive"] = 'timeout='+str(config.TIMEOUT)
        self.response_headers["Server"] = self.server_name
        self.response_headers['Cache-Control'] = 'no-store'

        self.response_headers["Content-Language"] = "en-US"

        return

    def handle_get_method(self, formatted_request):
        cookiefile = config.COOKIEFILE
        if os.path.exists(self.filename):
            allow_methods = self.check_file_permissions(self.filename)
            print(allow_methods)
            if 'GET' in allow_methods:
                file1 = open(self.filename, 'rb')
                file_info = os.stat(self.filename)
                file_size = file_info.st_size

                last_modified = format_date_time(file_info.st_mtime)

                if 'If-Range' in formatted_request.headers:
                    date1 = formatted_request.headers['If-Range']
                    if(self.check_ifmodified(date1, last_modified) == False):
                        if 'Range' in formatted_request.headers:
                            bytes_arr = formatted_request.headers['Range'].split(
                                '=')
                            bytes_list = bytes_arr[1].split(',')

                            filesize = os.path.getsize(self.filename)
                            file_content = b''

                            for i in bytes_list:
                                a = i.split('-')
                                if(a[0] == ''):
                                    a[0] = '0'
                                elif(a[1] == ''):
                                    a[1] = str(filesize)

                                if(int(a[0]) > int(filesize) or int(a[1]) > int(filesize)):
                                    self.status_code = '416'
                                    file_content = '<html>Invalid Ranges</html>'
                                    break
                                else:

                                    file1.seek(int(a[0]))
                                    file_content += file1.read(
                                        int(a[1]) - int(a[0]))
                                    self.status_code = '206'
                            self.response_headers["Accept-Ranges"] = "bytes"

                            self.phrase = self.status_codes_list[self.status_code]
                            self.body = file_content

                        else:

                            self.body = file1.read()
                            self.status_code = '200'
                            self.phrase = self.status_codes_list[self.status_code]

                    else:
                        self.body = file1.read()
                        self.status_code = '200'
                        self.phrase = self.status_codes_list[self.status_code]

                elif 'If-Modified-Since' in formatted_request.headers:
                    date1 = formatted_request.headers['If-Modified-Since']
                    if(self.check_ifmodified(date1, last_modified) == False):
                        self.status_code = '304'
                        self.phrase = self.status_codes_list[self.status_code]
                        self.body = b''
                    else:
                        self.body = file1.read()
                        self.status_code = '200'
                        self.phrase = self.status_codes_list[self.status_code]

                else:

                    if 'Range' in formatted_request.headers:
                        bytes_arr = formatted_request.headers['Range'].split(
                            '=')
                        bytes_list = bytes_arr[1].split(',')

                        filesize = os.path.getsize(self.filename)
                        file_content = b''

                        for i in bytes_list:
                            a = i.split('-')
                            if(a[0] == ''):
                                a[0] = '0'
                            elif(a[1] == ''):
                                a[1] = str(filesize)

                            if(int(a[0]) > int(filesize) or int(a[1]) > int(filesize)):
                                self.status_code = '416'
                                file_content = b'<html>Invalid Ranges</html>'
                                break
                            else:
                                print('In part of range')
                                file1.seek(int(a[0]))
                                file_content += file1.read(
                                    int(a[1]) - int(a[0]))
                                self.status_code = '206'

                        self.response_headers['Accept-Ranges'] = 'Bytes'
                        self.phrase = self.status_codes_list[self.status_code]
                        self.body = file_content

                    else:
                        print('In else part of range')
                        self.body = file1.read()
                        self.status_code = '200'
                        self.phrase = self.status_codes_list[self.status_code]

                if not 'Cookie' in formatted_request.headers:
                    random_id = ''.join(random.choices(
                        string.ascii_letters + string.digits, k=5))
                    now = datetime.now()+timedelta(hours=5)

                    stamp = mktime(now.timetuple())
                    expires_date = str(format_date_time(stamp))
                    key = 'id='+random_id+'; Expires='+expires_date
                    self.response_headers['Set-Cookie'] = key

                    with open(cookiefile, 'r+') as f:
                        json_data = json.load(f)
                        #json_data[formatted_request.headers["User-Agent"]] = {"id": random_id, "count": 1}
                        json_data[random_id] = {
                            "User-Agent": formatted_request.headers["User-Agent"], "count": 1}
                        f.seek(0)
                        f.write(json.dumps(json_data))
                    print('in set cookie')
                    # print(self.body)
                else:
                    with open(cookiefile, 'r+') as f:
                        json_data = json.load(f)
                        print(type(json_data))
                        # json_data[formatted_request.headers["User-Agent"]]["count"]+=1
                        cookie = formatted_request.headers['Cookie'].split('=')[
                            1]

                        json_data[cookie]['count'] += 1
                        f.seek(0)
                        f.write(json.dumps(json_data))
                        print('cookie already')
                    # print(self.body)
                self.response_headers['Last-Modified'] = last_modified
                self.response_headers['Content-Length'] = str(len(self.body))
                self.response_headers['Content-Type'] = mimetypes.guess_type(self.filename)[
                    0]
                if 'gzip' in formatted_request.headers['Accept-Encoding']:
                    self.body = gzip.compress(self.body)
                    self.response_headers['Content-Encoding'] = 'gzip'

                elif 'deflate' in formatted_request.headers['Accept-Encoding']:
                    self.body = zlib.compress(self.body)
                    self.response_headers['Content-Encoding'] = 'deflate'

                # this compression requires explicitly brotli library
                # elif 'br' in formatted_request.headers['Accept-Encoding'] :
                #	self.body = brotli.compress(self.body)
                #	self.response_headers['Content-Encoding']='br'
            else:
                self.status_code = "405"

                self.phrase = self.status_codes_list[self.status_code]
                allow_methods_string = ''
                for i in allow_methods:
                    if len(allow_methods)-1 == allow_methods.index(i):
                        allow_methods_string = allow_methods_string + i
                    else:
                        allow_methods_string = allow_methods_string + i + ', '
                self.response_headers['Allow'] = allow_methods_string
                self.body = b'This resource do not have permission for this method'

        else:
            print('In not found error')

            self.status_code = "404"

            self.phrase = self.status_codes_list[self.status_code]
            file1 = open('notfound.html', 'rb')
            self.body = file1.read()

        file1.close()
        return

    def handle_head_method(self, formatted_request):

        # in progress
        self.handle_get_method(formatted_request)
        self.body = b''

    def handle_post_method(self, formatted_request):

        file_type = mimetypes.guess_type(self.filename)[0]
        print(file_type)
        content_type_value = formatted_request.headers['Content-Type'].split(';')[
            0]
        print(content_type_value)
        print('before renaming ', self.filename)
        if(file_type is None and content_type_value == 'application/x-www-form-urlencoded'):
            self.filename = self.filename+'.json'
        elif(file_type is None and content_type_value == 'text/html'):
            self.filename = self.filename+'.html'
        print('after renaming ', self.filename)
        if os.path.exists(self.filename):
            allow_methods = self.check_file_permissions(self.filename)
            print(allow_methods)
            if 'POST' in allow_methods:
                if content_type_value == 'application/x-www-form-urlencoded':
                    content = {}
                    arr = formatted_request.body.split('&')
                    for i in arr:
                        temp = i.split('=')
                        content[temp[0]] = temp[1]
                    with open(self.filename, 'a+') as f:
                        json.dump(content, f)

                elif content_type_value == 'text/html':
                    with open(self.filename, 'a+') as f:
                        f.write(formatted_request.body)

                self.status_code = '200'
                self.phrase = self.status_codes_list[self.status_code]
                self.body = b'Data added successfully'
                self.response_headers['Content-Location'] = self.filename
            else:

                self.status_code = "405"

                self.phrase = self.status_codes_list[self.status_code]
                allow_methods_string = ''
                for i in allow_methods:
                    if len(allow_methods)-1 == allow_methods.index(i):
                        allow_methods_string = allow_methods_string + i
                    else:
                        allow_methods_string = allow_methods_string + i + ', '
                self.response_headers['Allow'] = allow_methods_string
                self.body = b''

        else:
            if content_type_value == 'application/x-www-form-urlencoded':

                content = {}
                arr = formatted_request.body.split('&')
                for i in arr:
                    temp = i.split('=')
                    content[temp[0]] = temp[1]
                with open(self.filename, 'a+') as f:
                    json.dump(content, f)

            elif content_type_value == 'text/html':

                with open(self.filename, 'a+') as f:
                    f.write(formatted_request.body)

            self.status_code = '201'
            self.body = b'File Created !!!'
            self.response_headers['Content-Location'] = self.filename
            self.phrase = self.status_codes_list[self.status_code]
        return

    def handle_put_method(self, formatted_request):

        file_type = mimetypes.guess_type(self.filename)[0]
        print(file_type)

        content_type_value = formatted_request.headers['Content-Type'].split(';')[
            0]
        print(content_type_value)
        print('before renaming ', self.filename)
        if(file_type is None and content_type_value == 'application/x-www-form-urlencoded'):
            self.filename = self.filename+'.json'
        elif(file_type is None and content_type_value == 'text/html'):
            self.filename = self.filename+'.html'
        print('after renaming ', self.filename)
        if os.path.exists(self.filename):
            allow_methods = self.check_file_permissions(self.filename)
            print(allow_methods)
            if 'PUT' in allow_methods:
                if content_type_value == 'application/x-www-form-urlencoded':

                    # else:
                    #	self.filename = 'data.json'
                    content = {}
                    arr = formatted_request.body.split('&')
                    for i in arr:
                        temp = i.split('=')
                        content[temp[0]] = temp[1]
                    with open(self.filename, 'w+') as f:
                        json.dump(content, f)

                elif content_type_value == 'text/html':
                    with open(self.filename, 'w+') as f:
                        f.write(formatted_request.body)

                self.status_code = '204'
                self.phrase = self.status_codes_list[self.status_code]
                self.body = b'File modified'
                self.response_headers['Content-Location'] = self.filename
            else:

                self.status_code = "405"

                self.phrase = self.status_codes_list[self.status_code]
                allow_methods_string = ''
                for i in allow_methods:
                    if len(allow_methods)-1 == allow_methods.index(i):
                        allow_methods_string = allow_methods_string + i
                    else:
                        allow_methods_string = allow_methods_string + i + ', '
                self.response_headers['Allow'] = allow_methods_string
                self.body = b''

        else:
            if content_type_value == 'application/x-www-form-urlencoded':

                content = {}
                arr = formatted_request.body.split('&')
                for i in arr:
                    temp = i.split('=')
                    content[temp[0]] = temp[1]
                with open(self.filename, 'w+') as f:
                    json.dump(content, f)

            elif content_type_value == 'text/html':

                with open(self.filename, 'w+') as f:
                    f.write(formatted_request.body)

            self.status_code = '201'
            self.body = b'File Created !!!'
            self.response_headers['Content-Location'] = self.filename
            self.phrase = self.status_codes_list[self.status_code]
        return

    def handle_delete_method(self, formatted_request):
        if os.path.exists(self.filename):
            os.remove(self.filename)
            self.status_code = '200'
            self.body = b'<html>File deleted Successfully</html>'
            self.phrase = self.status_codes_list[self.status_code]

        else:
            self.status_code = '404'
            self.body = b'<html><body><h1>File Not Found</h1></body></html>'
            self.phrase = self.status_codes_list[self.status_code]

        return

    def check_ifmodified(self, date1, date2):

        months = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
                  'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 				11, 'Dec': 12}
        currdate = date1.split(',')[1].split(' ')
        given_date = int(currdate[1])
        given_mon = months[currdate[2]]
        given_year = int(currdate[3])
        given_time = currdate[4]
        time_arr = given_time.split(':')
        hours = int(time_arr[0])
        minute = int(time_arr[1])
        seconds = int(time_arr[2])

        lastmodified = date2.split(',')[1].split(' ')

        newdate = int(lastmodified[1])
        newmon = months[lastmodified[2]]
        newyear = int(lastmodified[3])
        newtime = lastmodified[4]
        temp_arr1 = newtime.split(':')
        newhour = int(temp_arr1[0])
        newmin = int(temp_arr1[1])
        newsec = int(temp_arr1[2])

        temp1 = datetime(given_year, given_mon, given_date,
                         hours, minute, seconds, 0)
        temp2 = datetime(newyear, newmon, newdate, newhour, newmin, newsec, 0)
        print(temp1, temp2)
        return temp2 > temp1

    def check_file_permissions(self, filename):
        permissions_arr = []

        if os.access(filename, os.R_OK) == True:
            print('appending get method')
            permissions_arr.append('GET')
        if os.access(filename, os.W_OK) == True:
            print('appending post and put')
            permissions_arr.append('POST')
            permissions_arr.append('PUT')
        permissions_arr.append('DELETE')
        return permissions_arr


def access_log(formatted_request, response, ip):
    with open(config.ACCESSLOG, 'ab+') as f:
        log = bytes(ip + ' - ' + response.response_headers['Date'] + " " + formatted_request.method+' ' + formatted_request.url +
                    ' '+formatted_request.http_version+' ' + response.status_code+' ' + str(len(response.body)) + '\n', 'utf-8')
        f.write(log)


def error_log(formatted_request, response, ip):
    with open(config.ERRORLOG, 'ab+') as f:
        log = bytes(ip + ' - ' + response.response_headers['Date'] + " " + formatted_request.method+' ' + formatted_request.url +
                    ' '+formatted_request.http_version+' ' + response.status_code+' ' + str(len(response.body)) + '\n', 'utf-8')
        f.write(log)


def handle_request(request, addr):
    formatted_request = HttpRequest(request)
    formatted_response = HttpResponse(formatted_request)
    formatted_response.headers = '\r\n'.join(': '.join((key, val)) for (
        key, val) in formatted_response.response_headers.items())
    formatted_response.headers += '\r\n\r\n'
    formatted_response.headers = formatted_response.headers.encode()
    print('headers encoded')
    iskeepalive = True
    if formatted_response.response_headers['Connection'] == 'close':
        iskeepalive = False
    print(type(formatted_response.headers), type(formatted_response.body))
    resp = (formatted_response.http_version + ' ' + formatted_response.status_code + ' ' +
            formatted_response.phrase+'\r\n').encode() + formatted_response.headers + formatted_response.body

    if(formatted_response.status_code == '404' or formatted_response.status_code == '515' or formatted_response.status_code == '405' or formatted_response.status_code == '414' or formatted_response.status_code == '416'):
        error_log(formatted_request, formatted_response, addr[0])
    else:
        access_log(formatted_request, formatted_response, addr[0])
    return resp, iskeepalive


def handle_clients(newconn, addr):
    cond = True
    i = 0
    newconn.settimeout(config.TIMEOUT)
    while cond == True:
        print('receiving from existing client ', addr)
        try:
            req = newconn.recv(2048)
            if(req == b''):
                print(addr, 'will be closed')
                # Chrome was sending empty requests
                break
            resp, iskeepalive = handle_request(req, addr)
            cond = iskeepalive
            # print(resp)
            newconn.send(resp)
        except timeout as a:
            print(a)
            newconn.close()
            break
    print(newconn, ' connection closed')
    try:
        conn.close()
    except Exception:
        pass


ip = "127.0.0.1"
port = int(sys.argv[1])

s = socket(AF_INET, SOCK_STREAM)
s.bind((ip, port))
s.listen()
maxconn = config.MAXCONNECTIONS
Threadsarr = []
print("Server is Listening")

while True:

    newconn, addr = s.accept()
    print('new connection from ', addr, '\n')
    if(len(Threadsarr) < maxconn):
        thr = threading.Thread(target=handle_clients,
                               args=(newconn, addr), daemon=True)
        thr.start()
        Threadsarr.append(thr)
    else:

        #msg = b'503 Service Unavailable HTTP/1.1\r\nServer: Spidy/1.0\r\n\r\n<html><body>service is not available</body></html>'
        # newconn.send(msg)
        # newconn.close()
        print('service unavailable')
        break
