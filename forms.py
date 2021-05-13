from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, FileField, BooleanField
from wtforms.validators import DataRequired, Length, Email, NumberRange
from flask_wtf.file import FileRequired, FileAllowed
from wtforms.fields.html5 import DateField, TimeField, DateTimeLocalField
from flask_uploads import UploadSet, IMAGES
from wtforms.widgets import TextArea

photos = UploadSet("photos", IMAGES)


class LoginForm(FlaskForm):
    username = StringField("Username",
                           validators=[DataRequired()])
    password = PasswordField("Password",
                             validators=[DataRequired()])
    submit = SubmitField("Login")


class NewImage(FlaskForm):
    img = FileField("Upload Image Here", validators=[FileAllowed(photos, "Images only"),
                                                     FileRequired("File Was Empty")])

    submit = SubmitField("Save")


class NewMedrash(FlaskForm):
    parsha = StringField("Parsha", validators=[DataRequired()])

    # enddate = DateField("End Date")

    # endtime = TimeField("End Time")

    file = FileField("Upload File Here")

    submit = SubmitField("Upload")


class NewAnnouncement(FlaskForm):
    content = StringField("Announcement", widget=TextArea(), validators=[DataRequired()])

    enddate = DateField("End Date")

    endtime = TimeField("End Time")

    submit = SubmitField("Save")


class AskAdam(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])

    question = StringField("Question", widget=TextArea(), validators=[DataRequired()])

    submit = SubmitField("Ask Adam")


class Comment(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])

    comment = StringField("Comment", widget=TextArea(), validators=[DataRequired()])

    submit = SubmitField("Send")


class NewTeam(FlaskForm):
    schoolname = StringField("School Name", validators=[DataRequired()])

    sport = SelectField("Sport", choices=[("b", "Basketball"), ("h", "Hockey"), ("s", "Soccer")])

    gender = SelectField("Gender", choices=[("m", "Boys"), ("f", "Girls")])

    league = SelectField("League", choices=[("jv", "JV"), ("varsity", "Varsity")])

    file = FileField("Upload Team Image Logo")

    submit = SubmitField("Submit")


class NewGame(FlaskForm):
    team2 = SelectField("Other Team", coerce=str)

    ishome = BooleanField("Home Game")

    date = DateField("day of the game")

    time = TimeField("When is the game")

    submit = SubmitField("Save")


class Score(FlaskForm):
    team1 = StringField("HANC", validators=[DataRequired()])

    team2 = StringField("Other Team", validators=[DataRequired()])

    submit = SubmitField("Save")


class SearchForm(FlaskForm):
    query = StringField("Search", validators=[DataRequired()])

    submit = SubmitField('Search')
