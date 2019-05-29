import numpy as np
import pandas as pd
from django.shortcuts import render
from django.shortcuts import HttpResponse
from dataCRUD.models import *
from .scriptETL import *
from django.contrib.auth.decorators import login_required
from django.template.loader import get_template
from .forms import ContactForm
from django.core.mail import EmailMessage
from django.shortcuts import redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Max
from django_pandas.io import read_frame

# Create your views here.
@login_required
def home(request):
    return render(request, 'home.html')

# def descriptiveStats(request):
#     query_results=ProgramTable.objects.all()
#     context={'query_results':query_results}
#     return render(request, 'descriptiveStats.html', context)

@login_required
def descriptiveStats(request):                         ## function to display net charts without any filters being applied
    query_results=mergedTables.objects.all()
    df=mergedTables.pdobjects.all().to_dataframe()
    qs=mergedTables.objects.all().count()
    numSTU=mergedTables.objects.values('ID_ANO').distinct().count()
    numENT=mergedTables.objects.values('ENTREPRISE').distinct().count()
    STUyear=return_distinct_year(df)
    # STUQtdPerYear=return_distinct_STUQtdPerYear(df)
    dataGraph=[1000,10,552,2,63,830,10,84,400]
    heat_value=heatmap_ftr_slcor(df)

    num_records=num_records1(df)
    num_std=num_std1(df)
    num_entre=num_entre1(df)
    mean_sal=mean_sal1(df)

    d_stddist,l_site = stddist(df, 'SITE')
    c_cergy, c_pau, c_le =count_std(df,'PRG')
    s_cergy, s_pau, s_le =salary_avg(df, 'PRG')
    top, label = topx(df,'ENTREPRISE')




    context={'query_results':query_results,
             'NUMBERLINES':qs,
             'NUMBERSTU':numSTU,
             'NUMENT':numENT,
             'STUyear':STUyear, 
             'DATAGRAPH':dataGraph,
             'heat_value':heat_value,
             'Mean_sal':mean_sal,
             'num_records':num_records,
             'num_std':num_std,
             'num_entre':num_entre,
             'D_stddist':d_stddist,
             'L_stddist':list(l_site),
             'L_count':list(c_le),
             'D_cergyc':list(c_cergy),
             'D_pauc':list(c_pau),
             'L_sal': list(s_le),
             'D_cergys': list(c_cergy),
             'D_paus': list(c_pau),
             'D_top' :top,
             'D_label':label.tolist(),
                }
    return render(request, 'descriptiveStats2.html', context)


@login_required
@user_passes_test(lambda u: u.is_superuser)
def etl(request):
    df_list_versions=return_distinct_version(PRG_STUDENT_SITE.pdobjects.all().to_dataframe())
    max_version=max(df_list_versions)
    PRG= PRG_STUDENT_SITE.pdobjects.all().to_dataframe()
    ADR= ADR_STUDENTS.pdobjects.all().to_dataframe()
    STU= STUDENT_INTERNSHIP.pdobjects.all().to_dataframe()

    version_filtered =  (request.GET.get('version'))

    if version_filtered:
       version_filtered =  (int) (version_filtered)
    else:
        version_filtered=max_version

    PRG=PRG [PRG['idCSV']==version_filtered ]
    ADR=ADR [ADR['idCSV']==version_filtered ]
    STU=STU [STU['idCSV']==version_filtered ]

    PRGMissing=showMissingValues( PRG )
    ADRMissing=showMissingValues( ADR )
    STUMissing=showMissingValues( STU )

    context={'LIST_VERSIONS': df_list_versions,
             'SELECTED_VERSION':version_filtered,
             'PRG_STUDENT_SITE':PRGMissing.to_dict('split'),
             'ADR_STUDENTS':ADRMissing.to_dict('split'),
             'STUDENT_INTERNSHIP':STUMissing.to_dict('split')
            }
    
    return render(request, 'etl.html', context)


