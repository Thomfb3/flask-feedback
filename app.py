"""Example flask app that stores passwords hashed with Bcrypt"""
from flask import Flask, render_template, redirect, session, flash, request
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Feedback
from forms import RegisterForm, LoginForm, FeedbackForm

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///feedback"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "secretkey"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

connect_db(app)
db.create_all()


@app.route("/")
def homepage():
    """Show Profile page"""
    if "username" not in session:
        flash("Please login first!", "alert-danger")
        return redirect('/register')

    session_username = session["username"]
    return redirect(f'/users/{session_username}')
    

#### USER REGISTER and LOGIN

@app.route("/register", methods=['GET', "POST"])
def register():
    """Register a user: produce form and handle form submission."""
    form = RegisterForm()

    if form.validate_on_submit():
        name = form.username.data
        pwd = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        is_admin = form.is_admin.data

        user = User.register(name, pwd, email, first_name, last_name, is_admin)
        db.session.add(user)
        db.session.commit()

        session["username"] = user.username 

        return redirect(f"/users/{session['username']}")
    else:
        return render_template("register.html", form=form)



@app.route("/login", methods=['GET', 'POST'])
def login():
    """Register a user: produce form and handle form submission."""
    form = LoginForm()

    if form.validate_on_submit():
        name = form.username.data
        pwd = form.password.data

        # authenticate will return a user or False
        user = User.authenticate(name, pwd)

        if user: 
            session["username"] = user.username
            return redirect(f"/users/{session['username']}")
        else:
            form.username.errors = ["Bad name/password"]
    
    return render_template("login.html", form=form)



@app.route("/logout")
def logout():
    """Logs user out and redirects to homepage."""
    session.pop("username")
    return redirect("/login")


#### USER VIEWS


@app.route("/users/<username>")
def show_user_page(username):
    """Show user page"""
    if "username" not in session or session["username"] != username:
        flash("Please login first!", "alert-danger")
        return redirect('/login')
            
    user = User.query.get_or_404(username)

    feedback = Feedback.query.filter_by(username=username).all()

    return render_template("user_page.html", user=user, feedback=feedback)



@app.route("/users/<username>/delete", methods=['GET'])
def delete_user(username):
    """Delete User"""
    if "username" not in session:
        flash("Please login first!", "alert-danger")
        return redirect('/login')

    return render_template("delete_user.html")



@app.route("/users/<username>/delete", methods=['POST'])
def delete_user_commit(username):
    delete_user = User.query.get_or_404(username)
    # Delete user from db
    db.session.delete(delete_user)
    db.session.commit()

    session.pop("username")

    flash('User Account Deleted!', 'alert-success')
    return redirect(f"/register")


#### FEEDBACK VIEWS


@app.route("/users/<username>/feedback/add", methods=['GET', 'POST'])
def show_feedback_form(username):
    """Show feedback form"""
    if "username" not in session:
        flash("Please login first!", "alert-danger")
        return redirect('/login')

    form = FeedbackForm()

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        username = username

        feedback = Feedback(title=title, content=content, username=username)
        db.session.add(feedback)
        db.session.commit()

        flash('Feedback Submitted. Thank you!', 'alert-success')
        return redirect(f"/users/{username}")

    return render_template("feedback_form.html", form=form)



@app.route("/feedback/<int:id>/update", methods=['GET', 'POST'])
def update_feedback(id):
    """Show feedback form"""
    if "username" not in session:
        flash("Please login first!", "alert-danger")
        return redirect('/login')

    feedback = Feedback.query.get_or_404(id)

    session_username = session["username"]

    if session["username"] != feedback.username:
        flash('Feedback id error', 'alert-danger')
        return redirect(f"/users/{session_username}")

    form = FeedbackForm(obj=feedback)

    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data
        db.session.commit()

        flash('Feedback Updated. Thank you!', 'alert-success')
        return redirect(f"/users/{feedback.username}")

    return render_template("feedback_form.html", form=form)



@app.route("/feedback/<int:id>/delete")
def delete_feedback(id):
    if "username" not in session:
        flash("Please login first!", "alert-danger")
        return redirect('/login')

    feedback = Feedback.query.get_or_404(id)
    session_username = session["username"]

    if session["username"] != feedback.username:
        flash('Feedback id error', 'alert-danger')
        return redirect(f"/users/{session_username}")

    # Delete user from db
    db.session.delete(feedback)
    db.session.commit()

    flash('Feedback Deleted!', 'alert-warning')
    return redirect(f"/users/{session_username}")


#### ADMIN VIEWS

@app.route("/users/<username>/all_users")
def show_all_users(username):
    """Show feedback form"""
    if "username" not in session:
        flash("Please login first!", "alert-danger")
        return redirect('/login')

    admin = User.query.get_or_404(username)
    session_username = session["username"]

    if session["username"] != username:
        flash("Access Denied!", "alert-danger")
        return redirect(f'/users/{session_username}')
    

    if admin.is_admin != True:
        flash("Access Denied!", "alert-danger")
        return redirect(f'/users/{session_username}')

    users = User.query.all()

    return render_template("all_users.html", users=users)



@app.route("/users/<username>/all_feedback")
def show_all_feedback(username):
    """Show feedback form"""
    if "username" not in session:
        flash("Please login first!", "alert-danger")
        return redirect('/login')

    admin = User.query.get_or_404(username)
    session_username = session["username"]

    if session["username"] != username:
        flash("Access Denied!", "alert-danger")
        return redirect(f'/users/{session_username}')
    

    if admin.is_admin != True:
        flash("Access Denied!", "alert-danger")
        return redirect(f'/users/{session_username}')

    feedbacks = Feedback.query.all()

    return render_template("all_feedback.html", feedbacks=feedbacks)




####404

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404