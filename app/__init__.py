from flask import Flask

def create_app():
	app = Flask(__name__)
	# Only register API blueprints here
	return app
