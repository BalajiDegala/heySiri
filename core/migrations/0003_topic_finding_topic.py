from django.db import migrations, models
import django.db.models.deletion


def assign_general_topic(apps, schema_editor):
    Topic = apps.get_model("core", "Topic")
    Finding = apps.get_model("core", "Finding")

    topic, _ = Topic.objects.get_or_create(
        name="General",
        defaults={
            "overview": "General findings and notes.",
            "created_by": "System",
        },
    )
    Finding.objects.filter(topic__isnull=True).update(topic=topic)


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_sprint_standupupdate_sprintitem_blocker"),
    ]

    operations = [
        migrations.CreateModel(
            name="Topic",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255, unique=True)),
                ("overview", models.TextField(blank=True)),
                ("created_by", models.CharField(blank=True, max_length=100)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["name"],
            },
        ),
        migrations.AddField(
            model_name="finding",
            name="topic",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="findings", to="core.topic"),
        ),
        migrations.RunPython(assign_general_topic, migrations.RunPython.noop),
    ]
