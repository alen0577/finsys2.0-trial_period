#Finsys Final
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render,redirect
from django.contrib.auth.models import User, auth
from . models import *
from django.contrib import messages
from django.utils.crypto import get_random_string
from datetime import date
from datetime import timedelta
import random
import string
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.core.mail import send_mail, EmailMessage
from io import BytesIO
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from datetime import datetime
from datetime import date,datetime
from django.db.models import Sum,F,IntegerField,Q
from django.db.models.functions import ExtractMonth,ExtractYear,Cast
from django.core.mail import EmailMessage
from django.urls import reverse
from django.http import HttpResponse
from django.db import IntegrityError
from django.shortcuts import get_object_or_404

def Fin_index(request):
    return render(request,'Fin_index.html')


def Fin_login(request):
    if request.method == 'POST':
        user_name = request.POST['username']
        passw = request.POST['password']
    
        log_user = auth.authenticate(username = user_name,
                                  password = passw)
    
        if log_user is not None:
            auth.login(request, log_user)

        # ---super admin---

            if request.user.is_staff==1:
                return redirect('Fin_Adminhome') 
            
        # -------distributor ------    
            
        if Fin_Login_Details.objects.filter(User_name = user_name,password = passw).exists():
            data =  Fin_Login_Details.objects.get(User_name = user_name,password = passw)  
            if data.User_Type == 'Distributor':
                did = Fin_Distributors_Details.objects.get(Login_Id=data.id) 
                if did.Admin_approval_status == 'Accept':
                    request.session["s_id"]=data.id
                    if 's_id' in request.session:
                        if request.session.has_key('s_id'):
                            s_id = request.session['s_id']
                            print(s_id)
                            
                            current_day=date.today() 
                            if current_day == did.End_date:
                                print("wrong")
                                   
                                return redirect('Fin_Wrong')
                            else:
                                return redirect('Fin_DHome')
                            
                    else:
                        return redirect('/')
                else:
                    messages.info(request, 'Approval is Pending..')
                    return redirect('Fin_DistributorReg')
                      
            if data.User_Type == 'Company':
                cid = Fin_Company_Details.objects.get(Login_Id=data.id) 
                if cid.Admin_approval_status == 'Accept' or cid.Distributor_approval_status == 'Accept':
                    request.session["s_id"]=data.id
                    if 's_id' in request.session:
                        if request.session.has_key('s_id'):
                            s_id = request.session['s_id']
                            print(s_id)
                            com = Fin_Company_Details.objects.get(Login_Id = s_id)
                            

                            current_day=date.today() 
                            if current_day >= com.End_date:
                                print("wrong")
                                   
                                return redirect('Fin_Wrong')
                            else:
                                return redirect('Fin_Com_Home')
                    else:
                        return redirect('/')
                else:
                    messages.info(request, 'Approval is Pending..')
                    return redirect('Fin_CompanyReg')  
            if data.User_Type == 'Staff': 
                cid = Fin_Staff_Details.objects.get(Login_Id=data.id)   
                if cid.Company_approval_status == 'Accept':
                    request.session["s_id"]=data.id
                    if 's_id' in request.session:
                        if request.session.has_key('s_id'):
                            s_id = request.session['s_id']
                            print(s_id)
                            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
                            

                            current_day=date.today() 
                            if current_day >= com.company_id.End_date:
                                print("wrong")
                                messages.info(request, 'Your Account Temporary blocked')
                                return redirect('Fin_StaffReg') 
                            else:
                                return redirect('Fin_Com_Home')
                    else:
                        return redirect('/')
                else:
                    messages.info(request, 'Approval is Pending..')
                    return redirect('Fin_StaffReg') 
        else:
            messages.info(request, 'Invalid Username or Password. Try Again.')
            return redirect('Fin_CompanyReg')  
    else:  
        return redirect('Fin_CompanyReg')   
  

def logout(request):
    request.session["uid"] = ""
    auth.logout(request)
    return redirect('Fin_index')  

                    


 
    
# ---------------------------start admin ------------------------------------   


def Fin_Adminhome(request):
    noti = Fin_ANotification.objects.filter(status = 'New')
    n = len(noti)
    context = {
        'noti':noti,
        'n':n
    }
    return render(request,'Admin/Fin_Adminhome.html',context)

def Fin_PaymentTerm(request):
    terms = Fin_Payment_Terms.objects.all()
    noti = Fin_ANotification.objects.filter(status = 'New')
    n = len(noti)
    return render(request,'Admin/Fin_Payment_Terms.html',{'terms':terms,'noti':noti,'n':n})

def Fin_add_payment_terms(request):
  if request.method == 'POST':
    num=int(request.POST['num'])
    select=request.POST['select']
    if select == 'Years':
      days=int(num)*365
      pt = Fin_Payment_Terms(payment_terms_number = num,payment_terms_value = select,days = days)
      pt.save()
      messages.success(request, 'Payment term is added')
      return redirect('Fin_PaymentTerm')

    else:  
      days=int(num*30)
      pt = Fin_Payment_Terms(payment_terms_number = num,payment_terms_value = select,days = days)
      pt.save()
      messages.success(request, 'Payment term is added')
      return redirect('Fin_PaymentTerm')


  return redirect('Fin_PaymentTerm')

def Fin_ADistributor(request):
    noti = Fin_ANotification.objects.filter(status = 'New')
    n = len(noti)
    return render(request,"Admin/Fin_ADistributor.html",{'noti':noti,'n':n})

def Fin_Distributor_Request(request):
   data = Fin_Distributors_Details.objects.filter(Admin_approval_status = "NULL")
   print(data)
   noti = Fin_ANotification.objects.filter(status = 'New')
   n = len(noti)
   return render(request,"Admin/Fin_Distributor_Request.html",{'data':data,'noti':noti,'n':n})

def Fin_Distributor_Req_overview(request,id):
    data = Fin_Distributors_Details.objects.get(id=id)
    noti = Fin_ANotification.objects.filter(status = 'New')
    n = len(noti)
    return render(request,"Admin/Fin_Distributor_Req_overview.html",{'data':data,'noti':noti,'n':n})

def Fin_DReq_Accept(request,id):
   data = Fin_Distributors_Details.objects.get(id=id)
   data.Admin_approval_status = 'Accept'
   data.save()
   return redirect('Fin_Distributor_Request')

def Fin_DReq_Reject(request,id):
   data = Fin_Distributors_Details.objects.get(id=id)
   data.Login_Id.delete()
   data.delete()
   return redirect('Fin_Distributor_Request')

def Fin_Distributor_delete(request,id):
   data = Fin_Distributors_Details.objects.get(id=id)
   data.Login_Id.delete()
   data.delete()
   return redirect('Fin_All_distributors')

def Fin_All_distributors(request):
   data = Fin_Distributors_Details.objects.filter(Admin_approval_status = "Accept")
   print(data)
   noti = Fin_ANotification.objects.filter(status = 'New')
   n = len(noti)
   return render(request,"Admin/Fin_All_distributors.html",{'data':data,'noti':noti,'n':n})

def Fin_All_Distributor_Overview(request,id):
   data = Fin_Distributors_Details.objects.get(id=id)
   noti = Fin_ANotification.objects.filter(status = 'New')
   n = len(noti)
   return render(request,"Admin/Fin_All_Distributor_Overview.html",{'data':data,'noti':noti,'n':n})  

def Fin_AClients(request):
    noti = Fin_ANotification.objects.filter(status = 'New')
    n = len(noti)
    return render(request,"Admin/Fin_AClients.html",{'noti':noti,'n':n})


def Fin_AClients_Request(request):
    data = Fin_Company_Details.objects.filter(Registration_Type = "self", Admin_approval_status = "NULL")
    print(data)
    noti = Fin_ANotification.objects.filter(status = 'New')
    n = len(noti)
    return render(request,"Admin/Fin_AClients_Request.html",{'data':data,'noti':noti,'n':n})

def Fin_AClients_Request_OverView(request,id):
    data = Fin_Company_Details.objects.get(id=id)
    allmodules = Fin_Modules_List.objects.get(company_id = id,status = "New")
    noti = Fin_ANotification.objects.filter(status = 'New')
    n = len(noti)
    return render(request,'Admin/Fin_AClients_Request_OverView.html',{'data':data,'allmodules':allmodules,'noti':noti,'n':n})

def Fin_Client_Req_Accept(request,id):
   data = Fin_Company_Details.objects.get(id=id)
   data.Admin_approval_status = 'Accept'
   data.save()
   return redirect('Fin_AClients_Request')

def Fin_Client_Req_Reject(request,id):
   data = Fin_Company_Details.objects.get(id=id)
   data.Login_Id.delete()
   data.delete()
   return redirect('Fin_AClients_Request')

def Fin_Client_delete(request,id):
   data = Fin_Company_Details.objects.get(id=id)
   data.Login_Id.delete()
   data.delete()
   return redirect('Fin_Admin_clients')

def Fin_Admin_clients(request):
   data = Fin_Company_Details.objects.filter(Admin_approval_status = "Accept")
   print(data)
   noti = Fin_ANotification.objects.filter(status = 'New')
   n = len(noti)
   return render(request,"Admin/Fin_Admin_clients.html",{'data':data,'noti':noti,'n':n})

def Fin_Admin_clients_overview(request,id):
   data = Fin_Company_Details.objects.get(id=id)
   allmodules = Fin_Modules_List.objects.get(company_id = id,status = "New")
   noti = Fin_ANotification.objects.filter(status = 'New')
   n = len(noti)
   return render(request,"Admin/Fin_Admin_clients_overview.html",{'data':data,'allmodules':allmodules,'noti':noti,'n':n})   

def Fin_Anotification(request):
    noti = Fin_ANotification.objects.filter(status = 'New')
    n = len(noti)
    context = {
        'noti':noti,
        'n':n
    }
    return render(request,'Admin/Fin_Anotification.html',context) 

def  Fin_Anoti_Overview(request,id):
    noti = Fin_ANotification.objects.filter(status = 'New')
    n = len(noti)

    

    data = Fin_ANotification.objects.get(id=id)

    if data.Login_Id.User_Type == "Company":

        if data.Modules_List :
            allmodules = Fin_Modules_List.objects.get(Login_Id = data.Login_Id,status = "New")
            allmodules1 = Fin_Modules_List.objects.get(Login_Id = data.Login_Id,status = "pending")

        
            context = {
                'noti':noti,
                'n':n,
                'data':data,
                'allmodules':allmodules,
                'allmodules1':allmodules1,
            }
            return render(request,'Admin/Fin_Anoti_Overview.html',context)
        else:
            data1 = Fin_Company_Details.objects.get(Login_Id = data.Login_Id)
            context = {
                'noti':noti,
                'n':n,
                'data1':data1,
                'data':data,
                
            }
            return render(request,'Admin/Fin_Anoti_Overview.html',context)
    else:
        data1 = Fin_Distributors_Details.objects.get(Login_Id = data.Login_Id)
        context = {
                'noti':noti,
                'n':n,
                'data1':data1,
                'data':data,
                
            }

        return render(request,'Admin/Fin_Anoti_Overview.html',context)


def  Fin_Module_Updation_Accept(request,id):
    data = Fin_ANotification.objects.get(id=id)
    allmodules = Fin_Modules_List.objects.get(Login_Id = data.Login_Id,status = "New")
    allmodules.delete()

    allmodules1 = Fin_Modules_List.objects.get(Login_Id = data.Login_Id,status = "pending")
    allmodules1.status = "New"
    allmodules1.save()

    data.status = 'old'
    data.save()

    return redirect('Fin_Anotification')

def  Fin_Module_Updation_Reject(request,id):
    data = Fin_ANotification.objects.get(id=id)
    allmodules = Fin_Modules_List.objects.get(Login_Id = data.Login_Id,status = "pending")
    allmodules.delete()

    data.delete()

    return redirect('Fin_Anotification')

def  Fin_payment_terms_Updation_Accept(request,id):
    data = Fin_ANotification.objects.get(id=id)
    com = Fin_Company_Details.objects.get(Login_Id = data.Login_Id)
    terms=Fin_Payment_Terms.objects.get(id=data.PaymentTerms_updation.Payment_Term.id)
    
    
    com.Start_Date =date.today()
    days=int(terms.days)

    end= date.today() + timedelta(days=days)
    com.End_date = end
    com.Payment_Term = terms
    com.save()

    data.status = 'old'
    data.save()

    upt = Fin_Payment_Terms_updation.objects.get(id = data.PaymentTerms_updation.id)
    upt.status = 'old'
    upt.save()

    cnoti = Fin_CNotification.objects.filter(Company_id = com)
    for c in cnoti:
        c.status = 'old'
        c.save()    

    return redirect('Fin_Anotification')

def  Fin_payment_terms_Updation_Reject(request,id):
    data = Fin_ANotification.objects.get(id=id)

    upt = Fin_Payment_Terms_updation.objects.get(id = data.PaymentTerms_updation.id)

    upt.delete()
    data.delete()

    return redirect('Fin_Anotification')


def  Fin_ADpayment_terms_Updation_Accept(request,id):
    data = Fin_ANotification.objects.get(id=id)
    com = Fin_Distributors_Details.objects.get(Login_Id = data.Login_Id)
    terms=Fin_Payment_Terms.objects.get(id=data.PaymentTerms_updation.Payment_Term.id)
    
    
    com.Start_Date =date.today()
    days=int(terms.days)

    end= date.today() + timedelta(days=days)
    com.End_date = end
    com.Payment_Term = terms
    com.save()

    data.status = 'old'
    data.save()

    upt = Fin_Payment_Terms_updation.objects.get(id = data.PaymentTerms_updation.id)
    upt.status = 'old'
    upt.save()

    cnoti = Fin_DNotification.objects.filter(Distributor_id = com)
    for c in cnoti:
        c.status = 'old'
        c.save()    

    return redirect('Fin_Anotification')

def  Fin_ADpayment_terms_Updation_Reject(request,id):
    data = Fin_ANotification.objects.get(id=id)

    upt = Fin_Payment_Terms_updation.objects.get(id = data.PaymentTerms_updation.id)

    upt.delete()
    data.delete()

    return redirect('Fin_Anotification')

# -------------------------- admin updates ------------------------------------ 

def Fin_remove_payment_terms(request,pk):
    payment_term=Fin_Payment_Terms.objects.get(id=pk)
    payment_term.delete()
    messages.success(request, 'Payment term is removed')
    return redirect('Fin_PaymentTerm')

def Fin_Clients_under_distributors(request):
   distributors=Fin_Distributors_Details.objects.filter(Admin_approval_status="Accept")
   noti = Fin_ANotification.objects.filter(status = 'New')
   n = len(noti)

   context={
        'noti':noti,
        'n':n,
        'distributors':distributors
    }
   return render(request,"Admin/Fin_clients_under_distributors.html", context)

def get_clients_under_distributor(request):
  if request.method == 'GET':
    distributor_id = request.GET.get('distributor_id')
    
    # Query your database to fetch employee details based on the employee_id.

    company = Fin_Company_Details.objects.filter(Distributor_id=distributor_id,Admin_approval_status='Accept',Distributor_approval_status='Accept').order_by('-id')
    company_details=[]

    for i in company:
      cmp_id=i.id
      fname=i.Login_Id.First_name 
      lname=i.Login_Id.Last_name
      email=i.Email
      contact=i.Contact
      pterm_no=i.Payment_Term.payment_terms_number if i.Payment_Term else 'Trial'
      pterm_value=i.Payment_Term.payment_terms_value if i.Payment_Term else 'Period'
      sdate=i.Start_Date
      edate=i.End_date

      company_details.append({
        'cmp_id':cmp_id,
        'fname':fname,
        'lname':lname,
        'email':email,
        'contact':contact,
        'pterm_no':pterm_no,
        'pterm_value':pterm_value,
        'sdate':sdate,
        'edate':edate
      })
    
    # You might want to serialize the 'company_details' to a JSON format.
    return JsonResponse({'details': company_details})

  else:
    return JsonResponse({'error': 'Invalid request method.'}, status=400)


def distributor_client_profile_details(request,pk):
    data = Fin_Company_Details.objects.get(id=pk)
    allmodules = Fin_Modules_List.objects.get(company_id = pk,status = "New")
    noti = Fin_ANotification.objects.filter(status = 'New')
    n = len(noti)
 

    context={
        'data':data,'allmodules':allmodules,'noti':noti,'n':n
    }

    return render(request,'Admin/distributor_client_profile_details.html',context)


# ---------------------------end admin ------------------------------------ 