@login_required
def etl_mergetables(request):    
    version=int(mergedTables.objects.all().aggregate(Max('idCSV'))['idCSV__max']) + 1
    description='Delete Null Values'

    version_filtered =  (request.GET.get('version'))

    ADR=redefineDFTypes(ADR_STUDENTS.pdobjects.filter(idCSV=version_filtered).to_dataframe())    
    PRG=redefineDFTypes(PRG_STUDENT_SITE.pdobjects.filter(idCSV=version_filtered).to_dataframe())
    STU=redefineDFTypes(STUDENT_INTERNSHIP.pdobjects.filter(idCSV=version_filtered).to_dataframe())
    
    df=mergeTables(ADR,PRG,STU)
    df=deleteMissingValues(df)
    numberlines = df.ID_ANO.count()
    table = mergedTables.objects
    #writeDF2Table(df, table, version, description )

    df=showMissingValues( mergedTables.pdobjects.filter(idCSV=version).to_dataframe() )
    context={'MERGEDTABLES' :df.to_dict('split') ,
             'NUMBERLINES'  :numberlines ,
             'VERSION'      :str(version) + " - " + description
            }
    return render(request, 'etl_mergedtables.html', context)


@login_required
def etl_mergetablesRF(request):    
    version=int(mergedTables.objects.all().aggregate(Max('idCSV'))['idCSV__max']) + 1
    description='Fill with RandomForest Algorithm'
    
    version_filtered =  (request.GET.get('version'))

    ADR=redefineDFTypes(ADR_STUDENTS.pdobjects.filter(idCSV=version_filtered).to_dataframe())    
    PRG=redefineDFTypes(PRG_STUDENT_SITE.pdobjects.filter(idCSV=version_filtered).to_dataframe())
    STU=redefineDFTypes(STUDENT_INTERNSHIP.pdobjects.filter(idCSV=version_filtered).to_dataframe())
    LOC=redefineDFTypes(ADR_LOCATION.pdobjects.all().to_dataframe())
       
    ADR1,PRG1,STU1=UpdateMissingValues(ADR,PRG,STU,LOC )
    df=mergeTables(ADR1,PRG1,STU1)
    print(df)
    numberlines = df.ID_ANO.count()
    table = mergedTables.objects
    writeDF2Table(df, table, version, description )

    df=showMissingValues( mergedTables.pdobjects.filter(idCSV=version).to_dataframe() )
    context={'MERGEDTABLES' :df.to_dict('split') ,
             'NUMBERLINES'  :numberlines ,
             'VERSION'      :str(version) + " - " + description
            }
    return render(request, 'etl_mergedtables.html', context)

@login_required
def maps(request):
    return render(request, 'maps.html')

@login_required
def contact_us(request):                                        # contact us form
    form_class = ContactForm
    if request.method == 'POST':
        form = form_class(data=request.POST)

        if form.is_valid():
            contact_name = request.POST.get('contact_name', '')
            contact_email = request.POST.get('contact_email', '')
            form_content = request.POST.get('content', '')

            # Email the profile with the
            # contact information
            template = get_template('contacttemplate.txt')
            context = {
                'contact_name': contact_name,
                'contact_email': contact_email,
                'form_content': form_content,
                }
            content = template.render(context)

            email = EmailMessage(
                "New contact form submission",
                 content,
                "Your website" +'',
                ['induraj2020@gmail.com'],                        # has to be changed with unversity admin email
                headers = {'Reply-To': contact_email }
            )
            email.send()
            return redirect('home')

    return render(request, 'contact_us.html', {
        'form': form_class,
    })

#indu 17-may
def is_valid_queryparam(param):                                ## function to check if the dropdown lists are not empty
    if (param!='Choose...'):
        return(True)

def is_valid_queryparam2(param1,param2):                       ## function to check if the dropdown lists are not empty
    if (param1!='Choose...') and (param2 != 'Choose...'):
        return(True)

                    ##26-05-19## indu edit
@login_required
def checking(request):                                ## function related to filter tab-- To populate the dropdowns with the unique values 
    #query_results= mergedTables.objects.all()
    #query_results=mergeTables.objects.filter(item=item).distinct('ID_ANO')
    #query_results= mergedTables.objects.raw('SELECT DISTINCT PRG FROM mergedTables')
    # .count()
    #context = {'query_results': query_results}
    query_results=mergedTables.objects.all()                        # gets all objects of the mergedTables

    ### below 5 variables gets the unique fields from each of their mentioned fields
    df_new_prg = return_distinct_prg(mergedTables.pdobjects.all().to_dataframe())
    df_new_ville = return_distinct_ville(mergedTables.pdobjects.all().to_dataframe())
    df_new_cp = return_distinct_cp(mergedTables.pdobjects.all().to_dataframe())
    df_new_rem = return_distinct_rem(mergedTables.pdobjects.all().to_dataframe())
    df_new_year= return_distinct_year(mergedTables.pdobjects.all().to_dataframe())
    qs= query_results                       ## first when the page loads, all these are sent to the html and are rendered


    context = {'prg': df_new_prg,
               'ville': df_new_ville,
               'cp': df_new_cp,
               'rem': df_new_rem,
               'year':df_new_year,
               'query_results':qs,
               }
    
    return render(request,'checking.html',context)
    #return HttpResponse('<h1> hi </h1>')

                        ## 26-05-2019, indu ###


