from datetime import datetime
from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from io import StringIO
import csv
from flask import make_response


app = Flask(__name__)
app.secret_key = 'secretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///payback.db'
db = SQLAlchemy(app)

PASSWORD = 'ranbo'


class POST(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    choice = db.Column(db.String(2), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    detail = db.Column(db.String(30))
    date = db.Column(db.DateTime)


with app.app_context():
    db.create_all()


@app.route('/')
def index():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    password = request.form.get('password')
    if password == PASSWORD:
        session['logged_in'] = True
        return redirect('/contents')
    else:
        return render_template('login.html', error='Invalid password')


@app.route('/contents', methods=['GET', 'POST'])
def contents():
    if session.get('logged_in'):
        if request.method == 'GET':
            posts = POST.query.order_by(POST.date.desc()).all()
            total_price = 0
            for post in posts:
                if post.choice == "返済":
                    post.display_choice = "返済"
                    total_price -= post.price
                else:
                    post.display_choice = "借金"
                    total_price += post.price
            return render_template('contents.html', posts=posts, total_price=total_price)
        else:
            choice = request.form.get('choice')
            price = request.form.get('price')
            date = request.form.get('date')
            date = datetime.strptime(date, '%Y-%m-%d')
            detail = request.form.get('detail')
            new_post = POST(choice=choice, price=price, date=date, detail=detail)

            db.session.add(new_post)
            db.session.commit()

            return redirect('/contents')
    else:
        return redirect('/')


@app.route('/create')
def create():
    if session.get('logged_in'):
        return render_template('create.html')
    else:
        return redirect('/')


@app.route('/delete/<int:id>')
def delete(id):
    post = POST.query.get(id)
    db.session.delete(post)
    db.session.commit()
    return redirect('/contents')


@app.route('/download/<obj>/')
def download(obj):
    if obj == 'posts':
        posts = POST.query.order_by(POST.date.desc()).all()

        # Reorder posts as needed (e.g., ascending order by date)
        posts_sorted = sorted(posts, key=lambda x: x.date)

        # Create a CSV string using StringIO
        csv_output = StringIO()
        csv_writer = csv.writer(csv_output)
        csv_writer.writerow(['choice', 'price', 'date', 'detail'])

        # Write each POST object's data to the CSV
        for post in posts_sorted:
            csv_writer.writerow([post.choice, post.price, post.date, post.detail])

        # Create the response object and set headers for CSV download
        response = make_response(csv_output.getvalue())
        response.headers['Content-Disposition'] = f'attachment; filename={obj}.csv'
        response.headers['Content-Type'] = 'text/csv'

        return response

    return "Invalid request for download"


if __name__ == '__main__':
    app.run(debug=True)
