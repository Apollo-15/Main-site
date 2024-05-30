from django.shortcuts import render, redirect

from django.views.generic import View, ListView
from django.contrib import messages

from .models import Wishlist
from .forms import WishlistForm

# Create your views here.
def index(request):
    return render(request, 'main/index.html')


def wishlist(request):
    return render(request, 'main/wishlist.html')

class WishlistAddHandler(View):
    def post(self, request):
        form = WishlistForm(request.POST)
        if form.is_valid():
            wishlist = form.save(commit=False)
            wishlist_item = Wishlist.objects.filter(product=wishlist.product, user=request.user).first()
            if wishlist_item:
                wishlist_item.quantity = wishlist.quantity
                wishlist_item.save()    
                messages.success(request, 'Кількість товару змінено')
            else:
                wishlist.user = request.user
                wishlist.save()
                messages.success(request, 'Товар додано списку бажаємого')
        else:
            messages.error(request, f'Помилка додавання товару до кошика {form.errors}')
        return redirect('main:wishlist')

class WishlistHandler(ListView):
    model = Wishlist
    template_name = 'main/wishlist.html'
    context_object_name = 'wishlist'
    
    
    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['get_total_cost'] = sum([item.get_total() for item in context['wishlist']])
        return context
    
    
class WishlistDeleteHandler(View):
    def get(self, request, pk):
        cart = Wishlist.objects.get(pk=pk, user=request.user)
        cart.delete()
        messages.success(request, 'Товар видалено з кошика')
        return redirect('main:wishlist')
    