from datetime import datetime
from flask import Flask, render_template, request, url_for, redirect
from admin import admin_alert_thread


# Copyright 2023 Johnathan Pennington | All rights reserved.


app = Flask(__name__)


# Todo: For setup_cal_redirect(), where request.args is being repaired, say "Please doublecheck this info.",
#  then redirect to where they wanted to go after submit.

# Todo: Help calculate due date at start???


def events_str_to_list(events_str):
    if events_str == '':
        return []  # Otherwise, splitting an empty string would yield: events_list = [''].
    else:
        return events_str.split('~~')


def url_for_calendar(n=None, m=None, d=None, e=None, external=False):
    if n is None:
        n = request.args['n']
    if m is None:
        m = request.args['m']
    if d is None:
        d = request.args['d']
    if e is None:
        if 'e' in request.args:
            e = request.args['e']
    if e is None or e == '':
        # Don't include e in request.args.
        return url_for('calendar', n=n, m=m, d=d, _external=external)
    else:
        return url_for('calendar', n=n, m=m, d=d, e=e, _external=external)


def get_validated_events_list(events_list):

    events_list_validated = []

    for event in events_list:

        # Example event strings:
        # EventNameA~99991231~1159pm (calendar date of 31-DEC-9999, with time)
        # EventNameB~426 (gestational date of week42-day6, no time)

        event_fields = event.split('~')
        field_count = len(event_fields)

        if field_count < 2 or 3 < field_count:
            # Field_count should be either 2 (no time) or 3 (with time).
            continue

        # Validate date field.
        date_str_len = len(event_fields[1])
        if date_str_len != 3 and date_str_len != 8:
            # Date_str_len should be 3 for a gestational date, or 8 for a calendar date.
            continue
        try:
            int(event_fields[1])
        except:
            continue

        # Validate time field.
        if field_count == 3:
            if len(event_fields[2]) != 6:
                continue
            try:
                int(event_fields[2][:4])
            except:
                continue
            if event_fields[2][4:] != 'am' and event_fields[2][4:] != 'pm':
                continue

        events_list_validated.append(event)  # If this line reached, event is valid.

    return events_list_validated


def setup_cal_redirect(repair_mode=True):
    # Repair mode saves existing events, and prompts user to check info.

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

    if repair_mode:
        redirect_endpoint = 'repair_calendar'
    else:
        redirect_endpoint = 'setup_calendar'

    if 'e' in request.args and repair_mode:
        return redirect(url_for(redirect_endpoint, n=name, m=month, d=day, e=request.args['e']))
    else:
        return redirect(url_for(redirect_endpoint, n=name, m=month, d=day))


def setup_or_repair_calendar(mode):

    if request.method == 'POST':
        if 'n' in request.form and 'm' in request.form and 'd' in request.form:
            name = request.form['n'].replace('~', '')  # Remove all tildes, which delimits the url event data.
            return redirect(url_for_calendar(n=name, m=request.form['m'], d=request.form['d']))
        return 'Invalid request.'

    if mode == 'repair':
        button_text = 'Confirm'
        repair_message_display = 'block'
    else:
        button_text = 'Create Calendar'
        repair_message_display = 'none'

    # request.method == 'GET'
    return render_template('init_calendar.html', name=request.args['n'], month=request.args['m'], day=request.args['d'],
                           button_text=button_text, repair_message_display=repair_message_display)


