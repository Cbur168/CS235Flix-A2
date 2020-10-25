from datetime import date

from flask import Blueprint
from flask import request, render_template, redirect, url_for, session

from better_profanity import profanity
from flask_wtf import FlaskForm
from wtforms import TextAreaField, HiddenField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError

import csflix.adapters.repository as repo
import csflix.utilities.utilities as utilities
import csflix.news.services as services

from csflix.authentication.authentication import login_required


# Configure Blueprint.
news_blueprint = Blueprint(
    'news_bp', __name__)


@news_blueprint.route('/all_movies/<page_number>', methods=['GET'])
def all_movies(page_number):
    # Read query parameters.
    search = request.args.get('search')
    tag = request.args.get('sort')
    #article_to_show_comments = request.args.get('view_comments_for')

    # Fetch the first and last articles in the series.
    first_article = services.get_first_article(repo.repo_instance)
    last_article = services.get_last_article(repo.repo_instance)


    # if article_to_show_comments is None:
    #     # No view-comments query parameter, so set to a non-existent article id.
    #     article_to_show_comments = -1
    # else:
    #     # Convert article_to_show_comments from string to int.
    #     article_to_show_comments = int(article_to_show_comments)

    # Fetch article(s) for the target date. This call also returns the previous and next dates for articles immediately
    # before and after the target date.
    try:
        articles = services.get_all_movies(page_number, repo.repo_instance, search=search, tag=tag)
        del session['no_results']
    except IndexError:
        session['no_results'] = "No Results Found"
        repo.repo_instance.split_movies()
        articles = services.get_all_movies(page_number, repo.repo_instance)
    except:
        pass

    first_article_url = None
    last_article_url = None
    next_article_url = None
    prev_article_url = None

    if len(articles) > 0:
        # There's at least one article for the target date.
        prev_article_url = url_for('news_bp.all_movies', page_number=int(page_number)-1)
        first_article_url = url_for('news_bp.all_movies', page_number=0)

        # There are articles on a subsequent date, so generate URLs for the 'next' and 'last' navigation buttons.
        next_article_url = url_for('news_bp.all_movies', page_number=int(page_number)+1)
        last_article_url = url_for('news_bp.all_movies', page_number=-1)

        # Construct urls for viewing article comments and adding comments.
        #for article in articles:
          #  article['view_comment_url'] = url_for('news_bp.all_movies')
          #  article['add_comment_url'] = url_for('news_bp.comment_on_article', article=article['id'])

        # Generate the webpage to display the articles.
        return render_template(
            'news/articles.html',
            title='Articles',
            articles_title="Movies",
            articles=articles,
            selected_articles=utilities.get_selected_articles(),
            tag_urls=utilities.get_tags_and_urls(),
            first_article_url=first_article_url,
            last_article_url=last_article_url,
            prev_article_url=prev_article_url,
            next_article_url=next_article_url,
            #show_comments_for_article=article_to_show_comments
        )

    # No articles to show, so return the homepage.
    return redirect(url_for('home_bp.home'))

@news_blueprint.route('/comment', methods=['GET', 'POST'])
@login_required
def comment_on_article():
    # Obtain the username of the currently logged in user.
    username = session['username']

    # Create form. The form maintains state, e.g. when this method is called with a HTTP GET request and populates
    # the form with an article id, when subsequently called with a HTTP POST request, the article id remains in the
    # form.
    form = CommentForm()

    if form.validate_on_submit():
        # Successful POST, i.e. the comment text has passed data validation.
        # Extract the article id, representing the commented article, from the form.
        article_id = int(form.article_id.data)

        # Use the service layer to store the new comment.
        services.add_comment(article_id, form.comment.data, username, repo.repo_instance)

        # Retrieve the article in dict form.
        article = services.get_article(article_id, repo.repo_instance)

        # Cause the web browser to display the page of all articles that have the same date as the commented article,
        # and display all comments, including the new comment.
        return redirect(url_for('news_bp.all_movies', date=article['date'], view_comments_for=article_id))

    if request.method == 'GET':
        # Request is a HTTP GET to display the form.
        # Extract the article id, representing the article to comment, from a query parameter of the GET request.
        article_id = int(request.args.get('article'))

        # Store the article id in the form.
        form.article_id.data = article_id
    else:
        # Request is a HTTP POST where form validation has failed.
        # Extract the article id of the article being commented from the form.
        article_id = int(form.article_id.data)

    # For a GET or an unsuccessful POST, retrieve the article to comment in dict form, and return a Web page that allows
    # the user to enter a comment. The generated Web page includes a form object.
    article = services.get_article(article_id, repo.repo_instance)
    return render_template(
        'news/comment_on_article.html',
        title='Edit article',
        article=article,
        form=form,
        handler_url=url_for('news_bp.comment_on_article'),
        selected_articles=utilities.get_selected_articles(),
        tag_urls=utilities.get_tags_and_urls()
    )


class ProfanityFree:
    def __init__(self, message=None):
        if not message:
            message = u'Field must not contain profanity'
        self.message = message

    def __call__(self, form, field):
        if profanity.contains_profanity(field.data):
            raise ValidationError(self.message)


class CommentForm(FlaskForm):
    comment = TextAreaField('Comment', [
        DataRequired(),
        Length(min=4, message='Your comment is too short'),
        ProfanityFree(message='Your comment must not contain profanity')])
    article_id = HiddenField("Article id")
    submit = SubmitField('Submit')