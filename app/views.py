from django.shortcuts import render, redirect

from app import forms


def index(request):
    return render(request, "index.html")


def register(request):
    form = forms.RegisterForm()

    if request.method == 'POST':
        form = forms.RegisterForm(request.POST)

        if form.is_valid():
            form.save()

            return redirect("index.html")

    return render(request, "register.html", {
        'form': forms.RegisterForm()
    })