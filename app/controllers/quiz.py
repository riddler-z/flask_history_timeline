from datetime import datetime

from flask import Blueprint, request, g, flash, render_template, redirect, url_for
from werkzeug.exceptions import abort

from app.database.db import get_db
from app.controllers.auth import login_required


bp = Blueprint('quiz', __name__, url_prefix='/quiz')

@bp.route('/<int:quiz_id>')
def view_quiz(quiz_id):
	db = get_db()

	quiz_data = db.execute(
		'SELECT * FROM tabQuiz '
		'LEFT JOIN tabEvent ON tabEvent.event_id = tabQuiz.event_id '
		'WHERE tabQuiz.quiz_id = ?', [quiz_id]
	).fetchone()

	if not quiz_data:
		flash('Cannot find the specified quiz.', 'error')

	return render_template('quiz/view_quiz.html', data=quiz_data)


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

	quiz_data = dict(db.execute(
		'SELECT * FROM tabQuiz '
		'LEFT JOIN tabEvent ON tabEvent.event_id = tabQuiz.event_id '
		'WHERE tabQuiz.quiz_id = ?', [quiz_id]
	).fetchone())

	quiz_data['quiz_title'] = '{0}, {1}, {2}'.format(
			quiz_data['event_year'], quiz_data['event_country'], quiz_data['event_title']
		)

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
