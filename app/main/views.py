from flask import render_template, redirect, url_for, abort, flash, request,\
    current_app, send_from_directory, g
from flask_login import login_required, current_user
from . import main
from .forms import PostForm, AddPhotoForm, CateForm
from .. import db
from ..models import Post, Photo, Category
from .photos import save_image
import os
from datetime import datetime


@main.before_app_request
def before_request_defination():
    g.latest_posts = Post.query.order_by(Post.timestamp.desc()).all()[0:10]
    g.latest_categories = Category.query.order_by(Category.timestamp.desc()).all()[0:10]


@main.route('/', methods=['GET', 'POST'])
def index():
    # form = PostForm
    page = request.args.get('page', 1, type=int)
    query = Post.query
    pagination = query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    # latest_posts = query.order_by(Post.timestamp.desc()).all()[0:10]
    # latest_categories = Category.query.order_by(Category.timestamp.desc()).all()[0:10]
    return render_template('index.html', posts=posts, pagination=pagination,
                           latest_posts=g.latest_posts, latest_categories=g.latest_categories)


@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    # latest_posts = Post.query.order_by(Post.timestamp.desc()).all()[0:10]
    # latest_categories = Category.query.order_by(Category.timestamp.desc()).all()[0:10]
    return render_template('post.html', post=post,
                           latest_posts=g.latest_posts, latest_categories=g.latest_categories)


@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    form = PostForm()
    form.category.choices = [(c.id, c.name) for c in Category.query.order_by(Category.timestamp.desc())]
    if len(form.category.choices) == 0:
        form.category.choices.append(('-1', 'no category'))
    if form.validate_on_submit():
        if post.category is not None:
            if post.category.id != form.category.data:
                db.session.delete(post)
                db.session.commit()
                post = Post(category=Category.query.filter_by(id=form.category.data).first())
            else:
                pass
        else:
            post.category = Category.query.filter_by(id=form.category.data).first()
        post.title = form.title.data
        post.body = form.body.data
        post.author = current_user._get_current_object()
        if form.thum.data:
            post.thumbnail_url = form.thum.data
        else:
            post.thumbnail_url = None
        if form.abstract.data:
            post.abstract = form.abstract.data

        post.category.timestamp = datetime.utcnow()
        db.session.add(post)
        db.session.commit()
        flash('The post has been updated.')
        return redirect(url_for('main.post', id=post.id))
    form.title.data = post.title
    form.body.data = post.body
    form.abstract.data = post.abstract
    form.thum.data = post.thumbnail_url
    if post.category is not None:
        form.category.default = post.category.id
    return render_template('edit_post.html', form=form)


@main.route('/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    form.category.choices = [(c.id, c.name) for c in Category.query.order_by(Category.timestamp.desc())]
    if len(form.category.choices) == 0:
        form.category.choices.append(('-1', 'no category'))
    if form.validate_on_submit() and current_user.is_authenticated:
        post = Post(title=form.title.data, body=form.body.data, author=current_user._get_current_object(),
                    category=Category.query.filter_by(id=form.category.data).first())
        if form.thum.data:
            post.thumbnail_url = form.thum.data
        else:
            post.thumbnail_url = None
        if form.abstract.data:
            post.abstract = form.abstract.data
            # form.category.choices = []
        post.category.timestamp = datetime.utcnow()
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('.index'))

    return render_template('edit_post.html', form=form)

@main.route('/.delete/<int:id>')
def delete_post(id):
    post = Post.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    flash(u'删除成功。', 'success')
    return redirect(url_for('.index'))


@main.route('/.add-photo', methods=['GET', 'POST'])
@login_required
def add_photo():
    if request.method == 'POST' and 'photo' in request.files:
        urls = save_image(request.files.getlist('photo'))

        for url in urls:

            new_photo = Photo(url=url_for('.uploaded_file', filename=url[0]), url_t=url_for('.uploaded_file', filename=url[1]))
            new_photo.filename = url[0]
            new_photo.filename_t = url[1]

            print(new_photo.url, new_photo.url_t)
            db.session.add(new_photo)
        db.session.commit()
        flash('图片添加成功！')
        return redirect(url_for('main.show_photos'))
    abort(404)


@main.route('/photos')
@login_required
def show_photos():
    form = AddPhotoForm()
    page = request.args.get('page', 1, type=int)
    pagination = Photo.query.order_by(Photo.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_PHOTOS_PER_PAGE'], error_out=False
    )
    photos = pagination.items
    if len(photos) == 0:
        no_pic = True
    else:
        no_pic = False
    return render_template('photos.html', photos=photos,
                           pagination=pagination, no_pic=no_pic, form=form)


