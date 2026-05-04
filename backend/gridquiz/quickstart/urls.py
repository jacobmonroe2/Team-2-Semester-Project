from django.urls import path
from .views import (
	CreateGameboardView,
	GameboardByIdView,
	HistoryView,
	LeaderboardView,
	ValidateAnswerView,
)

urlpatterns = [
	path("game/", CreateGameboardView.as_view(), name="create-new-game"),
	path("game/<int:board_code>/", GameboardByIdView.as_view(), name="gameboard-detail"),
	path("games/<int:board_code>/leaderboard/", LeaderboardView.as_view(), name="game-leaderboard"),
	path("validate/", ValidateAnswerView.as_view(), name="validate-answer"),
	path("history/", HistoryView.as_view(), name="history"),
]
