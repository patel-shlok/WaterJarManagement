from django.shortcuts import render, redirect
from django.http import HttpResponseNotFound

from database.models import Asset, Customer, CustomerAssets, Bottles
from Admin.forms import PersonSearchForm
from Admin.views import string_to_list
from .forms import AddAssetForm, AddAssetForCustomer, AssetDataEditForm


def customer_inventory(request):
    if request.user.is_authenticated and request.user.is_superuser:
        user = Customer.objects.filter(is_approved=True)
        if request.POST:
            form = PersonSearchForm(request.POST)
            if form.is_valid():
                try:
                    user = user.filter(id=int(form.cleaned_data['name']))
                except:
                    user = user.filter(name__contains=form.cleaned_data['name'])
            context = {'users': user, 'admin': request.user, 'form': form}
            return render(request, 'inventory/all-customers-inventory.html', context=context)
        context = {'users': user, 'admin': request.user, 'form': PersonSearchForm()}
        return render(request, 'inventory/all-customer-inventory.html', context=context)
    return HttpResponseNotFound()


def inventory_details(request, username=None, *args, **kwargs):
    if request.user.is_authenticated and request.user.is_superuser:
        customer = Customer.objects.get(username=username)
        assets = Asset.objects.all()
        if request.POST and 'newAssetButton' in request.POST:
            form = AddAssetForCustomer(request.POST, customer=username)
            if form.is_valid():
                new_asset = CustomerAssets(asset=Asset.objects.get(id=form.cleaned_data['addAsset']))
                new_asset.save()
                customer.assets.add(new_asset)
                customer.save()
                data = {'customer': customer, 'newAssetForm': AddAssetForCustomer(customer=username),
                        'assetEditForm': AssetDataEditForm(customer=username),
                        'hasFields': True if AssetDataEditForm(customer=username).fields else False}
            else:
                data = {'customer': customer, 'newAssetForm': AddAssetForCustomer(customer=username),
                        'assetEditForm': AssetDataEditForm(customer=username),
                        'message': 'Invalid Data!',
                        'hasFields': True if AssetDataEditForm(customer=username).fields else False}
            return render(request, 'inventory/customer-inventory.html', data)
        if request.POST and 'editAssetButton' in request.POST:
            form = AssetDataEditForm(request.POST, customer=username)
            if form.is_valid():
                message = ""
                for field in form:
                    asset = CustomerAssets.objects.get(id=int(field.name))
                    if int(form.cleaned_data[field.name]) <= asset.asset.get_remaining() and not int(
                            form.cleaned_data[field.name]) < 0:
                        asset.asset.distributed -= asset.amount
                        asset.amount = int(form.cleaned_data[field.name])
                        asset.asset.distributed += asset.amount
                        asset.asset.save()
                        asset.save()
                    else:
                        message += ", %s " % asset.asset.name if message else "%s" % asset.asset.name
                    if int(form.cleaned_data[field.name]) < 0:
                        message = "Invalid Data!"
                        break
                if message and message != "Invalid Data!":
                    message += " not available"
                if not message:
                    message = "Assets Updated Successfully!"
                data = {'customer': customer, 'newAssetForm': AddAssetForCustomer(customer=username),
                        'assetEditForm': AssetDataEditForm(customer=username),
                        'hasFields': True if AssetDataEditForm(customer=username).fields else False,
                        'message': message}
            else:
                data = {'customer': customer, 'newAssetForm': AddAssetForCustomer(customer=username),
                        'assetEditForm': AssetDataEditForm(customer=username),
                        'message': 'Invalid Data!',
                        'hasFields': True if AssetDataEditForm(customer=username).fields else False}
            return render(request, 'inventory/customer-inventory.html', data)
        data = {'customer': customer, 'newAssetForm': AddAssetForCustomer(customer=username),
                'assetEditForm': AssetDataEditForm(customer=username),
                'hasFields': True if AssetDataEditForm(customer=username).fields else False}
        return render(request, 'inventory/customer-inventory.html', data)
    return HttpResponseNotFound()


def all_inventory(request):
    if request.user.is_authenticated and request.user.is_superuser:
        assets = Asset.objects.all()
        data = {'assets': assets}
        return render(request, 'inventory/inventory_all.html', data)


def asset_details(request, id=None, *args, **kwargs):
    if request.user.is_authenticated and request.user.is_superuser:
        asset = Asset.objects.get(id=id)
        context = {
            'details_of_asset': asset
        }
        if request.POST:
            print(request.POST.get('delete'))
            if request.POST.get('delete'):
                asset = request.POST.get('delete')
                asset = Asset.objects.get(id=asset)
                asset.delete()
            else:
                name = request.POST.get('name')
                desc = request.POST.get('desc')
                total_amount = request.POST.get('total_amount')
                if int(total_amount) < 0:
                    context['error'] = 'Invalid Input'
                else:
                    asset.name = name
                    asset.total_amount = total_amount
                    asset.desc = desc
                    asset.save()
                    context['massege'] = 'Asset Added'
            return redirect('/inventory/inventory_all/')

        return render(request, 'inventory/add_asset.html', context=context)
    return HttpResponseNotFound()


def add_asset(request):
    if request.user.is_authenticated and request.user.is_superuser:
        context = {}
        if request.POST:
            form = AddAssetForm(request.POST)
            if form.is_valid():
                form.save()
                context['massege'] = 'Asset Added'
            else:
                context['error'] = 'Invalid Input'
        context['form'] = AddAssetForm

        return render(request, 'inventory/add_asset.html', context=context)


def all_bottles(request):
    if request.user.is_authenticated and request.user.is_superuser:
        bottles = Bottles.objects.all()
        data = {'bottles': bottles}
        if request.POST:
            filled = request.POST.get('filled')
            total = request.POST.get('total')
            id = request.POST.get('id')
            distributed = sum([item.NoOfBottles for item in Customer.objects.all()])
            if int(total) < int(distributed) or int(filled) > (int(total) - int(distributed)):
                data['error'] = "Invalid Input"
            else:
                bottle = Bottles.objects.get(id=id)
                bottle.filled = filled
                bottle.total = total
                bottle.distributed = distributed
                bottle.save()
                return render(request, 'inventory/bottles_all.html', data)

        return render(request, 'inventory/bottles_all.html', data)
