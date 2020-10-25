from typing import List, Iterable

from csflix.adapters.repository import AbstractRepository
from csflix.domain.model import make_comment, Movie as Article, Review as Comment, Tag


class NonExistentArticleException(Exception):
    pass


class UnknownUserException(Exception):
    pass


def add_comment(article_id: int, comment_text: str, username: str, rating : str, repo: AbstractRepository):
    # Check that the article exists.
    article = repo.get_article(article_id)
    if article is None:
        raise NonExistentArticleException

    user = repo.get_user(username)
    if user is None:
        raise UnknownUserException

    # Create comment.
    comment = make_comment(comment_text, user, article, rating)
    # Update the repository.
    repo.add_comment(comment)


def get_article(article_id: int, repo: AbstractRepository):
    article = repo.get_article(article_id)

    if article is None:
        raise NonExistentArticleException

    return article_to_dict(article)


def get_first_article(repo: AbstractRepository):

    article = repo.get_first_article()

    return article_to_dict(article)


def get_last_article(repo: AbstractRepository):

    article = repo.get_last_article()
    return article_to_dict(article)


def get_all_movies(n, repo: AbstractRepository, search="", tag='title'):
    # Returns articles for the target date (empty if no matches), the date of the previous article (might be null), the date of the next article (might be null)

    articles = repo.get_all_movies(n, search, tag)
    articles_dto = list()

    # Convert Articles to dictionary form.
    articles_dto = articles_to_dict(articles)

    return articles_dto


def get_article_ids_for_tag(tag_name, repo: AbstractRepository):
    article_ids = repo.get_article_ids_for_tag(tag_name)

    return article_ids


def get_articles_by_id(id_list, repo: AbstractRepository):
    articles = repo.get_articles_by_id(id_list)

    # Convert Articles to dictionary form.
    articles_as_dict = articles_to_dict(articles)

    return articles_as_dict


def get_comments_for_article(article_id, repo: AbstractRepository):
    article = repo.get_article(article_id)

    if article is None:
        raise NonExistentArticleException

    return comments_to_dict(article.comments)


# ============================================
# Functions to convert model entities to dicts
# ============================================

def article_to_dict(article: Article):
    article_dict = {
        'id': article.id,
        'release_year': article.release_year,
        'title': article.title,
        'description': article.description,
        'hyperlink': article.hyperlink,
        'rating' : article.rating,
        'votes' : article.votes,
        'revenue' : article.revenue,
        'metascore' : article.metascore,
        'image_hyperlink': article.image_hyperlink,
        'comments': comments_to_dict(article.comments),
        # 'tags': tags_to_dict(article.tags)
    }
    return article_dict


def articles_to_dict(articles: Iterable[Article]):
    try:
        return [article_to_dict(article) for article in articles]
    except:
        return

def comment_to_dict(comment: Comment):
    comment_dict = {
        'username': comment.user.username,
        'article_id': comment.movie.id,
        'comment_text': comment.review_text,
        'timestamp': comment.timestamp
    }
    return comment_dict


def comments_to_dict(comments: Iterable[Comment]):
    return [comment_to_dict(comment) for comment in comments]


def tag_to_dict(tag: Tag):
    tag_dict = {
        'name': tag.tag_name,
        'tagged_articles': [article.id for article in tag.tagged_articles]
    }
    return tag_dict


def tags_to_dict(tags: Iterable[Tag]):
    return [tag_to_dict(tag) for tag in tags]


# ============================================
# Functions to convert dicts to model entities
# ============================================

def dict_to_article(dict):
    article = Article(dict['title'], dict['release_year'], dict['rating'], dict['votes'], dict['revenue'], dict['metascore'])
    # Note there's no comments or tags.
    return article
