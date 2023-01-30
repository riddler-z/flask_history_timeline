import os
from flask import Flask
from history_timeline import db


def create_app():
	# create and configure the app
	app = Flask(__name__, instance_relative_config=True)
	app.config.from_mapping(
		SECRET_KEY='dev',
		DATABASE=os.path.join(app.instance_path, 'history_timeline.sqlite'),
	)

	# load the instance config, if it exists
	app.config.from_pyfile('config.py', silent=True)

	# ensure the instance folder exists
	try:
		os.makedirs(app.instance_path)
	except OSError:
		pass

	# a simple route that says hello
	@app.route('/hello')
	def hello():
		return 'Hello, World!'

	# initialise database utilities 
	db.init_app(app)

	return app
