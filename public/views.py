from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


class IndexView(LoginRequiredMixin, TemplateView):
    """
    View to connect to websockets.
    Login from the admin to start.
    """
    template_name = "index.html"


index = IndexView.as_view()
