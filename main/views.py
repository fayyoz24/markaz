# # from rest_framework import viewsets, permissions, status
# # from rest_framework.decorators import action
# # from rest_framework.response import Response

# # from rest_framework_simplejwt.views import TokenObtainPairView
# # from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
# # from django.db.models.functions import TruncMonth, TruncDate, TruncDay
# # from django.db.models import Sum, Count
# # from django.contrib.auth.hashers import make_password
# # from datetime import date, timedelta
# # from .models import User, Group, StudentProfile, Payment, Attendance, Grade
# # from .serializers import (
# #     UserSerializer, GroupSerializer, StudentProfileSerializer,
# #     PaymentSerializer, AttendanceSerializer, GradeSerializer
# # )


# # # ─── Custom JWT with role ─────────────────────────────────────────────────────
# # class CustomTokenSerializer(TokenObtainPairSerializer):
# #     @classmethod
# #     def get_token(cls, user):
# #         token = super().get_token(user)
# #         token['role'] = user.role
# #         token['name'] = user.get_full_name()
# #         return token

# #     def validate(self, attrs):
# #         data = super().validate(attrs)
# #         data['role'] = self.user.role
# #         data['name'] = self.user.get_full_name()
# #         data['user_id'] = self.user.id
# #         return data


# # class LoginView(TokenObtainPairView):
# #     serializer_class = CustomTokenSerializer


# # # ─── Permissions ──────────────────────────────────────────────────────────────
# # class IsAdmin(permissions.BasePermission):
# #     def has_permission(self, request, view):
# #         return request.user.is_authenticated and request.user.role == 'admin'


# # class IsTeacher(permissions.BasePermission):
# #     def has_permission(self, request, view):
# #         return request.user.is_authenticated and request.user.role in ['admin', 'teacher']


# # # ─── Group ViewSet ────────────────────────────────────────────────────────────
# # class GroupViewSet(viewsets.ModelViewSet):
# #     queryset = Group.objects.select_related('teacher').prefetch_related('students')
# #     serializer_class = GroupSerializer

# #     def get_permissions(self):
# #         if self.action in ['create', 'update', 'partial_update', 'destroy']:
# #             return [IsAdmin()]
# #         return [permissions.IsAuthenticated()]

# #     @action(detail=True, methods=['get'])
# #     def students(self, request, pk=None):
# #         group = self.get_object()
# #         students = group.students.select_related('user')
# #         serializer = StudentProfileSerializer(students, many=True)
# #         return Response(serializer.data)


# # # ─── Student ViewSet ──────────────────────────────────────────────────────────
# # class StudentViewSet(viewsets.ModelViewSet):
# #     queryset = StudentProfile.objects.select_related('user', 'group')
# #     serializer_class = StudentProfileSerializer

# #     def get_permissions(self):
# #         if self.action in ['create', 'update', 'partial_update', 'destroy']:
# #             return [IsAdmin()]
# #         return [permissions.IsAuthenticated()]

# #     def get_queryset(self):
# #         user = self.request.user
# #         if user.role == 'admin':
# #             return StudentProfile.objects.select_related('user', 'group')
# #         elif user.role == 'teacher':
# #             # Teacher only sees students in their groups
# #             return StudentProfile.objects.filter(
# #                 group__teacher=user
# #             ).select_related('user', 'group')
# #         elif user.role == 'student':
# #             return StudentProfile.objects.filter(user=user).select_related('user', 'group')
# #         return StudentProfile.objects.none()

# #     @action(detail=True, methods=['get'])
# #     def payments(self, request, pk=None):
# #         student = self.get_object()
# #         payments = student.payments.all().order_by('-payment_date')
# #         serializer = PaymentSerializer(payments, many=True)
# #         return Response(serializer.data)

# #     @action(detail=True, methods=['get'])
# #     def attendance(self, request, pk=None):
# #         student = self.get_object()
# #         records = student.attendance_records.all().order_by('-date')
# #         serializer = AttendanceSerializer(records, many=True)
# #         return Response(serializer.data)

# #     @action(detail=True, methods=['get'])
# #     def grades(self, request, pk=None):
# #         student = self.get_object()
# #         grades = student.grades.all().order_by('-date')
# #         serializer = GradeSerializer(grades, many=True)
# #         return Response(serializer.data)


# # # ─── Payment ViewSet ──────────────────────────────────────────────────────────
# # class PaymentViewSet(viewsets.ModelViewSet):
# #     queryset = Payment.objects.select_related('student__user', 'student__group')
# #     serializer_class = PaymentSerializer
# #     permission_classes = [IsAdmin]

# #     def perform_create(self, serializer):
# #         serializer.save(created_by=self.request.user)

# #     def get_queryset(self):
# #         qs = super().get_queryset().order_by('-payment_date')
# #         month = self.request.query_params.get('month')
# #         if month:
# #             qs = qs.filter(month__startswith=month)
# #         group_id = self.request.query_params.get('group')
# #         if group_id:
# #             qs = qs.filter(student__group_id=group_id)
# #         return qs


# # # ─── Attendance ViewSet ───────────────────────────────────────────────────────
# # class AttendanceViewSet(viewsets.ModelViewSet):
# #     queryset = Attendance.objects.select_related('student__user', 'group')
# #     serializer_class = AttendanceSerializer
# #     permission_classes = [IsTeacher]

# #     def get_queryset(self):
# #         user = self.request.user
# #         qs = super().get_queryset()
# #         if user.role == 'teacher':
# #             qs = qs.filter(group__teacher=user)
# #         group_id = self.request.query_params.get('group')
# #         if group_id:
# #             qs = qs.filter(group_id=group_id)
# #         date_param = self.request.query_params.get('date')
# #         if date_param:
# #             qs = qs.filter(date=date_param)
# #         return qs.order_by('-date')

# #     @action(detail=False, methods=['post'])
# #     def bulk_create(self, request):
# #         """Mark attendance for multiple students at once."""
# #         records = request.data.get('records', [])
# #         results = []
# #         for rec in records:
# #             obj, created = Attendance.objects.update_or_create(
# #                 student_id=rec['student_id'],
# #                 date=rec['date'],
# #                 defaults={
# #                     'group_id': rec['group_id'],
# #                     'is_present': rec['is_present'],
# #                     'recorded_by': request.user
# #                 }
# #             )
# #             results.append({'id': obj.id, 'created': created})
# #         return Response({'saved': len(results)})


# # # ─── Grade ViewSet ────────────────────────────────────────────────────────────
# # class GradeViewSet(viewsets.ModelViewSet):
# #     queryset = Grade.objects.select_related('student__user', 'teacher')
# #     serializer_class = GradeSerializer
# #     permission_classes = [IsTeacher]

# #     def perform_create(self, serializer):
# #         serializer.save(teacher=self.request.user)

# #     def get_queryset(self):
# #         user = self.request.user
# #         qs = super().get_queryset()
# #         if user.role == 'teacher':
# #             qs = qs.filter(teacher=user)
# #         student_id = self.request.query_params.get('student')
# #         if student_id:
# #             qs = qs.filter(student_id=student_id)
# #         return qs


# # # ─── Admin Reports ────────────────────────────────────────────────────────────
# # class ReportViewSet(viewsets.ViewSet):
# #     permission_classes = [IsAdmin]

# #     @action(detail=False, methods=['get'])
# #     def monthly_revenue(self, request):
# #         """Monthly total revenue for the past 6 months."""
# #         data = (
# #             Payment.objects
# #             .annotate(payment_month=TruncMonth('payment_date'))
# #             .values('payment_month')
# #             .annotate(total=Sum('amount'), payment_count=Count('id'))
# #             .order_by('-payment_month')[:6]
# #         )
# #         return Response(list(data))

# #     @action(detail=False, methods=['get'])
# #     def daily_revenue(self, request):
# #         """Daily revenue for current month."""
# #         today = date.today()
# #         data = (
# #             Payment.objects
# #             .filter(payment_date__year=today.year, payment_date__month=today.month)
# #             .annotate(day=TruncDate('payment_date'))
# #             .values('day')
# #             .annotate(total=Sum('amount'), payment_count=Count('id'))
# #             .order_by('-total')[:10]
# #         )
# #         return Response(list(data))

