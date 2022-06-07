from secrets import choice
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SelectField, StringField, PasswordField, IntegerField, FileField, SubmitField, RadioField, DateField
from wtforms.validators import URL, DataRequired, Length

ep_addr = [("불광동", "불광동"), ("대조동", "대조동"), ("갈현동", "갈현동"), ("진관동", "진관동"), ("신사동", "신사동"), ("응암동", "응암동"), ("역촌동", "역촌동"), ("구산동", "구산동"), ("녹번동", "녹번동"), ("수색동", "수색동"), ("증산동", "증산동")]
category_places = [("cafe", "카페"), ("restaurant", "식당"), ("bookstore", "서점"), ("park", "공원") ,("etc", "기타")]

class RegisterForm(FlaskForm):
    name = StringField("이름", validators=[DataRequired()])
    phone = StringField("휴대전화", validators=[DataRequired(), Length(min=11,max=11)])
    password = PasswordField("비밀번호", validators=[DataRequired()])
    bday = DateField("생년월일")
    address = SelectField("간단 주소", validators=[DataRequired()], choices=ep_addr)
    single_house = RadioField("1인 가구 여부", choices=[(1, "1인 가구"), (0, "1인 가구가 아님")])
    submit = SubmitField("등록하기")

class PlaceForm(FlaskForm):
    category = SelectField("카테고리", validators=[DataRequired()], choices=category_places)
    name = StringField("장소명", validators=[DataRequired()])
    location = StringField("위치", validators=[DataRequired()])
    # photo = FileField("이미지") # , validators=[FileRequired(), FileAllowed(["jpg", "png", "jpeg"], "사진 파일만 업로드가 가능해요!")]
    sm_url = StringField("SNS 게시물 주소", validators=[DataRequired(), URL("주소를 제대로 입력하세요!")])
    submit = SubmitField("제출하기")

class LoginForm(FlaskForm):
    phone = StringField("휴대전화", validators=[DataRequired(), Length(min=11,max=11)])
    password = PasswordField("비밀번호", validators=[DataRequired()])
    submit = SubmitField("로그인")