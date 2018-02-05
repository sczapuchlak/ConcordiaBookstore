from flask import Flask, render_template

# set up the application with Flask

app = Flask(__name__, '/static', static_folder='static',
            template_folder='templates')
app.debug = True

# this is so the templates always reload when there are changes made

app.config['TEMPLATES_AUTO_RELOAD'] = True


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/signUp.html', methods=['GET'])
def signUp():
    return render_template('signUp.html')

@app.route('/login.html', methods=['GET'])
def login():
    return render_template('login.html')

@app.route('/about.html', methods=['GET'])
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run()


