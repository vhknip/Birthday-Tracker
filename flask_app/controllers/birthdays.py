from flask import Flask, render_template, session, redirect, request, flash

from flask_app import app

from flask_app.models.user import User
from flask_app.models.birthday import Birthday


@app.route("/dashboard")
def birthdays_home():
    if "user_id" not in session:
        flash("You must be logged in to access the dashboard.")
        return redirect("/")
    
    user = User.get_by_id(session["user_id"])
    birthdays = Birthday.get_all()

    return render_template("dashboard.html", user=user, birthdays=birthdays)


@app.route("/show/<int:birthday_id>")
def birthday_detail(birthday_id):
    user = User.get_by_id(session["user_id"])
    birthday = Birthday.get_by_id(birthday_id)
    return render_template("birthday_detail.html", user=user, birthday=birthday)


@app.route("/new/birthday")
def birthday_create_page():
    user = User.get_by_id(session["user_id"])
    return render_template("create_birthday.html", user=user)

#birthday creation requests and validation
@app.route("/birthdays", methods=["POST"])
def create_birthday():
    valid_birthday = Birthday.create_valid_birthday(request.form)
    if valid_birthday:
        return redirect(f'/show/{valid_birthday.id}')
    return redirect('/new/birthday')


### birthday EDIT PORTION ###

#birthday edit page display
@app.route("/edit/<int:birthday_id>")
def birthday_edit_page(birthday_id):
    birthday = Birthday.get_by_id(birthday_id)
    user = User.get_by_id(session["user_id"])
    return render_template("edit_birthday.html", birthday=birthday, user=user)

#birthday edit requests and validation
@app.route("/birthday/edit/<int:birthday_id>", methods=["POST"])
def update_birthday(birthday_id):

    valid_birthday = Birthday.update_birthday(request.form, session["user_id"])

    if not valid_birthday:
        return redirect(f"/edit/{birthday_id}")
        
    return redirect(f"/show/{birthday_id}")


# birthday delete
@app.route("/birthday/delete/<int:birthday_id>")
def delete_birthday_by_id(birthday_id):
    Birthday.delete_birthday_by_id(birthday_id)
    return redirect("/user/account")


#display page with all birthdays associated with logged in account
@app.route("/user/account")
def account_home():
    #ensures id associated with session and signed in
    if "user_id" not in session:
        flash("You must be logged in to access the dashboard.")
        return redirect("/")
    
    user = User.get_by_id(session["user_id"])
    birthdays = Birthday.get_all()

    return render_template("user_birthdays.html", user=user, birthdays=birthdays)