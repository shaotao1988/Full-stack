# WSGI 简介

## 什么是WSGI

WSGI是python网络程序中位于服务器和应用程序之间的一套规范，使服务器和应用程序可以单独开发并相互兼容。典型的web服务器有CGI，mod_python，FastCGI等，应用程序一般借助web框架开发，比如Flask和Django。

WSGI规范在PEP333中说明，要点如下：
- WSGI应用程序是一个可调用的python对象(函数或者实现了__call__方法的类)，由应用程序实现，接受2个参数：environ和start_response
- environ是一个字典结构，包含了运行时环境，比如用户请求信息，服务器以及WSGI中间件也可以根据需要设置一些自定义的环境变量，应用程序通过这个参数决定做什么动作
- start_response是一个函数，由服务器定义，参数为http响应的状态码和http头部，应用程序在处理完请求后必须调用该函数设置响应状态码和头部。
- WSGI应用程序必须返回可迭代的对象
- 可以包装WSGI应用程序来实现自定义中间件，中间件是一种特殊的WSGI应用程序

python的标准库wsgiref实现了一个简单的遵循WSGI标准的服务器：

```python
def run(self, application):
    ...
    try:
        # 设置服务器运行时变量比如服务器版本，解析客户端的请求参数
        self.setup_environ()
        # 调用web应用程序处理请求
        self.result = application(self.environ, self.start_response)
        # 向客户端发送响应
        self.finish_response()
    except:
        self.handle_error()
```

wsgiref对start_response函数的定义，只是简单的设置一下状态和http头部信息并做校验：
```python
def start_response(self, status, headers,exc_info=None):
    """'start_response()' callable as specified by PEP 3333"""
    ...
    self.status = status
    self.headers = self.headers_class(headers)
    status = self._convert_string_type(status, "Status")
    # 状态码是3个数字+空格+状态描述
    assert len(status)>=4,"Status must be at least 4 characters"
    assert status[:3].isdigit(), "Status message must begin w/3-digit code"
    assert status[3]==" ", "Status message must have a space after code"
    ...
```

## 一个简单的web应用程序示例

下面我们不借助任何框架，实现一个基本的web应用程序

1. 定义基本框架

定义一个WSGI应用程序application，获取用户请求路径，并用正则表达式完成url匹配，将请求分发到对应的请求函数，这个application函数由web服务器调用。

```python
import re

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
            # 应用程序可以更新environ变量
            environ['app.url_args'] = match.groups()
            return callback(environ, start_response)
    
    return not_found(environ, start_response)

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    # 将application传递给服务器，最终由wsgiref库中的run函数调用
    srv = make_server('localhost', 8080, application)
    srv.serve_forever()
```

2. 实现请求函数

```python
from cgi import escape

def index(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/html')])
    # 返回值必须是可迭代对象
    return [b'Hello World Application']

def hello(environ, start_response):
    # 从environ中获取客户端请求参数
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
```

现在，我们就得到了一个简单的能运行的web应用。

3. 实现错误处理中间件

下面我们实现一个自定义的中间件，用于应用程序抛出异常时向客户端返回"Server error"字符串

```python
class ExceptionMiddleware():
    def __init__(self, app):
        self.app = app
    
    # 中间件也需要遵循WSGI规范，以支持多个中间件嵌套
    def __call__(self, environ, start_response):
        app_result = None
        try:
            app_result = self.app(environ, start_response)
            for item in app_result:
                yield item
        except:
            # 可以根据需要记录日志或调用栈等信息
            logger.debug("Exception!!!")
            # 重新设置状态码和头部
            start_response('500 INTERNAL SERVER ERROR',
                        [('Content-Type', 'text/plain')])
            yield b'Server error'

        # 有些application返回的iterable可能有close方法，如果有的话结束的时候必须调用
        if hasattr(app_result, 'close'):
            app_result.close()
```

通过对WSGI应用程序包装来使中间件生效：
```python
application = ExceptionMiddleware(application)
```

## Flask封装

Flask对WSGI的实现方式跟上面略有不同，Flask类的__call__函数是对成员函数wsgi_app的代理：

```python
def wsgi_app(self, environ, start_response):
    ...
    response = self.full_dispatch_request()
    return response(environ, start_response)
        
def __call__(self, environ, start_response):
    # 代理
    return self.wsgi_app(environ, start_response)
```

这样实现的好处是，应用程序可以保留对Flask app对象的引用，中间件的封装可以由
```python
app = MyMiddleWare(app)
```
变为
```python
app.wsgi_app = MyMiddleWare(app.wsgi_app)
```

另外，Flask视图函数的返回值类型可以不仅仅是字符串，还可以是字典、元组或者WSGI callable对象，最终Flask会将视图函数返回值统一转换为WSGI callable的Reponse对象，即上面wsgi_app函数中的response变量