import json
from django.db import migrations


def add_ingredients(apps, schema_editor):
    file = r'D:\projects\foodgram-project-react\data\ingredients.json'
    Ingredient = apps.get_model("recipes", "Ingredient")
    with open(file, encoding='utf-8') as json_file:
        data = json.load(json_file)
        for ing in data:
            new_ing = Ingredient(**ing)
            new_ing.save()


def remove_ingredients(apps, schema_editor):
    Ingredient = apps.get_model("recipes", "Ingredient")
    Ingredient.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            add_ingredients,
            remove_ingredients
        )
    ]
