import csv
import locale
import os
import pathlib
import random

from flask_login import (
    login_user, 
    login_required, 
    logout_user,
    current_user
    )
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


from life import db
from life.models import Memory
from life.forms import (
    CreateMemoryForm, 
    UpdateMemoryForm,
    DeleteMemoryForm, 
    )



english = Blueprint('english', __name__, url_prefix='')


@english.route('/english',methods=['GET', 'POST'])
def english_start():
    return render_template('/english/english.html')

@english.route('/lesson',methods=['GET', 'POST'])
def lesson():
    return render_template('/english/lesson.html')

@english.route('/toeic_test', methods=['GET', 'POST'])
def toeic_test():
    p = pathlib.Path('life/static/csv/toeic300(1).csv')
    list = p
    list_data = []
    with open(list, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            list_data.append(row)
    list_num = random.randint(0,len(list_data)-1)
    return render_template(
        '/english/toeic_test.html', 
        list_data=list_data,
        list_num=list_num,
    )


@english.route('/memory_list')
def memory_list():
    memories = Memory.query.all()
    form = DeleteMemoryForm(request.form)
    return render_template('/english/memory_list.html',  memories=memories, form=form)

@english.route('/create_memory', methods=['GET', 'POST'])
def create_memory():
    form = CreateMemoryForm(request.form)
    if request.method == 'POST' and form.validate():
        word = form.word.data
        mean = form.mean.data
        user_id = current_user.get_id() 
        #Transaction
        with db.session.begin(subtransactions=True):
            new_memory = Memory(word=word, mean=mean, user_id=user_id)
            db.session.add(new_memory)
        db.session.commit()
        return redirect(url_for('english.memory_list'))
    
    return render_template('/english/create_memory.html', form=form)

@english.route('/update_memory/<int:memory_id>', methods=['GET', 'POST'])
def update_memory(memory_id):
    form = UpdateMemoryForm(request.form)
    memory = Memory.query.get(memory_id)
    if request.method == 'POST' and form.validate():
        id = form.id.data
        word = form.word.data
        mean = form.mean.data
        #Transaction
        with db.session.begin(subtransactions=True):
            memory = Memory.query.get(id)
            memory.word = word
            memory.mean = mean
        db.session.commit()
        return redirect(url_for('english.memory_list'))
    return render_template('/english/update_memory.html', form=form, memory=memory)
# delete memory list config
@english.route('/delete_memory', methods=['GET', 'POST'])
def delete_memory():
    form = DeleteMemoryForm(request.form)
    if request.method == 'POST' and form.validate():
        #Transaction
        with db.session.begin(subtransactions=True):
            id = form.id.data
            memory = Memory.query.get(id)
            db.session.delete(memory)
        db.session.commit()
        return redirect(url_for('english.memory_list'))
    return redirect(url_for('/english.memory_list'))


@english.route('/add_words', methods=['GET', 'POST'])
def add_words():
    form = CreateMemoryForm(request.form)
    if request.method == 'POST' and form.validate():
        word = form.word.data
        mean = form.mean.data
        user_id = current_user.get_id()
        #Transaction
        with db.session.begin(subtransactions=True):
            new_memory = Memory(word, mean, user_id)
            db.session.add(new_memory)
        db.session.commit()
        return redirect(url_for('english.memory_list'))
    return render_template('/english/create_memory.html', form=form)
