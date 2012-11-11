from django.views.generic import ListView, DetailView
from django.http import Http404
from django.shortcuts import get_object_or_404
from models import MultilingualPage

class IndexView(ListView):
    model = MultilingualPage
    template_name = 'index.html'
    
class MultilingualPageView(DetailView):
    template_name = 'detail.html'
    def get_object(self):
        return get_object_or_404(MultilingualPage, slug=self.kwargs['slug'])