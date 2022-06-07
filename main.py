from flask import Flask, render_template, redirect, url_for, flash, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from sqlalchemy import ForeignKey, func
from werkzeug.security import generate_password_hash, check_password_hash
from forms import LoginForm, PlaceForm, RegisterForm
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
from sqlalchemy.orm import relationship
from functools import wraps
from datetime import *

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///greeting.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))




def complete_user_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.pre_requisite:
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function



class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    phone = db.Column(db.Integer, unique=True)
    # bday = db.Column(db.String)
    simple_address = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    is_single = db.Column(db.Integer, nullable=False)
    places = relationship("Place", back_populates="user_name")
    pre_requisite = db.Column(db.Integer)
    package_option = db.Column(db.Integer)

class Place(db.Model):
    __tablename__ = "spot"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey("user.id"))
    user_name = relationship("User", back_populates="places")
    place_name = db.Column(db.String, nullable=False)
    category = db.Column(db.String, nullable=False)
    location = db.Column(db.String, nullable=False)
    # photo = db.Column(db.String, nullable=True)
    sm_url = db.Column(db.String, nullable=False)
    date = db.Column(db.String, nullable=False)

class Package(db.Model):
    __tablename__ = "welcome_package_management"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    stock = db.Column(db.Integer, nullable=False)

db.create_all()

@app.route("/")
def home():
    return render_template("index.html")

# 로그인
@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()

    if request.args.get("forget"):
        print(request.args.get("forget"))
        flash("근데 님 비번 암호화해가지궁,, 저두 몰라여!")

    if form.validate_on_submit():
        phone = form.phone.data
        password = form.password.data

        user = User.query.filter_by(phone=phone).first()
        # HP doesn't exist or password incorrect.
        if not user:
            flash("등록되지 않은 전화번호입니다.")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash('비밀번호가 일치하지 않습니다. 다시 시도해주세요.')
            return redirect(url_for('login', forget=True))
        else:
            login_user(user)
            return redirect(url_for('home'))
    return render_template("login.html", form=form, current_user=current_user)

@app.route("/logout", methods=["GET", "POST"])
def logout():
    logout_user()
    return redirect(url_for("home"))

# 신규 사용자 등록

@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm(
        name = "예) 문부야",
        phone = "- 없이 01012341234"
    )
    if form.validate_on_submit():

        if User.query.filter_by(phone=form.phone.data).first():
            #User already exists
            flash("이미 가입된 전화번호입니다. 로그인 하세요!")
            return redirect(url_for("login"))

        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=10
        )
        new_user = User(
            phone=form.phone.data,
            name=form.name.data,
            password=hash_and_salted_password,
            simple_address = form.address.data,
            is_single=int(form.single_house.data)
        )
    
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        flash("사용자 등록 성공")
        return redirect(url_for("home"))

    # return render_template("user_register.html", form=form)
    return render_template("user_register.html", form=form)


# 장소 등록
@app.route("/register_place", methods=["GET", "POST"])
@login_required
def register_place():
    form = PlaceForm()

    if form.validate_on_submit():
        # photo = form.photo.data
        # # photo_byte = photo_str.encode('utf-8')
        # print(photo)
        # print(type(photo))

        new_place = Place(
            user_name = current_user,
            place_name = form.name.data,
            category = form.category.data,
            location = form.location.data,
            # photo = photo,
            sm_url = form.sm_url.data,
            date = date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_place)
        db.session.commit()

        # if current_user의 place가 2개 이상 => current_user.pre_requisite = 1
        if Place.query.filter_by(user_id=current_user.id).count() >= 2:
            user = User.query.filter_by(id=current_user.id).first()
            user.pre_requisite = True

            db.session.commit()


        return redirect(url_for("register_complete", regi_success=True))
    return render_template("place_register.html", form=form) 


# 내 등록 장소
@app.route("/my_places")
@login_required
def my_places():
    all_places = Place.query.filter_by(user_id=current_user.id).all()
    # 지금은 place table서 user_id 로 필터링 하는 방법을 쓰고 있지만, user -> places로 접근하는 방법은 없을까요?
    satisfying = User.query.filter_by(id=current_user.id).first().pre_requisite
    return render_template("my_places.html", all_places=all_places, satisfying=satisfying)



@app.route("/register_complete")
def register_complete():
    return render_template("complete.html")


# 패키지 선택 페이지
@app.route("/package_options")
@complete_user_only
def select_options():

    return render_template("select_package.html")


@app.route("/map")
def map():
    return render_template("map.html")



if __name__ == "__main__":
    app.run(host="localhost", port=8000, debug=True)