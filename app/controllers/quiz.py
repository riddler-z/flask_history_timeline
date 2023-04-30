from datetime import datetime

from flask import Blueprint, request, g, flash, render_template, redirect, url_for, session
from werkzeug.exceptions import abort

from app.database.db import get_db
from app.controllers.auth import login_required


bp = Blueprint('quiz', __name__, url_prefix='/quiz')

@bp.route('/<int:quiz_id>')
def view_quiz(quiz_id):
	db = get_db()
	data = {
		'quiz_id': quiz_id
	}

	data['quiz_data'] = db.execute(
		'SELECT * FROM tabQuiz '
		'LEFT JOIN tabEvent ON tabEvent.event_id = tabQuiz.event_id '
		'WHERE tabQuiz.quiz_id = ?', [quiz_id]
	).fetchone()

	if not data['quiz_data']:
		flash('Cannot find the specified quiz.', 'error')
	else:
		questions = db.execute(
			'SELECT count(*) as total FROM tabQuizQuestion '
			'WHERE quiz_id = ?', [quiz_id]
		).fetchone()

		data['no_of_question'] = questions['total']
		data['results'] = get_quiz_results(quiz_id)

	return render_template('quiz/view_quiz.html', data=data)


@bp.route('/new', methods=['GET', 'POST'])
@login_required
def create_quiz():
	if g.user['role'] != "Teacher":
		abort(403, "Not permitted to view this page.")

	db = get_db()
	if request.method == 'POST':
		event_id = request.form['event_id']
		description = request.form['description']

		error = None

		if not event_id.isnumeric():
			error = 'Event not selected.'

		if not error:
			cursor = db.execute(
				'INSERT INTO tabQuiz (event_id, quiz_description, '
				'created_by_user, creation) VALUES (?, ?, ?, ?)',
				[event_id, description, g.user['user_id'], datetime.now()]
			)

			db.commit()
			flash("Quiz created successfully", 'success')
			return redirect(url_for("quiz.view_quiz", quiz_id=cursor.lastrowid))

		flash(error, 'error')

	data = {
		'event_options': []
	}

	event_data = db.execute(
		'SELECT * FROM tabEvent '
		'WHERE event_id NOT IN (SELECT event_id FROM tabQuiz)'
	).fetchall()

	for row in event_data:
		option_value = '{0}, {1}, {2}'.format(
			row['event_year'], row['event_country'], row['event_title']
		)
		option = (row['event_id'], option_value)
		data['event_options'].append(option)

	return render_template('quiz/new_quiz.html', data=data)


@bp.route('/edit/<int:quiz_id>', methods=['GET', 'POST'])
@login_required
def edit_quiz(quiz_id):
	if g.user['role'] != "Teacher":
		abort(403, "Not permitted to view this page.")

	db = get_db()
	error = None

	if request.method == 'POST':
		description = request.form['description']

		quiz_data = db.execute(
			'SELECT * FROM tabQuiz WHERE quiz_id = ?', [quiz_id]
		).fetchone()

		if description == quiz_data['quiz_description']:
			error = "No changes in the document."

		if not error:
			db.execute(
				'UPDATE tabQuiz SET quiz_description = ?, modified_by_user = ?, '
				'modified = ? WHERE quiz_id = ?',
				[description, g.user['user_id'], datetime.now(), quiz_id]
			)
			db.commit()

			flash("Quiz Updated Successfully.", 'success')
			return redirect(url_for('quiz.view_quiz', quiz_id=quiz_id))

		flash(error, 'error')

	quiz_data = db.execute(
		'SELECT * FROM tabQuiz '
		'LEFT JOIN tabEvent ON tabEvent.event_id = tabQuiz.event_id '
		'WHERE tabQuiz.quiz_id = ?', [quiz_id]
	).fetchone()

	if quiz_data:
		quiz_data = dict(quiz_data)

		quiz_data['quiz_title'] = '{0}, {1}, {2}'.format(
				quiz_data['event_year'], quiz_data['event_country'], quiz_data['event_title']
			)
	else:
		flash("Cannot find the specified quiz.", 'error')

	return render_template('quiz/edit_quiz.html', data=quiz_data)


@bp.route('/delete/<int:quiz_id>', methods=['POST'])
@login_required
def delete_quiz(quiz_id):
	if g.user['role'] != "Teacher":
		abort(403, "Not permitted to view this page.")

	db = get_db()

	event_data = db.execute(
		'SELECT event_id from tabQuiz where quiz_id = ?', [quiz_id]
	).fetchone()
	event_id = event_data['event_id']

	db.execute(
		'DELETE FROM tabQuiz WHERE quiz_id = ?', [quiz_id]
	)
	db.commit()

	flash("Quiz deleted successfully", 'info')
	return redirect(url_for('event.view_event', event_id=event_id))



@bp.route('/<int:quiz_id>/question/list')
@login_required
def list_question(quiz_id):
	db = get_db()

	data = {}

	quiz = db.execute(
		'SELECT * FROM tabQuiz '
		'LEFT JOIN tabEvent ON tabEvent.event_id = tabQuiz.event_id '
		'WHERE quiz_id = ?', [quiz_id]
	).fetchone()

	if quiz:
		data['quiz'] = quiz

		questions = db.execute(
			'SELECT * FROM tabQuizQuestion WHERE quiz_id = ?', [quiz_id]
		).fetchall()
		data['questions'] = []

		for question in questions:
			answers = db.execute(
				'SELECT * FROM tabQuizAnswer WHERE question_id = ?', [question['question_id']]
			).fetchall()
			data['questions'].append((question, answers))

	return render_template('quiz/list_question.html', data=data)


