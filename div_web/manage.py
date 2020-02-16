from wsgiref.simple_server import make_server
from app.views import *
import urls

def routers():
    URLpattern=urls.URLpattern
    return URLpattern

def applications(environ,start_response):
    path=environ.get("PATH_INFO")
    start_response('200 OK', [('Content-Type', 'text/html'),('Charset', 'utf8')])
    urlpattern=routers()
    func=None
    for item in urlpattern:
        if path==item[0]:
            func=item[1]
            break
    if func:
        return [func(environ)]
    else:
        return [b"<h1>404!<h1>"]

if __name__ == '__main__':
    server=make_server("",8889,applications)
    print("server is working...")
    server.serve_forever()