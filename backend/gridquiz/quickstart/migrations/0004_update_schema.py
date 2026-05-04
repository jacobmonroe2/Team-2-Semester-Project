import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quickstart', '0003_gameboard_date_created'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Fix Leaderboard.gameboard related_name: "gameboard" → "leaderboard"
        migrations.AlterField(
            model_name='leaderboard',
            name='gameboard',
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='leaderboard',
                to='quickstart.gameboard',
            ),
        ),
        # Fix LeaderboardEntry.leaderboard related_name: "leaderboard" → "entries"
        migrations.AlterField(
            model_name='leaderboardentry',
            name='leaderboard',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='entries',
                to='quickstart.leaderboard',
            ),
        ),
        # Make LeaderboardEntry.user nullable (no auth required to post scores)
        migrations.AlterField(
            model_name='leaderboardentry',
            name='user',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='leaderboard_entries',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        # Make LeaderboardEntry.time_taken nullable (replaced by time_seconds)
        migrations.AlterField(
            model_name='leaderboardentry',
            name='time_taken',
            field=models.DurationField(blank=True, null=True),
        ),
        # New LeaderboardEntry fields
        migrations.AddField(
            model_name='leaderboardentry',
            name='time_seconds',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='leaderboardentry',
            name='correct_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='leaderboardentry',
            name='hints_used',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='leaderboardentry',
            name='submitted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        # Add hint to Question
        migrations.AddField(
            model_name='question',
            name='hint',
            field=models.CharField(blank=True, default='', max_length=300),
        ),
    ]
