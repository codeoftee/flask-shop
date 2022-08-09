from datetime import timedelta
from fileinput import filename
import hashlib
import os
import profile
from flask import render_template, request, flash, send_from_directory, session
from flask import url_for, redirect

from app import app, db
from config import Config
from models import Product, User
from shop_functions import check_login

from werkzeug.utils import secure_filename

@app.route('/delete/<pid>')
def delete_product(pid):
     # check if product is in db
    pid = int(pid)
    product = Product.query.filter_by(id=pid).first()
    if product is None:
        flash("Product doesn't exist!")
        return redirect(url_for('dashboard'))
    db.session.delete(product)
    db.session.commit()
    flash("Product deleted successfully!")
    return redirect(url_for('dashboard'))

@app.route('/edit/<pid>', methods=['POST', 'GET'])
def edit_product(pid):
    profile = check_login()
    if profile is None:
        return redirect(url_for('login'))
    
    # check if product is in db
    pid = int(pid)
    product = Product.query.filter_by(id=pid).first()
    if product is None:
        flash("Product doesn't exist!")
        return redirect(url_for('dashboard'))

    if request.method == 'GET':
        return render_template('edit.html', product=product)
    
    # update product info
    product.title = request.form['title']
    product.category = request.form['category']
    product.price = request.form['price']
    product.description = request.form['description']

    picture = request.files['picture']
    if picture is None or picture.filename is None:
        flash("Please select product picture!")
        return render_template('edit.html', product=product)
        
    print("Uploading {}".format(picture.filename))
    # get the name of the picture
    filename = secure_filename(picture.filename)
    # save picture
    picture.save(os.path.join(Config.UPLOADS_FOLDER, filename))

    product.image = filename
    db.session.commit()
    
    flash("{} updated successfully!".format(product.title))
    return redirect(url_for('dashboard'))

@app.route('/add-product', methods=['POST'])
def add_product():
    profile = check_login()
    if profile is None:
        return redirect(url_for('login'))
    # collect form data
    title = request.form['title']
    category = request.form['category']
    price = request.form['price']
    description = request.form['description']
    picture = request.files['picture']
    if picture is None or picture.filename is None:
        flash("Please select product picture!")
        return redirect(url_for('add_product_page'))
    print("Uploading {}".format(picture.filename))
    # get the name of the picture
    filename = secure_filename(picture.filename)

    # save picture
    picture.save(os.path.join(Config.UPLOADS_FOLDER, filename))
    # add form details to database
    product = Product(title=title, category=category, price=price, 
    description=description, image=filename)

    db.session.add(product)
    db.session.commit()
    flash("{} added to product successfully!".format(title))
    return redirect(url_for('dashboard'))


@app.route('/add-new-product')
def add_product_page():
    profile = check_login()
    if profile is None:
        return redirect(url_for('login'))
    
    return render_template('add-product.html')


@app.route('/dashboard')
def dashboard():
    profile = check_login()
    if profile is None:
        return redirect(url_for('login'))

    products = Product.query.all()
    return render_template('dashboard.html', profile=profile, products=products)

@app.route('/')
def homepage():
    profile = check_login()
    return render_template("home.html", profile=profile)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        # send login page
        return render_template('login.html')
    elif request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        # check if email or password is empty
        if email == '' or password == '':
            flash("Please enter email and password.")
            return render_template('login.html')
        #hash password
        p_hash = hashlib.sha256(password.encode()).hexdigest()
        # check if user with email exist
        correct_user = User.query.filter_by(email=email).first()
        if correct_user is None:
            flash("Invalid email or password")
            return render_template('login.html')
        
        if correct_user.password_hash == p_hash:
            # login details are correct
            flash("Logged In!")
            # set session
            session['email'] = email
            session['p_hash'] = p_hash
            # set cookies
            resp = redirect(url_for('homepage'))
            resp.set_cookie('id', str(correct_user.id), max_age=timedelta(hours=24))
            resp.set_cookie('p_hash', p_hash, max_age=timedelta(hours=24))
            return resp
    flash("Invalid login details")    
    return render_template('login.html')


@app.route('/logout')
def log_out():
    # remove sessions
    if 'email' in session:
        session.pop('email')
        session.pop('p_hash')
    # remove cookies
    resp = redirect(url_for('login'))
    resp.set_cookie('id', expires=0)
    resp.set_cookie('p_hash', expires=0)
    return resp

@app.route('/sign-up')
def sign_up():
    return render_template('sign-up.html')

@app.route('/registration', methods=['POST'])
def register():
    email = request.form['email']
    password = request.form['password']
    username = request.form['username']

    if password == '':
        flash("password is required!")
        return redirect(url_for('sign_up'))
    else:
        p_hash = hashlib.sha256(password.encode()).hexdigest()
    
    new_user = User(username=username, password_hash=p_hash, email=email)
    db.session.add(new_user)
    db.session.commit()
    flash("Registered successfully")
    return redirect(url_for('homepage'))


@app.route('/uploads/<filename>')
def view_file(filename):
    return send_from_directory('static/uploads', filename)
