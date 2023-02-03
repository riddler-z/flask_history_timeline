import functools
from datetime import datetime
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from history_timeline.db import get_db


bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
	if request.method == 'POST':
		first_name = request.form['first_name']
		last_name = request.form['last_name']
		full_name = f'{first_name} {last_name}'.strip()
		email = request.form['email']
		password = request.form['password']
		re_password = request.form['re_password']
		user_type = "Teacher" if request.form.get('user_type') else "Student"

		db = get_db()
		error = None

		if not full_name:
			error = 'Name is required.'
		elif not email:
			error = 'Email is required.'
		elif not password:
			error = 'Password is required.'
		elif password != re_password:
			error = 'Password does not match.'

		if not error:
			try:
				db.execute("""
					INSERT INTO tabUser (first_name, last_name, full_name, email, password,
					user_type, creation) VALUES (?, ?, ?, ?, ?, ?, ?)""",
					[first_name, last_name, full_name, email, generate_password_hash(password),
					user_type, datetime.now()]
				)
				db.commit()
			except db.IntegrityError:
				error = f"Email {email} is already registered."
			else:
				flash("Account created successfully")
				return redirect(url_for("auth.login"))

		flash(error)

	return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
	if request.method == 'POST':
		email = request.form['email']
		password = request.form['password']
		db = get_db()
		error = None
		user = db.execute(
			'SELECT * FROM tabUser WHERE email = ?', [email]
		).fetchone()

		if not user:
			error = 'Incorrect email.'
		elif not check_password_hash(user['password'], password):
			error = 'Incorrect password.'

		if not error:
			session.clear()
			session['user_id'] = user['id']
			db.execute('UPDATE tabUser SET last_login = ?', [datetime.now()])
			return redirect(url_for('index'))

		flash(error)

	return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
	user_id = session.get('user_id')

	if not user_id:
		g.user = None
	else:
		g.user = get_db().execute(
			'SELECT * FROM tabUser WHERE id = ?', [user_id]
		).fetchone()


@bp.route('/logout')
def logout():
	session.clear()
	return redirect(url_for('index'))


def login_required(view):
	@functools.wraps(view)
	def wrapped_view(**kwargs):
		if g.user is None:
			return redirect(url_for('auth.login'))

		return view(**kwargs)

	return wrapped_view
