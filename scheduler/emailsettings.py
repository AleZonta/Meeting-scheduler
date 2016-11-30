class helper():
    def EMAIL_HOST(self):
        return "top.few.vu.nl"  # this one does not need authentication

    def EMAIL_PORT(self):
        return 25

    def EMAIL_USE_TLS(self):
        return False

    def EMAIL_SENDER(self):
        # return "wai-organization@few.vu.nl"
        return "salvarosacity@hotmail.it"

    def EMAIL_ANOUNCEMENT_RECIPIENTS(self):
        # return ['wai-meetings@few.vu.nl']
        return ["zohal@gmail.com"]

    def EMAIL_REQUEST_ABSTRACT_CC(self):
        # return ['wai-organization@few.vu.nl']
        return ['salvarosacity@hotmail.it']

    def EMAIL_FOOTER(self):
        return "Best, Amin and Alessandro"
