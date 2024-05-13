from django.shortcuts import render
from .models import Test
# Create your views here.


def home(request):
    if request.method == 'POST':
        input_text = request.POST.get('inputField')
        Test.objects.create(text=input_text) 
    all_data = Test.objects.all()
    return render(request, 'home.html', {'all_data': all_data})
