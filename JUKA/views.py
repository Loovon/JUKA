from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import messages
import logging
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect
from sellers.models import Advert
from django.conf import settings
from products.models import Product
from categories.models import Category
from customers.models import SavedItem






def home(request):
    # Only show active adverts on the home page
    adverts = Advert.objects.filter(active=True).order_by('-created_at')    # latest first
    categories = Category.objects.all()
    return render(request, "home.html", {"adverts": adverts, "show_sidebar": True,
                                         "categories": categories})


def show_map(request):
    return render(request, 'map.html', {
        'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY,
        "show_sidebar": True
    })


def profile_page(request):
    adverts = Advert.objects.filter(seller=request.user) if request.user.is_authenticated else None
    return render(request, "profile.html", {"user": request.user, "adverts": adverts})

def notifications(request):
    return render(request, "notifications.html")




def search_results(request):
    query = request.GET.get("q", "").strip()
    results = Advert.objects.filter(active=True)

    # Filter by search query
    if query:
        results = results.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        )

    # Price filter
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")
    if min_price:
        results = results.filter(price__gte=min_price)
    if max_price:
        results = results.filter(price__lte=max_price)

    # Condition filter
    condition = request.GET.get("condition")
    if condition:
        results = results.filter(type__iexact=condition)

    # Location filter (assuming Shop has a location field)
    location = request.GET.get("location")
    if location:
        results = results.filter(shop__location__icontains=location)

    # Category filter
    category_id = request.GET.get("category")
    if category_id:
        results = results.filter(category_id=category_id)

    # Remove adverts without images
    results = results.exclude(image="")

    categories = Category.objects.all()

    return render(request, "search_results.html", {
        "query": query,
        "results": results,
        "categories": categories,
        "show_sidebar": True
    })

def product_list(request):
    category = request.GET.get('category')
    if category:
        products = Advert.objects.filter(category=category)
    else:
        products = Advert.objects.all()
    return render(request, "product_list.html", {"products": products, "selected_category": category})



