from flask_wtf import FlaskForm as Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length, DataRequired
from wtforms import ValidationError
from ..models import User

class LoginForm(Form):
    username = StringField('用户名', validators=[DataRequired(), Length(1,64)] )
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登陆')

