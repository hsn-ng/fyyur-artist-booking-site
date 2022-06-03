#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import sys
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    if isinstance(value, str):
        date = dateutil.parser.parse(value)
    else:
        date = value
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    #All locations query
    areas = db.session.query(Venue.city, Venue.state).group_by(
        Venue.city, Venue.state).all()
    venues = []
    data = []

    for area in areas:
        venues_query = db.session.query(Venue).filter_by(
            city=area.city).filter_by(state=area.state).all()
        for venue in venues_query:
            print(area)
            venues.append({
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": len(db.session.query(Show).join(Venue).filter(Show.venue_id == venue.id).filter(Show.start_time > datetime.now()).all())
            })
        data.append({
            "city": area.city,
            "state": area.state,
            'venues': venues
        })

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():

    search_term = request.form.get('search_term', '')

    #All locations query filtering search results
    venues = db.session.query(Venue).filter(
        Venue.name.ilike(f'%{search_term}%')).all()
    data = []
    for venue in venues:
        data.append({
            'id': venue.id,
            'name': venue.name,
            'num_upcoming_shows': len(db.session.query(Show).join(Venue).filter(Venue.id == venue.id).filter(Show.start_time > datetime.now()).all())

        })
    response = {
        'count': len(venues),
        'data': data
    }
    return render_template('pages/search_venues.html', results=response, search_term=search_term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    #venue query by id
    venue = Venue.query.get(venue_id)
    upcoming_shows = []
    past_shows = []

    upcoming_shows_query = db.session.query(Show).join(Artist).filter(
        Show.venue_id == venue_id).filter(Show.start_time > datetime.now()).all()

    for show in upcoming_shows_query:
        upcoming_shows.append({
            'artist_id': show.artist_id,
            'artist_name': show.artists.name,
            'artist_image_link': show.artists.image_link,
            'start_time': show.start_time
        })

    past_shows_query = db.session.query(Show).join(Artist).filter(
        Show.venue_id == venue_id).filter(Show.start_time < datetime.now()).all()

    for show in past_shows_query:
        upcoming_shows.append({
            'artist_id': show.artist_id,
            'artist_name': show.artists.name,
            'artist_image_link': show.artists.image_link,
            'start_time': show.start_time
        })

    data = {
        'id': venue.id,
        'name': venue.name,
        'genres': venue.genres,
        "address": venue.address,
        'city': venue.city,
        'state': venue.state,
        'phone': venue.phone,
        'image_link': venue.image_link,
        'facebook_link': venue.facebook_link,
        'website_link': venue.website_link,
        'seeking_talent': True,
        'seeking_description': venue.seeking_description,
        'past_shows': past_shows,
        'upcoming_shows': upcoming_shows,
        'past_shows_count': len(past_shows),
        'upcoming_shows_count': len(upcoming_shows),
    }

    print(upcoming_shows, past_shows)

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    #Insert venue form data into the db table 
    error = False
    try:
        data = request.form
        venue = Venue(
            name=data['name'],
            city=data['city'],
            state=data['state'],
            address=data['address'],
            phone=data['phone'],
            genres=data['genres'],
            facebook_link=data['facebook_link'],
            image_link=data['image_link'],
            website_link=data['website_link'],
            seeking_description=data['seeking_description']
        )

        db.session.add(venue)
        db.session.commit()

    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())

    finally:
        db.session.close()

    if error == True:
        flash(f"An error occurred. Venue {data['name']} could not be listed.")
    else:
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>/delete', methods=['DELETE'])
def delete_venue(venue_id):
    
    error = False

    try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
    except:
        db.session.rollback()
        print(sys.exc_info())
        error = True
    finally:
        db.session.close()

    if error:
        flash(f'An error occured. Venue {venue.name} could not be deleted')
    else:
        flash(f'Venue {venue.name} deleted successfully')
    return render_template('pages/home.html', name=venue.name)

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    #All artists query
    
    artists = db.session.query(Artist).all()
    data = []
    print(artists)

    for artist in artists:
        data.append({
            'id': artist.id,
            'name': artist.name
        })
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term', '')

    #artists filter by search term
    artists = db.session.query(Artist).filter(
        Artist.name.ilike(f'%{search_term}%')).all()
    data = []

    for artist in artists:
        data.append({
            'id': artist.id,
            'name': artist.name,
            'num_upcoming_shows': len(db.session.query(Show).join(Artist).filter(Artist.id == artist.id).filter(Show.start_time > datetime.now()).all())
        })
    response = {
        'count': len(artists),
        'data': data
    }
    return render_template('pages/search_artists.html', results=response, search_term=search_term)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    #Artists query by id
    artist = Artist.query.get(artist_id)
    upcoming_shows = []
    past_shows = []

    upcoming_shows_query = db.session.query(Show).join(Venue).filter(
        Show.artist_id == artist_id).filter(Show.start_time > datetime.now()).all()

    print(upcoming_shows_query)

    for show in upcoming_shows_query:
        # print(show)
        upcoming_shows.append({
            'venue_id': show.venue_id,
            'venue_name': show.venues.name,
            'venue_image_link': show.venues.image_link,
            'start_time': show.start_time
        })

    past_shows_query = db.session.query(Show).join(Venue).filter(
        Show.artist_id == artist_id).filter(Show.start_time < datetime.now()).all()

    for show in past_shows_query:
        # print(show)
        upcoming_shows.append({
            'venue_id': show.venue_id,
            'venue_name': show.venues.name,
            'venue_image_link': show.venues.image_link,
            'start_time': show.start_time
        })

    data = {
        'id': artist.id,
        'name': artist.name,
        'genres': artist.genres,
        'city': artist.city,
        'state': artist.state,
        'phone': artist.phone,
        'image_link': artist.image_link,
        'facebook_link': artist.facebook_link,
        'website_link': artist.website_link,
        'seeking_venue': True,
        'seeking_description': artist.seeking_description,
        'past_shows': past_shows,
        'upcoming_shows': upcoming_shows,
        'past_shows_count': len(past_shows),
        'upcoming_shows_count': len(upcoming_shows),
    }

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)

    if artist:
        form.name.data = artist.name
        form.city.data = artist.city
        form.state.data = artist.state
        form.phone.data = artist.phone
        form.genres.data = artist.genres
        form.facebook_link.data = artist.facebook_link
        form.image_link.data = artist.image_link
        form.website_link.data = artist.website_link
        form.seeking_venue.data = artist.seeking_venue
        form.seeking_description.data = artist.seeking_description

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    #edit artists form data in db table

    error = False
    artist = Artist.query.get(artist_id)

    try:
        artist.name = request.form['name']
        artist.city = request.form['city']
        artist.state = request.form['state']
        artist.phone = request.form['phone']
        artist.genres = request.form.getlist('genres')
        artist.facebook_link = request.form['facebook_link']
        artist.image_link = request.form['image_link']
        artist.website_link = request.form['website_link']
        artist.seeking_venue = True
        artist.seeking_description = request.form['seeking_description']

        db.session.commit()

    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())

    finally:
        db.session.close()

    if error:
        flash('An error occurred. Artist could not be changed.')
    else:
        flash('Artist was successfully updated!')

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)

    form.name.data = venue.name
    form.city.data = venue.city
    form.state.data = venue.state
    form.address.data = venue.address
    form.phone.data = venue.phone
    form.genres.data = venue.genres
    form.facebook_link.data = venue.facebook_link
    form.image_link.data = venue.image_link
    form.website_link.data = venue.website_link
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    #Edit location data in the db
    
    error = False
    venue = Venue.query.get(venue_id)

    try:

        venue.name = request.form['name']
        venue.city = request.form['city']
        venue.state = request.form['state']
        venue.address = request.form['address']
        venue.phone = request.form['phone']
        venue.genres = request.form['genres']
        venue.facebook_link = request.form['facebook_link']
        venue.image_link = request.form['image_link']
        venue.website_link = request.form['website_link']
        venue.seeking_talent = True
        venue.seeking_description = request.form['seeking_description']

        db.session.commit()

    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())

    finally:
        db.session.close()

    if error:
        flash('An error occurred. Venue could not be updated.')
    else:
        flash('Venue was successfully updated!')

    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # Add artists data in the db table 

    error = False
    try:
        data = request.form

        artist = Artist(
            name=data['name'],
            city=data['city'],
            state=data['state'],
            phone=data['phone'],
            genres=data['genres'],
            facebook_link=data['facebook_link'],
            image_link=data['image_link'],
            website_link=data['website_link'],
            seeking_description=data['seeking_description']
        )

        db.session.add(artist)
        db.session.commit()

    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())

    finally:
        db.session.close()

    if error == True:
        flash(f"An error occurred. Artist {data['name']} could not be listed.")
    else:
        flash(f"Artist {data['name']} was successfully listed!")

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    #All shows query
    shows = db.session.query(Show).join(Artist).join(Venue).all()
    data = []

    for show in shows:
        data.append({
            'venue_id': show.venue_id,
            'venue_name': show.venues.name,
            'artist_id': show.artist_id,
            'artist_name': show.artists.name,
            'artist_image_link': show.artists.image_link,
            'start_time': show.start_time
        })

    print(data)
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create', methods=['GET'])
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    error = False
    try:
        data = request.form
        show = Show(artist_id=data['artist_id'],
                    venue_id=data['venue_id'], start_time=data['start_time'])

        db.session.add(show)
        db.session.commit()

    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())

    finally:
        db.session.close()

    if error == True:
        flash(f"An error occurred.Show could not be listed.")
    else:
        flash(f"Show was successfully listed!")

    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