# #     @action(detail=False, methods=['get'])
# #     def debtors(self, request):
# #         """Students who haven't paid this month."""
# #         today = date.today()
# #         current_month = date(today.year, today.month, 1)
# #         paid_ids = Payment.objects.filter(month=current_month).values_list('student_id', flat=True)
# #         debtors = StudentProfile.objects.exclude(id__in=paid_ids).select_related('user', 'group')
# #         serializer = StudentProfileSerializer(debtors, many=True)
# #         return Response(serializer.data)

# #     @action(detail=False, methods=['get'])
# #     def summary(self, request):
# #         """Dashboard summary stats."""
# #         today = date.today()
# #         current_month = date(today.year, today.month, 1)
# #         total_students = StudentProfile.objects.count()
# #         active_groups = Group.objects.filter(status='active').count()
# #         monthly_revenue = Payment.objects.filter(
# #             month=current_month
# #         ).aggregate(total=Sum('amount'))['total'] or 0
# #         debtors_count = StudentProfile.objects.exclude(
# #             payments__month=current_month
# #         ).count()
# #         return Response({
# #             'total_students': total_students,
# #             'active_groups': active_groups,
# #             'monthly_revenue': float(monthly_revenue),
# #             'debtors_count': debtors_count,
# #         })


# # class TeacherViewSet(viewsets.ModelViewSet):
# #     queryset = User.objects.filter(role='teacher')
# #     serializer_class = UserSerializer
# #     permission_classes = [IsAdmin]

# #     def perform_create(self, serializer):
# #         serializer.save(
# #             role='teacher',
# #             password=make_password(self.request.data.get('password', '12345678'))
# #         )

# # # class StudentViewSet(viewsets.ModelViewSet):
# # #     permission_classes = [IsAdmin]

# # #     # GET uchun StudentSerializer, POST uchun UserSerializer
# # #     def get_serializer_class(self):
# # #         if self.action == 'create':
# # #             return UserSerializer
# # #         return StudentProfileSerializer

# # #     def get_queryset(self):
# # #         return User.objects.filter(role='student').select_related(
# # #             'student_profile__group'
# # #         )

# # #     def perform_create(self, serializer):
# # #         data = self.request.data
# # #         user = serializer.save(
# # #             role='student',
# # #             password=make_password(data.get('password', '12345678'))
# # #         )
# # #         StudentProfile.objects.create(
# # #             user=user,
# # #             group_id=data.get('group') or None,
# # #             discount=data.get('discount', 0),
# # #             payment_due_day=data.get('payment_due_day', 15),
# # #         )



# from rest_framework import viewsets, permissions, status
# from rest_framework.decorators import action
# from rest_framework.response import Response
# from rest_framework_simplejwt.views import TokenObtainPairView
# from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
# from django.db.models.functions import TruncMonth, TruncDate
# from django.db.models import Sum, Count
# from django.contrib.auth.hashers import make_password
# from datetime import date
# from .models import User, Group, StudentProfile, Payment, Attendance, Grade
# from .serializers import (
#     UserSerializer, GroupSerializer, StudentProfileSerializer,
#     StudentSerializer, PaymentSerializer, AttendanceSerializer, GradeSerializer
# )


# # ─── Custom JWT ───────────────────────────────────────────────────────────────
# class CustomTokenSerializer(TokenObtainPairSerializer):
#     @classmethod
#     def get_token(cls, user):
#         token = super().get_token(user)
#         token['role'] = user.role
#         token['name'] = user.get_full_name()
#         return token

#     def validate(self, attrs):
#         data = super().validate(attrs)
#         data['role'] = self.user.role
#         data['name'] = self.user.get_full_name()
#         data['user_id'] = self.user.id
#         return data


# class LoginView(TokenObtainPairView):
#     serializer_class = CustomTokenSerializer


# # ─── Permissions ──────────────────────────────────────────────────────────────
# class IsAdmin(permissions.BasePermission):
#     def has_permission(self, request, view):
#         return request.user.is_authenticated and request.user.role == 'admin'


# class IsTeacher(permissions.BasePermission):
#     def has_permission(self, request, view):
#         return request.user.is_authenticated and request.user.role in ['admin', 'teacher']


# # ─── Group ViewSet ────────────────────────────────────────────────────────────
# class GroupViewSet(viewsets.ModelViewSet):
#     queryset = Group.objects.select_related('teacher').prefetch_related('students')
#     serializer_class = GroupSerializer

#     def get_permissions(self):
#         if self.action in ['create', 'update', 'partial_update', 'destroy']:
#             return [IsAdmin()]
#         return [permissions.IsAuthenticated()]

#     @action(detail=True, methods=['get'])
#     def students(self, request, pk=None):
#         group = self.get_object()
#         students = group.students.select_related('user')
#         serializer = StudentProfileSerializer(students, many=True)
#         return Response(serializer.data)


# # ─── Teacher ViewSet ──────────────────────────────────────────────────────────
# class TeacherViewSet(viewsets.ModelViewSet):
#     queryset = User.objects.filter(role='teacher')
#     serializer_class = UserSerializer
#     permission_classes = [IsAdmin]

#     def perform_create(self, serializer):
#         serializer.save(
#             role='teacher',
#             password=make_password(self.request.data.get('password', '12345678'))
#         )


# # ─── Student ViewSet ──────────────────────────────────────────────────────────
# class StudentViewSet(viewsets.ModelViewSet):
#     permission_classes = [IsAdmin]

#     def get_serializer_class(self):
#         # POST (create) — UserSerializer (username, first_name, last_name, phone yozish uchun)
#         # Qolgan barcha action — StudentSerializer (profile ma'lumotlari bilan)
#         if self.action == 'create':
#             return UserSerializer
#         return StudentSerializer

#     def get_queryset(self):
#         user = self.request.user
#         qs = User.objects.filter(role='student').select_related('student_profile__group')

#         # O'qituvchi faqat o'z gruppasidagi o'quvchilarni ko'radi
#         if user.role == 'teacher':
#             qs = qs.filter(student_profile__group__teacher=user)
#         # O'quvchi faqat o'zini ko'radi
#         elif user.role == 'student':
#             qs = qs.filter(id=user.id)

#         return qs

#     def get_permissions(self):
#         if self.action in ['create', 'update', 'partial_update', 'destroy']:
#             return [IsAdmin()]
#         return [permissions.IsAuthenticated()]

#     def perform_create(self, serializer):
#         data = self.request.data
#         user = serializer.save(
#             role='student',
#             password=make_password(data.get('password', '12345678'))
#         )
#         StudentProfile.objects.create(
#             user=user,
#             group_id=data.get('group') or None,
#             discount=data.get('discount', 0),
#             payment_due_day=data.get('payment_due_day', 15),
#         )

#     # /api/students/{id}/payments/
#     @action(detail=True, methods=['get'])
#     def payments(self, request, pk=None):
#         student_user = self.get_object()
#         try:
#             profile = student_user.student_profile
#         except StudentProfile.DoesNotExist:
#             return Response([])
#         payments = Payment.objects.filter(student=profile).order_by('-payment_date')
#         serializer = PaymentSerializer(payments, many=True)
#         return Response(serializer.data)

#     # /api/students/{id}/attendance/
#     @action(detail=True, methods=['get'])
#     def attendance(self, request, pk=None):
#         student_user = self.get_object()
#         try:
#             profile = student_user.student_profile
#         except StudentProfile.DoesNotExist:
#             return Response([])
#         records = Attendance.objects.filter(student=profile).order_by('-date')
#         serializer = AttendanceSerializer(records, many=True)
#         return Response(serializer.data)