@bp.route('/<int:quiz_id>/question/new', methods=['GET', 'POST'])
@login_required
def create_question(quiz_id):
	if g.user['role'] != "Teacher":
		abort(403, "Not permitted to view this page.")

	db = get_db()
	if request.method == 'POST':
		question = request.form['question']
		answer_opt = request.form['answer']
		option_1 = request.form['option_1']
		option_2 = request.form['option_2']
		option_3 = request.form['option_3']
		option_4 = request.form['option_4']

		answer = request.form[answer_opt]
		opts = [option_1, option_2, option_3, option_4]
		opts = [x for x in opts if x]
		options = []
		for opt in opts:
			options.append((opt, opt == answer))

		error = None

		if not question:
			error = 'Question is required'

		if not (option_1 and option_2):
			error = 'At least 2 Answer options are required'

		if not answer:
			error = 'Answer is required'

		if option_1 == option_2:
			error = 'Answer options cannot be same'

		if not error:
			cursor = db.execute(
				'INSERT INTO tabQuizQuestion (question, quiz_id, '
				'created_by_user, creation) VALUES (?, ?, ?, ?)',
				[question, quiz_id, g.user['user_id'], datetime.now()]
			)

			question_id = cursor.lastrowid

			for opt in options:
				db.execute(
					'INSERT INTO tabQuizAnswer (answer, is_correct, question_id, '
					'created_by_user, creation) VALUES (?, ?, ?, ?, ?)',
					[opt[0], opt[1], question_id, g.user['user_id'], datetime.now()]
				)

			db.commit()
			flash("Question created successfully", 'success')
			return redirect(url_for("quiz.list_question", quiz_id=quiz_id))

		flash(error, 'error')

	event_data = db.execute(
		'SELECT * FROM tabEvent '
		'LEFT JOIN tabQuiz ON tabQuiz.event_id = tabEvent.event_id '
		'WHERE tabQuiz.quiz_id = ?', [quiz_id]
	).fetchone()

	if not event_data:
		flash('Cannot find the specified quiz.', 'error')

	return render_template('quiz/new_question.html', data=event_data)


@bp.route('/<int:quiz_id>/question/<int:question_id>', methods=['POST'])
@login_required
def delete_question(quiz_id, question_id):
	if g.user['role'] != "Teacher":
		abort(403, "Not permitted to view this page.")

	db = get_db()
	db.execute(
		'DELETE FROM tabQuizQuestion WHERE question_id = ?', [question_id]
	)
	db.commit()

	flash("Question deleted successfully", 'info')
	return redirect(url_for('quiz.list_question', quiz_id=quiz_id))


@bp.route('<int:quiz_id>/take', methods=['GET', 'POST'])
@login_required
def take_quiz(quiz_id):
	db = get_db()

	quiz = db.execute(
		'SELECT * FROM tabQuiz WHERE quiz_id = ?', [quiz_id]
	).fetchone()

	if quiz:
		if request.method == 'POST':
			user_answers = {key: value for key, value in request.form.items() if key.startswith('answer_')}

			score = 0
			for answer_id in user_answers.values():
				is_correct = db.execute(
					'SELECT is_correct FROM tabQuizAnswer WHERE answer_id = ?', [answer_id]
				).fetchone()

				if is_correct and is_correct['is_correct']:
					score += 1

			db.execute(
				'INSERT INTO tabQuizResult (score, total, creation, quiz_id, user_id) VALUES (?, ?, ?, ?, ?)',
				[score, len(user_answers), datetime.now(), quiz_id, session.get('user_id')])

			db.commit()

			return redirect(url_for('quiz.result_quiz', quiz_id=quiz['quiz_id'], user_id=session.get('user_id')))

		else:
			questions = db.execute(
				'SELECT * FROM tabQuizQuestion WHERE quiz_id = ?', [quiz_id]
			).fetchall()

			questions_with_answers = []
			for question in questions:
				answers = db.execute(
					'SELECT * FROM tabQuizAnswer WHERE question_id = ?', [question['question_id']]
				).fetchall()

				questions_with_answers.append((question, answers))

			return render_template('quiz/take_quiz.html', quiz=dict(quiz), questions_with_answers=questions_with_answers)
	else:
		return "Quiz not found", 404


# Route to display the quiz results
@bp.route('/results')
@bp.route('/results/quiz_id=<int:quiz_id>')
@bp.route('/results/quiz_id=<int:quiz_id>/user_id=<int:user_id>')
@login_required
def result_quiz(quiz_id=None, user_id=None):
	data = {
		'quiz_id': quiz_id,
		'results': get_quiz_results(quiz_id, user_id)
	}

	return render_template('quiz/result_quiz.html', data=data)


def get_quiz_results(quiz_id=None, user_id=None):
	db = get_db()

	query = (
		'SELECT qr.score, qr.total, qr.creation, u.username, e.event_country, '
		'e.event_year, e.event_title FROM tabQuizResult qr '
		'LEFT JOIN tabUser u on u.user_id = qr.user_id '
		'LEFT JOIN tabQuiz q ON q.quiz_id = qr.quiz_id '
		'LEFT JOIN tabEvent e ON e.event_id = q.event_id '
	)
	params = []

	if quiz_id:
		query += 'WHERE q.quiz_id = ? '
		params.append(quiz_id)

	if g.user['role'] == "Student":
		user_id = g.user['user_id']

	if user_id:
		query += '{} u.user_id = ? '.format('AND' if 'WHERE' in query else 'WHERE')
		params.append(user_id)


	query += 'ORDER BY qr.creation DESC'
	results = db.execute(query, params).fetchall()
	return results
