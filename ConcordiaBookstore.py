import MySQLdb
from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from passlib.hash import sha256_crypt
from wtforms import Form, StringField, PasswordField, validators
from functools import wraps


def connection():
    conn = MySQLdb.connect(host="localhost",
                           user = "root",
                           passwd = "gikQr6kn",
                           db = "bookexchange")


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
        validators.EqualTo('confirmpassword', message="Passwords must match")
    ])
    confirmpassword = PasswordField('Re-enter Password')



@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


def validate_email():

    test = "@csp.edu"
    email = request.form['email']
    # create connection
    c, conn = connection()

    result = c.execute("SELECT * FROM user WHERE  USER_Email = %s", (email,))

    if int(result) > 0:
        error = "Email exist. Please use a different email";
        return render_template("signup.html", error=error)

    elif email[-8:] != test:
        error = "Not a valid CSP email";
        return render_template("signup.html", error=error)


@app.route('/signup.html', methods=["GET", "POST"])
def signup():
    test = "@csp.edu"

    #form = SignUpForm(request.form)
    if request.method == "POST":
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        password = sha256_crypt.encrypt((str(request.form['password'])))

        #create connection
        c, conn = connection()

        result = c.execute("SELECT * FROM user WHERE  USER_Email = %s", (email,))

        if int(result) > 0:
            error = "Email exist. Please use a different email";
            return render_template("signup.html", error=error)

        elif email[-8:] != test:
            error = "Not a valid CSP email";
            return render_template("signup.html", error=error)

        elif len(request.form['password']) < 8:
            error = "Password must be more than 8 charecters";
            return render_template("signup.html", error=error)

        elif request.form['password'] != request.form['confirmpassword']:
            error = "Password doesn't match"
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
    return render_template('signup.html')
    #return render_template('signup.html', form=form)



@app.route('/about.html', methods=['GET'])
def about():
    return render_template('about.html')


@app.route('/login.html', methods=['GET', 'POST'])
def login():

  try:

    if request.method == "POST":
        #get form values
        user_email = request.form['email']
        user_password = request.form['password']

        # create connection
        c, conn = connection()

        #get email addresss from db
        result = c.execute("SELECT * FROM user WHERE  USER_Email = %s", (user_email,))

        # get stored password hash from db
        result = c.fetchone()[1]

        #xompare and verify passwords
        if sha256_crypt.verify(user_password, result):
            session['logged_in'] = True
            session['user_email'] = user_email

            #flash("You are now logged in")
            msg = "You are now logged in"
            return render_template("home.html", msg=msg)
            #return redirect(url_for("login"))

        else:
            #flash("Invalid credential, try again")
            error = "Invalid credential, try again"
            return render_template("login.html", error=error)

    return render_template("login.html")

  except Exception as e:
      flash(e)
     # error = "Invalid Credentials, try again"
      return render_template("login.html")

#check if user is logged in
def require_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
                return f(*args, **kwargs)
        else:
            flash("unauthorized, Please log in")
            return redirect(url_for('login'))
    return wrap

@app.route('/logout')
def logout():
    #kill session
    session.clear()
    flash("you are now logged out")
    #msg = "You are now logged in"
    return redirect(url_for('login'))

@app.route('/home.html', methods=["GET", "POST"])
@require_logged_in
def home():

    # c, conn = connection()
    #
    # results = c.execute("SELECT userid, first_name, last_name, post_title from userTable order by date desc")
    # rows = results.fetchall()

    return render_template("home.html",
                           title='Listing Homepage')
                           # ,rows=listings)


@app.route('/profile.html', methods=["GET", "POST"])
@require_logged_in
def profile():
     return render_template("profile.html")

@app.route('/newpost.html', methods=["GET", "POST"])
@require_logged_in
def newpost():
     return render_template("newpost.html")



if __name__ == '__main__':
    app.secret_key='haha you cant guess my secret key'
    app.run(debug=True)


