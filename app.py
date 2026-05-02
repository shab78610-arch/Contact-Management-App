import re
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from email_validator import validate_email, EmailNotValidError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///contacts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret123'

db = SQLAlchemy(app)


class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)


def is_valid_email(email):
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False


def is_valid_phone(phone):
    pattern = r'^[0-9]{10}$'
    return re.match(pattern, phone)


@app.route('/')
def index():
    contacts = Contact.query.order_by(Contact.id.desc()).all()
    return render_template('index.html', contacts=contacts)


@app.route('/add', methods=['GET', 'POST'])
def add_contact():
    if request.method == 'POST':
        first_name = request.form['first_name'].strip()
        last_name = request.form['last_name'].strip()
        address = request.form['address'].strip()
        email = request.form['email'].strip().lower()
        phone = request.form['phone'].strip()

        if not first_name or not last_name or not address or not email or not phone:
            flash('All fields are required.', 'danger')
            return redirect(url_for('add_contact'))

        if not is_valid_email(email):
            flash('Please enter a valid email address.', 'danger')
            return redirect(url_for('add_contact'))

        if not is_valid_phone(phone):
            flash('Phone number must be exactly 10 digits.', 'danger')
            return redirect(url_for('add_contact'))

        existing_email = Contact.query.filter_by(email=email).first()
        if existing_email:
            flash('Email already exists.', 'danger')
            return redirect(url_for('add_contact'))

        existing_phone = Contact.query.filter_by(phone=phone).first()
        if existing_phone:
            flash('Phone number already exists.', 'danger')
            return redirect(url_for('add_contact'))

        new_contact = Contact(
            first_name=first_name,
            last_name=last_name,
            address=address,
            email=email,
            phone=phone
        )

        db.session.add(new_contact)
        db.session.commit()

        flash('Contact added successfully.', 'success')
        return redirect(url_for('index'))

    return render_template('add_contact.html')


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_contact(id):
    contact = Contact.query.get_or_404(id)

    if request.method == 'POST':
        first_name = request.form['first_name'].strip()
        last_name = request.form['last_name'].strip()
        address = request.form['address'].strip()
        email = request.form['email'].strip().lower()
        phone = request.form['phone'].strip()

        if not first_name or not last_name or not address or not email or not phone:
            flash('All fields are required.', 'danger')
            return redirect(url_for('edit_contact', id=id))

        if not is_valid_email(email):
            flash('Please enter a valid email address.', 'danger')
            return redirect(url_for('edit_contact', id=id))

        if not is_valid_phone(phone):
            flash('Phone number must be exactly 10 digits.', 'danger')
            return redirect(url_for('edit_contact', id=id))

        existing_email = Contact.query.filter(Contact.email == email, Contact.id != id).first()
        if existing_email:
            flash('Another contact with this email already exists.', 'danger')
            return redirect(url_for('edit_contact', id=id))

        existing_phone = Contact.query.filter(Contact.phone == phone, Contact.id != id).first()
        if existing_phone:
            flash('Another contact with this phone number already exists.', 'danger')
            return redirect(url_for('edit_contact', id=id))

        contact.first_name = first_name
        contact.last_name = last_name
        contact.address = address
        contact.email = email
        contact.phone = phone

        db.session.commit()
        flash('Contact updated successfully.', 'success')
        return redirect(url_for('index'))

    return render_template('edit_contact.html', contact=contact)


@app.route('/delete/<int:id>', methods=['POST'])
def delete_contact(id):
    contact = Contact.query.get_or_404(id)
    db.session.delete(contact)
    db.session.commit()
    flash('Contact deleted successfully.', 'success')
    return redirect(url_for('index'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)