#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import ARRAY
import logging
from flask_migrate import Migrate
from sqlalchemy import distinct
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy import Column
from forms import *
import sys

from model import Venue, Artist, Show
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'FALSE'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database (done)


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
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
  data = []
  try:
    venue_locations = db.session.query(distinct(Venue.city), Venue.state).all()
    for state in venue_locations:
      city = state[0]
      state = state[1]
      location = {"city": city, "state": state, "venues": []}
      venues = Venue.query.filter_by(city=city, state=state).all()
      for venue in venues:
        venue_name = venue.name
        venue_id = venue.id
        upcoming_shows = (Show.query.filter_by(venue_id=venue_id).all())
        venue_data = {
          "id": venue_id,
          "name": venue_name,
          "num_upcoming_shows": len(upcoming_shows)
          }
        location["venues"].append(venue_data)
        data.append(location)
  except:
        db.session.rollback()
        print(sys.exc_info())
        flash("Something went wrong. Please try again.")
        return render_template("pages/home.html")

  finally:
        return render_template("pages/venues.html", areas=data)
 #data=[{
   # "city": "San Francisco",
    #"state": "CA",
    #"venues": [{
     # "id": 1,
      #"name": "The Musical Hop",
      #"num_upcoming_shows": 0,
    #}, {
     # "id": 3,
      #"name": "Park Square Live Music & Coffee",
      #"num_upcoming_shows": 1,
    #}]
  #}, {
   # "city": "New York",
    #"state": "NY",
    #"venues": [{
     # "id": 2,
      #"name": "The Dueling Pianos Bar",
      #"num_upcoming_shows": 0,
    #}]
  #}]

  # TODO: replace with real venues data. (done)
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term', '')
  venues = db.session.query(Venue).filter(Venue.name.ilike('%' + search_term + '%')).all()
  data = []

  for venue in venues:
      num_upcoming_shows = 0
      shows = db.session.query(Show).filter(Show.venue_id == venue.id)
      for show in shows:
          if (show.start_time > datetime.now()):
              num_upcoming_shows += 1;

      data.append({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": num_upcoming_shows
      })

  response_data={
        "count": len(venues),
        "data": data
    }

  return render_template('pages/search_venues.html', results=response_data, search_term=request.form.get('search_term', ''))
#response={
   # "count": 1,
    #"data": [{
     # "id": 2,
      #"name": "The Dueling Pianos Bar",
    #  "num_upcoming_shows": 0,
#    }]
#  }
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.(done)
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = db.session.query(Venue).filter(Venue.id == venue_id).one()

  list_shows = db.session.query(Show).filter(Show.venue_id == venue_id)
  past_shows = []
  upcoming_shows = []

  for show in list_shows:
    artist = db.session.query(Artist.name, Artist.image_link).filter(Artist.id == show.artist_id).one()
    show_add = {
        "artist_id": show.artist_id,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        "start_time": show.start_time.strftime('%m/%d/%Y')
        }

    if (show.start_time < datetime.now()):
        #print(past_shows, file=sys.stderr)
        past_shows.append(show_add)
    else:
        upcoming_shows.append(show_add)

  data = {
      "id": venue.id,
      "name": venue.name,
      "genres": venue.genres,
      "address": venue.address,
      "city": venue.city,
      "state": venue.state,
      "phone": venue.phone,
      "website_link": venue.website_link,
      "facebook_link": venue.facebook_link,
      "seeking_talent": venue.seeking_talent,
      "seeking_description": venue.seeking_description,
      "image_link": venue.image_link,
      "past_shows": past_shows,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": len(past_shows),
      "upcoming_shows_count": len(upcoming_shows),
  }
  return render_template('pages/show_venue.html', venue=data)
  #  data1={
