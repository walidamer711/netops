from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from .models import Projects, Tasks
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView, DeleteView, CreateView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
# Create your views here.

def projects(request):
    tasks = Tasks.objects.filter(project__project_name='project1')
    return render(request, 'projects.html', {"tasks":tasks})

@method_decorator(login_required, name='dispatch')
class ProjectList(ListView):
    model = Projects

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

@method_decorator(login_required, name='dispatch')
class ProjectCreate(CreateView):
    model = Projects
    fields = ['project_name']
    success_url = reverse_lazy('projects')

    def post(self, request, *args, **kwargs):
        if "cancel" in request.POST:
            return redirect('projects')
        else:
            return super(ProjectCreate, self).post(request, *args, **kwargs)

@method_decorator(login_required, name='dispatch')
class TaskList(ListView):
    model = Tasks

    def get_queryset(self):
        return Tasks.objects.filter(project__id=self.kwargs['project_id'], is_completed=False)

    def get_context_data(self, **kwargs):
        context = super(TaskList, self).get_context_data(**kwargs)
        context['project'] = Projects.objects.get(id=self.kwargs['project_id'])
        return context


@method_decorator(login_required, name='dispatch')
class TaskCreate(CreateView):
    model = Tasks
    fields = ['task', 'status', 'assignee']
    pk_url_kwarg = 'project_id'
    success_url = reverse_lazy('projects')
    initial = {'status': 'in progress'}

    def form_valid(self, form):
        form.instance.project = Projects.objects.get(pk=self.kwargs['project_id'])
        form.save()
        return redirect('project', project_id=self.kwargs['project_id'])

    def post(self, request, *args, **kwargs):
        if "cancel" in request.POST:
            return redirect('project', project_id=self.kwargs['project_id'])
        else:
            return super(TaskCreate, self).post(request, *args, **kwargs)


'''
    def get_form(self, form_class):
        form = super(TaskCreate, self).get_form(form_class)
        form.fields['task'].widget = forms.PasswordInput()
        return form
'''




'''
    def get_success_url(self):
        return redirect('project', project_id=self.kwargs['project_id'])
    def get_queryset(self):
        return Tasks.objects.filter(project__id=self.kwargs['project_id'])
    def form_valid(self, form):
        self.object = self.get_object()
        self.object.save()
        return redirect('project', project_id=self.kwargs['project_id'])
'''

@method_decorator(login_required, name='dispatch')
class TaskUpdate(UpdateView):
    model = Tasks
    fields = ['task', 'status', 'assignee', 'is_completed']
    template_name = 'projects/Tasks_update_form.html'
    pk_url_kwarg = 'task_id'
    context_object_name = 'task'

    def form_valid(self, form):
        form.save()
        return redirect('project', project_id=self.kwargs['project_id'])

@method_decorator(login_required, name='dispatch')
class TaskDelete(DeleteView):
    model = Tasks
    pk_url_kwarg = 'task_id'
    #return reverse_lazy( 'single_post', kwargs={'post.id': post.id})

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return redirect('project', project_id=self.kwargs['project_id'])

    def post(self, request, *args, **kwargs):
        if "cancel" in request.POST:

            return redirect('project', project_id=self.kwargs['project_id'])
        else:
            return self.delete(request, *args, **kwargs)