from wtforms import Form, TextAreaField, StringField, DecimalField, SelectField, validators, FieldList, FormField


class NewRestaurantForm(Form):
    name = StringField(
        'Name', [validators.required(), validators.length(min=1, max=50)])
    description = TextAreaField(
        'Description', [validators.required(), validators.length(min=1, max=200)])


class MenuItemForm(NewRestaurantForm):
    price = DecimalField('Price', [validators.required()])
    courses = SelectField('Course', [validators.required()], choices=[('Appetizer', 'Appetizer'), (
        'Entree', 'Entree'), ('Dessert', 'Dessert'), ('Beverage', 'Beverage')])


class UpdateMenuItemsForm(Form):
    items = FieldList(FormField(MenuItemForm))
