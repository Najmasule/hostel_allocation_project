from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("hostel_app", "0005_enforce_single_allocation_per_student"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="allocation",
            name="unique_allocation_per_student",
        ),
    ]
