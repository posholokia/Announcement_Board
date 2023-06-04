from django.shortcuts import redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .filters import ResponseFilter
from .forms import AnnouncementForm, ResponseForm
from .models import Announcement, ResponseToAnnounce
from django.http import Http404
from django.urls import reverse_lazy


class AnnouncementList(ListView):
    model = Announcement
    ordering = '-date'
    template_name = 'announcement_list.html'
    context_object_name = 'list'
    paginate_by = 10

    def get_queryset(self):
        """
        На главной странице в блоке cat содержатся ссылки на страницы объявлений по категориям
        Категория передается в kwargs и соответствует категории в модели Announcement.
        Если категория передана, то возвращает объекты соответсвующие переданной категории,
        если нет, то выводим все объявления
        """
        category = self.kwargs.get('category', None)
        if category:
            queryset = Announcement.objects.filter(category=category)
        else:
            queryset = Announcement.objects.all()
        return queryset.order_by(self.ordering)

    def get_context_data(self, **kwargs):
        """
        promotion: последнее объявление опубликованное пользователем из группы administators. Выводится в блоке headnews
        """
        context = super().get_context_data(**kwargs)
        context['promotion'] = Announcement.objects.all().filter(
            author__groups__name='administators').order_by(self.ordering)[0]
        return context


class CreateAnnouncement(LoginRequiredMixin, CreateView):
    form_class = AnnouncementForm
    model = Announcement
    template_name = 'create_announcement.html'

    def get_form_kwargs(self):
        """
        В форме для персонала сайта доступно поле для отправки письма после создания объявления всем.
        В kwargs передается текущий пользователь в форму, где проверяется относится ли он к группе administators
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
    template_name = 'detail_announce.html'
    context_object_name = 'announce'

    def get_context_data(self, **kwargs):
        """
        Т.к. на страницу могут войти незарегистрированные пользователи, фильтр откликов должен быть не по модели,
        а по атрибуту модели, так как у незарегистрированного пользователя модель AnnonimousUser, а атрибут user
        связан с моделью User, из-за чего будет ошибка. А при фильтации по аттрибуту модели передаются значения
        атрибутов, а не объекты модели и ошибки не будет.

        sent_response: qs из принятых и не рассмотренных откликов. Если пользователь не отправил отклик или его
        отклонили, появится кнопка отправить отклик.
        all_responses: список всех откликов. Для вывода количества откликов в шаблоне
        """
        context = super().get_context_data(**kwargs)
        context['sent_response'] = ResponseToAnnounce.objects.all().filter(response_announcement__pk=self.kwargs['pk'],
                                                                           user__id=self.request.user.id).exclude(
            accepted=2)
        context['all_responses'] = ResponseToAnnounce.objects.all().filter(response_announcement__pk=self.kwargs['pk'])
        return context


class UpdateAnnouncement(LoginRequiredMixin, UpdateView):
    form_class = AnnouncementForm
    model = Announcement
    template_name = 'edit_announcement.html'


class DeleteAnnounce(PermissionRequiredMixin, DeleteView):
    """
    Права у группы administators
    """
    permission_required = 'Announcement.delete_announcement'
    model = Announcement
    template_name = 'announce_delete.html'
    success_url = reverse_lazy('list')


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
                                                                       user=self.request.user).exclude(accepted=2)
        return context

    def post(self, request, *args, **kwargs):
        """
        Пользователь может повторно отправить отклик только если его отклонили
        sent_response: qs из откликов в статусе "Не рассмотрено" или "Принято"
        Если sent_response не пустой, то обновим страницу. В шаблоне выводится сообщение, что отклик уже был отправлен
        """
        sent_response = ResponseToAnnounce.objects.all().filter(response_announcement__pk=self.kwargs['pk'],
                                                                user=self.request.user).exclude(accepted=2)
        if sent_response:
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
    """
    Представление откликов на объявления которые создал пользователь
    """
    model = ResponseToAnnounce
    ordering = '-id'
    template_name = 'resp_to_my_announce.html'
    context_object_name = 'responses'
    paginate_by = 10

    def get(self, request, *args, **kwargs):
        """
        Обработка нажатия кнопки Принять/Отклонить отклик.
        После обработки кнопки для сохранения фильтации и пагинации возвращает на тот же url
        где находился пользователь при нажатии кнопки.
        Если из-за фильтации количество страниц в пагинации стало меньше, и пользователь был на последней странице,
        которой больше нет, в конструкции try-except корректируется url
        """
        if request.GET.get('button'):
            button = request.GET.get('button')
            response = ResponseToAnnounce.objects.get(pk=request.GET['resp_id'])
            if button == 'Принять':  # помечаем отклики как принятые/отклоненные
                response.accept()
                return redirect(request.META['HTTP_REFERER'])
            elif button == 'Отклонить':
                response.decline()
                return redirect(request.META['HTTP_REFERER'])
        try:
            return super().get(self, request, *args, **kwargs)
        except Http404:
            url = request.META.get('HTTP_REFERER')
            last_page = url.split('page=')[1]
            url = url.replace(f'page={last_page}', f'page={int(last_page) - 1}')
            return redirect(url)

    def get_queryset(self):
        """
        queryset: отклики на объявления которые опубликованы текущим пользователем
        """
        queryset = ResponseToAnnounce.objects.filter(response_announcement__author=self.request.user)
        self.filterset = ResponseFilter(self.request.GET, queryset)  # фильтр откликов в шаблоне для пользователя
        return self.filterset.qs.order_by(self.ordering)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context


class MyResponsesList(LoginRequiredMixin, ListView):
    """
    Представление откликов, которые оставил пользователь на чужие объявления
    """
    model = ResponseToAnnounce
    ordering = '-id'
    template_name = 'my_responses.html'
    context_object_name = 'my_responses'
    paginate_by = 10

    def get_queryset(self):
        queryset = ResponseToAnnounce.objects.filter(user=self.request.user)
        self.filterset = ResponseFilter(self.request.GET, queryset)
        return self.filterset.qs.order_by(self.ordering)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['filterset'] = self.filterset
        return context


class MyAnnounce(LoginRequiredMixin, ListView):
    """
    Представление объявлений, созданных пользователем
    """
    model = Announcement
    ordering = '-date'
    template_name = 'my_announcement.html'
    context_object_name = 'my_announce'
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        queryset = Announcement.objects.filter(author=user)  # объявления созданные текущим пользователем
        return queryset.order_by(self.ordering)

    def get_context_data(self, **kwargs):
        """
        response: не рассмотренные (новые) отклики на объявления автора.
        Передаем в шаблон для вывода количества новых откликов
        """
        context = super().get_context_data(**kwargs)
        context['response'] = ResponseToAnnounce.objects.filter(
            response_announcement__author=self.request.user).filter(accepted=0)
        return context


def to_home_page(request):  # перенаправление с SITE_URL на домашнюю страницу
    return redirect('list')

# # функция для удаления отклика
# def remove_response(request, pk):
#     user = request.user
#     # получаем все отклики текущего пользователя на выбранное объявление
#     response = ResponseToAnnounce.objects.all().filter(response_announcement__pk=pk, user=user)
#     response.delete()  # и удаляем
#     return HttpResponseRedirect(reverse('announce', args=[pk]))  # перенаправляем на страницу с объявлением
