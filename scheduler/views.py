

import operator
import vobject
from dateutil.tz import gettz

from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render, render_to_response, get_object_or_404, get_list_or_404

# Create your views here.
from django.template import RequestContext
from django.utils.datetime_safe import datetime, date
from django.utils.http import urlquote_plus

from scheduler.mailMessages import getAnnounceHoliday, getNewPersonalScheduleMessage
from scheduler.models import Meeting, Presenter, Presentation, Group, SendRequestForm, SendAnnounceForm
from django.conf import settings

all_the_emails = ['a.c.m.ten.teije@vu.nl', 'a.e.eiben@vu.nl', 'a.e.van.aggelen@vu.nl', 'a.el.hassouni@student.vu.nl', 'a.h.abro@vu.nl', 'a.h.brandenburgh@vu.nl', 'a.h.j.c.a.isaac@vu.nl', 'a.loizou@vu.nl', 'a.manzoorrajper@vu.nl', 'a.nottamkandath@vu.nl', 'a.p.w.eliens@vu.nl', 'a.s.fokkens@vu.nl', 'a.tordai@vu.nl', 'a.van.wissen@vu.nl', 'a.zonta@vu.nl', 'abprieto@udc.es', 'adamou@cs.unibo.it', 'ai.robert.wangshuai@gmail.com', 'albert.merono@vu.nl', 'anca.dumitrache89@googlemail.com', 'anca.dumitrache@vu.nl', 'c.boscarino@vu.nl', 'c.d.m.gueret@vu.nl', 'c.groenouwe@vu.nl', 'c.i.bucur@vu.nl', 'c.n.vander.wal@vu.nl', 'c.r.dijkshoorn@vu.nl', 'c2.gerritsen@vu.nl', 'b.a.kamphorst@vu.nl', 'd.formolo@vu.nl', 'd.j.u.thilakarathne@vu.nl', 'd.spagnuelo@vu.nl', 'd.w.romeroguzman@vu.nl', 'danbri@danbri.org', 'e.den.heijer@vu.nl', 'e.haasdijk@vu.nl', 'e.r.kenny@uva.nl', 'f.a.h.van.harmelen@vu.nl', 'f.both@vu.nl', 'g.karafotias@vu.nl', 'h.g.gao@vu.nl', 'h.leopold@vu.nl', 'j.de.man@vu.nl', 'j.g.hubert@vu.nl', 'j.g.klein@vu.nl', 'j.gordijn@vu.nl', 'j.j.r.donkervliet@vu.nl', 'j.l.top@vu.nl', 'j.r.van.ossenbruggen@vu.nl', 'j.s.mollee@vu.nl', 'j.treur@vu.nl', 'j.urbani@vu.nl', 'j.v.heinerman@vu.nl', 'k.dentler@vu.nl', 'k.milian@vu.nl', 'k.s.m.a.dasilvamirasdearaujo@vu.nl', 'l.dosa@vu.nl', 'l.hollink@vu.nl', 'l.j.rietveld@vu.nl', 'l.k.vander.meij@vu.nl', 'l.m.aroyo@vu.nl', 'l.m.lischke@vu.nl', 'l.medeiros@vu.nl', 'l.moeskops@vu.nl', 'l.p.silvestrin@vu.nl', 'm.a.pontier@vu.nl', 'm.c.schut@vu.nl', 'm.decarlo@vu.nl', 'm.hildebrand@vu.nl', 'm.hoogendoorn@vu.nl', 'm.koorneef@vu.nl', 'm.lovrencak@vu.nl', 'm.otte@vu.nl', 'manolis.stamatogiannakis@vu.nl', 'mar.marcos@uji.es', 'mar.marcos@uji.es', 'o.a.k.idrissou@vu.nl', 'p.a.boncz@vu.nl', 'p.h.m.p.roelofsma@vu.nl', 'p.lago@vu.nl', 'qhu400@vu.nl', 'p.mika@vu.nl', 'r.duell@vu.nl', 'r.g.m.stegers@vu.nl', 'r.gligorov@vu.nl', 'r.h.segers@vu.nl', 'r.j.merk@vu.nl', 'r.m.konijn@vu.nl', 'r.m.van.lambalgen@vu.nl', 's.bocconi@vu.nl', 's.fundatureanu@vu.nl', 's.klarman@vu.nl', 's.magliacane@vu.nl', 's.s.m.z.mohammadiziabari@vu.nl', 's.tabatabaei@vu.nl', 's.ter.braake@vu.nl', 't.bosse@vu.nl', 'v.a.n.m.vander.goes@vu.nl', 'v.d.b.dibernardo@student.vu.nl', 'v.de.boer@vu.nl', 'v.maccatrozzo@vu.nl', 'v.n.stebletsova@vu.nl', 'v.a.n.m.vander.goes@vu.nl', 'v.d.b.dibernardo@student.vu.nl', 'v.de.boer@vu.nl', 'v.maccatrozzo@vu.nl', 'v.n.stebletsova@vu.nl', 'ytan@feweb.vu.nl', 'x.pan@vu.nl', 'z.huang@vu.nl', 'z.szlavik@vu.nl', 'v.p.de.kemp@vu.nl', 'veruskacz@gmail.com', 'vu@peterbloem.nl', 'v.p.de.kemp@vu.nl', 'veruskacz@gmail.com', 'vu@peterbloem.nl', 't.kuhn@vu.nl', 's.wang@vu.nl', 'slv.giannini@gmail.com', 'spyros.kotoulas@gmail.com', 'r.siebes@vu.nl', 'renzoangles@gmail.com', 'ruud@stegers.info', 'p.t.groth@vu.nl', 'p.van.maanen@vu.nl', 'pgroth@gmail.com', 'o.sharpanskykh@vu.nl', 'oana.inel@vu.nl', 'marieke.van.erp@dh.huc.knaw.nl', 'n.de.carvalhoferreira@vu.nl', 'n.m.mogles@vu.nl', 'niels.ockeloen@vu.nl', 'martine.de.vos@vu.nl', 'me@wouterbeek.com', 'michel.klein@vu.nl', 'laurens.rietveld@vu.nl', 'lilimelgar@gmail.com', 'lists.charlaganov@vu.nl', 'k.s.schlobach@vu.nl', 'k.v.hindriks@gmail.com', 'kgf300@vu.nl', 'j.wielemaker@vu.nl', 'jha400@student.vu.nl', 'jhulstijn@feweb.vu.nl', 'hans.akkermans@akmc.nl', 'i.malavolta@vu.nl', 'i.s.razozapata@vu.nl', 'i.tiddi@vu.nl', 'hrbazoo@gmail.com', 'hyperir@gmail.com', 'g.modena@vu.nl', 'gks290@vu.nl', 'f.den.hengst@vu.nl', 'filip.dbrsk@gmail.com', 'finn.potason@gmail.com', 'e.van.krieken@vu.nl', 'elly.lammers@vu.nl', 'erman.acar@vu.nl', 'davide.ceolin@gmail.com', 'derijke@uva.nl', 'dick.bulterman@cwi.nl', 'b.bredeweg@uva.nl', 'b.m.tesfa@student.vu.nl', 'b.timmermans@vu.nl', 'cburgemeestre@feweb.vu.nl', 'chris@vanaart.com', 'andreas.steyven@gmail.com', 't.singam@uva.nl']

