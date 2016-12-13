class helper():
    def EMAIL_HOST(self):
        return "top.few.vu.nl"  # this one does not need authentication

    def EMAIL_PORT(self):
        return 25

    def EMAIL_USE_TLS(self):
        return False

    def EMAIL_SENDER(self):
        return "wai-organization@few.vu.nl"


    def EMAIL_ANOUNCEMENT_RECIPIENTS(self):
        return ['wai-meetings@few.vu.nl']


    def EMAIL_REQUEST_ABSTRACT_CC(self):
        return ['wai-organization@few.vu.nl']


    def EMAIL_FOOTER(self):
        return "Best, Amin and Alessandro"

    def PRESENTER_NAME(self):
        return "me and Amin"
