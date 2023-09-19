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


# def sort_events_key(event):
#
#     key_value = 0
#
#     if 'eventTime' in event:
#         key_value += event['eventTime'][1]  # Minute is 0-59.
#         hours = event['eventTime'][0] % 12  # 12hr is 0-11
#         if event['eventTime'][2] == 'pm':
#             hours += 12  # 24hr is 0-23
#         key_value += hours * 60  # Hour is 0-23
#
#     key_value += (event['eventDate'][2] - 1) * 60 * 24  # Day is 0-30.
#     key_value += (event['eventDate'][1] - 1) * 60 * 24 * 31  # Month is 0-11.
#     key_value += event['eventDate'][0] * 60 * 24 * 31 * 12  # Year is any integer.
#
#     return key_value


# def sort_events_list(events_list):
#     return sorted(events_list, key=sort_events_key, reverse=True)


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

    # TODO remove ~ from eventName!

    if 'n' not in request.args or 'm' not in request.args or 'd' not in request.args:
        return 'Invalid request.'

    if request.method == 'GET':
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
        return 'Invalid request.'

    # new_event_obj = {'eventName': request.form['event-name']}
    new_event_arg_list = [request.form['event-name'].replace('~', '')]  # Remove all tildes, which delimits the url event data.

    if request.form['date-type'] == 'cal':
        try:
            cal_list = [int(request.form['cal-year']), int(request.form['cal-month']), int(request.form['cal-day'])]
        except:
            # Couldn't parse all date fields. Fields blank or invalid.
            return 'Invalid request.'
        else:
            if cal_list[0] < 0 or 9999 < cal_list[0] \
                    or cal_list[1] < 1 or 12 < cal_list[1] \
                    or cal_list[2] < 1 or 31 < cal_list[2]:
                return 'Date out of range.'
            date_str = f'{str(cal_list[0]).zfill(4)}{str(cal_list[1]).zfill(2)}{str(cal_list[2]).zfill(2)}'
            new_event_arg_list.append(date_str)
            # new_event_obj['eventDate'] = cal_list

    else:
        # request.form['date-type'] == 'gest':
        try:
            gest_list = [int(request.form['gest-week']), int(request.form['gest-day'])]
        except:
            # Couldn't parse all date fields. Fields blank or invalid.
            return 'Invalid request.'
        else:
            if gest_list[0] < 0 or 42 < gest_list[0] \
                    or gest_list[1] < 0 or 6 < gest_list[1]:
                return 'Date out of range.'
            date_str = f'{str(gest_list[0]).zfill(2)}{gest_list[1]}'
            new_event_arg_list.append(date_str)
            # new_event_obj['eventGestTime'] = gest_list

    if 'has-time' in request.form:
        # request.form['has-time'] == 'true':
        if request.form['am-or-pm'] != 'am' and request.form['am-or-pm'] != 'pm':
            return 'Invalid request.'
        try:
            time_list = [int(request.form['hour']), int(request.form['minute']), request.form['am-or-pm']]
        except:
            # Couldn't parse all time fields. Fields blank or invalid.
            return 'Invalid request.'
        else:
            if time_list[0] < 1 or 12 < time_list[0] \
                    or time_list[1] < 0 or 60 < time_list[1]:
                return 'Time out of range.'
            time_str = f'{str(time_list[0]).zfill(2)}{str(time_list[1]).zfill(2)}{time_list[2]}'
            new_event_arg_list.append(time_str)
            # new_event_obj['eventTime'] = time_list

    try:
        # events_list = json.loads(request.args['e'])
        all_events_str = f"{request.args['e']}~~"  # Todo need to try? What happens if not present?
    except:
        # Events data absent.
        # events_list = []
        all_events_str = ''

    all_events_str += '~'.join(new_event_arg_list)
    # events_list.append(new_event_obj)
    # sorted_events_list = sort_events_list(events_list)
    # events_str = json.dumps(events_list)
    return redirect(url_for('calendar', n=request.args['n'], m=request.args['m'], d=request.args['d'], e=all_events_str))


