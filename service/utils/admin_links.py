from django.urls import reverse
from django.utils.html import format_html

def work_order_links(obj):
    return format_html(
        '<a class="button" href="{}?instrument={}">New WO</a>&nbsp;'
        '<a class="button" href="{}?instrument={}">New SR</a>',
        reverse('admin:service_workorder_add'),
        obj.id,
        reverse('admin:service_servicereport_add'),
        obj.id
    )
