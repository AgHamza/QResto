from flask import Blueprint, render_template, flash, redirect, url_for, request, send_file
from app import db
from app.forms import LoginForm, RegistrationForm, CategoryForm, MenuItemForm
from app.models import User, Category, MenuItem
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
import io
import qrcode

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('main.login'))
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.dashboard')
        return redirect(next_page)
    return render_template('login.html', form=form)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, restaurant_name=form.restaurant_name.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    category_form = CategoryForm()
    item_form = MenuItemForm()

    # Handle adding a new category
    if category_form.validate_on_submit() and 'add_category' in request.form:
        category = Category(name=category_form.name.data, owner=current_user)
        db.session.add(category)
        db.session.commit()
        flash('Category added!')
        return redirect(url_for('main.dashboard'))
    
    # Handle adding a new menu item
    if item_form.validate_on_submit() and 'add_item' in request.form:
        category_id = request.form.get('category_id')
        category = Category.query.filter_by(id=category_id, user_id=current_user.id).first()
        if category:
            item = MenuItem(name=item_form.name.data,
                            description=item_form.description.data,
                            price=item_form.price.data,
                            category=category)
            db.session.add(item)
            db.session.commit()
            flash('Menu item added!')
        else:
            flash('Invalid category selected!')
        return redirect(url_for('main.dashboard'))

    categories = Category.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', category_form=category_form, item_form=item_form, categories=categories)

@bp.route('/menu/<username>')
def menu(username):
    user = User.query.filter_by(username=username).first_or_404()
    categories = Category.query.filter_by(user_id=user.id).all()
    return render_template('menu.html', user=user, categories=categories)

@bp.route('/download_qr')
@login_required
def download_qr():
    # Generate a QR code that points to the user's menu page.
    menu_url = url_for('main.menu', username=current_user.username, _external=True)
    qr_img = qrcode.make(menu_url)
    buf = io.BytesIO()
    qr_img.save(buf, 'PNG')
    buf.seek(0)
    return send_file(buf, mimetype='image/png', as_attachment=True, download_name='menu_qr.png')
