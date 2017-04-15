from flask_wtf import FlaskForm as Form
from wtforms import StringField, TextAreaField, BooleanField, SelectField, SubmitField, FileField
from wtforms.validators import DataRequired, Length
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import ValidationError
from flask_pagedown.fields import PageDownField
from ..models import User
from .. import  photos

class PostForm(Form):
    title = StringField("标题", validators=[DataRequired()])
    thum = StringField("封面")
    abstract = TextAreaField("摘要")
    category = SelectField("栏目", coerce=int)
    body = PageDownField("内容", validators=[DataRequired()])
    submit = SubmitField("提交")

class AddPhotoForm(Form):
    photo = FileField(u'图片', validators=[
        FileRequired(),
        FileAllowed(photos, u'只能上传图片！')
    ])
    submit = SubmitField(u'提交')

class CateForm(Form):
    name = StringField("栏目名", validators=[DataRequired()])
    abstract = TextAreaField("摘要")
    thum = StringField("封面")
    submit = SubmitField(u'提交')

