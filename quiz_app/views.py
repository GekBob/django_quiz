from django import views
from django.contrib import messages
from django.contrib.auth import login, mixins as django_auth_mixins, forms as django_auth_forms
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from quiz_app import models, forms, permissions, services


class RegistrationView(views.View):
	def get(self, request):
		form = django_auth_forms.UserCreationForm(request.POST or None)
		context = {
			'title': 'Registration',
			'form': form
		}
		return render(request, 'registration.html', context)

	def post(self, request):
		form = django_auth_forms.UserCreationForm(request.POST or None)
		if form.is_valid():
			user = form.save()
			login(request, user)
			return redirect('list_of_quizzes')
		context = {
			'title': 'Login',
			'form': form
		}
		return render(request, 'registration.html', context)

	def dispatch(self, request, *args, **kwargs):
		if request.user.is_authenticated:
			return redirect('list_of_quizzes')
		return super().dispatch(request, *args, **kwargs)


class ListOfQuizzesView(django_auth_mixins.LoginRequiredMixin, views.View):
	redirect_field_name = None

	def get(self, request):
		quizzes = models.Quiz.objects.filter(is_draft=False).select_related('author').order_by('-created_at')
		context = {
			'title': 'Public quizzes',
			'quizzes': quizzes
		}
		return render(request, 'list_of_quizzes.html', context)


class QuizCreationView(django_auth_mixins.LoginRequiredMixin, views.View):
	redirect_field_name = None

	def get(self, request):
		form = forms.QuizCreationForm(request.POST or None)
		context = {
			'title': 'Create a quiz',
			'form': form
		}
		return render(request, 'quiz_creation.html', context)

	def post(self, request):
		form = forms.QuizCreationForm(request.POST or None)
		if form.is_valid():
			new_quiz = form.save(user=request.user)
			messages.success(request, 'You have successfully created a quiz!')
			return redirect('edit_a_quiz', pk=new_quiz.id)
		context = {
			'title': 'Create a quiz',
			'form': form
		}
		return render(request, 'quiz_creation.html', context)


class QuizEditingView(
		permissions.RedirectPermissionRequiredPermission,
		django_auth_mixins.PermissionRequiredMixin,
		views.generic.UpdateView
	):
	permission_required = ('quiz.change_quiz', 'quiz.quiz__is_draft')

	model = models.Quiz
	form_class = forms.QuizUpdateForm
	template_name = 'quiz_editing.html'

	def get_success_url(self):
		return self.object.get_absolute_url()

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['quiz'] = self.object
		context['quiz_questions'] = self.get_quiz_questions()
		return context

	def form_valid(self, form):
		form.user = self.request.user
		return super().form_valid(form)

	def get_object(self, queryset=None):
		return get_object_or_404(models.Quiz, pk=self.kwargs.get('pk'))

	def get_quiz_questions(self):
		return models.Question.objects.filter(quiz=self.object).order_by('-id')

	def dispatch(self, request, *args, **kwargs):
		if not self.get_object().is_draft:
			return redirect('list_of_quizzes')
		return super().dispatch(request, *args, **kwargs)


class QuestionAddingView(
		django_auth_mixins.LoginRequiredMixin,
		permissions.RedirectPermissionRequiredPermission,
		views.View
	):
	permission_required = 'quiz.add_question'

	def get(self, request, **kwargs):
		form = forms.QuestionCreationForm(request.POST or None)
		context = {
			'title': 'Add a question',
			'quiz': self.get_quiz(),
			'form': form
		}
		return render(request, 'question_creation.html', context)

	def post(self, request, **kwargs):
		form = forms.QuestionCreationForm(request.POST or None)
		if form.is_valid():
			form.save(quiz=self.get_quiz())
			messages.success(request, 'You have successfully created a question!')
			return redirect('edit_a_quiz', pk=self.get_quiz().id)
		context = {
			'title': 'Add a question',
			'quiz': self.get_quiz(),
			'form': form
		}
		return render(request, 'question_creation.html', context)

	def get_quiz(self):
		return get_object_or_404(models.Quiz, pk=self.kwargs.get('pk'))

	def dispatch(self, request, *args, **kwargs):
		if not self.get_quiz().is_draft:
			return redirect('list_of_quizzes')
		return super().dispatch(request, *args, **kwargs)


