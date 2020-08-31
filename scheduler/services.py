import sqlite3



def findNameAndData():
    conn = sqlite3.connect("../../../waibase.db")
    c = conn.cursor()
    start = sqlite3.datetime.datetime.now()
    c.execute(
        'SELECT {n},{w} FROM {c} WHERE CAST(strftime("%s", {w})  AS  integer) > CAST(strftime("%s", "{d}")  AS  integer)'.format(
            n="presenter_id", c="scheduler_presentation", w="meeting_id", d=start.strftime('%Y-%m-%d')))
    already_planned = c.fetchall()


    total_list =[]
    for el in already_planned:
        c.execute('SELECT {a},{b} FROM {c} WHERE id={d}'.format(a="name", b="email", c="scheduler_presenter", d=el[0]))
        data = c.fetchall()
        print(data)
        total_list.append((data[0][0], data[0][1], el[1]))

    return total_list

