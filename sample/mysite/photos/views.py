from django.views.generic import ListView, CreateView
from .models import Photo
from .forms import PhotoForm

class PhotoListView(ListView):
    model = Photo
    context_object_name = 'photo_list'
    template_name = "photos/index.html"

class PhotoCreateView(CreateView):
    model = Photo
    form_class = PhotoForm
    template_name = "photos/form.html"
    success_url = '/'
