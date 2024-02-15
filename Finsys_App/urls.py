#Finsys Final
from . import views
from django.urls import path,re_path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.static import serve

urlpatterns = [
    path('',views.Fin_index,name='Fin_index'),
    path('Company_Registration',views.Fin_CompanyReg,name='Fin_CompanyReg'),
    path('Company_Registration2/<id>',views.Fin_CompanyReg2,name='Fin_CompanyReg2'),
    path('Distributor_Registration',views.Fin_DistributorReg,name='Fin_DistributorReg'),
    path('Distributor_Registration_Action',views.Fin_DReg_Action,name='Fin_DReg_Action'),
    path('Distributor_Registration2/<id>',views.Fin_DReg2,name='Fin_DReg2'), 
    path('Distributor_Registration_Action2/<id>',views.Fin_DReg2_Action2,name='Fin_DReg2_Action2'), 
    path('Staff_Registration',views.Fin_StaffReg,name='Fin_StaffReg'),
    path('Adminhome',views.Fin_Adminhome,name='Fin_Adminhome'),
    path('LogIn',views.Fin_login,name='Fin_login'),
    path('Payment_Terms',views.Fin_PaymentTerm,name='Fin_PaymentTerm'),
    path('add_payment_terms',views.Fin_add_payment_terms,name='Fin_add_payment_terms'),
    path('Distributor',views.Fin_ADistributor,name='Fin_ADistributor'),
    path('Distributor_Request',views.Fin_Distributor_Request,name='Fin_Distributor_Request'),
    path('Distributor_Request_overview/<id>',views.Fin_Distributor_Req_overview,name='Fin_Distributor_Req_overview'),
    path('DReq_Accept/<id>',views.Fin_DReq_Accept,name='Fin_DReq_Accept'), 
    path('DReq_Reject/<id>',views.Fin_DReq_Reject,name='Fin_DReq_Reject'),
    path('All_Distributors',views.Fin_All_distributors,name='Fin_All_distributors'),
    path('All_Distributor_Overview/<id>',views.Fin_All_Distributor_Overview,name='Fin_All_Distributor_Overview'),  
    path('Distributor_Home',views.Fin_DHome,name='Fin_DHome'),
    path('companyReg_action',views.Fin_companyReg_action,name='Fin_companyReg_action'),
    path('CompanyReg2_action2/<id>',views.Fin_CompanyReg2_action2,name='Fin_CompanyReg2_action2'),
    path('Fin_Modules/<id>',views.Fin_Modules,name='Fin_Modules'),
    path('Add_Modules/<id>',views.Fin_Add_Modules,name='Fin_Add_Modules'),
    path('Company_Home',views.Fin_Com_Home,name='Fin_Com_Home'),
    path('AClients',views.Fin_AClients,name='Fin_AClients'), 
    path('Fin_AClients_Request',views.Fin_AClients_Request,name='Fin_AClients_Request'),  
    path('Fin_AClients_Request_OverView/<id>',views.Fin_AClients_Request_OverView,name='Fin_AClients_Request_OverView'),
    path('Client_Req_Accept/<id>',views.Fin_Client_Req_Accept,name='Fin_Client_Req_Accept'),
    path('Client_Req_Reject/<id>',views.Fin_Client_Req_Reject,name='Fin_Client_Req_Reject'),
    path('Fin_Admin_clients',views.Fin_Admin_clients,name='Fin_Admin_clients'), 
    path('Fin_Admin_clients_overview/<id>',views.Fin_Admin_clients_overview,name='Fin_Admin_clients_overview'),
    path('LOgout',views.logout,name="logout"),
    path('Company_Profile',views.Fin_Company_Profile,name="Fin_Company_Profile"),
    path('Fin_staffReg_action',views.Fin_staffReg_action,name='Fin_staffReg_action'),
    path('StaffReg2/<id>',views.Fin_StaffReg2,name='Fin_StaffReg2'),
    path('StaffReg2_Action/<id>',views.Fin_StaffReg2_Action,name='Fin_StaffReg2_Action'),
    path('Staff_Req',views.Fin_Staff_Req,name='Fin_Staff_Req'),
    path('Staff_Req_Accept/<id>',views.Fin_Staff_Req_Accept,name='Fin_Staff_Req_Accept'),
    path('Staff_Req_Reject/<id>',views.Fin_Staff_Req_Reject,name='Fin_Staff_Req_Reject'),
    path('All_Staffs',views.Fin_All_Staff,name='Fin_All_Staff'),
    path('DClient_req',views.Fin_DClient_req,name='Fin_DClient_req'),
    path('DClient_Req_Accept/<id>',views.Fin_DClient_Req_Accept,name='Fin_DClient_Req_Accept'),
    path('DClient_Req_Reject/<id>',views.Fin_DClient_Req_Reject,name='Fin_DClient_Req_Reject'), 
    path('DClients',views.Fin_DClients,name='Fin_DClients'),
    path('DProfile',views.Fin_DProfile,name='Fin_DProfile'),
    path('Edit_Modules',views.Fin_Edit_Modules,name='Fin_Edit_Modules'),
    path('Edit_Modules_Action',views.Fin_Edit_Modules_Action,name='Fin_Edit_Modules_Action'),
    path('Anotification',views.Fin_Anotification,name='Fin_Anotification'),
    path('Anoti_Overview/<int:id>',views.Fin_Anoti_Overview,name='Fin_Anoti_Overview'), 
    path('Module_Updation_Accept/<int:id>',views.Fin_Module_Updation_Accept,name='Fin_Module_Updation_Accept'),
    path('Module_Updation_Reject/<int:id>',views.Fin_Module_Updation_Reject,name='Fin_Module_Updation_Reject'),
    path('Change_payment_terms',views.Fin_Change_payment_terms,name='Fin_Change_payment_terms'),
    path('payment_terms_Updation_Accept/<id>',views.Fin_payment_terms_Updation_Accept,name='Fin_payment_terms_Updation_Accept'),
    path('payment_terms_Updation_Reject/<id>',views.Fin_payment_terms_Updation_Reject,name='Fin_payment_terms_Updation_Reject'),
    path('Dnotification',views.Fin_Dnotification,name='Fin_Dnotification'),
    path('Dnoti_Overview/<id>',views.Fin_Dnoti_Overview,name='Fin_Dnoti_Overview'), 
    path('DModule_Updation_Accept/<id>',views.Fin_DModule_Updation_Accept,name='Fin_DModule_Updation_Accept'),
    path('DModule_Updation_Reject/<id>',views.Fin_DModule_Updation_Reject,name='Fin_DModule_Updation_Reject'),
    path('Cnotification',views.Fin_Cnotification,name='Fin_Cnotification'),
    path('Wrong',views.Fin_Wrong,name='Fin_Wrong'),
    path('Wrong_Action',views.Fin_Wrong_Action,name='Fin_Wrong_Action'),
    path('DChange_payment_terms',views.Fin_DChange_payment_terms,name='Fin_DChange_payment_terms'),
    path('Client_delete/<id>',views.Fin_Client_delete,name='Fin_Client_delete'),
    path('Distributor_delete/<id>',views.Fin_Distributor_delete,name='Fin_Distributor_delete'),
    path('Staff_delete/<id>',views.Fin_Staff_delete,name='Fin_Staff_delete'),
    path('Edit_Company_profile',views.Fin_Edit_Company_profile,name='Fin_Edit_Company_profile'),
    path('Edit_Company_profile_Action',views.Fin_Edit_Company_profile_Action,name='Fin_Edit_Company_profile_Action'),
    path('Edit_Staff_profile',views.Fin_Edit_Staff_profile,name='Fin_Edit_Staff_profile'),
    path('Edit_Staff_profile_Action',views.Fin_Edit_Staff_profile_Action,name='Fin_Edit_Staff_profile_Action'),
    path('Edit_Dprofile',views.Fin_Edit_Dprofile,name='Fin_Edit_Dprofile'),
    path('Edit_Dprofile_Action',views.Fin_Edit_Dprofile_Action,name='Fin_Edit_Dprofile_Action'),
    path('DClient_req_overview/<id>',views.Fin_DClient_req_overview,name='Fin_DClient_req_overview'),
    path('DClients_overview/<id>',views.Fin_DClients_overview,name='Fin_DClients_overview'),
    path('DClient_remove/<id>',views.Fin_DClient_remove,name='Fin_DClient_remove'),
    
    #------shemeem----Items&ChartOfAccounts-----------------------
    # Items
    path('Fin_items',views.Fin_items, name='Fin_items'),
    path('Fin_create_item',views.Fin_createItem, name = 'Fin_createItem'),
    path('Fin_create_new_item',views.Fin_createNewItem, name='Fin_createNewItem'),
    path('Fin_view_item/<int:id>',views.Fin_viewItem, name='Fin_viewItem'),
    path('Fin_save_item_unit',views.Fin_saveItemUnit, name='Fin_saveItemUnit'),
    path('Fin_get_item_units',views.Fin_getItemUnits, name='Fin_getItemUnits'),
    path('Fin_create_new_account_from_items',views.Fin_createNewAccountFromItems, name='Fin_createNewAccountFromItems'),
    path('Fin_change_item_status/<int:id>/<str:status>',views.Fin_changeItemStatus, name='Fin_changeItemStatus'),
    path('Fin_edit_item/<int:id>',views.Fin_editItem, name='Fin_editItem'),
    path('Fin_update_item/<int:id>',views.Fin_updateItem, name='Fin_updateItem'),
    path('Fin_delete_item/<int:id>',views.Fin_deleteItem, name='Fin_deleteItem'),
    path('Fin_item_history/<int:id>',views.Fin_itemHistory, name='Fin_itemHistory'),
    path('Fin_item_transaction_pdf/<int:id>',views.Fin_itemTransactionPdf, name='Fin_itemTransactionPdf'),
    path('Fin_share_item_transactions_to_email/<int:id>',views.Fin_shareItemTransactionsToEmail, name='Fin_shareItemTransactionsToEmail'),
    path('Fin_add_item_comment/<int:id>',views.Fin_addItemComment, name='Fin_addItemComment'),
    path('Fin_delete_item_comment/<int:id>',views.Fin_deleteItemComment, name='Fin_deleteItemComment'),

    # Chart of accounts
    path('Fin_chart_of_accounts',views.Fin_chartOfAccounts, name='Fin_chartOfAccounts'),
    path('Fin_add_account',views.Fin_addAccount, name='Fin_addAccount'),
    path('Fin_check_accounts',views.Fin_checkAccounts, name='Fin_checkAccounts'),
    path('Fin_create_account',views.Fin_createAccount, name='Fin_createAccount'),
    path('Fin_account_overview/<int:id>',views.Fin_accountOverview, name='Fin_accountOverview'),
    path('Fin_change_acc_status/<int:id>/<str:status>',views.Fin_changeAccountStatus, name='Fin_changeAccountStatus'),
    path('Fin_account_transaction_pdf/<int:id>',views.Fin_accountTransactionPdf, name='Fin_accountTransactionPdf'),
    path('Fin_share_acc_transactions_to_email/<int:id>',views.Fin_shareAccountTransactionsToEmail, name='Fin_shareAccountTransactionsToEmail'),
    path('Fin_delete_account/<int:id>',views.Fin_deleteAccount, name= 'Fin_deleteAccount'),
    path('Fin_edit_account/<int:id>',views.Fin_editAccount, name='Fin_editAccount'),
    path('Fin_update_account/<int:id>',views.Fin_updateAccount, name='Fin_updateAccount'),
    path('Fin_account_history/<int:id>',views.Fin_accountHistory, name='Fin_accountHistory'),
    #End
    
    path('Fin_bankholder',views.Fin_bankholder,name='Fin_bankholder'),
    path('Fin_addbank',views.Fin_addbank,name='Fin_addbank'),
    path('Fin_Bankaccountholder',views.Fin_Bankaccountholder,name='Fin_Bankaccountholder'),
    path('Fin_Bankholderview/<int:id>/', views.Fin_Bankholderview, name='Fin_Bankholderview'),
    path('Fin_activebankholder/<int:id>/',views.Fin_activebankholder,name='Fin_activebankholder'),
    path('Fin_inactivatebankaccount/<int:id>/',views.Fin_inactivatebankaccount,name='Fin_inactivatebankaccount'),
    path('Fin_Editholder/<int:id>/',views.Fin_Editholder,name='Fin_Editholder'),
    path('Fin_Editbankholder/<int:id>/',views.Fin_Editbankholder,name='Fin_Editbankholder'),
    path('Fin_deleteholder/<int:id>/',views.Fin_deleteholder,name='Fin_deleteholder'),
    path('Fin_addcomment/<int:id>/', views.Fin_addcomment, name='Fin_addcomment'),
    path('Fin_deletecomment/<int:id>/', views.Fin_deletecomment, name='Fin_deletecomment'),
    path('Fin_Bankhistory/<int:holder_id>/', views.Fin_Bankhistory, name='Fin_Bankhistory'),
    
    path('Fin_fetchaccountnumbers/', views.Fin_fetchaccountnumbers, name='Fin_fetchaccountnumbers'),
    path('Fin_fetchallbanks/', views.Fin_fetchallbanks, name='Fin_fetchallbanks'),
    path('Fin_AddBankinHolder/', views.Fin_AddBankinHolder, name='Fin_AddBankinHolder'),
    
    # -------------Shemeem--------Price List & Customers-------------------------------
    
    path('Fin_price_list',views.Fin_priceList, name='Fin_priceList'),
    path('Fin_add_price_list',views.Fin_addPriceList, name='Fin_addPriceList'),
    path('Fin_create_price_list',views.Fin_createPriceList, name='Fin_createPriceList'),
    path('Fin_view_price_list/<int:id>',views.Fin_viewPriceList, name='Fin_viewPriceList'),
    path('Fin_change_price_list_status/<int:id>/<str:status>',views.Fin_changePriceListStatus, name='Fin_changePriceListStatus'),
    path('Fin_delete_price_list/<int:id>',views.Fin_deletePriceList, name='Fin_deletePriceList'),
    path('Fin_add_price_list_comment/<int:id>',views.Fin_addPriceListComment, name='Fin_addPriceListComment'),
    path('Fin_delete_price_list_comment/<int:id>',views.Fin_deletePriceListComment, name='Fin_deletePriceListComment'),
    path('Fin_price_list_history/<int:id>',views.Fin_priceListHistory, name='Fin_priceListHistory'),
    path('Fin_edit_price_list/<int:id>',views.Fin_editPriceList, name='Fin_editPriceList'),
    path('Fin_update_price_list/<int:id>',views.Fin_updatePriceList, name='Fin_updatePriceList'),
    path('Fin_price_list_view_pdf/<int:id>',views.Fin_priceListViewPdf, name='Fin_priceListViewPdf'),
    path('Fin_share_price_list_view_to_email/<int:id>',views.Fin_sharePriceListViewToEmail, name='Fin_sharePriceListViewToEmail'),
    
    # Customers
    path('Fin_customers',views.Fin_customers, name='Fin_customers'),
    path('Fin_add_customer',views.Fin_addCustomer, name='Fin_addCustomer'),
    path('Fin_check_customer_name',views.Fin_checkCustomerName, name='Fin_checkCustomerName'),
    path('Fin_check_customer_GSTIN',views.Fin_checkCustomerGSTIN, name='Fin_checkCustomerGSTIN'),
    path('Fin_check_customer_PAN',views.Fin_checkCustomerPAN, name='Fin_checkCustomerPAN'),
    path('Fin_check_customer_phone',views.Fin_checkCustomerPhone, name='Fin_checkCustomerPhone'),
    path('Fin_check_customer_email',views.Fin_checkCustomerEmail, name='Fin_checkCustomerEmail'),
    path('Fin_create_customer',views.Fin_createCustomer, name='Fin_createCustomer'),
    path('Fin_new_customer_payment_term',views.Fin_newCustomerPaymentTerm, name='Fin_newCustomerPaymentTerm'),
    path('Fin_view_customer/<int:id>',views.Fin_viewCustomer, name='Fin_viewCustomer'),
    path('Fin_change_customer_status/<int:id>/<str:status>',views.Fin_changeCustomerStatus, name='Fin_changeCustomerStatus'),
    path('Fin_delete_customer/<int:id>',views.Fin_deleteCustomer, name= 'Fin_deleteCustomer'),
    path('Fin_edit_customer/<int:id>',views.Fin_editCustomer, name='Fin_editCustomer'),
    path('Fin_update_customer/<int:id>',views.Fin_updateCustomer, name='Fin_updateCustomer'),
    path('Fin_customer_history/<int:id>',views.Fin_customerHistory, name='Fin_customerHistory'),
    path('Fin_customer_transactions_pdf/<int:id>',views.Fin_customerTransactionsPdf, name='Fin_customerTransactionsPdf'),
    path('Fin_share_customer_transactions_to_email/<int:id>',views.Fin_shareCustomerTransactionsToEmail, name='Fin_shareCustomerTransactionsToEmail'),
    path('Fin_add_customer_comment/<int:id>',views.Fin_addCustomerComment, name='Fin_addCustomerComment'),
    path('Fin_delete_customer_comment/<int:id>',views.Fin_deleteCustomerComment, name='Fin_deleteCustomerComment'),
    
    # harikrishnan (start)--------------------------------
    
    path('employee_list',views.employee_list,name="employee_list"),
    path('employee_create_page',views.employee_create_page,name="employee_create_page"),
    path('employee_save',views.employee_save,name="employee_save"),
    path('employee_overview/<int:pk>',views.employee_overview,name="employee_overview"),
    path('activate/<int:pk>',views.activate,name="activate"),
    path('employee_edit_page/<int:pk>',views.employee_edit_page,name="employee_edit_page"),
    path('employee_update/<int:pk>',views.employee_update,name="employee_update"),
    path('employee_comment/<int:pk>',views.employee_comment,name="employee_comment"),
    path('employee_comment_view/<int:pk>',views.employee_comment_view,name="employee_comment_view"),
    path('employee_delete/<int:pk>',views.employee_delete,name="employee_delete"),
    path('employee_history/<int:pk>',views.employee_history,name="employee_history"),
    path('employee_profile_email/<int:pk>',views.employee_profile_email,name="employee_profile_email"),
    path('Employee_Profile_PDF/<int:pk>',views.Employee_Profile_PDF,name="Employee_Profile_PDF"),

    path('holiday_list',views.holiday_list,name="holiday_list"),
    path('holiday_create_page',views.holiday_create_page,name="holiday_create_page"),
    path('holiday_add',views.holiday_add,name="holiday_add"),
    path('holiday_calendar_view/<int:mn>/<int:yr>', views.holiday_calendar_view, name='holiday_calendar_view'),
    path('holiday_edit_page/<int:pk>/<int:mn>/<int:yr>', views.holiday_edit_page, name='holiday_edit_page'),
    path('holiday_update/<int:pk>/<int:mn>/<int:yr>',views.holiday_update,name="holiday_update"),
    path('holiday_delete/<int:pk>',views.holiday_delete,name="holiday_delete"),
    path('holiday_history/<int:month>/<int:year>',views.holiday_history,name="holiday_history"),
    
    # harikrishnan (end)--------------------------------
    
    # End
    
    # harikrishnan (start)--------------------------------

    path('employee_blood_group',views.employee_blood_group,name="employee_blood_group"),
    path('holiday_comment/<int:mn>/<int:yr>',views.holiday_comment,name="holiday_comment"),
    path('holiday_comment_delete/<int:pk>/<int:mn>/<int:yr>/',views.holiday_comment_delete,name="holiday_comment_delete"),
    path('employee_comment_delete/<int:pk>/<int:id>/',views.employee_comment_delete,name="employee_comment_delete"),
    path('bloodgroup_data',views.bloodgroup_data,name="bloodgroup_data"),
    
    # harikrishnan (end)--------------------------------
    
    # ---------------------------Start Banking------------------------------------ 

    path('Banking_listout',views.Fin_banking_listout,name='Fin_banking_listout'),
    path('Banking_sort_by_balance',views.Fin_banking_sort_by_balance,name='Fin_banking_sort_by_balance'),
    path('Banking_sort_by_name',views.Fin_banking_sort_by_name,name='Fin_banking_sort_by_name'),
    path('Banking_filter_active',views.Fin_banking_filter_active,name='Fin_banking_filter_active'),
    path('Banking_filter_inactive',views.Fin_banking_filter_inactive,name='Fin_banking_filter_inactive'),

    path('Create_bank',views.Fin_create_bank,name='Fin_create_bank'),
    path('Banking_check_account_number',views.Fin_banking_check_account_number,name='Fin_banking_check_account_number'),
    path('Create_bank_account',views.Fin_create_bank_account,name='Fin_create_bank_account'),

    path('View_Bank/<int:id>',views.Fin_view_bank,name='Fin_view_bank'),
    path('Bank_to_cash/<int:id>',views.Fin_bank_to_cash,name='Fin_bank_to_cash'),
    path('Save_bankTocash',views.Fin_save_bankTocash,name='Fin_save_bankTocash'),

    path('Cash_to_bank/<int:id>',views.Fin_cash_to_bank,name='Fin_cash_to_bank'),
    path('Save_cashTobank',views.Fin_save_cashTobank,name='Fin_save_cashTobank'),

    path('Bank_to_bank/<int:id>',views.Fin_bank_to_bank,name='Fin_bank_to_bank'),
    path('Save_bankTobank/<int:id>',views.Fin_save_bankTobank,name='Fin_save_bankTobank'),

    path('Bank_adjust/<int:id>',views.Fin_bank_adjust,name='Fin_bank_adjust'),
    path('Save_bank_adjust',views.Fin_save_bank_adjust,name='Fin_save_bank_adjust'),

    path('Edit_bank/<int:id>',views.Fin_edit_bank,name='Fin_edit_bank'),
    path('Edit_bank_account/<int:id>',views.Fin_edit_bank_account,name='Fin_edit_bank_account'),
    path('Change_bank_status/<int:id>',views.Fin_change_bank_status,name='Fin_change_bank_status'),
    path('Delete_bank/<int:id>',views.Fin_delete_bank,name='Fin_delete_bank'),

    path('Banking_add_file/<int:id>',views.Fin_banking_add_file,name='Fin_banking_add_file'),
    path('Banking_add_comment/<int:id>',views.Fin_banking_add_comment,name='Fin_banking_add_comment'),
    path('Banking_delete_comment/<int:id>',views.Fin_banking_delete_comment,name='Fin_banking_delete_comment'),
    path('Banking_history/<int:id>',views.Fin_banking_history,name='Fin_banking_history'),
    path('ShareBankingStatementToEmail/<int:id>',views.Fin_shareBankingStatementToEmail,name='Fin_shareBankingStatementToEmail'),
    path('Render_pdfstatment_view/<int:id>',views.Fin_render_pdfstatment_view,name='Fin_render_pdfstatment_view'),
    #End
    
    # ---------------Admin updates----------------
    path('remove_payment_terms/<int:pk>',views.Fin_remove_payment_terms,name='Fin_remove_payment_terms'),
    path('Clients_under_Distributors',views.Fin_Clients_under_distributors,name='Fin_Clients_under_distributors'),
    path('getClients_Under_Distributor',views.get_clients_under_distributor,name='get_clients_under_distributor'),
    path('Distributor/client/details/<int:pk>',views.distributor_client_profile_details,name='distributor_client_profile_details'),
    path('Admin/Trial_Period/Section',views.Fin_Admin_trial_period_section,name='Fin_Admin_trial_period_section'),
    path('Admin/Trial_Period/Clients',views.Fin_Admin_trial_period_clients,name='Fin_Admin_trial_period_clients'),
    path('Admin/Trial_Period/Distributor-Clients',views.Fin_Admin_trial_period_distributor_clients,name='Fin_Admin_trial_period_distributor_clients'),
    path('ADpayment_terms_Updation_Accept/<int:id>',views.Fin_ADpayment_terms_Updation_Accept,name='Fin_ADpayment_terms_Updation_Accept'),
    path('ADpayment_terms_Updation_Reject/<int:id>',views.Fin_ADpayment_terms_Updation_Reject,name='Fin_ADpayment_terms_Updation_Reject'),

    # ---------------Distributor updates----------------
    path('DClient/Trial_Period/Details',views.Fin_trial_periodclients,name='Fin_trial_periodclients'),
    path('Dpayment_terms_Updation_Accept/<int:id>',views.Fin_Dpayment_terms_Updation_Accept,name='Fin_Dpayment_terms_Updation_Accept'),
    path('Dpayment_terms_Updation_Reject/<int:id>',views.Fin_Dpayment_terms_Updation_Reject,name='Fin_Dpayment_terms_Updation_Reject'),
 
    # ---------------Company updates----------------
    path('Company/Trial/Review',views.Fin_company_trial_feedback,name='Fin_company_trial_feedback'),


    re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)