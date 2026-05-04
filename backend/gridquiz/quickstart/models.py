from __future__ import annotations

import uuid
from django.conf import settings
from django.db import models
import datetime


class Gameboard(models.Model):
	board_code = models.AutoField(primary_key=True, editable=False)
	name = models.CharField(max_length=200)
	date_created = models.DateTimeField(default=datetime.datetime.min)


class Leaderboard(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	gameboard = models.OneToOneField(
		Gameboard,
		on_delete=models.CASCADE,
		related_name='leaderboard',
	)


class LeaderboardEntry(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	leaderboard = models.ForeignKey(
		Leaderboard,
		on_delete=models.CASCADE,
		related_name='entries',
	)
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		related_name='leaderboard_entries',
		null=True,
		blank=True,
	)
	score = models.IntegerField()
	time_taken = models.DurationField(null=True, blank=True)
	time_seconds = models.IntegerField(default=0)
	correct_count = models.IntegerField(default=0)
	hints_used = models.IntegerField(default=0)
	submitted_at = models.DateTimeField(null=True, blank=True)


class Question(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	category = models.CharField(max_length=20)
	value = models.PositiveIntegerField()
	question_text = models.CharField(max_length=500)
	answer_text = models.CharField(max_length=100)
	hint = models.CharField(max_length=300, blank=True, default='')
	howard = models.BooleanField(default=False)
	gameboards = models.ManyToManyField(
		Gameboard,
		related_name='questions',
	)


# Kept for migration compatibility — not used by application logic
class User(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	username = models.CharField(max_length=30)
