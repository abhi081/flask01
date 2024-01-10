from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)
login_manager = LoginManager(app)



# User model
class User(UserMixin, db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)


# # User model
# class User(UserMixin, db.Model):
#     __tablename__ = 'Users'
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(100), unique=True, nullable=False)
#     password_hash = db.Column(db.String(100), nullable=False)

#     def set_password(self, password):
#         self.password_hash = generate_password_hash(password)

#     def check_password(self, password):
#         return check_password_hash(self.password_hash, password)

# User loader function
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Item model
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)

# Helper function to calculate total amount
def get_total_amount(items):
    return sum(item.price for item in items)

# Login and Register route
@app.route('/', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']

            user = User.query.filter_by(username=username).first()

            if user:
                # Login existing user
                if user.check_password(password):
                    login_user(user)
                    return redirect(url_for('form'))
                else:
                    return "Incorrect password. Please try again."

            else:
                # Register a new user
                new_user = User(username=username)
                new_user.set_password(password)
                db.session.add(new_user)
                db.session.commit()

                login_user(new_user)
                return redirect(url_for('form'))

        return render_template('login.html')

    except Exception as e:
        return f"An error occurred: {str(e)}"

# Form route
@app.route('/form', methods=['GET', 'POST'])
@login_required
def form():
    try:
        if request.method == 'POST':
            name = request.form['name']
            price = float(request.form['price'])
            item = Item(name=name, price=price, user_id=current_user.id)
            db.session.add(item)
            db.session.commit()
            return redirect(url_for('form'))

        items = Item.query.filter_by(user_id=current_user.id).all()
        return render_template('form.html', items=items, total_amount=get_total_amount(items))

    except Exception as e:
        return f"An error occurred: {str(e)}"

# Summary route
@app.route('/summary')
@login_required
def summary():
    try:
        items = Item.query.filter_by(user_id=current_user.id).all()
        return render_template('summary.html', items=items, total_amount=get_total_amount(items))

    except Exception as e:
        return f"An error occurred: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
