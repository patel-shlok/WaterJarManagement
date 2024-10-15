from django.conf.urls import url
from .views import *

urlpatterns = [

    url(r'^customer-inventory/$', customer_inventory),
    url(r'^inventory_all/$', all_inventory),
    url(r'^bottles/$', all_bottles),
    url(r'^add-asset/$', add_asset),
    url(r'^(?P<username>[ \w-]+)/$', inventory_details, name='customer-inventory'),
    url(r'^asset/(?P<id>[ \w-]+)/$', asset_details, name='asset-details'),

]
