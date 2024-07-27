import os

from flask import Flask,session,redirect,request,render_template,jsonify,after_this_request
import requests
import numpy as np
import pandas as pd


from datetime import datetime,date,timedelta

import json
 
user_activity_data = {}

USER_DATA_PATH = "test.json"
try:
    with open(USER_DATA_PATH, 'r') as f:
        # Reading from json file
        user_activity_data = json.load(f)
except FileNotFoundError as e:
    pass

def dump_to_file():
    with open(USER_DATA_PATH, 'w') as f:
        f.write(json.dumps(user_activity_data,indent=4))

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.secret_key = 'hi'

    @app.route('/',methods=["GET"])
    def main():
        # if not already logged in: 
        return render_template("/login.html")
    
    @app.route('/home')
    def home():
        return render_template("home.html")

    @app.route('/login.html',methods=["GET"])
    def login():
        print(session.get('access_token'))
        if session.get('access_token') == None or session.get('access_token') not in user_activity_data:
            return redirect('http://www.strava.com/oauth/authorize?client_id=117096&response_type=code&redirect_uri=http://127.0.0.1:5000/hello&approval_prompt=force&scope=read_all,activity:read_all')
        else:
            return redirect("/me")

    @app.route('/hello')
    def hello():
        user_code = request.args.get('code')
        req = requests.post("https://www.strava.com/api/v3/oauth/token", json={"client_id": "117096", "client_secret": "ca6bda0bcd120f49c2c540e656b8741204cf5ef7", "code": user_code, "grant_type": "authorization_code"})
        access_token = req.json().get('access_token')
        if access_token is not None:
            session['access_token'] = access_token
            
            headers = {
                "Authorization": f"Bearer {access_token}"
            }
            response = requests.get("https://www.strava.com/api/v3/athlete", headers=headers)
            data = response.json()
            session['firstname'] = data.get('firstname')
            
            load_user_activities()
            return redirect("/me")
        else:
            return redirect("/")

    @app.route('/me')
    def me():
        try:
            access_token = session['access_token']
            if(len(user_activity_data[access_token]) > 0):
                return render_template("home.html")
            else:
                return redirect('/logout')
        except KeyError:
            return redirect("/")
        
    @app.route('/activitytypeinfo')
    def activitytypeinfo():
        return render_template("main.html")

    @app.route('/reload')
    def reload():
        del user_activity_data[session.get('access_token')]
        load_user_activities();
        dump_to_file();
        return redirect("/me")

    @app.route('/logout')
    def logout():
        session.pop('access_token', default=None)
        session.pop('firstname', default=None)
        return render_template("logout.html")

    
    @app.route('/about')
    def about():
        return render_template("about_us.html")
    
    @app.route('/career')
    def career():
        return render_template("career.html")
    
    @app.route('/yearlyinfo')
    def yearlyinfo():
        return render_template("yearly.html")
    
    @app.route('/yearlypieinfo')
    def yearlypieinfo():
        return render_template("pieByYear.html")
    
    def load_user_activities():
        access_token = session['access_token']
        try:
            user_activity_data[access_token]
            return
        except KeyError:
            pass

        epoch_year = 31556926  
        start_year = 2009
        start_year_epoch = 1230768000  # January 1, 2009

        current_year = date.today().year
        json_data = []

        for year_index in range(start_year, current_year + 1):
            start_epoch = start_year_epoch + epoch_year * (year_index - start_year)
            end_epoch = start_epoch + epoch_year

            i = 1
            while True:
                print(f"Fetching data from {datetime.utcfromtimestamp(start_epoch)} to {datetime.utcfromtimestamp(end_epoch)}, page {i}")
                response = requests.get(
                    f"https://www.strava.com/api/v3/activities?before={end_epoch}&after={start_epoch}&access_token={access_token}&per_page=200&page={i}"
                )
                data = response.json()
                if not data:
                    break
                json_data.extend(data)
                i += 1
                if len(data) < 200:
                    break

        user_activity_data[access_token] = json_data
        dump_to_file()

    #function to find the oldest year with data for dropdowns on frontend
    @app.route('/me/years_with_data')
    def years_with_data():
        access_token = session['access_token']
        json_data = user_activity_data.get(access_token, [])
        years = sorted(set(activity['start_date_local'][:4] for activity in json_data))
        return jsonify(years)


    @app.route('/me/user_info')
    def get_user_info():
        access_token = session['access_token']
        if session.get('firstname') is None:
            headers = {
                "Authorization": f"Bearer {access_token}"
            }
            response = requests.get("https://www.strava.com/api/v3/athlete", headers=headers)
            data = response.json()
            session['firstname'] = data.get('firstname')
        return jsonify({"firstname": session.get('firstname')})

    @app.route('/me/yearly_data',methods=["GET"])
    def yearly_data():
        @after_this_request
        def add_header(response):
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
        access_token = session['access_token']
        activity_type = request.args.get('type', default=None)

        start_year = 2009
        current_date = date.today()
        current_year = current_date.year
        json_data = user_activity_data[access_token]
        current_day_of_year = current_date.timetuple().tm_yday

        first_year_with_data = current_year
        for activity in json_data:
            activity_year = int(activity['start_date_local'][:4])
            if activity_year < first_year_with_data:
                first_year_with_data = activity_year

        blank_data = []
        for i in range(current_year - first_year_with_data + 1):
            blank_data.append([0] * 366)
        result = {"data": blank_data}

        for activity in json_data:
            if activity["type"] == activity_type or activity_type is None:
                activity_date = activity['start_date_local']
                activity_epoch = date(int(activity_date[0:4]), int(activity_date[5:7]), int(activity_date[8:10]))

                beginning_of_year = date(activity_epoch.year, 1, 1)
                deltas = activity_epoch - beginning_of_year

                years_since_start_year = activity_epoch.year - first_year_with_data
                day_of_year = deltas.days

                distance = activity['distance'] / 1000
                result['data'][years_since_start_year][day_of_year] += distance

        for index in range(current_year - first_year_with_data + 1):
            result['data'][index] = list(np.cumsum(result['data'][index]))
            for i in range(366):
                result['data'][index][i] = "{:.2f}".format(result['data'][index][i])

        return jsonify(result)
    
    @app.route('/me/pie_data_count')
    def pie_data_count():
        @after_this_request
        def add_header(response):
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response

        access_token = session['access_token']
        json_data = user_activity_data[access_token]
        year = request.args.get('year', default=None, type=int)

        activity_counts = {}
        for activity in json_data:
            activity_year = int(activity['start_date_local'][:4])
            if year is None or activity_year == year:
                activity_type = activity.get('type', 'Unknown')
                if activity_type in activity_counts:
                    activity_counts[activity_type] += 1
                else:
                    activity_counts[activity_type] = 1

        result = [{"type": activity_type, "count": count} for activity_type, count in activity_counts.items()]

        return jsonify(result)
   
    @app.route('/me/pie_data_time')
    def pie_data_time():
        @after_this_request
        def add_header(response):
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response

        access_token = session['access_token']
        json_data = user_activity_data[access_token]
        year = request.args.get('year', default=None, type=int)

        activity_time = {}
        for activity in json_data:
            activity_year = int(activity['start_date_local'][:4])
            if year is None or activity_year == year:
                activity_type = activity.get('type', 'Unknown')
                moving_time_hours = activity.get('moving_time', 0) / 3600
                if activity_type in activity_time:
                    activity_time[activity_type] += moving_time_hours
                else:
                    activity_time[activity_type] = moving_time_hours

        result = [{"type": activity_type, "time": round(time, 2)} for activity_type, time in activity_time.items()]

        return jsonify(result) 

    @app.route('/me/pie_data_distance')
    def pie_data_distance():
        @after_this_request
        def add_header(response):
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response

        access_token = session['access_token']
        json_data = user_activity_data[access_token]
        year = request.args.get('year', default=None, type=int)

        activity_distance = {}
        for activity in json_data:
            activity_year = int(activity['start_date_local'][:4])
            if year is None or activity_year == year:
                activity_type = activity.get('type', 'Unknown')
                totalDistance = activity.get('distance', 0) / 1000
                if activity_type in activity_distance:
                    activity_distance[activity_type] += totalDistance
                else:
                    activity_distance[activity_type] = totalDistance

        result = [{"type": activity_type, "distance": distance} for activity_type, distance in activity_distance.items()]

        return jsonify(result)
    
    @app.route('/me/pie_data_kudos')
    def pie_data_kudos():
        @after_this_request
        def add_header(response):
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response

        access_token = session['access_token']
        json_data = user_activity_data[access_token]
        year = request.args.get('year', default=None, type=int)

        activity_kudos = {}
        for activity in json_data:
            activity_year = int(activity['start_date_local'][:4])
            if year is None or activity_year == year:
                activity_type = activity.get('type', 'Unknown')
                totalKudos = activity.get('kudos_count', 0)
                if totalKudos > 0:
                    if activity_type in activity_kudos:
                        activity_kudos[activity_type] += totalKudos
                    else:
                        activity_kudos[activity_type] = totalKudos

        result = [{"type": activity_type, "kudos": kudos} for activity_type, kudos in activity_kudos.items()]

        return jsonify(result) 


    @app.route('/me/pie_data_elevation', methods=["GET"])
    def pie_data_elevation():
        @after_this_request
        def add_header(response):
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
        
        access_token = session['access_token']
        json_data = user_activity_data[access_token]
        year = request.args.get('year', default=None, type=int)

        activity_elevation = {}
        for activity in json_data:
            activity_year = int(activity['start_date_local'][:4])
            if year is None or activity_year == year:
                activity_type = activity.get('type', 'Unknown')
                totalElevation = activity.get('total_elevation_gain', 0)
                if totalElevation > 0:
                    if activity_type in activity_elevation:
                        activity_elevation[activity_type] += totalElevation
                    else:
                        activity_elevation[activity_type] = totalElevation
        
        result = [{"type": activity_type, "elevation": elevation} for activity_type, elevation in activity_elevation.items()]

        return jsonify(result)


    @app.route('/me/yearly_time', methods=["GET"])
    def yearly_time():
        @after_this_request
        def add_header(response):
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response

        access_token = session['access_token']
        json_data = user_activity_data[access_token]

        start_year = 2020
        current_date = date.today()
        current_year = current_date.year

        # populate empty lists
        blank_data = []
        for i in range(current_year - start_year + 1):
            blank_data.append([0] * 366)  # 366 to account for leap years
        result = {"data": blank_data}

        for activity in json_data:
            activity_date = activity['start_date_local']
            activity_epoch = date(int(activity_date[0:4]), int(activity_date[5:7]), int(activity_date[8:10]))

            beginning_of_year = date(activity_epoch.year, 1, 1)
            day_of_year = (activity_epoch - beginning_of_year).days

            years_since_start_year = activity_epoch.year - start_year

            #count time
            time_hours = activity['moving_time'] / 3600
            result['data'][years_since_start_year][day_of_year] += time_hours

        for index in range(current_year - start_year + 1):
            result['data'][index] = list(np.cumsum(result['data'][index]))

            for i in range(366):
                # round to %.2f
                result['data'][index][i]="{:.2f}".format(result['data'][index][i])

        return jsonify(result)


    # @app.route('/me/monthly_dist_grouped')
    # def monthly_dist_grouped():
    #     @after_this_request
    #     def add_header(response):
    #         response.headers.add('Access-Control-Allow-Origin', '*')
    #         return response

    #     #get data
    #     access_token = session['access_token']
    #     json_data = user_activity_data[access_token]

    #     #declare months list
    #     monthly_dist = {}
    #     for activity in json_data:
    #         activity_date_str = activity['start_date_local']
    #         activity_date = datetime.strptime(activity_date_str, "%Y-%m-%dT%H:%M:%SZ").date()
    #         year_month = (activity_date.year, activity_date.month)

    #         #get distance
    #         distance = activity.get('distance', 0) /1000
    #         if year_month in monthly_dist:
    #             monthly_dist[year_month] += distance
    #         else:
    #             monthly_dist[year_month] = distance

    #     #put this in format that will work with plotly

    #     return jsonify(monthly_dist)
    
    @app.route('/me/yearly_kudos')
    def yearly_kudos():
        @after_this_request
        def add_header(response):
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response

        access_token = session['access_token']
        activity_type = request.args.get('type', default=None)
        json_data = user_activity_data[access_token]

        start_year = 2009
        current_date = date.today()
        current_year = current_date.year

        first_year_with_data = current_year
        for activity in json_data:
            activity_year = int(activity['start_date_local'][:4])
            if activity_year < first_year_with_data:
                first_year_with_data = activity_year

        blank_data = []
        for i in range(current_year - first_year_with_data + 1):
            blank_data.append([0] * 366)
        result = {"data": blank_data}

        for activity in json_data:
            if activity["type"] == activity_type or activity_type is None:
                activity_date = activity['start_date_local']
                activity_epoch = date(int(activity_date[0:4]), int(activity_date[5:7]), int(activity_date[8:10]))

                beginning_of_year = date(activity_epoch.year, 1, 1)
                deltas = activity_epoch - beginning_of_year

                years_since_start_year = activity_epoch.year - first_year_with_data
                day_of_year = deltas.days

                kudos = int(activity['kudos_count'])
                result['data'][years_since_start_year][day_of_year] += kudos

        for index in range(current_year - first_year_with_data + 1):
            result['data'][index] = list(np.cumsum(result['data'][index]))
            for i in range(366):
                result['data'][index][i] = "{:.2f}".format(result['data'][index][i])

        return jsonify(result)
    
    @app.route('/me/yearly_data_elev',methods=["GET"])
    def yearly_data_elev():
        @after_this_request
        def add_header(response):
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
        # get access token
        access_token = session['access_token']
        activity_type = request.args.get('type', default=None)

        # find range in EPOCH
        start_year = 2009
        current_date = date.today()
        current_year = current_date.year
        json_data = user_activity_data[access_token]

        # determine the first year with recorded data
        first_year_with_data = current_year
        for activity in json_data:
            activity_year = int(activity['start_date_local'][:4])
            if activity_year < first_year_with_data:
                first_year_with_data = activity_year

        # populate empty lists
        blank_data = []
        for i in range(current_year - first_year_with_data + 1):
            blank_data.append([0] * 366)
        result = {"data": blank_data}

        for activity in json_data:
            if activity["type"] == activity_type or activity_type is None:
                activity_date = activity['start_date_local']
                activity_epoch = date(int(activity_date[0:4]), int(activity_date[5:7]), int(activity_date[8:10]))

                beginning_of_year = date(activity_epoch.year, 1, 1)
                deltas = activity_epoch - beginning_of_year

                years_since_start_year = activity_epoch.year - first_year_with_data
                day_of_year = deltas.days

                elev = activity['total_elevation_gain']
                result['data'][years_since_start_year][day_of_year] += elev

        for index in range(current_year - first_year_with_data + 1):
            result['data'][index] = list(np.cumsum(result['data'][index]))
            for i in range(366):
                result['data'][index][i] = "{:.2f}".format(result['data'][index][i])

        return jsonify(result)

    
    
    @app.route('/me/annual_cumulative_time',methods=["GET"])
    def annual_cumulative_time():
        @after_this_request
        def add_header(response):
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
        access_token = session['access_token']
        activity_type = request.args.get('type', default=None)

        start_year = 2009
        current_date = date.today()
        current_year = current_date.year
        json_data = user_activity_data[access_token]

        first_year_with_data = current_year
        for activity in json_data:
            activity_year = int(activity['start_date_local'][:4])
            if activity_year < first_year_with_data:
                first_year_with_data = activity_year

        blank_data = []
        for i in range(current_year - first_year_with_data + 1):
            blank_data.append([0] * 366)
        result = {"data": blank_data}

        for activity in json_data:
            if activity["type"] == activity_type or activity_type is None:
                activity_date = activity['start_date_local']
                activity_epoch = date(int(activity_date[0:4]), int(activity_date[5:7]), int(activity_date[8:10]))

                beginning_of_year = date(activity_epoch.year, 1, 1)
                deltas = activity_epoch - beginning_of_year

                years_since_start_year = activity_epoch.year - first_year_with_data
                day_of_year = deltas.days

                time = activity['moving_time'] / 3600
                result['data'][years_since_start_year][day_of_year] += time

        for index in range(current_year - first_year_with_data + 1):
            result['data'][index] = list(np.cumsum(result['data'][index]))
            for i in range(366):
                result['data'][index][i] = "{:.2f}".format(result['data'][index][i])

        return jsonify(result)   

    return app



    