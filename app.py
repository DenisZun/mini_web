import re
import time

url_func_dict = dict()


def router(path):
    def _wrapper(func):
        url_func_dict[path] = func
        def _inner(*args, **kwargs):
            return func(*args, **kwargs)
        return _inner
    return _wrapper


def app(environ, start_response):
    # start_response表示客户端传给服务器的一个函数引用
    path_info = environ['PATH_INFO']
    print("收到动态资源请求路径是%s" % path_info)
    for path, func in url_func_dict.items():
        if path == path_info:
            headers = start_response('200 OK', [
                ('Content-Type', 'text/html; charset=utf-8\r\n'),
            ])
            return func(headers)
    else:
        response_line = "HTTP/1.1 404 NOT FOUND\r\n"
        response_headers = "Server: PWS4.0\r\n"
        response_headers += "\r\n"
        response_body = str(environ) + "==Hello World From a Simple WSGI application------>%s\n" % time.ctime()
        response_data = response_line + response_headers + response_body
        return response_data


@router("/index.html")
def index(headers):
    html_content = open("./template/index.html", encoding="utf-8")
    content = html_content.read()
    html_content.close()
    data = "Test"
    html_data = re.sub(r"\{%content%\}", data, content)
    response = (headers + html_data).encode("utf-8")
    return response


@router("/center.html")
def center(headers):
    html_content = open("./template/center.html", encoding="utf-8")
    content = html_content.read()
    html_content.close()
    data = "Test"
    html_data = re.sub(r"\{%content%\}", data, content)
    response = (headers + html_data).encode("utf-8")
    return response


@router("/update.html")
def update(headers):
    html_content = open("./template/update.html", encoding="utf-8")
    content = html_content.read()
    html_content.close()
    data = "Test"
    html_data = re.sub(r"\{%content%\}", data, content)
    response = (headers + html_data).encode("utf-8")
    return response