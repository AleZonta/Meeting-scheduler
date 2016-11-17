from __future__ import print_function

import copy
import sqlite3

from datetime import timedelta, date
from random import randrange


class pres(object):
    def __init__(self, element):
        self.available = element[0]
        self.group = element[1]
        self.name = element[2]
        self.id = element[3]
        self.note = element[4]
        self.email = element[5]
        self.date = None

    def addDate(self, date):
        self.date = date


class meeting():
    def __init__(self, date, name1, name2):
        self.date = date
        self.first_presenter = name1
        self.second_presenter = name2
        self.location = 19  # ID for N.A.


def organize(max_number_of_meeting_to_organise, all_the_group, mondays):
    different = False
    new_meeting = []
    while not different:
        copy_all_the_group = copy.deepcopy(all_the_group)
        # organise the meeting
        for x in range(max_number_of_meeting_to_organise):
            local_date = mondays[x]
            first_group = randrange(0, len(copy_all_the_group))
            first_name = copy_all_the_group[first_group].pop(0)
            if len(copy_all_the_group[first_group]) == 0:
                copy_all_the_group.pop(first_group)
            second_group = randrange(0, len(copy_all_the_group))
            while first_group == second_group and len(copy_all_the_group) > 1:
                second_group = randrange(0, len(copy_all_the_group))
            second_name = copy_all_the_group[second_group].pop(0)
            if len(copy_all_the_group[second_group]) == 0:
                copy_all_the_group.pop(second_group)
            new_meeting.append(meeting(local_date, first_name, second_name))

        # automatically check if in all the meeting the presenter are different
        equals = True
        for el in new_meeting:
            if el.first_presenter.group == el.second_presenter.group:
                equals = False
                break
        if not equals:
            print("Some meetings have presenter from same group. Try again")
            new_meeting = []
        else:
            different = True

    for el in new_meeting:
        print(el.first_presenter.name + " " + str(
            el.first_presenter.group) + " " + el.second_presenter.name + " " + str(el.second_presenter.group))
    #
    # var = None
    # try:
    #     var = input("Do you accept this setting? 1 -> yes; 2 ->no: ")
    # except:
    #     print("you entered a wrong character")
    # return var, new_meeting
    return new_meeting


