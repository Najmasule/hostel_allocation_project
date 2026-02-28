from django.db import migrations, models


def dedupe_allocations(apps, schema_editor):
    Allocation = apps.get_model("hostel_app", "Allocation")

    student_ids = (
        Allocation.objects.values_list("student_id", flat=True)
        .order_by()
        .distinct()
    )

    for student_id in student_ids:
        rows = list(
            Allocation.objects.filter(student_id=student_id)
            .order_by("-allocated_on", "-id")
            .values_list("id", flat=True)
        )
        if len(rows) > 1:
            Allocation.objects.filter(id__in=rows[1:]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("hostel_app", "0004_activitylog"),
    ]

    operations = [
        migrations.RunPython(dedupe_allocations, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name="allocation",
            constraint=models.UniqueConstraint(
                fields=("student",),
                name="unique_allocation_per_student",
            ),
        ),
    ]
