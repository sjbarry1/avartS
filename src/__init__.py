import os

from flask import Flask,session,redirect,request,render_template
import requests
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
            page_info = ""
            for i in range(len(json_data)):
                page_info+=json_data[i]['name']+'<br>'
        except KeyError:
            return redirect("/")
        return page_info
    @app.route('/logout')
    def logout():
        session.pop('access_token',default=None)
        return "logged out",{"Refresh": "1; url=/"}

    return app