def work():
    conn = sqlite3.connect("../../waibase.db")
    c = conn.cursor()

    c.execute('SELECT * FROM {c} WHERE {w}="True"'.format(c="scheduler_presenter", w="available"))
    presenter = c.fetchall()

    c.execute('SELECT * FROM {c} WHERE {w}={i}'.format(c="scheduler_presenter", w="available", i=1))
    presenter += c.fetchall()

    # list_presenter contain the list of all the available presenter
    list_presenter = []
    for el in presenter:
        list_presenter.append(pres(el))

    # check if in the selected period there are already presenter
    start = sqlite3.datetime.date(2017, 1, 9)
    print(start.strftime('%Y-%m-%d'))
    c.execute(
        'SELECT {n},{w} FROM {c} WHERE CAST(strftime("%s", {w})  AS  integer) > CAST(strftime("%s", "{d}")  AS  integer)'.format(
            n="presenter_id", c="scheduler_presentation", w="meeting_id", d=start.strftime('%Y-%m-%d')))
    already_planned = c.fetchall()
    # if the size is more than 0 I have already planned something.
    # need to remove those presenters from the general list
    if len(already_planned) > 0:
        for id_pres in already_planned:
            count = 0
            found = False
            while not found and count < len(list_presenter) - 1:
                if list_presenter[count].id == id_pres[0]:
                    found = True
                    list_presenter.remove(list_presenter[count])
                count += 1

    # now I have the real presenters that I have to organise
    # lets divide them in the group that I know
    # Web & Media = 3
    # CI = 4
    # Agent System = 5
    # KRR = 6
    WM = []
    CI = []
    AS = []
    KRR = []
    for el in list_presenter:
        if el.group == 3:
            WM.append(el)
        if el.group == 4:
            CI.append(el)
        if el.group == 5:
            AS.append(el)
        if el.group == 6:
            KRR.append(el)

    mondays = []
    str_mondays = []
    with open("mondays.txt", "r") as ins:
        for line in ins:
            str_mondays.append(line)
    for el in str_mondays:
        part = el.replace("\n", "").split("-")
        mondays.append(sqlite3.datetime.datetime(int(part[0]), int(part[1]), int(part[2])))

    max_number_of_meeting_to_organise = len(mondays)
    total_length = len(WM) + len(CI) + len(AS) + len(KRR)

    if total_length < max_number_of_meeting_to_organise * 2:
        print("Too many meeting for the number of presenters available")
        max_number_of_meeting_to_organise = total_length / 2

    # how I organise the meeting
    # lets find the order of the presenter per group
    check_start_date = sqlite3.datetime.datetime.now()
    check_start_date = check_start_date - timedelta(days=365)

    all_the_group = [WM, CI, AS, KRR]
    for group in all_the_group:
        for el in group:
            c.execute(
                'SELECT meeting_id FROM {c} WHERE CAST(strftime("%s", {w})  AS  integer) > CAST(strftime("%s", "{d}")  AS  integer) AND {i}={n}'.format(
                    c="scheduler_presentation", w="meeting_id", d=check_start_date.strftime('%Y-%m-%d'),
                    i="presenter_id", n=el.id))
            res = c.fetchall()
            dates = []
            for element in res:
                dates.append(sqlite3.datetime.datetime(*map(int, element[0].split('-'))))
            # if i have more dates I keep only the last one
            if len(dates) > 1:
                min_date = sqlite3.datetime.datetime(1000, 1, 1)
                for dat in dates:
                    if dat > min_date:
                        min_date = dat
                el.addDate(min_date)
            else:
                # check if I have data or not
                # if not set a very old data
                if len(dates) > 0:
                    el.addDate(dates[0])
                else:
                    el.addDate(sqlite3.datetime.datetime.now())

    # now I have the time
    # I order the person inside the group per time. The oldest one is the first one
    for group in all_the_group:
        group.sort(key=lambda x: x.date, reverse=False)

    copy_all_the_groups = copy.deepcopy(all_the_group)

    # res, meetings = organize(max_number_of_meeting_to_organise, copy_all_the_groups, mondays)
    # while res != 1:
    #     copy_all_the_groups = copy.deepcopy(all_the_group)
    #     res, meetings = organize(max_number_of_meeting_to_organise, copy_all_the_groups, mondays)
    conn.commit()
    conn.close()

    return organize(max_number_of_meeting_to_organise, copy_all_the_groups, mondays)


# main
if __name__ == "__main__":

    meetings = work()
    conn = sqlite3.connect("../../waibase.db")
    c = conn.cursor()
    var = None
    while var == None:
        try:
            var = input("Do you wann load this meeting into the database? 1 -> yes; 2 ->no: ")
        except:
            print("you entered a wrong character")

    # if i choose to add the meeting -> var = 1
    if var == 1:
        for el in meetings:
            try:
                # add the meeting
                c.execute("INSERT INTO {tn} ({idf}, {cn}) VALUES ('{idfv}', {cnv})". \
                          format(tn="scheduler_meeting", idf="date", cn="location_id", idfv=el.date.strftime('%Y-%m-%d'), cnv=el.location))
                # retrieve last id for the presenters
                c.execute("SELECT MAX(id) FROM scheduler_presentation")
                res = c.fetchall()
                id_i_need_to_use = res[0][0]
                id_i_need_to_use += 1
                c.execute(
                    "INSERT INTO {tn} ({id}, {meeting_id}, {presenter_id}, slides, title, abstract) VALUES ({id_value}, '{meeting_id_value}', {presenter_id_value},'','','')". \
                        format(tn="scheduler_presentation", id="id", meeting_id="meeting_id", presenter_id="presenter_id",
                               id_value=id_i_need_to_use,
                               meeting_id_value=el.date.strftime('%Y-%m-%d'), presenter_id_value=el.first_presenter.id))
                id_i_need_to_use += 1
                c.execute(
                    "INSERT INTO {tn} ({id}, {meeting_id}, {presenter_id}, slides, title, abstract) VALUES ({id_value}, '{meeting_id_value}', {presenter_id_value},'','','')". \
                        format(tn="scheduler_presentation", id="id", meeting_id="meeting_id", presenter_id="presenter_id",
                               id_value=id_i_need_to_use,
                               meeting_id_value=el.date.strftime('%Y-%m-%d'), presenter_id_value=el.second_presenter.id))
            except Exception as e:
                print(e)
            print("Successfully added meeting")

    conn.commit()
    conn.close()