@login_required
def filter_chart(request):                           ## function to change the chart dynamically with respect to selected filters
    query_results=mergedTables.objects.all() 
    qs= query_results

    ## this below code works only if the form is sending somedata via Get method..i.e if the user presses search button

    prg_filtered= request.GET.get('program')
    vil_filtered= request.GET.get('ville')
    cod_filtered= request.GET.get('code_postal')
    rem_filtered= request.GET.get('remuneration')
    yfr_filtered= request.GET.get('years_from')
    yto_filtered= request.GET.get('years_to')

    message=''

    ## the first if contions filters and stores things in qs, the 2nd if condition if is true further acts 
    ## on this result stored in qs by 1st if conditon(which means it is further filtering on the data its getting from previous if result,)

    if is_valid_queryparam(prg_filtered):
        qs=qs.filter(PRG=prg_filtered)
        #qs= qs & query_results.filter(ADR_VILLE='CERGY' )
        #print(str(qs.query))
        #print(prg_filtered)

    if is_valid_queryparam(vil_filtered):
        qs=qs.filter(ADR_VILLE=vil_filtered)     
       # print(qs)

    if is_valid_queryparam(cod_filtered):
        qs=qs.filter(ADR_CP=cod_filtered)

    if is_valid_queryparam(rem_filtered):
        qs=qs.filter(REMUNERATION=rem_filtered)
       # print(type(qs))   ## class 'django.db.models.query.QuerySet'

    elif is_valid_queryparam2(yfr_filtered,yto_filtered):
        if (yfr_filtered <= yto_filtered):                     ## since in database the years are in the format xxxx/yyyy, and is of object datatype, all these stuffs are wrtiten for splitting, type casting, and querring
            yfr_filtered=(int)(yfr_filtered)
            yfr_anotherhalf= yfr_filtered+1
            yto_filtered=(int)(yto_filtered)
            yto_anotherhalf = yto_filtered + 1
            yfr_filtered  =(str)(yfr_filtered)
            yto_filtered  = (str)(yto_filtered)
            yfr_anotherhalf = (str)(yfr_anotherhalf)
            yto_anotherhalf = (str)(yto_anotherhalf)
            yfr_filtered=yfr_filtered + '/' + (yfr_anotherhalf)
            yto_filtered=yto_filtered + '/' + (yto_anotherhalf)
            qs=query_results.filter(ANNEE_SCOLAIRE__gte=yfr_filtered,ANNEE_SCOLAIRE__lte=yto_filtered)
            
        else:
            message="Years From-To not correct"

    pd_df_of_query_result= read_frame(qs)                  ## to convert the query to dataframe objects... This Queried results are from the filter menu
    #pd_df_of_query_result= pd.DataFrame(list(qs))
    newTable=pd_df_of_query_result
    
    qs=newTable.count()
    numSTU=len(newTable['ID_ANO'].unique())               ## the distinct doesnt work so do the count,so used len() and unique()
    numENT=len(newTable['ENTREPRISE'].unique())
    STUyear=return_distinct_year(newTable)                ## this funciton is return in the scriptETL.py
    dataGraph=[1000,10,552,2,63,830,10,84,400]

    context={
             'query_results':query_results,
             'NUMBERSTU':numSTU,
             'NUMENT':numENT,
             'STUyear':STUyear, 
             'DATAGRAPH':dataGraph
            }

  
    return render(request,'descriptivestats3.html',context)     # descriptivestats3 is a new html for displaying the altered graphs based on query results


def mapindu(request):
    #return HttpResponse('<h1> hiiiii </h1>')
    

    map()
    return render(request, 'map.html', {'title': 'maps'})