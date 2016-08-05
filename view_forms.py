from wtforms import Form, TextAreaField, StringField, DecimalField, SelectField, validators


class NewRestaurantForm(Form):
    name = StringField(
        'Name', [validators.required(), validators.length(min=1, max=50)])
    description = TextAreaField(
        'Description', [validators.required(), validators.length(min=1, max=200)])


class MenuItemForm(NewRestaurantForm):
    price = DecimalField('Price', [validators.required()])
    courses = SelectField('Course')
