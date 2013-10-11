from flask import Flask, request, render_template
from WiringPin import WiringPin
from collections import OrderedDict
from strogonanoff_sender import send_command

app = Flask(__name__)

pin = WiringPin(0).export()
plugs = OrderedDict()
plugs[(1, 1)] = 'Bedroom Light'
plugs[(1, 2)] = 'Bedroom Speakers'
plugs[(1, 3)] = 'Lounge Cabinet'
plugs[(1, 4)] = 'Lounge Light'
plugs[(2, 1)] = 'Conservatory Light'


def all_plugs():
        out = ""
        for key, value in plugs.iteritems():
            out = out + "{name},{channel},{button}&".format(name=value, channel=key[0], button=key[1])
        return out


def perform_action(params):
        if params:
            for i in range(1,6):
                send_command(pin, params['channel'], params['button'], params['state']) 

@app.route("/GetPlugs")
def get_plugs():
    return all_plugs()
    
@app.route("/", methods=['GET'])
def index():
    if request.method == 'GET':
        if set(['channel', 'button', 'state']).issubset(set(request.args.keys())):
            params = {}
            params['channel'] = int(request.args['channel'])
            params['button'] = int(request.args['button'])
            params['state'] = True if request.args['state'] == 'on' else False
            perform_action(params)
        return render_template("template.html", plugs=plugs)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
