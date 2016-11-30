from django.core.mail import EmailMultiAlternatives
from HTMLParser import HTMLParser


class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


def mailWai(subject, message, sender, to, bcc=[]):
    msg = EmailMultiAlternatives(subject, strip_tags(message), sender, to, bcc)
    msg.attach_alternative(message, "text/html")
    msg.send()
