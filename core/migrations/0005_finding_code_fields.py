from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0004_findingcomment"),
    ]

    operations = [
        migrations.AddField(
            model_name="finding",
            name="code_language",
            field=models.CharField(blank=True, max_length=80),
        ),
        migrations.AddField(
            model_name="finding",
            name="code_snippet",
            field=models.TextField(blank=True),
        ),
    ]
