from django.shortcuts import render
from django.core.paginator import Paginator

from .models import PRG_STUDENT_SITE
from .models import ADR_STUDENTS
from .models import STUDENT_INTERNSHIP

from django.http import HttpResponse

#@login_required(login_url='/login')
def PRG_STUDENT_SITE_View(request,*args,**kwargs):
   PRG_STUDENT_SITE_list=PRG_STUDENT_SITE.objects.all()
   paginator=Paginator(PRG_STUDENT_SITE_list,25)
   page = request.GET.get('page')
   PRG_STUDENT_SITEs=paginator.get_page(page)
   #context_PRG_STUDENT_SITE={'query_results':query_results}
   
   return render(request,"dataCRUD.html",{'PRG_STUDENT_SITEs':PRG_STUDENT_SITEs})


#def PRG_STUDENT_SITE_View(*args,**kwargs):
#    return HttpResponse('<h1>Display PRG_STUDENT_SITE_view</h1>')

# Create your views here.