#     # /api/students/{id}/grades/
#     @action(detail=True, methods=['get'])
#     def grades(self, request, pk=None):
#         student_user = self.get_object()
#         try:
#             profile = student_user.student_profile
#         except StudentProfile.DoesNotExist:
#             return Response([])
#         grades = Grade.objects.filter(student=profile).order_by('-date')
#         serializer = GradeSerializer(grades, many=True)
#         return Response(serializer.data)


# # ─── Payment ViewSet ──────────────────────────────────────────────────────────
# class PaymentViewSet(viewsets.ModelViewSet):
#     queryset = Payment.objects.select_related('student__user', 'student__group')
#     serializer_class = PaymentSerializer
#     permission_classes = [IsAdmin]

#     def perform_create(self, serializer):
#         serializer.save(created_by=self.request.user)

#     def get_queryset(self):
#         qs = super().get_queryset().order_by('-payment_date')
#         month = self.request.query_params.get('month')
#         if month:
#             qs = qs.filter(month__startswith=month)
#         group_id = self.request.query_params.get('group')
#         if group_id:
#             qs = qs.filter(student__group_id=group_id)
#         return qs

# # ─── Attendance ViewSet ───────────────────────────────────────────────────────
# class AttendanceViewSet(viewsets.ModelViewSet):
#     queryset = Attendance.objects.select_related('student__user', 'group')
#     serializer_class = AttendanceSerializer
#     permission_classes = [IsTeacher]

#     def get_queryset(self):
#         user = self.request.user
#         qs = super().get_queryset()
#         if user.role == 'teacher':
#             qs = qs.filter(group__teacher=user)
#         group_id = self.request.query_params.get('group')
#         if group_id:
#             qs = qs.filter(group_id=group_id)
#         date_param = self.request.query_params.get('date')
#         if date_param:
#             qs = qs.filter(date=date_param)
#         return qs.order_by('-date')

#     @action(detail=False, methods=['post'])
#     def bulk_create(self, request):
#         records = request.data.get('records', [])
#         results = []
#         for rec in records:
#             obj, created = Attendance.objects.update_or_create(
#                 student_id=rec['student_id'],
#                 date=rec['date'],
#                 defaults={
#                     'group_id': rec['group_id'],
#                     'is_present': rec['is_present'],
#                     'recorded_by': request.user,
#                 }
#             )
#             results.append({'id': obj.id, 'created': created})
#         return Response({'saved': len(results)})


# # ─── Grade ViewSet ────────────────────────────────────────────────────────────
# class GradeViewSet(viewsets.ModelViewSet):
#     queryset = Grade.objects.select_related('student__user', 'teacher')
#     serializer_class = GradeSerializer
#     permission_classes = [IsTeacher]

#     def perform_create(self, serializer):
#         serializer.save(teacher=self.request.user)

#     def get_queryset(self):
#         user = self.request.user
#         qs = super().get_queryset()
#         if user.role == 'teacher':
#             qs = qs.filter(teacher=user)
#         student_id = self.request.query_params.get('student')
#         if student_id:
#             qs = qs.filter(student_id=student_id)
#         return qs


# # ─── Reports ──────────────────────────────────────────────────────────────────
# class ReportViewSet(viewsets.ViewSet):
#     permission_classes = [IsAdmin]

#     @action(detail=False, methods=['get'])
#     def monthly_revenue(self, request):
#         data = (
#             Payment.objects
#             .annotate(payment_month=TruncMonth('payment_date'))
#             .values('payment_month')
#             .annotate(total=Sum('amount'), payment_count=Count('id'))
#             .order_by('-payment_month')[:6]
#         )
#         return Response(list(data))

#     @action(detail=False, methods=['get'])
#     def daily_revenue(self, request):
#         today = date.today()
#         data = (
#             Payment.objects
#             .filter(payment_date__year=today.year, payment_date__month=today.month)
#             .annotate(day=TruncDate('payment_date'))
#             .values('day')
#             .annotate(total=Sum('amount'), payment_count=Count('id'))
#             .order_by('-total')[:10]
#         )
#         return Response(list(data))

#     @action(detail=False, methods=['get'])
#     def debtors(self, request):
#         today = date.today()
#         current_month = date(today.year, today.month, 1)
#         paid_ids = Payment.objects.filter(month=current_month).values_list('student_id', flat=True)
#         debtors = StudentProfile.objects.exclude(id__in=paid_ids).select_related('user', 'group')
#         serializer = StudentProfileSerializer(debtors, many=True)
#         return Response(serializer.data)

#     @action(detail=False, methods=['get'])
#     def summary(self, request):
#         today = date.today()
#         current_month = date(today.year, today.month, 1)
#         monthly_revenue = Payment.objects.filter(
#             month=current_month
#         ).aggregate(total=Sum('amount'))['total'] or 0
#         return Response({
#             'total_students': StudentProfile.objects.count(),
#             'active_groups': Group.objects.filter(status='active').count(),
#             'monthly_revenue': float(monthly_revenue),
#             'debtors_count': StudentProfile.objects.exclude(
#                 payments__month=current_month
#             ).count(),
#         })














from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.db.models.functions import TruncMonth, TruncDate
from django.db.models import Sum, Count
from django.contrib.auth.hashers import make_password
from datetime import date

from .models import User, Group, StudentProfile, Payment, Attendance, Grade, Expense
from .serializers import (
    UserSerializer, GroupSerializer, StudentProfileSerializer,
    StudentSerializer, PaymentSerializer, AttendanceSerializer,
    GradeSerializer, ExpenseSerializer,
    _monthly_debt_rows,   # yordamchi funksiya
)


from rest_framework.views import APIView
from rest_framework.response import Response
# ─── JWT ──────────────────────────────────────────────────────────────────────
class CustomTokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        token['name'] = user.get_full_name()
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['role']    = self.user.role
        data['name']    = self.user.get_full_name()
        data['user_id'] = self.user.id
        return data


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenSerializer


# ─── Ruxsatlar ────────────────────────────────────────────────────────────────
class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


class IsTeacher(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ('admin', 'teacher')


# ─── Group ViewSet ────────────────────────────────────────────────────────────
class GroupViewSet(viewsets.ModelViewSet):
    queryset         = Group.objects.select_related('teacher').prefetch_related('students')
    serializer_class = GroupSerializer

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsAdmin()]
        return [permissions.IsAuthenticated()]

    @action(detail=True, methods=['get'])
    def students(self, request, pk=None):
        """GET /api/groups/{id}/students/"""
        group = self.get_object()
        qs    = group.students.select_related('user')
        return Response(StudentProfileSerializer(qs, many=True).data)


# ─── Teacher ViewSet ──────────────────────────────────────────────────────────
class TeacherViewSet(viewsets.ModelViewSet):
    queryset           = User.objects.filter(role='teacher')
    serializer_class   = UserSerializer
    permission_classes = [IsAdmin]

    def perform_create(self, serializer):
        serializer.save(
            role='teacher',
            password=make_password(self.request.data.get('password', '12345678')),
        )

    def perform_update(self, serializer):
        pw = self.request.data.get('password')
        serializer.save(password=make_password(pw)) if pw else serializer.save()


