from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from .filters import RespToMyAnnounceFilter, MyResponseFilter
from .forms import AnnouncementForm, ResponseForm
from .models import Announcement, ResponseToAnnounce
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.http import Http404

class AnnouncementList(ListView):
    model = Announcement
    ordering = '-published_date'
    template_name = 'announcement_list.html'
    context_object_name = 'list'

    def get_queryset(self):  # сортировка по категориям на главной по ссылкам
        category = self.kwargs.get('category', None)
        if category:
            queryset = Announcement.objects.filter(category=category)
        else:
            queryset = Announcement.objects.all()
        return queryset.order_by(self.ordering)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['promotion'] = Announcement.objects.all().filter(author__username='admin').order_by('-published_date')[0]
        return context


class CreateAnnouncement(LoginRequiredMixin, CreateView):
    form_class = AnnouncementForm
    model = Announcement
    template_name = 'create_announcement.html'

    def get_form_kwargs(self):
        """
        В форме для группы пользователей доступно поле для отправки письма после создания объявления всем.
        В kwargs передается текущий пользователь в форму
        """
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form = AnnouncementForm(self.request.POST)  # данные формы
        form_announce = form.save(commit=False)
        form_announce.author = self.request.user  # подставляем текущего юера в поле автор
        form_announce.save()
        return super().form_valid(form)


class DetailAnnouncement(DetailView):
    model = Announcement
    template_name = 'announce.html'
    context_object_name = 'announce'

    def get_context_data(self, **kwargs):
        """
        В контекст добавляем параметр sent_response, в котором находится отклик пользователя или пустое значение,
        при его отсутствии.
        Т.к. на страницу могут войти незарегистрированные пользователи, фильтр откликов должен быть не по модели,
        а по атрибуту модели, так как у незарегистрированного пользователя модель AnnonimousUser, а атрибут user
        связан с моделью User, из-за чего будет ошибка.
        При фильтации по аттрибуту модели передаются значения атрибутов, а не объекты модели и ошибки не будет.
        """
        context = super().get_context_data(**kwargs)
        context['sent_response'] = ResponseToAnnounce.objects.all().filter(response_announcement__pk=self.kwargs['pk'],
                                                                           user__id=self.request.user.id)
        context['all_responses'] = ResponseToAnnounce.objects.all().filter(response_announcement__pk=self.kwargs['pk'])
        return context


class UpdateAnnouncement(LoginRequiredMixin, UpdateView):
    form_class = AnnouncementForm
    model = Announcement
    template_name = 'edit_announcement.html'


class AddResponse(LoginRequiredMixin, CreateView):
    form_class = ResponseForm
    model = ResponseToAnnounce
    template_name = 'add_response.html'

    def dispatch(self, request, *args, **kwargs):
        """
        Возвращает ошибку 404 если к объявлению нельзя отправить отклик
        obj: объект объявления
        opportunity_to_response: True or False - возможность оставлять отклик
        """
        obj = Announcement.objects.get(id=self.kwargs['pk'])
        if not obj.opportunity_to_response:
            raise Http404()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['responses'] = ResponseToAnnounce.objects.all().filter(response_announcement__pk=self.kwargs['pk'],
                                                                       user=self.request.user)
        return context

    def post(self, request, *args, **kwargs):
        # ограничим возможность отправки нескольких откликов одним пользователем на одно и то же объявление
        sent_response = ResponseToAnnounce.objects.all().filter(response_announcement__pk=self.kwargs['pk'],
                                                                user=self.request.user)
        if sent_response:  # если отклик уже есть, то обновим страницу.
            # В шаблоне будет выведено сообщение, что отклик уже был отправлен
            return redirect('add_response', pk=self.kwargs['pk'])
        return super().post(self, request, *args, **kwargs)

    # в форме нельзя выбрать к какому объявлению мы отправляем отклик, подставляем тут:
    def form_valid(self, form):
        announce = Announcement.objects.get(id=self.kwargs['pk'])  # получаем объявление, на которое отправляем отклик
        form = ResponseForm(self.request.POST)  # получаем значения полей fields из формы
        form_announce = form.save(commit=False)
        form_announce.response_announcement = announce  # дополняем форму объявлением, на которое отправлен отклик
        form_announce.user = self.request.user  # и юзером
        form_announce.save()
        return super().form_valid(form)


