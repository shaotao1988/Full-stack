import re
from cgi import escape

def index(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/html')])
    result = [b'Hello World Application']
    return result

def hello(environ, start_response):
    args = environ['app.url_args']
    if args:
        subject = escape(args[0])
    else:
        subject = "World"
    
    start_response('200 OK', [('Content-Type', 'text/html')])
    return [bytes('Hello {subject}!'.format(subject=subject), encoding='utf-8')]

def not_found(environ, start_response):
    start_response('404 NOT FOUND', [('Content-Type', 'text/plain')])
    return [b'Not Found']

urls = [
    (r'^$', index),
    (r'hello/?$', hello),
    (r'hello/(.+)$', hello)
]

def application(environ, start_response):
    path = environ.get('PATH_INFO', '').lstrip('/')
    for regex, callback in urls:
        match = re.search(regex, path)
        if match is not None:
            environ['app.url_args'] = match.groups()
            return callback(environ, start_response)
    
    return not_found(environ, start_response)

class ExceptionMiddleware():
    def __init__(self, app):
        self.app = app
    
    def __call__(self, environ, start_response):
        app_result = None
        try:
            app_result = self.app(environ, start_response)
            for item in app_result:
                yeild item
        except:
            # 可以根据需要记录日志或调用栈等信息
            logger.debug("Exception!!!")
            # 重新设置状态码和头部
            start_response('500 INTERNAL SERVER ERROR',
                        [('Content-Type', 'text/plain')])
            yeild b'Server error'

        # 有些application返回的iterable可能有close方法，如果有的话结束的时候必须调用
        if hasattr(app_result, 'close'):
            app_result.close()

# 用中间件包装原始WSGI应用程序
application = ExceptionMiddleware(application)

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    srv = make_server('localhost', 8080, application)
    srv.serve_forever()