# ─── Student ViewSet ──────────────────────────────────────────────────────────
class StudentViewSet(viewsets.ModelViewSet):
    """
    GET    /api/students/                     – ro'yxat
    POST   /api/students/                     – yangi o'quvchi
    GET    /api/students/{id}/
    PUT/PATCH/DELETE /api/students/{id}/
    GET    /api/students/{id}/payments/       – to'lovlar tarixi
    GET    /api/students/{id}/monthly_debts/  – oylar bo'yicha qarz holati  ← YANGI
    GET    /api/students/{id}/attendance/
    GET    /api/students/{id}/grades/
    """

    def get_serializer_class(self):
        return UserSerializer if self.action == 'create' else StudentSerializer

    def get_queryset(self):
        user = self.request.user
        qs   = User.objects.filter(role='student').select_related(
            'student_profile__group'
        ).prefetch_related(
            'student_profile__payments',          # payment_status uchun
            'student_profile__attendance_records', # attendance_rate uchun
        )
        if user.role == 'teacher':
            qs = qs.filter(student_profile__group__teacher=user)
        elif user.role == 'student':
            qs = qs.filter(id=user.id)
        return qs

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsAdmin()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        data = self.request.data
        user = serializer.save(
            role='student',
            password=make_password(data.get('password', '12345678')),
        )
        StudentProfile.objects.create(
            user=user,
            group_id=data.get('group') or None,
            discount=data.get('discount', 0),
            payment_due_day=data.get('payment_due_day', 15),
        )

    # ── /api/students/{id}/payments/ ─────────────────────────────────────────
    @action(detail=True, methods=['get'])
    def payments(self, request, pk=None):
        """To'lovlar tarixi (barcha oylar)"""
        try:
            profile = self.get_object().student_profile
        except StudentProfile.DoesNotExist:
            return Response([])
        qs = Payment.objects.filter(student=profile).order_by('-payment_date', '-id')
        return Response(PaymentSerializer(qs, many=True).data)

    # ── /api/students/{id}/monthly_debts/ ────────────────────────────────────
    @action(detail=True, methods=['get'])
    def monthly_debts(self, request, pk=None):
        """
        Har bir oy bo'yicha to'lov holati.

        Response misoli:
        [
          {
            "month":    "2024-11-01",
            "expected": 500000.0,
            "paid":     300000.0,
            "debt":     200000.0,
            "overpaid": 0.0,
            "status":   "partial"   // paid | partial | overdue | pending
          },
          ...
        ]
        """
        try:
            profile = self.get_object().student_profile
        except StudentProfile.DoesNotExist:
            return Response([])
        return Response(_monthly_debt_rows(profile))

    # ── /api/students/{id}/attendance/ ───────────────────────────────────────
    @action(detail=True, methods=['get'])
    def attendance(self, request, pk=None):
        try:
            profile = self.get_object().student_profile
        except StudentProfile.DoesNotExist:
            return Response([])
        qs = Attendance.objects.filter(student=profile).order_by('-date')
        return Response(AttendanceSerializer(qs, many=True).data)

    # ── /api/students/{id}/grades/ ───────────────────────────────────────────
    @action(detail=True, methods=['get'])
    def grades(self, request, pk=None):
        try:
            profile = self.get_object().student_profile
        except StudentProfile.DoesNotExist:
            return Response([])
        qs = Grade.objects.filter(student=profile).order_by('-date')
        return Response(GradeSerializer(qs, many=True).data)


# ─── Payment ViewSet ──────────────────────────────────────────────────────────
class PaymentViewSet(viewsets.ModelViewSet):
    """
    Bo'lib-bo'lib to'lash. Bir oyga bir necha marta to'lov mumkin.

    POST body: { student: <User.id>, amount: ..., month: "2024-11-01" }
      ↑ Frontend StudentSerializer ro'yxatidan s.id (User.id) yuboradi.
        Biz bu yerda User.id → StudentProfile ga aylantiramiz.

    Filtrlar:
      ?month=2024-11   → faqat shu oy to'lovlari
      ?group=<id>      → faqat shu guruh
      ?student=<id>    → faqat shu o'quvchi (User.id bo'yicha)
    """
    queryset           = Payment.objects.select_related('student__user', 'student__group')
    serializer_class   = PaymentSerializer
    permission_classes = [IsAdmin]

    def create(self, request, *args, **kwargs):
        """
        Frontend s.id = User.id yuboradi.
        Payment.student → StudentProfile FK, shuning uchun bu yerda
        User.id → StudentProfile.id ga aylantiramiz.
        """
        data    = request.data.copy()
        user_id = data.get('student')

        try:
            profile = StudentProfile.objects.get(user_id=user_id)
        except StudentProfile.DoesNotExist:
            return Response(
                {'student': [f"ID={user_id} bo'lgan o'quvchi topilmadi."]},
                status=400,
            )

        data['student'] = profile.id   # User.id → StudentProfile.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=request.user)
        return Response(serializer.data, status=201)

    def get_queryset(self):
        qs         = super().get_queryset().order_by('-payment_date', '-id')
        month      = self.request.query_params.get('month')      # "2024-11"
        group_id   = self.request.query_params.get('group')
        student_id = self.request.query_params.get('student')    # StudentProfile.id

        if month:
            # "2024-11" → year=2024, month=11
            try:
                y, m = month.split('-')
                qs = qs.filter(month__year=int(y), month__month=int(m))
            except ValueError:
                pass
        if group_id:
            qs = qs.filter(student__group_id=group_id)
        if student_id:
            # student_id = User.id bo'lishi mumkin, user__id orqali qidiramiz
            qs = qs.filter(student__user_id=student_id)
        return qs


# ─── Attendance ViewSet ───────────────────────────────────────────────────────
class AttendanceViewSet(viewsets.ModelViewSet):
    queryset           = Attendance.objects.select_related('student__user', 'group')
    serializer_class   = AttendanceSerializer
    permission_classes = [IsTeacher]

    def get_queryset(self):
        user       = self.request.user
        qs         = super().get_queryset()
        if user.role == 'teacher':
            qs = qs.filter(group__teacher=user)
        group_id   = self.request.query_params.get('group')
        date_param = self.request.query_params.get('date')
        if group_id:
            qs = qs.filter(group_id=group_id)
        if date_param:
            qs = qs.filter(date=date_param)
        return qs.order_by('-date')

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """
        POST /api/attendance/bulk_create/
        { "records": [{ "student_id", "date", "group_id", "is_present" }] }
        """
        records = request.data.get('records', [])
        saved   = []
        for rec in records:
            obj, created = Attendance.objects.update_or_create(
                student_id=rec['student_id'],
                date=rec['date'],
                defaults={
                    'group_id':    rec['group_id'],
                    'is_present':  rec['is_present'],
                    'recorded_by': request.user,
                },
            )
            saved.append({'id': obj.id, 'created': created})
        return Response({'saved': len(saved)})


# ─── Grade ViewSet ────────────────────────────────────────────────────────────
class GradeViewSet(viewsets.ModelViewSet):
    queryset           = Grade.objects.select_related('student__user', 'teacher')
    serializer_class   = GradeSerializer
    permission_classes = [IsTeacher]

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)

    def get_queryset(self):
        user       = self.request.user
        qs         = super().get_queryset()
        if user.role == 'teacher':
            qs = qs.filter(teacher=user)
        student_id = self.request.query_params.get('student')
        if student_id:
            # student_id = User.id bo'lishi mumkin, user__id orqali qidiramiz
            qs = qs.filter(student__user_id=student_id)
        return qs


# ─── Expense ViewSet ──────────────────────────────────────────────────────────
class ExpenseViewSet(viewsets.ModelViewSet):
    """
    GET    /api/expenses/           – bu oygi xarajatlar (?all=1 barchasi)
    POST   /api/expenses/           – yangi xarajat
    DELETE /api/expenses/{id}/
    GET    /api/expenses/summary/   – bu oy jami + kategoriya bo'yicha
    GET    /api/expenses/monthly/   – oxirgi 6 oy dinamikasi
    """
    queryset           = Expense.objects.all()
    serializer_class   = ExpenseSerializer
    permission_classes = [IsAdmin]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def get_queryset(self):
        qs       = super().get_queryset()
        all_     = self.request.query_params.get('all')
        month    = self.request.query_params.get('month')
        category = self.request.query_params.get('category')
        if month:
            qs = qs.filter(expense_date__startswith=month)
        elif not all_:
            today = date.today()
            qs = qs.filter(expense_date__year=today.year, expense_date__month=today.month)
        if category:
            qs = qs.filter(category=category)
        return qs

    @action(detail=False, methods=['get'])
    def summary(self, request):
        today       = date.today()
        qs          = Expense.objects.filter(
            expense_date__year=today.year, expense_date__month=today.month
        )
        month_total = qs.aggregate(total=Sum('amount'))['total'] or 0
        by_category = list(qs.values('category').annotate(total=Sum('amount')).order_by('-total'))
        return Response({'month_total': float(month_total), 'by_category': by_category})

    @action(detail=False, methods=['get'])
    def monthly(self, request):
        data = (
            Expense.objects
            .annotate(m=TruncMonth('expense_date'))
            .values('m')
            .annotate(total=Sum('amount'), count=Count('id'))
            .order_by('-m')[:6]
        )
        return Response(list(data))


