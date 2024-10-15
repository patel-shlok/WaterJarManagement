from django import forms
from database.models import Asset, Customer, CustomerAssets


class AddAssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = ['name', 'total_amount', 'desc']
        labels = {'name': 'Asset Name', 'total_amount': 'Total Amount', 'desc': 'Description'}
        widgets = {'desc': forms.Textarea()}


class AssetDataEditForm(forms.Form):
    def __init__(self, *args, **kwargs):
        customer = kwargs.pop('customer')
        super(AssetDataEditForm, self).__init__(*args, **kwargs)
        assets = Customer.objects.get(username=customer).assets.all()
        for given_asset in assets:
            self.fields['%d' % given_asset.id] = forms.IntegerField(initial=given_asset.amount,
                                                                    label=given_asset.asset.name)


class AddAssetForCustomer(forms.Form):
    def __init__(self, *args, **kwargs):
        customer = kwargs.pop('customer')
        super(AddAssetForCustomer, self).__init__(*args, **kwargs)
        customer_assets = Customer.objects.get(username=customer).assets.all()
        all_assets = Asset.objects.all()
        asset_code = []
        for asset in customer_assets:
            asset_code.append(asset.asset.id)
        if customer_assets:
            all_assets = all_assets.exclude(id__in=asset_code)
        options = [(asset.id, asset.name) for asset in all_assets]
        self.fields['addAsset'] = forms.ChoiceField(choices=options, widget=forms.Select(attrs={
            "class": "form-control"
        }), label="Add Asset")
