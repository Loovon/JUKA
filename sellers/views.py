from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import SellerProfileForm
from .models import SellerProfile
from .forms import AdvertForm
from .models import Advert
from django.shortcuts import render, get_object_or_404
from .models import Shop
from customers.models import Review
from customers.forms import ReviewForm
from .models import Shop, ShopImage
from .forms import ShopImageForm
from .forms import ShopSettingsForm
from google.cloud import bigquery
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest
from google.cloud import aiplatform
from django.contrib import messages



@login_required
def setup_seller_profile(request):
    try:
        profile = SellerProfile.objects.get(user=request.user)
    except SellerProfile.DoesNotExist:
        profile = None

    if request.method == "POST":
        form = SellerProfileForm(request.POST, instance=profile)
        if form.is_valid():
            seller_profile = form.save(commit=False)
            seller_profile.user = request.user
            seller_profile.save()

            request.user.role = "seller"
            request.user.save(update_fields=["role"])

            messages.success(request, "Your seller profile and shop were created successfully!")

            # ✅ auto-create or get shop tied to this user
            shop, created = Shop.objects.get_or_create(seller=request.user)

            # Always sync shop with latest profile info
            shop.shop_name = seller_profile.store_name or f"{request.user.username}'s Shop"
            shop.description = seller_profile.store_description
            shop.email = request.user.email
            shop.phone = seller_profile.phone_number
            shop.address = seller_profile.address
            shop.save()

            # ✅ mark user as seller (so navbar updates)
            if not hasattr(request.user, "is_seller") or not request.user.is_seller:
                request.user.is_seller = True
                request.user.save(update_fields=["is_seller"])

        return redirect("my_shop", seller_id=seller_profile.id)
    else:
        form = SellerProfileForm(instance=profile)

    return render(request, "setup_seller.html", {"form": form})


@login_required
def create_advert(request):
    if request.user.role != "seller":
        return redirect('setup_seller_profile')

    if request.method == "POST":
        form = AdvertForm(request.POST, request.FILES)
        if form.is_valid():
            advert = form.save(commit=False)
            advert.seller = request.user
            advert.shop = request.user.shop
            advert.save()
            return redirect("my_adverts")  # Or a seller dashboard
    else:
        form = AdvertForm()

    return render(request, 'create_advert.html', {'form': form})


def my_shop(request, seller_id):
    seller_profile = get_object_or_404(SellerProfile, id=seller_id)
    shop = get_object_or_404(Shop, seller=seller_profile.user)

    adverts = Advert.objects.filter(shop=shop)
    reviews = Review.objects.filter(advert__shop=shop).select_related("advert", "user")

    is_owner = request.user.is_authenticated and request.user == shop.seller

    return render(request, "my_shop.html", {
        "shop": shop,
        "adverts": adverts,
        "reviews": reviews,
        "is_owner": is_owner,
        "show_sidebar": is_owner,
    })



def my_adverts(request):
    status = request.GET.get("status")
    adverts = Advert.objects.filter(seller=request.user)

    if status == "active":
        adverts = adverts.filter(active=True)
    elif status == "draft":
        adverts = adverts.filter(active=False)
    return render(request, "my_adverts.html", {
        "adverts": adverts,
        "show_sidebar": True  # 👈 ensure sidebar is included
    })


@login_required
def edit_advert(request, pk):
    advert = get_object_or_404(Advert, pk=pk, seller=request.user)

    if request.method == "POST":
        form = AdvertForm(request.POST, request.FILES, instance=advert)
        if form.is_valid():
            form.save()
            messages.success(request, "Advert updated successfully.")
            return redirect("my_adverts")
    else:
        form = AdvertForm(instance=advert)

    return render(request, "edit_advert.html", {"form": form, "advert": advert})


@login_required
def toggle_advert_status(request, pk):
    advert = get_object_or_404(Advert, pk=pk, seller=request.user)
    advert.active = not advert.active
    advert.save()
    return redirect("my_adverts")


@login_required
def delete_advert(request, pk):
    advert = get_object_or_404(Advert, pk=pk, seller=request.user)

    if request.method == "POST":
        advert.delete()
        messages.success(request, "Advert deleted successfully.")
        return redirect("my_adverts")

    return render(request, "delete_advert_confirm.html", {"advert": advert})

