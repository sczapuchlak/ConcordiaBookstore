
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import base64
from base64 import b64encode
import os
from flask_mail import Mail, Message
import MySQLdb
from datetime import datetime
from threading import Thread
import serial as serial
from flask import Flask, render_template, flash, redirect, url_for, session, logging, request, abort, current_app
from future.backports.email.mime.text import MIMEText
from passlib.hash import sha256_crypt
from wtforms import Form, StringField, PasswordField, SelectField, validators
from functools import wraps
from random import *
from wtforms.validators import DataRequired, Email
from form import EmailForm, PasswordForm, BookSearchForm
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, URLSafeTimedSerializer, SignatureExpired

app = Flask(__name__)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'cspbookstore@gmail.com'
app.config['MAIL_PASSWORD'] = 'Concordia2018$'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

url = URLSafeTimedSerializer('SECRET_KEY')

# set up the application with Flask
app = Flask(__name__, '/static', static_folder='static',
            template_folder='templates')

# this is so the templates always reload when there are changes made
app.config['TEMPLATES_AUTO_RELOAD'] = True


# token generation serializer


class EmailForm(Form):
    email = StringField('Email', validators=[DataRequired(), Email()])


class PasswordForm(Form):
    password = PasswordField('Password', validators=[DataRequired()])


global userID


def connection():
    conn = MySQLdb.connect(host="localhost",
                           user="root",

                           # passwd="AMH12bmh#$",
                           passwd="mysql",
                           db="bookexchange")

    # Create a Cursor object to execute queries.
    c = conn.cursor()

    return c, conn


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/search.html', methods=["GET", "POST"])
def search():
    search = BookSearchForm(request.form)
    if request.method == 'POST':
        return search_results(search)

    return render_template('search.html', form=search)


@app.route('/results')
def search_results(search):
    results = []
    search_string = search.data['search']

    if search.data['search'] == '':
            # create connection
            c, conn = connection()
            c.executemany('''select * from book where BK_Title = %s''', request.form['search'])
            return render_template("search.html", records=c.fetchall())

    if not results:
        flash('No results found!')
        return redirect('/search.html')
    else:
        # display results
        return render_template('search.html', results=results)


@app.route('/signup.html', methods=["GET", "POST"])
def signup():
    test = "@csp.edu"

    # form = SignUpForm(request.form)
    if request.method == "POST":
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        studnumber = request.form['studentnumber']
        email = request.form['email']
        password = sha256_crypt.encrypt((str(request.form['password'])))

        # create connection
        c, conn = connection()

        result = c.execute("SELECT * FROM user WHERE  USER_Email = %s", (email,))

        if int(result) > 0:
            error = "Email exist. Please use a different email";
            return render_template("signup.html", error=error)

        elif len(request.form['studentnumber']) < 1:
            error = "Your L number is less than 8 characters long";
            return render_template("signup.html", error=error)

        elif email[-8:] != test:
            error = "Not a valid CSP email";
            return render_template("signup.html", error=error)

        elif len(request.form['password']) < 8:
            error = "Password must be more than 8 characters";
            return render_template("signup.html", error=error)

        elif request.form['password'] != request.form['confirmpassword']:
            error = "Password doesn't match"
            return render_template("signup.html", error=error)

        else:

            c.execute('''
                    INSERT INTO user( USER_PW, USER_Email, USER_FName, USER_LName)
                    VALUES(%s, %s, %s, %s)''',
                      (password, email, firstname, lastname))
            user_id = conn.insert_id()
            print(user_id)

            conn.commit()

            c.execute('''


                      INSERT INTO student(STU_ID, STU_Address, STU_City, STU_State, STU_Zip, STU_Phone, USER_ID)
                      VALUES(%s, 'St. Address', 'City', 'State', 'Zip Code', '(000)000-0000', %s)''',
                      (studnumber, [user_id]))

            conn.commit()

            # generate token
            token = url.dumps(email, salt='email-confirm')

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

            conn.commit()

            flash("Thanks for registering!")
            flash("Please Sign in below")
            c.close()
            conn.close()

        return redirect(url_for('login', flash=flash))
    return render_template('signup.html')
    # return render_template('signup.html', form=form)


