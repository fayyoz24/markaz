# from django.contrib import admin
# from django.urls import path, include
# from django.conf import settings
# from django.conf.urls.static import static

# from rest_framework.routers import DefaultRouter
# from rest_framework_simplejwt.views import TokenRefreshView

# from main.views import (
#     LoginView,
#     GroupViewSet,
#     TeacherViewSet,
#     StudentViewSet,
#     PaymentViewSet,
#     AttendanceViewSet,
#     GradeViewSet,
#     ExpenseViewSet,
#     ReportViewSet,
#     ReportView
# )

# router = DefaultRouter()
# router.register('api/groups',     GroupViewSet)
# router.register('api/teachers',   TeacherViewSet,   basename='teachers')
# router.register('api/students',   StudentViewSet,   basename='students')
# router.register('api/payments',   PaymentViewSet)
# router.register('api/attendance', AttendanceViewSet)
# router.register('api/grades',     GradeViewSet)
# router.register('api/expenses',   ExpenseViewSet,   basename='expenses')
# router.register('api/reports',    ReportViewSet,    basename='reports')

# urlpatterns = [
#     path('admin/',          admin.site.urls),
#     path('auth/login/',     LoginView.as_view(),        name='login'),
#     path('auth/refresh/',   TokenRefreshView.as_view(), name='token_refresh'),
#     path('api/reports/summary/', ReportView.as_view(), name='report_summary'),
#     path('',                include(router.urls)),
# ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)











from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from main.views import (
    LoginView,
    GroupViewSet,
    TeacherViewSet,
    StudentViewSet,
    PaymentViewSet,
    AttendanceViewSet,
    GradeViewSet,
    ExpenseViewSet,
    ReportViewSet,
    SeedView,          # ilgari ReportView deb noto'g'ri nomlanganedi
)

router = DefaultRouter()
router.register('api/groups',     GroupViewSet)
router.register('api/teachers',   TeacherViewSet,   basename='teachers')
router.register('api/students',   StudentViewSet,   basename='students')
router.register('api/payments',   PaymentViewSet)
router.register('api/attendance', AttendanceViewSet)
router.register('api/grades',     GradeViewSet)
router.register('api/expenses',   ExpenseViewSet,   basename='expenses')
router.register('api/reports',    ReportViewSet,    basename='reports')

urlpatterns = [
    path('admin/',          admin.site.urls),
    path('auth/login/',     LoginView.as_view(),        name='login'),
    path('auth/refresh/',   TokenRefreshView.as_view(), name='token_refresh'),
    path('api/seed/',       SeedView.as_view(),         name='seed_data'),   # demo data
    path('',                include(router.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)