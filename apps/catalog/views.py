from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render
from django.views.generic import ListView, DetailView
#Q search
from django.db.models import Q
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, HttpResponseRedirect, redirect
from apps.main.mixins import ListViewBreadCrumbMixin, DetailViewBreadCrumbMixin
from django.utils import timezone
from datetime import timedelta

from .models import Category, Product, Comment
from .forms import CommentForm
# Create your views here.

class CatalogListView(ListView):
    model = Category
    template_name = 'catalog/index.html'
    # context_object_name = 'categories'
    
    def get_queryset(self):
        return Category.objects.filter(parent=None)
    

class ProductByCategoryView(ListViewBreadCrumbMixin):
    model = Product
    template_name = 'catalog/product_catalog.html'
    context_object_name = 'products'
    paginate_by = 6
    
    def get_breadcrumb(self):
        self.breadcrumbs = {reverse("catalog:index"): "Каталог"}
        
        if self.category.parent:
            linkss = []
            
            parent = self.category.parent # визначаємо батьківську категорію поточної категорії
            while parent:
                linkss.append(
                    (
                        reverse("catalog:product_by_category", kwargs={"slug": parent.slug}),
                        parent.title
                    )
                )
                parent = parent.parent
            
            self.breadcrumbs.update(linkss)
            
            
            
        
        self.breadcrumbs["current"] = self.category.title
        return self.breadcrumbs
    
    def get_queryset(self):
       self.category = Category.objects.get(slug=self.kwargs['slug'])
       self.parents_categories = Category.objects.filter(parent=self.category).select_related('parent')
       self.all_categories = self.parents_categories.get_descendants(include_self=True).values_list('id', flat=True) # вибираємо всі категорії, які є нащадками поточної категорії
       self.products = Product.objects.filter(Q(category__in=self.all_categories) | Q(category=self.category)).distinct()
       return self.parents_categories
   
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['products'] = self.products
        return context
    

class ProductDetailView(DetailViewBreadCrumbMixin): 
    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'
    
    def get_queryset(self):
        return Product.objects.prefetch_related('images')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['main_image'] = self.object.main_image()
        return context
    
    def get_breadcrumb(self):
        self.breadcrumbs = {reverse("catalog:index"): "Каталог"}
        
        category = self.object.main_category()
        print(category)
        if category:
            if category.parent:
                linkss = []
                parent = category.parent
                while parent:
                    linkss.append(
                        (
                            reverse("catalog:product_by_category", kwargs={"slug": parent.slug}),
                            parent.title
                        )
                    )
                    parent = parent.parent
                    
                self.breadcrumbs.update(linkss)
            self.breadcrumbs[reverse("catalog:product_by_category", kwargs={"slug": category.slug})] = category.title
        self.breadcrumbs["current"] = self.object.title
        return self.breadcrumbs

class ProductNewsView(ListView):
    model = Product
    template_name = 'catalog/product_news.html'
    context_object_name = 'recent_products'
    
    def get_queryset(self):
        twenty_four_hours_ago = timezone.now() - timedelta(days=1)
        return Product.objects.filter(
            Q(created_at__gte=twenty_four_hours_ago) | 
            Q(updated_at__gte=twenty_four_hours_ago)
        ).distinct()

@login_required
def product_review(request, product_id):
    if request.method == 'POST':
        post = get_object_or_404(Product, pk=product_id)
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = Comment.objects.create(
                post=post,
                author=request.user,
                content=form.cleaned_data['content']
            )
            messages.success(request, 'Comment created successfully')
        else:
            messages.error(request, 'Error creating comment')
    return redirect('catalog:product_detail', slug=post.slug)