@app.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        email = url.loads(token, salt='email-confirm', max_age=3600)

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
        email = url.loads(token, salt='email-confirm')
        return render_template('resend.html', email=email)
    flash("You have registered successfully. Please log in", 'success')
    return redirect(url_for("login", flash=flash))


@app.route('/resend/<email>', methods=['GET'])
def resend(email):
    # generate token
    token = url.dumps(email, salt='email-confirm')

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


@app.route('/login.html', methods=['GET', 'POST'])
def login():

    try:

        if request.method == "POST":
            # get form values
            user_email = request.form['email']
            user_password = request.form['password']

            # create connection
            c, conn = connection()

            # get email addresss from db
            c.execute("SELECT * FROM user WHERE  USER_Email = %s", (user_email,))

            # get stored password hash from db
            result = c.fetchone()[1]

            # get confirmation status from db
            c.execute("SELECT USER_Cnfrm FROM user WHERE USER_Email = %s", (user_email,))
            conf = c.fetchone()[0]

            # compare and verify passwords
            if sha256_crypt.verify(user_password, result):
                if conf == 1:
                    session['logged_in'] = True
                    if session['logged_in'] is True:
                        session['user_email'] = user_email
                else:
                    flash("Unconfirmed registration. Please verify your email using the link sent to you", 'danger')
                    return render_template(url_for("login", flash=flash))

                c.execute("SELECT * FROM user WHERE  USER_Email = %s", (user_email,))
                # get user first and last name
                user_details = c.fetchall()
                for data in user_details:
                    session.firstname = data[3]
                    session.lastname = data[4]
                session.fullname = session.firstname + " " + session.lastname

                # flash("You are now logged in")
                msg = "You are now logged in"
                # return render_template("home.html", msg=msg)
                return redirect("home.html")
                # return redirect(url_for("login"))

            else:
                error = "Invalid credential, try again"
                return render_template("login.html", error=error)

        return render_template("login.html")

    except Exception as e:
        print(e)
        error = "Credentials don't exist. Please Sign Up "
        return render_template("login.html", error=error)


# check if user is logged in
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
    # kill session
    session.clear()
    flash("You are now logged out")
    # msg = "You are now logged in"
    return redirect(url_for('login'))


@app.route('/home.html', methods=["GET", "POST"])
@require_logged_in
def home():

    c, conn = connection()

    c.execute("SELECT USER_FName,USER_LName, LST_ID, LST_Title, LST_SellType, LST_Date,LST_ID "


              "FROM user,listing "
              "WHERE user.USER_ID = listing.LST_USER_ID")

    # get Listing table
    list = c.fetchall()

    # print(list)
    return render_template('home.html', data=list)

    # for data in list:
    #     firtsname = data[0]
    #     lastname = data[1]
    #     listID = data[2]
    #     listtitle = data[3]
    #     fullname = firtsname +" "+ lastname
    #
    #     #for testing only
    #     print(fullname)
    #     #print(firtsname)
    #     #print(lastname)
    #     print(listID)
    #     print(listtitle)
    #     print(data)
    # #get
    # return render_template("home.html", data=list)


@app.route('/mailto/<target>')
@require_logged_in
def mailto(target):
    return render_template('mailto.html', target=target)


@app.route('/send_msg/<target>', methods=["GET", "POST"])
@require_logged_in
def send_msg(target):
    subject = request.form['subject']
    message = request.form['message']
    email = session['user_email']

    c, conn = connection()

    # c.execute('''SELECT USER_Email FROM comments JOIN ON user
    #              WHERE comments.COM_USER_ID = user.USER_ID
    #              AND comments.COM_USER_ID = %s''', [target])

    c.execute('''SELECT USER_Email FROM user WHERE USER_ID = %s''', [target])

    # message parameters
    fromaddr = 'csp.bookshare@gmail.com'
    toaddr = c.fetchone()[0]
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = subject
    body = "<p>Message sent from " + email + "<br /><br />" + message + "</p>"
    msg.attach(MIMEText(body, 'html'))

    conn.close()

    # open email server connection
    s = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=120)
    s.login('csp.bookshare@gmail.com', 'Capstone450')
    text = msg.as_string()

    # send message
    s.sendmail(fromaddr, toaddr, text)

    # close email server connection
    s.quit()

    return render_template('sent.html')


