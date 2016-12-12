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


from scheduler.models import Meeting, Presenter, Presentation, Group, SendRequestForm, SendAnnounceForm
from django.conf import settings


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
        return HttpResponseRedirect("/schedule/schedule")


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
        message = getRequestMessage(presenters, meeting.date.strftime("%d %B %Y"), help.EMAIL_FOOTER)
        # cc = settings.EMAIL_REQUEST_ABSTRACT_CC
        to = []
        for pres in meeting.presentation_set.all():
            if len(pres.abstract) == 0:
                to.append(pres.presenter.email)
        if len(to) > 0:
            to.append(help.EMAIL_REQUEST_ABSTRACT_CC())
            mailWai(subject, message, help.EMAIL_SENDER, to)

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
        return HttpResponseRedirect("/schedule/schedule")


def send_alert(request):
    from scheduler.mailMessages import getNewScheduleSubject, getNewScheduleMessage
    from scheduler.mailHelper import mailWai

    from emailsettings import helper

    subject = getNewScheduleSubject()

    help = helper()
    message = getNewScheduleMessage(help.PRESENTER_NAME(), help.EMAIL_FOOTER)
    presenter_email = []
    mailWai(subject, message, help.EMAIL_SENDER(), help.EMAIL_ANOUNCEMENT_RECIPIENTS(), presenter_email)
    return HttpResponseRedirect("/schedule/schedule")


def generate(request):
    return render(request, 'generate.html')
