from django.shortcuts import render

# Create your views here.
#views.py

from djangomako.shortcuts import render_to_response, render_to_string
from django.shortcuts import render
from django import forms

def index(request):
    return render_to_response('test.mako',{})
