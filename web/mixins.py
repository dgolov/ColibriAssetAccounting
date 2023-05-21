from django.contrib.auth.mixins import LoginRequiredMixin


class UserMixin(LoginRequiredMixin):
    login_url = '/auth'
