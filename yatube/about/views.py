from django.views.generic.base import TemplateView

from yatube.settings import HTML_S


class AboutAuthorView(TemplateView):
    template_name = HTML_S['h_author']


class AboutTechView (TemplateView):
    template_name = HTML_S['h_tech']
