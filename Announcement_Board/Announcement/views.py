from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .filters import ResponseFilter
from .forms import AnnouncementForm, ResponseForm
from .models import Announcement, ResponseToAnnounce
from django.urls import reverse
from django.contrib.auth.decorators import login_required


class AnnouncementList(ListView):
    model = Announcement
    ordering = '-published_date'
    template_name = 'announcement_list.html'
    context_object_name = 'list'
    
    def get_queryset(self):
        category = self.kwargs.get('category', None)
        if category:
            queryset = Announcement.objects.filter(category=category)
        else:
            queryset = Announcement.objects.all()
        return queryset


class CreateAnnouncement(CreateView):
    form_class = AnnouncementForm
    model = Announcement
    template_name = 'create_announcement.html'

    def form_valid(self, form):
        user_name = self.request.user  #
        form = AnnouncementForm(self.request.POST)  #
        form_announce = form.save(commit=False)
        form_announce.author = user_name  #
        form_announce.save()
        return super().form_valid(form)


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
    
    
class AddResponse(CreateView):
    form_class = ResponseForm
    model = ResponseToAnnounce
    template_name = 'add_response.html'
    
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


class ResponseList(ListView):
    model = ResponseToAnnounce
    ordering = '-id'
    template_name = 'resp_to_my_announce.html'
    context_object_name = 'my_responses'
    
    def get(self, request, *args, **kwargs):
        # get('button') чтобы не получать ошибку при переходе на страницу при отсутствии в request.GET ключа button
        if request.GET.get('button') == 'Принять':
            response = ResponseToAnnounce.objects.get(pk=request.GET['resp_id'])
            response.accept()
        if request.GET.get('button') == 'Отклонить':
            response = ResponseToAnnounce.objects.get(pk=request.GET['resp_id'])
            response.decline()
        return super().get(self, request, *args, **kwargs)
    
    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = ResponseFilter(self.request.GET, queryset)
        self.filter_response = self.filterset.qs.exclude(accepted=False)
        return self.filter_response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем в контекст объект фильтрации.
        context['filter_response'] = self.filter_response
        return context


# @login_required
class MyAnnounce(ListView):
    model = Announcement
    ordering = '-published_date'
    template_name = 'my_announcement.html'
    context_object_name = 'my_announce'

    def get_queryset(self):
        user = self.request.user
        queryset = Announcement.objects.filter(author=user)
        return queryset

    def get_context_data(self, **kwargs):  # TODO надо сделать свой фильтр для вывода кол-ва откликов
        context = super().get_context_data(**kwargs)

        context['response'] = ResponseToAnnounce.objects.filter(response_announcement__author=self.request.user)
        return context


# функция для удаления отклика
def remove_response(request, pk):
    user = request.user
    # получаем все отклики текущего пользователя на выбранное объявление
    response = ResponseToAnnounce.objects.all().filter(response_announcement__pk=pk, user=user)
    response.delete()  # и удаляем
    return HttpResponseRedirect(reverse('announce', args=[pk]))  # перенаправляем на страницу с объявлением


def to_home_page(request):
    return redirect('list')
    