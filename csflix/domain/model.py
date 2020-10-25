from datetime import date, datetime
from typing import List, Iterable
import urllib, json


class User:
    
    def __init__(self, username, password):
        if type(username) == str:
            self.__username = username.strip().lower()
        else:
            self.__username = None
        
        if type(password) == str:
            self.__password = password
        else:
            self.__password = None

        self.__watched_movies = []
        self.__reviews = []
        self.__watch_time = 0

    @property
    def username(self):
        return self.__username
    
    @property
    def password(self):
        return self.__password
    
    @property
    def watched_movies(self):
        return self.__watched_movies

    @property
    def comments(self):
        return self.__reviews
    
    @property
    def time_spent_watching_movies_minutes(self):
        return self.__watch_time
    
    @username.setter
    def username(self, username):
        if type(username) == str:
            self.__username = username.strip().lower()
        
    @password.setter
    def password(self, password):
        if type(password) == str:
            self.__password = password
    
    @watched_movies.setter
    def watched_movies(self, watched_movies):
        if type(watched_movies) == list:
            self.__watched_movies = watched_movies
    
    @comments.setter
    def comments(self, reviews):
        if type(reviews) == list:
            self.__reviews = reviews

    @time_spent_watching_movies_minutes.setter
    def time_spent_watching_movies_minutes(self, time):
        try:
            if 0 >= int(time):
                raise ValueError
        except ValueError:
            pass
        else:
            self.__watch_time = time
    
    def __repr__(self):
        return f"<User {self.__username}>"
    
    def __eq__(self,other):
        return self.__username == other.__username
    
    def __lt__(self, other):
        return self.__username < other.__username
    
    def __hash__(self):
        return hash((self.__username, self.__password))
    
    def watch_movie(self, movie):
        if type(movie) != Movie:
            return
        self.__watched_movies.append(movie)
        self.__watch_time += movie.runtime_minutes

    def add_review(self, review):
        if type(review) != Review:
            return
        self.__reviews.append(review)


class Actor:

    def __init__(self, actor_full_name: str):
        if actor_full_name == "" or type(actor_full_name) is not str:
            self.__actor_full_name = None
        else:
            self.__actor_full_name = actor_full_name.strip()
        self.__colleagues = []

    @property
    def actor_full_name(self) -> str:
        return self.__actor_full_name

    @property
    def colleagues(self) -> list:
        return self.__colleagues

    def __repr__(self):
        return f"<Actor {self.__actor_full_name}>"

    def __eq__(self, other):
        return self.__actor_full_name == other.__actor_full_name
    
    def __lt__(self, other):
        return self.__actor_full_name < other.__actor_full_name
    
    def __hash__(self):
        return hash(self.__actor_full_name)
    
    def add_actor_colleague(self, colleague):
        self.__colleagues.append(colleague)

    def check_if_this_actor_worked_with(self, colleague):
        return colleague in self.__colleagues

class Director:

    def __init__(self, director_full_name: str):
        if director_full_name == "" or type(director_full_name) is not str:
            self.__director_full_name = None
        else:
            self.__director_full_name = director_full_name.strip()

    @property
    def director_full_name(self) -> str:
        return self.__director_full_name

    def __repr__(self):
        return f"<Director {self.__director_full_name}>"

    def __eq__(self, other):
        return self.__director_full_name == other.__director_full_name
    
    def __lt__(self, other):
        return self.__director_full_name < other.__director_full_name
    
    def __hash__(self):
        return hash(self.__director_full_name)

class Genre:

    def __init__(self, genre_name: str):
        if genre_name == "" or type(genre_name) is not str:
            self.__genre_name = None
        else:
            self.__genre_name = genre_name.strip()

    @property
    def genre_name (self) -> str:
        return self.__genre_name

    def __repr__(self):
        return f"<Genre {self.__genre_name}>"

    def __eq__(self, other):
        return self.__genre_name == other.__genre_name
    
    def __lt__(self, other):
        return self.__genre_name < other.__genre_name
    
    def __hash__(self):
        return hash(self.__genre_name)

