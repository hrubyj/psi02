import socket
import time
from datetime import datetime
from _thread import *


def handle_connection(sock):
    while True:
        data = read_data(sock)
        if not data:
            break
        handle_http_request(sock, data)

    sock.close()


def read_data(connection):
    connection.setblocking(False)
    complete_data = b''

    timeout = 3
    read_time = time.time()
    while True:
        if time.time() - read_time > timeout:
            break

        try:
            data = connection.recv(4 * 1024)
            if data:
                complete_data += data
                read_time = time.time()
            else:
                time.sleep(0.1)

        except BlockingIOError:
            pass

    return complete_data


def handle_http_request(sock, request):
    request_string = request.decode('utf-8')
    lines = request_string.split("\n")

    first_line = lines[0]
    request_parts = first_line.split()
    if len(request_parts) < 3:
        message = "<!DOCTYPE html>" \
                    "<html lang=\"en\">" \
                    " <head>" \
                    "  <meta charset=\"UTF-8\">" \
                    "  <title>ERROR</title>" \
                    " </head>" \
                    " <body>" \
                    "  <h2>Invalid HTTP request</h2>" \
                    " </body>" \
                    "</html>"
        send_response(sock, message, False)
        return

    method = request_parts[0]
    path = request_parts[1]

    if not method.upper() == "GET":
        message = "<!DOCTYPE html>" \
                    "<html lang=\"en\">" \
                    " <head>" \
                    "  <meta charset=\"UTF-8\">" \
                    "  <title>ERROR</title>" \
                    " </head>" \
                    " <body>" \
                    "  <h2>Invalid method, only GET method is supported</h2>" \
                    " </body>" \
                    "</html>"
        send_response(sock, message, False)
        return

    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    message = "<!DOCTYPE html>" \
              "<html lang=\"en\">" \
              " <head>" \
              "  <meta charset=\"UTF-8\">" \
              "  <title>Hello from context</title>" \
              " </head>" \
              " <body>" \
              "  <h2>Hello from " + path + "</h2>" \
              "  <p>Current datetime: " + dt_string + "</p>" \
              " </body>" \
              "</html>"
    send_response(sock, message, True)


def send_response(connection, content, ok: bool):
    if ok:
        header = b'HTTP/1.1 200 OK\n'\
               + b'Content-Type: text/html\n'\
               + b'Content-Length: ' + str(len(content)).encode('utf-8') \
               + b'\n' \
               + b'\n'
    else:
        header = b'HTTP/1.1 403 Forbidden'

    content_data = content.encode("utf-8")
    message = header + content_data
    connection.sendall(message)


def main():
    port = 8080
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("", port))
    server.listen()
    print("Server started, listening on port: ", port)

    while True:
        sock, addr = server.accept()
        start_new_thread(handle_connection, (sock, ))

    server.close()


if __name__ == '__main__':
    main()
