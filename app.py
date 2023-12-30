from datetime import datetime
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///payback.db'
db = SQLAlchemy(app)


class POST(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    choice = db.Column(db.Boolean)
    detail = db.Column(db.String(30))
    date = db.Column(db.DateTime, nullable=False)


with app.app_context():
    db.create_all()


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        posts = POST.query.all()
        for post in posts:
            if post.choice:
                post.display_choice = "返済"
            else:
                post.display_choice = "借金"
        return render_template('index.html', posts=posts)
    else:
        choice = request.form.get('choice')
        if choice == "返済":
            choice_value = True
        else:
            choice_value = False
        detail = request.form.get('detail')
        date = request.form.get('date')
        date = datetime.strptime(date, '%Y-%m-%d')
        new_post = POST(choice=choice_value, detail=detail, date=date)

        db.session.add(new_post)
        db.session.commit()

        return redirect('/')


@app.route('/create')
def create():
    return render_template('create.html')


if __name__ == '__main__':
    app.run(debug=True)
