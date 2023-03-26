import os
from flask import Flask
from app.database import db
from app.controllers import main, auth, event


def create_app():
	# create and configure the app
	app = Flask(__name__, instance_relative_config=True)
	app.config.from_mapping(
		SECRET_KEY='dev',
		DATABASE=os.path.join(app.instance_path, 'app.sqlite'),
	)

	# ensure the instance folder exists
	try:
		os.makedirs(app.instance_path)
	except OSError:
		pass

	# initialize database utilities
	db.init_app(app)

	# register blueprints
	app.register_blueprint(main.bp)
	app.register_blueprint(auth.bp)
	app.register_blueprint(event.bp)

	app.add_url_rule('/', endpoint='timeline')

	return app
