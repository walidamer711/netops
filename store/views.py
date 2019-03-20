from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from .models import Store
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView, DeleteView, CreateView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

# Create your views here.

@method_decorator(login_required, name='dispatch')
class StoreList(ListView):
    model = Store

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['item_type'] = self.kwargs['item_type']
        return context
    def get_queryset(self):
        return Store.objects.filter(item_type=self.kwargs['item_type'])

@method_decorator(login_required, name='dispatch')
class ItemCreate(CreateView):
    model = Store
    fields = ['item_type', 'item_model', 'item_quantity', 'item_status', 'comment']

    def get_success_url(self):
        return reverse('store', args=[self.kwargs['item_type']])

    def post(self, request, *args, **kwargs):
        if "cancel" in request.POST:
            return redirect('store', self.kwargs['item_type'])
        else:
            return super(ItemCreate, self).post(request, *args, **kwargs)

@method_decorator(login_required, name='dispatch')
class ItemUpdate(UpdateView):
    model = Store
    fields = ['item_type', 'item_model', 'item_quantity', 'item_status', 'comment']
    template_name = 'store/store_update_form.html'
    pk_url_kwarg = 'item_id'
    context_object_name = 'item'

    def form_valid(self, form):
        form.save()
        return redirect('store', self.kwargs['item_type'])