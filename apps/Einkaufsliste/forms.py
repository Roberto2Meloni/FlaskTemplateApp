from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField,  SelectField,  SelectMultipleField
from wtforms.validators import DataRequired
from wtforms.fields import DateField


class CreatNewList(FlaskForm):
    first_day = DateField("Start Tag", format="%Y-%m-%d", validators=[DataRequired()])
    last_day = DateField("End Tag", format="%Y-%m-%d", validators=[DataRequired()])
    no_lunch_on_weekday = BooleanField("Keine Einträge für Mittagessen von Mo-Fr")
    group_name = SelectField('Einkaufsgruppe', validators=[DataRequired()], coerce=int)
    submit = SubmitField("Neue Liste Erstellen")
    cancel = SubmitField("Abbrechen")


class CreatNewGroup(FlaskForm):
    group_name = StringField('Gruppenname', validators=[DataRequired()])
    group_members = SelectMultipleField('Gruppenmitglieder', coerce=int)
    group_public = BooleanField('Gruppe öffentlich')
    group_visible = BooleanField('Gruppe sichtbar')
    submit = SubmitField("Gruppe erstellen")

class ModifyGroup(FlaskForm):
    group_name = StringField('Gruppenname', validators=[DataRequired()])
    group_members = SelectMultipleField('Gruppenmitglieder', coerce=int)
    group_public = BooleanField('Gruppe öffentlich')
    group_visible = BooleanField('Gruppe sichtbar')
    submit = SubmitField("Speichern")