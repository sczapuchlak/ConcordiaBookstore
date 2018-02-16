import MySQLdb
from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
# from flask_mysqldb import MySQL
from passlib.hash import sha256_crypt
from wtforms import Form, StringField, PasswordField, validators

def connection():
    conn = MySQLdb.connect(host="localhost",
                           user = "root",
                           passwd = "yannique16",
                           db = "bookexchange2")


    # Create a Cursor object to execute queries.
    c = conn.cursor()

    return c, conn

# set up the application with Flask
app = Flask(__name__, '/static', static_folder='static',
            template_folder='templates')

# this is so the templates always reload when there are changes made
app.config['TEMPLATES_AUTO_RELOAD'] = True

class SignUpForm(Form):

    firstname = StringField('First Name', [validators.DataRequired()])
    lastname= StringField('Last Name', [validators.DataRequired()])
    email = StringField('Email Address', [validators.DataRequired(), validators.Email()])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirmpassword', message='Passwords must match')
    ])
    confirmpassword = PasswordField('Re-enter Password')

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/home')
def home():
    return render_template('home .html')


@app.route('/signup.html', methods=["GET", "POST"])
def signup():
    form = SignUpForm(request.form)
    if request.method == "POST" and form.validate():
        firstname = form.firstname.data
        lastname = form.lastname.data
        email = form.email.data
        password = sha256_crypt.encrypt((str(form.password.data)))

        #create connection
        c, conn = connection()

        result = c.execute("SELECT * FROM user WHERE  USER_Email = %s", (email,))

        if int(result) > 0:
            error = "Email exist. Please use a different email";
            #flash("Email exist. Please use a different email")
            return render_template("signup.html", error=error)

        else:

            c.execute('''
                                                                    INSERT INTO user( USER_PW, USER_Email, USER_FName, USER_LName)
                                                                    VALUES(%s, %s, %s, %s)''',
                      (password, email, firstname, lastname))

            conn.commit()
            flash("Thanks for registering!")
            flash("Please Sign in below")
            c.close()
            conn.close()

        return redirect(url_for('login', flash=flash))
    return render_template('signup.html', form=form)

@app.route('/login.html', methods=["GET", "POST"])
def login():
    return render_template("login.html")

@app.route('/about.html', methods=['GET'])
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.secret_key='haha you cant guess my secret key'
    app.run(debug=True)