def index(request):
    year = datetime.now().year
    return HttpResponseRedirect("/schedule/schedule/%s" % year)


def presentations(request):
    # Get the list of all presentations
    presentation_list = Presentation.objects.order_by('-meeting__date')

    # Set the context
    context = {
        'presentation_list': presentation_list
    }

    return render(request, 'presentations.html', context)


def presentation_detail(request, presentation_id):
    # Get this presentation
    presentation = get_object_or_404(Presentation, id=presentation_id)

    # Get the list of all presentations by the same presenter
    presentation_list = get_list_or_404(Presentation, presenter=presentation.presenter)

    # Set the context
    context = {
        'presentation': presentation,
        'presentation_list': presentation_list
    }

    return render(request, 'presentation_detail.html', context)


def meeting(request, year, month, day):
    # Get this presentation
    dates = datetime(int(year), int(month), int(day))
    meeting = get_object_or_404(Meeting, date=dates)

    # Set the context
    context = {
        'date': dates,
        'meeting': meeting,
        'url': request.build_absolute_uri(),
        'url2': urlquote_plus(request.build_absolute_uri())
    }

    return render(request, 'meeting.html', context)


def groups(request):
    group_list = Group.objects.order_by('name')
    context = {
        'group_list': group_list
    }
    return render(request, 'groups.html', context)


