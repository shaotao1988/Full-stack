from http.server import BaseHTTPRequestHandler, HTTPServer 
from urllib.parse import parse_qs

class webserverHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path.endswith("/hello"):
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()

                output = "<html><body>Hello!<br>"
                output += "<form method='POST' action='/hello' \
                <h2>What would you like me to say?</h2><input name='message' type='text'> \
                <input type='submit' value='Submit'></form>"

                self.wfile.write(output.encode('utf-8'))
                print(output)
        except IOError:
            self.send_error(404, 'File not found: {}'.format(self.path))

    def do_POST(self):
        try: 
            self.send_response(301)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            """
            ctype, pdict = cgi.parse_header(self.headers.get('content-type'))
            if ctype == "multipart/form-data":
                fields = cgi.parse_multipart(self.rfile, pdict)
                messagecontent = fields.get('message')
            """

            length = int(self.headers.get('Content-length'), 0)
            body = self.rfile.read(length).decode()
            params = parse_qs(body)
            messagecontent = params["message"]

            output = ""
            output += "<htm><body>"
            output += "<h2> Okay, how about this: </h2>"
            output += "<h1>hello {}</h1>".format(messagecontent[0])

            output += "<form method='POST' action='/hello' \
                <h2>What would you like me to say?</h2><input name='message' type='text'> \
                <input type='submit' value='Submit'></form>"
            output += "</body></html>"

            self.wfile.write(bytes(output, 'utf-8'))
            print(output)
        except:
            pass

def main():
    try:
        port = 8080
        server = HTTPServer(('', port), webserverHandler)
        print("Web server running on port {}".format(port))
        server.serve_forever()

    except  KeyboardInterrupt:
        print("Ctrl-C entered, stop web server...")
        server.socket.close()

if __name__ == "__main__":
    main()
