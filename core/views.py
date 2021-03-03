from django.shortcuts import render


def home(request):
    """The homepage."""
    return render(request, 'home.html')


def contact(request):
    """Contact page."""
    return render(request, 'contact.html')
