import os

from flask import Flask
from flask import render_template
from flask import redirect
from flask import url_for
import random
from flask import request, session, jsonify
from datetime import timedelta
# from DB_file import dbManager
from DB_Postgre import dbManager
from datetime import datetime
import time

app = Flask(__name__)
app.config.from_pyfile('settings.py')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=10000)


@app.route('/session')
def session_func():
    # print(session['CHECK'])
    return jsonify(dict(session))


@app.route('/', methods=['POST', 'GET'])
def log_in():
    return render_template('log_in.html')


@app.route('/Informed', methods=['POST', 'GET'])
def Informed_func():
    if request.method == "POST":
        if 'AmazonMT' in request.form:
            session['AmazonMT'] = request.form['AmazonMT']
            session['logedin'] = True
            query = f"select * from \"main_table\" where \"ID\"='%s'" % session['AmazonMT']
            query_result = dbManager.fetch(query)
            if len(query_result) == 0:
                query = "INSERT INTO \"main_table\"(\"ID\",\"ex_type\",\"motivation_type\",\"first_prediction\",\"final_prediction\",\"in_time\",\"end_time\",\"Explanation_Type\") VALUES ('%s',%s,%s,%s,%s,\'%s\',\'%s\',\'%s\')" % (
                    session['AmazonMT'], 0, 0, 0, 0, datetime.now(), datetime.now(), "no explanation")
                print(dbManager.commit(query))
                return render_template('Informed_Consent_Screen.html')
            else:
                return render_template('log_in.html', message='This Amazon Mechanical Turk ID has already been used ')
    return render_template('Error.html')


@app.route('/Instruction_screen', methods=['POST', 'GET'])
def Instruction():
    if session['AmazonMT']:
        ex_list = [1, 2, 3, 4, 5]
        ex_num = random.choice(ex_list)
        mt_list = [1, 2]
        mt_num = random.choice(mt_list)
        query = f"UPDATE \"main_table\" set \"ex_type\"='%s', \"motivation_type\"='%s' where \"ID\"='%s'" % (
            ex_num, mt_num, session['AmazonMT'])
        dbManager.commit(query)
        return render_template('Instruction_screen.html', mt_type=mt_num)
    return render_template('Error.html')


@app.route('/First_Prediction', methods=['POST', 'GET'])
def First_Prediction():
    if session['AmazonMT']:
        start_time = datetime.now()
        query = "INSERT INTO \"First_Duration_table\"(\"ID\",\"first_p_starttime\",\"first_p_endtime\") VALUES ('%s'," \
                "\'%s\',\'%s\')" % (
                    session['AmazonMT'], start_time, datetime.now())
        dbManager.commit(query)
        return render_template('First_Prediction_Screen.html')
    return render_template('Error.html')


@app.route('/Select_Explanation', methods=['POST', 'GET'])
def Select_Explanation():
    if session['AmazonMT']:
        start_time = datetime.now()
        first_selection_list = [1,2]
        first_selection = random.choice(first_selection_list)
        second_selection_list = [1, 2, 3, 4, 5]
        second_selection = random.choice(second_selection_list)
        First_pre = request.form['First_pre']
        query = f"UPDATE \"main_table\" set \"first_prediction\"='%s',\"in_time\"='%s',\"first_selection\"='%s',\"second_selection\"='%s',\"Ex_start\"='%s' where \"ID\"='%s'" % (
            First_pre, start_time, first_selection, second_selection, start_time, session['AmazonMT'])
        dbManager.commit(query)
        query_D = f"UPDATE \"First_Duration_table\" set \"first_p_endtime\"='%s' where \"ID\"='%s'" % (
            start_time, session['AmazonMT'])
        dbManager.commit(query_D)
        return render_template('Select_Explanation.html', first_selection=first_selection,
                               second_selection=second_selection)
    return render_template('Error.html')


