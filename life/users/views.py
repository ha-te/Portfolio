from datetime import date
from datetime import datetime
import locale
import os
import random
import json
import requests


from flask import (
    Blueprint, 
    abort, 
    request, 
    render_template,
    redirect, 
    url_for, 
    flash, 
    session, 
    jsonify
)
from flask_login import (
    login_user, 
    login_required, 
    logout_user,
    current_user
    )


# original module
from life.models import (
    User, 
    PasswordResetToken,  
    Message, 
    UserConnect,
    )
from life import db
from life.forms import (
    LoginForm, 
    RegisterForm, 
    ResetPasswordForm,
    ForgotPasswordForm, 
    UserForm, 
    ChangePasswordForm, 
    CreateMemoryForm, 
    UpdateMemoryForm, 
    DeleteMemoryForm, 
    ConnectForm, 
    MessageForm, 
    UserSearchForm,
    )
from life.utils.message_format import (
    make_message_format, 
    make_old_message_format,
    )


users = Blueprint('users', __name__, url_prefix='')


@users.route('/start')
def start():
    friends = requested_friends = requesting_friends = None
    connect_form = ConnectForm()
    if current_user.is_authenticated:
        friends = User.select_friends()
        requested_friends = User.select_requested_friends()
        requesting_friends = User.select_requesting_friends()
    return render_template(
        '/user/start.html',
        friends = friends,
        requested_friends = requested_friends,
        requesting_friends = requesting_friends,
        connect_form = connect_form,
        user = user,
        #content = content
    )

@users.route('/logout')
def logout():
    logout_user() # logout
    return redirect(url_for('app.home'))

@users.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User.select_user_by_email(form.email.data)
        if user and user.is_active and user.validate_password(form.password.data):
            login_user(user, remember=True)
            next = request.args.get('next')
            if not next:
                next = url_for('users.start')
            return redirect(next)
        elif not user:
            flash('存在しないユーザです')
        elif not user.is_active:
            flash(
                '無効なユーザです。パスワードを再設定してください'
            )
        elif not user.validate_password(form.password.data):
            flash(
                'メールアドレスとパスワードの組み合わせが誤っています'
            )
    return render_template('/user/login.html', form=form)

@users.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User(
            username = form.username.data,
            email = form.email.data
        )
        #Transaction
        with db.session.begin(subtransactions=True):
            user.create_new_user()
        db.session.commit()
        token = ''
        with db.session.begin(subtransactions=True):
            token = PasswordResetToken.publish_token(user)
        db.session.commit()
        print(
            f'パスワード設定用URL: http://127.0.0.1:5000/reset_password/{token}'
            )
        flash(f'パスワード設定用のURLをお送りしました。ご確認ください:http://127.0.0.1:5000/reset_password/{token}')
        return redirect(url_for('users.forgot_password'))
    return render_template('/user/register.html', form=form)

# if user forgot passward//
@users.route('/reset_password/<uuid:token>', methods=['GET', 'POST'])
def reset_password(token):
    form = ResetPasswordForm(request.form)
    reset_user_id = PasswordResetToken.get_user_id_by_token(token)
    if not reset_user_id:
        abort(500)
    if request.method=='POST' and form.validate():
        password = form.password.data
        user = User.select_user_by_id(reset_user_id)
        #Transaction
        with db.session.begin(subtransactions=True):
            user.save_new_password(password)
            PasswordResetToken.delete_token(token)
        db.session.commit()
        flash('パスワードを更新しました。')
        return redirect(url_for('users.login'))
    return render_template('/user/reset_password.html', form=form)

@users.route('/forgot_password' , methods=['GET', 'POST'])
def forgot_password():
        form = ForgotPasswordForm(request.form)
        if request.method == 'POST' and form.validate():
            email = form.email.data
            user = User.select_user_by_email(email)
            if user:
                #Transaction
                with db.session.begin(subtransactions=True):
                    token = PasswordResetToken.publish_token(user)
                db.session.commit()
                reset_url = f'http://127.0.0.1:5000/reset_password/{token}'
                print(reset_url)
                flash(f'パスワード再登録用のURLを発行しました。{reset_url}')
            else:
                flash('存在しないユーザです。')
        return render_template('/user/forgot_password.html', form=form)

@users.route('/user', methods=['GET', 'POST'])
@login_required
def user():
    form = UserForm(request.form)
    if request.method == 'POST' and form.validate():
        user_id = current_user.get_id()
        user = User.select_user_by_id(user_id)
        # Transaction
        with db.session.begin(subtransactions=True):
            user.username = form.username.data
            user.email = form.email.data
            file = request.files[form.picture_path.name].read()
            if file:
                file_name = user_id + '_' + \
                    str(int(datetime.now().timestamp())) + '.jpg'
                picture_path = 'life/static/user_img/' + file_name
                open(picture_path,'wb').write(file)
                user.picture_path = 'user_img/' + file_name
        db.session.commit()
        flash('ユーザー情報の更新に成功しました')
    return render_template('/user/user.html', form=form)

