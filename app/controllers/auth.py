import functools
from datetime import datetime

from flask import Blueprint, request, session, g, flash, redirect, url_for, render_template
from werkzeug.security import check_password_hash, generate_password_hash

from app.database.db import get_db


bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['GET', 'POST'])
def register():
	if request.method == 'POST':
		first_name = request.form['first_name']
		last_name = request.form['last_name']
		full_name = f'{first_name} {last_name}'.strip()
		email = request.form['email']
		password = request.form['password']
		re_password = request.form['re_password']
		role = 'Teacher' if request.form.get('is_teacher') else 'Student'

		error = None

		if not full_name:
			error = "Name is required."
		elif not email:
			error = "Email is required."
		elif not password:
			error = "Password is required."
		elif password != re_password:
			error = "Password does not match."

		if not error:
			db = get_db()
			try:
				cursor = db.execute(
					'INSERT INTO tabUser (username, email, password, role, creation) '
					'VALUES (?, ?, ?, ?, ?)',
					[full_name, email, generate_password_hash(password), role, datetime.now()]
				)

				if role == 'Teacher':
					db.execute(
						'INSERT INTO tabTeacher (user_id, creation) VALUES (?, ?)',
						[cursor.lastrowid, datetime.now()]
					)
				elif role == 'Student':
					db.execute(
						'INSERT INTO tabStudent (user_id, creation) VALUES (?, ?)', 
						[cursor.lastrowid, datetime.now()]
					)

			except db.IntegrityError:
				error = f"Email {email} is already registered."

			else:
				db.commit()
				flash("Account created successfully", 'success')
				return redirect(url_for('auth.login'))

		flash(error, 'error')

	return render_template('auth/register.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		email = request.form['email']
		password = request.form['password']

		error = None

		db = get_db()
		user = db.execute(
			'SELECT * FROM tabUser WHERE email = ?', [email]
		).fetchone()

		if not user:
			error = "Incorrect email."
		elif not check_password_hash(user['password'], password):
			error = "Incorrect password."

		if not error:
			db.execute(
				'UPDATE tabUser SET last_login = ? WHERE user_id = ?',
				[datetime.now(), user['user_id']]
			)
			db.commit()
			session.clear()
			session['user_id'] = user['user_id']
			flash("Logged in successfully", 'info')
			return redirect(url_for('timeline'))

		flash(error, 'error')

	return render_template('auth/login.html')


@bp.route('/logout')
def logout():
	session.clear()
	flash("Logged out successfully", 'info')
	return redirect(url_for('timeline'))


@bp.before_app_request
def load_logged_in_user():
	user_id = session.get('user_id')

	if not user_id:
		g.user = None
	else:
		db = get_db()
		g.user = db.execute(
			'SELECT * FROM tabUser WHERE user_id = ?', [user_id]
		).fetchone()


def login_required(view):
	@functools.wraps(view)
	def wrapped_view(**kwargs):
		if g.user is None:
			flash('Please log in to view this page.', 'info')
			return redirect(url_for('auth.login'))

		return view(**kwargs)

	return wrapped_view
