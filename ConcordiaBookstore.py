import base64
from base64 import b64encode
import MySQLdb
from datetime import datetime
from flask import Flask, render_template, flash, redirect, url_for, session, logging, request, abort
from passlib.hash import sha256_crypt
from wtforms import Form, StringField, PasswordField, validators
from functools import wraps
from random import *
from form import EmailForm, PasswordForm
# from utils import send_email, ts

global userID

def connection():
    conn = MySQLdb.connect(host="localhost",
                           user = "root",
                           passwd = "AMH12bmh#$",
                           db = "bookexchange")

    # Create a Cursor object to execute queries.
    c = conn.cursor()

    return c, conn

# set up the application with Flask
app = Flask(__name__, '/static', static_folder='static',
            template_folder='templates')

# this is so the templates always reload when there are changes made
app.config['TEMPLATES_AUTO_RELOAD'] = True

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')



@app.route('/signup.html', methods=["GET", "POST"])
def signup():
    test = "@csp.edu"

    #form = SignUpForm(request.form)
    if request.method == "POST":
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        studnumber = request.form['studentnumber']
        email = request.form['email']
        password = sha256_crypt.encrypt((str(request.form['password'])))

        #create connection
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

            conn.commit()
            flash("Thanks for registering!")
            flash("Please Sign in below")
            c.close()
            conn.close()

        return redirect(url_for('login', flash=flash))
    return render_template('signup.html')
    #return render_template('signup.html', form=form)


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

            #xompare and verify passwords
            if sha256_crypt.verify(user_password, result):

                session['logged_in'] = True

                if session['logged_in'] is True:
                    session['user_email'] = user_email

                    c.execute("SELECT * FROM user WHERE  USER_Email = %s", (user_email,))
                    # get user first and last name
                    user_details = c.fetchall()
                    for data in user_details:
                        session.firstname = data[3]
                        session.lastname = data[4]
                    session.fullname = session.firstname + " " + session.lastname

                    # for testing purposes
                    #print(firstname, lastname)
                    #print(fullname)

                #flash("You are now logged in")
                msg = "You are now logged in"
                # return render_template("home.html", msg=msg)
                return redirect("home.html")
                #return redirect(url_for("login"))


            else:
                error = "Invalid credential, try again"
                return render_template("login.html", error=error)

        return render_template("login.html")

    except Exception as e:
        print(e)
        error = "Credentials don't exist. Please Sign Up "
        return render_template("login.html", error=error)


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
    flash("You are now logged out")
    #msg = "You are now logged in"
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

    #print(list)
    return render_template('home.html', data=list)


    # for data in list:
        # firtsname = data[0]
        # lastname = data[1]
        # listID = data[2]
        # listtitle = data[3]

        # fullname = firtsname +" "+ lastname
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

        #image = open(file, 'rb')  # open binary file in read mode
        #image_read = file.read()
        #newFile = base64.encode(image_read)
        #newFile = base64.b64encode(image_read)

        # file.save(file.filename)
        newFile = file.read()

        #newFile = base64.encodestring(newFile1)

        #newFile1 = newFile.encode("base64")

        #print(file)
        #print(newFile)

        # Book Information
        book_ISBN = request.form['field4']
        listing_title = request.form['field5']
        book_Author = request.form['field6']
        book_publisher = request.form['field7']
        book_Edition = request.form['field8']
        #book_back_photo = request.form['field9']
        book_Comments = request.form['field10']
        #listing_date = request.form['todaysdate']
      # value = str(listing_date)
        #print(value)


        # Course Information
        course_Title = request.form['field11']
        course_Number = request.form['field12']

        #Payment Information
        sale_type = request.form['field13']

        c, conn = connection()

        email = session['user_email']

        c.execute("SELECT * FROM user WHERE  USER_Email = %s", (email,))
        details = c.fetchall()
        for data in details:
            user_id = data[0]
            u_email = data[2]

            #print(data)
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
#@require_logged_in
def listing(list_id=None):

    c, conn = connection()

    c.execute("SELECT USER_FName,USER_LName, LST_ID, LST_Title, LST_SellType, LST_Date,LST_ID "
              "FROM user,listing "
              "WHERE LST_ID = %s", [list_id])

    conn.commit()

    result = c.fetchall()
    for data in result:
        firstname = data[0]
        #print(data[1])
        lastname = data[1]
        listID = data[2]
        listtitle = data[3]
        print(data)



    return render_template("listing.html", data=data, firstname=firstname, lastname=lastname, listID=listID, listtitle=listtitle)



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



@app.route('/pwreset.html', methods=["GET", "POST"])
def pwreset():
#     form = EmailForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(email=form.email.data).first_or_404()
#
#         subject = "Password reset requested"
#
#         token = ts.dumps(user.email, salt='recover-key')
#
#         recover_url = url_for(
#             'reset_with_token',
#             token=token,
#             _external=True)
#
#         html = render_template(
#             'pwreset.html',
#             recover_url=recover_url)
#
#         # Let's assume that send_email was defined in myapp/util.py
#         send_email(user.email, subject, html)
#
#         return redirect(url_for('home'))
    return render_template('pwreset.html')
#,form=form)
#
# @app.route('/pwreset/<token>', methods=["GET", "POST"])
# def reset_with_token(token):
#     try:
#         email = ts.loads(token, salt="recover-key", max_age=86400)
#     except:
#         abort(404)
#
#     form = PasswordForm()
#
#     if form.validate_on_submit():
#         user = User.query.filter_by(email=email).first_or_404()
#
#         user.password = form.password.data
#
#         # need to add user to database session
#         #commit the DB session
#
#         return redirect(url_for('signin'))
#
#     return render_template('pwreset.html', form=form, token=token)

if __name__ == '__main__':
    app.secret_key='haha you cant guess my secret key'
    app.run(debug=True)