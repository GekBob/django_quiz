from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse

from quiz_app import choices

User = get_user_model()


class Quiz(models.Model):
	author = models.ForeignKey(User, related_name='test_author', on_delete=models.CASCADE, verbose_name='Author')
	name = models.CharField(max_length=255, verbose_name='Quiz name')
	description = models.TextField(verbose_name='Description')
	is_draft = models.BooleanField(blank=True, null=True, verbose_name='Is draft')
	created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created at')

	def __str__(self) -> str:
		return f'{self.id}; {self.name}'

	def get_absolute_url(self):
		return reverse('edit_a_quiz', kwargs={'pk': self.id})


class Question(models.Model):
	quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, verbose_name='Quiz')
	question = models.CharField(max_length=500, verbose_name='Question')
	first_option = models.CharField(max_length=100, verbose_name='First option')
	second_option = models.CharField(max_length=100, verbose_name='Second option')
	third_option = models.CharField(max_length=100, verbose_name='Third option')
	fourth_option = models.CharField(max_length=100, verbose_name='Fourth option')
	date_of_creation = models.DateTimeField(auto_now=True)

	correct_answer = models.CharField(
		max_length=20, choices=choices.CHOICE_OF_OPTIONS, default=first_option, verbose_name='Correct answer'
	)

	def __str__(self) -> str:
		return str(self.id)


class UserAnswer(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='User')
	question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name='Question')
	user_answer = models.CharField(max_length=500, verbose_name='User answer')
	date_of_creation = models.DateTimeField(auto_now=True)

	def __str__(self) -> str:
		return str(self.id)


class UserQuiz(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='User')
	quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, verbose_name='Quiz')
	user_questions = models.ManyToManyField(UserAnswer, verbose_name='User questions')
	correct_answers = models.SmallIntegerField(verbose_name='Correct answers', default=0)

	def __str__(self) -> str:
		return str(self.id)


