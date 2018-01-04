from flask.ext.wtf import Form
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired

class LoginForm(Form):
    #openid = StringField('openid', validators=[DataRequired()])
    #remember_me = BooleanField('remember_me', default=False)
    user_id = StringField('user_id',validators=[DataRequired()])
    Lambda = StringField('Lambda',validators=[DataRequired()])
    delta = StringField('delta',validators=[DataRequired()])
    n = StringField('n',validators=[DataRequired()])
