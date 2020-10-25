import csv
import os
import urllib, json, re
from datetime import date, datetime
from typing import List

from bisect import bisect, bisect_left, insort_left

from werkzeug.security import generate_password_hash

from csflix.adapters.repository import AbstractRepository, RepositoryException
from csflix.domain.model import Movie, Director, Genre, Actor, Tag, User, Review, make_tag_association, make_comment


class MemoryRepository(AbstractRepository):
    # Articles ordered by date, not id. id is assumed unique.

    def __init__(self):
        self._articles = list()
        self._articles_index = dict()
        self._tags = list()
        self._users = list()
        self._comments = list()
        self._articles_by_page = list()

    def add_user(self, user: User):
        self._users.append(user)

    def get_user(self, username) -> User:
        return next((user for user in self._users if user.username == username.lower()), None)

    def add_article(self, article: Movie):
        insort_left(self._articles, article)
        self._articles_index[int(article.id)] = article

    def get_article(self, id: int) -> Movie:
        article = None
        
        try:
            article = self._articles_index[int(id)]
        except KeyError:
            pass  # Ignore exception and return None.

        return article
    
    def split_movies(self, max_per_page = 5, filter = "", tag = 'title'):
        tags = {None: lambda x: x.title, 'title' : lambda x: x.title, 'genres' : lambda x: "".join([z.genre_name for z in x.genres]), 'actors' : lambda x:"".join([z.actor_full_name for z in x.actors]), 'director' : lambda x: x.director.director_full_name}
        func = tags[tag]
        filtered_articles = [movie for movie in self._articles if filter.lower() in func(movie).lower()]
        self._articles_by_page = [filtered_articles[i:i + max_per_page] for i in range(0, len(filtered_articles), max_per_page)]

    def get_all_movies(self, n, search, tag) -> List[Movie]:
        if search or tag:
            self.split_movies(filter=search, tag=tag)
        else:
            self.split_movies()
        try:
            return self._articles_by_page[int(n)]
        except:
            return
    def get_number_of_articles(self):
        return len(self._articles)

    def get_first_article(self):
        article = None

        if len(self._articles) > 0:
            article = self._articles[0]
        return article

    def get_last_article(self):
        article = None

        if len(self._articles) > 0:
            article = self._articles[-1]
        return article

    def get_articles_by_id(self, id_list):
        # Strip out any ids in id_list that don't represent Article ids in the repository.
        existing_ids = [id for id in id_list if id in self._articles_index]

        # Fetch the Articles.
        articles = [self._articles_index[id] for id in existing_ids]
        
        return articles

    def get_article_ids_for_tag(self, tag_name: str):
        # Linear search, to find the first occurrence of a Tag with the name tag_name.
        tag = next((tag for tag in self._tags if tag.tag_name == tag_name), None)

        # Retrieve the ids of articles associated with the Tag.
        if tag is not None:
            article_ids = [article.id for article in tag.tagged_articles]
        else:
            # No Tag with name tag_name, so return an empty list.
            article_ids = list()

        return article_ids

    def get_date_of_previous_article(self, article: Movie):
        previous_date = None

        try:
            index = self.article_index(article)
            for stored_article in reversed(self._articles[0:index]):
                if stored_article.date < article.date:
                    previous_date = stored_article.date
                    break
        except ValueError:
            # No earlier articles, so return None.
            pass

        return previous_date

    def get_date_of_next_article(self, article: Movie):
        next_date = None

        try:
            index = self.article_index(article)
            for stored_article in self._articles[index + 1:len(self._articles)]:
                if stored_article.id > article.id:
                    next_date = stored_article.id
                    break
        except ValueError:
            # No subsequent articles, so return None.
            pass

        return next_date

    def add_tag(self, tag: Tag):
        self._tags.append(tag)

    def get_tags(self) -> List[Tag]:
        return self._tags

    def add_comment(self, comment: Review):
        super().add_comment(comment)
        self._comments.append(comment)

    def get_comments(self):
        return self._comments

    # Helper method to return article index.
    def article_index(self, article: Review):
        index = bisect_left(self._articles, article)
        if index != len(self._articles) and self._articles[index].id == article.id:
            return index
        raise ValueError


def read_csv_file(filename: str):
    with open(filename, encoding='utf-8-sig') as infile:
        reader = csv.reader(infile)

        # Read first line of the the CSV file.
        headers = next(reader)

        # Read remaining rows from the CSV file.
        for row in reader:
            # Strip any leading/trailing white space from data read.
            row = [item.strip() for item in row]
            yield row


def load_articles_and_tags(data_path: str, repo: MemoryRepository):
    tags = dict()

    for data_row in read_csv_file(os.path.join(data_path, 'news_articles.csv')):

        # Add any new tags; associate the current article with tags.
        # for tag in article_tags:
        #     if tag not in tags.keys():
        #         tags[tag] = list()
        #     tags[tag].append(article_key)
        # del data_row[-number_of_tags:]

        # Create Movie object
        article = Movie(
            title=data_row[1],
            release_year=data_row[6],
            rating=data_row[8],
            votes=data_row[9],
            revenue=data_row[10],
            metascore=data_row[11]
        )
        article.id = data_row[0]
        article.description = data_row[3]
        article.director = Director(data_row[4])
        for actor in re.split(', |,', data_row[5]):
            article.add_actor(Actor(actor))
        
        for genre in re.split(', |,', data_row[2]):
            article.add_genre(Genre(genre))
        article.runtime_minutes = data_row[7]

        # Add the Article to the repository.
        repo.add_article(article)
    repo.split_movies()

    # Create Tag objects, associate them with Articles and add them to the repository.
    for tag_name in tags.keys():
        tag = Tag(tag_name)
        for article_id in tags[tag_name]:
            article = repo.get_article(article_id)
            make_tag_association(article, tag)
        repo.add_tag(tag)


def load_users(data_path: str, repo: MemoryRepository):
    users = dict()

    for data_row in read_csv_file(os.path.join(data_path, 'users.csv')):
        user = User(
            username=data_row[1],
            password=generate_password_hash(data_row[2])
        )
        repo.add_user(user)
        users[data_row[0]] = user
    return users


def load_comments(data_path: str, repo: MemoryRepository, users):
    for data_row in read_csv_file(os.path.join(data_path, 'comments.csv')):
        comment = make_comment(
            comment_text=data_row[3],
            user=users[data_row[1]],
            article=repo.get_article(int(data_row[2])),
            rating=data_row[4]
        )
        repo.add_comment(comment)


def populate(data_path: str, repo: MemoryRepository):
    # Load articles and tags into the repository.
    load_articles_and_tags(data_path, repo)

    # Load users into the repository.
    users = load_users(data_path, repo)

    # Load comments into the repository.
    load_comments(data_path, repo, users)
