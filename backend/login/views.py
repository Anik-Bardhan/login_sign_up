from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import render
from sign_up.models import *
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
import jwt
import secrets, string


# Create your views here.

def generate_token():  
    N = 10
    res = ''.join(secrets.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits)
                  for i in range(N))
    encoded_jwt = jwt.encode({"payload": res}, "secret", algorithm="HS256")
    return encoded_jwt

def is_authorised(email,token):
    user_obj = User.objects.get(username=email)        
    profile_obj = Profile.objects.get(user=user_obj)
    user_token = profile_obj.token
    is_logged_in = profile_obj.is_logged_in
    if user_token == token and is_logged_in:
        return True
    else:
        profile_obj.is_logged_in = False
        profile_obj.save()
        return False

@csrf_exempt
def sign_in(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        user_obj = User.objects.get(username = email)
        if user_obj.is_active:
            user = authenticate(username=email, password=password)
            if not user:
                return HttpResponse("Register first", status=422)
            else:
                profile_obj = Profile.objects.get(user = user_obj)
                profile_obj.is_logged_in = True
                token = generate_token()
                profile_obj.token = token
                profile_obj.save()
                return HttpResponse(token, status=202)
        else:
            return HttpResponse("Not activated", status=403)
    else:
        return HttpResponseNotAllowed(["GET"], status=403)

@csrf_exempt
def sign_out(request):
    if request.method == "POST":
        email = request.POST.get("email")
        token = request.POST.get("token")
        if not is_authorised(email, token):
            return HttpResponse("User not logged in", status=401)
        user_obj = User.objects.get(username=email)
        profile_obj = Profile.objects.get(user=user_obj)
        profile_obj.is_logged_in = False
        profile_obj.save()
        return HttpResponse("Signed out", status=200)
    else:
        return HttpResponseNotAllowed(["GET"], status=403)
