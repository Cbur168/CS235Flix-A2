from datetime import date, datetime
from typing import List

import pytest

from csflix.domain.model import User, Movie as Article, Tag, Review as Comment, make_comment
from csflix.adapters.repository import RepositoryException

def test_repository_can_add_a_user(in_memory_repo):
    user = User('Dave', '123456789')
    in_memory_repo.add_user(user)

    assert in_memory_repo.get_user('Dave') is user

def test_repository_can_retrieve_a_user(in_memory_repo):
    user = in_memory_repo.get_user('fmercury')
    assert user == User('fmercury', '8734gfe2058v')

def test_repository_does_not_retrieve_a_non_existent_user(in_memory_repo):
    user = in_memory_repo.get_user('prince')
    assert user is None

def test_repository_can_retrieve_article_count(in_memory_repo):
    number_of_articles = in_memory_repo.get_number_of_articles()

    # Check that the query returned 6 Articles.
    assert number_of_articles == 1000

def test_repository_can_add_article(in_memory_repo):
    article = Article(
        'Guardians of the Galaxy',
        '2014',
        '8.1',
        '757074',
        '333.13',
        '76',
    )
    article.id = 1001
    in_memory_repo.add_article(article)

    assert in_memory_repo.get_article(1001) is article

def test_repository_can_retrieve_article(in_memory_repo):
    article = in_memory_repo.get_article(1)

    # Check that the Article has the expected title.
    assert article.title == 'Guardians of the Galaxy'

    #Check that the Article is commented as expected.
    comment_one = [comment for comment in article.comments if comment.review_text == 'Oh no, csflix has hit New Zealand'][0]
    comment_two = [comment for comment in article.comments if comment.review_text == 'Yeah Freddie, bad news'][0]

    assert comment_one.user.username == 'fmercury'
    assert comment_two.user.username == "thorke"

    # Check that the Article is tagged as expected.

    assert repr(article.genres) == "[<Genre Action>, <Genre Adventure>, <Genre Sci-Fi>]"

def test_repository_does_not_retrieve_a_non_existent_article(in_memory_repo):
    article = in_memory_repo.get_article(1001)
    assert article is None


def test_repository_can_retrieve_page_of_movies(in_memory_repo):
    articles = in_memory_repo.get_all_movies(0, "", "title")
    # Check that the query returned 3 Articles.
    assert len(articles) == 5


def test_repository_can_get_first_article(in_memory_repo):
    article = in_memory_repo.get_first_article()
    assert article.title == '(500) Days of Summer'

def test_repository_can_get_last_article(in_memory_repo):
    article = in_memory_repo.get_last_article()
    assert article.title == 'Zootopia'


def test_repository_can_get_articles_by_ids(in_memory_repo):
    articles = in_memory_repo.get_articles_by_id([2, 5, 6])

    assert len(articles) == 3
    assert articles[0].title == 'Prometheus'
    assert articles[1].title == "Suicide Squad"
    assert articles[2].title == 'The Great Wall'


def test_repository_does_not_retrieve_article_for_non_existent_id(in_memory_repo):
    articles = in_memory_repo.get_articles_by_id([2, 1001])
    assert len(articles) == 1
    assert articles[0].title == 'Prometheus'

def test_repository_returns_an_empty_list_for_non_existent_ids(in_memory_repo):
    articles = in_memory_repo.get_articles_by_id([0, 1001])

    assert len(articles) == 0


def test_repository_can_add_a_comment(in_memory_repo):
    user = in_memory_repo.get_user('thorke')
    article = in_memory_repo.get_article(2)
    comment = make_comment("I don't know what to think", user, article, 7)

    in_memory_repo.add_comment(comment)

    assert comment in in_memory_repo.get_comments()

def test_repository_does_not_add_a_comment_without_a_user(in_memory_repo):
    article = in_memory_repo.get_article(2)
    comment = Comment(article, User('None', 'None'), "Wow great film", 10)

    with pytest.raises(RepositoryException):
        in_memory_repo.add_comment(comment)


def test_repository_does_not_add_a_comment_without_an_article_properly_attached(in_memory_repo):
    user = in_memory_repo.get_user('thorke')
    article = in_memory_repo.get_article(2)
    comment = Comment(Article(
        'None',
        '2014',
        '8.1',
        '757074',
        '333.13',
        '76',
    ), 
    user, "Wow trash", 0)

    user.add_review(comment)

    with pytest.raises(RepositoryException):
        # Exception expected because the Article doesn't refer to the Comment.
        in_memory_repo.add_comment(comment)


def test_repository_can_retrieve_comments(in_memory_repo):
    assert len(in_memory_repo.get_comments()) == 3