def group_detail(request, group_id):
    presenter_list = get_list_or_404(Presenter, group=group_id)
    context = {
        'presenter_list': presenter_list,
        'group_name': Group.objects.get(id=group_id).name
    }
    return render(request, 'group_detail.html', context)


def presenters(request):
    group_list = Group.objects.order_by('name')
    presenter_list = Presenter.objects.order_by('name')
    context = {
        'group_list': group_list,
        'presenter_list': presenter_list,
    }
    return render(request, 'presenters.html', context)


def presenter_detail(request, presenter_id):
    presenter = get_object_or_404(Presenter, id=presenter_id)
    presentation_list = presenter.presentation_set.all()

    context = {
        'presenter': presenter,
        'presentation_list': presentation_list
    }

    return render(request, 'presenter_detail.html', context)


def schedules(request):
    # Find first and last event
    first = Meeting.objects.order_by('date')[0]
    last = Meeting.objects.order_by('-date')[0]

    # Create the list of years and the presentations count
    years_list = {}
    for i in range(first.date.year, last.date.year + 1):
        years_list["%d" % i] = Meeting.objects.filter(date__year=i).count()

    context = {
        'years_list': years_list,
    }

    return render(request, 'schedules.html', context)


def schedule_year(request, year):
    meetings_list = Meeting.objects.filter(date__year=year).order_by('date')
    for meeting in meetings_list:
        if meeting.days_offset() >= 0:
            meeting.nextMeeting = True
            break
    presenters = Presenter.objects.filter(available=True)
    presenter_list = list()
    for presenter in presenters:
        last = presenter.last_presentation()
        if last == 'None':
            last = date(1970, 1, 1)
        if last < date.today():
            presenter_list.append({'presenter': presenter, 'date': last})

    context = {
        'meetings_list': meetings_list,
        'reserve_list': sorted(presenter_list, key=operator.itemgetter('date')),
        'year': year
    }

    return render(request, 'schedule_year.html', context)


def schedule_ics(request):
    meetings_list = Meeting.objects.order_by('date')

    # tz = pytz.timezone('Europe/Amsterdam')

    cal = vobject.iCalendar()
    cal.add('method').value = 'PUBLISH'  # IE/Outlook needs this

    for meeting in meetings_list:
        # date = datetime(meeting.date.year, meeting.date.month, meeting.date.day, tzinfo=zoneinfo('Europe/Amsterdam'))
        # date = datetime(meeting.date.year, meeting.date.month, meeting.date.day, tzinfo=tz)
        # date = datetime(meeting.date.year, meeting.date.month, meeting.date.day)
        date = datetime(meeting.date.year, meeting.date.month, meeting.date.day, 0, 0, 0, 0, gettz('Europe/Amsterdam'))
        vevent = cal.add('vevent')

        # UID
        vevent.add('uid').value = "WAI-%s@wai.few.vu.nl" % meeting.date

        # Begin and end
        vevent.add('dtstart').value = date.replace(hour=16)
        vevent.add('dtend').value = date.replace(hour=17)

        # Creation date
        vevent.add('dtstamp').value = datetime.utcnow()

        # Title, location and description
        vevent.add('summary').value = "WAI meeting : %s" % meeting.presenters()
        vevent.add('location').value = meeting.location.name
        text = ""
        for p in meeting.presentation_set.all():
            text += "%s : %s\n%s\n\n" % (p.presenter.name, p.title, p.abstract)
        vevent.add('description').value = text

    icalstream = cal.serialize()
    response = HttpResponse(icalstream, content_type='text/calendar')
    response['Filename'] = 'export.ics'  # IE needs this
    response['Content-Disposition'] = 'attachment; filename=export.ics'

    return response


def raw_mails(request):
    message = "";
    for presenter in Presenter.objects.order_by('name'):
        if presenter.available:
            message += "\"" + presenter.name + "\" <" + presenter.email + ">, "
    response = HttpResponse(message, mimetype='text/plain')
    response['Filename'] = 'mails.txt'
    response['Content-Disposition'] = 'attachment; filename=mails.txt'
    return response


