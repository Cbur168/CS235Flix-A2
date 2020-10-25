from datetime import date

import pytest

from csflix.authentication.services import AuthenticationException
from csflix.news import services as news_services
from csflix.authentication import services as auth_services
from csflix.news.services import NonExistentArticleException


def test_can_add_user(in_memory_repo):
    new_username = 'jz'
    new_password = 'abcd1A23'

    auth_services.add_user(new_username, new_password, in_memory_repo)

    user_as_dict = auth_services.get_user(new_username, in_memory_repo)
    assert user_as_dict['username'] == new_username

    # Check that password has been encrypted.
    assert user_as_dict['password'].startswith('pbkdf2:sha256:')


def test_cannot_add_user_with_existing_name(in_memory_repo):
    username = 'thorke'
    password = 'abcd1A23'

    with pytest.raises(auth_services.NameNotUniqueException):
        auth_services.add_user(username, password, in_memory_repo)


def test_authentication_with_valid_credentials(in_memory_repo):
    new_username = 'pmccartney'
    new_password = 'abcd1A23'

    auth_services.add_user(new_username, new_password, in_memory_repo)

    try:
        auth_services.authenticate_user(new_username, new_password, in_memory_repo)
    except AuthenticationException:
        assert False


def test_authentication_with_invalid_credentials(in_memory_repo):
    new_username = 'pmccartney'
    new_password = 'abcd1A23'

    auth_services.add_user(new_username, new_password, in_memory_repo)

    with pytest.raises(auth_services.AuthenticationException):
        auth_services.authenticate_user(new_username, '0987654321', in_memory_repo)


def test_can_add_comment(in_memory_repo):
    article_id = 3
    comment_text = 'The loonies are stripping the supermarkets bare!'
    username = 'fmercury'

    # Call the service layer to add the comment.
    news_services.add_comment(article_id, comment_text, username, 0, in_memory_repo)

    # Retrieve the comments for the article from the repository.
    comments_as_dict = news_services.get_comments_for_article(article_id, in_memory_repo)

    # Check that the comments include a comment with the new comment text.
    assert next(
        (dictionary['comment_text'] for dictionary in comments_as_dict if dictionary['comment_text'] == comment_text),
        None) is not None


def test_cannot_add_comment_for_non_existent_article(in_memory_repo):
    article_id = 1001
    comment_text = "csflix - what's that?"
    username = 'fmercury'

    # Call the service layer to attempt to add the comment.
    with pytest.raises(news_services.NonExistentArticleException):
        news_services.add_comment(article_id, comment_text, username, 5, in_memory_repo)


def test_cannot_add_comment_by_unknown_user(in_memory_repo):
    article_id = 3
    comment_text = 'The loonies are stripping the supermarkets bare!'
    username = 'gmichael'

    # Call the service layer to attempt to add the comment.
    with pytest.raises(news_services.UnknownUserException):
        news_services.add_comment(article_id, comment_text, username, 5, in_memory_repo)


def test_can_get_article(in_memory_repo):
    article_id = 2

    article_as_dict = news_services.get_article(article_id, in_memory_repo)

    assert article_as_dict['id'] == str(article_id)
    assert article_as_dict['release_year'] == 2012
    assert article_as_dict['title'] == 'Prometheus'
    assert article_as_dict['description'] == 'Following clues to the origin of mankind, a team finds a structure on a distant moon, but they soon realize they are not alone.'
    assert article_as_dict['image_hyperlink'] == 'http://image.tmdb.org/t/p/w500//omy5CiDMQnGqQUEJ9gNLOGPZQFW.jpg'
    assert len(article_as_dict['comments']) == 0


def test_cannot_get_article_with_non_existent_id(in_memory_repo):
    article_id = 1001

    # Call the service layer to attempt to retrieve the Article.
    with pytest.raises(news_services.NonExistentArticleException):
        news_services.get_article(article_id, in_memory_repo)


def test_get_first_article(in_memory_repo):
    article_as_dict = news_services.get_first_article(in_memory_repo)

    assert article_as_dict['id'] == '508'


def test_get_last_article(in_memory_repo):
    article_as_dict = news_services.get_last_article(in_memory_repo)

    assert article_as_dict['id'] == '75'


def test_get_all_movies_with_search_filter(in_memory_repo):


    articles_as_dict = news_services.get_all_movies(0, in_memory_repo, search="Zoo")
    assert len(articles_as_dict) == 2
    assert articles_as_dict[0]['id'] == '432'
    assert articles_as_dict[1]['title'] == 'Zootopia'


def test_get_first_page_movies_with_search_and_filter(in_memory_repo):

    articles_as_dict = news_services.get_all_movies(0, in_memory_repo, search="Comedy", tag="genres")
    assert len(articles_as_dict) == 5
    assert articles_as_dict[0]['id'] == '508'
    assert articles_as_dict[1]['title'] == '10 Years'
    assert articles_as_dict[2]['release_year'] == 2009

def test_invalid_search_is_handled_elsewhere(in_memory_repo):

    articles_as_dict = news_services.get_all_movies(0, in_memory_repo, search="sdthgsd")


def test_get_articles_by_filter_tag(in_memory_repo):
    articles_as_dict = news_services.get_all_movies(0, in_memory_repo, tag="genres")

    assert len(articles_as_dict) == 5



def test_get_comments_for_article(in_memory_repo):
    comments_as_dict = news_services.get_comments_for_article(1, in_memory_repo)

    # Check that 2 comments were returned for article with id 1.
    assert len(comments_as_dict) == 3

    # Check that the comments relate to the article whose id is 1.
    article_ids = [comment['article_id'] for comment in comments_as_dict]
    article_ids = set(article_ids)
    assert '1' in article_ids and len(article_ids) == 1


def test_get_comments_for_non_existent_article(in_memory_repo):
    with pytest.raises(NonExistentArticleException):
        comments_as_dict = news_services.get_comments_for_article(1001, in_memory_repo)


def test_get_comments_for_article_without_comments(in_memory_repo):
    comments_as_dict = news_services.get_comments_for_article(2, in_memory_repo)
    assert len(comments_as_dict) == 0