class Movie:

    def __init__(self, title: str, release_year: int, rating : str, votes : str, revenue : str, metascore : str):
        if title == "" or type(title) is not str:
            self.__title = None
        else:
            self.__title = title.strip()
        try:
            self.__release_year = int(release_year)
            if self.__release_year < 1900:
                raise ValueError
        except ValueError:
            self.__release_year = None

        self.__description = ""
        self.__director = Director("")
        self.__actors = []
        self.__genres = []
        self.__runtime_minutes = 0
        self.__id = 0
        self.__comments = []
        self._rating = rating
        self._votes = votes
        self._revenue = revenue
        self._metascore = metascore
        self.__url = None

    @property
    def number_of_comments(self) -> int:
        return len(self.__comments)

    @property
    def rating(self) -> str:
        return self._rating

    @property
    def votes(self) -> str:
        return self._votes

    @property
    def revenue(self) -> str:
        return self._revenue

    @property
    def metascore(self) -> str:
        return self._metascore

    @property
    def hyperlink(self) -> str:
        return f"/movie/{self.__id}"

    @property
    def image_hyperlink(self) -> str:
        if self.__url:
            return self.__url
        url = f"https://api.themoviedb.org/3/search/movie?api_key=15d2ea6d0dc1d476efbca3eba2b9bbfb&language=en-US&query={urllib.parse.quote(self.title, safe='')}&page=1&primary_release_year={urllib.parse.quote(str(self.release_year), safe='')}"
        response = urllib.request.urlopen(url)
        data = json.loads(response.read())
        if len(data['results']) > 0:
            self.__url = f"http://image.tmdb.org/t/p/w500/{data['results'][0]['poster_path']}"
        else:
            self.__url = None
        return self.__url

    @property
    def id(self) -> int:
        return self.__id
    @property
    def title(self) -> str:
        return self.__title

    @property
    def release_year(self) -> int:
        return self.__release_year

    @property
    def description(self) -> str:
        return self.__description

    @property
    def director(self) -> Director:
        return self.__director
    
    @property
    def actors(self) -> list:
        return self.__actors
    
    @property
    def genres(self) -> list:
        return self.__genres
    
    @property
    def runtime_minutes(self) -> int:
        return self.__runtime_minutes
    
    @property
    def comments(self) -> list:
        return self.__comments
        
    @id.setter
    def id(self, other):
        self.__id = other

    @description.setter
    def description(self, new):
        if type(new) == str:
            self.__description = new.strip()

    @director.setter
    def director(self, director):
        if type(director) == Director:
            self.__director = director
    
    @actors.setter
    def actors(self, actors):
        if type(actors) == list:
            self.__actors = actors
    
    @genres.setter
    def genres(self, genres):
        if type(genres) == list:
            self.__genres = genres
    
    @runtime_minutes.setter
    def runtime_minutes(self, runtime_minutes):
        if int(runtime_minutes) < 0:
            raise ValueError
        else:
            self.__runtime_minutes = int(runtime_minutes)

    def __repr__(self):
        return f"<Movie {self.__title}, {self.__release_year}>"

    def __eq__(self, other):
        return self.__title == other.__title and self.__release_year == other.__release_year
    
    def __lt__(self, other):
        if self.__title == other.__title:
            return self.__release_year < other.__release_year
        return self.__title < other.__title
    
    def __hash__(self):
        return hash((self.__title, self.__release_year))
    
    def add_actor(self, actor):
        if type(actor) == Actor:
            self.__actors.append(actor)
    
    def remove_actor(self, actor):
        if actor in self.__actors:
            self.__actors.pop(self.__actors.index(actor))
    
    def add_genre(self, genre):
        if type(genre) == Genre:
            self.__genres.append(genre)

    def remove_genre(self, genre):
        if genre in self.__genres:
            self.__genres.pop(self.__genres.index(genre))
    
    def add_comment(self, other):
        self.__comments.append(other)

class Review:
    
    def __init__(self, movie, user, review_text, rating):
        try:
            if not (1 <= int(rating) <= 10):
                raise ValueError
        except ValueError:
            self.__rating = None
        else:
            self.__rating = rating
        
        self.__movie = movie
        self.__review_text = review_text
        self.__timestamp = datetime.now()
        self.__user = user
    
    def __repr__(self):
        return f"<Review {self.__movie}>"
    
    def __eq__(self, other):
        return self.__movie == other.__movie and self.__review_text == other.__review_text and self.__rating == other.__rating and self.__timestamp == other.__timestamp

    @property 
    def user(self):
        return self.__user

    @property
    def movie(self):
        return self.__movie
    
    @property
    def review_text(self):
        return self.__review_text
    
    @property
    def rating(self):
        return self.__rating
    
    @property
    def timestamp(self):
        return self.__timestamp

    @user.setter
    def user(self, other):
        self.__user = other


class Tag:
    def __init__(self, tag_name: str):
        self._tag_name: str = tag_name
        self._tagged_articles: List[Movie] = list()

    @property
    def tag_name(self) -> str:
        return self._tag_name

    @property
    def tagged_articles(self) -> Iterable[Movie]:
        return iter(self._tagged_articles)

    @property
    def number_of_tagged_articles(self) -> int:
        return len(self._tagged_articles)

    def is_applied_to(self, article: Movie) -> bool:
        return article in self._tagged_articles

    def add_article(self, article: Movie):
        self._tagged_articles.append(article)

    def __eq__(self, other):
        if not isinstance(other, Tag):
            return False
        return other._tag_name == self._tag_name


class ModelException(Exception):
    pass


def make_comment(comment_text: str, user: User, article: Movie, rating : str):
    comment = Review(article, user, comment_text, rating)
    user.add_review(comment)
    article.add_comment(comment)

    return comment


def make_tag_association(article: Movie, tag: Tag):
    if tag.is_applied_to(article):
        raise ModelException(f'Tag {tag.tag_name} already applied to Article "{article.title}"')

    article.add_tag(tag)
    tag.add_article(article)
