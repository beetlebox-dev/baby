import os
import json
from datetime import datetime

from flask import Flask, render_template, request, url_for, redirect
from flask_login import LoginManager, login_required

import kid.kid_main as kid
from persist import TEMP_TOP_FOLDER
from admin import admin_alert_thread


# Copyright 2023 Johnathan Pennington | All rights reserved.


app = Flask(__name__)
# app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
# app.config['UPLOAD_FOLDER'] = TEMP_TOP_FOLDER
# login_manager = LoginManager()
# login_manager.init_app(app)


# @app.errorhandler(404)
# def page_not_found(e):
#
#     ignore_paths_starting_with = [  # Doesn't send an admin alert if request.path starts with any of these.
#         '20', 'admin', 'blog', 'cms', 'feed', 'media', 'misc', 'news', 'robots', 'site', 'sito',
#         'shop', 'test', 'web', 'wordpress', 'Wordpress', 'wp', 'Wp', 'xmlrpc.php',
#     ]
#     request_of_concern = True
#     for path_to_ignore in ignore_paths_starting_with:
#         if request.path.startswith(f'/{path_to_ignore}'):
#             request_of_concern = False
#             break
#
#     if request_of_concern:
#         message_body = f'Page not found: \n{request.url}\n' \
#                        f'Rendered page_not_found.html and suggested: beetlebox.dev'
#         admin_alert_thread('Web App - 404', message_body)
#
#     return render_template('page_not_found.html', relpath='https://beetlebox.dev', a_text='beetlebox.dev'), 404


@app.route('/favicon.ico')
def favicon():
    return redirect(url_for('static', filename='favicon.ico'))


# # KID ROUTES:
#
# @login_manager.user_loader
# def load_user(user_id):
#     return kid.load_user(user_id)
#
#
# @login_manager.unauthorized_handler
# def need_login_first():
#     return kid.need_login_first()
#
#
# @app.route('/')
# def kid_top():
#     return kid.top()
#
#
# @app.route('/login', methods=['GET', 'POST'])
# def kid_login():
#     return kid.login()
#
#
# @app.route('/login/<next_page>', methods=['GET', 'POST'])
# def kid_login_next(next_page):
#     return kid.login(next_page)
#
#
# @app.route('/logout')
# def kid_logout():
#     return kid.logout()
#
#
# # KID ROUTES - Login required.
#
#
# @app.route('/home')
# @login_required
# def kid_home():
#     return kid.home()
#
#
# @app.route('/data')
# @login_required
# def kid_serve_event_data():
#     return kid.serve_event_data()
#
#
# @app.route('/admin', methods=['GET', 'POST'])
# @login_required
# def kid_admin():
#     return kid.admin()
#
#
# @app.route('/add_new_event', methods=['POST'])
# @login_required
# def add_new_event():
#     return kid.add_new_event()


def sort_events_key(event):

    key_value = 0

    if 'eventTime' in event:
        key_value += event['eventTime'][1]  # Minute is 0-59.
        hours = event['eventTime'][0] % 12  # 12hr is 0-11
        if event['eventTime'][2] == 'pm':
            hours += 12  # 24hr is 0-23
        key_value += hours * 60  # Hour is 0-23

    key_value += (event['eventDate'][2] - 1) * 60 * 24  # Day is 0-30.
    key_value += (event['eventDate'][1] - 1) * 60 * 24 * 31  # Month is 0-11.
    key_value += event['eventDate'][0] * 60 * 24 * 31 * 12  # Year is any integer.

    return key_value


def sort_events_list(events_list):
    return sorted(events_list, key=sort_events_key, reverse=True)


