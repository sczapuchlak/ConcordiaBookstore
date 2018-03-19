import MySQLdb
import smtplib
from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from passlib.hash import sha256_crypt
from wtforms import Form, StringField, PasswordField, validators
from functools import wraps
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart



def connection():
    conn = MySQLdb.connect(host="localhost",
                           user = "root",
                           passwd = "password",
                           db = "bookexchange")


    # Create a Cursor object to execute queries.
    c = conn.cursor()

    return c, conn

# set up the application with Flask
app = Flask(__name__, '/static', static_folder='static',
            template_folder='templates')

# this is so the templates always reload when there are changes made
app.config['TEMPLATES_AUTO_RELOAD'] = True

# token generation serializer
serial = URLSafeTimedSerializer('its a secret')

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
        confirm = False

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
                                                                    INSERT INTO user( USER_PW, USER_Email, USER_FName, USER_LName, USER_Cnfrm)
                                                                    VALUES(%s, %s, %s, %s, %s)''',
                      (password, email, firstname, lastname, confirm))

            conn.commit()

            # generate token
            token = serial.dumps(email, salt='email-confirm')

            # create link for confirmation email
            link = url_for('confirm_email', token=token, external=True)

            # message parameters
            fromaddr = 'csp.bookshare@gmail.com'
            msg = MIMEMultipart()
            msg['From'] = fromaddr
            msg['To'] = email
            msg['Subject'] = 'Please confirm your email address'
            body = render_template('/activate.html', confirm_url=link)
            msg.attach(MIMEText(body, 'html'))

            # open email server connection
            s = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=120)
            s.login('csp.bookshare@gmail.com', 'Capstone450')
            text = msg.as_string()

            # send message
            s.sendmail(fromaddr, email, text)

            # close email server connection
            s.quit()

            # flash("Please Sign in below")
            c.close()
            conn.close()

            flash("Thanks for registering! Please verify your account with the email we sent you before logging in", 'success')

        return redirect(url_for('login', flash=flash))
        # return render_template('login.html')
    return render_template(url_for('signup'))
    #return render_template('signup.html', form=form)

@app.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        email = serial.loads(token, salt='email-confirm', max_age=3600)

        # create connection
        c, conn = connection()

        c.execute("SELECT USER_Cnfrm FROM user WHERE USER_Email = %s", (email,))
        test = c.fetchone()[0]

        if test == 1:
             flash("You have already registered. Please sign in", 'danger')
             c.close()
             conn.close()
             return redirect(url_for("login", flash=flash))
        c.execute("UPDATE user SET USER_Cnfrm = 1 WHERE USER_Email = %s", (email,))
        conn.commit()

        c.close()
        conn.close()
    except SignatureExpired:
        # if the token has expired, extract the email address and redirect them to the page to resend link
        email = serial.loads(token, salt='email-confirm')
        return render_template('resend.html', email=email)
    flash("You have registered successfully. Please log in", 'success')
    return redirect(url_for("login", flash=flash))


@app.route('/resend/<email>', methods=['GET'])
def resend(email):
    # generate token
    token = serial.dumps(email, salt='email-confirm')

    # create link for confirmation email
    link = url_for('confirm_email', token=token, external=True)

    # message parameters
    fromaddr = 'csp.bookshare@gmail.com'
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = email
    msg['Subject'] = 'Please confirm your email address'
    body = render_template('/activate.html', confirm_url=link)
    msg.attach(MIMEText(body, 'html'))

    # open email server connection
    s = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=120)
    s.login('csp.bookshare@gmail.com', 'Capstone450')
    text = msg.as_string()

    # send message
    s.sendmail(fromaddr, email, text)

    # close email server connection
    s.quit()

    flash("Please check your email address for the new verification link", 'success')
    return redirect(url_for("login", flash=flash))



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
        c.execute("SELECT * FROM user WHERE  USER_Email = %s", (user_email,))

        # get stored password hash from db
        result = c.fetchone()[1]

        #get confirmation status from db
        c.execute("SELECT USER_Cnfrm FROM user WHERE USER_Email = %s", (user_email,))
        conf = c.fetchone()[0]

        #compare and verify passwords
        if sha256_crypt.verify(user_password, result):
            if conf == 1:
                session['logged_in'] = True
                session['user_email'] = user_email
            else:
                flash("Unconfirmed registration. Please verify your email using the link sent to you", 'danger')
                return render_template(url_for("login", flash=flash))

            flash("You are now logged in", 'success')
            # msg = "You are now logged in"
            return render_template("home.html", flash=flash)
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
            flash("Unauthorized, Please log in", 'danger')
            return redirect(url_for('login', flash=flash))
    return wrap

@app.route('/logout')
def logout():
    #kill session
    session.clear()
    flash("You are now logged out", 'success')
    #msg = "You are now logged in"
    return redirect(url_for('login', flash=flash))

@app.route('/home.html', methods=["GET", "POST"])
@require_logged_in
def home():
    # rows = bookForum.query.all()
    return render_template("home.html",
                           title='Listing Homepage')
                           # ,rows=rows)


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