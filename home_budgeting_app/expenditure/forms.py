from datetime import datetime

from flask_wtf import Form
from wtforms import DateTimeField, DecimalField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired


class ExpenditureForm(Form):
    value = DecimalField("Value", places=2, validators=[DataRequired()])
    spent_at = DateTimeField("Spent at", format="%Y-%m-%dT%H:%M", validators=[])
    comment = StringField("Comment")
    category = SelectField("Category", coerce=int, validators=[DataRequired()])
    submit = SubmitField("Save")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.spent_at.data:
            self.spent_at.data = datetime.today().replace(microsecond=0, second=0)
