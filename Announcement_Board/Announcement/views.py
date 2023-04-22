from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .forms import AnnouncementForm, ResponseForm
from .models import Announcement, ResponseToAnnounce
from django.urls import reverse

class AnnouncementList(ListView):
    model = Announcement
    ordering = '-published_date'
    template_name = 'announcement_list.html'
    context_object_name = 'list'
    
    
class CreateAnnouncement(CreateView):
    form_class = AnnouncementForm
    model = Announcement
    template_name = 'create_announcement.html'
    
    
class DetailAnnouncement(DetailView):
    model = Announcement
    template_name = 'announce.html'
    context_object_name = 'announce'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        username = self.request.user.username
        context['responses'] = ResponseToAnnounce.objects.all().filter(response_announcement__pk=self.kwargs['pk'],
                                                                       user__username=username)
        return context
    
    
class UpdateAnnouncement(UpdateView):
    form_class = AnnouncementForm
    model = Announcement
    template_name = 'edit_announcement.html'
    
    
class Response(CreateView):
    form_class = ResponseForm
    model = ResponseToAnnounce
    template_name = 'response.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        username = self.request.user.username
        context['responses'] = ResponseToAnnounce.objects.all().filter(response_announcement__pk=self.kwargs['pk'],
                                                                       user__username=username)
        return context
    
    # в форме нельзя выбрать к какому объявлению мы отправляем отклик
    # поэтому нужное объявление нужно получить из формы и подставить в модель
    def form_valid(self, form):
        announce = Announcement.objects.get(id=self.kwargs['pk'])  # получаем объявление, на которое отправляем отклик
        user_name = self.request.user  # получаем текущего юзера
        form = ResponseForm(self.request.POST)  # получаем значения полей fields из формы
        form_announce = form.save(commit=False)
        form_announce.response_announcement = announce  # дополняем форму объявлением, на которое отправлен отклик
        form_announce.user = user_name  # и юзером
        form_announce.save()
        return super().form_valid(form)


# функция для удаления отклика
def remove_response(request, pk):
    user = request.user
    # получаем все отклики текущего пользователя на выбранное объявление
    response = ResponseToAnnounce.objects.all().filter(response_announcement__pk=pk, user=user)
    response.delete()  # и удаляем
    return HttpResponseRedirect(reverse('announce', args=[pk]))  # перенаправляем на страницу с объявлением
    