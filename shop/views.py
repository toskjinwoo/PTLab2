from django.shortcuts import get_object_or_404, render
from django.views.generic.edit import CreateView

from .discounts import DISCOUNT_TIERS
from .forms import PurchaseForm
from .models import Customer, Product, Purchase
from .services import make_purchase


def index(request):
    products = Product.objects.all()
    context = {'products': products, 'tiers': DISCOUNT_TIERS}
    return render(request, 'shop/index.html', context)


def customers(request):
    context = {'customers': Customer.objects.order_by('-total_spent', 'name')}
    return render(request, 'shop/customers.html', context)


class PurchaseCreate(CreateView):
    model = Purchase
    form_class = PurchaseForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = get_object_or_404(
            Product, pk=self.kwargs['product_id'])
        return context

    def form_valid(self, form):
        self.object = make_purchase(
            product=form.cleaned_data['product'],
            person=form.cleaned_data['person'],
            address=form.cleaned_data['address'])
        return render(self.request, 'shop/purchase_done.html',
                      {'purchase': self.object})
