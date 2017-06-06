from flask import Blueprint, render_template

ui = Blueprint('ui', __name__, url_prefix='/ui')


@ui.route('/')
def home():
    return render_template('home.html')
