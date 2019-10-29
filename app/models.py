from app import db, login, app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import jwt
from time import time


class User(UserMixin, db.Model):
    """
    Classe User
    :param id: identifiant de l'utilisateur
    :param username: nom d'utilisateur
    :param email: email utilisateur
    :param name: prenom de l'utilisateur
    :param surname: nom de famille de l'utilisateur
    :param password_hash : mot de passe hash apres inscription de l'utilisateur
    :param series: texte avec des id series associes au code du dernier episode vu par l'utilisateur
    :param movies: texte avec la liste des id des films vus
    :param series_grades: texte avec des id series associes a la note donnee par l'utilisateur
    :param movies_grades: texte avec des id movies associes a la note donnee par l'utilisateur
    :param current_grade: nombre correspondant a la note actuelle de l'utilisateur
    :param session_id: l'id_session donne par l'API MovieDB pour avoir une guest session pour l'utilisateur
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    name = db.Column(db.String(64))
    surname = db.Column(db.String(64))
    password_hash = db.Column(db.String(128))
    _series = db.Column(db.Text())
    _movies = db.Column(db.Text())
    series_grades = db.Column(db.Text())
    movies_grades = db.Column(db.Text())
    current_grade = db.Column(db.Float)
    session_id = db.Column(db.String(64))

    def __repr__(self):
        return f"Username : {self.username}, Name : {self.name}, Surname : {self.surname}, Email : {self.email}," \
               f" Series : {self.series}"


    """
    Getters et setters pour series, movies et password
    """
    def _set_series(self, series):
        self._series = series

    def _get_series(self):
        return self._series

    def _set_movies(self, movies):
        self._movies = movies

    def _get_movies(self):
        return self._movies

    series = property(_get_series,_set_series)
    movies = property(_get_movies,_set_movies)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


    """
    Cette methode permet de retourner la liste des id des series ajoutees par l'utilisateur
    """
    def list_serie(self):
        # Le format du texte est sous la forme {idserie}x{Snum_saisonEnum_episode}-{idserie}x{Snum_saisonEnum_episode} .
        # Renvoie une liste de id_serie
        if self.series is not None and self.series != '':
            serie_episode_list = self.series.split('-')
            serie_list = []
            for serie in serie_episode_list:
                serie_list.append(serie.split('x')[0])
            return serie_list
        else :
            return "The user doesn't have any series"

    """
    Cette methode permet de retourner la liste des id des films ajoutees par l'utilisateur
    """
    def list_movie(self):
        #Le format du texte est sous la forme {idmovie}-{idmovie}
        #Renvoie une liste de idmovie
        if self.movies is not None and self.movies != '':
            moviestring = self.movies.split('-')
            movie_list = []
            for movie in moviestring:
                movie_list.append(movie)
            return movie_list
        else:
            return "The user doesn't have any movie"


    """
    Cette methode permet de savoir si une serie est dans la liste des series de l'utilisateur
    """
    def is_in_series(self,id):
        db.session.commit()
        list_serie = self.list_serie()
        return self.series is not None and str(id) in list_serie

    """
    Cette methode permet de savoir si un film est dans la liste des films de l'utilisateur
    """
    def has_movie(self,id):
        db.session.commit()
        list_movie = self.list_movie()
        return self.movies is not None and str(id) in list_movie

    """
    Cette methode permet de retourner le derniere episode vu pour la serie avec l'ID "id"
    """
    def get_last_episode_viewed(self,id):
        if self.series == None :
            return('S1E1')
        else :
            series_strings = self.series.split('-')
            for serie_string in series_strings:
                serieid = serie_string.split('x')[0]
                if serieid == str(id):
                    return(serie_string.split('x')[1])

    """
    Cette methode sert a determiner si un episode de la saison "season" et de numero d'episode "episode"
    est posterieur au dernier episode vu pour la serie qui a l'ID "serie"
    """
    def is_after(self, season, episode, serie):
        if str(serie) not in self.series:
            return True
        else :
            series_strings = self.series.split('-')
            for serie_string in series_strings :
                if int(serie_string.split('x')[0]) == serie :
                    code = serie_string.split('x')[1]
                    code_last = code.split('E')
            return(int(code_last[0].split('S')[1]) < season or (int(code_last[0].split('S')[1]) == season and int(code_last[1]) < episode) )

    """
    Cette methode permet de remplacer le dernier episode vu par l'utilisateur pour la serie d'ID "serie" par l'episode "episode"
    on va donc remplacer le code de l'episode dans series par le code "episode"
    """
    def view_episode(self, episode, serie):
        user_series = self.series.split('-')
        for userserie in user_series :
            if userserie.split('x')[0] == str(serie) :
                last_episode_watched = userserie.split('x')[1]
                new_series = self.series.replace(userserie, userserie.replace(last_episode_watched, episode))
                self._set_series(new_series)
                db.session.commit()

    """
    Cette methode permet d'ajouter une serie a la liste des series de l'utilisateur dans le texte series
    """
    def add_serie(self, id_serie):
        list_serie = self.list_serie()
        if id_serie not in list_serie:
            if self.series is None or self.series == '':
                self._series = f"{id_serie}xS1E1"
            else:
                self._series += f"-{id_serie}xS1E1"
            db.session.commit()

    """
    Cette methode permet d'enlever une serie de la liste des series de l'utilisateur dans le texte series
    """
    def remove_serie(self,id_serie):
        string_series = self._series.split('-')
        for i, string_serie in enumerate(string_series):
            split_serie = string_serie.split('x')
            if split_serie[0] == str(id_serie):
                if i == 0 :
                    if len(string_series) == 1:
                        self._series = self._series.replace(string_serie, '')
                    else:
                        self._series = self._series.replace(string_serie+'-','')
                else :
                    self._series = self._series.replace('-'+string_serie,'')
        db.session.commit()

    """
    Cette methode permet d'ajouter un film a la liste des films de l'utilisateur dans le texte movies
    """
    def add_movie(self, id_movie):
        list_movie = self.list_movie()
        if id_movie not in list_movie:
            if self.movies is None or self.movies == '':
                self._movies = f"{id_movie}"
            else:
                self._movies += f"-{id_movie}"
            db.session.commit()

    """
    Cette methode permet d'enlever un film de la liste des films de l'utilisateur dans le texte movies
    """
    def remove_movie(self, id_movie):
        list_movie = self.list_movie()
        if id_movie in list_movie:
            i = list_movie.index(id_movie)
            if i == 0:
                if len(list_movie) == 1:
                    self._movies = self._movies.replace(str(id_movie) , '')
                else:
                    self._movies = self._movies.replace(str(id_movie)+'-','')
            else:
                self._movies = self._movies.replace('-'+str(id_movie),'')
            db.session.commit()

    """
    Cette methode permet de changer la note actuelle de l'utilisateur quand il clique sur une etoile
    """
    def update_grade(self, new_grade):
        self.current_grade = new_grade
        db.session.commit()


    """
    Cette methode permet d'associer une note a un film ou une serie dans movies_grades ou series_grades
    """
    def grade(self, id, type, grade):
        if type == 'serie':
            if self.series_grades is None or self.series_grades == '':
                self.series_grades = str(id) + 'x' + str(grade)
            else:
                self.series_grades += '-' + str(id) + 'x' + str(grade)
        else:
            if type == 'movie':
                if self.movies_grades is None or self.movies_grades == '':
                    self.movies_grades = str(id) + 'x' + str(grade)
                else:
                    self.movies_grades += '-' + str(id) + 'x' + str(grade)
        db.session.commit()


    """
    Cette methode permet de savoir si l'on a deja note une serie ou un film
    """
    def is_graded(self, type, id):
        if type == 'serie':
            if self.series_grades is None:
                return(False)
            else :
                return str(id) in self.series_grades
        elif type == 'movie':
            if self.movies_grades is None:
                return(False)
            return str(id) in self.movies_grades
        else:
            raise ValueError("The type of this media is unknown")

    """
    Cette methode permet d'obtenir la note donnee par l'utilisateur a un film ou une serie
    """
    def get_grade(self, type, id):
        if type == 'serie':
            if self.series_grades is None:
                return False
            else:
                grades = self.series_grades.split('-')
                for grade in grades:
                    if grade.split('x')[0] == str(id):
                        return (float(grade.split('x')[1]))
                if str(id) not in grades :
                    return False
        elif type == 'movie':
            if self.movies_grades is None:
                return False
            else:
                grades = self.movies_grades.split('-')
                for grade in grades:
                    if grade.split('x')[0] == str(id):
                        return (float(grade.split('x')[1]))
                if str(id) not in grades:
                    return False
        else:
            raise ValueError("The type of this media is unknown")
    """
    Cette methode permet de retirer la note associee a un film ou une serie pour l'utilisateur
    """
    def unrate(self, type, id):
        if type == 'serie' and self.series_grades is not None:
            grades = self.series_grades.split('-')
            for i, grade in enumerate(grades):
                if grade.split('x')[0] == str(id):
                    if i == 0:
                        if len(grades) == 1:
                            self.series_grades = self.series_grades.replace(grade, '')
                        else:
                            self.series_grades = self.series_grades.replace(grade + '-', '')
                    else:
                        self.series_grades = self.series_grades.replace('-' + grade, '')
        elif type == 'movie' and self.movies_grades is not None:
            grades = self.movies_grades.split('-')
            for i, grade in enumerate(grades):
                if grade.split('x')[0] == str(id):
                    if i == 0:
                        if len(grades)==1:
                            self.movies_grades = self.movies_grades.replace(grade, '')
                        else:
                            self.movies_grades = self.movies_grades.replace(grade + '-', '')
                    else:
                        self.movies_grades = self.movies_grades.replace('-' + grade, '')
        db.session.commit()


    """
    Ces methodes sont utilisees lorsque l'utilisateur souhaite reinitialiser sont mot de passe
    """
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


@login.user_loader
def user_loader(id):
    return User.query.get(int(id))