#    "id": 1,
#    "name": "The Musical Hop",
#    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
#    "address": "1015 Folsom Street",
#    "city": "San Francisco",
#    "state": "CA",
#    "phone": "123-123-1234",
 #   "website": "https://www.themusicalhop.com",
 #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
 #   "seeking_talent": True,
  #  "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
 #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
 #   "past_shows": [{
 #     "artist_id": 4,
  #    "artist_name": "Guns N Petals",
   #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #    "start_time": "2019-05-21T21:30:00.000Z"
  #  }],
  #  "upcoming_shows": [],
  #  "past_shows_count": 1,
  #  "upcoming_shows_count": 0,
  #}
  #data2={
  #  "id": 2,
   # "name": "The Dueling Pianos Bar",
   # "genres": ["Classical", "R&B", "Hip-Hop"],
 #   "address": "335 Delancey Street",
 #   "city": "New York",
 #   "state": "NY",
 #   "phone": "914-003-1132",
 #   "website": "https://www.theduelingpianos.com",
 #   "facebook_link": "https://www.facebook.com/theduelingpianos",
 #   "seeking_talent": False,
 #   "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
 #   "past_shows": [],
 #   "upcoming_shows": [],
 #   "past_shows_count": 0,
 #   "upcoming_shows_count": 0,
 # }
 # data3={
 #   "id": 3,
 #   "name": "Park Square Live Music & Coffee",
 #   "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
  #  "address": "34 Whiskey Moore Ave",
  #  "city": "San Francisco",
  #  "state": "CA",
 #   "phone": "415-000-1234",
 #   "website": "https://www.parksquarelivemusicandcoffee.com",
 #   "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
 #   "seeking_talent": False,
 #   "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
 #   "past_shows": [{
 #     "artist_id": 5,
 #     "artist_name": "Matt Quevedo",
  #    "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #    "start_time": "2019-06-15T23:00:00.000Z"
  #  }],
 #   "upcoming_shows": [{
 #     "artist_id": 6,
 #     "artist_name": "The Wild Sax Band",
 #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
 #     "start_time": "2035-04-01T20:00:00.000Z"
 #   }, {
 #     "artist_id": 6,
 #     "artist_name": "The Wild Sax Band",
 #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
 #     "start_time": "2035-04-08T20:00:00.000Z"
 #   }, {
 #     "artist_id": 6,
 #     "artist_name": "The Wild Sax Band",
 #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
 #     "start_time": "2035-04-15T20:00:00.000Z"
 #   }],
 #   "past_shows_count": 1,
 #   "upcoming_shows_count": 1,
 # }
 # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id(done)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  new_venue = VenueForm(request.form)

  venue = Venue(
    name = new_venue.name.data,
    genres = "".join(new_venue.genres.data),
    address = new_venue.address.data,
    city = new_venue.city.data,
    state = new_venue.state.data,
    phone = new_venue.phone.data,
    website_link = new_venue.website_link.data,
    facebook_link = new_venue.facebook_link.data,
    seeking_talent = new_venue.seeking_talent.data,
    seeking_description = new_venue.seeking_description.data,
    image_link = new_venue.image_link.data
  )
  try:
      db.session.add(venue)
      db.session.commit()
      # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be added.')
  finally:
      db.session.close()
  return render_template('pages/home.html')
      

  # TODO: insert form data as a new Venue record in the db, instead (done)
  # TODO: modify data to be the data object returned from db insertion (done)

  # on successful db insert, flash success(done)
  # TODO: on unsuccessful db insert, flash an error instead.(done)
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
        db.session.query(Venue).filter(Venue.id == venue_id).delete()
        db.session.commit()
        flash('Venue was successfully deleted!')
  except:
        flash('An error occurred. Venue could not be deleted.')
        db.session.rollback()
        return render_template('pages/home.html')
  finally:
        db.session.close()
        return render_template('pages/home.html')
  
  # TODO: Complete this endpoint for taking a venue_id, and using(done)
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage (done)
  
#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
   artists = db.session.query(Artist.id, Artist.name)
   artist_data=[]

   for artist in artists:
      artist_data.append({
        "id": artist[0],
        "name": artist[1]
      })
   return render_template('pages/artists.html', artists=artist_data)
    # data=[{
  #  "id": 4,