def send_announce(request):
    from mailMessages import getAnnounceMessage, getAnnounceSubject
    from mailHelper import mailWai
    from emailsettings import helper

    help = helper()

    # Code for the auto-mailer
    if type(request) == str:
        meeting = get_object_or_404(Meeting, date=request)

        subject = "[WAI-meetings] " + getAnnounceSubject(meeting.date.strftime("%d %B %Y"), meeting.presenters(),
                                                         meeting.location.name)
        presenters = []
        presenter_email = []

        for pres in meeting.presentation_set.all():
            presenter = {
                'name': pres.presenter.name,
                'title': pres.title,
                'abstract': pres.abstract
            }
            presenters.append(presenter)
            presenter_email.append(pres.presenter.email)

        message = getAnnounceMessage(meeting.date.strftime("%d %B %Y"), meeting.location.name, presenters,
                                     help.EMAIL_FOOTER())

        mailWai(subject, message, help.EMAIL_SENDER(), help.EMAIL_ANOUNCEMENT_RECIPIENTS(), presenter_email)

    # Code for the website mailing buttons
    else:
        meeting = get_object_or_404(Meeting, date=request.GET['id'])

        subject = "[WAI-meetings] " + getAnnounceSubject(meeting.date.strftime("%d %B %Y"), meeting.presenters(), meeting.location.name)
        presenters = []
        presenter_email = []
        for pres in meeting.presentation_set.all():
            presenter = {
                'name': pres.presenter.name,
                'title': pres.title,
                'abstract': pres.abstract
            }
            presenters.append(presenter)
            presenter_email.append(pres.presenter.email)
        message = getAnnounceMessage(meeting.date.strftime("%d %B %Y"), meeting.location.name, presenters,
                                     help.EMAIL_FOOTER())
        mailWai(subject, message, help.EMAIL_SENDER(), help.EMAIL_ANOUNCEMENT_RECIPIENTS(), presenter_email)
        return HttpResponseRedirect("/schedule")


def send_request(request):
    from mailMessages import getRequestMessage, getRequestSubject
    from mailHelper import mailWai
    from emailsettings import helper

    help = helper()
    # Code for the auto-mailer
    if type(request) == str:
        meeting = get_object_or_404(Meeting, date=request)
        subject = getRequestSubject()

        presenters = ""
        for pres in meeting.presentation_set.all():
            a = pres.presenter.name.split(' ')
            presenters += "%s, " % a[0]

        message = getRequestMessage(presenters, meeting.date.strftime("%d %B %Y"), help.EMAIL_FOOTER())
        to = help.EMAIL_REQUEST_ABSTRACT_CC()
        for pres in meeting.presentation_set.all():
            to.append(pres.presenter.email)
#        if len(to) > 1:
#            mailWai(subject, message, help.EMAIL_SENDER(), to)

            # Code for the website mailing buttons
    else:
        meeting = get_object_or_404(Meeting, date=request.GET['id'])
        subject = getRequestSubject()

        presenters = ""
        for pres in meeting.presentation_set.all():
            a = pres.presenter.name.split(' ')
            presenters += "%s, " % a[0]

        message = getRequestMessage(presenters, meeting.date.strftime("%d %B %Y"), help.EMAIL_FOOTER())
        to = help.EMAIL_REQUEST_ABSTRACT_CC()
        for pres in meeting.presentation_set.all():
            to.append(pres.presenter.email)

        mailWai(subject, message, help.EMAIL_SENDER(), to)
        return HttpResponseRedirect("/schedule")

def send_ping(request):
    from mailMessages import getNewScheduleSubject
    from emailsettings import helper
    from scheduler.mailHelper import mailWai

    help = helper()
    meeting = get_object_or_404(Meeting, date=request.GET['id'])
    subject = getNewScheduleSubject()
    presenters = []
    emails = []
    for pres in meeting.presentation_set.all():
        presenters.append(pres.presenter.name)
        emails.append(pres.presenter.email)

    for i in range(len(presenters)):
        presenter = presenters[i]
        email = emails[i]
        message = getNewPersonalScheduleMessage(presenter, meeting, help.PRESENTER_NAME(), help.EMAIL_FOOTER())
        # print("{}, {}, {}, {}, {}".format(subject, message, help.EMAIL_SENDER(), email, []))
        mailWai(subject, message, help.EMAIL_SENDER(), [email], [])

    return HttpResponseRedirect("/schedule")

def send_alert(request):
    from scheduler.mailMessages import getNewScheduleSubject, getNewScheduleMessage
    from scheduler.mailHelper import mailWai
    from scheduler.services import findNameAndData
    from emailsettings import helper

    subject = getNewScheduleSubject()

    help = helper()
    message = getNewScheduleMessage(help.PRESENTER_NAME(), help.EMAIL_FOOTER())
    presenter_email = []
    mailWai(subject, message, help.EMAIL_SENDER(), help.EMAIL_ANOUNCEMENT_RECIPIENTS(), presenter_email)

    # send an email to everyone with their data

