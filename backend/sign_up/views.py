from django.shortcuts import render
# from django.views.decorators.csrf import csrf_exempt
# Create your views here.
# @csrf_exempt

def add_email(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        pass

# @csrf_exempt
def verify_email(request):
    pass

def add_password(request):
    pass