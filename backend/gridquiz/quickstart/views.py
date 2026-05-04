import re
from datetime import datetime, timezone

from django.contrib.auth import get_user_model
from django.db import transaction
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Gameboard, Leaderboard, LeaderboardEntry, Question
from .serializers import (
	GameboardSerializer,
	LeaderboardEntrySerializer,
	LeaderboardSerializer,
	QuestionSerializer,
)
from .randomBoard import createNewBoard

User = get_user_model()


# ── Answer validation helpers ──────────────────────────────────────────────

def _levenshtein(a, b):
	if a == b: return 0
	if not a: return len(b)
	if not b: return len(a)
	prev = list(range(len(a) + 1))
	for i, cb in enumerate(b, 1):
		curr = [i]
		for j, ca in enumerate(a, 1):
			curr.append(min(prev[j] + 1, curr[j - 1] + 1, prev[j - 1] + (0 if ca == cb else 1)))
		prev = curr
	return prev[len(a)]


def _normalize(s):
	s = s.lower()
	s = re.sub(r"[^a-z0-9\s]", " ", s)
	s = re.sub(r"\b(the|a|an|who is|what is|whats|whos)\b", " ", s)
	return re.sub(r"\s+", " ", s).strip()


def validate_answer(user_answer, correct_answer):
	u = _normalize(user_answer)
	c = _normalize(correct_answer)
	if not u or len(u) < 2:
		return {"correct": False, "reason": "Answer too short"}
	if u == c:
		return {"correct": True, "reason": "Exact match"}
	if c in u and len(u) >= max(len(c) * 0.5, 6):
		return {"correct": True, "reason": "Recognized the key term"}
	if u in c:
		return {"correct": True, "reason": "Recognized the key term"}
	dist = _levenshtein(u, c)
	tolerance = max(2, int(len(c) * 0.2))
	if dist <= tolerance:
		return {"correct": True, "reason": "Close enough — minor typo"}
	c_words = [w for w in c.split() if len(w) > 2]
	u_words = [w for w in u.split() if len(w) > 2]
	if c_words and u_words:
		matched = [
			cw for cw in c_words
			if any(_levenshtein(cw, uw) <= max(1, int(len(cw) * 0.25)) for uw in u_words)
		]
		if len(matched) == len(c_words):
			return {"correct": True, "reason": "All key terms present"}
	return {"correct": False, "reason": "Not a close enough match"}


# ── Views ──────────────────────────────────────────────────────────────────

class CreateGameboardView(APIView):
	"""GET /api/game/ — create a new board with randomised questions."""
	permission_classes = [AllowAny]

	def get(self, request):
		try:
			with transaction.atomic():
				questions = Question.objects.all()
				board_questions = createNewBoard(questions)

				new_gameboard = Gameboard.objects.create(
					name=f"Gameboard:{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
					date_created=datetime.now(),
				)
				for question in board_questions:
					question.gameboards.add(new_gameboard)

				Leaderboard.objects.create(gameboard=new_gameboard)

				return Response(
					GameboardSerializer(new_gameboard).data,
					status=status.HTTP_201_CREATED,
				)
		except Exception as e:
			return Response(
				{"detail": f"Game creation failed: {str(e)}"},
				status=status.HTTP_500_INTERNAL_SERVER_ERROR,
			)


class GameboardByIdView(APIView):
	"""GET /api/game/<board_code>"""
	permission_classes = [AllowAny]

	def get(self, request, board_code):
		gameboard = get_object_or_404(Gameboard, board_code=board_code)
		return Response(GameboardSerializer(gameboard).data)


class LeaderboardView(APIView):
	"""
	GET  /api/games/<board_code>/leaderboard/
	POST /api/games/<board_code>/leaderboard/
	"""
	permission_classes = [AllowAny]

	def get(self, request, board_code):
		gameboard = get_object_or_404(Gameboard, board_code=board_code)
		leaderboard = getattr(gameboard, "leaderboard", None)
		if leaderboard is None:
			leaderboard = Leaderboard.objects.create(gameboard=gameboard)
		return Response(LeaderboardSerializer(leaderboard).data)

	def post(self, request, board_code):
		gameboard = get_object_or_404(Gameboard, board_code=board_code)
		leaderboard = getattr(gameboard, "leaderboard", None)
		if leaderboard is None:
			leaderboard = Leaderboard.objects.create(gameboard=gameboard)

		username = request.data.get("username", "anonymous")
		user, _ = User.objects.get_or_create(username=username)

		entry = LeaderboardEntry.objects.create(
			leaderboard=leaderboard,
			user=user,
			score=request.data.get("score", 0),
			time_seconds=request.data.get("time_seconds", 0),
			correct_count=request.data.get("correct_count", 0),
			hints_used=request.data.get("hints_used", 0),
			submitted_at=datetime.now(tz=timezone.utc),
		)
		return Response(
			LeaderboardEntrySerializer(entry).data,
			status=status.HTTP_201_CREATED,
		)


class ValidateAnswerView(APIView):
	"""POST /api/validate/ — server-side fuzzy answer checking."""
	permission_classes = [AllowAny]

	def post(self, request):
		question_id = request.data.get("question_id")
		user_answer = request.data.get("user_answer", "")

		if not question_id:
			return Response({"detail": "question_id required"}, status=status.HTTP_400_BAD_REQUEST)

		question = get_object_or_404(Question, id=question_id)
		result = validate_answer(user_answer, question.answer_text)
		return Response(result)


class HistoryView(APIView):
	"""GET /api/history/?username=<username>"""
	permission_classes = [AllowAny]

	def get(self, request):
		username = request.query_params.get("username")
		if not username:
			return Response({"detail": "username query param required"}, status=status.HTTP_400_BAD_REQUEST)

		user = get_object_or_404(User, username=username)
		entries = LeaderboardEntry.objects.filter(user=user).order_by("-submitted_at")
		return Response(LeaderboardEntrySerializer(entries, many=True).data)
