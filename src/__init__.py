import os

from flask import Flask,session,redirect,request,render_template,jsonify,after_this_request
import requests
import numpy as np
import pandas as pd

<<<<<<< Updated upstream
from datetime import datetime,date
=======
from datetime import datetime,date,timedelta
>>>>>>> Stashed changes

# {access_token, data}
user_activity_data = {}

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.secret_key = 'hi'

    @app.route('/',methods=["GET"])
    def main():
        # if not already logged in: 
<<<<<<< Updated upstream
        return render_template("login.html")
=======
        return render_template("/login.html")
>>>>>>> Stashed changes

    @app.route('/login.html',methods=["GET"])
    def login():
        print(session.get('access_token'))
        if session.get('access_token') == None:
            return redirect('http://www.strava.com/oauth/authorize?client_id=117096&response_type=code&redirect_uri=http://127.0.0.1:5000/hello&approval_prompt=force&scope=read_all,activity:read_all')
        else:
            return redirect("/me")

    @app.route('/hello')
    def hello():
        # process "cancel"
        user_code = request.args.get('code')
<<<<<<< Updated upstream
        req = requests.post("https://www.strava.com/api/v3/oauth/token",json={"client_id":"117096","client_secret":"68791d309fc676d56dd6c88a5a35b340e8b68a38","code":user_code,"grade_type":"authorization_code"})
=======
        req = requests.post("https://www.strava.com/api/v3/oauth/token",json={"client_id":"117096","client_secret":"ca6bda0bcd120f49c2c540e656b8741204cf5ef7","code":user_code,"grade_type":"authorization_code"})
>>>>>>> Stashed changes
        # store as session access_token
        access_token = req.json().get('access_token')
        if access_token != None:
            session['access_token'] = access_token
            load_user_activities()
            return redirect("/me")
        else:
            return redirect("/")
        # return get_req.text
    @app.route('/me')
    def me():
        try:
            access_token = session['access_token']
            return render_template("main.html")
        except KeyError:
            return redirect("/")
<<<<<<< Updated upstream
        return page_info
=======
>>>>>>> Stashed changes

    @app.route('/logout')
    def logout():
        session.pop('access_token',default=None)
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
    
    @app.route('/weeklyinfo')
    def weeklyinfo():
        return render_template("weekly.html")
    
    def load_user_activities():

        access_token = session['access_token']
        try:
            user_activity_data[access_token]
            return
        except KeyError:
            pass

        epoch_year = 31556926  
        start_year = 2020
        start_year_epoch = 1577836800  #2020

        current_year = date.today().year
        json_data = []

        for year_index in range(start_year, current_year + 1):
            start_epoch = start_year_epoch + epoch_year * (year_index - start_year)
            end_epoch = start_epoch + epoch_year

            i = 1
            while True:
                print(f"Fetching data from {start_epoch} to {end_epoch}, page {i}")
                response = requests.get(
                    f"https://www.strava.com/api/v3/activities?before={end_epoch}&after={start_epoch}&access_token={access_token}&per_page=200&page={i}"
                )
                data = response.json()
                if not data:
                    break
                json_data.extend(data)
                i += 1

        user_activity_data[access_token] = json_data



    @app.route('/me/user_info')
    def get_user_info():
        access_token = session['access_token']

        headers = {
            "Authorization": f"Bearer {access_token}"
        }
    
        response = requests.get("https://www.strava.com/api/v3/athlete", headers = headers)
        data = response.json()
        print(data)
        first_name = data.get('firstname')
        print(first_name)
        return jsonify({"firstname": first_name})


    def load_user_activities():
        access_token = session['access_token']
        try:
            user_activity_data[access_token]
            return
        except KeyError:
            pass

        # find weekly range in EPOCH
        start_year = 2020
        # TODO calculate this
        current_year = 2024
        start_date = 1577836800
        year_time = 31556926
        json_data = []
        for index,year in enumerate(range(start_year,current_year+1)):
            end_date = start_date+year_time*(index+1)

            # get data from Strava API
            # TODO make this a while loop
            i = 1
            while True:
                print("using start_epoch: ",end_date,"using end_epoch",start_date+year_time*index)
                strava_request = requests.get(f"https://www.strava.com/api/v3/activities?before={end_date}&after={start_date+year_time*index}&access_token={access_token}&per_page=200&page={i}")
                r = strava_request.json()
                if not r:
                    break
                json_data += r
                i+=1

        user_activity_data[access_token] = json_data


    @app.route('/me/weekly_data',methods=["GET"])
    def load_weekly_data():
        @after_this_request
        def add_header(response):
            # response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
        # TODO check if its already loaded
        try:
            access_token = session['access_token']
            json_data = user_activity_data[access_token]
        except KeyError:
            return redirect("/")

