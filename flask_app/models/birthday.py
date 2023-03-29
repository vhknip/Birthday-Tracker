from flask import flash
from flask_bcrypt import Bcrypt
import re


from flask_app import app

from flask_app.config.mysqlconnection import connectToMySQL
from flask_app.models import user


DB = "birthday_tracker"

class Birthday:
    
    def __init__(self, birthday):
        self.id = birthday["id"]
        self.name = birthday["name"]
        self.birthday = birthday["birthday"]
        self.preferences = birthday["preferences"]
        self.created_at = birthday["created_at"]
        self.updated_at = birthday["updated_at"]
        self.user = None


    @classmethod
    def create_valid_birthday(cls, birthday_dict):
        
        if not cls.is_valid(birthday_dict):
            return False
        
        query = "INSERT INTO birthdays (name, birthday, preferences, user_id) VALUES (%(name)s, %(birthday)s, %(preferences)s, %(user_id)s);"
        birthday_id = connectToMySQL(DB).query_db(query, birthday_dict)
        birthday = cls.get_by_id(birthday_id)
        return birthday

    @classmethod
    def get_by_id(cls, birthday_id):
        data = {"id": birthday_id}
        # query to select birthday and user data, join on birthdays_user_id = user.id and match to specified id
        query = "SELECT birthdays.id, name, birthday, preferences, birthdays.created_at, birthdays.updated_at, users.id, first_name, last_name, email, password, users.created_at, users.updated_at FROM birthdays JOIN users on users.id = birthdays.user_id WHERE birthdays.id = %(id)s;"
        result = connectToMySQL(DB).query_db(query,data)
        result = result[0]
        birthday = cls(result)
        
        birthday.user = user.User(
                {
                    "id": result["users.id"],
                    "first_name": result["first_name"],
                    "last_name": result["last_name"],
                    "password": result["password"],
                    "email": result["email"],
                    "created_at": result["created_at"],
                    "updated_at": result["updated_at"]
                }
            )
        return birthday

    @classmethod
    def update_birthday(cls, birthday_dict, session_id):

        # Authenticate User first
        birthday = cls.get_by_id(birthday_dict["id"])
        if birthday.user.id != session_id:
            flash("You can't edit this birthday.")
            return False

        # Validate the input
        if not cls.is_valid(birthday_dict):
            return False
        
        query = "UPDATE birthdays SET name=%(name)s, birthday=%(birthday)s, preferences=%(preferences)s, updated_at = NOW() WHERE id = %(id)s;"
        result = connectToMySQL(DB).query_db(query,birthday_dict)
        birthday = cls.get_by_id(birthday_dict["id"])
        return birthday

    @classmethod
    def get_all(cls):

        query = "SELECT birthdays.id, name, birthday, preferences, birthdays.created_at, birthdays.updated_at, users.id, first_name, last_name, email, password, users.created_at, users.updated_at FROM birthdays JOIN users on users.id = birthdays.user_id;"
        birthday_data = connectToMySQL(DB).query_db(query)
        birthdays = []
        for birthday in birthday_data:
            birthday_obj = cls(birthday)
            birthday_obj.user = user.User(
                {
                    "id": birthday["users.id"],
                    "first_name": birthday["first_name"],
                    "last_name": birthday["last_name"],
                    "password": birthday["password"],
                    "email": birthday["email"],
                    "created_at": birthday["users.created_at"],
                    "updated_at": birthday["users.updated_at"]
                }
            )
            birthdays.append(birthday_obj)


        return birthdays
    
    @classmethod
    def delete_birthday_by_id(cls, birthday_id):

        data = {"id": birthday_id}
        query = "DELETE from birthdays WHERE id = %(id)s;"
        connectToMySQL(DB).query_db(query,data)

        return birthday_id

    @staticmethod
    def is_valid(birthday_dict):
        valid = True
        if len(birthday_dict["name"]) < 2:
            flash("Name must be at least 2 characters")
            valid = False
        if len(birthday_dict["preferences"]) < 5:
            flash("Preferences must be at least 5 characters.")
            valid = False
        if len(birthday_dict["preferences"]) > 50:
            flash("Preferences  too long. Maximum 50 characters.")
            valid = False
        if len(birthday_dict["birthday"]) <= 0:
            flash("Date input is required.")
            valid = False
        return valid