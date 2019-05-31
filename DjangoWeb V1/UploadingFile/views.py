from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import FileSystemStorage

from django.http import HttpResponseRedirect
from django.urls import reverse

from django.contrib import messages 
import logging

from django.db import models
from django.db import connection 

from dataCRUD.models import PRG_STUDENT_SITE 
from dataCRUD.models import ADR_STUDENTS
from dataCRUD.models import STUDENT_INTERNSHIP

from .forms import DocumentForm

import csv
import codecs
import ast
import re

def uploadCSV(request):
     #tables=models._meta.db_table
     #tables=connection.introspection.table_names()
     
     Models={'PRG_STUDENT_SITE':1,
             'ADR_STUDENTS':2,
             'STUDENT_INTERNSHIP':3,
            }
     #modelPicked = request.POST.get('tablesDropdown',False) 
    
     if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        if  'tableselected' in request.GET:
            tablePicked=request.GET.get('tableselected')
        else:
            tablePicked=request.GET.get('tableselected','empty')
            print(tablePicked)
        #else:
        #    return render(request,'uploadcsv.html',{'tables': Models})

        if not myfile.name.endswith('.csv'):
            messages.error(request,'File is not CSV type')
            return HttpResponseRedirect(reverse('uploadcsv'))
        elif myfile.multiple_chunks():
            messages.error(request,"Uploaded file is too big (%.2f MB)." % (myfile.size/(1000*1000),))
            return HttpResponseRedirect(reverse('uploadcsv'))
        
        #modelPicked=request.POST.get('tablesDropdown','')
        #modelPicked=request.GET['tablesDropdown']
        for key in Models:
            if key==modelPicked:
                print(modelPicked)
                file_data = myfile.read().decode("utf-8")		
                lines = file_data.split("\n")
                #loop over the lines and save them in db. If error , store as string and then display
                for line in lines:
                    if line.strip():
                    #   line = line.strip().strip('\n')
                        line.strip('\n')
                        fields = line.split(",")
                        prg_student_site=Models['modelPicked'](ID_ANO=fields[1],PRG=fields[2],ANNE_SCOLAIRE=fields[3],SITE=fields[4])
                        try:
                            prg_student_site.save()
                        except Exception as e:
                            messages.error(request,"Unable to upload file. "+repr(e))


  #      file_data = myfile.read().decode("utf-8")		
  #      lines = file_data.split("\n")
		##loop over the lines and save them in db. If error , store as string and then display
  #      for line in lines:
  #          if line.strip():
  #          #line = line.strip().strip('\n')
  #              line.strip('\n')
  #              fields = line.split(",")
  #              prg_student_site= PRG_STUDENT_SITE(ID_ANO=fields[1],PRG=fields[2],ANNE_SCOLAIRE=fields[3],SITE=fields[4])
  #              try:
  #                  prg_student_site.save()
  #              except Exception as e:
  #                  messages.error(request,"Unable to upload file. "+repr(e))
        
        #save file to server
        
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        return render(request, 'uploadcsv.html', {
            'uploaded_file_url': uploaded_file_url
        })

     return render(request, 'uploadcsv.html',{'tables': Models})
    

def model_form_upload(request):

    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            ptable=form.cleaned_data.get('selectedtable')
            uploadedFile=request.FILES['document']
            fileType=form.cleaned_data.get('fileFormat').lower()
            separator=form.cleaned_data['separator']
            #Process the file
            if uploadedFile.multiple_chunks():
                messages.error(request,"Uploaded file is too big (%.2f MB)." % (myfile.size/(1000*1000),))
            
            if uploadedFile.name.endswith(fileType):
                if fileType=='csv':
                    handle_csv_file(uploadedFile,ptable)
                if fileType=='txt':
                    handle_uploaded_file(uploadedFile,ptable,separator)
            else:
                messages.error(request,'File is not CSV & text type')
                return HttpResponseRedirect(reverse('model_form_upload'))

            form.save()
            return HttpResponseRedirect(reverse('model_form_upload'))
    else:
        form = DocumentForm()
    return render(request, 'model_form_upload.html',{'form': form})

