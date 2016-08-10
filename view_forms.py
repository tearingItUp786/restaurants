from wtforms import Form, TextAreaField, StringField, DecimalField, SelectField, validators, FieldList, FormField, HiddenField, BooleanField


class NewRestaurantForm(Form):
    name = StringField(
        'Name', [validators.required(), validators.length(min=1, max=50)])
    description = TextAreaField(
        'Description', [validators.required(), validators.length(min=1, max=200)])
    entry_id = HiddenField()


class MenuItemForm(NewRestaurantForm):
    price = DecimalField('Price', [validators.required()])
    courses = SelectField('Course', [validators.required()], choices=[('Appetizer', 'Appetizer'), (
        'Entree', 'Entree'), ('Dessert', 'Dessert'), ('Beverage', 'Beverage')])


class UpdateMenuItemsForm(Form):
    items = FieldList(FormField(MenuItemForm))


class DeleteMenuItem(MenuItemForm):
    status = BooleanField('Delete', [validators.required()])


class DeleteMenuItemsForm(Form):
    items = FieldList(FormField(DeleteMenuItem))