class ResponsesToMyAnnounce(LoginRequiredMixin, ListView):
    model = ResponseToAnnounce
    ordering = '-id'
    template_name = 'resp_to_my_announce.html'
    context_object_name = 'responses'

    def get(self, request, *args, **kwargs):
        print(request.META.get('HTTP_REFERER'))
        # get('button') чтобы не получать ошибку при переходе на страницу при отсутствии в request.GET ключа button
        if request.GET.get('button'):
            button = request.GET.get('button')
            response = ResponseToAnnounce.objects.get(pk=request.GET['resp_id'])
            if button == 'Принять':  # помечаем отклики как принятые/отклоненные
                response.accept()
                return redirect(request.META['HTTP_REFERER'])
            elif button == 'Отклонить':
                response.decline()
                return redirect(request.META['HTTP_REFERER'])
        # if request.META.get('HTTP_REFERER') != 'http://127.0.0.1:8000/board/my_announcement/':
        #
        #     return redirect(request.META['HTTP_REFERER'])

        return super().get(self, request, *args, **kwargs)

    def get_queryset(self):
        queryset = ResponseToAnnounce.objects.filter(response_announcement__author=self.request.user)
        self.filterset = RespToMyAnnounceFilter(self.request.GET, queryset)  # фильтр откликов в шаблоне для пользователя
        self.new_response = self.filterset.qs.exclude(accepted=2)  # показываем только новые и принятые отклики
        return self.filterset.qs.order_by(self.ordering)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        context['new_response'] = self.new_response
        context['referer'] = self.request.META
        return context


class MyResponsesList(LoginRequiredMixin, ListView):
    model = ResponseToAnnounce
    ordering = '-id'
    template_name = 'my_responses.html'
    context_object_name = 'my_responses'

    def get_queryset(self):
        queryset = ResponseToAnnounce.objects.filter(user=self.request.user)
        self.filterset = MyResponseFilter(self.request.GET, queryset)
        return self.filterset.qs.order_by(self.ordering)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['filterset'] = self.filterset
        return context

# @login_required
class MyAnnounce(LoginRequiredMixin, ListView):
    model = Announcement
    ordering = '-published_date'
    template_name = 'my_announcement.html'
    context_object_name = 'my_announce'

    def get_queryset(self):
        user = self.request.user
        queryset = Announcement.objects.filter(author=user)
        return queryset.order_by(self.ordering)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # получаем все отклики, которые оставил пользователь
        context['response'] = ResponseToAnnounce.objects.filter(
            response_announcement__author=self.request.user).filter(accepted=0)
        return context


# функция для удаления отклика
def remove_response(request, pk):
    user = request.user
    # получаем все отклики текущего пользователя на выбранное объявление
    response = ResponseToAnnounce.objects.all().filter(response_announcement__pk=pk, user=user)
    response.delete()  # и удаляем
    return HttpResponseRedirect(reverse('announce', args=[pk]))  # перенаправляем на страницу с объявлением


def to_home_page(request):  # перенаправление с SITE_URL на домашнюю страницу
    return redirect('list')


def accept_response(request):
    # get('button') чтобы не получать ошибку при переходе на страницу при отсутствии в request.GET ключа button
    if request.GET.get('button'):
        button = request.GET.get('button')
        response = ResponseToAnnounce.objects.get(pk=request.GET['resp_id'])
        if button == 'Принять':  # помечаем отклики как принятые/отклоненные
            response.accept()
        elif button == 'Отклонить':
            response.decline()
    return HttpResponseRedirect(reverse('responses'))