@main.route('/photo/<int:id>', methods=['GET', 'POST'])
@login_required
def photo(id):
    photo = Photo.query.get_or_404(id)
    return render_template('photo.html', photo=photo)


@main.route('/photo/n/<int:id>')
def photo_next(id):
    "redirect to next imgae"
    photo_now = Photo.query.get_or_404(id)
    photos = Photo.query.order_by(db.asc(Photo.id)).all()
    position = list(photos).index(photo_now) + 1
    if position == len(list(photos)):
        flash(u'已经是最后一张了。', 'info')
        return redirect(url_for('.photo', id=id))
    photo = photos[position]
    return redirect(url_for('.photo', id=photo.id))


@main.route('/photo/p/<int:id>')
def photo_previous(id):
    "redirect to previous imgae"
    photo_now = Photo.query.get_or_404(id)
    photos = Photo.query.order_by(Photo.order.asc()).all()
    position = list(photos).index(photo_now) - 1
    if position == -1:
        flash(u'已经是第一张了。', 'info')
        return redirect(url_for('.photo', id=id))
    photo = photos[position]
    return redirect(url_for('.photo', id=photo.id))


@main.route('/save-photo-edit/<int:id>', methods=['GET', 'POST'])
@login_required
def save_photo_edit(id):
    photo = Photo.query.get_or_404(id)
    photo.about = request.form.get('about', '')
    # set default_value to avoid 400 error.
    db.session.add(photo)
    db.session.commit()
    flash(u'更改已保存。', 'success')
    return redirect(url_for('.photo', id=id))


@main.route('/.delete_photo/<id>')
@login_required
def delete_photo(id):
    photo = Photo.query.filter_by(id=id).first()
    if photo is None:
        flash(u'无效的操作。', 'warning')
        return redirect(url_for('.index'))
    db.session.delete(photo)
    db.session.commit()
    os.remove(current_app.config['UPLOADED_PHOTOS_DEST']+photo.filename)
    os.remove(current_app.config['UPLOADED_PHOTOS_DEST']+photo.filename_t)
    #add path
    flash(u'删除成功。', 'success')
    return redirect(url_for('.show_photos'))


@main.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOADED_PHOTOS_DEST'],
                               filename)


@main.route('/categories',  methods=['GET', 'POST'])
def all_categories():
    categories = Category.query.order_by(Category.timestamp.desc()).all()
    return render_template('categories.html', categories=categories,
                           latest_posts=g.latest_posts, latest_categories=g.latest_categories)


@main.route('/category/<int:id>')
def category(id):
    category = Category.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = category.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    return render_template('category.html', posts=posts, pagination=pagination,
                           category=category, len=len(category.posts.all()),
                           latest_posts=g.latest_posts, latest_categories=g.latest_categories)


@main.route('/new-category', methods=['GET', 'POST'])
@login_required
def new_category():
    form = CateForm()
    if form.validate_on_submit():
        category = Category(name=form.name.data, thumbnail_url=form.thum.data,
                            abstract=form.abstract.data)
        category.timestamp = datetime.utcnow()
        db.session.add(category)
        db.session.commit()
        return redirect(url_for('.all_categories'))
    return render_template('edit_category.html', form=form)


@main.route('/edit-category/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_category(id):
    category = Category.query.get_or_404(id)
    form = CateForm()
    if form.validate_on_submit():
        category.name = form.title.data
        category.abstract = form.abstract.data
        if form.thum.data:
            post.thumbnail_url = form.thum.data
        else:
            post.thumbnail_url = None

        category.timestamp = datetime.utcnow()
        db.session.add(post)
        db.session.commit()
        flash('The category has been updated.')
        return redirect(url_for('.category', id=category.id))
    form.name.data = category.name
    form.abstract.data = category.abstract
    form.thum.data = category.thumbnail_url
    return render_template('edit_category.html', form=form)


@main.route('/.delete-category/<int:id>')
@login_required
def delete_category(id):
    cate = Category.query.get_or_404(id)
    db.session.delete(cate)
    db.session.commit()
    flash(u'删除成功。', 'success')
    return redirect(url_for('.index'))


@main.route('/.search', methods=['POST'])
def search():
    if 'content' not in request.form:
        return redirect(url_for('.index'))
    content = request.form.get('content')
    contents = content.split()
    query = Post.query
    for c in contents:
        query = query.filter(Post.title.like('%' + c + '%'))
    posts = query.all()
    return render_template('search_results.html', query=content, posts=posts)

