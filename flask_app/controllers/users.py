from flask import Flask, render_template, session, redirect, request, flash

from flask_app import app

from flask_app.models.user import User


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["POST"])
def register():
    valid_user = User.create_valid_user(request.form)
    if valid_user == False:
        return redirect("/")
    
    session["user_id"] = valid_user.id
    return redirect("/dashboard")

@app.route("/login", methods=["POST"])
def login():
    valid_user = User.authenticated_user_by_input(request.form)
    if valid_user == False:
        return redirect("/")

    session["user_id"] = valid_user.id
    return redirect("/dashboard")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

