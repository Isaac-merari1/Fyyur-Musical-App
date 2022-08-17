#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import sys
import dateutil.parser
import babel
from flask import (
Flask,
render_template,
request, 
Response,
flash, 
redirect,
url_for
)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import app, db, Venue, Artist, Show
from config import DatabaseURI
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

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
  venues = Venue.query.order_by(desc(Venue.created_date)).limit(10).all()
  artists = Artist.query.order_by(desc(Artist.created_date)).limit(10).all()
  return render_template('pages/home.html', venues=venues, artists=artists)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  data = []
  Venues = venue.query.all(),
  venueData = []

  for eachVenue in venueData:
    data.append({
      "city": Venues.city,
      "state": Venues.state,
      "venues": []
    })

  for venue in Venues:
    num_upcoming_shows = 0
    presentDate=  str(datetime.today())
    shows = Show.query.filter_by(venue_id=venue.id).all()
    for show in shows:
      if show.start_time > presentDate:
        num_upcoming_shows +=1

    for finalData in data:
      if venue.city == finalData['city'] and venue.state == finalData['state']:
        finalData['venues'].append({
          "id": venue.id,
          "name": venue.name,
          "num_upcoming_shows": num_upcoming_shows
        })
    
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  venues = Venue.query.all()
  venueData = []

  for venue in venues:
    venueData.append({
      'id': venue.id,
      'name': venue.name,
      'num_upcoming_shows': 0
    })

  response = {
    "count": len(venues),
    'data': venueData
  }
  print(sys.exc_info())
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):

  venues = Venue.query.get(venue_id)
  pastData =[]
  upcomingData=[]
  dataList=[]
  pastShowsData = db.session.query(Show).join(Venue).filter(Show.venue_id==venue_id).filter(Show.start_time < str(datetime.today())).all()
  upcomingShowsData= db.session.query(Show).join(Venue).filter(Show.venue_id==venue_id).filter(Show.start_time >= str(datetime.today())).all()

  for data in pastShowsData:
    pastShow = Artist.query.get(data.artist_id)
    past = {
      "artist_id":pastShow.id,
      "artist_name":pastShow.name,
      "artist_image_link":pastShow.image_link,
      "artist_time":data.artist_id,
      "start_time":data.start_time
    }
    pastData.append(past)

  for data in upcomingShowsData:
    upcomingShow = Artist.query.get(data.artist_id)
    upcoming = {
      "artist_id":upcomingShow.id,
      "artist_name":upcomingShow.name,
      "artist_image_link":upcomingShow.image_link,
      "start_time":data.artist_id,
      "start_time":data.start_time
    }
    upcomingData.append(upcoming)

  dataObj = {
    'id':venues.id,
    'name':venues.name,
    'genres':venues.genres,
    'address':venues.address,
    'city':venues.city,
    'state':venues.state,
    'phone':venues.phone,
    'website_link':venues.website_link,
    'facebook_link':venues.facebook_link,
    'seeking_talent':venues.seeking_talent,
    'seeking_description':venues.seeking_description,
    'image_link':venues.image_link,
    'past_shows':pastData,
    'upcoming_shows':upcomingData,
    'past_shows_count':len(pastData),
    'upcoming_shows_count':len(upcomingData)
  }
  dataList.append(dataObj)
  data = list(filter(lambda d: d['id'] == venue_id, dataList))[0]
  print(sys.exc_info())
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  try:
    form = VenueForm(request.form)
    name = form.name.data,
    city = form.city.data,
    state = form.state.data,
    address = form.address.data,
    phone = form.phone.data,
    image_link = form.image_link.data,
    facebook_link = form.facebook_link.data
    genres = form.genres.data
    venue = venue(name=name,city=city,state=state,address=address,phone=phone,
            image_link=image_link,facebook_link=facebook_link,genres=genres)
    db.session.add(venue)
    db.session.comit()
  # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('Unable to create venue submission  ' + request.form['name'] + ' cannot be create!')
  finally:
    db.session.close()

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  try:
      Venue.query.filter_by(id=venue_id).delete()
      db.session.commit()
  except:
      db.session.rollback()
      print(sys.exc_info())
  finally:
      db.session.close()
  return jsonify({'success': True})

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data=[{
    "id": 4,
    "name": "Guns N Petals",
  }, {
    "id": 5,
    "name": "Matt Quevedo",
  }, {
    "id": 6,
    "name": "The Wild Sax Band",
  }]
  print(sys.exc_info())
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  artists = Artist.query.filter(Artist.id).all()
  data =[]

  for artist in artists:
    data.append({
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": 0
    })

  response={
    "count": len(artists),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
 
  artists = Artist.query.get(artist_id)
  pastData =[]
  upcomingData=[]
  dataList=[]
  pastShowsData = db.session.query(Show).join(Artist).filter(Show.artist_id==artist_id).filter(Show.start_time < str(datetime.today())).all()
  upcomingShowsData= db.session.query(Show).join(Artist).filter(Show.artist==artist_id).filter(Show.start_time >= str(datetime.today())).all()

  for data in pastShowsData:
    pastShow = Venue.query.get(data.venue_id)
    past = {
      "venue_id":pastShow.id,
      "venue_name":pastShow.name,
      "venue_image_link":pastShow.image_link,
      "start_time":data.start_time
    }
    pastData.append(past)

  for data in upcomingShowsData:
    upcomingShow = Venue.query.get(data.artist_id)
    upcoming = {
      "venue_id":upcomingShow.id,
      "venue_name":upcomingShow.name,
      "venue_image_link":upcomingShow.image_link,
      "start_time":data.start_time
    }
    upcomingData.append(upcoming)
  
  dataObj = {
    "id": artists.id,
    "name": artists.name,
    "genres": artists.genres,
    "city": artists.city,
    "state": artists.state,
    "phone": artists.phone,
    "website_link": artists.website_link,
    "facebook_link": artists.facebook_link,
    "seeking_venue": artists.seeking_venue,
    "seeking_description": artists.seeking_description,
    "image_link": artists.image_link,
    'past_shows':pastData,
    'upcoming_shows':upcomingData,
    'past_shows_count':len(pastData),
    'upcoming_shows_count':len(upcomingData)
  }
  dataList.append(dataObj)
  data = list(filter(lambda d: d['id'] == artist_id, dataList))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()

  artists = Artist.query.filter_by(id=artist_id).first()

  artist={
    'id': artists.id,
    'name': artists.name,
    'genres': artists.genre,
    'city': artists.city,
    'state': artists.state,
    'phone': artists.phone,
    "website_link": artists.website_link,
    'facebook_link': artists.facebook_link,
    'seeking_venue': artists.seeking_venue,
    'seeking_description': artists.seeking_description,
    'image_link': artists.image_link
  }
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

  try:
    form = ArtistForm()
    artists =Artist.query.filter_by(id=artist_id).first()

    artists.name = artist_id,
    artists.city = form.name.data,
    artists.state = form.genres.data,
    artists.phone = form.city.data,
    artists.genres =form.state.data,
    artists.facebook= form.phone.data,
    artists.website= form.website_link.data,
    artists = form.facebook_link.data,
    artists.seeking_venue = form.seeking_venue.data,
    artists.seeking_description = form.seeking_description.data,
    artists.image_link = form.image_link.data
    

    db.session.commit()
    flash('Artist' + request.form['name'] + 'was successfully updated!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occured. Artist' + request.form['name'] + 'could not be updated!')
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    'id': venue_id,
    'name': venue.name,
    'genres': venue.genre,
    'address': venue.address,
    'city': venue.city,
    'state': venue.state,
    'phone': venue.phone,
    'website_link': venue.website_link,
    'facebook_link': venue.facebook_link,
    'seeking_talent': venue.seeking_talent,
    'seeking_description': venue.seeking_description,
    'image_link': venue.image_link
  }

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  try:
    form = VenueForm(request.form)

    venue =Venue.query.filter_by(id=artist_id).first()

    venue.name = form.name.data
    venue.city = form.city.data
    venue.state = form.state.data
    venue.phone = form.phone.data
    venue.genres = form.genres.data
    venue.facebook_link = form.facebook_link.data
    venue.website_link = form.website_link.data
    venue.image_link = form.image_link.data
    venue.seeking_venue = form.seeking_venue.data
    venue.seeking_description = form.seeking_description.data

    db.session.commit()
    flash('Venue' + request.form['name'] + 'was successfully updated!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occured editing Venue' + request.form['name'] + 'could not be updated!')
  finally:
    db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
   try:
    form = ArtistForm(request.form)
    name = form.name.data
    city = form.city.data
    state = form.state.data
    phone = form.phone.data
    genres = form.genres.data
    facebook_link = form.facebook_link.data
    website_link = form.website_link.data
    image_link = form.image_link.data
    seeking_venue = form.seeking_venue.data
    seeking_description = form.seeking_description.data

    artist = Artist(name=name, city=city, state=state, phone=phone,
    genres=genres, facebook_link=facebook_link,
    website_link=website_link, image_link=image_link,
    seeking_venue=seeking_venue,seeking_description=seeking_description)

    db.session.add(artist)
    db.session.commit()
  # on successful db insert form = ArtistForm(request.form)
    name = form.name.data
    city = form.city.data
    state = form.state.data
    phone = form.phone.data
    genres = form.genres.data
    facebook_link = form.facebook_link.data
    website_link = form.website_link.data
    image_link = form.image_link.data
    seeking_venue = form.seeking_venue.data
    seeking_description = form.seeking_description.data

    artist = Artist(name=name, city=city, state=state, phone=phone,
    genres=genres, facebook_link=facebook_link,
    website_link=website_link, image_link=image_link,
    seeking_venue=seeking_venue,seeking_description=seeking_description)
  
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
   except:
    print(sys.exc_info())
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
   finally:
    db.session.close()

   return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  shows = show.query.order_by('start_time').all()
  artist = Artist.query.filter_by(id=show.artist_id).first()
  venue = Venue.query.filter_by(id=show.artist_id).first()
  data = []
  for show in shows:
    data.append({
      "venue_id": show.venue_id,
      "venue_name": venue.name,
      "artist_id": show.artist_id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": show.start_time
    })

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():

  try:
    form = ShowForm(request.form)
    artist_id = form.artist_id
    venue_id = form.venue_id
    start_time = form.start_time

    show = Show(artist_id=artist_id, venue_id=venue_id,start_time=start_time)
    db.session.add(show)
    db.session.commit()
  # on successful db insert, flash success
    flash('Show was successfully listed!')

  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()  

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
