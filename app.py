from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from send_mail import send_mail
from datetime import datetime
import json
import os
# import math

with open('config.json', 'r') as c:
    params = json.load(c)["params"]

local_server = True
app = Flask(__name__)
app.secret_key = 'super-secret-key'
app.config['UPLOAD_FOLDER'] = params['upload_location']


# ENV = 'dev'

if (local_server):
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Contacts(db.Model):
    __tablename__ = 'contacts'
    # sno, name, email, phone, message

    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(25), nullable=False)
    phone = db.Column(db.String(12), nullable=False)
    message = db.Column(db.String(120), nullable=False)

    def __init__(self, name, email, phone, message):
        self.name = name
        self.email = email
        self.phone = phone
        self.message = message


class Posts(db.Model):
    __tablename__ = 'posts'
    # sno, title, tagline, slug, content, posted_by, date, img_file

    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    tagline = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(25), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    # posted_by = db.Column(db.String(25), nullable=False)
    # date = db.Column(db.String(12), nullable=True)
    img_file = db.Column(db.String(25), nullable=True)

    def __init__(self, title, tagline, slug, content, img_file):
        self.title = title
        self.tagline = tagline
        self.slug = slug
        self.content = content
        self.img_file = img_file


@app.route("/")

def home():
    posts = Posts.query.filter_by().all()
    # last = math.ceil(len(self.posts)/int(params['no_of_posts']))

    # post=posts[]
    page=(request.args.get('page'))
    if(not str(page).isnumeric()):
        page = 1
    page=int(page)

    posts = posts[(page-1)*int(params['no_of_posts']): (page-1)*int(params['no_of_posts']) + int(params['no_of_posts'])]
    # Pagination Logic
    # First --
    if(page==1):
        prev = "#"
        next = "/?page=" + str(page+1)
    # middle -- prev = page - 1, next = page +1
    # last -- prev = page - 1, next = #
    # elif(page==last):
    #     prev="/?page=" + str(page-1)
    #     next="#"
    else:
        prev="/?page=" + str(page-1)
        next="/?page=" + str(page+1)

    return render_template('index.html', params=params, posts=posts, prev=prev, next=next)

@app.route("/about")
def about():
    return render_template('about.html', params=params)

@app.route("/post/<string:post_slug>", methods= ['GET'])
def post(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    return render_template('post.html', params=params, post=post)

@app.route("/dashboard", methods=['GET','POST'])
def dashboard():
    # this line explains whether user is signed in or not
    if ('user' in session and session['user'] == params['admin_user']):
        posts = Posts.query.all()
        return render_template('dashboard.html', params=params, posts=posts)

    if request.method=='POST':
       username = request.form.get('uname')
       userpass = request.form.get('pass')
       if(username == params['admin_user'] and userpass == params['admin_password']):
            # set the session variable
            session['user'] = username
            posts=Posts.query.all()
            return render_template('dashboard.html', params=params, posts=posts)

    return render_template('signin.html', params=params)

@app.route("/signout")
def signout():
    session.pop('user')
    return redirect('/dashboard')

@app.route("/delete/<string:sno>", methods = ['GET','POST'])
def delete(sno):
    if ('user' in session and session['user'] == params['admin_user']):
        post = Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect('/dashboard')


@app.route("/uploader", methods=['GET','POST'])
def uploader():
    if ('user' in session and session['user'] == params['admin_user']):
        if (request.method == 'POST'):
            f= request.files['file1']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename) ))
            return "Uploaded Successfully"



@app.route("/edit/<string:sno>", methods = ['GET','POST'])
def edit(sno):
    if ('user' in session and session['user'] == params['admin_user']):
        if request.method == 'POST':
            # sno, title, tagline, slug, content, img_file, posted_by, date
            title = request.form.get('title')
            tagline = request.form.get('tagline')
            slug = request.form.get('slug')
            content = request.form.get('content')
            img_file = request.form.get('img_file')
            # date = datetime.now()

            if(sno == '0'):
                post = Posts(title=title, tagline=tagline, slug=slug, content=content, img_file=img_file)
                db.session.add(post)
                db.session.commit()
            else:
                post = Posts.query.filter_by(sno=sno).first()
                post.title= title
                post.tagline=tagline
                post.slug=slug
                post.content= content
                post.img_file=img_file
                # post.date=date
                db.session.commit()
                return redirect('/edit/'+sno)

        post = Posts.query.filter_by(sno=sno).first()
        return render_template('edit.html', params=params, post=post, sno=sno)


@app.route("/contact", methods = ["GET","POST"])
def contact():
    if(request.method == "POST"):

        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        message = request.form.get("message")

        entry = Contacts(name=name, email=email, phone=phone, message=message)
        db.session.add(entry)
        db.session.commit()
        send_mail(name, email, phone, message)
        
    return render_template('contact.html', params=params)

if __name__ == "__main__":
    app.run()