#    "name": "Guns N Petals",
#  }, {
#    "id": 5,
#    "name": "Matt Quevedo",
#  }, {
#    "id": 6,
#    "name": "The Wild Sax Band",
#  }]
#  return render_template('pages/artists.html', artists=data)


  # TODO: replace with real data returned from querying the database (done)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term', '')
  artists = db.session.query(Artist).filter(Artist.name.ilike('%' + search_term + '%')).all()
  artist_data = []

  for artist in artists:
        num_upcoming_shows = 0
        shows = db.session.query(Show).filter(Show.artist_id == artist.id)
        for show in shows:
            if(show.start_time > datetime.now()):
                num_upcoming_shows += 1;
        artist_data.append({
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": num_upcoming_shows
        })
  response={
        "count": len(artists),
        "data": artist_data
    }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

 # response={
 #   "count": 1,
 #   "data": [{
 #     "id": 4,
 #     "name": "Guns N Petals",
 #     "num_upcoming_shows": 0,
 #   }]
 # }
 # return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive. (done)
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = db.session.query(Artist).filter(Artist.id == artist_id).one()
  list_shows = db.session.query(Show).filter(Show.artist_id == artist_id)
  past_shows = []
  upcoming_shows = []
  for show in list_shows:
    venue = db.session.query(Venue.name, Venue.image_link).filter(Venue.id == show.venue_id).one()
    show_add = {
            "venue_id": show.venue_id,
            "venue_name": venue.name,
            "venue_image_link": venue.image_link,
            "start_time": show.start_time.strftime('%m/%d/%Y')
            }
    if (show.start_time < datetime.now()):
            past_shows.append(show_add)
    else:
            print(show_add, file=sys.stderr)
            upcoming_shows.append(show_add)
    artist_data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website_link": artist.website_link,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venues,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows)
    }

    return render_template('pages/show_artist.html', artist=artist_data)
    # data1={
 #   "id": 4,
 #   "name": "Guns N Petals",
 #   "genres": ["Rock n Roll"],
 #   "city": "San Francisco",
 #   "state": "CA",
 #   "phone": "326-123-5000",
 #   "website": "https://www.gunsnpetalsband.com",
 #   "facebook_link": "https://www.facebook.com/GunsNPetals",
 #   "seeking_venue": True,
 #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
 #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
 #   "past_shows": [{
 #     "venue_id": 1,
 #     "venue_name": "The Musical Hop",
 #     "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
 #     "start_time": "2019-05-21T21:30:00.000Z"
 #   }],
 #   "upcoming_shows": [],
 #   "past_shows_count": 1,
 #   "upcoming_shows_count": 0,
 # }
 # data2={
 #   "id": 5,
 #   "name": "Matt Quevedo",
 #   "genres": ["Jazz"],
 #   "city": "New York",
 #   "state": "NY",
 #   "phone": "300-400-5000",
 #   "facebook_link": "https://www.facebook.com/mattquevedo923251523",
 #   "seeking_venue": False,
 #   "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
 #   "past_shows": [{
 #     "venue_id": 3,
 #     "venue_name": "Park Square Live Music & Coffee",
 #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
 #     "start_time": "2019-06-15T23:00:00.000Z"
 #   }],
 #   "upcoming_shows": [],
 #   "past_shows_count": 1,
 #   "upcoming_shows_count": 0,
 # }
 # data3={
 #   "id": 6,
 #   "name": "The Wild Sax Band",
 #   "genres": ["Jazz", "Classical"],
 #   "city": "San Francisco",
 #   "state": "CA",
 #   "phone": "432-325-5432",
 #   "seeking_venue": False,
 #   "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
 #   "past_shows": [],
 #   "upcoming_shows": [{
 #     "venue_id": 3,
 #     "venue_name": "Park Square Live Music & Coffee",
 #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
 #     "start_time": "2035-04-01T20:00:00.000Z"
 #   }, {
 #     "venue_id": 3,
 #     "venue_name": "Park Square Live Music & Coffee",
 #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
 #     "start_time": "2035-04-08T20:00:00.000Z"
 #   }, {
 #     "venue_id": 3,
 #     "venue_name": "Park Square Live Music & Coffee",
 #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
 #     "start_time": "2035-04-15T20:00:00.000Z"
 #   }],
 #   "past_shows_count": 0,
 #   "upcoming_shows_count": 3,
 #}
 # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  # shows the artist page with the given artist_id(done)
  # TODO: replace with real artist data from the artist table, using artist_id (done)
  