@users.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User.select_user_by_id(current_user.get_id())
        password = form.password.data
        #Transaction
        with db.session.begin(subtransactions=True):
            user.save_new_password(password)
        db.session.commit()
        flash('パスワードの更新に成功しました')
        return redirect(url_for('users.user'))
    return render_template('/user/change_passwork.html', form=form)


# seach user
@users.route('/user_search', methods=['GET'])
@login_required
def user_search():
    form = UserSearchForm(request.form)
    connect_form = ConnectForm()
    session['url'] = 'users.user_search'
    users = None
    user_name = request.args.get(
        'username', 
        None, 
        type=str
    )
    next_url = prev_url = None
    if user_name:
        page = request.args.get(
            'page',
            1, 
            type=int
        )
        posts = User.search_by_name(
            user_name, 
            page
        )
        next_url = url_for(
            'users.user_search', 
            page=posts.next_num, 
            username=user_name
            ) if posts.has_next else None
        prev_url = url_for(
            'users.user_search', 
            page=posts.prev_num, 
            username=user_name
            ) if posts.has_prev else None
        users = posts.items
        # from_user_id = my ID,　to_user_id = someone ID、when status=1, you apply
        # to_user_id = my ID, from_user_id = someone ID、when status=1、you applyed by someone
        # status = 2 is already friend
    return render_template(
        '/user/user_search.html', 
        form=form, 
        connect_form=connect_form,
        users=users, 
        next_url=next_url, 
        prev_url=prev_url,
    )

# to be friend for serched user
@users.route('/connect_user', methods=['POST'])
@login_required
def connect_user():
    form = ConnectForm(request.form)
    if request.method == 'POST' and form.validate():
        if form.connect_condition.data == 'connect':
            new_connect = UserConnect(current_user.get_id(), form.to_user_id.data)
            with db.session.begin(subtransactions=True):
                new_connect.create_new_connect()
            db.session.commit()
        elif form.connect_condition.data == 'accept':
            connect = UserConnect.select_by_from_user_id(form.to_user_id.data)
            # get UserConnect to someone from me
            if connect:
                with db.session.begin(subtransactions=True):
                    connect.update_status() # status 1 => 2
                db.session.commit()
    next_url = session.pop('url', 'users:start')
    return redirect(url_for(next_url))

# keep in touch with users
@users.route('/message/<id>', methods=['GET', 'POST'])
@login_required
def message(id):
    if not UserConnect.is_friend(id):
        return redirect(url_for('users.start'))
    form = MessageForm(request.form)
    # get message memory
    messages = Message.get_friend_messages(current_user.get_id(), id)
    user = User.select_user_by_id(id)
    # read message yet but will read message someday
    read_message_ids = [message.id for message in messages if (not message.is_read) and (message.from_user_id == int(id))]
    # already read and check my unread message 
    not_checked_message_ids = [message.id for message in messages if message.is_read and (not message.is_checked) and (message.from_user_id == int(current_user.get_id()))]
    if not_checked_message_ids:
        with db.session.begin(subtransactions=True):
            Message.update_is_checked_by_ids(not_checked_message_ids)
        db.session.commit()
    # change read_message_ids of is_read to True
    if read_message_ids:
        with db.session.begin(subtransactions=True):
            Message.update_is_read_by_ids(read_message_ids)
        db.session.commit()
    if request.method == 'POST' and form.validate():
        new_message = Message(current_user.get_id(), id, form.message.data)
        with db.session.begin(subtransactions=True):
            new_message.create_message()
        db.session.commit()
        return redirect(url_for('users.message', id=id))
    return render_template(
        '/user/message.html', 
        form = form,
        messages = messages, 
        to_user_id = id,
        user = user
    )

@users.route('/message_ajax', methods=['GET'])
@login_required
def message_ajax():
    user_id = request.args.get(
        'user_id', 
        -1, 
        type=int
    )
    # get message from unreaded person
    user = User.select_user_by_id(user_id)
    not_read_messages = Message.select_not_read_messages(user_id, current_user.get_id())
    not_read_message_ids = [message.id for message in not_read_messages]
    if not_read_message_ids:
        with db.session.begin(subtransactions=True):
            Message.update_is_read_by_ids(not_read_message_ids)
        db.session.commit()
    # get unchecking my message which someone read message
    not_checked_messages = Message.select_not_checked_messages(current_user.get_id(), user_id)
    not_checked_message_ids = [not_checked_message.id for not_checked_message in not_checked_messages]
    if not_checked_message_ids:
        with db.session.begin(subtransactions=True):
            Message.update_is_checked_by_ids(not_checked_message_ids)
        db.session.commit()
    return jsonify(
        data=make_message_format(user, not_read_messages), 
        checked_message_ids = not_checked_message_ids
    )

@users.route('/load_old_messages', methods=['GET'])
@login_required
def load_old_messages():
    user_id = request.args.get(
        'user_id', 
        -1, 
        type=int
    )
    offset_value = request.args.get(
        'offset_value', 
        -1, 
        type=int
    )
    if user_id == -1 or offset_value == -1:
        return
    messages = Message.get_friend_messages(current_user.get_id(), user_id, offset_value * 100)
    user = User.select_user_by_id(user_id)
    return jsonify(data=make_old_message_format(user, messages))
