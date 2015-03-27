from django.shortcuts import render
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt

import json
# Create your views here.

@csrf_exempt
def register(request):
  response = {}
  if request.method == 'POST':
    user_data = request.POST

    user_email = user_data.get('email', '')
    user_fn  = user_data.get('first_name', '')
    user_ln  = user_data.get('last_name', '')
    user_pswd = user_data.get('password', '')

    if not user_email or not user_fn or not user_ln or not user_pswd:
      return HttpResponse("MISSING INFORMATION")

    # checks if email is used
    if User.objects.filter(email=user_email):
      response['error'] = 'That email is being used. Please use another email'
      response['accepted'] = False
      return HttpResponse(json.dumps(response), content_type="application/json")
    user = User.objects.create_user(username=user_email, password=user_pswd, email=user_email, first_name=user_fn, last_name=user_ln)
    response['accepted'] = True 
    return HttpResponse(json.dumps(response), content_type="application/json")