# @app.route('/add_submit', methods=['POST'])
# def add_submit():
#
#     if 'n' not in request.args or 'm' not in request.args or 'd' not in request.args \
#             or 'event-name' not in request.form or 'date-type' not in request.form \
#             or 'cal-year' not in request.form or 'cal-month' not in request.form or 'cal-day' not in request.form \
#             or 'gest-week' not in request.form or 'gest-day' not in request.form \
#             or 'hour' not in request.form or 'minute' not in request.form or 'am-or-pm' not in request.form:
#         print('a')
#         return 'Invalid request.'
#
#     new_event_obj = {'eventName': request.form['event-name']}
#
#     if request.form['date-type'] == 'cal':
#         try:
#             cal_list = [int(request.form['cal-year']), int(request.form['cal-month']), int(request.form['cal-day'])]
#         except:
#             # Couldn't parse all date fields. Fields blank or invalid.
#             print('b')
#             return 'Invalid request.'
#         else:
#             new_event_obj['eventDate'] = cal_list
#
#     else:
#         # request.form['date-type'] == 'gest':
#         try:
#             gest_list = [int(request.form['gest-week']), int(request.form['gest-day'])]
#         except:
#             # Couldn't parse all date fields. Fields blank or invalid.
#             print('c')
#             return 'Invalid request.'
#         else:
#             new_event_obj['eventGestTime'] = gest_list
#
#     if 'has-time' in request.form:
#         # request.form['has-time'] == 'true':
#         if request.form['am-or-pm'] != 'am' and request.form['am-or-pm'] != 'pm':
#             print('d')
#             return 'Invalid request.'
#         try:
#             time_list = [int(request.form['hour']), int(request.form['minute']), request.form['am-or-pm']]
#         except:
#             # Couldn't parse all time fields. Fields blank or invalid.
#             print('e')
#             return 'Invalid request.'
#         else:
#             new_event_obj['eventTime'] = time_list
#
#     try:
#         events_list = json.loads(request.args['e'])
#     except:
#         # Events data absent or invalid.
#         events_list = []
#
#     events_list.append(new_event_obj)
#     sorted_events_list = sort_events_list(events_list)
#     events_str = json.dumps(sorted_events_list)
#     return redirect(url_for('calendar', n=request.args['n'], m=request.args['m'], d=request.args['d'], e=events_str))


@app.route('/add', methods=['GET', 'POST'])
def add_event():

    if 'n' not in request.args or 'm' not in request.args or 'd' not in request.args:
        return 'Invalid request.'

    if request.method != 'POST':
        current_year = datetime.now().year
        # if 'name' in request.args:
        #     name = request.args['name']
        # else:
        #     name = ''
        # if 'month' in request.args:
        #     month = request.args['month']
        # else:
        #     month = '1'
        # if 'day' in request.args:
        #     day = request.args['day']
        # else:
        #     day = '1'
        return kid.render_template('kid_temps/add_event.html', current_year=current_year)

    # request.method == 'POST':

    if 'event-name' not in request.form or 'date-type' not in request.form \
            or 'cal-year' not in request.form or 'cal-month' not in request.form or 'cal-day' not in request.form \
            or 'gest-week' not in request.form or 'gest-day' not in request.form \
            or 'hour' not in request.form or 'minute' not in request.form or 'am-or-pm' not in request.form:
        print('a')
        return 'Invalid request.'

    new_event_obj = {'eventName': request.form['event-name']}

    if request.form['date-type'] == 'cal':
        try:
            cal_list = [int(request.form['cal-year']), int(request.form['cal-month']), int(request.form['cal-day'])]
        except:
            # Couldn't parse all date fields. Fields blank or invalid.
            print('b')
            return 'Invalid request.'
        else:
            new_event_obj['eventDate'] = cal_list

    else:
        # request.form['date-type'] == 'gest':
        try:
            gest_list = [int(request.form['gest-week']), int(request.form['gest-day'])]
        except:
            # Couldn't parse all date fields. Fields blank or invalid.
            print('c')
            return 'Invalid request.'
        else:
            new_event_obj['eventGestTime'] = gest_list

    if 'has-time' in request.form:
        # request.form['has-time'] == 'true':
        if request.form['am-or-pm'] != 'am' and request.form['am-or-pm'] != 'pm':
            print('d')
            return 'Invalid request.'
        try:
            time_list = [int(request.form['hour']), int(request.form['minute']), request.form['am-or-pm']]
        except:
            # Couldn't parse all time fields. Fields blank or invalid.
            print('e')
            return 'Invalid request.'
        else:
            new_event_obj['eventTime'] = time_list

    try:
        events_list = json.loads(request.args['e'])
    except:
        # Events data absent or invalid.
        events_list = []

    events_list.append(new_event_obj)
    sorted_events_list = sort_events_list(events_list)
    events_str = json.dumps(sorted_events_list)
    return redirect(url_for('calendar', n=request.args['n'], m=request.args['m'], d=request.args['d'], e=events_str))


@app.route('/create')
def init_calendar():
    if 'n' in request.args:
        name = request.args['n']
    else:
        name = ''
    if 'm' in request.args:
        month = request.args['m']
    else:
        month = '1'
    if 'd' in request.args:
        day = request.args['d']
    else:
        day = '1'
    return kid.render_template('kid_temps/init_calendar.html', name=name, month=month, day=day)


@app.route('/')
def calendar():
    try:
        int(request.args['m'])
        int(request.args['d'])
    except:
        return redirect(url_for('init_calendar'))
    return kid.render_template('kid_temps/calendar.html')


if __name__ == '__main__':
    # kid.app_startup()
    app.run(debug=True)
