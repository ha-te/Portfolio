from flask import flash
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms.form import Form
from wtforms import (
    StringField,
    FileField,
    PasswordField,
    SubmitField,
    HiddenField,
    DateField,
    TextAreaField,
    RadioField,
    SelectField
)
from wtforms.validators import(
    DataRequired,
    Email,
    EqualTo
)
from wtforms import ValidationError


from life.models import User, UserConnect


class LoginForm(Form):
    email = StringField(validators=[DataRequired(), Email()])
    password = PasswordField(
        validators=[
            DataRequired(),
            EqualTo(
            'confirm_password', 
            message='パスワードが一致しません'
            )
        ]
    )
    confirm_password = PasswordField(
        validators=[DataRequired()]
    )
    submit = SubmitField('LOGIN NOW')

class RegisterForm(Form):
    email = StringField( validators=[DataRequired(), Email('メールアドレスが誤っています')])
    username = StringField('名前: ', validators=[DataRequired()])
    submit = SubmitField('登録')

    def validate_email(self, field):
        if User.select_user_by_email(field.data):
            raise ValidationError('メールアドレスはすでに登録されています')

class ResetPasswordForm(Form):
    password = PasswordField(
        'パスワード',
        validators=[
            DataRequired(), 
            EqualTo(
                'confirm_password', 
                message='パスワードが一致しません'
            )
        ]
    )
    confirm_password = PasswordField(
        'パスワード確認: ', 
        validators=[DataRequired()]
    )
    submit = SubmitField('パスワードを更新する')
    def validate_password(self, field):
        if len(field.data) < 8:
            raise ValidationError('パスワードは8文字以上です')

class ForgotPasswordForm(Form):
        email = StringField(
            'メール:', 
            validators=[DataRequired(), Email()],
            render_kw={"placeholder":"xxx@xx"}
        )
        submit = SubmitField('パスワード再設定')

        def validate_email(self, field):
            if not User.select_user_by_email(field.data):
                raise ValidationError('そのメールアドレスは存在しません。')

class UserForm(Form):
    email = StringField('メール:', validators=[DataRequired()],render_kw={"placeholder":"xxx@xx"})
    username = StringField('名前: ', validators=[DataRequired()])
    picture_path = FileField('ファイルアップロード')
    submit = SubmitField ('登録情報更新')

    def validate(self):
        if not super(Form, self).validate():
            return False
        user = User.select_user_by_email(self.email.data)
        if user:
            if user.id != int(current_user.get_id()):
                flash('そのメールアドレスは既に登録されています。')
                return False
        return True

class ChangePasswordForm(Form):
    password = PasswordField(
        'パスワード',
        render_kw={"placeholder":"新しいパスワードを入力"},
        validators=[
            DataRequired(), 
            EqualTo(
                'confirm_password', 
                message='パスワードが一致しません'
            )
        ]
    )
    confirm_password = PasswordField(
        'パスワード確認: ', validators=[DataRequired()]
    )
    submit = SubmitField('パスワードの更新')
    def validate_password(self, field):
        if len(field.data) < 8:
            raise ValidationError('パスワードは8文字以上です')

class UserSearchForm(FlaskForm):
    username = StringField(
        '名前: ', 
        validators=[DataRequired()]
    )
    submit = SubmitField('ユーザ検索')

class ConnectForm(FlaskForm):
    connect_condition = HiddenField()
    to_user_id = HiddenField()
    submit = SubmitField()

class MessageForm(FlaskForm):
    to_user_id = HiddenField()
    message = TextAreaField(render_kw={"placeholder":"メッセージを入力"})
    submit = SubmitField('メッセージ送信')

    def validate(self):
        if not super(FlaskForm, self).validate():
            return False
        is_friend = UserConnect.is_friend(self.to_user_id.data)
        if not is_friend:
            return False
        return True

class CreateMemoryForm(Form):
    word = StringField('用語:')
    mean = StringField('意味:')
    submit = SubmitField('記録')

class UpdateMemoryForm(Form):
    id = HiddenField()
    word = StringField('用語:')
    mean = StringField('意味:')
    submit = SubmitField('記録')

class DeleteMemoryForm(Form):
    id = HiddenField()
    submit = SubmitField('削除')

class RecipeForm(FlaskForm):
    title = StringField('レシピ名', validators=[DataRequired()])
    creater = SelectField('料理家', coerce=int, validators=[DataRequired()])
    genre = SelectField('ジャンル',choices=[('和食','和食'),('エスニック','エスニック'),('中華','中華'),('イタリアン','イタリアン'),('フレンチ','フレンチ'),('洋食','洋食'),('アメリカ料理','アメリカ料理'),('スイーツ','スイーツ'),('カフェ','カフェ'),('その他','その他')])
    date = DateField('更新日', format="%Y-%m-%d")
    people = SelectField('人数', choices=[('11','10人以上'),('10','10人'),('9','9人'),('8','8人'),('7','7人'),('6','6人'),('5','5人'),('4','4人'),('3','3人'),('2','2人'),('1','1人')])
    cost = SelectField('費用感', choices=[('5','1000円以上'),('4','800円〜1000円'),('3','600円〜800円'),('2','400円〜600円'),('1','200円〜400円'),('0','200円以下')])
    recommend = SelectField('オススメ度', choices=[('5','5: とても簡単'),('4','4: やや簡単'),('3','3: 普通'),('2','2: 余り難しい'),('1','1: 難しい')])
    comment = TextAreaField('実際どうでした？')
    items = StringField('素材')
    submit = SubmitField('登録')

class CreaterForm(FlaskForm):
    name = StringField('料理家', validators=[DataRequired()])
    extras = StringField('説明')
    submit = SubmitField('登録')

class RecipeUpdateForm(RecipeForm):
    submit = SubmitField('修正')

class CreaterUpdateForm(CreaterForm):
    submit = SubmitField('修正')

class SearchForm(FlaskForm):
    title = StringField('レシピタイトル')
    creater = SelectField('ニックネーム', coerce=int)
    people = SelectField('人数', choices=[('11','10人以上'),('10','10人'),('9','9人'),('8','8人'),('7','7人'),('6','6人'),('5','5人'),('4','4人'),('3','3人'),('2','2人'),('1','1人')])
    cost = SelectField('費用感', choices=[('5','1000円以上'),('4','800円〜1000円'),('3','600円〜800円'),('2','400円〜600円'),('1','200円〜400円'),('0','200円以下')])
    items = StringField('素材')
    submit = SubmitField('検索')