# ─── Report ViewSet ───────────────────────────────────────────────────────────
class ReportViewSet(viewsets.ViewSet):
    permission_classes = [IsAdmin]

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        /api/reports/summary/
        total_students, active_groups, monthly_revenue,
        monthly_expenses, net_profit, debtors_count
        """
        today         = date.today()
        current_month = date(today.year, today.month, 1)

        monthly_revenue = float(
            Payment.objects.filter(month=current_month)
            .aggregate(total=Sum('amount'))['total'] or 0
        )
        monthly_expenses = float(
            Expense.objects.filter(
                expense_date__year=today.year, expense_date__month=today.month
            ).aggregate(total=Sum('amount'))['total'] or 0
        )
        # Qarzdorlar: bu oy uchun to'liq to'lamagan o'quvchilar
        paid_ids      = Payment.objects.filter(
            month__year=today.year, month__month=today.month
        ).values_list('student_id', flat=True)
        debtors_count = StudentProfile.objects.exclude(id__in=paid_ids).count()

        return Response({
            'total_students':   StudentProfile.objects.count(),
            'active_groups':    Group.objects.filter(status='active').count(),
            'monthly_revenue':  monthly_revenue,
            'monthly_expenses': monthly_expenses,
            'net_profit':       monthly_revenue - monthly_expenses,
            'debtors_count':    debtors_count,
        })

    @action(detail=False, methods=['get'])
    def monthly_revenue(self, request):
        """Oxirgi 6 oylik tushum dinamikasi"""
        data = (
            Payment.objects
            .annotate(payment_month=TruncMonth('payment_date'))
            .values('payment_month')
            .annotate(total=Sum('amount'), payment_count=Count('id'))
            .order_by('-payment_month')[:6]
        )
        return Response(list(data))

    @action(detail=False, methods=['get'])
    def daily_revenue(self, request):
        """Bu oyning kunlik tushum top-10"""
        today = date.today()
        data  = (
            Payment.objects
            .filter(payment_date__year=today.year, payment_date__month=today.month)
            .annotate(day=TruncDate('payment_date'))
            .values('day')
            .annotate(total=Sum('amount'), payment_count=Count('id'))
            .order_by('-total')[:10]
        )
        return Response(list(data))

    @action(detail=False, methods=['get'])
    def debtors(self, request):
        """
        Bu oy to'lov qilmagan o'quvchilar.
        Har bir o'quvchi uchun monthly_debts ham qaytariladi.
        """
        today         = date.today()
        current_month = date(today.year, today.month, 1)

        # Bu oy hech narsa to'lamagan yoki to'liq to'lamagan profillar
        paid_full_ids = Payment.objects.filter(
            month=current_month
        ).values('student_id').annotate(
            paid=Sum('amount')
        )
        # Qulaylik uchun: to'liq to'lamaganlarni StudentProfileSerializer bilan qaytaramiz
        debtors = StudentProfile.objects.exclude(
            id__in=[
                r['student_id'] for r in paid_full_ids
                # (to'liq tekshirish monthly_debts action orqali qilinadi)
            ]
        ).select_related('user', 'group')

        serializer = StudentProfileSerializer(debtors, many=True)
        return Response(serializer.data)



class SeedView(APIView):
    """
    GET /api/seed/  →  demo ma'lumotlar yaratadi (faqat admin uchun).
    Haqiqiy hisobot /api/reports/summary/ orqali ReportViewSet.summary da.
    """
    permission_classes = [IsAdmin]

    def get(self, request, format=None):
        from datetime import date, timedelta
        from decimal import Decimal
        import random


        # =========================
        # USERS
        # =========================

        teachers_data = [
            ("Jamshid", "Karimov"),
            ("Dilshod", "Rasulov"),
            ("Aziz", "Toshpo'latov"),
            ("Sardor", "Qodirov"),
            ("Bekzod", "Yo'ldoshev"),
        ]

        students_data = [
            ("Ali", "Valiyev"),
            ("Hasan", "Karimov"),
            ("Husan", "Sobirov"),
            ("Muhammad", "Rahimov"),
            ("Javohir", "Usmonov"),
            ("Akmal", "Tursunov"),
            ("Sherzod", "Aliyev"),
            ("Oybek", "Qobilov"),
            ("Farrux", "Sodiqov"),
            ("Temur", "Nazarov"),
        ]

        admin_user, _ = User.objects.get_or_create(
            username="admin",
            defaults={
                "first_name": "Super",
                "last_name": "Admin",
                "role": "admin",
                "phone": "+998901112233",
                "password": make_password("admin123"),
            }
        )

        teachers = []

        for i, (first, last) in enumerate(teachers_data, start=1):
            teacher, created = User.objects.get_or_create(
                username=f"teacher{i}",
                defaults={
                    "first_name": first,
                    "last_name": last,
                    "role": "teacher",
                    "phone": f"+99890{i}111111",
                    "password": make_password("teacher123"),
                }
            )
            teachers.append(teacher)

        students = []

        for i, (first, last) in enumerate(students_data, start=1):
            student, created = User.objects.get_or_create(
                username=f"student{i}",
                defaults={
                    "first_name": first,
                    "last_name": last,
                    "role": "student",
                    "phone": f"+99891{i}222222",
                    "password": make_password("student123"),
                }
            )
            students.append(student)


        # =========================
        # GROUPS
        # =========================

        group_names = [
            "Python Beginner",
            "Python Intermediate",
            "Frontend React",
            "IELTS Foundation",
            "Math Advanced",
            "Backend Django",
            "AI Basics",
            "Robotics Kids",
            "SAT Math",
            "English Speaking",
        ]

        subjects = [
            "Python",
            "Python",
            "Frontend",
            "English",
            "Math",
            "Django",
            "AI",
            "Robotics",
            "Math",
            "English",
        ]

        groups = []

        for i in range(10):
            group, created = Group.objects.get_or_create(
                name=group_names[i],
                defaults={
                    "teacher": random.choice(teachers),
                    "subject": subjects[i],
                    "schedule": "Du-Chor-Juma 18:00",
                    "monthly_fee": Decimal(random.randint(300000, 800000)),
                    "start_date": date.today() - timedelta(days=random.randint(10, 100)),
                    "status": "active",
                }
            )
            groups.append(group)


        # =========================
        # STUDENT PROFILES
        # =========================

        profiles = []

        for student in students:
            profile, created = StudentProfile.objects.get_or_create(
                user=student,
                defaults={
                    "group": random.choice(groups),
                    "discount": random.choice([0, 5, 10, 15]),
                    "payment_due_day": random.randint(1, 28),
                }
            )
            profiles.append(profile)


        # =========================
        # PAYMENTS
        # =========================

        for i in range(10):
            Payment.objects.create(
                student=random.choice(profiles),
                amount=Decimal(random.randint(200000, 800000)),
                payment_date=date.today() - timedelta(days=random.randint(1, 30)),
                month=date.today().replace(day=1),
                note="Oylik to'lov",
                created_by=admin_user,
            )


        # =========================
        # ATTENDANCE
        # =========================

        for i in range(10):
            student_profile = random.choice(profiles)

            Attendance.objects.get_or_create(
                student=student_profile,
                date=date.today() - timedelta(days=i),
                defaults={
                    "group": student_profile.group,
                    "is_present": random.choice([True, False]),
                    "note": "Dars holati",
                    "recorded_by": random.choice(teachers),
                }
            )


        # =========================
        # GRADES
        # =========================

        topics = [
            "Variables",
            "Functions",
            "Loops",
            "OOP",
            "HTML",
            "CSS",
            "React",
            "Math Test",
            "Grammar",
            "Vocabulary",
        ]

        for i in range(10):
            Grade.objects.create(
                student=random.choice(profiles),
                teacher=random.choice(teachers),
                topic=topics[i],
                score=random.randint(60, 100),
                note="Yaxshi natija",
            )


        # =========================
        # EXPENSES
        # =========================

        expense_titles = [
            "O'qituvchi maoshi",
            "Internet to'lovi",
            "Ijara puli",
            "Projektor xaridi",
            "Reklama xarajati",
            "Stol xaridi",
            "Elektr energiyasi",
            "Konditsioner ta'miri",
            "Printer qog'ozi",
            "Ofis xarajatlari",
        ]

        categories = [
            "salary",
            "utility",
            "rent",
            "equipment",
            "marketing",
            "equipment",
            "utility",
            "other",
            "other",
            "other",
        ]

        for i in range(10):
            Expense.objects.create(
                title=expense_titles[i],
                category=categories[i],
                amount=Decimal(random.randint(100000, 5000000)),
                expense_date=date.today() - timedelta(days=random.randint(1, 60)),
                note="Test xarajat",
                created_by=admin_user,
    )

        return Response({"message": "Demo data muvaffaqiyatli yaratildi!"})












# from rest_framework import viewsets, permissions
# from rest_framework.decorators import action
# from rest_framework.response import Response
# from rest_framework_simplejwt.views import TokenObtainPairView
# from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
# from django.db.models.functions import TruncMonth, TruncDate
# from django.db.models import Sum, Count
# from django.contrib.auth.hashers import make_password
# from datetime import date

# from .models import User, Group, StudentProfile, Payment, Attendance, Grade, Expense
# from .serializers import (
#     UserSerializer, GroupSerializer, StudentProfileSerializer,
#     StudentSerializer, PaymentSerializer, AttendanceSerializer,
#     GradeSerializer, ExpenseSerializer,
#     _monthly_debt_rows,   # yordamchi funksiya
# )


# from rest_framework.views import APIView
# from rest_framework.response import Response
# # ─── JWT ──────────────────────────────────────────────────────────────────────
# class CustomTokenSerializer(TokenObtainPairSerializer):
#     @classmethod
#     def get_token(cls, user):
#         token = super().get_token(user)
#         token['role'] = user.role
#         token['name'] = user.get_full_name()
#         return token

#     def validate(self, attrs):
#         data = super().validate(attrs)
#         data['role']    = self.user.role
#         data['name']    = self.user.get_full_name()
#         data['user_id'] = self.user.id
#         return data


# class LoginView(TokenObtainPairView):
#     serializer_class = CustomTokenSerializer


# # ─── Ruxsatlar ────────────────────────────────────────────────────────────────
# class IsAdmin(permissions.BasePermission):
#     def has_permission(self, request, view):
#         return request.user.is_authenticated and request.user.role == 'admin'


# class IsTeacher(permissions.BasePermission):
#     def has_permission(self, request, view):
#         return request.user.is_authenticated and request.user.role in ('admin', 'teacher')


# # ─── Group ViewSet ────────────────────────────────────────────────────────────
# class GroupViewSet(viewsets.ModelViewSet):
#     queryset         = Group.objects.select_related('teacher').prefetch_related('students')
#     serializer_class = GroupSerializer

#     def get_permissions(self):
#         if self.action in ('create', 'update', 'partial_update', 'destroy'):
#             return [IsAdmin()]
#         return [permissions.IsAuthenticated()]

#     @action(detail=True, methods=['get'])
#     def students(self, request, pk=None):
#         """GET /api/groups/{id}/students/"""
#         group = self.get_object()
#         qs    = group.students.select_related('user')
#         return Response(StudentProfileSerializer(qs, many=True).data)


# # ─── Teacher ViewSet ──────────────────────────────────────────────────────────
# class TeacherViewSet(viewsets.ModelViewSet):
#     queryset           = User.objects.filter(role='teacher')
#     serializer_class   = UserSerializer
#     permission_classes = [IsAdmin]

#     def perform_create(self, serializer):
#         serializer.save(
#             role='teacher',
#             password=make_password(self.request.data.get('password', '12345678')),
#         )

#     def perform_update(self, serializer):
#         pw = self.request.data.get('password')
#         serializer.save(password=make_password(pw)) if pw else serializer.save()


# # ─── Student ViewSet ──────────────────────────────────────────────────────────
# class StudentViewSet(viewsets.ModelViewSet):
#     """
#     GET    /api/students/                     – ro'yxat
#     POST   /api/students/                     – yangi o'quvchi
#     GET    /api/students/{id}/
#     PUT/PATCH/DELETE /api/students/{id}/
#     GET    /api/students/{id}/payments/       – to'lovlar tarixi
#     GET    /api/students/{id}/monthly_debts/  – oylar bo'yicha qarz holati  ← YANGI
#     GET    /api/students/{id}/attendance/
#     GET    /api/students/{id}/grades/
#     """