@app.route('/create', methods=['GET', 'POST'])
def init_calendar():

    if request.method == 'POST':
        if 'n' in request.form and 'm' in request.form and 'd' in request.form:
            name = request.form['n'].replace('~', '')  # Remove all tildes, which delimits the url event data.
            month = request.form['m']
            day = request.form['d']
            return redirect(url_for('calendar', n=name, m=month, d=day, e=''))
        return 'Invalid request.'

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


# def validate_args(args):
#
#     if 'n' not in args:
#         return redirect(url_for('init_calendar'))
#     try:
#         int(args['m'])
#         int(args['d'])
#     except:
#         return redirect(url_for('init_calendar'))
#
#     if 'e' not in args:
#         return kid.render_template('kid_temps/calendar.html')
#         # return redirect(url_for('calendar', n=args['n'], m=args['m'], d=args['d']))
#
#     events_list = args['e'].split('~~')
#     events_list_validated = []
#
#     for event in events_list:
#         # ~~nameA~20231231~1159pm
#         # ~~nameB~426  (week 42 day 6)
#         event_fields = event.split('~')
#         field_count = len(event_fields)
#         if field_count < 2 or 3 < field_count:
#             continue
#         date_str_len = len(event_fields[1])
#         if date_str_len != 3 and date_str_len != 8:
#             continue
#         try:
#             int(event_fields[1])
#         except:
#             continue
#         if field_count > 2:
#             if len(event_fields[2]) != 6:
#                 continue
#             try:
#                 int(event_fields[2][:4])
#             except:
#                 continue
#             if event_fields[2][4:] != 'am' and event_fields[2][4:] != 'pm':
#                 continue
#         events_list_validated.append(event)
#
#     events_str = '~~'.join(events_list_validated)
#     # return kid.render_template('kid_temps/calendar.html')
#     return redirect(url_for('calendar', n=args['n'], m=args['m'], d=args['d'], e=events_str))


@app.route('/')
def calendar():

    if 'n' not in request.args or 'e' not in request.args:
        return redirect(url_for('init_calendar'))
    try:
        int(request.args['m'])
        int(request.args['d'])
    except:
        return redirect(url_for('init_calendar'))

    # if 'e' not in request.args:
    #     return kid.render_template('kid_temps/calendar.html')
    #     # return redirect(url_for('calendar', n=request.args['n'], m=request.args['m'], d=request.args['d']))

    if request.args['e'] == '':
        events_list = []
    else:
        events_list = request.args['e'].split('~~')
    events_list_validated = []

    for event in events_list:
        # ~~nameA~20231231~1159pm
        # ~~nameB~426  (week 42 day 6)
        event_fields = event.split('~')
        field_count = len(event_fields)
        if field_count < 2 or 3 < field_count:
            continue
        date_str_len = len(event_fields[1])
        if date_str_len != 3 and date_str_len != 8:
            continue
        try:
            int(event_fields[1])
        except:
            continue
        if field_count > 2:
            if len(event_fields[2]) != 6:
                continue
            try:
                int(event_fields[2][:4])
            except:
                continue
            if event_fields[2][4:] != 'am' and event_fields[2][4:] != 'pm':
                continue
        events_list_validated.append(event)

    # Todo prevent inf loop of redirects if never validated????????

    if len(events_list) != len(events_list_validated):
        events_str = '~~'.join(events_list_validated)
        print(f'Pruned events string: \n    from: {request.args["e"]}\n      to: {events_str}')
        return redirect(url_for('calendar', n=request.args['n'], m=request.args['m'], d=request.args['d'], e=events_str))

    if len(request.args) != 4:
        return redirect(url_for('calendar', n=request.args['n'], m=request.args['m'], d=request.args['d'], e=request.args['e']))

    return kid.render_template('kid_temps/calendar.html')


if __name__ == '__main__':
    # kid.app_startup()
    app.run(debug=True)
