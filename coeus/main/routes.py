from flask import Blueprint, request, render_template
from flask_login import current_user, login_required
from coeus.models import Post
from coeus import gmaps
import uuid
import jsonify
import json

sesstoken = uuid.uuid4()

main = Blueprint('main', __name__)
@main.route('/')
@main.route('/home')
def home():
    #Pagination
    page = request.args.get('page', 1, type = int) #get args, default page is 1, type is int for page #http://127.0.0.1:5000/home?page=1
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(per_page = 5, page = page)
    return render_template('start.html', posts=posts)

@main.route('/about')
def about():
    return render_template('about.html', title = 'About')

@main.route('/initialize_search', methods=["GET", "POST"])
@login_required
def initialize_search():
    print(sesstoken)

    return render_template('initialize_search.html', title = 'Initialize')

@main.route('/livesearch', methods=["GET", "POST"])
@login_required
def livesearch():
    data = request.form.get("text")
    google_return = gmaps.places_autocomplete(input_text = str(data), session_token = sesstoken, language = "en", types = "establishment", components = {'country': ['US', 'CA']},  strict_bounds = False)
    google_list = {}
    count = 0
    for item in google_return:
        count+=1
        google_list[str(count)] = {'description': item['description'], 
                                   'place_id': item['place_id'],
                                   'main_text':item['structured_formatting']['main_text'],
                                   'city': item['terms'][-3]['value'],
                                   'state': item['terms'][-2]['value'],
                                   'country': item['terms'][-1]['value']}
    count = 0
    return google_list

@main.route('/hotels_nearby', methods=["POST"])
@login_required
def hotels_nearby():
    global sesstoken
    
    #details of selected location from initialize_search page
    location_search2 = request.form['location_search2']
    location_description = request.form['location_description']
    location_placeid = request.form['location_placeid']
    location_city = request.form['location_city']
    location_state = request.form['location_state']
    location_country = request.form['location_country']

    #Use this code to check if city has been previously added, if not, use a query of nearby to log. Need to create a SQL Database eventually
    db_query_city = "" + str(location_city) + "-" + str(location_state) + "-" + str(location_country)

    #Details for location search from prior. Mainly for lat, long and photo for front end (later)
    detail_fields = ["geometry", "icon", "name", "photo", "place_id"]
    detail_language = "en"
    print(sesstoken)
    detail_result = gmaps.place(place_id = str(location_placeid), session_token = sesstoken, fields = detail_fields, language = detail_language)
    
    # print(detail_result)
    #Needed Items for result in hotels_list results
    longitude = detail_result["result"]["geometry"]["location"]["lng"]
    latitude = detail_result["result"]["geometry"]["location"]["lat"]
    location_nearby = str(latitude)+ "," + str(longitude)
    
    #Create a new session id for the next instance of search
    sesstoken = uuid.uuid4()
    
    #Print Hotels Nearly
    hotels_list = gmaps.places_nearby(location = location_nearby, radius = 5000, language = detail_language, type = "lodging")
    count = 0
    master_dict = []
    while ("next_page_token" in hotels_list) and count < 2:
        count+=1
        for each in hotels_list["results"]:
            current_hotel_dict = {}
            

            print(each)
            
    
    return render_template('hotels_nearby.html', title = 'Hotels Nearby', location_search2 = location_search2,
                            location_description = location_description, location_placeid = location_placeid, 
                            location_city = location_city, location_state = location_state, location_country = location_country )


