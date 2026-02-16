# products/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from categories.models import Category
from sellers.models import Advert, AdvertVariant
from customers.models import SavedItem
from products.models import Offer
from customers.models import Review
from customers.forms import ReviewForm


def index(request):
    adverts = Advert.objects.all()
    return render(request, "index.html", {
        "adverts": adverts,
        "categories": Category.objects.all(),
        "show_sidebar": True,
    })


def product_list(request):
    adverts = Advert.objects.all(active=True)
    category_name = request.GET.get("category")
    if category_name:
        adverts = adverts.filter(category__name=category_name)

    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")
    if min_price:
        adverts = adverts.filter(price__gte=min_price)
    if max_price:
        adverts = adverts.filter(price__lte=max_price)

    return render(request, "product_list.html", {
        "adverts": adverts,
        "categories": Category.objects.all(),
        "show_sidebar": True,
    })


def product_list_by_category(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    base_qs = Advert.objects.filter(category=category)

    # selected values
    q = request.GET
    min_price = q.get("min_price") or ""
    max_price = q.get("max_price") or ""
    size = q.get("size") or ""
    color = q.get("color") or ""
    thickness = q.get("thickness") or ""
    type_ = q.get("type") or ""
    weight = q.get("weight") or ""
    shape = q.get("shape") or ""

    adverts = base_qs.filter(active=True)
    if min_price: adverts = adverts.filter(price__gte=min_price)
    if max_price: adverts = adverts.filter(price__lte=max_price)
    if size: adverts = adverts.filter(size=size)
    if color: adverts = adverts.filter(color=color)
    if thickness: adverts = adverts.filter(thickness=thickness)
    if type_: adverts = adverts.filter(type=type_)
    if weight: adverts = adverts.filter(weight=weight)
    if shape: adverts = adverts.filter(shape=shape)

    # options for filters (distinct, non-empty)
    def options(field):
        return (base_qs
                .exclude(**{f"{field}__isnull": True})
                .exclude(**{f"{field}": ""})
                .values_list(field, flat=True)
                .distinct().order_by(field))

    ctx = {
        "category": category,
        "adverts": adverts,
        "categories": Category.objects.all(),
        "sizes": options("size"),
        "colors": options("color"),
        "thicknesses": options("thickness"),
        "types": options("type"),
        "weights": options("weight"),
        "shapes": options("shape"),
        "selected": {
            "min_price": min_price, "max_price": max_price,
            "size": size, "color": color, "thickness": thickness,
            "type": type_, "weight": weight, "shape": shape,
        },
        "show_sidebar": True,
    }
    return render(request, "product_list.html", ctx)


def product_detail(request, advert_id):
    advert = get_object_or_404(Advert, id=advert_id)
    reviews = advert.reviews.all()  # thanks to related_name in model
    form = ReviewForm()
    variants = advert.variants.all()

    return render(request, "product_detail.html", {
        "advert": advert,
        "reviews": reviews,
        "form": form,
        "variants": variants,
    })

@login_required
def save_advert(request, advert_id):
    advert = get_object_or_404(Advert, id=advert_id)
    SavedAdvert.objects.get_or_create(user=request.user, advert=advert)
    return redirect("product_detail", advert_id=advert.id)


@login_required
def saved_list(request):
    saved = SavedAdvert.objects.filter(user=request.user)
    return render(request, "saved_items.html", {"saved": saved})


def offer_detail(request, offer_id):
    offer = get_object_or_404(Offer, id=offer_id)
    return render(request, "offer_detail.html", {"offer": offer})


@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    if request.method == "POST":
        form = ReviewForm(request.POST, request.FILES, instance=review)
        if form.is_valid():
            form.save()
            return redirect("product_detail", advert_id=review.advert.id)
    else:
        form = ReviewForm(instance=review)
    return render(request, "edit_review.html", {"form": form, "review": review})



@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    advert_id = review.advert.id
    review.delete()
    return redirect("product_detail", advert_id=advert_id)