def handle_uploaded_file(f,table,separator):
    
    file_data = f.read().decode("utf-8")		
    lines = file_data.split("\n")
    #loop over the lines and save them in db. If error , store as string and then display
    if separator=='comma':
        for line in lines:
            if line.strip():
            #   line = line.strip().strip('\n')
                line.strip('\n')
                fields = line.split(",")
                prg_student_site=PRG_STUDENT_SITE(ID_ANO=fields[0],PRG=fields[1],ANNE_SCOLAIRE=fields[2],SITE=fields[3])
                try:
                    prg_student_site.save()
                except Exception as e:
                    messages.error(request,"Unable to upload file. "+repr(e))   
    if separator=='tab':
        for line in lines:
            if line.strip():
            #   line = line.strip().strip('\n')
                line.strip('\n')
                fields=line.split('\t')
                #fields =re.split(r'\t+', line.rstrip('\t')) 
                #prg_student_site=eval(table)(ID_ANO=fields[0],PRG=fields[1],ANNE_SCOLAIRE=fields[2],SITE=fields[3])
                prg_student_site=PRG_STUDENT_SITE(ID_ANO=fields[0],PRG=fields[1],ANNE_SCOLAIRE=fields[2],SITE=fields[3])
                try:
                    prg_student_site.save()
                except Exception as e:
                    messages.error(request,"Unable to upload file. "+repr(e))  
def handle_csv_file(f,tablePicked):
    reader = csv.DictReader(codecs.iterdecode(f, 'latin-1'))
    #reader = csv.DictReader(codecs.iterdecode(f, 'utf-8'))
 
    if tablePicked=='PRG_STUDENT_SITE':
        for row in reader:
            id_ano          =row['ID_ANO']
            prg             =row['PRG']
            anne_scolaire   =row['ANNE_SCOLAIRE']
            site            =row['SITE']
            prg_student_site=PRG_STUDENT_SITE(ID_ANO=id_ano,PRG=prg,ANNE_SCOLAIRE=anne_scolaire,SITE=site)
            try:
                prg_student_site.save()
            except Exception as e:
                messages.error(request,"Unable to save csv data to the database. "+repr(e))   
    if tablePicked=='ADR_STUDENTS':
        for row in reader:
            adr_cp      =row['ADR_CP']
            adr_ville   =row['ADR_VILLE']
            adr_pays    =row['ADR_PAYS']           
            id_ano      =row['ID_ANO']
            adr_student =ADR_STUDENTS(ADR_CP=adr_cp,ADR_VILLE=adr_ville,ADR_PAYS=adr_pays,ID_ANO=id_ano)
            try:
                adr_student.save()
            except Exception as e:
                messages.error(request,"Unable to save csv data to the database. "+repr(e)) 
    if tablePicked=='STUDENT_INTERNSHIP':
        for row in reader:
            annee=row['ANNEE']
            annee_scolaire=row['ANNEE_SCOLAIRE'] 
            entreprise=row['ENTREPRISE']
            code_postal=row['CODE_POSTAL']
            ville=row['VILLE']
            pays=row['PAYS']
            sujet=row['SUJET']
            remuneration=row['REMUNERATION'].replace(',', ".")
            #remuneration=ast.literal_eval(row['REMUNERATION'].replace(',', '.'))
            id_ano=row['ID_ANO']
            student_internship=STUDENT_INTERNSHIP(ANNEE=annee,ANNEE_SCOLAIRE=annee_scolaire,ENTREPRISE=entreprise,
                                                  CODE_POSTAL=code_postal,VILLE=ville,PAYS=pays,SUJET=sujet,
                                                  REMUNERATION=float(remuneration),ID_ANO=id_ano)
            student_internship.save()
            #try:
            #    student_internship.save()
            #except Exception as e:
            #    messages.error(request,"Unable to save csv data to the database. "+repr(e)) 
# Create your views here.
