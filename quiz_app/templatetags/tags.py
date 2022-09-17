from django import template
from django.utils.safestring import mark_safe

from quiz_app import models, services

register = template.Library()


@register.simple_tag()
def get_next_question(quiz_reply_url: str, question_id: int):
	next_question = services.get_next_question(question_id=question_id)
	return mark_safe(
		f'<a href="{quiz_reply_url}?question={next_question}" style="text-decoration: none; color: white;">></a>'
	)


@register.simple_tag()
def get_previous_question(quiz_reply_url: str, question_id: int):
	previous_question = services.get_previous_question(question_id=question_id)
	return mark_safe(
		f'<a href="{quiz_reply_url}?question={previous_question}" style="text-decoration: none; color: white;"><</a>'
	)


@register.simple_tag()
def get_questions_count(question_id: int, questions) -> str:
	return f'{question_id + 1}/{questions.count()}'


@register.filter()
def return_userquiz_or_create_link(quiz, user) -> bool:
	if models.UserQuiz.objects.filter(quiz=quiz, user=user).exists():
		return True
	return False


@register.filter()
def get_choice_value(user_answer, question) -> dict:
	return dict(services.get_choices(question=question)).get(user_answer)


@register.simple_tag(takes_context=True)
def active(context, question_id: int, questions) -> str:
	checked_question_id = services.return_the_checked_question_id(question_id=str(question_id), questions=questions)
	question_id_from_url = services.return_the_checked_question_id(
		question_id=context['request'].GET.get('question'),
		questions=questions
	)
	if question_id_from_url == checked_question_id:
		return 'active'
	return 'disabled'


@register.simple_tag(takes_context=True)
def answered_question(context, question):
	user_answer = models.UserAnswer.objects.filter(user=context['request'].user, question=question)
	if user_answer:
		return mark_safe('<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-check" viewBox="0 0 16 16"><path d="M10.97 4.97a.75.75 0 0 1 1.07 1.05l-3.99 4.99a.75.75 0 0 1-1.08.02L4.324 8.384a.75.75 0 1 1 1.06-1.06l2.094 2.093 3.473-4.425a.267.267 0 0 1 .02-.022z"/></svg>')
	return ''
