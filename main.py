from flask import Flask, request, redirect, render_template, url_for, flash, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.fields.datetime import DateField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DB_URI', 'sqlite:///todo.db')
db = SQLAlchemy(app)

class MyForm(FlaskForm):
    task = StringField('task', validators=[DataRequired()])
    date = DateField('date', validators=[DataRequired()])
    category = StringField('category', validators=[DataRequired()])
    submit = SubmitField('Add')

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(200), unique=False, nullable=False)
    category = db.Column(db.String(200), unique=False, nullable=False)
    date = db.Column(db.DateTime, unique=False, nullable=False)
    is_completed = db.Column(db.Boolean, unique=False, nullable=False)

with app.app_context():
    db.create_all()

@app.route("/", methods = ["GET","POST"])
def home():
    form = MyForm()
    todo_list = db.session.execute(db.select(Todo).order_by(Todo.is_completed)).scalars().all()
    if form.validate_on_submit():
        user_input = form.task.data
        if user_input:
            new_todo = Todo(task=form.task.data, category=form.category.data, date=form.date.data, is_completed=False)
            db.session.add(new_todo)
            db.session.commit()
        else:
            flash('Todo entry is empty, try again')
        return redirect(url_for("home"))
    return render_template("home.html", form=form, todo_list=todo_list)

@app.route("/update_task", methods = ["GET","POST"])
def update_task():
    data = request.get_json()
    done_todo_id = data.get("todo_id")
    done_todo = Todo.query.get_or_404(done_todo_id)
    if done_todo.is_completed == 0:
        done_todo.is_completed = 1
    else:
        done_todo.is_completed = 0
    db.session.commit()
    return jsonify({"message": "Task marked as completed", "todo_id": done_todo_id})

@app.route("/delete_task", methods = ["GET","POST"])
def delete_task():
    delete_todo_id = request.args.get("todo_id")
    delete_todo = Todo.query.get_or_404(delete_todo_id)
    db.session.delete(delete_todo)
    db.session.commit()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run()