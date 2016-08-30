import os
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

# Default Flask configuration

app = Flask(__name__)
app.config.from_object(__name__)
db = SQLAlchemy(app)

import models

app.config.update(dict(
    SECRET_KEY='devkey',
    SQLALCHEMY_DATABASE_URI='sqlite:///'+os.path.join(app.root_path, 'mbmt.db')
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


@app.cli.command('initdb')
def initdb_command():
    db.create_all()


@app.route('/')
def page_index():
    return render_template('index.html')

@app.route("/register")
def page_register():
    return render_template("register.html")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)