#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = db.session.query(Artist).filter(Artist.id == artist_id).one()
  form.name.data = artist.name
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.facebook_link.data = artist.facebook_link
  form.image_link.data = artist.image_link
  form.website_link.data = artist.website_link
  form.genres.data = artist.genres
  form.seeking_venues.data = artist.seeking_venues
  form.seeking_description.data = artist.seeking_description
   # form = ArtistForm()
 # artist={
 #   "id": 4,
 #   "name": "Guns N Petals",
 #   "genres": ["Rock n Roll"],
 #   "city": "San Francisco",
 #   "state": "CA",
 #   "phone": "326-123-5000",
 #   "website": "https://www.gunsnpetalsband.com",
 #   "facebook_link": "https://www.facebook.com/GunsNPetals",
 #   "seeking_venue": True,
 #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
 #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
 # }
  return render_template('forms/edit_artist.html', form=form, artist=artist)
  # TODO: populate form with fields from artist with ID <artist_id> (done)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  form = ArtistForm(request.form)
  artist = db.session.query(Artist).filter(Artist.id == artist_id).one()

  update_artist = {
        'name': form.name.data,
        'city': form.city.data,
        'state': form.state.data,
        'phone': form.phone.data,
        'genres': "".join(form.genres.data),
        'website_link': form.website_link.data,
        'facebook_link': form.facebook_link.data,
        'seeking_venues': form.seeking_venues.data,
        'seeking_description': form.seeking_description.data,
        'image_link': form.image_link.data,
    }
  try:
        db.session.query(Artist).filter(Artist.id == artist_id).update(update_artist)
        db.session.commit()
        flash('Artist ' + form.name.data + ' was successfully listed!')
  except:
        flash('An error occurred. Artist ' + form.name.data + 'could not be added')
  finally:
        db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

  # TODO: take values from the form submitted, and update existing (done)
  # artist record with ID <artist_id> using the new attributes

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = db.session.query(Venue).filter(Venue.id == venue_id).one()
  form.name.data = venue.name
  form.city.data = venue.city
  form.state.data = venue.state
  form.phone.data = venue.phone
  form.address.data = venue.address
  form.facebook_link.data = venue.facebook_link
  form.image_link.data = venue.image_link
  form.website_link.data = venue.website_link
  form.genres.data = venue.genres
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_description.data = venue.seeking_description
  # TODO: populate form with values from venue with ID <venue_id> (done)
  #  form = VenueForm()
