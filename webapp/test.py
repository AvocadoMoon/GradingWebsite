from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

class TestForm(FlaskForm):
    section = StringField('Section', validators=[DataRequired()])
    team = StringField('Team', validators=[DataRequired()])
    question = StringField('Question', validators=[DataRequired()])
    answer = StringField('Answer', validators=[DataRequired()])
    submit = SubmitField('Test it!')
