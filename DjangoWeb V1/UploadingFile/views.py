
from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import FileSystemStorage

from django.http import HttpResponseRedirect
from django.urls import reverse

from django.contrib import messages 
import logging

from django.db import models
from django.db import connection 
#from .models import PRG_STUDENT_SITE
from dataCRUD.models import PRG_STUDENT_SITE 


def uploadCSV(request):
     #tables=models._meta.db_table
     tables=connection.introspection.table_names()
     if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        if not myfile.name.endswith('.csv'):
            messages.error(request,'File is not CSV type')
            return HttpResponseRedirect(reverse('uploadcsv'))
        elif myfile.multiple_chunks():
            messages.error(request,"Uploaded file is too big (%.2f MB)." % (myfile.size/(1000*1000),))
            return HttpResponseRedirect(reverse('uploadcsv'))

        #tableSelected=request.get['tablesDropdown']
        file_data = myfile.read().decode("utf-8")		
        lines = file_data.split("\n")
		#loop over the lines and save them in db. If error , store as string and then display
        for line in lines:
            fields = line.split(",")
            prg_student_site= PRG_STUDENT_SITE(ID_ANO=fields[1],PRG=fields[2],ANNE_SCOLAIRE=fields[3],SITE=fields[4])
            try:
                prg_student_site.save()
            except Exception as e:
                messages.error(request,"Unable to upload file. "+repr(e))
           
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        return render(request, 'uploadcsv.html', {
            'uploaded_file_url': uploaded_file_url
        })

        
     return render(request, 'uploadcsv.html',{'tables': tables})
    

# Create your views here.
