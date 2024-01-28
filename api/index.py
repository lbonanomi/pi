from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(302)
        self.send_header('Location','https://www.google.com/')
        #self.send_header('Content-type','text/plain')
        self.end_headers()
        #self.wfile.write('Hello, world!'.encode('utf-8'))
        return