# ---------------------------start distributor------------------------------------   

 
def Fin_DHome(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Distributors_Details.objects.get(Login_Id = s_id)
        current_day=date.today() 
        diff = (data.End_date - current_day).days
        num = 20
        print(diff)
        if diff <= 20:
            n=Fin_DNotification(Login_Id = data.Login_Id,Distributor_id = data,Title = "Payment Terms Alert",Discription = "Your Payment Terms End Soon")
            n.save() 

        noti = Fin_DNotification.objects.filter(status = 'New',Distributor_id = data.id)
        n = len(noti)
        context = {
            'noti':noti,
            'n':n,
            'data':data
        }
        return render(request,'Distributor/Fin_DHome.html',context)
    else:
       return redirect('/')   

def Fin_DistributorReg(request):
    terms = Fin_Payment_Terms.objects.all()
    context = {
       'terms':terms
    }
    return render(request,'Distributor/Fin_DistributorReg.html',context)

def Fin_DReg_Action(request):
    if request.method == 'POST':
      first_name = request.POST['first_name']
      last_name = request.POST['last_name']
      email = request.POST['email']
      user_name = request.POST['username']
      password = request.POST['dpassword']

      if Fin_Login_Details.objects.filter(User_name=user_name).exists():
        messages.info(request, 'This username already exists. Sign up again')
        return redirect('Fin_DistributorReg')
      
      elif Fin_Distributors_Details.objects.filter(Email=email).exists():
        messages.info(request, 'This email already exists. Sign up again')
        return redirect('Fin_DistributorReg')
      else:
        dlog = Fin_Login_Details(First_name = first_name,Last_name = last_name,
                                User_name = user_name,password = password,
                                User_Type = 'Distributor')
        dlog.save()

        code_length = 8  
        characters = string.ascii_letters + string.digits  # Letters and numbers

        while True:
            unique_code = ''.join(random.choice(characters) for _ in range(code_length))
        
            # Check if the code already exists in the table
            if not Fin_Company_Details.objects.filter(Company_Code = unique_code).exists():
              break 

        ddata = Fin_Distributors_Details(Email = email,Login_Id = dlog,Distributor_Code = unique_code,Admin_approval_status = "NULL")
        ddata.save()
        return redirect('Fin_DReg2',dlog.id)    

        # code=get_random_string(length=6)
        # if Fin_Distributors_Details.objects.filter( Distributor_Code = code).exists():
        #     code2=get_random_string(length=6)

        #     ddata = Fin_Distributors_Details(Email = email,Login_Id = dlog,Distributor_Code = code2,Admin_approval_status = "NULL")
        #     ddata.save()
        #     return redirect('Fin_DReg2',dlog.id)
        # else:
        #     ddata = Fin_Distributors_Details(Email = email,Login_Id = dlog,Distributor_Code = code,Admin_approval_status = "NULL")
        #     ddata.save()
        #     return redirect('Fin_DReg2',dlog.id)
 
    return redirect('Fin_DistributorReg')

def Fin_DReg2(request,id):
    dlog = Fin_Login_Details.objects.get(id = id)
    ddata = Fin_Distributors_Details.objects.get(Login_Id = id)
    terms = Fin_Payment_Terms.objects.all()
    context = {
       'terms':terms,
       'dlog':dlog,
       'ddata':ddata
    }
    return render(request,'Distributor/Fin_DReg2.html',context)

def Fin_DReg2_Action2(request,id):
   if request.method == 'POST':
      ddata = Fin_Distributors_Details.objects.get(Login_Id = id)

      ddata.Contact = request.POST['phone']
      ddata.Image=request.FILES.get('img')

      payment_term = request.POST['payment_term']
      terms=Fin_Payment_Terms.objects.get(id=payment_term)
    
      start_date=date.today()
      days=int(terms.days)

      end= date.today() + timedelta(days=days)
      End_date=end

      ddata.Payment_Term  = terms
      ddata.Start_Date = start_date
      ddata.End_date = End_date

      ddata.save()
      return redirect('Fin_DistributorReg')
   return render('Fin_DReg2',id)  

def Fin_DClient_req(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Distributors_Details.objects.get(Login_Id = s_id)
        data1 = Fin_Company_Details.objects.filter(Registration_Type = "distributor",Distributor_approval_status = "NULL",Distributor_id = data.id)
        noti = Fin_DNotification.objects.filter(status = 'New',Distributor_id = data.id)
        n = len(noti)
        return render(request,'Distributor/Fin_DClient_req.html',{'data':data,'data1':data1,'noti':noti,'n':n})
    else:
       return redirect('/') 
    
def Fin_DClient_req_overview(request,id):
    data = Fin_Company_Details.objects.get(id=id)
    allmodules = Fin_Modules_List.objects.get(company_id = id,status = "New")
    noti = Fin_DNotification.objects.filter(status = 'New',Distributor_id = data.id)
    n = len(noti)
    return render(request,'Distributor/Fin_DClient_req_overview.html',{'data':data,'allmodules':allmodules,'noti':noti,'n':n})    
    
def Fin_DClient_Req_Accept(request,id):
   data = Fin_Company_Details.objects.get(id=id)
   data.Distributor_approval_status = 'Accept'
   data.save()
   return redirect('Fin_DClient_req')

def Fin_DClient_Req_Reject(request,id):
   data = Fin_Company_Details.objects.get(id=id)
   data.Login_Id.delete()
   data.delete()
   return redirect('Fin_DClient_req')   

def Fin_DClients(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Distributors_Details.objects.get(Login_Id = s_id)
        data1 = Fin_Company_Details.objects.filter(Registration_Type = "distributor",Distributor_approval_status = "Accept",Distributor_id = data.id)
        noti = Fin_DNotification.objects.filter(status = 'New',Distributor_id = data.id)
        n = len(noti)
        return render(request,'Distributor/Fin_DClients.html',{'data':data,'data1':data1,'noti':noti,'n':n})
    else:
       return redirect('/')  
   
def Fin_DClients_overview(request,id):
    data = Fin_Company_Details.objects.get(id=id)
    allmodules = Fin_Modules_List.objects.get(company_id = id,status = "New")
    noti = Fin_DNotification.objects.filter(status = 'New',Distributor_id = data.id)
    n = len(noti)
    return render(request,'Distributor/Fin_DClients_overview.html',{'data':data,'allmodules':allmodules,'noti':noti,'n':n})

def Fin_DClient_remove(request,id):
   data = Fin_Company_Details.objects.get(id=id)
   data.Login_Id.delete()
   data.delete()
   return redirect('Fin_DClients') 
    
def Fin_DProfile(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Distributors_Details.objects.get(Login_Id = s_id)
        data1 = Fin_Company_Details.objects.filter(Registration_Type = "distributor",Distributor_approval_status = "Accept",Distributor_id = data.id)
        terms = Fin_Payment_Terms.objects.all()
        noti = Fin_DNotification.objects.filter(status = 'New',Distributor_id = data.id)
        n = len(noti)
        return render(request,'Distributor/Fin_DProfile.html',{'data':data,'data1':data1,'terms':terms,'noti':noti,'n':n})
    else:
       return redirect('/')  
    
def Fin_Dnotification(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Distributors_Details.objects.get(Login_Id = s_id)

        noti = Fin_DNotification.objects.filter(status = 'New',Distributor_id = data.id)
        n = len(noti)
        context = {
            'noti':noti,
            'n':n,
            'data':data
        }
        return render(request,'Distributor/Fin_Dnotification.html',context)  
    else:
       return redirect('/') 
    
def  Fin_Dnoti_Overview(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        d = Fin_Distributors_Details.objects.get(Login_Id = s_id)
        noti = Fin_DNotification.objects.filter(status = 'New',Distributor_id = d.id)
        n = len(noti)

        

        data = Fin_DNotification.objects.get(id=id)

        if data.Modules_List :
            allmodules = Fin_Modules_List.objects.get(Login_Id = data.Login_Id,status = "New")
            allmodules1 = Fin_Modules_List.objects.get(Login_Id = data.Login_Id,status = "pending")

        
            context = {
                'noti':noti,
                'n':n,
                'data':data,
                'allmodules':allmodules,
                'allmodules1':allmodules1,
            }
            return render(request,'Distributor/Fin_Dnoti_Overview.html',context)
        else:
            data1 = Fin_Company_Details.objects.get(Login_Id = data.Login_Id)
            context = {
                'noti':noti,
                'n':n,
                'data1':data1,
                'data':data,
                
            }
            return render(request,'Distributor/Fin_Dnoti_Overview.html',context)    
    else:
       return redirect('/') 
    
def  Fin_DModule_Updation_Accept(request,id):
    data = Fin_DNotification.objects.get(id=id)
    allmodules = Fin_Modules_List.objects.get(Login_Id = data.Login_Id,status = "New")
    allmodules.delete()

    allmodules1 = Fin_Modules_List.objects.get(Login_Id = data.Login_Id,status = "pending")
    allmodules1.status = "New"
    allmodules1.save()

    data.status = 'old'
    data.save()

    return redirect('Fin_Dnotification')

def  Fin_DModule_Updation_Reject(request,id):
    data = Fin_DNotification.objects.get(id=id)
    allmodules = Fin_Modules_List.objects.get(Login_Id = data.Login_Id,status = "pending")
    allmodules.delete()

    data.delete()

    return redirect('Fin_Dnotification')

def  Fin_Dpayment_terms_Updation_Accept(request,id):
    data = Fin_DNotification.objects.get(id=id)
    com = Fin_Company_Details.objects.get(Login_Id = data.Login_Id)
    terms=Fin_Payment_Terms.objects.get(id=data.PaymentTerms_updation.Payment_Term.id)
    
    
    com.Start_Date =date.today()
    days=int(terms.days)

    end= date.today() + timedelta(days=days)
    com.End_date = end
    com.Payment_Term = terms
    com.save()

    data.status = 'old'
    data.save()

    upt = Fin_Payment_Terms_updation.objects.get(id = data.PaymentTerms_updation.id)
    upt.status = 'old'
    upt.save()

    return redirect('Fin_Dnotification')

def  Fin_Dpayment_terms_Updation_Reject(request,id):
    data = Fin_DNotification.objects.get(id=id)

    upt = Fin_Payment_Terms_updation.objects.get(id = data.PaymentTerms_updation.id)

    upt.delete()
    data.delete()

    return redirect('Fin_Dnotification')    

def Fin_DChange_payment_terms(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        
        if request.method == 'POST':
            data = Fin_Login_Details.objects.get(id = s_id)
            com = Fin_Distributors_Details.objects.get(Login_Id = s_id)
            pt = request.POST['payment_term']

            pay = Fin_Payment_Terms.objects.get(id=pt)

            data1 = Fin_Payment_Terms_updation(Login_Id = data,Payment_Term = pay)
            data1.save()

            
            noti = Fin_ANotification(Login_Id = data,PaymentTerms_updation = data1,Title = "Change Payment Terms",Discription = com.Login_Id.First_name + " is change Payment Terms")
            noti.save()
              


        
            return redirect('Fin_DProfile')
    else:
       return redirect('/') 
    

def Fin_Edit_Dprofile(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        com = Fin_Distributors_Details.objects.get(Login_Id = s_id)
        data = Fin_Distributors_Details.objects.get(Login_Id = s_id)

        noti = Fin_DNotification.objects.filter(status = 'New',Distributor_id = data.id)
        n = len(noti)

        context ={
            'com':com,
            'data':data,
            'n':n,
            'noti':noti
        }

        return render(request,"Distributor/Fin_Edit_Dprofile.html",context)    
    else:
       return redirect('/')    
    
def Fin_Edit_Dprofile_Action(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        com = Fin_Distributors_Details.objects.get(Login_Id = s_id)
        if request.method == 'POST':
            com.Login_Id.First_name = request.POST['first_name']
            com.Login_Id.Last_name = request.POST['last_name']
            com.Email = request.POST['email']
            com.Contact = request.POST['contact']
            
            com.Image  = request.FILES.get('img')
            

            com.Login_Id.save()
            com.save()

            return redirect('Fin_DProfile')
        return redirect('Fin_Edit_Dprofile')     
    else:
       return redirect('/')     

      
# ---------------------------end distributor------------------------------------  


             
# ---------------------------start staff------------------------------------   
    

def Fin_StaffReg(request):
    return render(request,'company/Fin_StaffReg.html')

def Fin_staffReg_action(request):
   if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        user_name = request.POST['cusername']
        password = request.POST['cpassword'] 
        cid = request.POST['Company_Code']
        if Fin_Company_Details.objects.filter(Company_Code = cid ).exists():
            com =Fin_Company_Details.objects.get(Company_Code = cid )

            if Fin_Staff_Details.objects.filter(company_id=com,Login_Id__User_name=user_name).exists():
                messages.info(request, 'This username already exists. Sign up again')
                return redirect('Fin_StaffReg')

            if Fin_Login_Details.objects.filter(User_name=user_name,password = password).exists():
                messages.info(request, 'This username and password already exists. Sign up again')
                return redirect('Fin_StaffReg')
        
            elif Fin_Staff_Details.objects.filter(Email=email).exists():
                messages.info(request, 'This email already exists. Sign up again')
                return redirect('Fin_StaffReg')
            else:
                dlog = Fin_Login_Details(First_name = first_name,Last_name = last_name,
                                    User_name = user_name,password = password,
                                    User_Type = 'Staff')
                dlog.save()

                ddata = Fin_Staff_Details(Email = email,Login_Id = dlog,Company_approval_status = "NULL",company_id = com)
                ddata.save()
                return redirect('Fin_StaffReg2',dlog.id)
        else:
            messages.info(request, 'This company code  not exists. Sign up again')  
            return redirect('Fin_StaffReg')    
        
def Fin_StaffReg2(request,id):
    dlog = Fin_Login_Details.objects.get(id = id)
    ddata = Fin_Staff_Details.objects.get(Login_Id = id)
    context = {
       'dlog':dlog,
       'ddata':ddata
    }
    return render(request,'company/Fin_StaffReg2.html',context)

def Fin_StaffReg2_Action(request,id):
    if request.method == 'POST':
        
        staff = Fin_Staff_Details.objects.get(Login_Id = id)
        log = Fin_Login_Details.objects.get(id = id)

        staff.Login_Id = log
           
        staff.contact = request.POST['phone']
        staff.img=request.FILES.get('img')
        staff.Company_approval_status = "Null"
        staff.save()
        print("Staff Registration Complete")
    
        return redirect('Fin_StaffReg')
        
    else:
        return redirect('Fin_StaffReg2',id)
# ---------------------------end staff------------------------------------ 


    
# ---------------------------start company------------------------------------ 

def Fin_Com_Home(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')

            current_day=date.today() 
            diff = (com.End_date - current_day).days
            num = 20
            print(diff)
            if diff <= 20:
                n=Fin_CNotification(Login_Id = data,Company_id = com,Title = "Payment Terms Alert",Discription = "Your Payment Terms End Soon")
                n.save()    

            noti = Fin_CNotification.objects.filter(status = 'New',Company_id = com)
            n = len(noti)

            context = {
                'allmodules':allmodules,
                'com':com,
                'data':data,
                'noti':noti,
                'n':n
                }

            return render(request,'company/Fin_Com_Home.html',context)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            return render(request,'company/Fin_Com_Home.html',{'allmodules':allmodules,'com':com,'data':data})
    else:
       return redirect('/') 
    
def Fin_Cnotification(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')

            noti = Fin_CNotification.objects.filter(status = 'New',Company_id = com)
            n = len(noti)
            context = {
                'allmodules':allmodules,
                'com':com,
                'data':data,
                'noti':noti,
                'n':n
            }
            return render(request,'company/Fin_Cnotification.html',context)  
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            context = {
                'allmodules':allmodules,
                'com':com,
                'data':data,
                
            }
            return render(request,'company/Fin_Cnotification.html',context)
    else:
       return redirect('/')     
     

def Fin_CompanyReg(request):
    return render(request,'company/Fin_CompanyReg.html')

def Fin_companyReg_action(request):
   if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        user_name = request.POST['cusername']
        password = request.POST['cpassword']


        if Fin_Login_Details.objects.filter(User_name=user_name).exists():
            messages.info(request, 'This username already exists. Sign up again')
            return redirect('Fin_CompanyReg')
      
        elif Fin_Company_Details.objects.filter(Email=email).exists():
            messages.info(request, 'This email already exists. Sign up again')
            return redirect('Fin_CompanyReg')
        else:
            dlog = Fin_Login_Details(First_name = first_name,Last_name = last_name,
                                User_name = user_name,password = password,
                                User_Type = 'Company')
            dlog.save()

        code_length = 8  
        characters = string.ascii_letters + string.digits  # Letters and numbers

        while True:
            unique_code = ''.join(random.choice(characters) for _ in range(code_length))
        
            # Check if the code already exists in the table
            if not Fin_Company_Details.objects.filter(Company_Code = unique_code).exists():
              break  

        ddata = Fin_Company_Details(Email = email,Login_Id = dlog,Company_Code = unique_code,Admin_approval_status = "NULL",Distributor_approval_status = "NULL")
        ddata.save()
        return redirect('Fin_CompanyReg2',dlog.id)      

        # code=get_random_string(length=6)
        # if Fin_Company_Details.objects.filter( Company_Code = code).exists():
        #     code2=get_random_string(length=6)

        #     ddata = Fin_Company_Details(Email = email,Login_Id = dlog,Company_Code = code2,Admin_approval_status = "NULL",Distributor_approval_status = "NULL")
        #     ddata.save()
        #     return redirect('Fin_CompanyReg2',dlog.id)
        # else:
        #     ddata = Fin_Company_Details(Email = email,Login_Id = dlog,Company_Code = code,Admin_approval_status = "NULL",Distributor_approval_status = "NULL")
        #     ddata.save()
        #     return redirect('Fin_CompanyReg2',dlog.id)
 
   return redirect('Fin_DistributorReg')

def Fin_CompanyReg2(request,id):
    data = Fin_Login_Details.objects.get(id=id)
    terms = Fin_Payment_Terms.objects.all()
    return render(request,'company/Fin_CompanyReg2.html',{'data':data,'terms':terms})

def Fin_CompanyReg2_action2(request,id):
    if request.method == 'POST':
        data = Fin_Login_Details.objects.get(id=id)
        com = Fin_Company_Details.objects.get(Login_Id=data.id)

        com.Company_name = request.POST['cname']
        com.Address = request.POST['caddress']
        com.City = request.POST['city']
        com.State = request.POST['state']
        com.Pincode = request.POST['pincode']
        com.Country = request.POST['ccountry']
        com.Image  = request.FILES.get('img1')
        com.Business_name = request.POST['bname']
        com.Industry = request.POST['industry']
        com.Company_Type = request.POST['ctype']
        com.Accountant = request.POST['staff']
        com.Payment_Type = request.POST['paid']
        com.Registration_Type = request.POST['reg_type']
        com.Contact = request.POST['phone']

        dis_code = request.POST['dis_code']
        if dis_code != '':
            if Fin_Distributors_Details.objects.filter(Distributor_Code = dis_code).exists():
                com.Distributor_id = Fin_Distributors_Details.objects.get(Distributor_Code = dis_code)
            else :
                messages.info(request, 'Sorry, distributor id does not exists')
                return redirect('Fin_CompanyReg2',id)
            
        
        payment_term = request.POST['payment_term']
        terms=Fin_Payment_Terms.objects.get(id=payment_term)
        com.Payment_Term =terms
        com.Start_Date=date.today()
        days=int(terms.days)

        end= date.today() + timedelta(days=days)
        com.End_date=end

        com.save()
        return redirect('Fin_Modules',id)
   
def Fin_Modules(request,id):
    data = Fin_Login_Details.objects.get(id=id)
    return render(request,'company/Fin_Modules.html',{'data':data})   

def Fin_Add_Modules(request,id):
    if request.method == 'POST':
        data = Fin_Login_Details.objects.get(id=id)
        com = Fin_Company_Details.objects.get(Login_Id=data.id)

        # -----ITEMS----

        Items = request.POST.get('c1')
        Price_List = request.POST.get('c2')
        Stock_Adjustment = request.POST.get('c3')


        # --------- CASH & BANK-----
        Cash_in_hand = request.POST.get('c4')
        Offline_Banking = request.POST.get('c5')
        # Bank_Reconciliation = request.POST.get('c6')
        UPI = request.POST.get('c7')
        Bank_Holders = request.POST.get('c8')
        Cheque = request.POST.get('c9')
        Loan_Account = request.POST.get('c10')

        #  ------SALES MODULE -------
        Customers = request.POST.get('c11')
        Invoice  = request.POST.get('c12')
        Estimate = request.POST.get('c13')
        Sales_Order = request.POST.get('c14')
        Recurring_Invoice = request.POST.get('c15')
        Retainer_Invoice = request.POST.get('c16')
        Credit_Note = request.POST.get('c17')
        Payment_Received = request.POST.get('c18')
        Delivery_Challan = request.POST.get('c19')

        #  ---------PURCHASE MODULE--------- 
        Vendors = request.POST.get('c20') 
        Bills  = request.POST.get('c21')
        Recurring_Bills = request.POST.get('c22')
        Debit_Note = request.POST.get('c23')
        Purchase_Order = request.POST.get('c24')
        Expenses = request.POST.get('c25')
        Payment_Made = request.POST.get('c27')

        #  ---------EWay_Bill---------
        EWay_Bill = request.POST.get('c28')

        #  -------ACCOUNTS--------- 
        Chart_of_Accounts = request.POST.get('c29') 
        Manual_Journal = request.POST.get('c30')
        # Reconcile  = request.POST.get('c36')


        # -------PAYROLL------- 
        Employees = request.POST.get('c31')
        Employees_Loan = request.POST.get('c32')
        Holiday = request.POST.get('c33') 
        Attendance = request.POST.get('c34')
        Salary_Details = request.POST.get('c35')

        modules = Fin_Modules_List(Items = Items,Price_List = Price_List,Stock_Adjustment = Stock_Adjustment,
            Cash_in_hand = Cash_in_hand,Offline_Banking = Offline_Banking,
            UPI = UPI,Bank_Holders = Bank_Holders,Cheque = Cheque,Loan_Account = Loan_Account,
            Customers = Customers,Invoice = Invoice,Estimate = Estimate,Sales_Order = Sales_Order,
            Recurring_Invoice = Recurring_Invoice,Retainer_Invoice = Retainer_Invoice,Credit_Note = Credit_Note,
            Payment_Received = Payment_Received,Delivery_Challan = Delivery_Challan,
            Vendors = Vendors,Bills = Bills,Recurring_Bills = Recurring_Bills,Debit_Note = Debit_Note,
            Purchase_Order = Purchase_Order,Expenses = Expenses,
            Payment_Made = Payment_Made,EWay_Bill = EWay_Bill,
            Chart_of_Accounts = Chart_of_Accounts,Manual_Journal = Manual_Journal,
            Employees = Employees,Employees_Loan = Employees_Loan,Holiday = Holiday,
            Attendance = Attendance,Salary_Details = Salary_Details,
            Login_Id = data,company_id = com)
        
        modules.save()

        #Adding Default Units under company
        Fin_Units.objects.create(Company=com, name='BOX')
        Fin_Units.objects.create(Company=com, name='NUMBER')
        Fin_Units.objects.create(Company=com, name='PACK')

        # Adding default accounts for companies

        created_date = date.today()
        account_info = [
            {"company_id": com, "Login_Id": data, "account_type": "Accounts Payable", "account_name": "Accounts Payable", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "This is an account of all the money which you owe to others like a pending bill payment to a vendor,etc.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Accounts Receivable", "account_name": "Accounts Receivable", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "The money that customers owe you becomes the accounts receivable. A good example of this is a payment expected from an invoice sent to your customer.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Other Current Asset", "account_name": "Advance Tax", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "Any tax which is paid in advance is recorded into the advance tax account. This advance tax payment could be a quarterly, half yearly or yearly payment", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Advertising and Marketing", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "Your expenses on promotional, marketing and advertising activities like banners, web-adds, trade shows, etc. are recorded in advertising and marketing account.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Automobile Expense", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "Transportation related expenses like fuel charges and maintenance charges for automobiles, are included to the automobile expense account.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Bad Debt", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "Any amount which is lost and is unrecoverable is recorded into the bad debt account.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Bank Fees and Charges", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": " Any bank fees levied is recorded into the bank fees and charges account. A bank account maintenance fee, transaction charges, a late payment fee are some examples.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},

            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Consultant Expense", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "Charges for availing the services of a consultant is recorded as a consultant expenses. The fees paid to a soft skills consultant to impart personality development training for your employees is a good example.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Cost Of Goods Sold", "account_name": "Cost of Goods Sold", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "An expense account which tracks the value of the goods sold.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Credit Card Charges", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": " Service fees for transactions , balance transfer fees, annual credit fees and other charges levied on a credit card are recorded into the credit card account.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Depreciation Expense", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "Any depreciation in value of your assets can be captured as a depreciation expense.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},

            {"company_id": com, "Login_Id": data, "account_type": "Income", "account_name": "Discount", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "Any reduction on your selling price as a discount can be recorded into the discount account.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Equity", "account_name": "Drawings", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "The money withdrawn from a business by its owner can be tracked with this account.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Other Current Asset", "account_name": "Employee Advance", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "Money paid out to an employee in advance can be tracked here till it's repaid or shown to be spent for company purposes", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Other Current Liability", "account_name": "Employee Reimbursements", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "This account can be used to track the reimbursements that are due to be paid out to employees.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Other Expense", "account_name": "Exchange Gain or Loss", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "Changing the conversion rate can result in a gain or a loss. You can record this into the exchange gain or loss account.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},

            {"company_id": com, "Login_Id": data, "account_type": "Fixed Asset", "account_name": "Furniture and Equipment", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "Purchases of furniture and equipment for your office that can be used for a long period of time usually exceeding one year can be tracked with this account.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Income", "account_name": "General Income", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "A general category of account where you can record any income which cannot be recorded into any other category", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Income", "account_name": "Interest Income", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "A percentage of your balances and deposits are given as interest to you by your banks and financial institutions. This interest is recorded into the interest income account.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Stock", "account_name": "Inventory Asset", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "An account which tracks the value of goods in your inventory.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "IT and Internet Expenses", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "Money spent on your IT infrastructure and usage like internet connection, purchasing computer equipment etc is recorded as an IT and Computer Expense", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},

            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Janitorial Expense", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "All your janitorial and cleaning expenses are recorded into the janitorial expenses account.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Income", "account_name": "Late Fee Income", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "Any late fee income is recorded into the late fee income account. The late fee is levied when the payment for an invoice is not received by the due date", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Lodging", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "Any expense related to putting up at motels etc while on business travel can be entered here.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Meals and Entertainment", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "Expenses on food and entertainment are recorded into this account.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Office Supplies", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "All expenses on purchasing office supplies like stationery are recorded into the office supplies account.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},

            {"company_id": com, "Login_Id": data, "account_type": "Other Current Liability", "account_name": "Opening Balance Adjustments", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "This account will hold the difference in the debits and credits entered during the opening balance.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Equity", "account_name": "Opening Balance Offset", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "This is an account where you can record the balance from your previous years earning or the amount set aside for some activities. It is like a buffer account for your funds.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Income", "account_name": "Other Charges", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "Miscellaneous charges like adjustments made to the invoice can be recorded in this account.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Other Expenses", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": " Any minor expense on activities unrelated to primary business operations is recorded under the other expense account.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Equity", "account_name": "Owner's Equity", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "The owners rights to the assets of a company can be quantified in the owner's equity account.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},

            {"company_id": com, "Login_Id": data, "account_type": "Cash", "account_name": "Petty Cash", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "It is a small amount of cash that is used to pay your minor or casual expenses rather than writing a check.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Postage", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "Your expenses on ground mails, shipping and air mails can be recorded under the postage account.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Other Current Asset", "account_name": "Prepaid Expenses", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "An asset account that reports amounts paid in advance while purchasing goods or services from a vendor.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Printing and Stationery", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": " Expenses incurred by the organization towards printing and stationery.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Rent Expense", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "The rent paid for your office or any space related to your business can be recorded as a rental expense.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},

            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Repairs and Maintenance", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "The costs involved in maintenance and repair of assets is recorded under this account.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Equity", "account_name": "Retained Earnings", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "The earnings of your company which are not distributed among the share holders is accounted as retained earnings.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Salaries and Employee Wages", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "Salaries for your employees and the wages paid to workers are recorded under the salaries and wages account.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Income", "account_name": "Sales", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": " The income from the sales in your business is recorded under the sales account.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Income", "account_name": "Shipping Charge", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "Shipping charges made to the invoice will be recorded in this account.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},

            {"company_id": com, "Login_Id": data, "account_type": "Other Liability", "account_name": "Tag Adjustments", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": " This adjustment account tracks the transfers between different reporting tags.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Other Current Liability", "account_name": "Tax Payable", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "The amount of money which you owe to your tax authority is recorded under the tax payable account. This amount is a sum of your outstanding in taxes and the tax charged on sales.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Telephone Expense", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "The expenses on your telephone, mobile and fax usage are accounted as telephone expenses.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Travel Expense", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": " Expenses on business travels like hotel bookings, flight charges, etc. are recorded as travel expenses.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Uncategorized", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "This account can be used to temporarily track expenses that are yet to be identified and classified into a particular category.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},

            {"company_id": com, "Login_Id": data, "account_type": "Cash", "account_name": "Undeposited Funds", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "Record funds received by your company yet to be deposited in a bank as undeposited funds and group them as a current asset in your balance sheet.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Other Current Liability", "account_name": "Unearned Revenue", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "A liability account that reports amounts received in advance of providing goods or services. When the goods or services are provided, this account balance is decreased and a revenue account is increased.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Equity", "account_name": "Capital Stock", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": " An equity account that tracks the capital introduced when a business is operated through a company or corporation.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Long Term Liability", "account_name": "Construction Loans", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "An expense account that tracks the amount you repay for construction loans.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Contract Assets", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "An asset account to track the amount that you receive from your customers while you're yet to complete rendering the services.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},

            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Depreciation And Amortisation", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "An expense account that is used to track the depreciation of tangible assets and intangible assets, which is amortization.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Equity", "account_name": "Distributions", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "An equity account that tracks the payment of stock, cash or physical products to its shareholders.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Equity", "account_name": "Dividends Paid", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "An equity account to track the dividends paid when a corporation declares dividend on its common stock.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},

            {"company_id": com, "Login_Id": data, "account_type": "Other Current Liability", "account_name": "GST Payable", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Other Current Liability", "account_name": "Output CGST", "credit_card_no": "", "sub_account": True, "parent_account": "GST Payable", "bank_account_no": None, "account_code": "", "description": "", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Other Current Liability", "account_name": "Output IGST", "credit_card_no": "", "sub_account": True, "parent_account": "GST Payable", "bank_account_no": None, "account_code": "", "description": "", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Other Current Liability", "account_name": "Output SGST", "credit_card_no": "", "sub_account": True, "parent_account": "GST Payable", "bank_account_no": None, "account_code": "", "description": "", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},

            {"company_id": com, "Login_Id": data, "account_type": "Other Current Asset", "account_name": "GST TCS Receivable", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Other Current Asset", "account_name": "GST TDS Receivable", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},

            {"company_id": com, "Login_Id": data, "account_type": "Other Current Asset", "account_name": "Input Tax Credits", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Other Current Asset", "account_name": "Input CGST", "credit_card_no": "", "sub_account": True, "parent_account": "Input Tax Credits", "bank_account_no": None, "account_code": "", "description": "", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Other Current Asset", "account_name": "Input IGST", "credit_card_no": "", "sub_account": True, "parent_account": "Input Tax Credits", "bank_account_no": None, "account_code": "", "description": "", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Other Current Asset", "account_name": "Input SGST", "credit_card_no": "", "sub_account": True, "parent_account": "Input Tax Credits", "bank_account_no": None, "account_code": "", "description": "", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},

            {"company_id": com, "Login_Id": data, "account_type": "Equity", "account_name": "Investments", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "An equity account used to track the amount that you invest.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Cost Of Goods Sold", "account_name": "Job Costing", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "An expense account to track the costs that you incur in performing a job or a task.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Cost Of Goods Sold", "account_name": "Labor", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "An expense account that tracks the amount that you pay as labor.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Cost Of Goods Sold", "account_name": "Materials", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "An expense account that tracks the amount you use in purchasing materials.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Merchandise", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "An expense account to track the amount spent on purchasing merchandise.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},

            {"company_id": com, "Login_Id": data, "account_type": "Long Term Liability", "account_name": "Mortgages", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "An expense account that tracks the amounts you pay for the mortgage loan.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Raw Materials And Consumables", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "An expense account to track the amount spent on purchasing raw materials and consumables.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Other Current Asset", "account_name": "Reverse Charge Tax Input but not due", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "The amount of tax payable for your reverse charge purchases can be tracked here.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Other Current Asset", "account_name": "Sales to Customers (Cash)", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Cost Of Goods Sold", "account_name": "Subcontractor", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": " An expense account to track the amount that you pay subcontractors who provide service to you.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},

            {"company_id": com, "Login_Id": data, "account_type": "Other Current Liability", "account_name": "TDS Payable", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Other Current Asset", "account_name": "TDS Receivable", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Transportation Expense", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "An expense account to track the amount spent on transporting goods or providing services.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},

            {"company_id": com, "Login_Id": data, "account_type": "Bank", "account_name": "Bank Account", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Cash", "account_name": "Cash Account", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Credit Card", "account_name": "Credit Card Account", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Payment Clearing Account", "account_name": "Payment Clearing Account", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
        ]

        for account in account_info:
            if not Fin_Chart_Of_Account.objects.filter(Company = com,account_name=account['account_name']).exists():
                new_account = Fin_Chart_Of_Account(Company=account['company_id'],LoginDetails=account['Login_Id'],account_name=account['account_name'],account_type=account['account_type'],credit_card_no=account['credit_card_no'],sub_account=account['sub_account'],parent_account=account['parent_account'],bank_account_no=account['bank_account_no'],account_code=account['account_code'],description=account['description'],balance=account['balance'],balance_type=account['balance_type'],create_status=account['create_status'],status=account['status'],date=account['date'])
                new_account.save()

        #Adding Default Customer payment under company
        Fin_Company_Payment_Terms.objects.create(Company=com, term_name='Due on Receipt', days=0)
        Fin_Company_Payment_Terms.objects.create(Company=com, term_name='NET 30', days=30)
        Fin_Company_Payment_Terms.objects.create(Company=com, term_name='NET 60', days=60)

        print("add modules")
        return redirect('Fin_CompanyReg')
    return redirect('Fin_Modules',id)

def Fin_Edit_Modules(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        
        com = Fin_Company_Details.objects.get(Login_Id = s_id)
        allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
        return render(request,'company/Fin_Edit_Modules.html',{'allmodules':allmodules,'com':com})
       
    else:
       return redirect('/') 
def Fin_Edit_Modules_Action(request): 
    if 's_id' in request.session:
        s_id = request.session['s_id']
        
        if request.method == 'POST':
            data = Fin_Login_Details.objects.get(id = s_id)
        
            com = Fin_Company_Details.objects.get(Login_Id = s_id)

            # -----ITEMS----

            Items = request.POST.get('c1')
            Price_List = request.POST.get('c2')
            Stock_Adjustment = request.POST.get('c3')


            # --------- CASH & BANK-----
            Cash_in_hand = request.POST.get('c4')
            Offline_Banking = request.POST.get('c5')
            # Bank_Reconciliation = request.POST.get('c6')
            UPI = request.POST.get('c7')
            Bank_Holders = request.POST.get('c8')
            Cheque = request.POST.get('c9')
            Loan_Account = request.POST.get('c10')

            #  ------SALES MODULE -------
            Customers = request.POST.get('c11')
            Invoice  = request.POST.get('c12')
            Estimate = request.POST.get('c13')
            Sales_Order = request.POST.get('c14')
            Recurring_Invoice = request.POST.get('c15')
            Retainer_Invoice = request.POST.get('c16')
            Credit_Note = request.POST.get('c17')
            Payment_Received = request.POST.get('c18')
            Delivery_Challan = request.POST.get('c19')

            #  ---------PURCHASE MODULE--------- 
            Vendors = request.POST.get('c20') 
            Bills  = request.POST.get('c21')
            Recurring_Bills = request.POST.get('c22')
            Debit_Note = request.POST.get('c23')
            Purchase_Order = request.POST.get('c24')
            Expenses = request.POST.get('c25')
            
            Payment_Made = request.POST.get('c27')

            # ----------EWay_Bill-----
            EWay_Bill = request.POST.get('c28')

            #  -------ACCOUNTS--------- 
            Chart_of_Accounts = request.POST.get('c29') 
            Manual_Journal = request.POST.get('c30')
            # Reconcile  = request.POST.get('c36')


            # -------PAYROLL------- 
            Employees = request.POST.get('c31')
            Employees_Loan = request.POST.get('c32')
            Holiday = request.POST.get('c33') 
            Attendance = request.POST.get('c34')
            Salary_Details = request.POST.get('c35')

            modules = Fin_Modules_List(Items = Items,Price_List = Price_List,Stock_Adjustment = Stock_Adjustment,
                Cash_in_hand = Cash_in_hand,Offline_Banking = Offline_Banking,
                UPI = UPI,Bank_Holders = Bank_Holders,Cheque = Cheque,Loan_Account = Loan_Account,
                Customers = Customers,Invoice = Invoice,Estimate = Estimate,Sales_Order = Sales_Order,
                Recurring_Invoice = Recurring_Invoice,Retainer_Invoice = Retainer_Invoice,Credit_Note = Credit_Note,
                Payment_Received = Payment_Received,Delivery_Challan = Delivery_Challan,
                Vendors = Vendors,Bills = Bills,Recurring_Bills = Recurring_Bills,Debit_Note = Debit_Note,
                Purchase_Order = Purchase_Order,Expenses = Expenses,
                Payment_Made = Payment_Made,EWay_Bill = EWay_Bill,
                Chart_of_Accounts = Chart_of_Accounts,Manual_Journal = Manual_Journal,
                Employees = Employees,Employees_Loan = Employees_Loan,Holiday = Holiday,
                Attendance = Attendance,Salary_Details = Salary_Details,
                Login_Id = data,company_id = com,status = 'pending')
            
            modules.save()
            data1=Fin_Modules_List.objects.filter(company_id = com).update(update_action=1)

            if com.Registration_Type == 'self':
                noti = Fin_ANotification(Login_Id = data,Modules_List = modules,Title = "Module Updation",Discription = com.Company_name + " is change Modules")
                noti.save()
            else:
                noti = Fin_DNotification(Distributor_id = com.Distributor_id,Login_Id = data,Modules_List = modules,Title = "Module Updation",Discription = com.Company_name + " is change Modules")
                noti.save()   

            print("edit modules")
            return redirect('Fin_Company_Profile')
        return redirect('Fin_Edit_Modules')
       
    else:
       return redirect('/')    
    


def Fin_Company_Profile(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
            terms = Fin_Payment_Terms.objects.all()
            noti = Fin_CNotification.objects.filter(status = 'New',Company_id = com)
            n = len(noti)
            return render(request,'company/Fin_Company_Profile.html',{'allmodules':allmodules,'com':com,'data':data,'terms':terms,'noti':noti,'n':n})
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            return render(request,'company/Fin_Company_Profile.html',{'allmodules':allmodules,'com':com,'data':data})
        
    else:
       return redirect('/') 
    
def Fin_Staff_Req(request): 
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        com = Fin_Company_Details.objects.get(Login_Id = s_id)
        data1 = Fin_Staff_Details.objects.filter(company_id = com.id,Company_approval_status = "NULL")
        allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
        noti = Fin_CNotification.objects.filter(status = 'New',Company_id = com)
        n = len(noti)
        return render(request,'company/Fin_Staff_Req.html',{'com':com,'data':data,'allmodules':allmodules,'data1':data1,'noti':noti,'n':n})
    else:
       return redirect('/') 

def Fin_Staff_Req_Accept(request,id):
   data = Fin_Staff_Details.objects.get(id=id)
   data.Company_approval_status = 'Accept'
   data.save()
   return redirect('Fin_Staff_Req')

def Fin_Staff_Req_Reject(request,id):
   data = Fin_Staff_Details.objects.get(id=id)
   data.Login_Id.delete()
   data.delete()
   return redirect('Fin_Staff_Req')  

def Fin_Staff_delete(request,id):
   data = Fin_Staff_Details.objects.get(id=id)
   data.Login_Id.delete()
   data.delete()
   return redirect('Fin_All_Staff')  

def Fin_All_Staff(request): 
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        com = Fin_Company_Details.objects.get(Login_Id = s_id)
        data1 = Fin_Staff_Details.objects.filter(company_id = com.id,Company_approval_status = "Accept")
        allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
        noti = Fin_CNotification.objects.filter(status = 'New',Company_id = com)
        n = len(noti)
        return render(request,'company/Fin_All_Staff.html',{'com':com,'data':data,'allmodules':allmodules,'data1':data1,'noti':noti,'n':n})
    else:
       return redirect('/') 


def Fin_Change_payment_terms(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        
        if request.method == 'POST':
            data = Fin_Login_Details.objects.get(id = s_id)
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            pt = request.POST['payment_term']

            pay = Fin_Payment_Terms.objects.get(id=pt)

            data1 = Fin_Payment_Terms_updation(Login_Id = data,Payment_Term = pay)
            data1.save()

            if com.Registration_Type == 'self':
                noti = Fin_ANotification(Login_Id = data,PaymentTerms_updation = data1,Title = "Change Payment Terms",Discription = com.Company_name + " is change Payment Terms")
                noti.save()
            else:
                noti = Fin_DNotification(Distributor_id = com.Distributor_id,Login_Id = data,PaymentTerms_updation = data1,Title = "Change Payment Terms",Discription = com.Company_name + " is change Payment Terms")
                noti.save()    


        
            return redirect('Fin_Company_Profile')
    else:
       return redirect('/') 
    
def Fin_Wrong(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
           com = Fin_Distributors_Details.objects.get(Login_Id = s_id)     
        terms = Fin_Payment_Terms.objects.all()
        context= {
            'com':com,
            'terms':terms
        }
        return render(request,"company/Fin_Wrong.html",context)    
    else:
       return redirect('/') 
    
def Fin_Wrong_Action(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        
        if request.method == 'POST':
            data = Fin_Login_Details.objects.get(id = s_id)

            if data.User_Type == "Company":
                com = Fin_Company_Details.objects.get(Login_Id = s_id)
                pt = request.POST['payment_term']

                pay = Fin_Payment_Terms.objects.get(id=pt)

                data1 = Fin_Payment_Terms_updation(Login_Id = data,Payment_Term = pay)
                data1.save()

                if com.Registration_Type == 'self':
                    noti = Fin_ANotification(Login_Id = data,PaymentTerms_updation = data1,Title = "Change Payment Terms",Discription = com.Company_name + " is change Payment Terms")
                    noti.save()
                else:
                    noti = Fin_DNotification(Distributor_id = com.Distributor_id,Login_Id = data,PaymentTerms_updation = data1,Title = "Change Payment Terms",Discription = com.Company_name + " is change Payment Terms")
                    noti.save()    


            
                return redirect('Fin_CompanyReg')
            else:
                com = Fin_Distributors_Details.objects.get(Login_Id = s_id)
                pt = request.POST['payment_term']

                pay = Fin_Payment_Terms.objects.get(id=pt)

                data1 = Fin_Payment_Terms_updation(Login_Id = data,Payment_Term = pay)
                data1.save()

                noti = Fin_ANotification(Login_Id = data,PaymentTerms_updation = data1,Title = "Change Payment Terms",Discription = com.Login_Id.First_name + com.Login_Id.Last_name + " is change Payment Terms")
                noti.save()

                return redirect('Fin_DistributorReg')



    else:
       return redirect('/')  

def Fin_Edit_Company_profile(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        com = Fin_Company_Details.objects.get(Login_Id = s_id)
        noti = Fin_CNotification.objects.filter(status = 'New',Company_id = com)
        n = len(noti)

        context ={
            'com':com,
            'data':data,
            'n':n,
            'noti':noti


        }

        return render(request,"company/Fin_Edit_Company_profile.html",context)    
    else:
       return redirect('/') 
    

def Fin_Edit_Company_profile_Action(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        com = Fin_Company_Details.objects.get(Login_Id = s_id)
        if request.method == 'POST':
            com.Login_Id.First_name = request.POST['first_name']
            com.Login_Id.Last_name = request.POST['last_name']
            com.Email = request.POST['email']
            com.Contact = request.POST['contact']
            com.Company_name = request.POST['cname']
            com.Address = request.POST['caddress']
            com.City = request.POST['city']
            com.State = request.POST['state']
            com.Pincode = request.POST['pincode']
            com.Business_name = request.POST['bname']
            com.Pan_NO = request.POST['pannum']
            com.GST_Type = request.POST.get('gsttype')
            com.GST_NO = request.POST['gstnum']
            com.Industry = request.POST['industry']
            com.Company_Type = request.POST['ctype']
            com.Image = request.FILES.get('img')
            

            com.Login_Id.save()
            com.save()

            return redirect('Fin_Company_Profile')
        return redirect('Fin_Edit_Company_profile')     
    else:
       return redirect('/') 
    
def Fin_Edit_Staff_profile(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        com = Fin_Staff_Details.objects.get(Login_Id = s_id)

        context ={
            'com':com
        }

        return render(request,"company/Fin_Edit_Staff_profile.html",context)    
    else:
       return redirect('/')    
    
def Fin_Edit_Staff_profile_Action(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        com = Fin_Staff_Details.objects.get(Login_Id = s_id)
        if request.method == 'POST':
            com.Login_Id.First_name = request.POST['first_name']
            com.Login_Id.Last_name = request.POST['last_name']
            com.Email = request.POST['email']
            com.contact = request.POST['contact']
            
            com.img = request.FILES.get('img')
            

            com.Login_Id.save()
            com.save()

            return redirect('Fin_Company_Profile')
        return redirect('Fin_Edit_Staff_profile')     
    else:
       return redirect('/')     
      
    
# ---------------------------end company------------------------------------     


# ------------------shemeem-----Items&ChartOfAccounts-----------------------

# Items
def Fin_items(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
            items = Fin_Items.objects.filter(Company = com)
            return render(request,'company/Fin_Items.html',{'allmodules':allmodules,'com':com,'data':data,'items':items})
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            items = Fin_Items.objects.filter(Company = com.company_id)
            return render(request,'company/Fin_Items.html',{'allmodules':allmodules,'com':com,'data':data,'items':items})
    else:
       return redirect('/')

def Fin_createItem(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
            units = Fin_Units.objects.filter(Company = com)
            acc = Fin_Chart_Of_Account.objects.filter(Q(account_type='Expense') | Q(account_type='Other Expense') | Q(account_type='Cost Of Goods Sold'), Company=com).order_by('account_name')
            return render(request,'company/Fin_Add_Item.html',{'allmodules':allmodules,'com':com,'data':data,'units':units, 'accounts':acc})
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            units = Fin_Units.objects.filter(Company = com.company_id)
            acc = Fin_Chart_Of_Account.objects.filter(Q(account_type='Expense') | Q(account_type='Other Expense') | Q(account_type='Cost Of Goods Sold'), Company=com.company_id).order_by('account_name')
            return render(request,'company/Fin_Add_Item.html',{'allmodules':allmodules,'com':com,'data':data,'units':units, 'accounts':acc})
    else:
       return redirect('/')

def Fin_createNewItem(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        if request.method == 'POST':
            name = request.POST['name']
            type = request.POST['type']
            unit = request.POST.get('unit')
            hsn = request.POST['hsn']
            tax = request.POST['taxref']
            gstTax = 0 if tax == 'non taxable' else request.POST['intra_st']
            igstTax = 0 if tax == 'non taxable' else request.POST['inter_st']
            purPrice = request.POST['pcost']
            purAccount = None if not 'pur_account' in request.POST or request.POST['pur_account'] == "" else request.POST['pur_account']
            purDesc = request.POST['pur_desc']
            salePrice = request.POST['salesprice']
            saleAccount = None if not 'sale_account' in request.POST or request.POST['sale_account'] == "" else request.POST['sale_account']
            saleDesc = request.POST['sale_desc']
            inventory = request.POST.get('invacc')
            stock = 0 if request.POST.get('stock') == "" else request.POST.get('stock')
            stockUnitRate = 0 if request.POST.get('stock_rate') == "" else request.POST.get('stock_rate')
            minStock = request.POST['min_stock']
            createdDate = date.today()
            
            #save item and transaction if item or hsn doesn't exists already
            if Fin_Items.objects.filter(Company=com, name__iexact=name).exists():
                res = f'<script>alert("{name} already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)
            elif Fin_Items.objects.filter(Company = com, hsn__iexact = hsn).exists():
                res = f'<script>alert("HSN - {hsn} already exists, try another.!");window.history.back();</script>'
                return HttpResponse(res)
            else:
                item = Fin_Items(
                    Company = com,
                    LoginDetails = data,
                    name = name,
                    item_type = type,
                    unit = unit,
                    hsn = hsn,
                    tax_reference = tax,
                    intra_state_tax = gstTax,
                    inter_state_tax = igstTax,
                    sales_account = saleAccount,
                    selling_price = salePrice,
                    sales_description = saleDesc,
                    purchase_account = purAccount,
                    purchase_price = purPrice,
                    purchase_description = purDesc,
                    item_created = createdDate,
                    min_stock = minStock,
                    inventory_account = inventory,
                    opening_stock = stock,
                    current_stock = stock,
                    stock_in = 0,
                    stock_out = 0,
                    stock_unit_rate = stockUnitRate,
                    status = 'Active'
                )
                item.save()

                #save transaction

                Fin_Items_Transaction_History.objects.create(
                    Company = com,
                    LoginDetails = data,
                    item = item,
                    action = 'Created'
                )
                
                return redirect(Fin_items)

        return redirect(Fin_createItem)
    else:
       return redirect('/')

def Fin_viewItem(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
            item = Fin_Items.objects.get(id = id)
            hist = Fin_Items_Transaction_History.objects.filter(Company = com, item = item).last()
            cmt = Fin_Items_Comments.objects.filter(item = item)
            context = {'allmodules':allmodules,'com':com,'data':data,'item':item, 'history': hist,'comments':cmt}
            return render(request,'company/Fin_View_Item.html',context)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            item = Fin_Items.objects.get(id = id)
            hist = Fin_Items_Transaction_History.objects.filter(Company = com.company_id, item = item).last()
            cmt = Fin_Items_Comments.objects.filter(item = item)
            context = {'allmodules':allmodules,'com':com,'data':data,'item':item, 'history': hist,'comments':cmt}
            return render(request,'company/Fin_View_Item.html',context)
    else:
       return redirect('/')
    
def Fin_saveItemUnit(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        if request.method == "POST":
            name = request.POST['name'].upper()

            if not Fin_Units.objects.filter(Company = com, name__iexact = name).exists():
                unit = Fin_Units(
                    Company = com,
                    name = name
                )
                unit.save()
                return JsonResponse({'status':True})
            else:
                return JsonResponse({'status':False, 'message':'Unit already exists.!'})

def Fin_getItemUnits(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        list= []
        option_objects = Fin_Units.objects.filter(Company = com)

        for item in option_objects:
            itemUnitDict = {
                'name': item.name,
            }
            list.append(itemUnitDict)

        return JsonResponse({'units':list},safe=False)
    
def Fin_createNewAccountFromItems(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        if request.method == 'POST':
            name = request.POST['account_name']
            type = request.POST['account_type']
            subAcc = True if request.POST['subAccountCheckBox'] == 'true' else False
            parentAcc = request.POST['parent_account'] if subAcc == True else None
            accCode = request.POST['account_code']
            bankAccNum = None
            desc = request.POST['description']
            
            createdDate = date.today()
            
            #save account and transaction if account doesn't exists already
            if Fin_Chart_Of_Account.objects.filter(Company=com, account_name__iexact=name).exists():
                res = f'<script>alert("{name} already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)
            else:
                account = Fin_Chart_Of_Account(
                    Company = com,
                    LoginDetails = data,
                    account_type = type,
                    account_name = name,
                    account_code = accCode,
                    description = desc,
                    balance = 0.0,
                    balance_type = None,
                    credit_card_no = None,
                    sub_account = subAcc,
                    parent_account = parentAcc,
                    bank_account_no = bankAccNum,
                    date = createdDate,
                    create_status = 'added',
                    status = 'active'
                )
                account.save()

                #save transaction

                Fin_ChartOfAccount_History.objects.create(
                    Company = com,
                    LoginDetails = data,
                    account = account,
                    action = 'Created'
                )
                
                list= []
                account_objects = Fin_Chart_Of_Account.objects.filter(Q(account_type='Expense') | Q(account_type='Other Expense'), Company=com).order_by('account_name')

                for account in account_objects:
                    accounts = {
                        'name': account.account_name,
                    }
                    list.append(accounts)

                return JsonResponse({'status':True,'accounts':list},safe=False)

        return JsonResponse({'status':False})
    else:
       return redirect('/')
    
def Fin_changeItemStatus(request,id,status):
    if 's_id' in request.session:
        
        item = Fin_Items.objects.get(id = id)
        item.status = status
        item.save()
        return redirect(Fin_viewItem, id)

def Fin_editItem(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        item = Fin_Items.objects.get(id = id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
            units = Fin_Units.objects.filter(Company = com)
            acc = Fin_Chart_Of_Account.objects.filter(Q(account_type='Expense') | Q(account_type='Other Expense') | Q(account_type='Cost Of Goods Sold'), Company=com).order_by('account_name')
            return render(request,'company/Fin_Edit_Item.html',{'allmodules':allmodules,'com':com,'data':data,'units':units, 'accounts':acc, 'item':item})
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            units = Fin_Units.objects.filter(Company = com.company_id)
            acc = Fin_Chart_Of_Account.objects.filter(Q(account_type='Expense') | Q(account_type='Other Expense') | Q(account_type='Cost Of Goods Sold'), Company=com.company_id).order_by('account_name')
            return render(request,'company/Fin_Edit_Item.html',{'allmodules':allmodules,'com':com,'data':data,'units':units, 'accounts':acc, 'item':item})
    else:
       return redirect('/')
    

def Fin_updateItem(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        item = Fin_Items.objects.get(id = id)
        if request.method == 'POST':
            name = request.POST['name']
            type = request.POST['type']
            unit = request.POST.get('unit')
            hsn = int(request.POST['hsn'])
            tax = request.POST['taxref']
            gstTax = 0 if tax == 'non taxable' else request.POST['intra_st']
            igstTax = 0 if tax == 'non taxable' else request.POST['inter_st']
            purPrice = request.POST['pcost']
            purAccount =  None if not 'pur_account' in request.POST or request.POST['pur_account'] == "" else request.POST['pur_account']
            purDesc = request.POST['pur_desc']
            salePrice = request.POST['salesprice']
            saleAccount = None if not 'sale_account' in request.POST or request.POST['sale_account'] == "" else request.POST['sale_account']
            saleDesc = request.POST['sale_desc']
            inventory = request.POST.get('invacc')
            stock = item.opening_stock if request.POST.get('stock') == "" else request.POST.get('stock')
            stockUnitRate = 0 if request.POST.get('stock_rate') == "" else request.POST.get('stock_rate')
            minStock = request.POST['min_stock']
            createdDate = date.today()

            oldOpen = int(item.opening_stock)
            newOpen = int(stock)
            diff = abs(oldOpen - newOpen)

            
            #save item and transaction if item or hsn doesn't exists already
            if item.name != name and Fin_Items.objects.filter(Company=com, name__iexact=name).exists():
                res = f'<script>alert("{name} already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)
            elif item.hsn != hsn and Fin_Items.objects.filter(Company = com, hsn__iexact = hsn).exists():
                res = f'<script>alert("HSN - {hsn} already exists, try another.!");window.history.back();</script>'
                return HttpResponse(res)
            else:
                item.Company = com
                item.LoginDetails = data
                item.name = name
                item.item_type = type
                item.unit = unit
                item.hsn = hsn
                item.tax_reference = tax
                item.intra_state_tax = gstTax
                item.inter_state_tax = igstTax
                item.sales_account = saleAccount
                item.selling_price = salePrice
                item.sales_description = saleDesc
                item.purchase_account = purAccount
                item.purchase_price = purPrice
                item.purchase_description = purDesc
                item.item_created = createdDate
                item.min_stock = minStock
                item.inventory_account = inventory
                
                if item.opening_stock != int(stock) and oldOpen > newOpen:
                    item.current_stock -= diff
                elif item.opening_stock != int(stock) and oldOpen < newOpen:
                    item.current_stock += diff
                
                item.opening_stock = stock
                item.stock_unit_rate = stockUnitRate

                item.save()

                #save transaction

                Fin_Items_Transaction_History.objects.create(
                    Company = com,
                    LoginDetails = data,
                    item = item,
                    action = 'Edited'
                )
                
                return redirect(Fin_viewItem, item.id)

        return redirect(Fin_editItem, item.id)
    else:
       return redirect('/')

def Fin_deleteItem(request, id):
    if 's_id' in request.session:
        item = Fin_Items.objects.get(id = id)
        #check whether any transaction are completed for the item(sales,purchase,estimate,bill etc.), if so, restrict deletion.

        item.delete()
        return redirect(Fin_items)

def Fin_itemHistory(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        itm = Fin_Items.objects.get(id = id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
            his = Fin_Items_Transaction_History.objects.filter(Company = com , item = itm)
            return render(request,'company/Fin_Item_History.html',{'allmodules':allmodules,'com':com,'data':data,'history':his, 'item':itm})
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            his = Fin_Items_Transaction_History.objects.filter(Company = com.company_id, item = itm)
            return render(request,'company/Fin_Item_History.html',{'allmodules':allmodules,'com':com,'data':data,'history':his, 'item':itm})
    else:
       return redirect('/')

def Fin_itemTransactionPdf(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
        
        item = Fin_Items.objects.get(id = id)
        stock = int(item.current_stock)
        rate = float(item.stock_unit_rate)
        stockValue = float(stock * rate)
    
        context = {'item': item, 'stockValue':stockValue}
        
        template_path = 'company/Fin_Item_Transaction_Pdf.html'
        fname = 'Item_transactions_'+item.name
        # return render(request, 'company/Fin_Item_Transaction_Pdf.html',context)
        # Create a Django response object, and specify content_type as pdftemp_
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] =f'attachment; filename = {fname}.pdf'
        # find the template and render it.
        template = get_template(template_path)
        html = template.render(context)

        # create a pdf
        pisa_status = pisa.CreatePDF(
        html, dest=response)
        # if error then show some funny view
        if pisa_status.err:
            return HttpResponse('We had some errors <pre>' + html + '</pre>')
        return response
    else:
        return redirect('/')
    
def Fin_shareItemTransactionsToEmail(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        item = Fin_Items.objects.get(id = id)
        try:
            if request.method == 'POST':
                emails_string = request.POST['email_ids']

                # Split the string by commas and remove any leading or trailing whitespace
                emails_list = [email.strip() for email in emails_string.split(',')]
                email_message = request.POST['email_message']
                # print(emails_list)
            
                stock = int(item.current_stock)
                rate = float(item.stock_unit_rate)
                stockValue = float(stock * rate)
            
                context = {'item': item, 'stockValue':stockValue}
                template_path = 'company/Fin_Item_Transaction_Pdf.html'
                template = get_template(template_path)

                html  = template.render(context)
                result = BytesIO()
                pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
                pdf = result.getvalue()
                filename = f'Item_transactions-{item.name}.pdf'
                subject = f"Item_transactions_{item.name}"
                email = EmailMessage(subject, f"Hi,\nPlease find the attached Transaction details - ITEM-{item.name}. \n{email_message}\n\n--\nRegards,\n{com.Company_name}\n{com.Address}\n{com.State} - {com.Country}\n{com.Contact}", from_email=settings.EMAIL_HOST_USER, to=emails_list)
                email.attach(filename, pdf, "application/pdf")
                email.send(fail_silently=False)

                messages.success(request, 'Bill has been shared via email successfully..!')
                return redirect(Fin_viewItem,id)
        except Exception as e:
            print(e)
            messages.error(request, f'{e}')
            return redirect(Fin_viewItem, id)
        
def Fin_addItemComment(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        itm = Fin_Items.objects.get(id = id)
        if request.method == "POST":
            cmt = request.POST['comment'].strip()

            Fin_Items_Comments.objects.create(Company = com, item = itm, comments = cmt)
            return redirect(Fin_viewItem, id)
        return redirect(Fin_viewItem, id)
    return redirect('/')

def Fin_deleteItemComment(request,id):
    if 's_id' in request.session:
        cmt = Fin_Items_Comments.objects.get(id = id)
        itemId = cmt.item.id
        cmt.delete()
        return redirect(Fin_viewItem, itemId)


# Chart of accounts

def Fin_chartOfAccounts(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
            acc = Fin_Chart_Of_Account.objects.filter(Company = com)
            return render(request,'company/Fin_ChartOfAccounts.html',{'allmodules':allmodules,'com':com,'data':data,'accounts':acc})
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            acc = Fin_Chart_Of_Account.objects.filter(Company = com.company_id)
            return render(request,'company/Fin_ChartOfAccounts.html',{'allmodules':allmodules,'com':com,'data':data,'accounts':acc})
    else:
       return redirect('/')

def Fin_addAccount(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
            return render(request,'company/Fin_Add_Account.html',{'allmodules':allmodules,'com':com,'data':data})
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            return render(request,'company/Fin_Add_Account.html',{'allmodules':allmodules,'com':com,'data':data})
    else:
       return redirect('/')
    
def Fin_checkAccounts(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        if Fin_Chart_Of_Account.objects.filter(Company = com, account_type = request.GET['type']).exists():
            list= []
            account_objects = Fin_Chart_Of_Account.objects.filter(Company = com, account_type = request.GET['type'])

            for account in account_objects:
                accounts = {
                    'name': account.account_name,
                }
                list.append(accounts)

            return JsonResponse({'status':True,'accounts':list},safe=False)
        else:
            return JsonResponse({'status':False})

def Fin_createAccount(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        if request.method == 'POST':
            name = request.POST['account_name']
            type = request.POST['account_type']
            subAcc = True if 'subAccountCheckBox' in request.POST else False
            parentAcc = request.POST['parent_account'] if 'subAccountCheckBox' in request.POST else None
            accCode = request.POST['account_code']
            bankAccNum = None if request.POST['account_number'] == "" else request.POST['account_number']
            desc = request.POST['description']
            
            createdDate = date.today()
            
            #save account and transaction if account doesn't exists already
            if Fin_Chart_Of_Account.objects.filter(Company=com, account_name__iexact=name).exists():
                res = f'<script>alert("{name} already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)
            else:
                account = Fin_Chart_Of_Account(
                    Company = com,
                    LoginDetails = data,
                    account_type = type,
                    account_name = name,
                    account_code = accCode,
                    description = desc,
                    balance = 0.0,
                    balance_type = None,
                    credit_card_no = None,
                    sub_account = subAcc,
                    parent_account = parentAcc,
                    bank_account_no = bankAccNum,
                    date = createdDate,
                    create_status = 'added',
                    status = 'active'
                )
                account.save()

                #save transaction

                Fin_ChartOfAccount_History.objects.create(
                    Company = com,
                    LoginDetails = data,
                    account = account,
                    action = 'Created'
                )
                
                return redirect(Fin_chartOfAccounts)

        return redirect(Fin_createAccount)
    else:
       return redirect('/')

def Fin_accountOverview(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        acc = Fin_Chart_Of_Account.objects.get(id = id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
            hist = Fin_ChartOfAccount_History.objects.filter(Company = com, account = acc).last()
            return render(request,'company/Fin_Account_Overview.html',{'allmodules':allmodules,'com':com,'data':data, 'account':acc, 'history':hist})
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            hist = Fin_ChartOfAccount_History.objects.filter(Company = com.company_id, account = acc).last()
            return render(request,'company/Fin_Account_Overview.html',{'allmodules':allmodules,'com':com,'data':data, 'account':acc, 'history':hist})
    else:
       return redirect('/')
    
def Fin_changeAccountStatus(request,id,status):
    if 's_id' in request.session:
        
        acc = Fin_Chart_Of_Account.objects.get(id = id)
        acc.status = status
        acc.save()
        return redirect(Fin_accountOverview, id)
    
def Fin_accountTransactionPdf(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
        
        acc = Fin_Chart_Of_Account.objects.get(id = id)
    
        context = {'account': acc}
        
        template_path = 'company/Fin_Account_Transaction_Pdf.html'
        fname = 'Account_transactions_'+acc.account_name
        # return render(request, 'company/Fin_Account_Transaction_Pdf.html',context)
        # Create a Django response object, and specify content_type as pdftemp_
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] =f'attachment; filename = {fname}.pdf'
        # find the template and render it.
        template = get_template(template_path)
        html = template.render(context)

        # create a pdf
        pisa_status = pisa.CreatePDF(
        html, dest=response)
        # if error then show some funny view
        if pisa_status.err:
            return HttpResponse('We had some errors <pre>' + html + '</pre>')
        return response
    else:
        return redirect('/')

def Fin_shareAccountTransactionsToEmail(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        acc = Fin_Chart_Of_Account.objects.get(id = id)
        try:
            if request.method == 'POST':
                emails_string = request.POST['email_ids']

                # Split the string by commas and remove any leading or trailing whitespace
                emails_list = [email.strip() for email in emails_string.split(',')]
                email_message = request.POST['email_message']
                # print(emails_list)
            
                context = {'account': acc}
                template_path = 'company/Fin_Account_Transaction_Pdf.html'
                template = get_template(template_path)

                html  = template.render(context)
                result = BytesIO()
                pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
                pdf = result.getvalue()
                filename = f'Account_transactions-{acc.account_name}.pdf'
                subject = f"Account_transactions_{acc.account_name}"
                email = EmailMessage(subject, f"Hi,\nPlease find the attached Transaction details - ACCOUNT-{acc.account_name}. \n{email_message}\n\n--\nRegards,\n{com.Company_name}\n{com.Address}\n{com.State} - {com.Country}\n{com.Contact}", from_email=settings.EMAIL_HOST_USER, to=emails_list)
                email.attach(filename, pdf, "application/pdf")
                email.send(fail_silently=False)

                messages.success(request, 'Bill has been shared via email successfully..!')
                return redirect(Fin_accountOverview,id)
        except Exception as e:
            print(e)
            messages.error(request, f'{e}')
            return redirect(Fin_accountOverview, id)

def Fin_deleteAccount(request, id):
    if 's_id' in request.session:
        acc = Fin_Chart_Of_Account.objects.get( id = id)
        acc.delete()
        return redirect(Fin_chartOfAccounts)

def Fin_editAccount(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
            acc = Fin_Chart_Of_Account.objects.get(id = id)
            return render(request,'company/Fin_Edit_Account.html',{'allmodules':allmodules,'com':com,'data':data, 'account':acc})
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            acc = Fin_Chart_Of_Account.objects.get(id = id)
            return render(request,'company/Fin_Edit_Account.html',{'allmodules':allmodules,'com':com,'data':data, 'account':acc})
    else:
       return redirect('/')

def Fin_updateAccount(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        acc = Fin_Chart_Of_Account.objects.get(id = id)
        if request.method == 'POST':
            name = request.POST['account_name']
            subAcc = True if 'subAccountCheckBox' in request.POST else False
            parentAcc = request.POST['parent_account'] if 'subAccountCheckBox' in request.POST else None
            accCode = request.POST['account_code']
            bankAccNum = None if request.POST['account_number'] == "" else request.POST['account_number']
            desc = request.POST['description']
            
            #save account and transaction if account doesn't exists already
            if acc.account_name != name and Fin_Chart_Of_Account.objects.filter(Company=com, account_name__iexact=name).exists():
                res = f'<script>alert("{name} already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)
            else:
                acc.account_name = name
                acc.account_code = accCode
                acc.description = desc
                acc.sub_account = subAcc
                acc.parent_account = parentAcc
                acc.bank_account_no = bankAccNum
                acc.save()

                #save transaction
                if acc.create_status == 'added':
                    Fin_ChartOfAccount_History.objects.create(
                        Company = com,
                        LoginDetails = data,
                        account = acc,
                        action = 'Edited'
                    )
                
                return redirect(Fin_accountOverview, id)

        return redirect(Fin_editAccount, id)
    else:
       return redirect('/')
    
def Fin_accountHistory(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        acc = Fin_Chart_Of_Account.objects.get(id = id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
            his = Fin_ChartOfAccount_History.objects.filter(Company = com , account = acc)
            return render(request,'company/Fin_Account_History.html',{'allmodules':allmodules,'com':com,'data':data,'history':his, 'account':acc})
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            his = Fin_ChartOfAccount_History.objects.filter(Company = com.company_id, account = acc)
            return render(request,'company/Fin_Account_History.html',{'allmodules':allmodules,'com':com,'data':data,'history':his, 'account':acc})
    else:
       return redirect('/')
       
#End

def Fin_bankholder(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        try:
            data = Fin_Login_Details.objects.get(id=s_id)
            if data.User_Type == "Company":
                com = Fin_Company_Details.objects.get(Login_Id=s_id)
                allmodules = Fin_Modules_List.objects.get(Login_Id=s_id,status='New')
                bank_holders = Fin_BankHolder.objects.filter(Company=com)
                comments = Fin_BankHolderComment.objects.filter(Company=com)
                history = Fin_BankHolderHistory.objects.filter(Company=com)
                banking_details = Fin_Banking.objects.filter(company=com) 
                
            else:
                com = Fin_Staff_Details.objects.get(Login_Id=s_id)
                # com = staff_details.company_id 
                allmodules = Fin_Modules_List.objects.get(company_id=com.company_id, status='New')
                bank_holders = Fin_BankHolder.objects.filter(Company=com.company_id)
                comments = Fin_BankHolderComment.objects.filter(Company=com.company_id)
                history = Fin_BankHolderHistory.objects.filter(Company=com.company_id)
                banking_details = Fin_Banking.objects.filter(company=com.company_id) 
            
            sort_by = request.GET.get('sort_by', None)
            if sort_by == 'holder_name':
                bank_holders = bank_holders.order_by('Holder_name')
            elif sort_by == 'bank_name':
                bank_holders = bank_holders.order_by('Bank_name')

            context = {
                'com': com,
                'bank_holders': bank_holders,
                'comments': comments,
                'history': history,
                'sort_by': sort_by,
                'banking_details':banking_details,
                'allmodules':allmodules,
                'data':data,              
            }
            return render(request, 'company/Fin_Bankholders.html', context)
        except Fin_Login_Details.DoesNotExist:
            return redirect('/')
    else:
        return redirect('/')  


def Fin_addbank(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        try:
            data = Fin_Login_Details.objects.get(id=s_id)
            if data.User_Type == "Company":
                com = Fin_Company_Details.objects.get(Login_Id=data)
                allmodules = Fin_Modules_List.objects.get(Login_Id=s_id,status='New')
                bank_names = Fin_Banking.objects.filter(company=com).values_list('bank_name', flat=True).distinct()
                bank_holders = Fin_BankHolder.objects.filter(Company=com)
                comments = Fin_BankHolderComment.objects.filter(Company=com)
                history = Fin_BankHolderHistory.objects.filter(Company=com)
                banking_details = Fin_Banking.objects.filter(company=com)
                bank_history = Fin_BankingHistory.objects.filter(company=com)
            else:
                com = Fin_Staff_Details.objects.get(Login_Id=data)
                # com = staff_details.company_id 
                allmodules = Fin_Modules_List.objects.get(company_id=com.company_id, status='New')
                bank_names = Fin_Banking.objects.filter(company=com.company_id).values_list('bank_name', flat=True).distinct()
                bank_holders = Fin_BankHolder.objects.filter(Company=com.company_id)
                comments = Fin_BankHolderComment.objects.filter(Company=com.company_id)
                history = Fin_BankHolderHistory.objects.filter(Company=com.company_id)
                banking_details = Fin_Banking.objects.filter(company=com.company_id)
                bank_history = Fin_BankingHistory.objects.filter(company=com.company_id)

           

            context = {
                'com': com,
                'bank_names': bank_names,
                'bank_holders':bank_holders,
                'comments':comments,
                'history':history,
                'banking_details':banking_details,
                'bank_history':bank_history,
                'LoginDetails': data,
                'allmodules':allmodules,
                'data':data,

            }
            return render(request, 'company/Fin_Createbankholder.html', context)
        except Fin_Login_Details.DoesNotExist:
            return redirect('/') 
    return redirect('Fin_bankholder')

def Fin_fetchaccountnumbers(request):
    try:
        if request.method == 'GET' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
            selected_bank = request.GET.get('bank_name', None)

            if 's_id' in request.session:
                s_id = request.session['s_id']
                try:
                    user_data = Fin_Login_Details.objects.get(id=s_id)

                    if user_data.User_Type == "Company":
                        company = Fin_Company_Details.objects.get(Login_Id=s_id)
                    else:
                        staff_details = Fin_Staff_Details.objects.get(Login_Id=s_id)
                        company = staff_details.company_id

                    if selected_bank:
                        account_numbers_queryset = Fin_Banking.objects.filter(bank_name=selected_bank, company=company)
                        account_numbers = [
                            {
                                'account_number': account.account_number,
                                'ifsc_code': account.ifsc_code,
                                'branch_name': account.branch_name
                            }
                            for account in account_numbers_queryset
                        ]
                        data = {'account_numbers': account_numbers}
                        return JsonResponse(data, safe=False)
                except Fin_Login_Details.DoesNotExist:
                    return JsonResponse({'error': 'User not found'}, status=404)
            else:
                return JsonResponse({'error': 'User not authenticated'}, status=401)

        return JsonResponse({}, status=400)
    except Exception as e:
        print(f"Error in Fin_fetchaccountnumbers: {str(e)}")
        return JsonResponse({'error': 'Internal Server Error'}, status=500)

def Fin_fetchallbanks(request):
    try:
        if 's_id' in request.session:
            s_id = request.session['s_id']
            user_data = Fin_Login_Details.objects.get(id=s_id)

            if user_data.User_Type == "Company":
                company = Fin_Company_Details.objects.get(Login_Id=s_id)
            else:
                staff_details = Fin_Staff_Details.objects.get(Login_Id=s_id)
                company = staff_details.company_id

            banks = Fin_Banking.objects.filter(company=company).values('bank_name')

            return JsonResponse({'banks': list(banks)})
        else:
            return JsonResponse({'error': 'User not authenticated'}, status=401)
    except Exception as e:
        print(f"Error in Fin_fetchallbanks: {str(e)}")
        return JsonResponse({'error': 'Internal Server Error'}, status=500)
    
def Fin_Bankaccountholder(request):
    selected_bank = None
    error_message_phone = ""
    error_message_email = ""
    error_message_account = ""
    e = None

    if 's_id' in request.session:
        s_id = request.session['s_id']
        try:
            data = Fin_Login_Details.objects.get(id=s_id)

            if data.User_Type == "Company":
                com = Fin_Company_Details.objects.get(Login_Id=data)
            else:
                staff_details = Fin_Staff_Details.objects.get(Login_Id=data)
                com = staff_details.company_id  

            if request.method == "POST":
                try:
                    swift_code = request.POST['swiftCode']
                    name = request.POST['name']
                    alias = request.POST['alias']
                    phone_number = request.POST['phone_number']
                    email = request.POST['email']
                    account_type = request.POST['account_type']
                    mailing_name = request.POST['mailingName']
                    address = request.POST['address']
                    country = request.POST['country']
                    state = request.POST['state']
                    pin = request.POST['pin']
                    date = request.POST['date']
                    amount = request.POST['Opening']
                    pan_it_number = request.POST['pan_it_number']
                    registration_type = request.POST['registration_type']
                    gstin_un = request.POST['gstin_un']
                    types = request.POST['termof']
                    set_cheque_book_range = request.POST['set_cheque_book_range']
                    enable_cheque_printing = request.POST['enable_cheque_printing']
                    set_cheque_printing_configuration = request.POST['set_cheque_printing_configuration']
                    if 'bank_name' in request.POST:
                        selected_bank_name = request.POST['bank_name']
                        account_number = request.POST.get('accountNumber', '')
                        bank_queryset = Fin_Banking.objects.filter(company=com,bank_name=selected_bank_name, account_number=account_number)

                        if not bank_queryset.exists():
                            selected_bank = Fin_Banking.objects.create(
                                company=com,
                                bank_name=selected_bank_name,
                                branch_name=request.POST.get('branch_name', ''),
                                ifsc_code=request.POST.get('ifscCode', ''),
                                account_number=account_number
                            )
                        else:
                            for bank_instance in bank_queryset:
                                bank_instance.branch_name = request.POST.get('branch_name', '')
                                bank_instance.ifsc_code = request.POST.get('ifscCode', '')
                                bank_instance.save()

                            selected_bank = bank_queryset.first()

                    swift_code = request.POST.get('swiftCode', '') 

                    if Fin_BankHolder.objects.filter(
                        Q(Account_number=selected_bank.account_number) |
                        Q(phone_number=phone_number) |
                        Q(Email=email)
                    ).exclude(LoginDetails=data).exists():
                        if 'phone_number' in str(e):
                            error_message_phone = "Phone number is already in use by another holder."
                        elif 'email' in str(e):
                            error_message_email = "Email is already in use by another holder."
                        elif 'account_number' in str(e):
                            error_message_account = "Account number is already in use by another holder."
                        else:
                            raise e
                        context = {
                            'bank': bank_queryset,
                            'error_message_phone': error_message_phone,
                            'error_message_email': error_message_email,
                            'error_message_account': error_message_account,
                        }
                        return render(request, 'company/Fin_Createbankholder.html', context)
                    
                    account_holder = Fin_BankHolder(
                        LoginDetails=data,
                        Company=com,
                        Holder_name=name,
                        Alias=alias,
                        phone_number=phone_number,
                        Email=email,
                        Account_type=account_type,
                        Mailing_name=mailing_name,
                        Address=address,
                        Country=country,
                        State=state,
                        Pin=pin,
                        Date=date,
                        ArithmeticErrormount=amount,
                        Open_type=types,
                        Pan_it_number=pan_it_number,
                        Registration_type=registration_type,
                        Gstin_un=gstin_un,
                        Swift_code=swift_code,
                        Bank_name=selected_bank.bank_name,
                        Account_number=selected_bank.account_number,
                        Branch_name=selected_bank.branch_name,
                        Ifsc_code = selected_bank.ifsc_code,
                        Set_cheque_book_range=True if set_cheque_book_range == "Yes" else False,
                        Enable_cheque_printing=True if enable_cheque_printing == "Yes" else False,
                        Set_cheque_printing_configuration=True if set_cheque_printing_configuration == "Yes" else False,
                    )
                    account_holder.save()

                    account_holder.banking_details = selected_bank
                    account_holder.save()

                    Fin_BankHolderHistory.objects.create(
                        Company=com,
                        LoginDetails=data,
                        Holder=account_holder,
                        date=timezone.now(),
                        action='Created'
                    )
                    return redirect('Fin_bankholder')
                
                except IntegrityError as e:
                    if 'phone_number' in str(e):
                        error_message_phone = "Phone number is already in use by another holder."
                    elif 'email' in str(e):
                        error_message_email = "Email is already in use by another holder."
                    elif 'account_number' in str(e):
                        error_message_account = "Account number is already in use by another holder."
                    else:
                        error_message_account = "Error in creating bank holder."

                    context = {
                        'bank': bank_queryset,
                        'error_message_phone': error_message_phone,
                        'error_message_email': error_message_email,
                        'error_message_account': error_message_account,
                    }
                    return render(request, 'company/Fin_Createbankholder.html', context)
                
            else:
                bank_queryset = Fin_Banking.objects.filter(company=com)
                context = {'bank': bank_queryset}
                return render(request, 'company/Fin_Createbankholder.html', context)
        
        except Fin_Login_Details.DoesNotExist:
            return redirect('/')
    
    return redirect('Fin_bankholder')

def Fin_AddBankinHolder(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        try:
            data = Fin_Login_Details.objects.get(id=s_id)

            if data.User_Type == "Company":
                com = Fin_Company_Details.objects.get(Login_Id=data)
                bank_queryset = Fin_Banking.objects.filter(company=com)
            else:
                staff_details = Fin_Staff_Details.objects.get(Login_Id=data)
                com = staff_details.company_id  
                bank_queryset = Fin_Banking.objects.filter(company=com)

            # bank_queryset = Fin_Banking.objects.filter(company=com)

            if request.method == 'POST':
                bank_name = request.POST.get('bank_name')
                ifsc_code = request.POST.get('ifsc_code')
                account_number = request.POST.get('account_number')
                branch_name = request.POST.get('branch_name')

                if not all([bank_name, ifsc_code, account_number, branch_name]):
                    return JsonResponse({'error_message': 'All fields are required'}, status=400)

                new_bank = Fin_Banking(
                    company=com,
                    bank_name=bank_name,
                    ifsc_code=ifsc_code,
                    account_number=account_number,
                    branch_name=branch_name,
                )
                new_bank.save()
                
                return JsonResponse({
                    'bank_name': new_bank.bank_name,
                })

        except Fin_Login_Details.DoesNotExist:
            return redirect('/')
    return JsonResponse({'error_message': 'Invalid request'}, status=400)
    
def Fin_Bankholderview(request, id):
    print(f"Requested ID: {id}")
    if 's_id' in request.session:
        s_id = request.session['s_id']
        try:
            data = Fin_Login_Details.objects.get(id=s_id)
            if data.User_Type == "Company":
                com = Fin_Company_Details.objects.get(Login_Id=data)
                allmodules = Fin_Modules_List.objects.get(Login_Id=s_id,status='New')
                account_holder = get_object_or_404(Fin_BankHolder, id=id)
                try:
                    banking_details = account_holder.banking_details
                except Fin_BankHolder.DoesNotExist:
                    banking_details = None
                last_history_entry = Fin_BankHolderHistory.objects.filter(Holder_id=account_holder).order_by('date').last()
                comments = Fin_BankHolderComment.objects.filter(Holder=account_holder, Company=com)
            else:
                com = Fin_Staff_Details.objects.get(Login_Id=data)
                # com = staff_details.company_id
                allmodules = Fin_Modules_List.objects.get(company_id=com.company_id, status='New')
                account_holder = get_object_or_404(Fin_BankHolder, id=id)
                try:
                    banking_details = account_holder.banking_details
                except Fin_BankHolder.DoesNotExist:
                    banking_details = None
                last_history_entry = Fin_BankHolderHistory.objects.filter(Holder_id=account_holder).order_by('date').last()
                comments = Fin_BankHolderComment.objects.filter(Holder=account_holder, Company=com.company_id)


            context = {
                'account_holder': account_holder,
                'banking_details': banking_details,
                'com': com,
                'last_history_entry': last_history_entry,
                'comments': comments,
                'allmodules':allmodules,
                'data':data,
            }

            return render(request, 'company/Fin_Bankholderview.html', context)
        except Fin_Login_Details.DoesNotExist:
            return redirect('/')  
    return redirect('Fin_bankholder')


def Fin_activebankholder(request, id):
    account_holder = Fin_BankHolder.objects.get(id=id)
    account_holder.is_active = True
    account_holder.save()
    return redirect('Fin_Bankholderview', id=id)


def Fin_inactivatebankaccount(request, id):
    account_holder= Fin_BankHolder.objects.get(id=id)
    account_holder.is_active = False
    account_holder.save()
    return redirect('Fin_Bankholderview', id=id)

def Fin_Editbankholder(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        try:
            data = Fin_Login_Details.objects.get(id=s_id)
            if data.User_Type == "Company":
                com = Fin_Company_Details.objects.get(Login_Id=s_id)
                allmodules = Fin_Modules_List.objects.get(Login_Id=s_id, status='New')
                account_holder = get_object_or_404(Fin_BankHolder, id=id)
                banking_details = account_holder.banking_details  
            else:
                com = Fin_Staff_Details.objects.get(Login_Id=s_id)
                allmodules = Fin_Modules_List.objects.get(company_id=com.company_id, status='New')
                account_holder = get_object_or_404(Fin_BankHolder, id=id)
                banking_details = account_holder.banking_details  

            context = {
                'com': com,
                'account_holder': account_holder,
                'banking_details': banking_details,
                'allmodules': allmodules,
                'data': data,
            }
            return render(request, 'company/Fin_Editbankholder.html', context)
        except Fin_Login_Details.DoesNotExist:
            return redirect('/') 
    return redirect('Fin_bankholder')



def Fin_Editholder(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        try:
            data = Fin_Login_Details.objects.get(id=s_id)
            if data.User_Type == "Company":
                com = Fin_Company_Details.objects.get(Login_Id=s_id)
            else:
                staff_details = Fin_Staff_Details.objects.get(Login_Id=s_id)
                com = staff_details.company_id
            account_holder = get_object_or_404(Fin_BankHolder, id=id, Company=com)

            if request.method == "POST":
                try:
                    name = request.POST.get('name')
                    alias = request.POST.get('alias')
                    phone_number = request.POST.get('phone_number')
                    email = request.POST.get('email')
                    account_type = request.POST.get('account_type')
                    mailing_name = request.POST.get('mailingName')
                    address = request.POST.get('address')
                    country = request.POST.get('country')
                    state = request.POST.get('state')
                    pin = request.POST.get('pin')
                    date_str = request.POST.get('date')
                    amount = request.POST.get('Opening')
                    types = request.POST.get('termof')
                    pan_it_number = request.POST.get('pan_it_number')
                    registration_type = request.POST.get('registration_type')
                    gstin_un = request.POST.get('gstin_un')
                    account_number = request.POST.get('accountNumber')
                    ifsc_code = request.POST.get('ifscCode')
                    swift_code = request.POST.get('swiftCode')
                    bank_name = request.POST.get('bank_name')
                    branch_name = request.POST.get('branch_name')
                    set_cheque_book_range = request.POST.get('set_cheque_book_range')
                    enable_cheque_printing = request.POST.get('enable_cheque_printing')
                    set_cheque_printing_configuration = request.POST.get('set_cheque_printing_configuration')

                    date = datetime.strptime(date_str, '%Y-%m-%d').date()

                    account_holder.Holder_name = name
                    account_holder.Alias = alias
                    account_holder.phone_number = phone_number
                    account_holder.Email = email
                    account_holder.Account_type = account_type
                    account_holder.Account_number = account_number
                    account_holder.Ifsc_code = ifsc_code
                    account_holder.Swift_code = swift_code
                    account_holder.Bank_name = bank_name
                    account_holder.Branch_name = branch_name
                    account_holder.Mailing_name = mailing_name
                    account_holder.Address = address
                    account_holder.Country = country
                    account_holder.State = state
                    account_holder.Pin = pin
                    account_holder.Date = date
                    account_holder.ArithmeticErrormount = amount
                    account_holder.Open_type = types
                    account_holder.Pan_it_number = pan_it_number
                    account_holder.Registration_type = registration_type
                    account_holder.Gstin_un = gstin_un
                    account_holder.Set_cheque_book_range = True if set_cheque_book_range == "Yes" else False
                    account_holder.Enable_cheque_printing = True if enable_cheque_printing == "Yes" else False
                    account_holder.Set_cheque_printing_configuration = True if set_cheque_printing_configuration == "Yes" else False

                    if 'bank_name' in request.POST:
                        selected_bank_name = request.POST['bank_name']
                        account_number = request.POST.get('accountNumber', '')
                        bank_queryset = Fin_Banking.objects.filter(bank_name=selected_bank_name, account_number=account_number)

                        if not bank_queryset.exists():
                            selected_bank = Fin_Banking.objects.create(
                                bank_name=selected_bank_name,
                                branch_name=request.POST.get('branch_name', ''),
                                ifsc_code=request.POST.get('ifscCode', ''),
                                account_number=account_number
                            )
                        else:
                            for bank_instance in bank_queryset:
                                bank_instance.branch_name = request.POST.get('branch_name', '')
                                bank_instance.ifsc_code = request.POST.get('ifscCode', '')
                                bank_instance.save()

                            selected_bank = bank_queryset.first()

                        account_holder.banking_details = selected_bank

                        account_holder.Bank_name = selected_bank.bank_name
                        account_holder.Account_number = selected_bank.account_number
                        account_holder.Branch_name = selected_bank.branch_name
                        account_holder.Ifsc_code = selected_bank.ifsc_code

                        account_holder.save()

                        Fin_BankHolderHistory.objects.create(
                            LoginDetails=data,
                            Company=com,
                            Holder=account_holder,
                            date=date,
                            action='Edited'
                        )
                    return redirect('Fin_Bankholderview', id)

                except IntegrityError as e:
                    error_message_phone = ""
                    error_message_email = ""
                    error_message_account = ""
                    error_message_swift = ""

                    if 'phone_number' in str(e):
                        error_message_phone = "Phone number is already in use by another holder."
                    elif 'email' in str(e):
                        error_message_email = "Email is already in use by another holder."
                    elif 'account_number' in str(e):
                        error_message_account = "Account number is already in use by another holder."
                    elif 'swift_code' in str(e):
                        error_message_swift = "Swift code is already in use by another holder."
                    else:
                        raise e
                    
                    bank_queryset = Fin_Banking.objects.all()
                    context = {
                        'bank': selected_bank,
                        'account_holder': account_holder,
                        'error_message_phone': error_message_phone,
                        'error_message_email': error_message_email,
                        'error_message_account': error_message_account,
                        'error_message_swift': error_message_swift,
                    }
                    return render(request, 'company/Fin_Editholder.html', context)

            bank_queryset = Fin_Banking.objects.all()
            context = {'bank': bank_queryset, 'account_holder': account_holder}
            return render(request, 'company/Fin_Editbankholder.html', context)

        except Fin_Login_Details.DoesNotExist:
            return redirect('/')

    return redirect('Fin_bankholder') 


def Fin_deleteholder(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        try:
            data = Fin_Login_Details.objects.get(id=s_id)
            if data.User_Type == "Company":
                com = Fin_Company_Details.objects.get(Login_Id=s_id)
            else:
                staff_details = Fin_Staff_Details.objects.get(Login_Id=s_id)
                com = staff_details.company_id 
            try:
                account_holder = Fin_BankHolder.objects.get(id=id, Company=com)
                banking_details = account_holder.banking_details
                Fin_BankHolderComment.objects.filter(Holder_id=account_holder).delete()
                Fin_BankHolderHistory.objects.filter(Holder_id=account_holder).delete()
                account_holder.delete()
                banking_details.delete()
                return redirect('Fin_bankholder')
            except Fin_BankHolder.DoesNotExist:
                message = f"Fin_BankHolder instance with ID {id} does not exist for the company {com}"
                return render(request, '404.html', {'message': message}, status=404)
        except Fin_Login_Details.DoesNotExist:
            return redirect('/')  
    return redirect('Fin_bankholder')

def Fin_addcomment(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        try:
            data = Fin_Login_Details.objects.get(id=s_id)

            if data.User_Type == "Company":
                com = Fin_Company_Details.objects.get(Login_Id=s_id)
            else:
                staff_details = Fin_Staff_Details.objects.get(Login_Id=s_id)
                com = staff_details.company_id

            account_holder = get_object_or_404(Fin_BankHolder, id=id)

            if request.method == 'POST':
                comment_text = request.POST.get('comment')
                print("Received Comment Text:", comment_text)

                comment = Fin_BankHolderComment.objects.create(
                    comment_text=comment_text,
                    Holder=account_holder,
                    LoginDetails=data,
                    Company=com
                )
                comment.save()
                print("Comment Saved in the Database")

            comments = Fin_BankHolderComment.objects.filter(Holder=account_holder, Company=com)
            print("Comments in view:", comments)

            if account_holder.id is not None:
                return redirect(reverse('Fin_Bankholderview', kwargs={'id': id}))
            else:
                return HttpResponse("Invalid account holder ID")

        except Fin_Login_Details.DoesNotExist:
            print("Error: Fin_Login_Details.DoesNotExist")
            return redirect('/')

    print("Redirecting to /")
    return redirect('/') 



def Fin_deletecomment(request, id):
    comment = get_object_or_404(Fin_BankHolderComment, id=id)
    comment.delete() 
    return redirect(reverse('Fin_addcomment', args=[comment.Holder.id]))



def Fin_Bankhistory(request, holder_id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        try:
            data = Fin_Login_Details.objects.get(id=s_id)

            if data.User_Type == "Company":
                com = Fin_Company_Details.objects.get(Login_Id=s_id)
                allmodules = Fin_Modules_List.objects.get(Login_Id=s_id,status='New')
                account_holder = get_object_or_404(Fin_BankHolder, id=holder_id, Company=com)
                history = Fin_BankHolderHistory.objects.filter(Holder=account_holder).order_by('-date')
            else:
                com = Fin_Staff_Details.objects.get(Login_Id=s_id)
                # com = staff_details.company_id
                allmodules = Fin_Modules_List.objects.get(company_id=com.company_id, status='New')
                account_holder = get_object_or_404(Fin_BankHolder, id=holder_id, Company=com.company_id)
                history = Fin_BankHolderHistory.objects.filter(Holder=account_holder).order_by('-date')


            context = {
                'account_holder': account_holder,
                'history': history,
                'allmodules':allmodules,
                'com':com,
                'data':data,
            }
            return render(request, 'company/Fin_BankHistory.html', context)
        except Fin_Login_Details.DoesNotExist:
            return redirect('/')  
    return redirect('/')
        
# -------------Shemeem--------Price List & Customers-------------------------------

# PriceList

def Fin_priceList(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
            list = Fin_Price_List.objects.filter(Company = com)
            return render(request,'company/Fin_Price_List.html',{'allmodules':allmodules,'com':com,'data':data,'list':list})
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            list = Fin_Price_List.objects.filter(Company = com.company_id)
            return render(request,'company/Fin_Price_List.html',{'allmodules':allmodules,'com':com,'data':data,'list':list})
    else:
       return redirect('/')
    
def Fin_addPriceList(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
            items = Fin_Items.objects.filter(Company = com, status = 'Active').order_by('name')
            return render(request,'company/Fin_Add_Price_List.html',{'allmodules':allmodules,'com':com,'data':data,'items':items})
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            items = Fin_Items.objects.filter(Company = com.company_id, status = 'Active').order_by('name')
            return render(request,'company/Fin_Add_Price_List.html',{'allmodules':allmodules,'com':com,'data':data,'items':items})
    else:
       return redirect('/')

def Fin_createPriceList(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        if request.method == 'POST':
            name = request.POST['name']
            type = request.POST['type']
            itemRate = request.POST['item_rate']
            description = request.POST['description']
            upOrDown = request.POST['up_or_down']
            percent = request.POST['percentage']
            roundOff = request.POST['round_off']
            currency = request.POST['currency']

            if Fin_Price_List.objects.filter(Company = com, name__iexact = name).exists():
                res = f'<script>alert("{name} already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)

            priceList = Fin_Price_List(
                Company = com, LoginDetails = data, name = name, type = type, item_rate = itemRate, description = description, currency = currency, up_or_down = upOrDown, percentage = percent, round_off = roundOff, status = 'Active'
            )
            priceList.save()

            #save transaction

            Fin_PriceList_Transaction_History.objects.create(
                Company = com,
                LoginDetails = data,
                list = priceList,
                action = 'Created'
            )

            if itemRate == 'Customized individual rate':
                itemName = request.POST.getlist('itemName[]')
                stdRate = request.POST.getlist('itemRateSale[]') if type == 'Sales' else request.POST.getlist('itemRatePurchase[]')
                customRate = request.POST.getlist('customRate[]')
                
                if len(itemName) == len(stdRate) == len(customRate):
                    values = zip(itemName,stdRate,customRate)
                    lis = list(values)

                    for ele in lis:
                        Fin_PriceList_Items.objects.get_or_create(Company = com, LoginDetails = data, list = priceList, item = Fin_Items.objects.get(id = int(ele[0])), standard_rate = float(ele[1]), custom_rate = float(ele[2]))

                    return redirect(Fin_priceList)

                return redirect(Fin_addPriceList)

            return redirect(Fin_priceList)

        else:
                return redirect(Fin_addPriceList)
    else:
        return redirect('/')

def Fin_viewPriceList(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        list = Fin_Price_List.objects.get(id = id)
        plItems = Fin_PriceList_Items.objects.filter(list = list)
        cmt = Fin_PriceList_Comments.objects.filter(list = list)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
            hist = Fin_PriceList_Transaction_History.objects.filter(Company = com, list = list).last()
            return render(request,'company/Fin_View_PriceList.html',{'allmodules':allmodules,'com':com,'data':data,'plItems':plItems, 'list':list, 'comments':cmt, 'history': hist})
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            hist = Fin_PriceList_Transaction_History.objects.filter(Company = com.company_id, list = list).last()
            return render(request,'company/Fin_View_PriceList.html',{'allmodules':allmodules,'com':com,'data':data,'plItems':plItems, 'list':list, 'comments':cmt, 'history': hist})
    else:
       return redirect('/')
    
def Fin_changePriceListStatus(request,id,status):
    if 's_id' in request.session:
        list = Fin_Price_List.objects.get(id = id)
        list.status = status
        list.save()
        return redirect(Fin_viewPriceList, id)
    
def Fin_deletePriceList(request, id):
    if 's_id' in request.session:
        list = Fin_Price_List.objects.get( id = id)
        list.delete()
        return redirect(Fin_priceList)
    
def Fin_addPriceListComment(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        list = Fin_Price_List.objects.get(id = id)
        if request.method == "POST":
            cmt = request.POST['comment'].strip()

            Fin_PriceList_Comments.objects.create(Company = com, list = list, comments = cmt)
            return redirect(Fin_viewPriceList, id)
        return redirect(Fin_viewPriceList, id)
    return redirect('/')

def Fin_deletePriceListComment(request,id):
    if 's_id' in request.session:
        cmt = Fin_PriceList_Comments.objects.get(id = id)
        listId = cmt.list.id
        cmt.delete()
        return redirect(Fin_viewPriceList, listId)

def Fin_priceListHistory(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        list = Fin_Price_List.objects.get(id = id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
            his = Fin_PriceList_Transaction_History.objects.filter(Company = com , list = list)
            return render(request,'company/Fin_PriceList_History.html',{'allmodules':allmodules,'com':com,'data':data,'history':his, 'list':list})
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            his = Fin_PriceList_Transaction_History.objects.filter(Company = com.company_id , list = list)
            return render(request,'company/Fin_PriceList_History.html',{'allmodules':allmodules,'com':com,'data':data,'history':his, 'list':list})
    else:
       return redirect('/')
    
def Fin_editPriceList(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        list = Fin_Price_List.objects.get(id = id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
            plItems = Fin_PriceList_Items.objects.filter(Company = com, list = list)
            items = Fin_Items.objects.filter(Company = com, status = 'Active').order_by('name')
            return render(request,'company/Fin_Edit_Price_List.html',{'allmodules':allmodules,'com':com,'data':data,'list':list, 'plItems':plItems, 'items':items })
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            plItems = Fin_PriceList_Items.objects.filter(Company = com.company_id, list = list)
            items = Fin_Items.objects.filter(Company = com.company_id, status = 'Active').order_by('name')
            return render(request,'company/Fin_Edit_Price_List.html',{'allmodules':allmodules,'com':com,'data':data,'list':list, 'plItems':plItems, 'items':items })
    else:
       return redirect('/')

def Fin_updatePriceList(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        lst = Fin_Price_List.objects.get(id = id)
        if request.method == 'POST':
            name = request.POST['name']
            type = request.POST['type']
            itemRate = request.POST['item_rate']
            description = request.POST['description']
            upOrDown = request.POST['up_or_down']
            percent = request.POST['percentage']
            roundOff = request.POST['round_off']
            currency = request.POST['currency']

            if lst.name != name and Fin_Price_List.objects.filter(Company = com, name__iexact = name).exists():
                res = f'<script>alert("{name} already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)

            if lst.item_rate == 'Customized individual rate' and itemRate != 'Customized individual rate':
                Fin_PriceList_Items.objects.filter(list = lst).delete()

            lst.name = name
            lst.type = type
            lst.item_rate = itemRate
            lst.description = description
            lst.currency = currency
            lst.up_or_down = upOrDown
            if itemRate == 'Customized individual rate':
                lst.percentage = None
                lst.round_off = None
            else:
                lst.percentage = percent
                lst.round_off = roundOff
            lst.save()

            #save transaction

            Fin_PriceList_Transaction_History.objects.create(
                Company = com,
                LoginDetails = data,
                list = lst,
                action = 'Edited'
            )

            itemName = request.POST.getlist('itemName[]')
            stdRate = request.POST.getlist('itemRateSale[]') if type == 'Sales' else request.POST.getlist('itemRatePurchase[]')
            customRate = request.POST.getlist('customRate[]')
            
            if itemRate == 'Customized individual rate':
                if Fin_PriceList_Items.objects.filter(list = lst).exists():
                    ids = request.POST.getlist('plItemId[]')
                    
                    if len(ids) == len(itemName) == len(stdRate) == len(customRate):
                        values = zip(ids, itemName,stdRate,customRate)
                        lis = list(values)

                        for ele in lis:
                            Fin_PriceList_Items.objects.filter(id = ele[0]).update(Company = com, LoginDetails = data, list = lst, item = Fin_Items.objects.get(id = int(ele[1])), standard_rate = float(ele[2]), custom_rate = float(ele[3]))

                        return redirect(Fin_viewPriceList,id)

                    else:
                        return redirect(Fin_editPriceList, id)
                else:
                    if len(itemName) == len(stdRate) == len(customRate):
                        values = zip(itemName,stdRate,customRate)
                        lis = list(values)
                        for ele in lis:
                            Fin_PriceList_Items.objects.create(Company = com, LoginDetails = data, list = lst, item = Fin_Items.objects.get(id = int(ele[0])), standard_rate = float(ele[1]), custom_rate = float(ele[2]))
                        
                        return redirect(Fin_viewPriceList,id)
            else:
                return redirect(Fin_viewPriceList,id)

        else:
            return redirect(Fin_editPriceList, id)
    else:
        return redirect('/')

def Fin_priceListViewPdf(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        lst = Fin_Price_List.objects.get(id = id)
        plItems = Fin_PriceList_Items.objects.filter(list = lst)
    
        context = {'list': lst, 'plItems':plItems}
        
        template_path = 'company/Fin_PriceListView_Pdf.html'
        fname = 'Price_List_'+lst.name
        # return render(request, 'company/Fin_PriceListView_Pdf.html',context)
        # Create a Django response object, and specify content_type as pdftemp_
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] =f'attachment; filename = {fname}.pdf'
        # find the template and render it.
        template = get_template(template_path)
        html = template.render(context)

        # create a pdf
        pisa_status = pisa.CreatePDF(
        html, dest=response)
        # if error then show some funny view
        if pisa_status.err:
            return HttpResponse('We had some errors <pre>' + html + '</pre>')
        return response
    else:
        return redirect('/')

def Fin_sharePriceListViewToEmail(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        lst = Fin_Price_List.objects.get(id = id)
        plItems = Fin_PriceList_Items.objects.filter(list = lst)
        try:
            if request.method == 'POST':
                emails_string = request.POST['email_ids']

                # Split the string by commas and remove any leading or trailing whitespace
                emails_list = [email.strip() for email in emails_string.split(',')]
                email_message = request.POST['email_message']
                # print(emails_list)
            
                context = {'list': lst, 'plItems':plItems}
                template_path = 'company/Fin_PriceListView_Pdf.html'
                template = get_template(template_path)

                html  = template.render(context)
                result = BytesIO()
                pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
                pdf = result.getvalue()
                filename = f'Price_list_{lst.name}.pdf'
                subject = f"Price_list_{lst.name}"
                email = EmailMessage(subject, f"Hi,\nPlease find the attached Price List details - Price List-{lst.name}. \n{email_message}\n\n--\nRegards,\n{com.Company_name}\n{com.Address}\n{com.State} - {com.Country}\n{com.Contact}", from_email=settings.EMAIL_HOST_USER, to=emails_list)
                email.attach(filename, pdf, "application/pdf")
                email.send(fail_silently=False)

                messages.success(request, 'Price List details has been shared via email successfully..!')
                return redirect(Fin_viewPriceList,id)
        except Exception as e:
            print(e)
            messages.error(request, f'{e}')
            return redirect(Fin_viewPriceList, id)


# Customers
        
def Fin_customers(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
            cust = Fin_Customers.objects.filter(Company = com)
            return render(request,'company/Fin_Customers.html',{'allmodules':allmodules,'com':com,'data':data,'customers':cust})
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            cust = Fin_Customers.objects.filter(Company = com.company_id)
            return render(request,'company/Fin_Customers.html',{'allmodules':allmodules,'com':com,'data':data,'customers':cust})
    else:
       return redirect('/')

def Fin_addCustomer(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
            trms = Fin_Company_Payment_Terms.objects.filter(Company = com)
            lst = Fin_Price_List.objects.filter(Company = com, status = 'Active')
            return render(request,'company/Fin_Add_Customer.html',{'allmodules':allmodules,'com':com,'data':data, 'pTerms':trms, 'list':lst})
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            trms = Fin_Company_Payment_Terms.objects.filter(Company = com.company_id)
            lst = Fin_Price_List.objects.filter(Company = com.company_id, status = 'Active')
            return render(request,'company/Fin_Add_Customer.html',{'allmodules':allmodules,'com':com,'data':data, 'pTerms':trms, 'list':lst})
    else:
       return redirect('/')

def Fin_checkCustomerName(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        fName = request.POST['fname']
        lName = request.POST['lname']

        if Fin_Customers.objects.filter(Company = com, first_name__iexact = fName, last_name__iexact = lName).exists():
            msg = f'{fName} {lName} already exists, Try another.!'
            return JsonResponse({'is_exist':True, 'message':msg})
        else:
            return JsonResponse({'is_exist':False})
    else:
        return redirect('/')
    
def Fin_checkCustomerGSTIN(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        gstIn = request.POST['gstin']

        if Fin_Customers.objects.filter(Company = com, gstin__iexact = gstIn).exists():
            msg = f'{gstIn} already exists, Try another.!'
            return JsonResponse({'is_exist':True, 'message':msg})
        else:
            return JsonResponse({'is_exist':False})
    else:
        return redirect('/')
    
def Fin_checkCustomerPAN(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        pan = request.POST['pan']

        if Fin_Customers.objects.filter(Company = com, pan_no__iexact = pan).exists():
            msg = f'{pan} already exists, Try another.!'
            return JsonResponse({'is_exist':True, 'message':msg})
        else:
            return JsonResponse({'is_exist':False})
    else:
        return redirect('/')

def Fin_checkCustomerPhone(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        phn = request.POST['phone']

        if Fin_Customers.objects.filter(Company = com, mobile__iexact = phn).exists():
            msg = f'{phn} already exists, Try another.!'
            return JsonResponse({'is_exist':True, 'message':msg})
        else:
            return JsonResponse({'is_exist':False})
    else:
        return redirect('/')

def Fin_checkCustomerEmail(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        email = request.POST['email']

        if Fin_Customers.objects.filter(Company = com, email__iexact = email).exists():
            msg = f'{email} already exists, Try another.!'
            return JsonResponse({'is_exist':True, 'message':msg})
        else:
            return JsonResponse({'is_exist':False})
    else:
        return redirect('/')
    
def Fin_createCustomer(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        if request.method == 'POST':
            fName = request.POST['first_name']
            lName = request.POST['last_name']
            gstIn = request.POST['gstin']
            pan = request.POST['pan_no']
            email = request.POST['email']
            phn = request.POST['mobile']

            if Fin_Customers.objects.filter(Company = com, first_name__iexact = fName, last_name__iexact = lName).exists():
                res = f'<script>alert("Customer `{fName} {lName}` already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)
            elif Fin_Customers.objects.filter(Company = com, gstin__iexact = gstIn).exists():
                res = f'<script>alert("GSTIN `{gstIn}` already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)
            elif Fin_Customers.objects.filter(Company = com, pan_no__iexact = pan).exists():
                res = f'<script>alert("PAN No `{pan}` already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)
            elif Fin_Customers.objects.filter(Company = com, mobile__iexact = phn).exists():
                res = f'<script>alert("Phone Number `{phn}` already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)
            elif Fin_Customers.objects.filter(Company = com, email__iexact = email).exists():
                res = f'<script>alert("Email `{email}` already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)

            cust = Fin_Customers(
                Company = com,
                LoginDetails = data,
                title = request.POST['title'],
                first_name = fName,
                last_name = lName,
                company = request.POST['company_name'],
                location = request.POST['location'],
                place_of_supply = request.POST['place_of_supply'],
                gst_type = request.POST['gst_type'],
                gstin = None if request.POST['gst_type'] == "Unregistered Business" or request.POST['gst_type'] == 'Overseas' or request.POST['gst_type'] == 'Consumer' else gstIn,
                pan_no = pan,
                email = email,
                mobile = phn,
                website = request.POST['website'],
                price_list = None if request.POST['price_list'] ==  "" else Fin_Price_List.objects.get(id = request.POST['price_list']),
                payment_terms = None if request.POST['payment_terms'] == "" else Fin_Company_Payment_Terms.objects.get(id = request.POST['payment_terms']),
                opening_balance = 0 if request.POST['open_balance'] == "" else float(request.POST['open_balance']),
                open_balance_type = request.POST['balance_type'],
                current_balance = 0 if request.POST['open_balance'] == "" else float(request.POST['open_balance']),
                credit_limit = 0 if request.POST['credit_limit'] == "" else float(request.POST['credit_limit']),
                billing_street = request.POST['street'],
                billing_city = request.POST['city'],
                billing_state = request.POST['state'],
                billing_pincode = request.POST['pincode'],
                billing_country = request.POST['country'],
                ship_street = request.POST['shipstreet'],
                ship_city = request.POST['shipcity'],
                ship_state = request.POST['shipstate'],
                ship_pincode = request.POST['shippincode'],
                ship_country = request.POST['shipcountry'],
                status = 'Active'
            )
            cust.save()

            #save transaction

            Fin_Customers_History.objects.create(
                Company = com,
                LoginDetails = data,
                customer = cust,
                action = 'Created'
            )

            return redirect(Fin_customers)

        else:
            return redirect(Fin_addCustomer)
    else:
        return redirect('/')

def Fin_newCustomerPaymentTerm(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        term = request.POST['term']
        days = request.POST['days']

        if not Fin_Company_Payment_Terms.objects.filter(Company = com, term_name__iexact = term).exists():
            Fin_Company_Payment_Terms.objects.create(Company = com, term_name = term, days =days)
            
            list= []
            terms = Fin_Company_Payment_Terms.objects.filter(Company = com)

            for term in terms:
                termDict = {
                    'name': term.term_name,
                    'id': term.id
                }
                list.append(termDict)

            return JsonResponse({'status':True,'terms':list},safe=False)
        else:
            return JsonResponse({'status':False})

    else:
        return redirect('/')

def Fin_viewCustomer(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        cust = Fin_Customers.objects.get(id = id)
        cmt = Fin_Customers_Comments.objects.filter(customer = cust)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
            hist = Fin_Customers_History.objects.filter(Company = com, customer = cust).last()
            return render(request,'company/Fin_View_Customer.html',{'allmodules':allmodules,'com':com,'data':data, 'customer':cust, 'history':hist, 'comments':cmt})
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            hist = Fin_Customers_History.objects.filter(Company = com.company_id, customer = cust).last()
            return render(request,'company/Fin_View_Customer.html',{'allmodules':allmodules,'com':com,'data':data, 'customer':cust, 'history':hist, 'comments':cmt})
    else:
       return redirect('/')

def Fin_changeCustomerStatus(request,id,status):
    if 's_id' in request.session:
        
        cust = Fin_Customers.objects.get(id = id)
        cust.status = status
        cust.save()
        return redirect(Fin_viewCustomer, id)
    
def Fin_deleteCustomer(request, id):
    if 's_id' in request.session:
        cust = Fin_Customers.objects.get( id = id)
        cust.delete()
        return redirect(Fin_customers)
    
def Fin_customerHistory(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        cust = Fin_Customers.objects.get(id = id)
        his = Fin_Customers_History.objects.filter(customer = cust)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
            return render(request,'company/Fin_Customer_History.html',{'allmodules':allmodules,'com':com,'data':data,'history':his, 'customer':cust})
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            return render(request,'company/Fin_Customer_History.html',{'allmodules':allmodules,'com':com,'data':data,'history':his, 'customer':cust})
    else:
       return redirect('/')

def Fin_editCustomer(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        cust = Fin_Customers.objects.get(id = id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
            trms = Fin_Company_Payment_Terms.objects.filter(Company = com)
            lst = Fin_Price_List.objects.filter(Company = com, status = 'Active')
            return render(request,'company/Fin_Edit_Customer.html',{'allmodules':allmodules,'com':com,'data':data, 'customer':cust, 'pTerms':trms, 'list':lst})
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            trms = Fin_Company_Payment_Terms.objects.filter(Company = com.company_id)
            lst = Fin_Price_List.objects.filter(Company = com.company_id, status = 'Active')
            return render(request,'company/Fin_Edit_Customer.html',{'allmodules':allmodules,'com':com,'data':data, 'customer':cust, 'pTerms':trms, 'list':lst})
    else:
       return redirect('/')

def Fin_updateCustomer(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        cust = Fin_Customers.objects.get(id = id)

        if request.method == 'POST':
            fName = request.POST['first_name']
            lName = request.POST['last_name']
            gstIn = request.POST['gstin']
            pan = request.POST['pan_no']
            email = request.POST['email']
            phn = request.POST['mobile']

            if cust.first_name != fName and cust.last_name != lName and Fin_Customers.objects.filter(Company = com, first_name__iexact = fName, last_name__iexact = lName).exists():
                res = f'<script>alert("Customer `{fName} {lName}` already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)
            elif cust.gstin != gstIn and Fin_Customers.objects.filter(Company = com, gstin__iexact = gstIn).exists():
                res = f'<script>alert("GSTIN `{gstIn}` already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)
            elif cust.pan_no != pan and Fin_Customers.objects.filter(Company = com, pan_no__iexact = pan).exists():
                res = f'<script>alert("PAN No `{pan}` already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)
            elif cust.mobile != phn and Fin_Customers.objects.filter(Company = com, mobile__iexact = phn).exists():
                res = f'<script>alert("Phone Number `{phn}` already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)
            elif cust.email != email and Fin_Customers.objects.filter(Company = com, email__iexact = email).exists():
                res = f'<script>alert("Email `{email}` already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)

            # Updating customer details

            cust.title = request.POST['title']
            cust.first_name = fName
            cust.last_name = lName
            cust.company = request.POST['company_name']
            cust.location = request.POST['location']
            cust.place_of_supply = request.POST['place_of_supply']
            cust.gst_type = request.POST['gst_type']
            cust.gstin = None if request.POST['gst_type'] == "Unregistered Business" or request.POST['gst_type'] == 'Overseas' or request.POST['gst_type'] == 'Consumer' else gstIn
            cust.pan_no = pan
            cust.email = email
            cust.mobile = phn
            cust.website = request.POST['website']
            cust.price_list = None if request.POST['price_list'] ==  "" else Fin_Price_List.objects.get(id = request.POST['price_list'])
            cust.payment_terms = None if request.POST['payment_terms'] == "" else Fin_Company_Payment_Terms.objects.get(id = request.POST['payment_terms'])
            cust.opening_balance = 0 if request.POST['open_balance'] == "" else float(request.POST['open_balance'])
            cust.open_balance_type = request.POST['balance_type']
            cust.current_balance = 0 if request.POST['open_balance'] == "" else float(request.POST['open_balance'])
            cust.credit_limit = 0 if request.POST['credit_limit'] == "" else float(request.POST['credit_limit'])
            cust.billing_street = request.POST['street']
            cust.billing_city = request.POST['city']
            cust.billing_state = request.POST['state']
            cust.billing_pincode = request.POST['pincode']
            cust.billing_country = request.POST['country']
            cust.ship_street = request.POST['shipstreet']
            cust.ship_city = request.POST['shipcity']
            cust.ship_state = request.POST['shipstate']
            cust.ship_pincode = request.POST['shippincode']
            cust.ship_country = request.POST['shipcountry']

            cust.save()

            #save transaction

            Fin_Customers_History.objects.create(
                Company = com,
                LoginDetails = data,
                customer = cust,
                action = 'Edited'
            )

            return redirect(Fin_viewCustomer, id)

        else:
            return redirect(Fin_editCustomer, id)
    else:
        return redirect('/')

def Fin_customerTransactionsPdf(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        cust = Fin_Customers.objects.get(id = id)
    
        context = {'customer':cust}
        
        template_path = 'company/Fin_Customer_Transaction_Pdf.html'
        fname = 'Customer_Transactions_'+cust.first_name+'_'+cust.last_name
        # return render(request, 'company/Fin_Customer_Transaction_Pdf.html',context)
        # Create a Django response object, and specify content_type as pdftemp_
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] =f'attachment; filename = {fname}.pdf'
        # find the template and render it.
        template = get_template(template_path)
        html = template.render(context)

        # create a pdf
        pisa_status = pisa.CreatePDF(
        html, dest=response)
        # if error then show some funny view
        if pisa_status.err:
            return HttpResponse('We had some errors <pre>' + html + '</pre>')
        return response
    else:
        return redirect('/')

def Fin_shareCustomerTransactionsToEmail(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        cust = Fin_Customers.objects.get(id = id)
        try:
            if request.method == 'POST':
                emails_string = request.POST['email_ids']

                # Split the string by commas and remove any leading or trailing whitespace
                emails_list = [email.strip() for email in emails_string.split(',')]
                email_message = request.POST['email_message']
                # print(emails_list)
            
                context = {'customer': cust}
                template_path = 'company/Fin_Customer_Transaction_Pdf.html'
                template = get_template(template_path)

                html  = template.render(context)
                result = BytesIO()
                pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
                pdf = result.getvalue()
                filename = f'Customer_Transactions_{cust.first_name}_{cust.last_name}'
                subject = f"Customer_Transactions_{cust.first_name}_{cust.last_name}"
                email = EmailMessage(subject, f"Hi,\nPlease find the attached Transaction details for - Customer-{cust.first_name} {cust.last_name}. \n{email_message}\n\n--\nRegards,\n{com.Company_name}\n{com.Address}\n{com.State} - {com.Country}\n{com.Contact}", from_email=settings.EMAIL_HOST_USER, to=emails_list)
                email.attach(filename, pdf, "application/pdf")
                email.send(fail_silently=False)

                messages.success(request, 'Transactions details has been shared via email successfully..!')
                return redirect(Fin_viewCustomer,id)
        except Exception as e:
            print(e)
            messages.error(request, f'{e}')
            return redirect(Fin_viewCustomer, id)

def Fin_addCustomerComment(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        cust = Fin_Customers.objects.get(id = id)
        if request.method == "POST":
            cmt = request.POST['comment'].strip()

            Fin_Customers_Comments.objects.create(Company = com, customer = cust, comments = cmt)
            return redirect(Fin_viewCustomer, id)
        return redirect(Fin_viewCustomer, id)
    return redirect('/')

def Fin_deleteCustomerComment(request,id):
    if 's_id' in request.session:
        cmt = Fin_Customers_Comments.objects.get(id = id)
        custId = cmt.customer.id
        cmt.delete()
        return redirect(Fin_viewCustomer, custId)
        
# End

# harikrishnan start------------------------------
    
def employee_list(request):
    sid = request.session['s_id']
    loginn = Fin_Login_Details.objects.get(id=sid)
    if loginn.User_Type == 'Company':
        com = Fin_Company_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = com.id)
        employee = Employee.objects.filter(company_id=com.id)
    elif loginn.User_Type == 'Staff' :
        com = Fin_Staff_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = com.company_id_id)
        employee = Employee.objects.filter(company_id=com.company_id_id)
    else:
        distributor = Fin_Distributors_Details.objects.get(Login_Id = sid)

    return render(request,'company/Employee_List.html',{'employee':employee,'allmodules':allmodules,'com':com,'data':loginn})

def employee_create_page(request):
    sid = request.session['s_id']
    loginn = Fin_Login_Details.objects.get(id=sid)
    
    if loginn.User_Type == 'Company':
        com = Fin_Company_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = com.id)
        bloodgroup = Employee_Blood_Group.objects.filter(company_id=com.id,login_id=sid).values('blood_group').distinct()
        
    elif loginn.User_Type == 'Staff' :
        com = Fin_Staff_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = com.company_id_id)
        bloodgroup = Employee_Blood_Group.objects.filter(company_id=com.company_id_id,login_id=sid).values('blood_group').distinct()

    return render(request,'company/Employee_Create_Page.html',{'allmodules':allmodules,'bloodgroup':bloodgroup,'com':com,'data':loginn})   

def employee_save(request):

    if request.method == 'POST':

        title = request.POST['Title']
        firstname = request.POST['First_Name'].capitalize()
        lastname = request.POST['Last_Name'].capitalize()
        alias = request.POST['Alias']
        joiningdate = request.POST['Joining_Date']
        salarydate = request.POST['Salary_Date']
        salaryamount = request.POST['Salary_Amount']

        if request.POST['Salary_Amount'] == '':
            salaryamount = None
        else:
            salaryamount = request.POST['Salary_Amount']

        amountperhour = request.POST['perhour']
        if amountperhour == '' or amountperhour == '0':
            amountperhour = 0
        else:
            amountperhour = request.POST['perhour']

        workinghour = request.POST['workhour']
        if workinghour == '' or workinghour == '0':
            workinghour = 0
        else:
            workinghour = request.POST['workhour']

        salary_type = request.POST['Salary_Type']
        
        employeenumber = request.POST['Employee_Number']
        designation = request.POST['Designation']
        location = request.POST['Location']
        gender = request.POST['Gender']
        image = request.FILES.get('Image', None)
        if image:
            image = request.FILES['Image']
        else:
            image = ''

        dob = request.POST['DOB']
        blood = request.POST['Blood']
        parent = request.POST['Parent'].capitalize()
        spouse = request.POST['Spouse'].capitalize()
        street = request.POST['street']
        city = request.POST['city']
        state = request.POST['state']
        pincode = request.POST['pincode']
        country = request.POST['country']
        tempStreet = request.POST['tempStreet']
        tempCity = request.POST['tempCity']
        tempState = request.POST['tempState']
        tempPincode = request.POST['tempPincode']
        tempCountry = request.POST['tempCountry']
        
        
        contact = request.POST['Contact_Number']
        emergencycontact = request.POST['Emergency_Contact']
        email = request.POST['Email']
        file = request.FILES.get('File', None)
        if file:
            file = request.FILES['File']
        else:
            file=''
        bankdetails = request.POST['Bank_Details']
        accoutnumber = request.POST['Account_Number']
        ifsc = request.POST['IFSC']
        bankname = request.POST['BankName']
        branchname = request.POST['BranchName']
        transactiontype = request.POST['Transaction_Type']

        

        if request.POST['tds_applicable'] == 'Yes':
            tdsapplicable = request.POST['tds_applicable']
            tdstype = request.POST['TDS_Type']
            
            if tdstype == 'Amount':
                tdsvalue = request.POST['TDS_Amount']
            elif tdstype == 'Percentage':
                tdsvalue = request.POST['TDS_Percentage']
            else:
                tdsvalue = 0
        elif request.POST['tds_applicable'] == 'No':
            tdsvalue = 0
            tdstype = ''
            tdsapplicable = request.POST['tds_applicable']
        else:
            tdsvalue = 0
            tdstype = ''
            tdsapplicable = ''

        
        
        incometax = request.POST['Income_Tax']
        aadhar = request.POST['Aadhar']
        uan = request.POST['UAN']
        pf = request.POST['PF']
        pan = request.POST['PAN']
        pr = request.POST['PR']

        if dob == '':
            age = 2
        else:
            dob2 = date.fromisoformat(dob)
            today = date.today()
            age = int(today.year - dob2.year - ((today.month, today.day) < (dob2.month, dob2.day)))
        
        sid = request.session['s_id']
        employee = Fin_Login_Details.objects.get(id=sid)
        
        if employee.User_Type == 'Company':
            companykey =  Fin_Company_Details.objects.get(Login_Id_id=sid)
        elif employee.User_Type == 'Staff':
            staffkey = Fin_Staff_Details.objects.get(Login_Id=sid)
            companykey = Fin_Company_Details.objects.get(id=staffkey.company_id_id)
        else:
            distributorkey = Fin_Distributors_Details.objects.get(login_Id=sid)
            companykey = Fin_Company_Details.objects.get(id=distributorkey.company_id_id)

        
        if Employee.objects.filter(employee_mail=email,mobile = contact,employee_number=employeenumber,company_id = companykey.id).exists():
            messages.error(request,'user exist')
            return render(request,'company/Employee_Create_Page.html')
        
        elif Employee.objects.filter(mobile = contact,company_id = companykey.id).exists():
            messages.error(request,'phone number exist')
            return render(request,'company/Employee_Create_Page.html')
        
        elif Employee.objects.filter(employee_mail=email,company_id = companykey.id).exists():
            messages.error(request,'email exist')
            return render(request,'company/Employee_Create_Page.html')
        
        elif Employee.objects.filter(employee_number=employeenumber,company_id = companykey.id).exists():
            messages.error(request,'employee id exist')
            return render(request,'company/Employee_Create_Page.html')
        
        elif Employee.objects.filter(aadhar_number = aadhar,company_id = companykey.id).exists():
            messages.error(request,'Aadhar number exist')
            return render(request,'company/Employee_Create_Page.html')
        
        elif bankdetails.lower() == 'yes':
            if Employee.objects.filter(account_number=accoutnumber,company_id = companykey.id).exists():
                messages.error(request,'Bank account number already exist')
                return render(request,'company/Employee_Create_Page.html')
        
        else:
            if employee.User_Type == 'Company':
                

                new = Employee(upload_image=image,title = title,first_name = firstname,last_name = lastname,alias = alias,
                        employee_mail = email,employee_number = employeenumber,employee_designation = designation,
                        employee_current_location = location,mobile = contact,date_of_joining = joiningdate,
                        employee_status = 'Active' ,company_id = companykey.id,login_id=sid,salary_amount = salaryamount ,
                        amount_per_hour = amountperhour ,total_working_hours = workinghour,gender = gender ,date_of_birth = dob ,
                        age = age,blood_group = blood,fathers_name_mothers_name = parent,spouse_name = spouse,
                        emergency_contact = emergencycontact,provide_bank_details = bankdetails,account_number = accoutnumber,
                        ifsc = ifsc,name_of_bank = bankname,branch_name = branchname,bank_transaction_type = transactiontype,
                        tds_applicable = tdsapplicable, tds_type = tdstype,percentage_amount = tdsvalue,pan_number = pan,
                        income_tax_number = incometax,aadhar_number = aadhar,universal_account_number = uan,pf_account_number = pf,
                        pr_account_number = pr,upload_file = file,employee_salary_type =salary_type,salary_effective_from=salarydate,
                        city=city,street=street,state=state,country=country,pincode=pincode,temporary_city=tempCity,
                        temporary_street=tempStreet,temporary_state=tempState,temporary_pincode=tempPincode,temporary_country=tempCountry)
                new.save()

                history = Employee_History(company_id = companykey.id,login_id=sid,employee_id = new.id,date = date.today(),action = 'Created')
                history.save()
        
            elif employee.User_Type == 'Staff':
                

                new =  Employee(upload_image=image,title = title,first_name = firstname,last_name = lastname,alias = alias,
                            employee_mail = email,employee_number = employeenumber,employee_designation = designation,
                            employee_current_location = location,mobile = contact,date_of_joining = joiningdate,
                            employee_salary_type = salary_type,employee_status = 'Active' ,company_id = companykey.id,login_id=sid ,
                            amount_per_hour = amountperhour ,total_working_hours = workinghour,gender = gender ,date_of_birth = dob ,
                            age = age,blood_group = blood,fathers_name_mothers_name = parent,spouse_name = spouse,
                            emergency_contact = emergencycontact,provide_bank_details = bankdetails,account_number = accoutnumber,
                            ifsc = ifsc,name_of_bank = bankname,branch_name = branchname,bank_transaction_type = transactiontype,
                            tds_applicable = tdsapplicable, tds_type = tdstype,percentage_amount = tdsvalue,pan_number = pan,
                            income_tax_number = incometax,aadhar_number = aadhar,universal_account_number = uan,pf_account_number = pf,
                            pr_account_number = pr,upload_file = file,salary_amount = salaryamount,salary_effective_from=salarydate,
                            city=city,street=street,state=state,country=country,pincode=pincode,temporary_city=tempCity,
                            temporary_street=tempStreet,temporary_state=tempState,temporary_pincode=tempPincode,temporary_country=tempCountry)
                
                new.save()

                history = Employee_History(company_id = companykey.id,login_id=sid,employee_id = new.id,date = date.today(),action = 'Created')
                history.save()

        sid = request.session['s_id']
        loginn = Fin_Login_Details.objects.get(id=sid)
        if loginn.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = sid)
            allmodules = Fin_Modules_List.objects.get(company_id = com.id)
            employee = Employee.objects.filter(company_id=com.id)
            
        elif loginn.User_Type == 'Staff' :
            com = Fin_Staff_Details.objects.get(Login_Id = sid)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id_id)
            employee = Employee.objects.filter(company_id=com.company_id_id)
        return render(request,'company/Employee_List.html',{'allmodules':allmodules,'employee':employee,'com':com,'data':loginn})

def employee_overview(request,pk):
    employ = Employee.objects.get(id = pk)
    comments = Employee_Comment.objects.filter(employee_id = pk,company_id=employ.company_id)
    history = Employee_History.objects.filter(employee_id=pk,company_id=employ.company_id).latest('date')
    if comments.exists():
        for index, comment in enumerate(comments):
            comment.index = index + 1
    else: 
        index = '0'

    sid = request.session['s_id']
    loginn = Fin_Login_Details.objects.get(id=sid)
    if loginn.User_Type == 'Company':
        com = Fin_Company_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = com.id)
        
    elif loginn.User_Type == 'Staff' :
        com = Fin_Staff_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = com.company_id_id)
    return render(request,'company/Employee_Overview.html',{'index':index,'comments':comments ,'employ':employ,'allmodules':allmodules,'history':history,'com':com,'data':loginn})

def employee_delete(request,pk):
    employ = Employee.objects.get(id = pk)
    employ.delete()
    sid = request.session['s_id']
    loginn = Fin_Login_Details.objects.get(id=sid)
    if loginn.User_Type == 'Company':
        com = Fin_Company_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = com.id)
        employee = Employee.objects.filter(company_id=com.id)
        
    elif loginn.User_Type == 'Staff' :
        com = Fin_Staff_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = com.company_id_id)
        employee = Employee.objects.filter(company_id=com.company_id_id)
    return render(request,'company/Employee_List.html',{'employee':employee,'allmodules':allmodules,'com':com,'data':loginn})

def employee_comment(request,pk):
    employ = Employee.objects.get(id = pk)
    todayDate = date.today()
    sid = request.session['s_id']
    log_in = Fin_Login_Details.objects.get(id=sid)
    loginID = log_in.id
    

    if request.method == 'POST':
        comments = request.POST['comment']  
        employeeComment = Employee_Comment(employee_id=pk,company_id=employ.company_id,login_id=loginID,comment=comments,date=todayDate)
        employeeComment.save()
        comments = Employee_Comment.objects.filter(employee_id = pk,company_id=employ.company_id)
        history = Employee_History.objects.filter(employee_id=pk,company_id=employ.company_id).latest('date')
        if comments.exists():
            for index, comment in enumerate(comments):
                comment.index = index + 1
        else: 
            index = '0'

    
    
    if log_in.User_Type == 'Company':
        com = Fin_Company_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = com.id)
        
    elif log_in.User_Type == 'Staff' :
        com = Fin_Staff_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = com.company_id_id)
    return render(request,'company/Employee_Overview.html',{'employ':employ,'allmodules':allmodules,'index':index,'comments':comments ,'history':history})


def employee_comment_view(request,pk):
    employ = Employee.objects.get(id = pk)
    comments = Employee_Comment.objects.filter(employee_id = pk,company_id=employ.company_id)
    sid = request.session['s_id']
    loginn = Fin_Login_Details.objects.get(id=sid)
    if loginn.User_Type == 'Company':
        com = Fin_Company_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = com.id)
        
    elif loginn.User_Type == 'Staff' :
        com = Fin_Staff_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = com.company_id_id)
    return render(request,'company/Employee_Comment.html',{'comments':comments,'employ':employ,'allmodules':allmodules,'com':com,'data':loginn})

def employee_history(request,pk):
    employ = Employee.objects.get(id = pk)
    history = Employee_History.objects.filter(employee_id = pk,company_id=employ.company_id)
    sid = request.session['s_id']
    loginn = Fin_Login_Details.objects.get(id=sid)
    if loginn.User_Type == 'Company':
        com = Fin_Company_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = com.id)
        
    elif loginn.User_Type == 'Staff' :
        com = Fin_Staff_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = com.company_id_id)
    return render(request,'company/Employee_History.html',{'history':history,'employ':employ,'allmodules':allmodules,'com':com,'data':loginn})

def activate(request,pk):
    employ = Employee.objects.get(id = pk)
    if employ.employee_status == 'Active':
        employ.employee_status = 'Inactive'
    else:
        employ.employee_status = 'Active'
    employ.save()

    sid = request.session['s_id']
    loginn = Fin_Login_Details.objects.get(id=sid)
    if loginn.User_Type == 'Company':
        com = Fin_Company_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = com.id)
        
    elif loginn.User_Type == 'Staff' :
        com = Fin_Staff_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = com.company_id_id)

    comments = Employee_Comment.objects.filter(employee_id = pk,company_id=employ.company_id)
    history = Employee_History.objects.filter(employee_id=pk,company_id=employ.company_id).latest('date')
    if comments.exists():
        for index, comment in enumerate(comments):
            comment.index = index + 1
    else: 
        index = '0'
    return render(request,'company/Employee_Overview.html',{'employ':employ,'allmodules':allmodules,'index':index,'comments':comments ,'history':history,'com':com,'data':loginn})

def employee_edit_page(request,pk):
    employe = Employee.objects.get(id=pk)
    sid = request.session['s_id']
    loginn = Fin_Login_Details.objects.get(id=sid)
    if loginn.User_Type == 'Company':
        com = Fin_Company_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = com.id)
        bloodgroup = Employee_Blood_Group.objects.filter(company_id=com.id,login_id=sid).values('blood_group').distinct()
        
    elif loginn.User_Type == 'Staff' :
        com = Fin_Staff_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = com.company_id_id)
        bloodgroup = Employee_Blood_Group.objects.filter(company_id=com.company_id_id,login_id=sid).values('blood_group').distinct()

    return render(request,'company/Employee_Edit_Page.html',{'employe':employe,'allmodules':allmodules,'bloodgroup':bloodgroup,'com':com,'data':loginn})


def employee_update(request,pk):
    employ = Employee.objects.get(id=pk)
    if request.method == 'POST':

        title = request.POST['Title']
        firstname = request.POST['First_Name']
        lastname = request.POST['Last_Name']
        alias = request.POST['Alias']
        joiningdate = request.POST['Joining_Date']
        salarydate = request.POST['Salary_Date']
        
        salary_type = request.POST['Salary_Type']

        if salary_type == 'Fixed':
            amountperhour = 0
            workinghour = 0
            salaryamount = request.POST['Salary_Amount']

        elif salary_type == 'Temporary' :
            amountperhour = 0
            workinghour = 0
            salaryamount = request.POST['Salary_Amount']

        elif salary_type == 'Time Based' :
            amountperhour = request.POST['perhour']
            workinghour = request.POST['workhour']
            salaryamount = request.POST['Salary_Amount']
            

        
        
        employeenumber = request.POST['Employee_Number']
        designation = request.POST['Designation']
        location = request.POST['Location']
        gender = request.POST['Gender']
        image = request.FILES.get('Image', '')
        if len(image) != 0:
            image = request.FILES['Image']
        else:
            image = employ.upload_image
        
        dob = request.POST['DOB']
        blood = request.POST['Blood']
        parent = request.POST['Parent']
        spouse = request.POST['Spouse']
        street = request.POST['street']
        city = request.POST['city']
        state = request.POST['state']
        pincode = request.POST['pincode']
        country = request.POST['country']
        tempStreet = request.POST['tempStreet']
        tempCity = request.POST['tempCity']
        tempState = request.POST['tempState']
        tempPincode = request.POST['tempPincode']
        tempCountry = request.POST['tempCountry']
        
        
        contact = request.POST['Contact_Number']
        emergencycontact = request.POST['Emergency_Contact']
        email = request.POST['Email']
        file = request.FILES.get('File', '')
        if len(file) != 0:
            file = request.FILES['File']
        else:
            file= employ.upload_file

        bankdetails = request.POST['Bank_Details']
        accoutnumber = request.POST['Account_Number']
        ifsc = request.POST['IFSC']
        bankname = request.POST['BankName']
        branchname = request.POST['BranchName']
        transactiontype = request.POST['Transaction_Type']

        

        if request.POST['tds_applicable'] == 'Yes':
            tdsapplicable = request.POST['tds_applicable']
            tdstype = request.POST['TDS_Type']
            
            if tdstype == 'Amount':
                tdsvalue = request.POST['TDS_Amount']
            elif tdstype == 'Percentage':
                tdsvalue = request.POST['TDS_Percentage']
            else:
                tdsvalue = 0
        elif request.POST['tds_applicable'] == 'No':
            tdsvalue = 0
            tdstype = ''
            tdsapplicable = request.POST['tds_applicable']
        else:
            tdsvalue = 0
            tdstype = ''
            tdsapplicable = ''

        
        
        incometax = request.POST['Income_Tax']
        aadhar = request.POST['Aadhar']
        uan = request.POST['UAN']
        pf = request.POST['PF']
        pan = request.POST['PAN']
        pr = request.POST['PR']

        if dob == '':
            age = 2
        else:
            dob2 = date.fromisoformat(dob)
            today = date.today()
            age = int(today.year - dob2.year - ((today.month, today.day) < (dob2.month, dob2.day)))
        
        sid = request.session['s_id']
        emply = Fin_Login_Details.objects.get(id=sid)
        employeee = Employee.objects.get(id=pk)

        

        if emply.User_Type == 'Company':
            companykey =  Fin_Company_Details.objects.get(Login_Id_id=sid)
        elif emply.User_Type == 'Staff':
            staffkey = Fin_Staff_Details.objects.get(Login_Id=sid)
            companykey = Fin_Company_Details.objects.get(id=staffkey.company_id_id)
        else:
            distributorkey = Fin_Distributors_Details.objects.get(login_Id=sid)
            companykey = Fin_Company_Details.objects.get(id=distributorkey.company_id_id)

        emp = Employee.objects.exclude(company_id = companykey.id,id=pk)
        
        if emp.filter(employee_mail=email,mobile = contact,employee_number=employeenumber,company_id = companykey.id).exists():
            messages.error(request,'user exist')
            return redirect(reverse('employee_edit_page', kwargs={'pk': pk}))

        
        elif emp.filter(mobile = contact,company_id = companykey.id).exists():
            messages.error(request,'phone number exist')
            url = reverse('employee_edit_page', kwargs={'pk': 10})
            print(url)
            return redirect(reverse('employee_edit_page', kwargs={'pk': pk}))
        
        elif emp.filter(employee_mail=email,company_id = companykey.id).exists():
            messages.error(request,'email exist')
            url = reverse('employee_edit_page', kwargs={'pk': 10})
            print(url)
            return redirect(reverse('employee_edit_page', kwargs={'pk': pk}))
        
        elif emp.filter(employee_number=employeenumber,company_id = companykey.id).exists():
            messages.error(request,'employee id exist')
            url = reverse('employee_edit_page', kwargs={'pk': 10})
            print(url)
            return redirect(reverse('employee_edit_page', kwargs={'pk': pk}))
        
        elif emp.filter(aadhar_number = aadhar,company_id = companykey.id).exists():
            messages.error(request,'Aadhar number exist')
            url = reverse('employee_edit_page', kwargs={'pk': 10})
            print(url)
            return redirect(reverse('employee_edit_page', kwargs={'pk': pk}))
        
        elif bankdetails.lower() == 'yes':
            if emp.filter(account_number=accoutnumber,company_id = companykey.id).exists():
                messages.error(request,'Bank account number already exist')
                url = reverse('employee_edit_page', kwargs={'pk': 10})
                print(url)
                return redirect(reverse('employee_edit_page', kwargs={'pk': pk}))
        
        else:
        
            employeee.upload_image=image
            employeee.title = title
            employeee.first_name = firstname
            employeee.last_name = lastname
            employeee.alias = alias
            employeee.employee_mail = email
            employeee.employee_number = employeenumber
            employeee.employee_designation = designation
            employeee.employee_current_location = location
            employeee.mobile = contact
            employeee.date_of_joining = joiningdate
            employeee.salary_amount = salaryamount 
            employeee.amount_per_hour = amountperhour 
            employeee.total_working_hours = workinghour
            employeee.gender = gender 
            employeee.date_of_birth = dob 
            employeee.age = age
            employeee.blood_group = blood
            employeee.fathers_name_mothers_name = parent
            employeee.spouse_name = spouse
            employeee.emergency_contact = emergencycontact
            employeee.provide_bank_details = bankdetails
            employeee.account_number = accoutnumber
            employeee.ifsc = ifsc
            employeee.name_of_bank = bankname
            employeee.branch_name = branchname
            employeee.bank_transaction_type = transactiontype
            employeee.tds_applicable = tdsapplicable
            employeee.tds_type = tdstype
            employeee.percentage_amount = tdsvalue
            employeee.pan_number = pan
            employeee.income_tax_number = incometax
            employeee.aadhar_number = aadhar
            employeee.universal_account_number = uan
            employeee.pf_account_number = pf
            employeee.pr_account_number = pr
            employeee.upload_file = file
            employeee.employee_salary_type=salary_type
            employeee.salary_effective_from=salarydate
            employeee.city=city
            employeee.street=street
            employeee.state=state
            employeee.country=country
            employeee.pincode=pincode
            employeee.temporary_city=tempCity
            employeee.temporary_street=tempStreet
            employeee.temporary_state=tempState
            employeee.temporary_pincode=tempPincode
            employeee.temporary_country=tempCountry
            employeee.save()

            history = Employee_History(company_id = employeee.company_id,employee_id = pk,login_id= emply.id,date = date.today(),action = 'Edited')
            history.save()
        
        return redirect('employee_overview',pk=employ.id)
    

def employee_profile_email(request,pk):
    
            try:
                if request.method == 'POST':
                    emails_string = request.POST['email_ids']
                    data = Employee.objects.get(id=pk)
                    cmp = Fin_Company_Details.objects.get(id=data.company_id)

                    # Split the string by commas and remove any leading or trailing whitespace
                    emails_list = [email.strip() for email in emails_string.split(',')]
                    email_message = "Here's the requested profile"
                    

                    context = {'cmp': cmp, 'employ': data, 'email_message': email_message}
                    print('context working')

                    template_path = 'company/Employee_Profile_PDF.html'
                    print('tpath working')

                    template = get_template(template_path)
                    print('template working')

                    html = template.render(context)
                    print('html working')

                    result = BytesIO()
                    print('bytes working')

                    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result,path='company/Employee_Profile_PDF.html',base_url=request.build_absolute_uri('/'))
                    print('pisa working')

                    if pdf.err:
                        raise Exception(f"PDF generation error: {pdf.err}")

                    pdf = result.getvalue()
                    print('')
                    filename = f"{data.first_name}_{data.last_name}'s_Profile.pdf"
                    subject = f"{data.first_name}_{data.last_name}'s_Profile"
                    email = EmailMessage(subject, f"Hi, \n{email_message} -of -{cmp.Company_name}. ", from_email=settings.EMAIL_HOST_USER, to=emails_list)
                    email.attach(filename, pdf, "application/pdf")
                    email.send(fail_silently=False)

                    messages.success(request, 'Report has been shared via email successfully..!')
                    return redirect('employee_list')
            except Exception as e:
                messages.error(request, f'Error while sending report: {e}')
                return redirect('employee_list')


def Employee_Profile_PDF(request,pk):
    employ = Employee.objects.get(id=pk)
    return render(request,'company/Employee_Profile_PDF.html',{'employ':employ})
        
def employee_blood_group(request):
    if request.method == 'POST':
        bloodGroup = request.POST.get('bloodGroup', '').upper()
        sid = request.session.get('s_id')
        loginn = Fin_Login_Details.objects.get(id=sid)
        invalid_group = ['A+', 'A-', 'B+', 'O+']

        if loginn.User_Type == 'Company' and bloodGroup not in invalid_group:
            com = Fin_Company_Details.objects.get(Login_Id=sid)
            
            allmodules = Fin_Modules_List.objects.get(company_id=com.id)
            group = Employee_Blood_Group(blood_group=bloodGroup, company_id=com.id, login_id=sid)
            group.save()
            bloodgroup = Employee_Blood_Group.objects.filter(company_id=com.id,login_id=sid).values('blood_group').distinct()
            return JsonResponse({'success': True,'bloodgroup': list(bloodgroup)})

        elif loginn.User_Type == 'Staff' and bloodGroup not in invalid_group:
            com = Fin_Staff_Details.objects.get(Login_Id = sid)
            allmodules = Fin_Modules_List.objects.get(company_id=com.company_id_id)
            group = Employee_Blood_Group(blood_group=bloodGroup, company_id=com.company_id_id, login_id=sid)
            group.save()
            bloodgroup = Employee_Blood_Group.objects.filter(company_id=com.company_id_id,login_id=sid).values('blood_group').distinct()
            return JsonResponse({'success': True,'bloodgroup': list(bloodgroup)})

    return JsonResponse({'success': False, 'error': 'Invalid blood group or user type'})
    
def bloodgroup_data(request):
    sid = request.session.get('s_id')
    loginn = Fin_Login_Details.objects.get(id=sid)
    
    if loginn.User_Type == 'Company' :
            com = Fin_Company_Details.objects.get(Login_Id=sid)
            
            bloodgroup = Employee_Blood_Group.objects.filter(company_id=com.id,login_id=sid).values('blood_group').distinct()
            return JsonResponse({'success': True,'bloodgroup': list(bloodgroup)})

    elif loginn.User_Type == 'Staff' :
            com = Fin_Staff_Details.objects.get(Login_Id = sid)
            bloodgroup = Employee_Blood_Group.objects.filter(company_id=com.company_id_id,login_id=sid).values('blood_group').distinct()
            return JsonResponse({'success': True,'bloodgroup': list(bloodgroup)})

    else:
        return JsonResponse({'success': False,'bloodgroup': list(bloodgroup)})
# holiday section--------------------------------------------------------------------------------------------------------------------------
    
def holiday_list(request):
    sid = request.session['s_id']
    loginn = Fin_Login_Details.objects.get(id=sid)
    if loginn.User_Type == 'Company':
        com = Fin_Company_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = com.id)
        # holiday = Holiday.objects.filter(company_id=com.id).annotate(month=ExtractMonth('start_date'),year=ExtractYear('start_date')).values('month','year').annotate(total_holiday=Sum('holiday_days')).order_by('year','month')
        holiday = Holiday.objects.filter(company_id=com.id).annotate(month=ExtractMonth('start_date'), year=ExtractYear('start_date')).values('month', 'year').annotate(total_holiday=Cast(Sum(F('holiday_days')),IntegerField())).order_by('year', 'month')
        
        
    else:
        com = Fin_Staff_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = com.company_id_id)
        holiday = Holiday.objects.filter(company_id=com.company_id_id).annotate(month=ExtractMonth('start_date'), year=ExtractYear('start_date')).values('month', 'year').annotate(total_holiday=Cast(Sum(F('holiday_days')),IntegerField())).order_by('year', 'month')
    
    
    return render(request,'company/Holiday_List.html',{'holiday':holiday,'allmodules':allmodules,'com':com,'data':loginn})
 
def holiday_create_page(request):
    sid = request.session['s_id']
    loginn = Fin_Login_Details.objects.get(id=sid)
    if loginn.User_Type == 'Company':
        com = Fin_Company_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = com.id)
        
    elif loginn.User_Type == 'Staff' :
        com = Fin_Staff_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = com.company_id_id)
    return render(request,'company/Holiday_Create_Page.html',{'allmodules':allmodules,'com':com,'data':loginn})

def holiday_add(request):
    if request.method == 'POST':
        startdate = request.POST['date1']
        enddate = request.POST['date2']
        title = request.POST['title']

        start_date1 = datetime.strptime(startdate, '%Y-%m-%d').date()
        end_date1 = datetime.strptime(enddate, '%Y-%m-%d').date()
        day_s = end_date1 - start_date1 + timedelta(days=1)
        
    sid = request.session['s_id']
    loginn = Fin_Login_Details.objects.get(id=sid)
    if loginn.User_Type == 'Company':
        com = Fin_Company_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = com.id)
        holiday_check = Holiday.objects.filter(start_date=startdate,end_date=enddate,company_id=com.id)
            
    elif loginn.User_Type == 'Staff' :
        com = Fin_Staff_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = com.company_id_id)
        holiday_check = Holiday.objects.filter(start_date=startdate,end_date=enddate,company_id=com.company_id_id)
        
    if holiday_check.exists():
        messages.error(request,' Dates are already listed as holiday')
        return render(request,'company/Holiday_Create_Page.html',{'allmodules':allmodules,'com':com,'data':loginn})

    # uncomment if you want to check whether the holidays would overlap
    # elif Holiday.objects.filter(Q(start_date__lte=startdate) & Q(end_date__gte=startdate)).exists() or Holiday.objects.filter(Q(start_date__lte=enddate) & Q(end_date__gte=enddate)).exists():
    #     messages.error(request,'Some dates are already listed as holiday')
    #     sid = request.session['s_id']
    #     loginn = Fin_Login_Details.objects.get(id=sid)
    #     if loginn.User_Type == 'Company':
    #         com = Fin_Company_Details.objects.get(Login_Id = sid)# 
    #         allmodules = Fin_Modules_List.objects.get(company_id = com.id)
            
    #     elif loginn.User_Type == 'Staff' :
    #         com = Fin_Staff_Details.objects.get(Login_Id = sid)# 
    #         allmodules = Fin_Modules_List.objects.get(company_id = com.company_id_id)
    #     return render(request,'company/Holiday_Create_Page.html',{'allmodules':allmodules})
    
    else:
        sid = request.session['s_id']
        loginn = Fin_Login_Details.objects.get(id=sid)
        if loginn.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = sid)
            allmodules = Fin_Modules_List.objects.get(company_id = com.id)
            holiday = Holiday(start_date=startdate,end_date=enddate,login_id=sid,holiday_name=title,company_id=com.id,holiday_days=day_s)
            holiday.save()
            history = Holiday_History(company_id = com.id,login_id=sid,holiday_id = holiday.id,date = date.today(),action = 'Created',start_date = startdate,end_date = enddate,holiday_name=title)
            history.save()
            holidayss = Holiday.objects.filter(company_id=com.id).annotate(month=ExtractMonth('start_date'), year=ExtractYear('start_date')).values('month', 'year').annotate(total_holiday=Cast(Sum(F('holiday_days')),IntegerField())).order_by('year', 'month')

        else:
            com = Fin_Staff_Details.objects.get(Login_Id = sid)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id_id)
            holiday = Holiday(start_date=startdate,end_date=enddate,holiday_name=title,login_id=sid,company_id=com.company_id_id,holiday_days=day_s)
            holiday.save()
            history = Holiday_History(company_id = com.id,login_id=sid,holiday_id = holiday.id,date = date.today(),action = 'Created',start_date = startdate,end_date = enddate,holiday_name=title)
            history.save()
            holidayss = Holiday.objects.filter(company_id=com.company_id_id).annotate(month=ExtractMonth('start_date'), year=ExtractYear('start_date')).values('month', 'year').annotate(total_holiday=Cast(Sum(F('holiday_days')),IntegerField())).order_by('year', 'month')
            
        return render(request,'company/Holiday_List.html',{'allmodules':allmodules,'holiday':holidayss,'com':com,'data':loginn})
        
    
def holiday_calendar_view(request,mn,yr):
    month = int(mn)-1
    year = int(yr)
    
    sid = request.session['s_id']
    loginn = Fin_Login_Details.objects.get(id=sid)
    if loginn.User_Type == 'Company':
        com = Fin_Company_Details.objects.get(Login_Id = sid)
        events = Holiday.objects.filter(start_date__month=mn,start_date__year=year,company_id=com.id)
        allmodules = Fin_Modules_List.objects.get(company_id = com.id)
        comments = Holiday_Comment.objects.filter(month=mn,year=year,company_id=com.id)
        for index, comment in enumerate(comments):
            comment.index = index + 1
        
    elif loginn.User_Type == 'Staff' :
        com = Fin_Staff_Details.objects.get(Login_Id = sid)
        events = Holiday.objects.filter(start_date__month=mn,start_date__year=year,company_id=com.company_id_id)
        allmodules = Fin_Modules_List.objects.get(company_id = com.company_id_id)
        comments = Holiday_Comment.objects.filter(month=mn,year=year,company_id=com.company_id_id)
        for index, comment in enumerate(comments):
            comment.index = index + 1

    return render(request, 'company/Holiday_Calendar.html', {'comments':comments,'events': events,'allmodules':allmodules,'year':year,'month':month,'com':com,'data':loginn})

def holiday_delete(request, pk):
    sid = request.session['s_id']
    loginn = Fin_Login_Details.objects.get(id=sid)
    if loginn.User_Type == 'Company':
        com = Fin_Company_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = com.id)
        
    elif loginn.User_Type == 'Staff' :
        com = Fin_Staff_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = com.company_id_id)

    if request.method == 'POST':
        ogMonth = int(request.POST['month'])
        year = int(request.POST['year'])
        month = ogMonth + 1
        holiday = Holiday.objects.get(id=pk)
        holiday.delete()
        events = Holiday.objects.filter(start_date__month=month,start_date__year=year)
        if events.exists():
            return render(request, 'company/Holiday_Calendar.html', {'events': events,'allmodules':allmodules,'year':year,'month':ogMonth,'com':com,'data':loginn})
        else:
            return redirect('holiday_list')


def holiday_edit_page(request,pk,mn,yr):
    holiday = Holiday.objects.get(id=pk)
    sid = request.session['s_id']
    loginn = Fin_Login_Details.objects.get(id=sid)
    if loginn.User_Type == 'Company':
        com = Fin_Company_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = com.id)
        
    elif loginn.User_Type == 'Staff' :
        com = Fin_Staff_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = com.company_id_id)
    return render(request,'company/Holiday_Edit_Page.html',{'holiday':holiday,'allmodules':allmodules,'com':com,'data':loginn,'year':yr,'month':mn})


def holiday_update(request,pk,mn,yr):
    mon = mn+1
    holiday = Holiday.objects.get(id=pk)
    if request.method == 'POST':
        startdate = request.POST['date1']
        enddate = request.POST['date2']
        title = request.POST['title']

        start_date1 = datetime.strptime(startdate, '%Y-%m-%d').date()
        end_date1 = datetime.strptime(enddate, '%Y-%m-%d').date()
        day_s = end_date1 - start_date1 + timedelta(days=1)

    sid = request.session['s_id']
    loginn = Fin_Login_Details.objects.get(id=sid)
    if loginn.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = sid)
            companyID = com.id
            allmodules = Fin_Modules_List.objects.get(company_id = com.id)
            
    elif loginn.User_Type == 'Staff' :
            com = Fin_Staff_Details.objects.get(Login_Id = sid)
            companyID = com.company_id_id
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id_id)
        
    holi = Holiday.objects.filter(start_date=startdate,end_date=enddate,company_id=companyID)
    if holi.exclude(id=pk).exists():
            error = 'yes'
            messages.error(request,'Some dates are already listed as holiday')
            sid = request.session['s_id']
            loginn = Fin_Login_Details.objects.get(id=sid)
            if loginn.User_Type == 'Company':
                com = Fin_Company_Details.objects.get(Login_Id = sid)
                allmodules = Fin_Modules_List.objects.get(company_id = com.id)
                
            elif loginn.User_Type == 'Staff' :
                com = Fin_Staff_Details.objects.get(Login_Id = sid)
                allmodules = Fin_Modules_List.objects.get(company_id = com.company_id_id)
            return render(request,'company/Holiday_Edit_Page.html',{'holiday':holiday,'allmodules':allmodules,'com':com,'data':loginn})
        
    else:
            sid = request.session['s_id']
            loginn = Fin_Login_Details.objects.get(id=sid)
            if loginn.User_Type == 'Company':
                com = Fin_Company_Details.objects.get(Login_Id = sid)
                allmodules = Fin_Modules_List.objects.get(company_id = com.id)
                
                holiday.start_date = startdate
                holiday.end_date = enddate
                holiday.holiday_name=title
                holiday.login_id=sid
                holiday.company_id=com.id
                holiday.holiday_days=day_s
                holiday.save()
                history = Holiday_History(company_id = com.id,login_id=sid,holiday_id = holiday.id,date = date.today(),action = 'Edited',start_date = startdate,end_date = enddate,holiday_name=title)
                history.save()  
                
                holida_y = Holiday.objects.filter(company_id=com.id).annotate(month=ExtractMonth('start_date'), year=ExtractYear('start_date')).values('month', 'year').annotate(total_holiday=Cast(Sum(F('holiday_days')),IntegerField())).order_by('year', 'month')

            else:
                com = Fin_Staff_Details.objects.get(Login_Id = sid)
                allmodules = Fin_Modules_List.objects.get(company_id = com.company_id_id)
                
                holiday.start_date = startdate
                holiday.end_date = enddate
                holiday.holiday_name=title
                holiday.login_id=sid
                holiday.company_id=com.company_id_id
                holiday.holiday_days=day_s
                holiday.save()
                history = Holiday_History(company_id = com.company_id_id,login_id=sid,holiday_id = holiday.id,date = date.today(),action = 'Edited',start_date = startdate,end_date = enddate,holiday_name=title)
                history.save()  

                holida_y = Holiday.objects.filter(company_id=com.company_id_id).annotate(month=ExtractMonth('start_date'), year=ExtractYear('start_date')).values('month', 'year').annotate(total_holiday=Cast(Sum(F('holiday_days')),IntegerField())).order_by('year', 'month')

    return redirect('holiday_calendar_view', mn=mon, yr=yr)
    # return render(request,'company/Holiday_List.html',{'holiday':holida_y,'allmodules':allmodules,'com':com,'data':loginn})


def holiday_comment(request,mn,yr):
    Month = mn+1
    
    todayDate = date.today()
    sid = request.session['s_id']
    log_in = Fin_Login_Details.objects.get(id=sid)
    loginID = log_in.id
    
    if log_in.User_Type == 'Company':
        com = Fin_Company_Details.objects.get(Login_Id = sid)
        
        if request.method == 'POST':
            comments = request.POST['comment']  
            holidayComment = Holiday_Comment(month = Month, year = yr,company_id=com.id,login_id=loginID,comment=comments,date=todayDate)
            holidayComment.save()
            
    elif log_in.User_Type == 'Staff' :
        com = Fin_Staff_Details.objects.get(Login_Id = sid)
        
        if request.method == 'POST':
            comments = request.POST['comment']  
            holidayComment = Holiday_Comment(month = Month, year = yr,company_id=com.company_id_id,login_id=loginID,comment=comments,date=todayDate)
            holidayComment.save()
    
    redirect_url = reverse('holiday_calendar_view', args=[Month, yr])
    return redirect(redirect_url)
    
def holiday_comment_delete(request, pk,mn,yr):
    holiday = Holiday_Comment.objects.get(id=pk)
    holiday.delete()
    redirect_url = reverse('holiday_calendar_view', args=[mn, yr])
    return redirect(redirect_url)

def holiday_history(request,month,year):
        mn = month + 1
        
        startdate = datetime(year, mn, 1)
        if mn == 12:
            enddate = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            enddate = datetime(year, mn + 1, 1) - timedelta(days=1)

        print(startdate,enddate,'----------------------------------------------------')
        sid = request.session['s_id']
        loginn = Fin_Login_Details.objects.get(id=sid)
        if loginn.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = sid)
            allmodules = Fin_Modules_List.objects.get(company_id = com.id)
            history = Holiday_History.objects.filter(company_id=com.id,start_date__gt = startdate,end_date__lt = enddate)
            
        elif loginn.User_Type == 'Staff' :
            com = Fin_Staff_Details.objects.get(Login_Id = sid)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id_id)
            history = Holiday_History.objects.filter(company_id=com.company_id_id,start_date__gt = startdate,end_date__lt = enddate)
        
        
        return render(request,'company/Holiday_History.html',{'history':history,'allmodules':allmodules,'com':com,'data':loginn,'month':mn,'year':year})
        
def employee_comment_delete(request,pk,id):
    employee_comment = Employee_Comment.objects.get(id=pk)
    employee_comment.delete()
    redirect_url = reverse('employee_overview', args=[id])
    return redirect(redirect_url)
# harikrishnan end ---------------

# ---------------------------Start Banking------------------------------------ 

def Fin_banking_listout(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id

        allmodules = Fin_Modules_List.objects.get(company_id = company,status = 'New')

        all_bankings = Fin_Banking.objects.filter(company = company)
        print(all_bankings)

        context = {
            'login_det':login_det,
            'com':com,
            'allmodules':allmodules,
            'all_bankings':all_bankings
        }
        return render(request,'company/banking/Fin_banking_listout.html',context)
    else:
       return redirect('/')  

def Fin_banking_sort_by_name(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id

        allmodules = Fin_Modules_List.objects.get(company_id = company,status = 'New')

        all_bankings = Fin_Banking.objects.filter(company = company).order_by('bank_name')
        print(all_bankings)

        context = {
            'login_det':login_det,
            'com':com,
            'allmodules':allmodules,
            'all_bankings':all_bankings
        }
        return render(request,'company/banking/Fin_banking_listout.html',context)
    else:
       return redirect('/')  
    
def Fin_banking_sort_by_balance(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id

        allmodules = Fin_Modules_List.objects.get(company_id = company,status = 'New')

        all_bankings = Fin_Banking.objects.filter(company = company).order_by('bank_name')
        print(all_bankings)

        context = {
            'login_det':login_det,
            'com':com,
            'allmodules':allmodules,
            'all_bankings':all_bankings
        }
        return render(request,'company/banking/Fin_banking_listout.html',context)
    else:
       return redirect('/')

def Fin_banking_filter_active(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id

        allmodules = Fin_Modules_List.objects.get(company_id = company,status = 'New')

        all_bankings = Fin_Banking.objects.filter(company = company,bank_status = 'Active')
        print(all_bankings)

        context = {
            'login_det':login_det,
            'com':com,
            'allmodules':allmodules,
            'all_bankings':all_bankings
        }
        return render(request,'company/banking/Fin_banking_listout.html',context)
    else:
       return redirect('/') 

def Fin_banking_filter_inactive(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id

        allmodules = Fin_Modules_List.objects.get(company_id = company,status = 'New')

        all_bankings = Fin_Banking.objects.filter(company = company,bank_status = 'Inactive')
        print(all_bankings)

        context = {
            'login_det':login_det,
            'com':com,
            'allmodules':allmodules,
            'all_bankings':all_bankings
        }
        return render(request,'company/banking/Fin_banking_listout.html',context)
    else:
       return redirect('/') 

def Fin_create_bank(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id

        allmodules = Fin_Modules_List.objects.get(company_id = company,status = 'New')


        context = {
                'login_det':login_det,
                'com':com,
                'allmodules':allmodules
            }
        return render(request,'company/banking/Fin_create_bank.html',context)
    else:
       return redirect('/')  

def Fin_banking_check_account_number(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id


        if request.method == 'GET':
            bank_name = request.GET.get('bank_name', '')
            account_number = request.GET.get('account_number', '')

            print(account_number)
            # Check if the account number exists for the given bank
            exists = Fin_Banking.objects.filter( account_number=account_number,company = company ).exists()

            # Return a JSON response indicating whether the account number exists
            return JsonResponse({'exists': exists})

    # Handle other HTTP methods if necessary
    return JsonResponse({'exists': False})  # Default to 'False' if the request is not a GET

def Fin_create_bank_account(request):
     if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id

        allmodules = Fin_Modules_List.objects.get(company_id = company,status = 'New')


        if request.method == 'POST':
            bname = request.POST.get('bname')
            ifsc = request.POST.get('ifsc')
            branch = request.POST.get('branch')
            opening_balance = request.POST.get('Opening')
            date = request.POST.get('date')
            opening_blnc_type = request.POST.get('op_type')
            acc_num = request.POST.get('acc_num')
            
            if opening_blnc_type == 'CREDIT':
                opening_balance = 0 -int(opening_balance)
            
            bank = Fin_Banking(
                login_details = login_det,
                company = company,
                bank_name=bname, 
                ifsc_code=ifsc,
                branch_name=branch, 
                opening_balance=opening_balance, 
                opening_balance_type = opening_blnc_type,
                date=date,
                current_balance=opening_balance,
                account_number=acc_num,
                bank_status = 'Active')
            bank.save()

            banking_history = Fin_BankingHistory(
                login_details = login_det,
                company = company,
                banking = bank,
                action = 'Created'
            )
            banking_history.save()
            
            transaction=Fin_BankTransactions(
                login_details = login_det,
                company = company,
                banking = bank,
                amount = opening_balance,
                adjustment_date = date,
                transaction_type = "Opening Balance",
                from_type = '',
                to_type = '',
                current_balance = opening_balance
                
            )
            transaction.save()

            transaction_history = Fin_BankTransactionHistory(
                login_details = login_det,
                company = company,
                bank_transaction = transaction,
                action = 'Created'
            )
            transaction_history.save()

            
            return redirect('Fin_banking_listout')

def Fin_view_bank(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id

        allmodules = Fin_Modules_List.objects.get(company_id = company,status = 'New')
        
        bank = Fin_Banking.objects.get(id=id)
        bank_list = Fin_Banking.objects.filter(company=company)
        trans = Fin_BankTransactions.objects.filter(banking_id=id) 
        comments = Fin_BankingComments.objects.filter(banking_id=id) 
        last_history = Fin_BankingHistory.objects.filter(banking_id=id).last()
        
        context = {
                'login_det':login_det,
                'com':com,
                'allmodules':allmodules,
                "bank":bank,
                'bl':bank_list,
                'trans':trans,
                'comments':comments,
                'last_history':last_history,
            }   

        return render(request,'company/banking/Fin_view_bank.html',context)

def Fin_bank_to_cash(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id

        allmodules = Fin_Modules_List.objects.get(company_id = company,status = 'New')

        bank=Fin_Banking.objects.get(id = id)
        all_banks = Fin_Banking.objects.filter(company = company)

        context = {
                'login_det':login_det,
                'com':com,
                'allmodules':allmodules,
                'bank':bank,
                'all_banks':all_banks,
               
            }  
       
        return render(request,'company/banking/Fin_bank_to_cash.html',context)
    
def Fin_save_bankTocash(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id

        if request.method == 'POST':
            f_bank = request.POST.get('bank')
            amount = int(request.POST.get('amount'))
            adj_date = request.POST.get('adjdate')
            desc = request.POST.get('desc')

            

            bank = Fin_Banking.objects.get(id=f_bank)
            bank.current_balance -= amount
            bank.save()
            
            transaction = Fin_BankTransactions(
                login_details = login_det,
                company = company,
                banking = bank,
                from_type = '',
                to_type='',
                amount=amount,
                description=desc,
                adjustment_date=adj_date,
                transaction_type='Cash Withdraw',
                current_balance= bank.current_balance               
            )
            transaction.save()
            transaction_history = Fin_BankTransactionHistory(
                login_details = login_det,
                company = company,
                bank_transaction = transaction,
                action = 'Created'
            )
            transaction_history.save()
            
        return redirect('Fin_view_bank',bank.id)
    
def Fin_cash_to_bank(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id

        allmodules = Fin_Modules_List.objects.get(company_id = company,status = 'New')

        bank=Fin_Banking.objects.get(id = id)
        all_banks = Fin_Banking.objects.filter(company = company)

        context = {
                'login_det':login_det,
                'com':com,
                'allmodules':allmodules,
                'bank':bank,
                'all_banks':all_banks,
               
            }  
       
        return render(request,'company/banking/Fin_cash_to_bank.html',context)
    
def Fin_save_cashTobank(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id

        if request.method == 'POST':
            t_bank = request.POST.get('bank')
            amount = int(request.POST.get('amount'))
            adj_date = request.POST.get('adjdate')
            desc = request.POST.get('desc')

            

            bank = Fin_Banking.objects.get(id=t_bank)
            bank.current_balance += amount
            bank.save()
            
            transaction = Fin_BankTransactions(
                login_details = login_det,
                company = company,
                banking = bank,
                from_type = '',
                to_type='',
                amount=amount,
                description=desc,
                adjustment_date=adj_date,
                transaction_type='Cash Deposit', 
                current_balance= bank.current_balance                 
            )
            transaction.save()
            transaction_history = Fin_BankTransactionHistory(
                login_details = login_det,
                company = company,
                bank_transaction = transaction,
                action = 'Created'
            )
            transaction_history.save()
            
        return redirect('Fin_view_bank',bank.id)   
    
def Fin_bank_to_bank(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id

        allmodules = Fin_Modules_List.objects.get(company_id = company,status = 'New')

        bank=Fin_Banking.objects.get(id = id)
        all_banks = Fin_Banking.objects.filter(company = company)

        context = {
                'login_det':login_det,
                'com':com,
                'allmodules':allmodules,
                'bank':bank,
                'all_banks':all_banks,
               
            }  
       
        return render(request,'company/banking/Fin_bank_to_bank.html',context)
    
def Fin_save_bankTobank(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id

        current_bank = Fin_Banking.objects.get(id=id)

        if request.method == 'POST':
            print('hi')
            f_bank = request.POST.get('fbank')
            print(f_bank)
            t_bank = request.POST.get('tbank')
            amount = int(request.POST.get('amount'))
            adj_date = request.POST.get('adjdate')
            desc = request.POST.get('desc')


            from_bank = Fin_Banking.objects.get(id=f_bank)
            print(from_bank)
            to_bank = Fin_Banking.objects.get(id=t_bank)
            to_bank.current_balance += amount
            from_bank.current_balance -= amount
            to_bank.save()
            from_bank.save()
            

            transaction_withdraw = Fin_BankTransactions(
                login_details = login_det,
                company = company,
                banking = from_bank,
                from_type = 'From :' + from_bank.bank_name,
                to_type='To :' + to_bank.bank_name,
                amount=amount,
                description=desc,
                adjustment_date=adj_date,
                transaction_type='From Bank Transfer', 
                current_balance= from_bank.current_balance
                               
            )
            transaction_withdraw.save()
            transaction_history = Fin_BankTransactionHistory(
                login_details = login_det,
                company = company,
                bank_transaction = transaction_withdraw,
                action = 'Created'
            )
            transaction_history.save()

            transaction_deposit = Fin_BankTransactions(
                login_details = login_det,
                company = company,
                banking = to_bank,
                from_type = 'From :' + from_bank.bank_name,
                to_type='To :' + to_bank.bank_name,
                amount=amount,
                description=desc,
                adjustment_date=adj_date,
                transaction_type='To Bank Transfer', 
                current_balance= to_bank.current_balance               
            )
            transaction_deposit.save()
            transaction_history = Fin_BankTransactionHistory(
                login_details = login_det,
                company = company,
                bank_transaction = transaction_deposit,
                action = 'Created'
            )
            transaction_history.save()

            
        return redirect('Fin_view_bank',current_bank.id)   
    
def Fin_bank_adjust(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id

        allmodules = Fin_Modules_List.objects.get(company_id = company,status = 'New')

        bank=Fin_Banking.objects.get(id = id)
        all_banks = Fin_Banking.objects.filter(company = company)

        context = {
                'login_det':login_det,
                'com':com,
                'allmodules':allmodules,
                'bank':bank,
                'all_banks':all_banks,
               
            }  
       
        return render(request,'company/banking/Fin_bank_adjust.html',context)

def Fin_save_bank_adjust(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id

        if request.method == 'POST':
            t_bank = request.POST.get('bank')
            amount = int(request.POST.get('amount'))
            adj_date = request.POST.get('adjdate')
            adj_type = request.POST.get('typ')
            desc = request.POST.get('desc')

            bank = Fin_Banking.objects.get(id=t_bank)

            if adj_type == 'Increase Balance':
                bank.current_balance += amount
                bank.save()
               
            else:
                bank.current_balance -= amount
                bank.save()
                
            
            transaction = Fin_BankTransactions(
                login_details = login_det,
                company = company,
                banking = bank,
                from_type = '',
                to_type='',
                amount=amount,
                description=desc,
                adjustment_date=adj_date,
                transaction_type='Adjust bank Balance', 
                current_balance= bank.current_balance,     
                      
            )
            transaction.save()


            if adj_type == 'Increase Balance':
              
                transaction.adjustment_type = 'Increase Balance'
                transaction.save()
            else:
               
                transaction.adjustment_type = 'Reduce Balance'
                transaction.save()

            
            transaction_history = Fin_BankTransactionHistory(
                login_details = login_det,
                company = company,
                bank_transaction = transaction,
                action = 'Created'
            )
            transaction_history.save()
            
        return redirect('Fin_view_bank',bank.id) 

def Fin_edit_bank(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id

        allmodules = Fin_Modules_List.objects.get(company_id = company,status = 'New')

        bank = Fin_Banking.objects.get(id=id)

        context = {
                'login_det':login_det,
                'com':com,
                'allmodules':allmodules,
                'bank':bank
            }
        return render(request,'company/banking/Fin_edit_bank.html',context)
    else:
       return redirect('/')   

def Fin_edit_bank_account(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id

        allmodules = Fin_Modules_List.objects.get(company_id = company,status = 'New')

        bank = Fin_Banking.objects.get(id = id)
        old_op_blnc = int(bank.opening_balance)
        transactions = Fin_BankTransactions.objects.filter(banking=bank)
        transactions_count = Fin_BankTransactions.objects.filter(banking=bank).count()

        
        if request.method == 'POST':
            bname = request.POST.get('bname')
            ifsc = request.POST.get('ifsc')
            branch = request.POST.get('branch')
            opening_balance = request.POST.get('Opening')
            date = request.POST.get('date')
            opening_blnc_type = request.POST.get('op_type')
            acc_num = request.POST.get('acc_num')
            
            if opening_blnc_type == 'CREDIT':
                opening_balance = 0 -int(opening_balance)

            if old_op_blnc == int(opening_balance):
                print('same')
                bank.login_details = login_det
                bank.company = company
                bank.bank_name=bname
                bank.ifsc_code=ifsc
                bank.branch_name=branch
                bank.opening_balance=opening_balance 
                bank.opening_balance_type = opening_blnc_type
                bank.date=date
                bank.current_balance=opening_balance
                bank.account_number=acc_num
                bank.save()

                banking_history = Fin_BankingHistory(
                    login_details = login_det,
                    company = company,
                    banking = bank,
                    action = 'Updated'
                )
                banking_history.save()

            elif old_op_blnc < int(opening_balance): 

                print('increase')
                increased_amount =  int(opening_balance) - old_op_blnc 
                print('increased_amount')
                bank.login_details = login_det
                bank.company = company
                bank.bank_name=bname
                bank.ifsc_code=ifsc
                bank.branch_name=branch
                bank.opening_balance=opening_balance 
                bank.opening_balance_type = opening_blnc_type
                bank.date=date
                bank.current_balance += int(increased_amount)
                bank.account_number=acc_num
                bank.save()

                banking_history = Fin_BankingHistory(
                    login_details = login_det,
                    company = company,
                    banking = bank,
                    action = 'Updated'
                )
                banking_history.save() 

                for t in transactions:
                    print('for')
                    print(t)
                    t.login_details_id = login_det.id
                    t.company_id = company.id
                    t.banking_id = bank.id
                    if t.transaction_type == "Opening Balance":
                        t.amount = t.amount + int(increased_amount)
                    t.current_balance = t.current_balance + int(increased_amount)
                    t.save()

                transaction_history = Fin_BankTransactionHistory(
                    login_details = login_det,
                    company = company,
                    bank_transaction = t,
                    action = 'Updated'
                )
                transaction_history.save() 

            elif old_op_blnc > int(opening_balance): 

                print('decrease')  
                decreased_amount =  old_op_blnc - int(opening_balance)
                print('decreased_amount')
                bank.login_details = login_det
                bank.company = company
                bank.bank_name=bname
                bank.ifsc_code=ifsc
                bank.branch_name=branch
                bank.opening_balance=opening_balance 
                bank.opening_balance_type = opening_blnc_type
                bank.date=date
                bank.current_balance = bank.current_balance - int(decreased_amount)
                bank.account_number=acc_num
                bank.save()

                banking_history = Fin_BankingHistory(
                    login_details = login_det,
                    company = company,
                    banking = bank,
                    action = 'Updated'
                )
                banking_history.save() 

                for t in transactions:
                    print(t)
                    t.login_details_id = login_det.id
                    t.company_id = company.id
                    t.banking_id = bank.id
                    if t.transaction_type == "Opening Balance":
                        t.amount = t.amount - int(decreased_amount)
                    t.current_balance = t.current_balance - int(decreased_amount)
                    t.save()

                transaction_history = Fin_BankTransactionHistory(
                    login_details = login_det,
                    company = company,
                    bank_transaction = t,
                    action = 'Updated'
                )
                transaction_history.save()       
                        
    return redirect('Fin_view_bank',bank.id)



def Fin_change_bank_status(request,id):
   
    bank = Fin_Banking.objects.get(id =id)
    
    if bank.bank_status == "Active":
        bank.bank_status = "Inactive"
    else:
        bank.bank_status = "Active"
    bank.save()

    return redirect('Fin_view_bank',id=id)

def Fin_delete_bank(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id

        allmodules = Fin_Modules_List.objects.get(company_id = company,status = 'New')

        all_bankings = Fin_Banking.objects.filter(company = company)
   
        bank = Fin_Banking.objects.get(id =id)
        
        transactions_count = Fin_BankTransactions.objects.filter(banking = bank).count()
        print(transactions_count) 

        if transactions_count == 0:
            try:
                bank_history = Fin_BankingHistory.objects.filter(banking = bank)
                bank_history.delete()
                bank.delete()
            except:
                bank.delete()
            
            messages.success(request, 'Bank has been deleted successfully.')

            return redirect('Fin_banking_listout')

        elif transactions_count == 1:
            transaction = Fin_BankTransactions.objects.get(banking = bank)
            transaction_history = Fin_BankTransactionHistory.objects.filter(bank_transaction = transaction)
            bank_history = Fin_BankingHistory.objects.filter(banking = bank)
            transaction_history.delete()
            transaction.delete()
            bank_history.delete()
            bank.delete()

            messages.success(request, 'Bank has been deleted successfully.')

            return redirect('Fin_banking_listout')

        elif transactions_count > 1:
            bank.bank_status = "Inactive"
            bank.save()

            messages.success(request, 'Bank already have some transactions so the status has been changed to Inactive')

            return redirect('Fin_view_bank',id=id)


def Fin_banking_add_file(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id

        allmodules = Fin_Modules_List.objects.get(company_id = company,status = 'New')

        bank = Fin_Banking.objects.get(id =id)

        if request.method == 'POST':
            
            if len(request.FILES) != 0:
               file = request.FILES['file']

               attachment = Fin_BankingAttachments(
                   login_details = login_det,
                   company = company,
                   banking = bank,
                   file = file
               )
               attachment.save()

            messages.success(request, 'File has been saved successfully.')
            return redirect('Fin_view_bank',id=id)

def Fin_banking_add_comment(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id

        allmodules = Fin_Modules_List.objects.get(company_id = company,status = 'New')

        bank = Fin_Banking.objects.get(id =id)

        if request.method == 'POST':
            comment_text = request.POST.get('comment_text', '')

            if comment_text and bank:
                comment = Fin_BankingComments.objects.create(
                    login_details = login_det,
                    company = company,
                    banking = bank,
                    comment=comment_text)
                comment.save()

        messages.success(request, 'Comment has been saved successfully.')
        return redirect('Fin_view_bank',id=id)

def Fin_banking_delete_comment(request,id):

    if request.method == 'GET':

        comment = Fin_BankingComments.objects.get(id=id)
        bank = comment.banking

        comment.delete()

    messages.success(request, 'Comment has been deleted..')
    return redirect('Fin_view_bank',id=bank.id)


def Fin_banking_history(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id

        allmodules = Fin_Modules_List.objects.get(company_id = company,status = 'New')

        bank = Fin_Banking.objects.get(id =id)
        bank_history = Fin_BankingHistory.objects.filter(banking = bank)

        context = {
                'login_det':login_det,
                'com':com,
                'allmodules':allmodules,
                'bank_history':bank_history,
                'bank':bank
            }
        return render(request,'company/banking/Fin_banking_history.html',context)
    


def Fin_shareBankingStatementToEmail(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id

        try:
            if request.method == 'POST':
                emails_string = request.POST['email_ids']

    
                emails_list = [email.strip() for email in emails_string.split(',')]
                email_message = request.POST['email_message']
                print(emails_list)

               
                bank = Fin_Banking.objects.get(id=id)
                transactions = Fin_BankTransactions.objects.filter(banking=bank)
                        
                context = {'bank':bank, 
                           'company':company,
                           'trans':transactions
                           }
                template_path = 'company/banking/Fin_statement_template_to_mail.html'
                template = get_template(template_path)

                html  = template.render(context)
                result = BytesIO()
                pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
                pdf = result.getvalue()
                filename = f'BANKING - {bank.id}.pdf'
                subject = f"BANKING - {bank.id}"
                email = EmailMessage(subject, f"Hi,\nPlease find the attached STATEMENT - File-{bank.id}. \n{email_message}\n\n--\nRegards,\n{company.Company_name}\n{company.Address}\n{company.State} - {company.Country}\n{company.Contact}", from_email=settings.EMAIL_HOST_USER, to=emails_list)
                email.attach(filename, pdf, "application/pdf")
                email.send(fail_silently=False)

                msg = messages.success(request, 'Statement has been shared via email successfully..!')
                return redirect('Fin_view_bank',id=bank.id)
        except Exception as e:
            print(e)
            messages.error(request, f'{e}')
            return redirect('Fin_view_bank',id=bank.id)

def Fin_render_pdfstatment_view(request,id):
    
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id

        bank = Fin_Banking.objects.get(id=id)
        trans = Fin_BankTransactions.objects.filter(banking=bank)
        template_path = 'company/banking/Fin_banking_statement_pdf.html'
        context ={
            'bank':bank,
            'company':company,
            'trans':trans,
            
        }
        fname=bank.bank_name
    
        # Create a Django response object, and specify content_type as pdftemp_creditnote
        response = HttpResponse(content_type='application/pdf')
        #response['Content-Disposition'] = 'attachment; filename="certificate.pdf"'
        response['Content-Disposition'] =f'attachment; filename= {fname}.pdf'
        # find the template and render it.
        template = get_template(template_path)
        html = template.render(context)

        # create a pdf
        pisa_status = pisa.CreatePDF(
        html, dest=response)
        


        # if error then show some funy view
        if pisa_status.err:
            return HttpResponse('We had some errors <pre>' + html + '</pre>')
        return response
#-------------------------------------------------------------------------- end of banking----------------------------------------------------------------