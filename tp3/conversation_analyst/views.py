from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from .forms import UploadFileForm
from .models import File


# Create your views here.
def homepage(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded = request.FILES["file"]
            file_obj = File.objects.create(file=uploaded)
            file_obj.save()
            return HttpResponse("You have successfully uploaded" + str(uploaded))
    else:
        form = UploadFileForm()
    return render(request, "conversation_analyst/homepage.html", {"form": form})