#    total_list = findNameAndData()
#    message = getNewPersonalScheduleMessage(total_list[0][0], total_list[0][2], help.PRESENTER_NAME(), help.EMAIL_FOOTER())
#    presenter_email = []
#    mailWai(subject, message, "test@gmail.com", ["salvarosacity@gmail.com"], presenter_email)

#    message = getNewPersonalScheduleMessage(total_list[1][0], total_list[1][2], help.PRESENTER_NAME(), help.EMAIL_FOOTER())
#    presenter_email = []
#    mailWai(subject, message, "test@gmail.com", ["salvarosacity@gmail.com"], presenter_email)


    return HttpResponseRedirect("/schedule")


def send_custom(request):
    from mailHelper import mailWai
    from emailsettings import helper

    help = helper()
    subject = "[WAI-meetings][Long Meetings] Results from the votation + call for presenters"

    message = "Dear All,"
    message += "<br><br>"
    message += "24 people voted at the online doodle. The pic shows the results:"
    message += "<br>"
    message += "<img src='https://www.cs.vu.nl/ci/plot.png' height='414' width='585'><br>"
    message += "The most voted subjects are: <br>"
    message += "<ul>"
    message += "<li>Explainable AI</li>"
    message += "<li>AI for data preparation and data engineering</li>"
    message += "<li>Reinforcement Learning</li>"
    message += "<li>AI with Humans in the Loops</li>"
    message += "<li>Combination of symbolic and sub-symbolic AI</li>"
    message += "<li>Large Scale Machine Learning</li>"
    message += "<li>The Statistics done wrong</li>"
    message += "</ul><br><br>"
    message += "One of the ideas discussed in January was to have external speakers for these talks (50 minutes + 10)<br>"
    message += "I am asking for your help in order to find speakers for these dates:<br>"
    message += "<ul>"
    message += "<li>11 March 2019</li>"
    message += "<li>08 April 2019</li>"
    message += "<li>20 May 2019</li>"
    message += "<li>17 June 2019</li>"
    message += "</ul><br><br>"
    message += "Thank you very much!<br>"
    message += "Best, WAI Administrator"

    #all_the_emails = ['a.zonta@vu.nl']
    all_the_senior_members = ['a.e.eiben@vu.nl', 'm.hoogendoorn@vu.nl', 'd.m.roijers@vu.nl', 'k.v.hindriks@vu.nl', 'a.t.van.halteren@vu.nl',
                              'c2.gerritsen@vu.nl', 'michel.klein@vu.nl', 'v.n.stebletsova@vu.nl', 'v.de.boer@vu.nl', 't.kuhn@vu.nl',
                              'j.r.ossenbruggen@vu.nl', 'f.a.h.van.harmelen@vu.nl', 'a.c.m.ten.teije@vu.nl', 'k.s.schlobachvu.nl']
    for email in all_the_emails:
        em = []
        em.append(email)
        mailWai(subject, message, help.EMAIL_SENDER(), em, [])

    return HttpResponseRedirect("/schedule")

def generate(request):
    return render(request, 'generate.html')

def send_announce_second(request):
    from mailMessages import getAnnounceMessage, getAnnounceSubject
    from mailHelper import mailWai
    from emailsettings import helper

    help = helper()
    meeting = get_object_or_404(Meeting, date=request.GET['id'])
    subject = "[WAI-meetings]" + getAnnounceSubject(meeting.date.strftime("%d %B %Y"), meeting.presenters(), meeting.location.name)
    presenters = []
    presenter_email = []
    for pres in meeting.presentation_set.all():
        presenter = {
            'name': pres.presenter.name,
            'title': pres.title,
            'abstract': pres.abstract
        }
        presenters.append(presenter)
        presenter_email.append(pres.presenter.email)
    message = getAnnounceMessage(meeting.date.strftime("%d %B %Y"), meeting.location.name, presenters,
                                 help.EMAIL_FOOTER())
    all_the_emails = ["salvarosacity@hotmail.it"]
    for email in all_the_emails:
        em = []
        em.append(email)
        mailWai(subject, message, help.EMAIL_SENDER(), em, [])

    return HttpResponseRedirect("/schedule")