class QuestionEditingView(
		django_auth_mixins.LoginRequiredMixin,
		permissions.RedirectPermissionRequiredPermission,
		views.generic.UpdateView
	):
	permission_required = 'quiz.change_question'
	redirect_field_name = None

	model = models.Question
	form_class = forms.QuestionCreationForm
	template_name = 'question_editing.html'

	def get_success_url(self):
		return self.object.quiz.get_absolute_url()

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['title'] = 'Edit a question'
		context['question'] = self.object
		return context

	def form_valid(self, form):
		form.quiz = self.get_object().quiz
		return super().form_valid(form)

	def get_object(self, queryset=None):
		return get_object_or_404(models.Question, pk=self.kwargs.get('pk'))

	def dispatch(self, request, *args, **kwargs):
		if not self.get_object().quiz.is_draft:
			return redirect('list_of_quizzes')
		return super().dispatch(request, *args, **kwargs)


class DeletingQuestionView(
		django_auth_mixins.LoginRequiredMixin,
		permissions.RedirectPermissionRequiredPermission,
		views.generic.DeleteView
	):
	permission_required = 'quiz.delete_question'
	redirect_field_name = None

	model = models.Question
	template_name = 'question_confirm_delete.html'

	def get_success_url(self):
		return self.object.quiz.get_absolute_url()

	def dispatch(self, request, *args, **kwargs):
		if not self.get_object().quiz.is_draft:
			return redirect('list_of_quizzes')
		return super().dispatch(request, *args, **kwargs)


class QuizDetailView(django_auth_mixins.LoginRequiredMixin, views.View):
	def get(self, request, pk):
		quiz = get_object_or_404(models.Quiz, pk=pk)
		context = {
			'quiz': quiz
		}
		return render(request, 'quiz_detail.html', context)


@login_required
def start_quiz(request, pk):
	quiz = get_object_or_404(models.Quiz, pk=pk)
	user_quiz = models.UserQuiz.objects.filter(user=request.user, quiz=quiz)
	quiz_reply_url = reverse('quiz_reply', kwargs={'pk': quiz.id})
	if user_quiz.exists():
		return redirect(quiz_reply_url)
	questions = models.Question.objects.filter(quiz=quiz).order_by('date_of_creation')
	question_id = services.return_the_checked_question_id(
		question_id=str(request.GET.get('question')), questions=questions
	)
	question = questions[question_id]
	user_answer_question = models.UserAnswer.objects.filter(user=request.user, question=question).first()
	form = forms.QuizStartingForm(request.POST or None, question=question, instance=user_answer_question)
	if request.method == 'POST':
		if form.is_valid():
			user_answer = form.save(commit=False)
			user_answer.user = request.user
			user_answer.question = question
			user_answer.save()
			return redirect(quiz_reply_url + f'?question={services.get_next_question(question_id=question_id)}')
	context = {
		'quiz': quiz,
		'question': question,
		'questions': questions,
		'question_id': question_id,
		'quiz_reply_url': quiz_reply_url,
		'form': form
	}
	return render(request, 'start_quiz.html', context)


@login_required
def finish_quiz(request, pk):
	user_correct_answers_list = []
	quiz = get_object_or_404(models.Quiz, pk=pk)
	user_answers = models.UserAnswer.objects.filter(user=request.user, question__quiz=quiz)
	if not user_answers:
		return redirect('list_of_quizzes')
	get_user_quiz, created_user_quiz = models.UserQuiz.objects.prefetch_related(
		'user_questions'
	).get_or_create(user=request.user, quiz=quiz)
	if created_user_quiz:
		user_quiz = models.UserQuiz.objects.get(user=request.user, quiz=quiz)
		user_quiz.user_questions.add(*user_answers)
	else:
		user_quiz = get_user_quiz
	for user_answer in user_quiz.user_questions.all():
		if user_answer.user_answer == user_answer.question.correct_answer:
			user_correct_answers_list.append(user_answer.user_answer)
		user_quiz.correct_answers = len(user_correct_answers_list)
		user_quiz.save()
	return render(request, 'finish_test.html', {'quiz': quiz, 'user_quiz': user_quiz})
