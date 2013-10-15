import yaml
from WiringPin import WiringPin
from strogonanoff_sender import send_command
from flask import Flask, request, render_template, redirect

app = Flask(__name__)
pin = WiringPin(0).export()


def all_plugs():
    plugs = yaml.load(open('./plugs.yaml','r'))
    return '&'.join(['{name},{channel},{button}'.format(**plug) for plug in plugs])


def save_text(yaml_file, text):
    file = open(yaml_file, 'w')
    file.write(text)
    file.close()

def perform_action(params):
    if params:
        for i in range(1, 6):
            send_command(pin, params['channel'], params['button'], params['state']) 

@app.route('/saveplugs', methods=['GET'])
def save_plugs():
    if request.method == 'GET':
        text = request.args['yaml']
        text.replace('+', ' ')
        text.replace('%3A', ':')
        text.replace('%0D%0A', '\n')
        save_text('./plugs.yaml', text)
    return redirect('/')

@app.route('/setplugs', methods=['GET'])
def set_plugs():
    if request.method == 'GET':
        if set(['channel', 'button', 'state']).issubset(set(request.args.keys())):
            params = {}
            params['channel'] = int(request.args['channel'])
            params['button'] = int(request.args['button'])
            params['state'] = True if request.args['state'] == 'on' else False
            perform_action(params)
        return redirect('/')

@app.route('/getplugs')
def get_plugs():
    return all_plugs()
    
@app.route('/editplugs')
def edit_plugs():
    text = ''.join(open('./plugs.yaml', 'r').readlines())
    return render_template('edit_plugs.html', pagetitle='Edit Plugs',  yaml=text)
   
@app.route('/')
def index():
    return render_template('set_plugs.html', pagetitle='Set Plugs', plugs=yaml.load(open('./plugs.yaml', 'r')))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
