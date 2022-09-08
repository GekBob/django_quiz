from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from quiz_app import models, choices, services


class QuizCreationForm(forms.ModelForm):
	name = forms.CharField(widget=forms.TextInput())
	description = forms.CharField(required=False, widget=forms.Textarea())

	class Meta:
		model = models.Quiz
		fields = ['id', 'name', 'description']

	def save(self, commit=True, user=None):
		quiz = super().save(commit=False)
		if commit and user:
			quiz.author = user
			quiz.is_draft = True
		quiz.save()
		self.save_m2m()
		return quiz


class QuizUpdateForm(QuizCreationForm):
	is_draft = forms.BooleanField(
		required=False,
		help_text=mark_safe(
			_('<small style="color: #d3d3d1;">If you uncheck the box, you will not be able to change the quiz and it will be published.</small>')
		))

	class Meta:
		model = models.Quiz
		fields = ['id', 'name', 'description', 'is_draft']


class QuestionCreationForm(forms.ModelForm):
	question = forms.CharField(widget=forms.TextInput())
	first_option = forms.CharField(widget=forms.TextInput())
	second_option = forms.CharField(widget=forms.TextInput())
	third_option = forms.CharField(widget=forms.TextInput())
	fourth_option = forms.CharField(widget=forms.TextInput())
	correct_answer = forms.ChoiceField(choices=choices.CHOICE_OF_OPTIONS, widget=forms.Select())

	class Meta:
		model = models.Question
		fields = [
			'id', 'question', 'first_option', 'second_option', 'third_option', 'fourth_option', 'correct_answer'
		]

	def save(self, commit=True, quiz=None):
		question = super().save(commit=False)
		if commit and quiz:
			question.quiz = quiz
		question.save()
		return question


class QuizStartingForm(forms.ModelForm):
	user_answer = forms.ChoiceField(label='', widget=forms.RadioSelect)

	class Meta:
		model = models.UserAnswer
		fields = ['id', 'user_answer']

	def __init__(self, *args, **kwargs):
		question = kwargs.pop("question")
		super().__init__(*args, **kwargs)
		if question:
			self.fields['user_answer'].choices = services.get_choices(question=question)