#  venue={
#    "id": 1,
#    "name": "The Musical Hop",
#    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
#    "address": "1015 Folsom Street",
#    "city": "San Francisco",
#    "state": "CA",
#    "phone": "123-123-1234",
#    "website": "https://www.themusicalhop.com",
#    "facebook_link": "https://www.facebook.com/TheMusicalHop",
#    "seeking_talent": True,
#    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
#    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
#  }
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  form = VenueForm(request.form)
  if form.delete.data:
    return redirect(url_for(delete_venue, id=id))
  venue = db.session.query(Venue).filter(Venue.id == venue_id).one()

  updated_venue = {
        'name': form.name.data,
        'city': form.city.data,
        'state': form.state.data,
        'address': form.address.data,
        'phone': form.phone.data,
        'genres': "".join(form.genres.data),
        'website_link': form.website_link.data,
        'facebook_link': form.facebook_link.data,
        'seeking_talent': form.seeking_talent.data,
        'seeking_description': form.seeking_description.data,
        'image_link': form.image_link.data,
    }
  try:
        db.session.query(Venue).filter(Venue.id == venue_id).update(updated_venue)
        db.session.commit()
        flash('Venue' + form.name.data + ' was successfully updated!')
  except:
        flash('An error occurred. Venue ' + form.name.data + ' could not be updated.')
  finally:
        db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

  # TODO: take values from the form submitted, and update existing(done)
  # venue record with ID <venue_id> using the new attributes

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  new_artist = ArtistForm(request.form)

  artist = Artist(
    name = new_artist.name.data,
    genres = "".join(new_artist.genres.data),
    city = new_artist.city.data,
    state = new_artist.state.data,
    phone = new_artist.phone.data,
    website_link = new_artist.website_link.data,
    facebook_link = new_artist.facebook_link.data,
    seeking_venues = new_artist.seeking_venues.data,
    seeking_description = new_artist.seeking_description.data,
    image_link = new_artist.image_link.data
  )
  try:
      db.session.add(artist)
      db.session.commit()
      # on successful db insert, flash success (done)
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be added.')
  finally:
      db.session.close()
  return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  data = []
  shows = db.session.query(Show.artist_id, Show.venue_id, Show.start_time).all()

  for show in shows:
        artist = db.session.query(Artist.name, Artist.image_link).filter(Artist.id == show[0]).one()
        venue = db.session.query(Venue.name).filter(Venue.id == show[1]).one()
        data.append({
            "venue_id": show[1],
            "venue_name": venue[0],
            "artist_id": show[0],
            "artist_name": artist[0],
            "artist_image_link": artist[1],
            "start_time": str(show[2])
        })
  return render_template('pages/shows.html', shows=data)
  # displays list of shows at /shows
  # TODO: replace with real venues data. (done)
  
@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  new_show = ShowForm(request.form)

  show = Show(
    artist_id = new_show.artist_id.data,
    venue_id = new_show.venue_id.data,
    start_time = new_show.start_time.data
  )
  try:
      db.session.add(show)
      db.session.commit()
      # on successful db insert, flash success (done)
      flash('Show  was successfully listed!')
  except:
      flash('An error occurred. Show  could not be added.')
  finally:
      db.session.close()
  return render_template('pages/home.html')
  # called to create new shows in the db, upon submitting new show listing form (done)
  # TODO: insert form data as a new Show record in the db, instead (done)
  #  data=[{
#    "venue_id": 1,
#    "venue_name": "The Musical Hop",
#    "artist_id": 4,
#    "artist_name": "Guns N Petals",
#    "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
#    "start_time": "2019-05-21T21:30:00.000Z"
#  }, {
#    "venue_id": 3,
#    "venue_name": "Park Square Live Music & Coffee",
#    "artist_id": 5,
#    "artist_name": "Matt Quevedo",
#    "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
#    "start_time": "2019-06-15T23:00:00.000Z"
#  }, {
#    "venue_id": 3,
#    "venue_name": "Park Square Live Music & Coffee",
#    "artist_id": 6,
#    "artist_name": "The Wild Sax Band",
#    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
#    "start_time": "2035-04-01T20:00:00.000Z"
#  }, {
#    "venue_id": 3,
#    "venue_name": "Park Square Live Music & Coffee",
#    "artist_id": 6,
#    "artist_name": "The Wild Sax Band",
#    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
#    "start_time": "2035-04-08T20:00:00.000Z"
#  }, {
#    "venue_id": 3,
#    "venue_name": "Park Square Live Music & Coffee",
#    "artist_id": 6,
#    "artist_name": "The Wild Sax Band",
#    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
#    "start_time": "2035-04-15T20:00:00.000Z"
#  }]

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead. (done)
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
