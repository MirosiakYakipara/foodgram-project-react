from django.db import migrations

INITAIL_TAGS = [
    {'color': '#FAFF01FF', 'name': 'Завтрак', 'slug': 'breakfast'},
    {'color': '#80FF7EFF', 'name': 'Обед', 'slug': 'lunch'},
    {'color': '#7071FFFF', 'name': 'Ужин', 'slug': 'dinner'}
]


def add_tags(apps, schema_editor):
    Tag = apps.get_model("recipes", "Tag")
    for tag in INITAIL_TAGS:
        new_tag = Tag(**tag)
        new_tag.save()


def remove_tags(apps, schema_editor):
    Tag = apps.get_model("recipes", "Tag")
    for tag in INITAIL_TAGS:
        Tag.objects.get(slug=tag['slug']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_add_ingredients'),
    ]

    operations = [
        migrations.RunPython(
            add_tags,
            remove_tags
        )
    ]