@app.route('/Select_Explanation_Update', methods=['POST', 'GET'])
def Select_Explanation_Update():
    if session['AmazonMT'] and 'Ex_Type' in request.form:
        start_time = datetime.now()
        Ex_Type = request.form['Ex_Type']
        query = "INSERT INTO \"Explanation_Select\"(\"ID\",\"Time\",\"Explanation_Type\") VALUES ('%s',\'%s\','%s')" % (
            session['AmazonMT'], start_time, Ex_Type)
        dbManager.commit(query)
        return render_template('Select_Explanation_Update.html')
    return render_template('Error.html')


@app.route('/Final_Prediction', methods=['POST', 'GET'])
def Final_Prediction():
    if request.method == "POST":
        if session['AmazonMT']:
            now = datetime.now()
            if 'Ex_Type' in request.form:
                Ex_Type = request.form['Ex_Type']
                query = f"UPDATE \"main_table\" set \"Explanation_Type\"='%s' where \"ID\"='%s'" % (
                    Ex_Type, session['AmazonMT'])
                dbManager.commit(query)
            query = f"select * from \"main_table\" where \"ID\"='%s'" % session['AmazonMT']
            query_result = dbManager.fetch(query)
            mt_num = query_result[0][2]
            if mt_num == 1:
                prize = 1
            else:
                prize = 10
            query = f"UPDATE \"main_table\" set \"in_time\"='%s',\"Ex_end\"='%s' where \"ID\"='%s'" % (
                now, now, session['AmazonMT'])
            dbManager.commit(query)
            return render_template('Final_Prediction_Screen.html', prize=prize)
    return render_template('Error.html')


@app.route('/End_Question_Screen', methods=['POST', 'GET'])
def End_Question():
    if request.method == "POST":
        if 'Final_pre' in request.form:
            if session['AmazonMT']:
                now = datetime.now()
                Final_pre = request.form['Final_pre']
                query = f"UPDATE \"main_table\" set \"final_prediction\"='%s',\"end_time\"='%s' where \"ID\"='%s'" % (
                    Final_pre, now, session['AmazonMT'])
                dbManager.commit(query)
                return render_template('End_Question_Screen.html')
    return render_template('Error.html')


@app.route('/Thank_you', methods=['POST', 'GET'])
def Thank_you():
    if request.method == "POST":
        if 'Age' in request.form and 'Gender' in request.form and 'Length' in request.form and 'Quality' in request.form and 'Helpful' in request.form and 'Motivation' in request.form and 'Effort' in request.form and 'realistic' in request.form and 'device' in request.form and 'privet' in request.form and 'prize' in request.form and 'knowledge' in request.form and 'noise' in request.form:
            if session['AmazonMT']:
                query = "INSERT INTO \"Demographic_table\"(\"ID\",\"ex_Length\",\"Age\",\"Gender\",\"Quality\",\"Helpful\",\"Motivation\",\"Effort\"," \
                        "\"realistic\",\"device\",\"privet\",\"prize\",\"knowledge\",\"noise\",\"education\",\"confident\",\"information\",\"difficulty\",\"prediction\",\"Prediction_Price\",\"Assessment\",\"Understand\",\"Learn\",\"acceptance\") " \
                        "VALUES ('%s',%s,%s,'%s',%s,%s,%s,%s,%s,'%s',%s,%s,%s,%s,'%s',%s,%s,%s,'%s','%s',%s,%s,%s,%s)" % (
                            session['AmazonMT'], request.form['Length'], request.form['Age'], request.form['Gender'],
                            request.form['Quality'], request.form['Helpful'], request.form['Motivation'],
                            request.form['Effort'], request.form['realistic'], request.form['device'],
                            request.form['privet'],
                            request.form['prize'], request.form['knowledge'], request.form['noise'],
                            request.form['education'],
                            request.form['confident'], request.form['information'], request.form['difficult'],
                            request.form['prediction'], request.form['prediction_price'], request.form['assessment'],
                            request.form['understand'], request.form['learn'], request.form['acceptance'])
                dbManager.commit(query)
                Amazon_code = "8257c52c06"
                return render_template('Thank_You_Screen.html', Amazon_code=Amazon_code)
    return render_template('Error.html')


port = 80
try:
    port = os.environ['PORT']
except:
    pass

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=False)
