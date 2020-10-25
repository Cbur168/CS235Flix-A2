from datetime import date

from csflix.domain.model import User, Movie as Article, Tag, make_comment, make_tag_association, ModelException

import pytest


@pytest.fixture()
def article():
    return Article(
        'Guardians of the Galaxy',
        '2014',
        '8.1',
        '757074',
        '333.13',
        '76',
    )


@pytest.fixture()
def user():
    return User('dbowie', '1234567890')

def test_user_construction(user):
    assert user.username == 'dbowie'
    assert user.password == '1234567890'
    assert repr(user) == '<User dbowie>'

    for comment in user.comments:
        # User should have an empty list of Comments after construction.
        assert False


def test_article_construction(article):
    assert article.id is 0
    assert article.release_year == 2014
    assert article.title == 'Guardians of the Galaxy'
    article.description = "A group of intergalactic criminals are forced to work together to stop a fanatical warrior from taking control of the universe."
    assert article.description == 'A group of intergalactic criminals are forced to work together to stop a fanatical warrior from taking control of the universe.'
    assert article.image_hyperlink == 'http://image.tmdb.org/t/p/w500//r7vmZjiyZw9rpJMQJdXpjgiCOk9.jpg'

    assert article.number_of_comments == 0
    assert repr(
        article) == '<Movie Guardians of the Galaxy, 2014>'


def test_article_less_than_operator():
    article_1 = Article(
        'Guardians of the Galaxy',
        '2014',
        '8.1',
        '757074',
        '333.13',
        '76',
    )

    article_2 = Article(
        'Guardians of the Galaxy',
        '2017',
        '8.1',
        '757074',
        '333.13',
        '76',
    )
    assert article_1 < article_2

def test_make_comment_establishes_relationships(article, user):
    comment_text = 'csflix in the USA!'
    rating = 3
    comment = make_comment(comment_text, user, article, rating)

    # Check that the User object knows about the Comment.
    assert comment in user.comments

    # Check that the Comment knows about the User.
    assert comment.user is user

    # Check that Article knows about the Comment.
    assert comment in article.comments

    # Check that the Comment knows about the Article.
    assert comment.movie is article
