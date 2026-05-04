from __future__ import annotations

from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Gameboard, Leaderboard, LeaderboardEntry, Question

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ('id', 'username')
		read_only_fields = ('id', 'username')


class LeaderboardEntrySerializer(serializers.ModelSerializer):
	user = UserSerializer(read_only=True)

	class Meta:
		model = LeaderboardEntry
		fields = (
			'id',
			'leaderboard',
			'user',
			'score',
			'time_seconds',
			'correct_count',
			'hints_used',
			'submitted_at',
		)
		read_only_fields = ('id',)


class LeaderboardSerializer(serializers.ModelSerializer):
	entries = LeaderboardEntrySerializer(many=True, read_only=True)

	class Meta:
		model = Leaderboard
		fields = ('id', 'gameboard', 'entries')
		read_only_fields = ('id',)


class QuestionSerializer(serializers.ModelSerializer):
	class Meta:
		model = Question
		fields = ('id', 'category', 'value', 'question_text', 'hint', 'howard')
		read_only_fields = fields


class GameboardSerializer(serializers.ModelSerializer):
	questions = QuestionSerializer(many=True, read_only=True)
	leaderboard = LeaderboardSerializer(read_only=True)

	class Meta:
		model = Gameboard
		fields = ('board_code', 'name', 'date_created', 'questions', 'leaderboard')
		read_only_fields = ('board_code', 'name', 'date_created', 'questions')
