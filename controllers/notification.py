# This is a notification controller.
import tornado.ioloop
import tornado.web
import tornado.httpserver
import tornado.websocket

from tornado.options import define, options

define("port", default=8888, help="run on the 8888 port.", type=int)

class MainHandler(tornado.web.RequestHandler):

    """Docstring for MainHandler. """
    
    def get(self):
        self.write("Hello, wordl")

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    
    """
    Doctring for EchoWebSocket
    """

    def check_origin(self, origin):
        return True

    def open(self):
        print "WebSocket opened"


    def on_message(self, message):
        """@todo: Docstring for on_message.
        :returns: @todo

        """
        print "Mensagem recebida: {}".format(message)
        self.write_message(u"You saind:" + message)

    def on_close(self):
        """@todo: Docstring for on_close.
        :returns: @todo

        """
        print "WebSocket closed"

def main():
    tornado.options.parse_command_line()
    application = tornado.web.Application([
        (r"/", MainHandler),
        (r"/socket", WebSocketHandler),
        (r"/teste", MainHandler),
    ])
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
