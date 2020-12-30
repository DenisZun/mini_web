import re
import socket
from threading import Thread

"""
不要把静态的请求和动态的请求代码都混在一起
"""


class HTTPServer(object):
    """静态资源服务器"""
    def __init__(self, port, app):
        # listen是将主动套接字变为被动套接字, accept等待新的客户端的连接
        self.tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # 绑定本地服务器地址
        server_ip, server_port = "127.0.0.1", int(port)
        self.tcp_server_socket.bind((server_ip, server_port))
        # 监听,将主动套接字变为被动套接字
        self.tcp_server_socket.listen(128)
        self.app = app

    def service_client(self, new_socket):
        # http请求 GET/HTTP/1.1
        # 为服务端返回数据接收客户端的
        try:
            request = new_socket.recv(1024).decode("utf-8")
        except Exception as ret:
            print("========>", ret)
            new_socket.close()
            return
        if not request:
            new_socket.close()
            return
        request_lines = request.splitlines()

        # 这一步是为了匹配路由使用正则表达式
        res = re.match(r'\w+\s+(\S+)', request_lines[0])
        if res:
            file_name = res.group(1)
            print(f"响应静态文件{file_name}")

            if file_name == '/':
                file_name = '/index.html'

            env = dict()
            env["PATH_INFO"] = file_name

            # 判断是否以动态的方式请求资源
            if file_name.endswith(".html"):
                # 根据用户的请求返回文件
                body = self.app.app(env, self.start_response)
                if isinstance(body, str):body=body.encode("utf-8")
                new_socket.send(body)
                new_socket.close()
            else:
                try:
                    # 根据用户请求的路径 读取指定路径下的文件数据 将数据 以HTTP响应报文格式发送给浏览器即可
                    file = open("./static" + file_name, "rb")
                    file_data = file.read()  # bytes
                    file.close()
                except FileNotFoundError as e:
                    response_data = self.request_content(404).encode("utf-8")
                    new_socket.send(response_data)
                    print(e)
                else:
                    response_data = self.request_content(200, file_data=file_data)
                    new_socket.send(response_data)
                finally:
                    # 关掉套接字
                    new_socket.close()

    def request_content(self, status, file_data=""):
        # 当处理请求为静态资源请求时,构建响应头
        if int(status) == 404:
            response_line = "HTTP/1.1 404 Not Found\r\n"
            response_headers = "Server: PWS4.0\r\n"
            response_body = "<h1>-------file not found-------</h1>"
            response_data = response_line + response_headers + "\r\n" + response_body
            return response_data

        elif int(status) == 200:
            # 给客户端回HTTP响应报文
            response_line = "HTTP/1.1 200 OK\r\n"
            response_headers = "Server: PWS4.0\r\n"
            response_body = file_data
            # 拼接响应报文  发送给客户端
            response_data = (response_line + response_headers + '\r\n').encode() + response_body
            return response_data

    def start_response(self, status, header_list):
        """保存框架提供的应用状态和响应头"""
        # 该属性存储 响应状态和 响应头  在其他方法中使用
        status_header = "HTTP/1.1 %s\r\n" % status
        for header_name, header_value in header_list:
            status_header += f"{header_name}: {header_value}\r\n"
        status_header += '\r\n'
        return status_header

    def start(self):
        while True:
            # 采用多线程的方式启动服务器
            new_socket, client_addr = self.tcp_server_socket.accept()
            ip, port = client_addr[0], client_addr[1]
            print(f"Sending request to the server {ip}:{port}.....")
            t = Thread(target=self.service_client, args=(new_socket,))
            t.start()


def main():
    # 服务器对象调用无限循环方法
    import app
    server = HTTPServer(8888, app)
    server.start()


if __name__ == '__main__':
    main()
