from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from ..models import WorkOrder

class WorkOrderListView(LoginRequiredMixin, ListView):
    model = WorkOrder
    template_name = 'service/workorder_list.html'
    context_object_name = 'workorders'
    paginate_by = 10

class WorkOrderDetailView(LoginRequiredMixin, DetailView):
    model = WorkOrder
    template_name = 'service/workorder_detail.html'
    context_object_name = 'workorder'