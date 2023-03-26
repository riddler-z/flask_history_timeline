from flask import Blueprint, render_template
from app.database.db import get_db


bp = Blueprint('main', __name__)

@bp.route('/')
def timeline():
	db = get_db()

	events = db.execute("SELECT event_id, event_title, event_year, event_country FROM tabEvent").fetchall()

	events_data = {}

	for row in events:
		year_group = events_data.setdefault(row['event_year'], {})
		country_group = year_group.setdefault(row['event_country'], [])
		country_group.append(dict(row))

	return render_template('main/timeline.html', data=events_data)
