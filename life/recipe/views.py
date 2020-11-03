from datetime import date
from datetime import datetime
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

from life.models import Recipe, Creater
from life import create_app ,db
from life.forms import RecipeForm, CreaterForm, SearchForm, CreaterUpdateForm, RecipeUpdateForm

recipes = Blueprint('recipes', __name__, url_prefix='')
app = create_app()

@recipes.route('/creaters', methods=['GET'])
def creater():
    creaters = Creater.query.order_by(Creater.name).paginate(page=1, per_page=app.config['ITEMS_PER_PAGE'], error_out=False)
    return render_template('/recipe/creaters.html', creaters=creaters)

@recipes.route('/creaters/index/<int:page_num>', methods=['GET','POST'])
def index_careater_pages(page_num):
    creaters = Creater.query.order_by(Creater.name).paginate(page=page_num, per_page=app.config['ITEMS_PER_PAGE'], error_out=False)
    return render_template('/recipe/creaters.html', creaters=creaters)

@recipes.route('/creaters/register', methods=['GET','POST'])
def creater_register():
    form = CreaterForm()

    if form.validate_on_submit():
        check= Creater.query.filter(Creater.name == form.name.data).first()
        if check:
            errors = '既にこのニックネームは登録されています。他のニックネームを登録してください。'
            return render_template('/recipe/creater_register.html', form=form, errors=errors)

        creater = Creater(name=form.name.data, extras=form.extras.data)
        db.session.add(creater)
        db.session.commit()
        return redirect(url_for('recipes.creater'))
    return render_template('/recipe/creater_register.html', form=form)

@recipes.route('/creaters/<int:id>/update', methods=['GET','POST'])
def creater_update(id):
    creater = Creater.query.get(id)

    form = CreaterUpdateForm()

    if form.validate_on_submit():
        check= Creater.query.filter(Creater.name == form.name.data).first()
        
        creater.name = form.name.data
        creater.extras = form.extras.data
        db.session.commit()

        return redirect(url_for('recipes.creater'))

    elif request.method == 'GET':
        form.name.data = creater.name
        form.extras.data = creater.extras

    return render_template('/recipe/creater_each.html', form=form, id=id)

@recipes.route('/creaters/<int:id>/delete', methods=['GET','POST'])
def creater_delete(id):
    creater = Creater.query.get(id)
    check = Recipe.query.filter(Recipe.creater_id == id).first()
    if check:
        errors = "レシピを先に削除してください。"
        form = CreaterUpdateForm()
        form.name.data = creater.name
        form.extras.data = creater.extras
        return render_template('/recipe/creater_each.html', form=form, id=id, errors=errors)
    db.session.delete(creater)
    db.session.commit()
    return redirect(url_for('recipes.creater'))
    

@recipes.route('/recipe', methods=['GET'])
def recipe():
    recipes = Recipe.query.order_by(Recipe.date.desc()).paginate(page=1, per_page=app.config['ITEMS_PER_PAGE'], error_out=False)
    creaters = db.session.query(Creater).join(Recipe, Recipe.creater_id == Creater.id).all()
    return render_template('/recipe/recipe.html', recipes=recipes, creaters=creaters)

@recipes.route('/recipes/pages/<int:page_num>', methods=['GET','POST'])
def recipe_pages(page_num):

    recipes = Recipe.query.order_by(Recipe.date.desc()).paginate(page=page_num, per_page=app.config['ITEMS_PER_PAGE'], error_out=False)
    creaters = db.session.query(Creater).join(Recipe, Recipe.creater_id == Creater.id).all()
    return render_template('/recipe/recipe.html', recipes=recipes, creaters=creaters)


@recipes.route('/recipes/register', methods=['GET','POST'])
def recipe_register():

    registered_creaters = db.session.query(Creater).order_by('name')
    creaters_list = [(i.id, i.name) for i in registered_creaters]

    form = RecipeForm()
    form.creater.choices = creaters_list

    if form.date.data is None:
        form.date.data = datetime.now()

    if form.validate_on_submit():
        recipe = Recipe(title=form.title.data, genre=form.genre.data, date=form.date.data, cost=form.cost.data, people=form.people.data, recommend=form.recommend.data, comment=form.comment.data, creater_id=form.creater.data)
        db.session.add(recipe)
        db.session.commit()
        return redirect(url_for('recipes.recipe'))
    return render_template('/recipe/recipe_register.html', form=form)