@app.errorhandler(404)
def page_not_found(e):

    ignore_paths_starting_with = [  # Doesn't send an admin alert if request.path starts with any of these.
        '20', 'admin', 'blog', 'cms', 'feed', 'media', 'misc', 'news', 'robots', 'site', 'sito',
        'shop', 'test', 'web', 'wordpress', 'Wordpress', 'wp', 'Wp', 'xmlrpc.php',
    ]
    site_root = url_for_calendar(external=True).split('//', 1)[-1][:-1]
    # Siteroot includes domain, but removes http:// or https:// if present, and removes the final forward slash.
    a_text = site_root
    rel_path = '/'

    request_of_concern = True
    for path_to_ignore in ignore_paths_starting_with:
        if request.path.startswith(f'/{path_to_ignore}'):
            request_of_concern = False
            break

    if request_of_concern:

        for rule in app.url_map.iter_rules():
            if "GET" in rule.methods and len(rule.arguments) == 0:
                # Static folder has rule.arguments, so is skipped and rerouted to root.
                if request.path.startswith(rule.rule):  # Rule.rule is relative path.
                    rel_path = url_for(rule.endpoint)
                    if rel_path == '/':
                        continue  # Otherwise, displays final slash after site root <a> text.
                    a_text = f'{site_root}<wbr>{rel_path}'
                    break

        message_body = f'Page not found: \n{request.url}\n' \
                       f'Rendered page_not_found.html and suggested: \n{site_root}{rel_path}'
        admin_alert_thread('Web App - 404', message_body)

    return render_template('page_not_found.html', relpath=rel_path, a_text=a_text), 404


@app.route('/favicon.ico')
def favicon():
    return redirect(url_for('static', filename='favicon.ico'))


@app.route('/new')
def new_calendar():
    return setup_cal_redirect(False)


# Always go through setup_cal_redirect (via repair_calendar or new_calendar endpoints) for validation.
# Never come straight here.
@app.route('/repair', methods=['GET', 'POST'])
def repair_calendar():
    return setup_or_repair_calendar('repair')


# Always go through setup_cal_redirect (via repair_calendar or new_calendar endpoints) for validation.
# Never come straight here.
@app.route('/setup', methods=['GET', 'POST'])
def setup_calendar():
    return setup_or_repair_calendar('setup')


@app.route('/add', methods=['GET', 'POST'])
def add_event():

    if 'n' not in request.args or 'm' not in request.args or 'd' not in request.args:
        return setup_cal_redirect()

    if request.method == 'GET':
        return render_template('add_event.html', go_back_href=url_for_calendar(),
                               calendar_name=request.args['n'], current_year=datetime.now().year)

    # request.method == 'POST':

    if 'event-name' not in request.form or 'date-type' not in request.form \
            or 'cal-year' not in request.form or 'cal-month' not in request.form or 'cal-day' not in request.form \
            or 'gest-week' not in request.form or 'gest-day' not in request.form \
            or 'hour' not in request.form or 'minute' not in request.form or 'am-or-pm' not in request.form:
        return 'Invalid request.'

    # Remove all tildes from event-name, which delimits the url event data.
    new_event_arg_list = [request.form['event-name'].replace('~', '')]

    if request.form['date-type'] == 'cal':
        try:
            cal_date = {
                'year': int(request.form['cal-year']),
                'month': int(request.form['cal-month']),
                'day': int(request.form['cal-day'])
            }
        except:
            # Couldn't parse all date fields. Fields blank or invalid.
            return 'Invalid request.'
        else:
            if cal_date['year'] < 0 or 9999 < cal_date['year'] \
                    or cal_date['month'] < 1 or 12 < cal_date['month'] \
                    or cal_date['day'] < 1 or 31 < cal_date['day']:
                return 'Date out of range.'
            date_str = f"{str(cal_date['year']).zfill(4)}" \
                       f"{str(cal_date['month']).zfill(2)}" \
                       f"{str(cal_date['day']).zfill(2)}"
            new_event_arg_list.append(date_str)

    else:
        # request.form['date-type'] == 'gest':
        try:
            gest_date = {'week': int(request.form['gest-week']), 'day': int(request.form['gest-day'])}
        except:
            # Couldn't parse all date fields. Fields blank or invalid.
            return 'Invalid request.'
        else:
            if gest_date['week'] < 0 or 42 < gest_date['week'] or gest_date['day'] < 0 or 6 < gest_date['day']:
                return 'Date out of range.'
            date_str = f"{str(gest_date['week']).zfill(2)}{gest_date['day']}"
            new_event_arg_list.append(date_str)

    if 'has-time' in request.form:
        if request.form['am-or-pm'] != 'am' and request.form['am-or-pm'] != 'pm':
            return 'Invalid request.'
        try:
            time = {'hour': int(request.form['hour']), 'minute': int(request.form['minute'])}
        except:
            # Couldn't parse all time fields. Fields blank or invalid.
            return 'Invalid request.'
        else:
            if time['hour'] < 1 or 12 < time['hour'] or time['minute'] < 0 or 60 < time['minute']:
                return 'Time out of range.'
            time_str = f"{str(time['hour']).zfill(2)}{str(time['minute']).zfill(2)}{request.form['am-or-pm']}"
            new_event_arg_list.append(time_str)

    if 'e' in request.args:
        all_events_str = f"{request.args['e']}~~"  # Add ~~ to delimit before new event.
    else:
        # No custom events data.
        all_events_str = ''

    all_events_str += '~'.join(new_event_arg_list)
    return redirect(url_for_calendar(e=all_events_str))


