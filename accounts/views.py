from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .forms import CustomUserCreationForm



def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        seller_form = SellerProfileForm(request.POST)
        if form.is_valid():
            user = form.save()(commit=False)
            if form.cleaned_data['role'] == 'seller' and seller_form.is_valid():
                user.save()
                seller_profile = seller_form.save(commit=False)
                seller_profile.user = user
                seller_profile.save()
            else:
                user.save()
            messages.success(request, "Account created! You can now log in.")
            return redirect('login')
    else:
        form = CustomUserCreationForm()
        seller_form = SellerProfileForm()
    return render(request, 'account/register.html',
                  {'form': form,
                   'seller_form': seller_form})