@app.route('/profile.html', methods=["GET", "POST"])
@require_logged_in
def profile():

    c, conn = connection()

    email = session['user_email']

    # get User information with JOIN to get User's Phone number
    c.execute("SELECT USER_FName, USER_LName, USER_Email, USER_Rating, "
              "STU_ID, STU_Address, STU_City, STU_State, STU_Zip, STU_Phone, user.USER_ID "
              "FROM user JOIN student ON user.USER_ID=student.USER_ID "
              "WHERE USER_Email = %s", (email,))

    # assign from SQL statement to an array named prof
    prof = c.fetchall()

    for data in prof:
        proFName = data[0]
        proLName = data[1]
        proEmail = data[2]
        proRating = data[3]
        proID = data[10]
        studId = data[4]
        proAddy = data[5]
        proCity = data[6]
        proState = data[7]
        proZip = data[8]
        proPhone = data[9]
        proName = proFName + " " + proLName

    print(prof)

    conn.commit()

    return render_template("profile.html", data=prof)


@app.route('/updateProfile.html', methods=["GET", "POST"])
@require_logged_in
def updateProfile():

    if request.method == "POST":

        c, conn = connection()

        email = session['user_email']

        # get User information with JOIN to get User's information
        c.execute("SELECT USER_FName, USER_LName, USER_Email, USER_Rating, "
                  "STU_ID, STU_Address, STU_City, STU_State, STU_Zip, STU_Phone, user.USER_ID "
                  "FROM user JOIN student ON user.USER_ID=student.USER_ID "
                  "WHERE USER_Email = %s", (email,))

        pro = c.fetchall()

        for data in pro:
            proFName = data[0]
            proLName = data[1]
            proEmail = data[2]
            proRating = data[3]
            proID = data[10]
            studId = data[4]
            proAddy = data[5]
            proCity = data[6]
            proState = data[7]
            proZip = data[8]
            proPhone = data[9]
            proName = proFName + " " + proLName

        print(pro)

        profFName = request.form['field1']
        profLName = request.form['field2']
        profStuID = request.form['field3']
        profAddy = request.form['field4']
        profCity = request.form['field5']
        profState = request.form['field6']
        profZip = request.form['field7']
        profPhone = request.form['field8']

        if profFName == '':
            Fname = proFName
        else:
            Fname = profFName

        if profLName == '':
            Lname = proLName
        else:
            Lname = profLName

        if profStuID == '':
            Stud = studId
        else:
            Stud = profStuID

        if profAddy == '':
            Addy = proAddy
        else:
            Addy = profAddy

        if profCity == '':
            City = proCity
        else:
            City = profCity

        if profState == '':
            State = proState
        else:
            State = profState

        if profZip == '':
            Zip = proZip
        else:
            Zip = profZip

        if profPhone == '':
            Phone = proPhone
        else:
            Phone = profPhone

        c.execute('''

                  UPDATE student
                  SET STU_ID = %s, STU_Address = %s,
                  STU_City = %s, STU_State = %s,
                  STU_Zip = %s, STU_Phone = %s
                  WHERE student.USER_ID = %s''',
                  (Stud, Addy, City, State, Zip, Phone, proID, ))
        conn.commit()

        c.execute('''
                  UPDATE user SET USER_FName = %s, USER_LName = %s
                  WHERE USER_Email = %s''',
                  (Fname, Lname, email, ))

        conn.commit()

        return redirect("profile.html")
    return render_template("updateProfile.html")


