import tornado
import random
import hashlib
import tornado.ioloop
import tornado.web
import tornado.websocket
import json
import os.path
import sys
import inspect

pagelist = []

class BaseHandler(tornado.web.RequestHandler):pass

class BaseWebsocket(tornado.websocket.WebSocketHandler):pass

def GuiFaker(klass):
    def wopen(self):
        self.uid = self.get_secure_cookie("uid").decode()
        print(self.uid)
        print("Python user "+self.uid+" connected")
        self.methods = {i[0]:i[1] for i in inspect.getmembers(klass) if inspect.isfunction(i[1])} #Maps function names to input lists

    def on_message(self, message):
        payload = {}
        print(str(self.uid) + " says " + str(message))
        message = json.loads(message) #Message is in format {"method":[args]}
        print(message)
        for call in list(message):  #method dictionary key
            payload.update({call: self.methods[call](*message[call])})
        self.write_message(json.dumps(payload))

    def get(self):
        h = hashlib.new('sha1')
        h.update(str(random.randint(-10000, 10000)).encode())

        self.clear_all_cookies()

        #Python modules must start with a letter
        self.set_secure_cookie('uid', 'a' + str(h.hexdigest()))
        post(self)

    def post(self):
        methods = {i[0]:inspect.getargspec(i[1])[0] for i in inspect.getmembers(klass) if inspect.isfunction(i[1]) and i[0] not in dir(klass.__bases__[0])} #Maps function names to input lists
        print(methods)
        self.render(klass.name + ".html", name = klass.name, methods = methods, uri = self.request.host)

    pagelist.append((r'/'+klass.name, type(klass.name+"Handler",(BaseHandler,), {'get':get, 'post':post})))
    pagelist.append((r'/'+klass.name+"Websocket", type(klass.name+"Websocket", (BaseWebsocket,), {'open':wopen,'on_message': on_message})))
    return klass

def start(port = 8080, title = "GuiFaker", cookie_secret="secure secret"):
    print(pagelist)
    server = tornado.web.Application(
            pagelist,
            title= title,
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            login_url="/",
            cookie_secret=cookie_secret,
            debug=True
        )
    server.listen(port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