@recipes.route('/recipes/<int:id>/update', methods=['GET','POST'])
def recipe_update(id):
    recipe = Recipe.query.get(id)

    registered_creaters = db.session.query(Creater).order_by('name')
    creaters_list = [(i.id, i.name) for i in registered_creaters]

    form = RecipeUpdateForm()

    form.creater.choices = creaters_list

    if form.validate_on_submit():

        recipe.title = form.title.data
        recipe.genre = form.genre.data
        recipe.date = form.date.data
        recipe.creater_id = form.creater.data
        recipe.people = form.people.data
        recipe.cost = form.cost.data
        recipe.recommended = form.recommended.data
        recipe.comment = form.comment.data
        recipe.items = form.items.data
        db.session.commit()

        return redirect(url_for('recipes.recipe'))

    elif request.method == 'GET':

        form.title.data = recipe.title
        form.creater.data = recipe.creater_id
        form.genre.data = recipe.genre
        form.date.data = recipe.date
        form.people.data = recipe.people
        form.cost.data = recipe.cost
        form.recommended.data = recipe.recommended
        form.comment.data = recipe.comment
        form.items = recipe.items

    return render_template('/recipe/recipe_each.html', form=form, id=id)

@recipes.route('/recipes/<int:id>/delete', methods=['GET','POST'])
def recipe_delete(id):
    recipe = Recipe.query.get(id)
    db.session.delete(recipe)
    db.session.commit()
    return redirect(url_for('recipes.recipe'))

@recipes.route('/searches/', methods=['GET','POST'])
def search():

    registered_creaters = db.session.query(Creater).order_by('name')
    creaters_list = [(0,"")]
    for i in registered_creaters:
        creaters_list.append([i.id, i.name])

    form = SearchForm()
    form.creater.choices = creaters_list

    if form.validate_on_submit():

        if form.creater.data != 0:
            recipes = Recipe.query.filter(Recipe.title.like('%' + form.title.data + '%')).filter(Recipe.creater_id==form.creater.data).filter(Recipe.cost==form.cost.data).filter(Recipe.people==form.people.data)
        else:
            recipes = Recipe.query.filter(Recipe.title.like('%' + form.title.data + '%')).filter(Recipe.cost==form.cost.data).filter(Recipe.people==form.people.data)

        recipes = recipes.order_by(Recipe.date.desc()).paginate(page=1, per_page=app.config['ITEMS_PER_PAGE'], error_out=False)
        creaters = db.session.query(Creater).join(Recipe, Recipe.creater_id == Creater.id).all()

        session['title'] = form.title.data
        session['creater'] = form.creater.data
        session['cost'] = form.cost.data
        session['people'] = form.people.data
        session['items'] = form.items.data

        return render_template('/recipe/search_results.html', recipes=recipes, creaters=creaters)
    return render_template('/recipe/search.html', form=form)

@recipes.route('/searches/<int:page_num>', methods=['GET','POST'])
def search_results(page_num):

    form = SearchForm()

    form.title.data = session.get('title')
    form.creater.data = session.get('creater')

    if form.creater.data != 0:
        recipes = Recipe.query.filter(Recipe.title.like('%' + form.title.data + '%')).filter(Recipe.creater_id==form.creater.data).filter(Recipe.cost==form.cost.data).filter(Book.people==form.people.data)
    else:
        recipes = Recipe.query.filter(Recipe.title.like('%' + form.title.data + '%')).filter(Recipe.cost==form.cost.data).filter(Recipe.people==form.people.data)
    recipes = recipes.order_by(Recipe.date.desc()).paginate(page=page_num, per_page=app.config['ITEMS_PER_PAGE'], error_out=False)
    creaters = db.session.query(Creater).join(Recipe,Recipe.creater_id == Creater.id).all()

    return render_template('/recipe/search_results.html', recipes=recipes, creaters=creaters)