@app.route('/newpost.html', methods=["GET", "POST"])
@require_logged_in
def newpost():

    if request.method == "POST":

        file = request.files['pic']

        # image = open(file, 'rb')  # open binary file in read mode
        # image_read = file.read()
        # newFile = base64.encode(image_read)
        # newFile = base64.b64encode(image_read)

        # file.save(file.filename)
        newFile = file.read()

        # newFile = base64.encodestring(newFile1)

        # newFile1 = newFile.encode("base64")

        # print(file)
        # print(newFile)

        # Book Information
        book_ISBN = request.form['field4']
        listing_title = request.form['field5']
        book_Author = request.form['field6']
        book_publisher = request.form['field7']
        book_Edition = request.form['field8']
        # book_back_photo = request.form['field9']
        book_Comments = request.form['field10']
        # listing_date = request.form['todaysdate']
        # value = str(listing_date)

        # Course Information
        course_Title = request.form['field11']
        course_Number = request.form['field12']

        # Payment Information
        sale_type = request.form['field13']

        c, conn = connection()

        email = session['user_email']

        c.execute("SELECT * FROM user WHERE  USER_Email = %s", (email,))
        details = c.fetchall()
        for data in details:
            user_id = data[0]
            u_email = data[2]

            # print(data)
            print(user_id)
            print(u_email)

        print(user_id)

        conn.commit()

        c.execute('''
                  INSERT INTO course (CRS_ID, CRS_Name )
                  VALUES(%s,%s)''',
                  (course_Number, course_Title,))
        conn.commit()

        c.execute('''
                 INSERT INTO photo(PHT_Image)
                 VALUES(%s)''',
                  [newFile])
        photo_id = conn.insert_id()
        print(photo_id)
        conn.commit()

        c.execute('''
                 INSERT INTO book (CRS_ID, BK_Publisher, PHT_ID, BK_Sale_Type, BK_Comment, BK_Title, BK_ISBN, BK_Author, BK_Edition )
                 VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
                  (course_Number, book_publisher, [photo_id], sale_type, book_Comments, listing_title, book_ISBN, book_Author,
                   book_Edition))
        course_id = conn.insert_id()
        conn.commit()

        c.execute("SELECT * FROM user WHERE  USER_Email = %s", (email,))

        now = datetime.now()
        print(now)

        c.execute('''
                INSERT INTO listing (LST_SellType, LST_Title, BK_ID, LST_USER_ID,LST_Date)
                VALUES(%s,%s,%s,%s,%s)''',
                  (sale_type, listing_title, [course_id], user_id, now))
        conn.commit()

    return render_template("newpost.html")


@app.route('/listing/<list_id>', methods=["GET", "POST"])
# @require_logged_in
def listing(list_id=None):

    c, conn = connection()

    c.execute("SELECT USER_FName,USER_LName, USER_ID, LST_ID, LST_Title, LST_SellType, LST_Date, BK_Author,BK_Edition,BK_Title,"
              "BK_Publisher,BK_Comment,BK_ISBN,USER_Rating,course.CRS_ID,course.CRS_Name, photo.PHT_ID, photo.PHT_Image "
              "FROM user,listing,book,course,photo "
              "WHERE LST_ID = %s AND listing.LST_USER_ID = user.USER_ID AND listing.BK_ID = book.BK_ID "
              "AND book.CRS_ID = course.CRS_ID AND book.PHT_ID = photo.PHT_ID ", [list_id])

    conn.commit()

    result = c.fetchall()
    for data in result:
        firstname = data[0]
        # print(data[1])
        lastname = data[1]
        id = data[2]
        listID = data[3]
        listtitle = data[4]
        listSellType = data[5]
        listDate = data[6]
        bookAuthor = data[7]
        bookEdition = data[8]
        bookTitle = data[9]
        bookPublisher = data[10]
        bookDesc = data[11]
        bookISBN = data[12]
        userRating = data[13]
        courseID = data[14]
        courseName = data[15]
        photoID = data[16]
        photoImage = data[17]

        print(data)

    # Pull comments from comments table for display related to selected listing
    c.execute("SELECT COM_Auth, COM_Date, COM_Body, COM_USER_ID FROM comments WHERE LST_ID = %s", [listID])
    rows = c.fetchall()

    return render_template("listing.html", data=data, firstname=firstname, lastname=lastname, listID=listID,
                           listtitle=listtitle, listDate=listDate, bookTitle=bookTitle, bookAuthor=bookAuthor,
                           bookEdition=bookEdition, listSellType=listSellType,bookPublisher=bookPublisher,
                           bookDesc=bookDesc, bookISBN=bookISBN, userRating=userRating, courseID=courseID,
                           courseName=courseName,id=id, image=photoImage, rows=rows)


@app.route("/submit_comment/<list_id>", methods=["GET", "POST"])
@require_logged_in
def submit_comment(list_id):
    date = datetime.now()
    msg = request.form['message']
    email = session['user_email']

    c, conn = connection()

    c.execute("SELECT USER_FName, USER_LName, USER_ID FROM user WHERE USER_Email = %s", [email])
    result = c.fetchall()
    for data in result:
        firstname = data[0]
        lastname = data[1]
        id = data[2]

    auth = firstname + " " + lastname
    # c.execute('''INSERT INTO comments (LST_ID,COM_Auth,COM_Date,COM_Body,...)
    #           VALUES (%s, %s, %s, %s, %s)''', (list_id, auth, date, msg, email))
    c.execute('''INSERT INTO comments (LST_ID,COM_Auth,COM_Date,COM_Body, COM_USER_ID) 
                          VALUES (%s, %s, %s, %s, %s)''', (list_id, auth, date, msg, id))
    conn.commit()

    conn.close()

    return redirect(url_for("listing", list_id=list_id))


@app.route('/changepassword.html', methods=["GET", "POST"])
@require_logged_in
def changepassword():

    if request.method == "POST":

        oldPassword = request.form['oldPassword']
        newPassword = request.form['newPassword']
        confirmPassword = request.form['confirmPassword']

        # create connection
        c, conn = connection()

        if len(newPassword) < 8:
            error = "Password must be more than 8 characters"
            return render_template("changepassword.html", error=error)

        elif newPassword != confirmPassword:
            error = "Password doesn't match"
            return render_template("changepassword.html", error=error)

        elif newPassword == oldPassword:
            error = "Old password cannot match new password"
            return render_template("changepassword.html", error=error)
        else:

            password = sha256_crypt.encrypt((str(newPassword)))

            email = session['user_email']


            c.execute("""
                      UPDATE user
                      SET USER_PW=%s
                      WHERE USER_Email=%s
                   """, (password, email))

            conn.commit()

    return render_template("changepassword.html")


@app.route('/reset.html', methods=["GET", "POST"])
def reset():

    try:
        c, conn = connection()
        if request.method == "POST":

            email = request.form['email']

            c.execute("SELECT USER_Email, USER_FName, USER_LName "
                      "FROM user "
                      "WHERE USER_Email = %s", (email,))

            result = c.fetchall()
            for data in result:
                user = data[0]
                firstname = data[1]
                lastname = data[2]

                fullname = firstname + " " + lastname

            if email == user:
                token = url.dumps(email, salt='reset-password')

                message = Message('Reset Password', sender='awahndingwan@gmail.com', recipients=[email])

                password_link = url_for('reset_token', token=token, _external=True)

                message.body = render_template('email_password_reset.html', password_link=password_link,
                                               fullname=fullname)
                mail.send(message)

                msg = 'Please check your email for a password reset link.'
                return render_template('login.html', msg=msg)
            else:
                error = 'Invalid Email Address'
                return render_template('login.html', error=error)
    except:
        error = "Account doesn't exist. Please Sign Up"
        return render_template('reset.html', error=error)

    return render_template('reset.html')


@app.route('/reset_token/<token>', methods=["GET", "POST"])
def reset_token(token):
    try:
        email = url.loads(token, salt='reset-password', max_age=3600)
    except:
        error = 'The password reset link is invalid or has expired.'
        return render_template('reset.html', error=error)

    c, conn = connection()
    if request.method == "POST":
        password1 = request.form['password']
        confirmpassword = request.form['confirmpassword']
        print(email)
        print(password1)

        c.execute("SELECT USER_Email "
                  "FROM user "
                  "WHERE USER_Email = %s", (email,))
        user = c.fetchone()[0]

        print(user)
        if user == email:
            if password1 != confirmpassword:
                error = "Password doesn't match"
                return render_template("reset_token.html", error=error, token=token)

            elif len(password1) < 8:
                error = "Password must be more than 8 characters";
                return render_template("reset_token.html", error=error, token=token)

            else:
                password = sha256_crypt.encrypt((str(password1)))
                print(password)

                c.execute("""
                                                     UPDATE user
                                                     SET USER_PW=%s
                                                     WHERE USER_Email=%s
                                                  """, (password, email))
                conn.commit()
                # msg = 'Your password has been updated! '
                return redirect(url_for('login'))
                # return render_template('login.html', msg=msg)

        else:
            error = 'Invalid email address!'
            render_template('reset.html', error=error)

    conn.commit()

    return render_template('reset_token.html', token=token)


if __name__ == '__main__':
    app.secret_key='SECRET_KEY'
    app.run(debug=True)
