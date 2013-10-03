import urlparse
import BaseHTTPServer
from WiringPin import WiringPin
from collections import OrderedDict
from strogonanoff_sender import send_command


class GETHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    pin = WiringPin(0).export()
    plugs = OrderedDict()
    plugs[(1, 1)] = 'Bedroom Light'
    plugs[(1, 2)] = 'Bedroom Speakers'
    plugs[(1, 3)] = 'Lounge Cabinet'
    plugs[(1, 4)] = 'Lounge Light'
    plugs[(2, 1)] = 'Conservatory Light'

    def do_GET(self):
        parsed_path = urlparse.urlparse(self.path)
        print parsed_path.path
        app = None if parsed_path.path == '/' else parsed_path.path
        message = parsed_path.query
        params = self.parse_message(message)

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        if app == '/GetPlugs':
            self.wfile.write(str(self.get_plugs()))
            return
        self.wfile.write(self.get_html())
        for i in xrange(6):
            self.perform_action(params)
        return

    def perform_action(self, params):
        if params:
            for i in range(1, 6):
                send_command(self.pin, params['channel'], params['button'], params['state'])

    def parse_message(self, message):
        try:
            params = dict([(x.split('=')[0], x.split('=')[1]) for x in message.split('&')])
            if 'channel' in params.keys() and 'button' in params.keys() and 'state' in params.keys():
                params['channel'] = int(params['channel'])
                params['button'] = int(params['button'])
                params['state'] = True if params['state'] == 'on' else False
                return params
            return None
        except IndexError:
            return None

    def get_html(self):
        out = ""
        for key, value in self.plugs.iteritems():
            out = out + """
            <a href="/?channel={channel}&button={button}&state=on">
            <input type="button" value="On"></a>
            {name}
            <a href="/?channel={channel}&button={button}&state=off">
            <input type="button" value="Off"></a><br />
            """.format(name=value, channel=key[0], button=key[1])
        return out

    def get_plugs(self):
        out = ""
        for key, value in self.plugs.iteritems():
            out = out + "{name},{channel},{button}&".format(name=value, channel=key[0], button=key[1])
        return out

if __name__ == '__main__':
    server = BaseHTTPServer.HTTPServer(('localhost', 8080), GETHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
