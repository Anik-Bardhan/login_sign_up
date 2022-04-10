from django.http import HttpResponse, HttpResponseNotAllowed
from .models import *
from django.contrib.auth.models import User
import math, random, jwt
from django.core.mail import EmailMessage
from django.views.decorators.csrf import csrf_exempt
import secrets, string
# Create your views here.


def send_otp(email, OTP):
    subject = f'OTP for verification.'
    html_content = f'Your OTP for verification is: {OTP}'
    message = EmailMessage(subject=subject, body=html_content, to=[email])
    message.content_subtype = 'html'
    message.send()

    user_obj = User.objects.get(username = email)
    print(user_obj)
    try:
        print('1')
        Profile.objects.create(user=user_obj, otp=OTP)
        print('2')
    except Exception as e:
        print('User does not exist', e)

def generate_otp():
    OTP = ""
    digits = "0123456789"
    for i in range(6):
        OTP += digits[math.floor(random.random()*10)]
    return OTP

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
def add_email(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user_obj = User.objects.get(username=email)
            if user_obj:
                if user_obj.is_active:
                    return HttpResponse("User already exists", status=409)
                else:
                    user_obj.password("hello")
                    user_obj.save()
                    OTP = generate_otp()
                    send_otp(email, OTP)
                    return HttpResponse("User re-signed-up successfully", status=200)
        except:
            User.objects.create_user(
                username=email, password="hello", is_active=False)
            otp=generate_otp()
            send_otp(email, otp)
            return HttpResponse("User signed-up successfully", status=200)
    else:
        return HttpResponseNotAllowed(["GET"], status=403)



@csrf_exempt
def verify_email(request):
    if request.method == "POST":
        email = request.POST.get('email')
        otp_frontend = request.POST.get('otp')
        user_obj = User.objects.get(username=email)
        OTP = Profile.objects.get(user=user_obj).otp
        if OTP == otp_frontend:
            user_obj.is_active = True
            user_obj.save()
            token = generate_token()
            profile_obj = Profile.objects.get(user=user_obj)
            profile_obj.is_logged_in = True
            profile_obj.token = token
            profile_obj.save()
            return HttpResponse(token, status=200)
        else:
            return HttpResponse('False', status=406)
    else:
        return HttpResponseNotAllowed(["GET"], status=403)
        

@csrf_exempt
def add_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        token = request.POST.get("token")
        name = request.POST.get("name")
        password = request.POST.get("password")
        if not is_authorised(email, token):
            return HttpResponse("User not logged in", status=401)
        user_obj = User.objects.get(username=email)
        user_obj.set_password(password)
        user_obj.save()
        profile_obj = Profile.objects.get(user = user_obj)
        profile_obj.name = name
        profile_obj.save()
        return HttpResponse("Success", status=201)
    else:
        return HttpResponseNotAllowed(["GET"], status=403)


