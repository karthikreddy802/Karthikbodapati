from django.contrib import admin
from django.urls import path
from myapp import views

urlpatterns = [
    path('', views.home_view, name='root'),   #  root URL
    path('login/', views.login_view, name='login'),
    path('contact/', views.contact_view, name='contact'),
    path('about/', views.about_view, name='about'),
    path('admin_login/', views.admin_login_view, name='admin_login'),
    path('admin_panel/', views.admin_panel_view, name='admin_panel'),
    path('user_login/', views.user_login_view, name='user_login'),
    path('instructions/', views.instructions_view, name='instructions'),
    path('register/', views.register_view, name='register'),
    path('home/', views.home_view, name='home'),
    path('verify/<str:certificate_id>/', views.verify_certificate_view, name='verify_certificate'),
    #path('exam/<str:exam_type>/', views.exam_view, name='exam'),
    path('exam/<int:exam_id>/', views.exam_view, name='exam'),
    path("convert_pdf/<int:exam_id>/", views.convert_pdf_to_exam, name="convert_pdf"),
    path('admin_logout/', views.admin_logout_view, name='admin_logout'),
    path("update_violation/",views.update_violation,name="update_violation"),
    path('exam_finished/', views.exam_finished_view, name='exam_finished'),
    path('convert_pdf_to_exam/<int:exam_id>/', views.convert_pdf_to_exam, name='convert_pdf'),
    path('submit_exam/<int:exam_id>/', views.submit_exam_view, name='submit_exam'),

    path('add_exam/', views.add_exam_view, name='add_exam'),
    path('view_exam/', views.view_exam_view, name='view_exam'),
    path('delete_exam/<int:exam_id>/', views.delete_exam_view, name='delete_exam'),
    path('update_exam/<int:exam_id>/', views.update_exam_view, name='update_exam'),
    path('add_question/<int:exam_id>/', views.add_question_view, name='add_question'),
    path('generate_certificate/', views.generate_certificate_view, name='generate_certificate'),
    path('upload_pdf/<int:exam_id>/', views.upload_pdf_view, name='upload_pdf'),
    

]