#     def get_serializer_class(self):
#         return UserSerializer if self.action == 'create' else StudentSerializer

#     def get_queryset(self):
#         user = self.request.user
#         qs   = User.objects.filter(role='student').select_related('student_profile__group')
#         if user.role == 'teacher':
#             qs = qs.filter(student_profile__group__teacher=user)
#         elif user.role == 'student':
#             qs = qs.filter(id=user.id)
#         return qs

#     def get_permissions(self):
#         if self.action in ('create', 'update', 'partial_update', 'destroy'):
#             return [IsAdmin()]
#         return [permissions.IsAuthenticated()]

#     def perform_create(self, serializer):
#         data = self.request.data
#         user = serializer.save(
#             role='student',
#             password=make_password(data.get('password', '12345678')),
#         )
#         StudentProfile.objects.create(
#             user=user,
#             group_id=data.get('group') or None,
#             discount=data.get('discount', 0),
#             payment_due_day=data.get('payment_due_day', 15),
#         )

#     # ── /api/students/{id}/payments/ ─────────────────────────────────────────
#     @action(detail=True, methods=['get'])
#     def payments(self, request, pk=None):
#         """To'lovlar tarixi (barcha oylar)"""
#         try:
#             profile = self.get_object().student_profile
#         except StudentProfile.DoesNotExist:
#             return Response([])
#         qs = Payment.objects.filter(student=profile).order_by('-payment_date', '-id')
#         return Response(PaymentSerializer(qs, many=True).data)

#     # ── /api/students/{id}/monthly_debts/ ────────────────────────────────────
#     @action(detail=True, methods=['get'])
#     def monthly_debts(self, request, pk=None):
#         """
#         Har bir oy bo'yicha to'lov holati.

#         Response misoli:
#         [
#           {
#             "month":    "2024-11-01",
#             "expected": 500000.0,
#             "paid":     300000.0,
#             "debt":     200000.0,
#             "overpaid": 0.0,
#             "status":   "partial"   // paid | partial | overdue | pending
#           },
#           ...
#         ]
#         """
#         try:
#             profile = self.get_object().student_profile
#         except StudentProfile.DoesNotExist:
#             return Response([])
#         return Response(_monthly_debt_rows(profile))

#     # ── /api/students/{id}/attendance/ ───────────────────────────────────────
#     @action(detail=True, methods=['get'])
#     def attendance(self, request, pk=None):
#         try:
#             profile = self.get_object().student_profile
#         except StudentProfile.DoesNotExist:
#             return Response([])
#         qs = Attendance.objects.filter(student=profile).order_by('-date')
#         return Response(AttendanceSerializer(qs, many=True).data)

#     # ── /api/students/{id}/grades/ ───────────────────────────────────────────
#     @action(detail=True, methods=['get'])
#     def grades(self, request, pk=None):
#         try:
#             profile = self.get_object().student_profile
#         except StudentProfile.DoesNotExist:
#             return Response([])
#         qs = Grade.objects.filter(student=profile).order_by('-date')
#         return Response(GradeSerializer(qs, many=True).data)


# # ─── Payment ViewSet ──────────────────────────────────────────────────────────
# class PaymentViewSet(viewsets.ModelViewSet):
#     """
#     Bo'lib-bo'lib to'lash. Bir oyga bir necha marta to'lov mumkin.