<<<<<<< Updated upstream

        # find weekly range in EPOCH
        start_date = int(request.args.get('start_date'))/1000
        week_time = 604800
        end_date = start_date+week_time
        # populate empty lists
        result = {"data":[0]*7}
        # time for a day
        delta = 86400
        for i in range(len(json_data)):
            activity_date = json_data[i]['start_date_local']
            activity_epoch = datetime(int(activity_date[0:4]),int(activity_date[5:7]),int(activity_date[8:10])).strftime("%s")
            if(int(activity_epoch) > start_date and int(activity_epoch) < end_date):
                diff = int(activity_epoch) - start_date

                # distance in km
                distance = float(json_data[i]['distance'])/1000
                # store
                result['data'][int(diff//delta)]+=distance
            
        for i in range(7):
            # round to %.2f
            result['data'][i]="{:.2f}".format(result['data'][i])
        
=======

        start_date_unix = int(request.args.get('start_date')) / 1000
        start_date = datetime.fromtimestamp(start_date_unix).date()
        week_time = timedelta(days=7)
        end_date = start_date + week_time

        result = {"data": [0]*7}
        delta = timedelta(days=1)

        for activity in json_data:
            activity_date_str = activity['start_date_local']
            activity_date = datetime.strptime(activity_date_str, "%Y-%m-%dT%H:%M:%SZ").date()

            if start_date <= activity_date < end_date:
                diff = (activity_date - start_date).days
                distance = float(activity['distance']) / 1000  # Convert to km
                result['data'][diff] += distance

        for i in range(7):
            result['data'][i] = "{:.2f}".format(result['data'][i])

>>>>>>> Stashed changes
        return jsonify(result)

    @app.route('/me/yearly_data',methods=["GET"])
    def yearly_data():
        @after_this_request
        def add_header(response):
            # response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
        # get access token
        access_token = session['access_token']

        # find range in EPOCH
        start_year = 2020
<<<<<<< Updated upstream

        start_date = date(2020,1,1)
        current_date = date.today()
        # TODO calculate this
        current_year = 2024
        start_date = 1577836800
        year_time = 31556926
        json_data = []

=======
        current_date = date.today()
        current_year = current_date.year
        print(current_year)
        json_data = []
        current_day_of_year = current_date.timetuple().tm_yday


>>>>>>> Stashed changes
        # get user data from access_token
        json_data = user_activity_data[access_token]

        # populate empty lists
        blank_data = []
        for i in range(current_year-start_year+1):
<<<<<<< Updated upstream
            blank_data.append([0]*365)
        result = {"data":blank_data}
        # time for a day
        delta = 86400
=======
            blank_data.append([0]*366)
        result = {"data":blank_data}
        # time for a day
>>>>>>> Stashed changes
        for i in range(len(json_data)):
            activity_date = json_data[i]['start_date_local']
            activity_epoch = date(int(activity_date[0:4]),int(activity_date[5:7]),int(activity_date[8:10]))

            beginning_of_year = date(activity_epoch.year,1,1)
            deltas = activity_epoch - beginning_of_year

<<<<<<< Updated upstream
            years_since_start_year = activity_epoch.year - start_year # (int(activity_epoch) - start_date) // year_time
            # can't use index
            day_of_year = deltas.days
            # distance in km
            distance = json_data[i]['distance']/1000
            result['data'][years_since_start_year][day_of_year]+=distance
=======
            years_since_start_year = activity_epoch.year - start_year 
            day_of_year = deltas.days

            if activity_epoch.year == current_year & day_of_year < current_day_of_year + 1:
                # distance in km
                result['data'][years_since_start_year][day_of_year]=None
            else:
                # distance in km
                distance = json_data[i]['distance']/1000
                result['data'][years_since_start_year][day_of_year]+=distance
>>>>>>> Stashed changes

        for index in range(current_year-start_year+1):
            result['data'][index] = list(np.cumsum(result['data'][index]))
            for i in range(366):
                # round to %.2f
                result['data'][index][i]="{:.2f}".format(result['data'][index][i])

       #some logic to set values greater than current day to none for current year
        #if current_year == 

        return jsonify(result)
    
    @app.route('/me/pie_data_count')
    def pie_data_count():
        @after_this_request
        def add_header(response):
            # response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
        
        #get access token
        access_token = session['access_token']
        #get data
        json_data = user_activity_data[access_token]

        #initialize count array
        activity_counts = {}
        #tally number of times each activity ahs been done
        for activity in json_data:
            activity_type = activity.get('type', 'Unknown')
            #increment if that type has been found 
            if activity_type in activity_counts:
                activity_counts[activity_type] += 1
            #add to activity type if not found 
            else:
                activity_counts[activity_type] = 1

        #format result for plotly 
        result = [{"type": activity_type, "count": count} for activity_type, count in activity_counts.items()]

        return jsonify(result)
    
    
    @app.route('/me/pie_data_time')
    def pie_data_time():
        @after_this_request
        def add_header(response):
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
        
        #get access token, activity data
        access_token = session['access_token']
        json_data = user_activity_data[access_token]


        activity_time = {}
        #iterate through activities by type, increment by time
        for activity in json_data:
            activity_type = activity.get('type', 'Unknown')
            #get time, convert to hours
            moving_time_hours = activity.get('moving_time', 0) / 3600 
            if moving_time_hours < 1:
                if activity_type in activity_time:
                    activity_time[activity_type] += moving_time_hours
                else:
                    activity_time[activity_type] = moving_time_hours

        # format result for plotly
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

        activity_distance = {}
        #iterate by activity type, increase by distance
        for activity in json_data:
            activity_type = activity.get('type', 'Unknown')
            #get distance, covert to km
            totalDistance = int(activity.get('distance', 0) / 1000)
            #check if distance is greater than 0
            if totalDistance > 0:
                if activity_type in activity_distance:
                    activity_distance[activity_type] += totalDistance
                else:
                    activity_distance[activity_type] = totalDistance

        #format result for plotly
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

        activity_distance = {}

        for activity in json_data:
            activity_type = activity.get('type', 'Unknown')
            #get distance, covert to km
            totalKudos = int(activity.get('kudos_count', 0))
            #check if distance is greater than 0
            if totalKudos > 0:
                if activity_type in activity_distance:
                    activity_distance[activity_type] += totalKudos
                else:
                    activity_distance[activity_type] = totalKudos

        #format result for plotly
        result = [{"type": activity_type, "kudos": kudos} for activity_type, kudos in activity_distance.items()]

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


    @app.route('/me/monthly_dist_grouped')
    def monthly_dist_grouped():
        @after_this_request
        def add_header(response):
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response

        #get data
        access_token = session['access_token']
        json_data = user_activity_data[access_token]

        #declare months list
        monthly_dist = {}
        for activity in json_data:
            activity_date_str = activity['start_date_local']
            activity_date = datetime.strptime(activity_date_str, "%Y-%m-%dT%H:%M:%SZ").date()
            year_month = (activity_date.year, activity_date.month)

            #get distance
            distance = activity.get('distance', 0) /1000
            if year_month in monthly_dist:
                monthly_dist[year_month] += distance
            else:
                monthly_dist[year_month] = distance
        print(monthly_dist)

        #put this in format that will work with plotly

        return jsonify(monthly_dist)
    
    @app.route('/me/yearly_kudos')
    def yearly_kudos():
        @after_this_request
        def add_header(response):
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response

        access_token = session['access_token']
        json_data = user_activity_data[access_token]

        start_year = 2020
        current_date = date.today()
        current_year = current_date.year

        blank_data = []
        for i in range(current_year - start_year + 1):
            blank_data.append([0] * 366) 
        result = {"data": blank_data}

        for activity in json_data:
            activity_date = activity['start_date_local']
            activity_epoch = date(int(activity_date[0:4]), int(activity_date[5:7]), int(activity_date[8:10]))

            beginning_of_year = date(activity_epoch.year, 1, 1)
            deltas = activity_epoch - beginning_of_year

            years_since_start_year = activity_epoch.year - start_year
            day_of_year = deltas.days

            #count kudos
            kudos = int(activity['kudos_count'])
            result['data'][years_since_start_year][day_of_year] += kudos

        #accumulate
        for index in range(current_year - start_year + 1):
            result['data'][index] = list(np.cumsum(result['data'][index]))
            for i in range(366):
                result['data'][index][i] = "{:.2f}".format(result['data'][index][i])

        return jsonify(result)
    
    @app.route('/me/yearly_data_elev',methods=["GET"])
    def yearly_data_elev():
        @after_this_request
        def add_header(response):
            # response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
        # get access token
        access_token = session['access_token']

        # find range in EPOCH
        start_year = 2020
        start_date = date(2020,1,1)
        current_date = date.today()
        current_year = current_date.year
        json_data = []

        # get user data from access_token
        json_data = user_activity_data[access_token]

        # populate empty lists
        blank_data = []
        for i in range(current_year-start_year+1):
            blank_data.append([0]*366)
        result = {"data":blank_data}
        # time for a day
        delta = 86400
        for i in range(len(json_data)):
            activity_date = json_data[i]['start_date_local']
            activity_epoch = date(int(activity_date[0:4]),int(activity_date[5:7]),int(activity_date[8:10]))

            beginning_of_year = date(activity_epoch.year,1,1)
            deltas = activity_epoch - beginning_of_year

            years_since_start_year = activity_epoch.year - start_year 
            # can't use index
            day_of_year = deltas.days
            # elevation in meters
            elev = json_data[i]['total_elevation_gain']
            result['data'][years_since_start_year][day_of_year]+=elev

        for index in range(current_year-start_year+1):
            result['data'][index] = list(np.cumsum(result['data'][index]))
            for i in range(366):
                # round to %.2f
                result['data'][index][i]="{:.2f}".format(result['data'][index][i])

        return jsonify(result)
    
    
    @app.route('/me/annual_cumulative_time',methods=["GET"])
    def annual_cumulative_time():
        @after_this_request
        def add_header(response):
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
        # get access token
        access_token = session['access_token']

        # find range in EPOCH
        start_year = 2020
        current_date = date.today()
        current_year = current_date.year
        json_data = []

        # get user data from access_token
        json_data = user_activity_data[access_token]

        # populate empty lists
        blank_data = []
        for i in range(current_year-start_year+1):
            blank_data.append([0]*366)
        result = {"data":blank_data}
        # time for a day
        delta = 86400
        for i in range(len(json_data)):
            activity_date = json_data[i]['start_date_local']
            activity_epoch = date(int(activity_date[0:4]),int(activity_date[5:7]),int(activity_date[8:10]))

            beginning_of_year = date(activity_epoch.year,1,1)
            deltas = activity_epoch - beginning_of_year

            years_since_start_year = activity_epoch.year - start_year 
            # can't use index
            day_of_year = deltas.days
            # time in hours
            time = json_data[i]['moving_time'] / 3600
            result['data'][years_since_start_year][day_of_year]+=time

        for index in range(current_year-start_year+1):
            result['data'][index] = list(np.cumsum(result['data'][index]))
            for i in range(366):
                # round to %.2f
                result['data'][index][i]="{:.2f}".format(result['data'][index][i])

        return jsonify(result)
    

    @app.route('/me/pie_data_elevation', methods=["GET"])
    def pie_data_elevation():
        @after_this_request
        def add_header(response):
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
        
        access_token = session['access_token']
        json_data = user_activity_data[access_token]

        activity_distance = {}
        #iterate by activity type, increase by elevation
        for activity in json_data:
            activity_type = activity.get('type', 'Unknown')
            #get elevation
            totalDistance = int(activity.get('total_elevation_gain', 0))
            #check if elevation is greater than 0
            if totalDistance > 0:
                if activity_type in activity_distance:
                    activity_distance[activity_type] += totalDistance
                else:
                    activity_distance[activity_type] = totalDistance

        #format result for plotly
        result = [{"type": activity_type, "distance": distance} for activity_type, distance in activity_distance.items()]

        return jsonify(result) 
    

    return app



    