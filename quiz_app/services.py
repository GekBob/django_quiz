def get_choices(question) -> tuple:
	return (
		('first_option', question.first_option),
		('second_option', question.second_option),
		('third_option', question.third_option),
		('fourth_option', question.fourth_option),
	)


def return_the_checked_question_id(question_id: str, questions) -> int:
	if question_id and question_id.isdigit():
		question_id = int(question_id)
	else:
		question_id = 0
	question_last_object_index = len(questions) - 1
	if question_id > question_last_object_index:
		question_id = question_last_object_index
	return question_id


def get_next_question(question_id: int) -> int:
	return question_id + 1


def get_previous_question(question_id: int) -> int:
	return question_id - 1
