from datetime import datetime
from flask import Blueprint, request, session, g, flash, \
	render_template, redirect, url_for
from werkzeug.exceptions import abort
from app.database.db import get_db
from app.controllers.auth import login_required


bp = Blueprint('event', __name__, url_prefix='/event')

@bp.route('/<int:event_id>')
def view_event(event_id):
	db = get_db()

	event_data = db.execute(
		'SELECT * FROM tabEvent WHERE event_id = ?', [event_id]
	).fetchone()

	if not event_data:
		flash('Cannot find the specified event.', 'error')

	return render_template('event/view_event.html', data=event_data)


@bp.route('/group/<int:event_year>')
def view_event_group(event_year):
	db = get_db()

	events = db.execute(
		'SELECT * FROM tabEvent where event_year = ?', [event_year]
	).fetchall()

	events_data = {}

	for row in events:
		year_group = events_data.setdefault(row['event_year'], {})
		country_group = year_group.setdefault(row['event_country'], [])
		country_group.append(dict(row))

	if not events_data:
		flash("No events found for the specified year.", 'error')

	return render_template('event/view_event_group.html', data=events_data)


@bp.route('/new', methods=['GET', 'POST'])
@login_required
def create_event():
	if g.user['role'] != "Teacher":
		abort(403, "Not permitted to view this page.")

	if request.method == 'POST':
		country = request.form['country']
		year = request.form['year']
		title = request.form['title']
		description = request.form['description']

		db = get_db()
		error = None

		if not (country and year and title):
			error = 'Please fill all data.'

		if country not in ["Italy", "Germany"]:
			error = 'Please select a country from list'

		if not error:
			try:
				cursor = db.execute("""INSERT INTO tabEvent (event_country, event_year, event_title,
					event_description, created_by_user, creation) VALUES (?, ?, ?, ?, ?, ?)""",
					[country, year, title, description, session.get('user_id'), datetime.now()])

				event_id = cursor.lastrowid
				db.commit()
			except db.IntegrityError:
				error = f"An event with same details already exist."
			else:
				flash("Event created successfully", 'success')
				return redirect(url_for("event.view_event", event_id=event_id))

		flash(error, 'error')

	return render_template('event/new_event.html')


@bp.route('/edit/<int:event_id>', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
	if g.user['role'] != "Teacher":
		abort(403, "Not permitted to view this page.")

	db = get_db()
	error = None

	if request.method == 'POST':
		description = request.form['description']

		event_description = db.execute("SELECT event_description FROM tabEvent WHERE event_id = ?",
			[event_id]).fetchone()

		if description == event_description[0]:
			error = "No changes in the document."

		print(description)


		if not error:
			db.execute("""UPDATE tabEvent SET event_description = ?, modified_by_user = ?, modified = ?
			 	WHERE event_id = ?""", [description, g.user['user_id'], datetime.now(), event_id])

			db.commit()

			flash("Event Updated Successfully.", 'success')
			return redirect(url_for('event.view_event', event_id=event_id))

		flash(error, 'error')

	event_data = db.execute("SELECT * FROM tabEvent WHERE event_id = ?",
		[event_id]).fetchone()
	return render_template('event/edit_event.html', data=event_data)


@bp.route('/delete/<int:event_id>', methods=['POST'])
@login_required
def delete_event(event_id):
	if g.user['role'] != "Teacher":
		abort(403, "Not permitted to view this page.")

	db = get_db()
	db.execute("DELETE FROM tabEvent WHERE event_id = ?", [event_id])
	db.commit()
	flash("Event deleted successfully", 'success')
	return redirect(url_for('main.timeline'))
