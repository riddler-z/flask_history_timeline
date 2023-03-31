from datetime import datetime
from flask import Blueprint, request, session, g, flash, \
	render_template, redirect, url_for
from werkzeug.exceptions import abort
from app.database.db import get_db
from app.controllers.auth import login_required


bp = Blueprint('announcement', __name__, url_prefix='/announcement')

@bp.route('/list')
@login_required
def list_announcement():
	db = get_db()
	announcement_data = db.execute(
		'SELECT ann.announcement_id, ann.announcement_title, ann.announcement_content, '
		'ann.creation, user.username FROM tabAnnouncement ann '
		'LEFT JOIN tabUser user ON user.user_id = ann.created_by_user '
		'ORDER BY ann.creation DESC'
	).fetchall()

	return render_template('announcement/list_announcement.html', data=announcement_data)


@bp.route('/new', methods=['GET', 'POST'])
@login_required
def create_announcement():
	if g.user['role'] != "Teacher":
		abort(403, "Not permitted to view this page.")

	if request.method == 'POST':
		title = request.form['title']
		message = request.form['message']

		db = get_db()
		error = None

		if not (title and message):
			error = 'Please fill all data.'

		if not error:
			db.execute(
				'INSERT INTO tabAnnouncement (announcement_title, announcement_content, '
				'created_by_user, creation) VALUES (?, ?, ?, ?)',
				[title, message, session.get('user_id'), datetime.now()]
			)

			db.commit()
			flash("Announcement created successfully", 'success')
			return redirect(url_for("announcement.list_announcement"))

		flash(error, 'error')

	return render_template('announcement/new_announcement.html')


@bp.route('/delete/<int:announcement_id>', methods=['POST'])
@login_required
def delete_announcement(announcement_id):
	if g.user['role'] != "Teacher":
		abort(403, "Not permitted to view this page.")

	db = get_db()
	db.execute(
		'DELETE FROM tabAnnouncement WHERE announcement_id = ?', [announcement_id]
	)
	db.commit()

	flash("Announcement deleted successfully", 'info')
	return redirect(url_for('announcement.list_announcement'))
