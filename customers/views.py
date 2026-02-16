from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import CartItem
from sellers.models import Advert # instead of Product
from .models import SavedItem, CustomerProfile
from .models import Review
from .forms import ReviewForm


@login_required
def add_to_cart(request, advert_id):
    advert = get_object_or_404(Advert, id=advert_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, advert=advert)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('cart_detail')


@login_required
def cart_detail(request):
    cart_items = CartItem.objects.filter(user=request.user)

    # add a subtotal for each item
    for item in cart_items:
        item.subtotal = item.advert.price * item.quantity

    total = sum(item.subtotal for item in cart_items)

    return render(request, "cart_detail.html", {
        "cart_items": cart_items,
        "total": total
    })


@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    cart_item.delete()
    return redirect('cart_detail')

@login_required
def update_cart(request):
    if request.method == "POST":
        for key, value in request.POST.items():
            if key.startswith("quantity_"):
                item_id = key.split("_")[1]
                try:
                    cart_item = CartItem.objects.get(id=item_id, user=request.user)

                    if "increase" in request.POST and request.POST["increase"] == item_id:
                        cart_item.quantity += 1
                    elif "decrease" in request.POST and request.POST["decrease"] == item_id:
                        if cart_item.quantity > 1:
                            cart_item.quantity -= 1
                    cart_item.save()
                except CartItem.DoesNotExist:
                    continue
    return redirect("cart_detail")

@login_required
def save_item(request, advert_id):
    advert = get_object_or_404(Advert, id=advert_id)
    saved, created = SavedItem.objects.get_or_create(user=request.user, advert=advert)

    if not created:
        # Already saved -> unsave
        saved.delete()
    return redirect(request.META.get('HTTP_REFERER', '/'))  # return to previous page

@login_required
def saved_items(request):
    saved_items = SavedItem.objects.filter(user=request.user)
    return render(request, "saved_items.html", {"items": saved_items})

@login_required
def add_review(request, advert_id):
    advert = get_object_or_404(Advert, id=advert_id)
    if request.method == "POST":
        form = ReviewForm(request.POST, request.FILES)  # include files
        if form.is_valid():
            review = form.save(commit=False)
            review.advert = advert
            review.user = request.user
            review.save()
            return redirect("product_detail", advert_id=advert.id)
    else:
        form = ReviewForm()
    return render(request, "reviews/add_review.html", {"form": form, "advert": advert})

