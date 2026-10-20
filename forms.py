from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, PasswordField, DateField
from wtforms.validators import InputRequired, NumberRange, EqualTo, ValidationError


class SearchForm(FlaskForm):
    title = StringField("Movie Title:", validators=[InputRequired()])
    submit = SubmitField("Search")

class BookingForm(FlaskForm):
    adult_seats = IntegerField("Adult Seats:", validators=[InputRequired(), NumberRange(min=0, max=10)], default=0)
    child_seats = IntegerField("Child Seats (Half Price):", validators=[InputRequired(), NumberRange(min=0, max=10)], default=0)
    submit = SubmitField("Book")
    
    def validate(self, extra_validators=None):  
        if not super().validate(extra_validators=extra_validators):
            return False
            
        if self.adult_seats.data == 0 and self.child_seats.data == 0:
            self.adult_seats.errors.append("Please book at least one seat")
            return False

    
        if self.child_seats.data > 0 and self.adult_seats.data == 0:
            self.child_seats.errors.append("Children cannot book without at least one adult")
            return False
        return True


class RegistrationForm(FlaskForm):
    user_id = StringField("User ID:", validators=[InputRequired()])
    password = PasswordField("Password:", validators=[InputRequired()])
    password2 = PasswordField("Confirm Password:", validators=[InputRequired(), EqualTo("password")])
    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    user_id = StringField("User ID:", validators=[InputRequired()])
    password = PasswordField("Password:", validators=[InputRequired()])
    submit = SubmitField("Login")

class DateFilterForm(FlaskForm):
    show_date = DateField("Select Date:", validators=[InputRequired()])
    submit = SubmitField("Filter")

class AdminLoginForm(FlaskForm):
    admin_id = StringField("Admin ID:", validators=[InputRequired()])
    password = PasswordField("Password:", validators=[InputRequired()])
    submit = SubmitField("Login")


