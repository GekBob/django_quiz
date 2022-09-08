from django.urls import path
from django.contrib.auth import views as django_auth_views

from quiz_app import views

urlpatterns = [
	path('registration/', views.RegistrationView.as_view(), name='registration'),
	path('login/', django_auth_views.LoginView.as_view(
		next_page='/',
		redirect_authenticated_user='/',
		template_name='login.html'
	), name='login'),
	path('logout/', django_auth_views.LogoutView.as_view(
		next_page='/login/'
	), name='logout'),

	path('', views.ListOfQuizzesView.as_view(), name='list_of_quizzes'),

	path('quiz-creation/', views.QuizCreationView.as_view(), name='create_a_quiz'),
	path('quiz/<int:pk>/view', views.QuizDetailView.as_view(), name='quiz_detail'),
	path('quiz/<int:pk>/reply', views.start_quiz, name='quiz_reply'),
	path('quiz/<int:pk>/editing', views.QuizEditingView.as_view(), name='edit_a_quiz'),
	path('quiz/<int:pk>/question-adding', views.QuestionAddingView.as_view(), name='question_adding'),

	path('quiz/<int:pk>/results', views.finish_quiz, name='quiz_results'),

	path('question/<int:pk>/editing', views.QuestionEditingView.as_view(), name='edit_a_question'),
	path('question/<int:pk>/delete', views.DeletingQuestionView.as_view(), name='delete_a_question'),
]