#     POST body: { student: <User.id>, amount: ..., month: "2024-11-01" }
#       ↑ Frontend StudentSerializer ro'yxatidan s.id (User.id) yuboradi.
#         Biz bu yerda User.id → StudentProfile ga aylantiramiz.

#     Filtrlar:
#       ?month=2024-11   → faqat shu oy to'lovlari
#       ?group=<id>      → faqat shu guruh
#       ?student=<id>    → faqat shu o'quvchi (User.id bo'yicha)
#     """
#     queryset           = Payment.objects.select_related('student__user', 'student__group')
#     serializer_class   = PaymentSerializer
#     permission_classes = [IsAdmin]

#     def create(self, request, *args, **kwargs):
#         """
#         Frontend s.id = User.id yuboradi.
#         Payment.student → StudentProfile FK, shuning uchun bu yerda
#         User.id → StudentProfile.id ga aylantiramiz.
#         """
#         data    = request.data.copy()
#         user_id = data.get('student')

#         try:
#             profile = StudentProfile.objects.get(user_id=user_id)
#         except StudentProfile.DoesNotExist:
#             return Response(
#                 {'student': [f"ID={user_id} bo'lgan o'quvchi topilmadi."]},
#                 status=400,
#             )

#         data['student'] = profile.id   # User.id → StudentProfile.id
#         serializer = self.get_serializer(data=data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save(created_by=request.user)
#         return Response(serializer.data, status=201)

#     def get_queryset(self):
#         qs         = super().get_queryset().order_by('-payment_date', '-id')
#         month      = self.request.query_params.get('month')      # "2024-11"
#         group_id   = self.request.query_params.get('group')
#         student_id = self.request.query_params.get('student')    # StudentProfile.id

#         if month:
#             # "2024-11" → year=2024, month=11
#             try:
#                 y, m = month.split('-')
#                 qs = qs.filter(month__year=int(y), month__month=int(m))
#             except ValueError:
#                 pass
#         if group_id:
#             qs = qs.filter(student__group_id=group_id)
#         if student_id:
#             # student_id = User.id bo'lishi mumkin, user__id orqali qidiramiz
#             qs = qs.filter(student__user_id=student_id)
#         return qs


# # ─── Attendance ViewSet ───────────────────────────────────────────────────────
# class AttendanceViewSet(viewsets.ModelViewSet):
#     queryset           = Attendance.objects.select_related('student__user', 'group')
#     serializer_class   = AttendanceSerializer
#     permission_classes = [IsTeacher]

#     def get_queryset(self):
#         user       = self.request.user
#         qs         = super().get_queryset()
#         if user.role == 'teacher':
#             qs = qs.filter(group__teacher=user)
#         group_id   = self.request.query_params.get('group')
#         date_param = self.request.query_params.get('date')
#         if group_id:
#             qs = qs.filter(group_id=group_id)
#         if date_param:
#             qs = qs.filter(date=date_param)
#         return qs.order_by('-date')

#     @action(detail=False, methods=['post'])
#     def bulk_create(self, request):
#         """
#         POST /api/attendance/bulk_create/
#         { "records": [{ "student_id", "date", "group_id", "is_present" }] }
#         """
#         records = request.data.get('records', [])
#         saved   = []
#         for rec in records:
#             obj, created = Attendance.objects.update_or_create(
#                 student_id=rec['student_id'],
#                 date=rec['date'],
#                 defaults={
#                     'group_id':    rec['group_id'],
#                     'is_present':  rec['is_present'],
#                     'recorded_by': request.user,
#                 },
#             )
#             saved.append({'id': obj.id, 'created': created})
#         return Response({'saved': len(saved)})


# # ─── Grade ViewSet ────────────────────────────────────────────────────────────
# class GradeViewSet(viewsets.ModelViewSet):
#     queryset           = Grade.objects.select_related('student__user', 'teacher')
#     serializer_class   = GradeSerializer
#     permission_classes = [IsTeacher]

#     def perform_create(self, serializer):
#         serializer.save(teacher=self.request.user)

#     def get_queryset(self):
#         user       = self.request.user
#         qs         = super().get_queryset()
#         if user.role == 'teacher':
#             qs = qs.filter(teacher=user)
#         student_id = self.request.query_params.get('student')
#         if student_id:
#             # student_id = User.id bo'lishi mumkin, user__id orqali qidiramiz
#             qs = qs.filter(student__user_id=student_id)
#         return qs


# # ─── Expense ViewSet ──────────────────────────────────────────────────────────
# class ExpenseViewSet(viewsets.ModelViewSet):
#     """
#     GET    /api/expenses/           – bu oygi xarajatlar (?all=1 barchasi)
#     POST   /api/expenses/           – yangi xarajat
#     DELETE /api/expenses/{id}/
#     GET    /api/expenses/summary/   – bu oy jami + kategoriya bo'yicha
#     GET    /api/expenses/monthly/   – oxirgi 6 oy dinamikasi
#     """
#     queryset           = Expense.objects.all()
#     serializer_class   = ExpenseSerializer
#     permission_classes = [IsAdmin]

#     def perform_create(self, serializer):
#         serializer.save(created_by=self.request.user)

#     def get_queryset(self):
#         qs       = super().get_queryset()
#         all_     = self.request.query_params.get('all')
#         month    = self.request.query_params.get('month')
#         category = self.request.query_params.get('category')
#         if month:
#             qs = qs.filter(expense_date__startswith=month)
#         elif not all_:
#             today = date.today()
#             qs = qs.filter(expense_date__year=today.year, expense_date__month=today.month)
#         if category:
#             qs = qs.filter(category=category)
#         return qs

#     @action(detail=False, methods=['get'])
#     def summary(self, request):
#         today       = date.today()
#         qs          = Expense.objects.filter(
#             expense_date__year=today.year, expense_date__month=today.month
#         )
#         month_total = qs.aggregate(total=Sum('amount'))['total'] or 0
#         by_category = list(qs.values('category').annotate(total=Sum('amount')).order_by('-total'))
#         return Response({'month_total': float(month_total), 'by_category': by_category})

#     @action(detail=False, methods=['get'])
#     def monthly(self, request):
#         data = (
#             Expense.objects
#             .annotate(m=TruncMonth('expense_date'))
#             .values('m')
#             .annotate(total=Sum('amount'), count=Count('id'))
#             .order_by('-m')[:6]
#         )
#         return Response(list(data))


# # ─── Report ViewSet ───────────────────────────────────────────────────────────
# class ReportViewSet(viewsets.ViewSet):
#     permission_classes = [IsAdmin]

#     @action(detail=False, methods=['get'])
#     def summary(self, request):
#         """
#         /api/reports/summary/
#         total_students, active_groups, monthly_revenue,
#         monthly_expenses, net_profit, debtors_count
#         """
#         today         = date.today()
#         current_month = date(today.year, today.month, 1)

#         monthly_revenue = float(
#             Payment.objects.filter(month=current_month)
#             .aggregate(total=Sum('amount'))['total'] or 0
#         )
#         monthly_expenses = float(
#             Expense.objects.filter(
#                 expense_date__year=today.year, expense_date__month=today.month
#             ).aggregate(total=Sum('amount'))['total'] or 0
#         )
#         # Qarzdorlar: bu oy uchun to'liq to'lamagan o'quvchilar
#         paid_ids      = Payment.objects.filter(
#             month__year=today.year, month__month=today.month
#         ).values_list('student_id', flat=True)
#         debtors_count = StudentProfile.objects.exclude(id__in=paid_ids).count()

#         return Response({
#             'total_students':   StudentProfile.objects.count(),
#             'active_groups':    Group.objects.filter(status='active').count(),
#             'monthly_revenue':  monthly_revenue,
#             'monthly_expenses': monthly_expenses,
#             'net_profit':       monthly_revenue - monthly_expenses,
#             'debtors_count':    debtors_count,
#         })

