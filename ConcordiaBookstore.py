from flask import Flask, render_template

# set up the application with Flask
app = Flask(__name__, '/static', static_folder='static', template_folder='templates')
app.debug = True
# this is so the templates always reload when there are changes made
app.config['TEMPLATES_AUTO_RELOAD'] = True

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run()