@app.route('/remove', methods=['POST'])
def remove_event():

    if 'n' not in request.args or 'm' not in request.args or 'd' not in request.args:
        return setup_cal_redirect()

    if 'e' not in request.args:
        return redirect(url_for_calendar())

    try:
        remove_index = int(request.form['index'])
    except:
        # Index value invalid or missing.
        return 'Invalid request.'

    events_list = events_str_to_list(request.args['e'])

    if 0 <= remove_index < len(events_list):
        del events_list[remove_index]

    new_events_str = '~~'.join(events_list)

    return redirect(url_for_calendar(e=new_events_str))


@app.route('/')
def calendar():

    if 'n' not in request.args:
        # Name arg is required.
        return setup_cal_redirect()

    try:
        int(request.args['m'])
        int(request.args['d'])
    except:
        # Month or day args missing, blank, or not parsable to integers.
        return setup_cal_redirect()

    if 'e' not in request.args:
        if len(request.args) != 3:
            # This redirect will remove all request args besides those passed into url_for.
            return redirect(url_for_calendar())
        new_cal_href = url_for('new_calendar', n=request.args['n'], m=request.args['m'], d=request.args['d'])
        add_event_href = url_for('add_event', n=request.args['n'], m=request.args['m'], d=request.args['d'])
        return render_template('calendar.html', calendar_name=request.args['n'], new_cal_href=new_cal_href,
                               add_event_href=add_event_href)

    # 'e' in request.args

    events_list = events_str_to_list(request.args['e'])
    events_list_validated = get_validated_events_list(events_list)

    print(events_list, events_list_validated)

    if len(events_list_validated) == 0:
        # Remove 'e' from request.args.
        print(url_for_calendar())
        return redirect(url_for_calendar())

    if len(events_list) != len(events_list_validated):
        # Remove invalid events within request.args.
        events_str = '~~'.join(events_list_validated)
        return redirect(url_for_calendar(e=events_str))

    if len(request.args) != 4:
        # This redirect will remove all request args besides those passed into url_for.
        return redirect(url_for_calendar())

    # 'n' in request.args, 'm' and 'd' parsable to ints, 'e' in request.args,
    # len(events_list_validated) != 0, len(events_list) == len(events_list_validated), len(request.args) == 4
    new_cal_href = url_for('new_calendar', n=request.args['n'], m=request.args['m'],
                           d=request.args['d'], e=request.args['e'])
    add_event_href = url_for('add_event', n=request.args['n'], m=request.args['m'],
                             d=request.args['d'], e=request.args['e'])
    return render_template('calendar.html', calendar_name=request.args['n'], new_cal_href=new_cal_href,
                           add_event_href=add_event_href)


if __name__ == '__main__':
    app.run()