#     @action(detail=False, methods=['get'])
#     def monthly_revenue(self, request):
#         """Oxirgi 6 oylik tushum dinamikasi"""
#         data = (
#             Payment.objects
#             .annotate(payment_month=TruncMonth('payment_date'))
#             .values('payment_month')
#             .annotate(total=Sum('amount'), payment_count=Count('id'))
#             .order_by('-payment_month')[:6]
#         )
#         return Response(list(data))

#     @action(detail=False, methods=['get'])
#     def daily_revenue(self, request):
#         """Bu oyning kunlik tushum top-10"""
#         today = date.today()
#         data  = (
#             Payment.objects
#             .filter(payment_date__year=today.year, payment_date__month=today.month)
#             .annotate(day=TruncDate('payment_date'))
#             .values('day')
#             .annotate(total=Sum('amount'), payment_count=Count('id'))
#             .order_by('-total')[:10]
#         )
#         return Response(list(data))

#     @action(detail=False, methods=['get'])
#     def debtors(self, request):
#         """
#         Bu oy to'lov qilmagan o'quvchilar.
#         Har bir o'quvchi uchun monthly_debts ham qaytariladi.
#         """
#         today         = date.today()
#         current_month = date(today.year, today.month, 1)

#         # Bu oy hech narsa to'lamagan yoki to'liq to'lamagan profillar
#         paid_full_ids = Payment.objects.filter(
#             month=current_month
#         ).values('student_id').annotate(
#             paid=Sum('amount')
#         )
#         # Qulaylik uchun: to'liq to'lamaganlarni StudentProfileSerializer bilan qaytaramiz
#         debtors = StudentProfile.objects.exclude(
#             id__in=[
#                 r['student_id'] for r in paid_full_ids
#                 # (to'liq tekshirish monthly_debts action orqali qilinadi)
#             ]
#         ).select_related('user', 'group')

#         serializer = StudentProfileSerializer(debtors, many=True)
#         return Response(serializer.data)



# class ReportView(APIView):
#     permission_classes = [IsAdmin]

#     def get(self, request, format=None):
#         from datetime import date, timedelta
#         from decimal import Decimal
#         import random


#         # =========================
#         # USERS
#         # =========================

#         teachers_data = [
#             ("Jamshid", "Karimov"),
#             ("Dilshod", "Rasulov"),
#             ("Aziz", "Toshpo'latov"),
#             ("Sardor", "Qodirov"),
#             ("Bekzod", "Yo'ldoshev"),
#         ]

#         students_data = [
#             ("Ali", "Valiyev"),
#             ("Hasan", "Karimov"),
#             ("Husan", "Sobirov"),
#             ("Muhammad", "Rahimov"),
#             ("Javohir", "Usmonov"),
#             ("Akmal", "Tursunov"),
#             ("Sherzod", "Aliyev"),
#             ("Oybek", "Qobilov"),
#             ("Farrux", "Sodiqov"),
#             ("Temur", "Nazarov"),
#         ]

#         admin_user, _ = User.objects.get_or_create(
#             username="admin",
#             defaults={
#                 "first_name": "Super",
#                 "last_name": "Admin",
#                 "role": "admin",
#                 "phone": "+998901112233",
#                 "password": make_password("admin123"),
#             }
#         )

#         teachers = []

#         for i, (first, last) in enumerate(teachers_data, start=1):
#             teacher, created = User.objects.get_or_create(
#                 username=f"teacher{i}",
#                 defaults={
#                     "first_name": first,
#                     "last_name": last,
#                     "role": "teacher",
#                     "phone": f"+99890{i}111111",
#                     "password": make_password("teacher123"),
#                 }
#             )
#             teachers.append(teacher)

#         students = []

#         for i, (first, last) in enumerate(students_data, start=1):
#             student, created = User.objects.get_or_create(
#                 username=f"student{i}",
#                 defaults={
#                     "first_name": first,
#                     "last_name": last,
#                     "role": "student",
#                     "phone": f"+99891{i}222222",
#                     "password": make_password("student123"),
#                 }
#             )
#             students.append(student)


#         # =========================
#         # GROUPS
#         # =========================

#         group_names = [
#             "Python Beginner",
#             "Python Intermediate",
#             "Frontend React",
#             "IELTS Foundation",
#             "Math Advanced",
#             "Backend Django",
#             "AI Basics",
#             "Robotics Kids",
#             "SAT Math",
#             "English Speaking",
#         ]

#         subjects = [
#             "Python",
#             "Python",
#             "Frontend",
#             "English",
#             "Math",
#             "Django",
#             "AI",
#             "Robotics",
#             "Math",
#             "English",
#         ]

#         groups = []

#         for i in range(10):
#             group, created = Group.objects.get_or_create(
#                 name=group_names[i],
#                 defaults={
#                     "teacher": random.choice(teachers),
#                     "subject": subjects[i],
#                     "schedule": "Du-Chor-Juma 18:00",
#                     "monthly_fee": Decimal(random.randint(300000, 800000)),
#                     "start_date": date.today() - timedelta(days=random.randint(10, 100)),
#                     "status": "active",
#                 }
#             )
#             groups.append(group)


#         # =========================
#         # STUDENT PROFILES
#         # =========================

#         profiles = []

#         for student in students:
#             profile, created = StudentProfile.objects.get_or_create(
#                 user=student,
#                 defaults={
#                     "group": random.choice(groups),
#                     "discount": random.choice([0, 5, 10, 15]),
#                     "payment_due_day": random.randint(1, 28),
#                 }
#             )
#             profiles.append(profile)


#         # =========================
#         # PAYMENTS
#         # =========================

#         for i in range(10):
#             Payment.objects.create(
#                 student=random.choice(profiles),
#                 amount=Decimal(random.randint(200000, 800000)),
#                 payment_date=date.today() - timedelta(days=random.randint(1, 30)),
#                 month=date.today().replace(day=1),
#                 note="Oylik to'lov",
#                 created_by=admin_user,
#             )


#         # =========================
#         # ATTENDANCE
#         # =========================

#         for i in range(10):
#             student_profile = random.choice(profiles)

#             Attendance.objects.get_or_create(
#                 student=student_profile,
#                 date=date.today() - timedelta(days=i),
#                 defaults={
#                     "group": student_profile.group,
#                     "is_present": random.choice([True, False]),
#                     "note": "Dars holati",
#                     "recorded_by": random.choice(teachers),
#                 }
#             )


#         # =========================
#         # GRADES
#         # =========================

#         topics = [
#             "Variables",
#             "Functions",
#             "Loops",
#             "OOP",
#             "HTML",
#             "CSS",
#             "React",
#             "Math Test",
#             "Grammar",
#             "Vocabulary",
#         ]

#         for i in range(10):
#             Grade.objects.create(
#                 student=random.choice(profiles),
#                 teacher=random.choice(teachers),
#                 topic=topics[i],
#                 score=random.randint(60, 100),
#                 note="Yaxshi natija",
#             )


#         # =========================
#         # EXPENSES
#         # =========================

#         expense_titles = [
#             "O'qituvchi maoshi",
#             "Internet to'lovi",
#             "Ijara puli",
#             "Projektor xaridi",
#             "Reklama xarajati",
#             "Stol xaridi",
#             "Elektr energiyasi",
#             "Konditsioner ta'miri",
#             "Printer qog'ozi",
#             "Ofis xarajatlari",
#         ]

#         categories = [
#             "salary",
#             "utility",
#             "rent",
#             "equipment",
#             "marketing",
#             "equipment",
#             "utility",
#             "other",
#             "other",
#             "other",
#         ]

#         for i in range(10):
#             Expense.objects.create(
#                 title=expense_titles[i],
#                 category=categories[i],
#                 amount=Decimal(random.randint(100000, 5000000)),
#                 expense_date=date.today() - timedelta(days=random.randint(1, 60)),
#                 note="Test xarajat",
#                 created_by=admin_user,
#     )

#         return Response({"message": "Demo data muvaffaqiyatli yaratildi!"})