@login_required
def feedback(request):
    # all reviews for products belonging to this seller
    adverts = Advert.objects.filter(seller=request.user)  # adjust if your relation is different
    reviews = Review.objects.filter(advert__in=adverts).select_related("user", "advert")

    return render(request, "feedback.html", {"reviews": reviews})


def performance(request, seller_id):
    shop = get_object_or_404(Shop, seller__id=seller_id)
    adverts = shop.adverts.all()

    # -------------------------
    # 1. Get sales data (BigQuery)
    # -------------------------
    from google.cloud import bigquery

    bq_client = bigquery.Client()
    job_config = bigquery.QueryJobConfig(
        default_dataset="juka-468915.jukadata",
        query_parameters=[
            bigquery.ScalarQueryParameter("seller_id", "STRING", str(seller_id))
        ]
    )

    query = """
            SELECT FORMAT_DATE('%b', date) AS month, SUM(amount) AS sales
            FROM sales
            WHERE seller_id = @seller_id
            GROUP BY month
            ORDER BY MIN (date) \
            """
    results = bq_client.query(query, job_config=job_config).result()

    months, sales_data = [], []
    for row in results:
        months.append(row.month)
        sales_data.append(row.sales)

    # fallback if no data yet
    if not sales_data:
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug"]
        sales_data = [200, 400, 600, 1200, 1500, 1800, 2100, 2399]

    total_sales = sum(sales_data)

    # -------------------------
    # 2. Google Analytics (Active users)
    # -------------------------
    analytics_client = BetaAnalyticsDataClient()
    request_ga = RunReportRequest(
        property="properties/468804578",
        dimensions=[{"name": "date"}],
        metrics=[{"name": "activeUsers"}],
        date_ranges=[{"start_date": "30daysAgo", "end_date": "today"}],
    )
    response_ga = analytics_client.run_report(request_ga)

    user_dates = [row.dimension_values[0].value for row in response_ga.rows]
    user_counts = [int(row.metric_values[0].value) for row in response_ga.rows]

    # fallback if GA is empty
    if not user_dates or not user_counts:
        today = datetime.date.today()
        user_dates = [(today - datetime.timedelta(days=i)).strftime("%d %b") for i in range(7)][::-1]
        user_counts = [5, 12, 9, 14, 20, 18, 25]

    # -------------------------
    # 3. Sales Forecast (Vertex AI)
    # -------------------------
    from google.cloud import aiplatform

    aiplatform.init(project="juka-468915", location="us-central1")
    model = aiplatform.Model(
        "projects/juka-468915/locations/us-central1/models/YOUR_MODEL_ID"
    )
    prediction = model.predict(instances=[{"seller_id": seller_id}])

    forecast = prediction.predictions[0].get("value", 0)

    # -------------------------
    # 4. File Upload handling (Vision / Document AI)
    # -------------------------
    extracted_text = None
    if request.method == "POST" and request.FILES.get("document"):
        uploaded_file = request.FILES["document"]

    # Save temporarily
    import tempfile

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        for chunk in uploaded_file.chunks():
            temp_file.write(chunk)
    file_path = temp_file.name

    if uploaded_file.name.endswith((".png", ".jpg", ".jpeg")):
        from google.cloud import vision
        vision_client = vision.ImageAnnotatorClient()
        with open(file_path, "rb") as f:
            image = vision.Image(content=content)
        response = vision_client.document_text_detection(image=image)
        extracted_text = response.full_text_annotation.text

    elif uploaded_file.name.endswith(".pdf"):
        from google.cloud import documentai

    docai_client = documentai.DocumentProcessorServiceClient()
    name = "projects/juka-468915/locations/us/processors/https://us-documentai.googleapis.com/v1/projects/1095974089100/locations/us/processors/14dd55c7bc8ec6c7:process"
    with open(file_path, "rb") as f:
        document = {"content": f.read(), "mime_type": "application/pdf"}
    result = docai_client.process_document(
        request={"name": name, "raw_document": document}
    )
    extracted_text = result.document.text

    # -------------------------
    # Context for template
    # -------------------------
    context = {
        "shop": shop,
        "adverts": adverts,
        "months": months,
        "sales_data": sales_data,
        "total_sales": total_sales,
        "active_ads": adverts.filter(active=True).count(),
        "user_dates": user_dates,
        "user_counts": user_counts,
        "forecast": forecast,
        "extracted_text": extracted_text,
    }
    return render(request, "performance.html", context)
