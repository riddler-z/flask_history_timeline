import os
from flask import Flask


def create_app():
	# create and configure the app
	app = Flask(__name__, instance_relative_config=True)
	app.config.from_mapping(
		SECRET_KEY='dev',
		DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
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

	return app
