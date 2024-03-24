import os

from flask import Flask,session,redirect,request,render_template,jsonify,after_this_request
import requests
import datetime
import numpy as np
# from flask_session import Session

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.secret_key = 'hi'

    @app.route('/',methods=["GET"])
    def main():
        # if not already logged in: 
        print(session.get('access_token'))
        return render_template("login.html")
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
        req = requests.post("https://www.strava.com/api/v3/oauth/token",json={"client_id":"117096","client_secret":"68791d309fc676d56dd6c88a5a35b340e8b68a38","code":user_code,"grade_type":"authorization_code"})
        print(req.text)
        # store as session access_token
        access_token = req.json().get('access_token')
        if access_token != None:
            session['access_token'] = access_token
            return redirect("/me")
        else:
            return redirect("/")
        # return get_req.text
    @app.route('/me')
    def me():
        try:
            access_token = session['access_token']
            get_req = requests.get(f"https://www.strava.com/api/v3/activities?access_token={access_token}")
            json_data = get_req.json()
            #page_info = ""
            #for i in range(len(json_data)):
            #    page_info+=json_data[i]['name']+'<br>'
            return render_template("main.html")
        except KeyError:
            return redirect("/")
        return page_info
    @app.route('/logout')
    def logout():
        session.pop('access_token',default=None)
        return render_template("logout.html")
    
    @app.route('/about')
    def about():
        return render_template("about_us.html")


    @app.route('/me/weekly_data',methods=["GET"])
    def weekly_data():
        @after_this_request
        def add_header(response):
            # response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
        # get access token
        access_token = session['access_token']

        # find weekly range in EPOCH
        start_date = int(request.args.get('start_date'))/1000
        week_time = 604800
        end_date = start_date+week_time
        # get data from Strava API
        strava_request = requests.get(f"https://www.strava.com/api/v3/activities?before={end_date}&after={start_date}&access_token={access_token}")
        json_data = strava_request.json()
        # populate empty lists
        result = {"data":[0]*7}
        # time for a day
        delta = 86400
        for i in range(len(json_data)):
            activity_date = json_data[i]['start_date']
            activity_datetime = datetime.datetime(int(activity_date[0:4]), int(activity_date[5:7]), int(activity_date[8:10]))
            activity_epoch = int(activity_datetime.timestamp())
            diff = int(activity_epoch) - start_date
            # distance in km
            distance = json_data[i]['distance']/1000
            # store
            result['data'][int(diff//delta)]+=distance
        for i in range(7):
            # round to %.2f
            result['data'][i]="{:.2f}".format(result['data'][i])

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

        # find weekly range in EPOCH
        start_year = 2020
        # TODO calculate this
        current_year = 2024
        start_date = 1577836800
        year_time = 31556926
        json_data = []
        for index,year in enumerate(range(start_year,current_year)):
            end_date = start_date+year_time*(index+1)

            json_data.append([])
            # get data from Strava API
            for i in range(1,6):
                strava_request = requests.get(f"https://www.strava.com/api/v3/activities?before={end_date+year_time*index}&after={start_date+year_time*index}&access_token={access_token}&per_page=200&page={i}")
                json_data[index] += strava_request.json()

        # populate empty lists
        blank_data = []
        for i in range(current_year-start_year):
            blank_data.append([0]*365)
        result = {"data":blank_data}
        print(result)
        # time for a day
        delta = 86400
        print(len(blank_data))
        for index in range(len(blank_data)):
            for i in range(len(json_data[index])):
                activity_date = json_data[index][i]['start_date']
                activity_datetime = datetime.datetime(int(activity_date[0:4]), int(activity_date[5:7]), int(activity_date[8:10]))
                activity_epoch = int(activity_datetime.timestamp())
                diff = int(activity_epoch) - start_date+year_time*index
                # distance in km
                distance = json_data[index][i]['distance']/1000
                # store
                print('day of year',int(diff//delta%365))
                result['data'][index][int(diff//delta%365)]+=distance
            result['data'][index] = list(np.cumsum(result['data'][index]))
            for i in range(365):
                # round to %.2f
                result['data'][index][i]="{:.2f}".format(result['data'][index][i])

        print(result)
        return jsonify(result)



    return app