#
@login_required
def settings(request):
    shop = get_object_or_404(Shop, seller=request.user)

    if request.method == "POST":
        form = ShopSettingsForm(request.POST, request.FILES, instance=shop)
        if form.is_valid():
            form.save()
            return redirect("settings")  # refresh after save
    else:
        form = ShopSettingsForm(instance=shop)

    return render(request, "settings.html", {"form": form})


@login_required
def upload_shop_images(request, shop_id):
    shop = get_object_or_404(Shop, id=shop_id)

    # Only allow shop owner
    if request.user != shop.seller:
        return redirect("my_shop", seller_id=request.user.sellerprofile.id)

    if request.method == "POST":
        files = request.FILES.getlist("image")
        if files:
            for f in files:
                ShopImage.objects.create(shop=shop, image=f)
            return redirect("my_shop", seller_id=request.user.sellerprofile.id)
        else:
            # Optional: show a message if no files were uploaded
            messages.error(request, "No file selected.")
    else:
        form = ShopImageForm()

    return render(request, "upload_shop_images.html", {"form": form, "shop": shop})

@login_required
def delete_shop_image(request, image_id):
    image = get_object_or_404(ShopImage, id=image_id)

    # Only allow the shop owner
    if request.user != image.shop.seller:
        return redirect("my_shop", seller_id=request.user.sellerprofile.id)

    if request.method == "POST":
        image.delete()
        messages.success(request, "Image deleted successfully.")
        return redirect("my_shop", seller_id=request.user.sellerprofile.id)

    return render(request, "confirm_delete_image.html", {"image": image})


@login_required
def edit_shop_image(request, image_id):
    image = get_object_or_404(ShopImage, id=image_id)

    # Only allow shop owner
    if request.user != image.shop.seller:
        return redirect("my_shop", seller_id=request.user.sellerprofile.id)

    if request.method == "POST":
        form = ShopImageForm(request.POST, request.FILES, instance=image)
        if form.is_valid():
            form.save()
            messages.success(request, "Image updated successfully.")
            return redirect("my_shop", seller_id=request.user.sellerprofile.id)
    else:
        form = ShopImageForm(instance=image)

    return render(request, "edit_shop_image.html", {"form": form, "image": image})


def get_sales_data():
    client = bigquery.Client()
    query = """
            SELECT FORMAT_DATE('%b', date) AS month, SUM(amount) AS sales
            FROM `your_project.sales`
            GROUP BY month
            ORDER BY MIN (date) \
            """
    results = client.query(query).result()
    months, sales = [], []
    for row in results:
        months.append(row.month)
        sales.append(row.sales)
    return months, sales


from google.cloud import aiplatform


def get_sales_forecast():
    aiplatform.init(project="your_project", location="us-central1")
    model = aiplatform.Model("projects/your_project/locations/us-central1/models/YOUR_MODEL_ID")
    prediction = model.predict(instances=[{"month": "2025-09", "features": {...}}])
    return prediction


from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest


def get_analytics_data():
    client = BetaAnalyticsDataClient()
    request = RunReportRequest(
        property="properties/468804578",
        dimensions=[{"name": "date"}],
        metrics=[{"name": "activeUsers"}],
        date_ranges=[{"start_date": "30daysAgo", "end_date": "today"}],
    )
    response = client.run_report(request)
    return [(row.dimension_values[0].value, row.metric_values[0].value) for row in response.rows]


from google.cloud import vision


def extract_text_from_image(image_path):
    client = vision.ImageAnnotatorClient()
    with open(image_path, "rb") as f:
        content = f.read()
    image = vision.Image(content=content)
    response = client.document_text_detection(image=image)
    return response.full_text_annotation.text


from google.cloud import documentai_v1 as documentai


def parse_document(file_path):
    client = documentai.DocumentProcessorServiceClient()
    name = "projects/YOUR_PROJECT/locations/us/processors/YOUR_PROCESSOR_ID"
    with open(file_path, "rb") as f:
        document = {"content": f.read(), "mime_type": "application/pdf"}
    result = client.process_document(request={"name": name, "raw_document": document})
    return result.document.text
