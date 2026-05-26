# from rest_framework import serializers
# from django.db.models import Sum, Count, Avg
# from .models import User, Group, StudentProfile, Payment, Attendance, Grade
# from datetime import date
# from django.db.models import Q
# import calendar

# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['id', 'username', 'first_name', 'last_name', 'role', 'phone', 'email']


# class GroupSerializer(serializers.ModelSerializer):
#     teacher_name = serializers.SerializerMethodField()
#     student_count = serializers.SerializerMethodField()

#     def get_teacher_name(self, obj):
#         return obj.teacher.get_full_name() if obj.teacher else None

#     def get_student_count(self, obj):
#         return obj.students.count()

#     class Meta:
#         model = Group
#         fields = ['id', 'name', 'teacher', 'teacher_name', 'subject',
#                   'schedule', 'monthly_fee', 'start_date', 'status', 'student_count']


# class StudentProfileSerializer(serializers.ModelSerializer):
#     full_name = serializers.SerializerMethodField()
#     phone = serializers.SerializerMethodField()
#     group_name = serializers.SerializerMethodField()
#     effective_fee = serializers.SerializerMethodField()
#     payment_status = serializers.SerializerMethodField()
#     attendance_rate = serializers.SerializerMethodField()
#     balance = serializers.SerializerMethodField()

#     def get_full_name(self, obj):
#         return obj.user.get_full_name()

#     def get_phone(self, obj):
#         return obj.user.phone

#     def get_group_name(self, obj):
#         return obj.group.name if obj.group else None

#     def get_effective_fee(self, obj):
#         return float(obj.get_effective_fee())

#     def get_payment_status(self, obj):
#         today = date.today()
#         current_month = date(today.year, today.month, 1)
#         paid_this_month = obj.payments.filter(month=current_month).exists()
#         if paid_this_month:
#             return 'paid'
#         if today.day > obj.payment_due_day:
#             return 'overdue'
#         return 'pending'

#     def get_attendance_rate(self, obj):
#         total = obj.attendance_records.count()
#         if not total:
#             return 0
#         present = obj.attendance_records.filter(is_present=True).count()
#         return round((present / total) * 100, 1)

#     def get_balance(self, obj):
#         today = date.today()
#         current_month = date(today.year, today.month, 1)
#         this_month_payment = obj.payments.filter(month=current_month).aggregate(Sum('amount'))['amount__sum'] or 0
#         effective_fee = float(obj.get_effective_fee())
#         return float(this_month_payment) - effective_fee

#     class Meta:
#         model = StudentProfile
#         fields = ['id', 'full_name', 'phone', 'group', 'group_name', 'join_date',
#                   'discount', 'payment_due_day', 'effective_fee', 'payment_status',
#                   'attendance_rate', 'balance']


# class PaymentSerializer(serializers.ModelSerializer):
#     student_name = serializers.SerializerMethodField()
#     group_name = serializers.SerializerMethodField()

#     def get_student_name(self, obj):
#         return obj.student.user.get_full_name()

#     def get_group_name(self, obj):
#         return obj.student.group.name if obj.student.group else None

#     class Meta:
#         model = Payment
#         fields = ['id', 'student', 'student_name', 'group_name', 'amount',
#                   'payment_date', 'month', 'note']


# class AttendanceSerializer(serializers.ModelSerializer):
#     student_name = serializers.SerializerMethodField()

#     def get_student_name(self, obj):
#         return obj.student.user.get_full_name()

#     class Meta:
#         model = Attendance
#         fields = ['id', 'student', 'student_name', 'group', 'date', 'is_present', 'note']


# class GradeSerializer(serializers.ModelSerializer):
#     student_name = serializers.SerializerMethodField()
#     teacher_name = serializers.SerializerMethodField()

#     def get_student_name(self, obj):
#         return obj.student.user.get_full_name()

#     def get_teacher_name(self, obj):
#         return obj.teacher.get_full_name() if obj.teacher else None

#     class Meta:
#         model = Grade
#         fields = ['id', 'student', 'student_name', 'teacher', 'teacher_name',
#                   'topic', 'score', 'date', 'note']


# # Admin reports serializers
# class MonthlyRevenueSerializer(serializers.Serializer):
#     month = serializers.DateField()
#     total = serializers.DecimalField(max_digits=15, decimal_places=2)
#     payment_count = serializers.IntegerField()


# class DailyRevenueSerializer(serializers.Serializer):
#     date = serializers.DateField()
#     total = serializers.DecimalField(max_digits=15, decimal_places=2)
#     payment_count = serializers.IntegerField()


# class StudentSerializer(serializers.ModelSerializer):
#     full_name       = serializers.SerializerMethodField()
#     group_name      = serializers.SerializerMethodField()
#     payment_due_day = serializers.SerializerMethodField()
#     discount        = serializers.SerializerMethodField()
#     payment_status  = serializers.SerializerMethodField()
#     effective_fee   = serializers.SerializerMethodField()
#     attendance_rate = serializers.SerializerMethodField()

#     class Meta:
#         model = User
#         fields = [
#             'id', 'username', 'first_name', 'last_name', 'phone', 'email',
#             'full_name', 'group_name',
#             'payment_due_day', 'discount', 'payment_status', 'effective_fee', 'attendance_rate',
#         ]

#     def get_full_name(self, obj):
#         return f"{obj.first_name} {obj.last_name}".strip() or obj.username

#     def get_group_name(self, obj):
#         try:
#             return obj.student_profile.group.name if obj.student_profile.group else None
#         except StudentProfile.DoesNotExist:
#             return None

#     def get_payment_due_day(self, obj):
#         try:
#             return obj.student_profile.payment_due_day
#         except StudentProfile.DoesNotExist:
#             return None

#     def get_discount(self, obj):
#         try:
#             return float(obj.student_profile.discount)
#         except StudentProfile.DoesNotExist:
#             return 0

#     # StudentSerializer ichida — get_payment_status
#     def get_payment_status(self, obj):
#         # obj = User instance
#         try:
#             profile = obj.student_profile  # StudentProfile olish
#         except StudentProfile.DoesNotExist:
#             return 'pending'

#         if not profile.group:
#             return 'pending'

#         today = date.today()
        
#         # ✅ TO'G'RI: student=profile (StudentProfile instance)
#         paid = Payment.objects.filter(
#             student=profile,          # <-- User emas, profile
#             month__year=today.year,
#             month__month=today.month,
#         ).exists()

#         if paid:
#             return 'paid'

#         due_day = profile.payment_due_day
#         last_day = calendar.monthrange(today.year, today.month)[1]
#         due_date = today.replace(day=min(due_day, last_day))
#         return 'overdue' if today > due_date else 'pending'

#     # get_attendance_rate ham xuddi 
#     def get_attendance_rate(self, obj):
#         try:
#             profile = obj.student_profile
#         except StudentProfile.DoesNotExist:
#             return 0
        
#         # ✅ TO'G'RI: student=profile
#         total = Attendance.objects.filter(student=profile).count()
#         if not total:
#             return 0
#         present = Attendance.objects.filter(student=profile, is_present=True).count()
#         return round((present / total) * 100)

#     def get_effective_fee(self, obj):
#         try:
#             return float(obj.student_profile.get_effective_fee())
#         except StudentProfile.DoesNotExist:
#             return 0

#     # def get_attendance_rate(self, obj):
#     #     try:
#     #         total = Attendance.objects.filter(student=obj).count()
#     #         if not total:
#     #             return 0
#     #         present = Attendance.objects.filter(student=obj, is_present=True).count()
#     #         return round((present / total) * 100)
#     #     except Exception:
#     #         return 0






from rest_framework import serializers
from django.db.models import Sum
from .models import User, Group, StudentProfile, Payment, Attendance, Grade, Expense
from datetime import date, timedelta
import calendar


# ─────────────────────────────────────────────────────────────────────────────
# YORDAMCHI FUNKSIYA: o'quvchining oylik qarz/to'lov holati
# ─────────────────────────────────────────────────────────────────────────────
def _monthly_debt_rows(profile: StudentProfile) -> list[dict]:
    """
    O'quvchi guruhga kirgan oydan bugungi oygacha har bir oy uchun:
      {month, expected, paid, debt, status}

    status:
      'paid'     – to'liq to'landi (yoki ortiqcha)
      'partial'  – qisman to'landi
      'overdue'  – muddat o'tgan, to'lanmagan
      'pending'  – muddat hali kelmagan
    """
    if not profile.group:
        return []

    fee_per_month = float(profile.get_effective_fee())
    if fee_per_month <= 0:
        return []

    # Boshlang'ich oy: join_date oyining 1-kuni
    start = profile.join_date.replace(day=1)
    today = date.today()
    # Oxirgi oy: shu oy
    end   = today.replace(day=1)

    # Har bir oy uchun to'langan summani olish (bir SQL query)
    payments_qs = (
        Payment.objects
        .filter(student=profile, month__gte=start, month__lte=end)
        .values('month')
        .annotate(total=Sum('amount'))
    )
    paid_map = {row['month']: float(row['total']) for row in payments_qs}

    rows = []
    cur  = start
    while cur <= end:
        paid     = paid_map.get(cur, 0.0)
        debt     = round(fee_per_month - paid, 2)

        # Status aniqlash
        if debt <= 0:
            status = 'paid'
        elif paid > 0:
            status = 'partial'
        else:
            last_day = calendar.monthrange(cur.year, cur.month)[1]
            due_date = cur.replace(day=min(profile.payment_due_day, last_day))
            if today > due_date:
                status = 'overdue'
            else:
                status = 'pending'

        rows.append({
            'month':    cur.isoformat(),            # "2024-11-01"
            'expected': fee_per_month,
            'paid':     paid,
            'debt':     max(debt, 0),               # manfiy bo'lmaydi
            'overpaid': abs(min(debt, 0)),           # ortiqcha to'langan
            'status':   status,
        })

        # Keyingi oy
        if cur.month == 12:
            cur = cur.replace(year=cur.year + 1, month=1)
        else:
            cur = cur.replace(month=cur.month + 1)

    return rows


def _total_debt(profile: StudentProfile) -> float:
    """
    Barcha oylar bo'yicha umumiy qarzdorlik (manfiy = ortiqcha to'lagan).
    """
    rows = _monthly_debt_rows(profile)
    return round(sum(r['debt'] - r['overpaid'] for r in rows), 2)


def _payment_status_smart(profile: StudentProfile) -> str:
    """
    Joriy oyning to'lov holati.
    'paid' | 'partial' | 'overdue' | 'pending'

    Agar serializer context da 'paid_map' bo'lsa (bulk optimizatsiya),
    undan foydalanadi — DB ga qo'shimcha query ketmaydi.
    """
    if not profile.group:
        return 'pending'
    today = date.today()
    cur   = today.replace(day=1)
    rows  = _monthly_debt_rows(profile)
    for r in rows:
        if r['month'] == cur.isoformat():
            return r['status']
    return 'pending'


# ─── User ─────────────────────────────────────────────────────────────────────
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = ['id', 'username', 'first_name', 'last_name', 'role', 'phone', 'email']


# ─── Group ────────────────────────────────────────────────────────────────────
class GroupSerializer(serializers.ModelSerializer):
    teacher_name  = serializers.SerializerMethodField()
    student_count = serializers.SerializerMethodField()

    def get_teacher_name(self, obj):
        return obj.teacher.get_full_name() if obj.teacher else None

    def get_student_count(self, obj):
        return obj.students.count()

    class Meta:
        model  = Group
        fields = [
            'id', 'name', 'teacher', 'teacher_name', 'subject',
            'schedule', 'monthly_fee', 'start_date', 'status', 'student_count',
        ]


# ─── StudentProfile ───────────────────────────────────────────────────────────
class StudentProfileSerializer(serializers.ModelSerializer):
    full_name       = serializers.SerializerMethodField()
    phone           = serializers.SerializerMethodField()
    group_name      = serializers.SerializerMethodField()
    effective_fee   = serializers.SerializerMethodField()
    payment_status  = serializers.SerializerMethodField()
    attendance_rate = serializers.SerializerMethodField()
    total_debt      = serializers.SerializerMethodField()   # eski: balance

    def get_full_name(self, obj):
        return obj.user.get_full_name()

    def get_phone(self, obj):
        return obj.user.phone

    def get_group_name(self, obj):
        return obj.group.name if obj.group else None

    def get_effective_fee(self, obj):
        return float(obj.get_effective_fee())

    def get_payment_status(self, obj):
        return _payment_status_smart(obj)

    def get_attendance_rate(self, obj):
        total = obj.attendance_records.count()
        if not total:
            return 0
        present = obj.attendance_records.filter(is_present=True).count()
        return round((present / total) * 100, 1)

    def get_total_debt(self, obj):
        """Manfiy = ortiqcha to'lagan, musbat = qarzdor"""
        return _total_debt(obj)

    class Meta:
        model  = StudentProfile
        fields = [
            'id', 'full_name', 'phone', 'group', 'group_name', 'join_date',
            'discount', 'payment_due_day', 'effective_fee', 'payment_status',
            'attendance_rate', 'total_debt',
        ]


# ─── Student (User-based, admin ro'yxati uchun) ───────────────────────────────
class StudentSerializer(serializers.ModelSerializer):
    """
    O'quvchilar ro'yxati uchun optimallashtirilgan serializer.

    N+1 muammosidan qochish uchun ViewSet queryset'ida
    prefetch_related('student_profile__payments') qo'shilishi kerak.
    """
    full_name       = serializers.SerializerMethodField()
    group_name      = serializers.SerializerMethodField()
    payment_due_day = serializers.SerializerMethodField()
    discount        = serializers.SerializerMethodField()
    payment_status  = serializers.SerializerMethodField()
    effective_fee   = serializers.SerializerMethodField()
    attendance_rate = serializers.SerializerMethodField()
    total_debt      = serializers.SerializerMethodField()

    class Meta:
        model  = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 'phone', 'email',
            'full_name', 'group_name',
            'payment_due_day', 'discount', 'payment_status',
            'effective_fee', 'attendance_rate', 'total_debt',
        ]

    def _get_profile(self, obj):
        try:
            return obj.student_profile
        except StudentProfile.DoesNotExist:
            return None

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username

    def get_group_name(self, obj):
        p = self._get_profile(obj)
        return p.group.name if p and p.group else None

    def get_payment_due_day(self, obj):
        p = self._get_profile(obj)
        return p.payment_due_day if p else None

    def get_discount(self, obj):
        p = self._get_profile(obj)
        return float(p.discount) if p else 0

    def get_payment_status(self, obj):
        p = self._get_profile(obj)
        if not p:
            return 'pending'
        # Tez yo'l: faqat joriy oy uchun payment bor-yo'qligini tekshir
        today = date.today()
        cur   = today.replace(day=1)
        # prefetch_related bo'lsa all_cached_payments ishlatiladi
        payments_this_month = [
            pay for pay in p.payments.all()
            if pay.month.year == today.year and pay.month.month == today.month
        ]
        paid = sum(float(pay.amount) for pay in payments_this_month)
        fee  = float(p.get_effective_fee())
        if fee <= 0:
            return 'pending'
        if paid >= fee:
            return 'paid'
        if paid > 0:
            return 'partial'
        last_day = calendar.monthrange(today.year, today.month)[1]
        due_date = cur.replace(day=min(p.payment_due_day, last_day))
        return 'overdue' if today > due_date else 'pending'

    def get_effective_fee(self, obj):
        p = self._get_profile(obj)
        return float(p.get_effective_fee()) if p else 0

    def get_attendance_rate(self, obj):
        p = self._get_profile(obj)
        if not p:
            return 0
        records = p.attendance_records.all()
        total   = len(records)
        if not total:
            return 0
        present = sum(1 for r in records if r.is_present)
        return round((present / total) * 100)

    def get_total_debt(self, obj):
        p = self._get_profile(obj)
        return _total_debt(p) if p else 0


# ─── Payment ──────────────────────────────────────────────────────────────────
class PaymentSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    group_name   = serializers.SerializerMethodField()

    def get_student_name(self, obj):
        return obj.student.user.get_full_name()

    def get_group_name(self, obj):
        return obj.student.group.name if obj.student.group else None

    class Meta:
        model  = Payment
        fields = [
            'id', 'student', 'student_name', 'group_name',
            'amount', 'payment_date', 'month', 'note',
        ]


# ─── Attendance ───────────────────────────────────────────────────────────────
class AttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()

    def get_student_name(self, obj):
        return obj.student.user.get_full_name()

    class Meta:
        model  = Attendance
        fields = ['id', 'student', 'student_name', 'group', 'date', 'is_present', 'note']


# ─── Grade ────────────────────────────────────────────────────────────────────
class GradeSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    teacher_name = serializers.SerializerMethodField()

    def get_student_name(self, obj):
        return obj.student.user.get_full_name()

    def get_teacher_name(self, obj):
        return obj.teacher.get_full_name() if obj.teacher else None

    class Meta:
        model  = Grade
        fields = ['id', 'student', 'student_name', 'teacher', 'teacher_name',
                  'topic', 'score', 'date', 'note']


# ─── Expense ──────────────────────────────────────────────────────────────────
class ExpenseSerializer(serializers.ModelSerializer):
    category_display = serializers.SerializerMethodField()

    def get_category_display(self, obj):
        return obj.get_category_display()

    class Meta:
        model  = Expense
        fields = ['id', 'title', 'category', 'category_display',
                  'amount', 'expense_date', 'note', 'created_at']
        read_only_fields = ['created_at']




# from rest_framework import serializers
# from django.db.models import Sum
# from .models import User, Group, StudentProfile, Payment, Attendance, Grade, Expense
# from datetime import date, timedelta
# import calendar


# # ─────────────────────────────────────────────────────────────────────────────
# # YORDAMCHI FUNKSIYA: o'quvchining oylik qarz/to'lov holati
# # ─────────────────────────────────────────────────────────────────────────────
# def _monthly_debt_rows(profile: StudentProfile) -> list[dict]:
#     """
#     O'quvchi guruhga kirgan oydan bugungi oygacha har bir oy uchun:
#       {month, expected, paid, debt, status}

#     status:
#       'paid'     – to'liq to'landi (yoki ortiqcha)
#       'partial'  – qisman to'landi
#       'overdue'  – muddat o'tgan, to'lanmagan
#       'pending'  – muddat hali kelmagan
#     """
#     if not profile.group:
#         return []

#     fee_per_month = float(profile.get_effective_fee())
#     if fee_per_month <= 0:
#         return []

#     # Boshlang'ich oy: join_date oyining 1-kuni
#     start = profile.join_date.replace(day=1)
#     today = date.today()
#     # Oxirgi oy: shu oy
#     end   = today.replace(day=1)

#     # Har bir oy uchun to'langan summani olish (bir SQL query)
#     payments_qs = (
#         Payment.objects
#         .filter(student=profile, month__gte=start, month__lte=end)
#         .values('month')
#         .annotate(total=Sum('amount'))
#     )
#     paid_map = {row['month']: float(row['total']) for row in payments_qs}

#     rows = []
#     cur  = start
#     while cur <= end:
#         paid     = paid_map.get(cur, 0.0)
#         debt     = round(fee_per_month - paid, 2)

#         # Status aniqlash
#         if debt <= 0:
#             status = 'paid'
#         elif paid > 0:
#             status = 'partial'
#         else:
#             last_day = calendar.monthrange(cur.year, cur.month)[1]
#             due_date = cur.replace(day=min(profile.payment_due_day, last_day))
#             if today > due_date:
#                 status = 'overdue'
#             else:
#                 status = 'pending'

#         rows.append({
#             'month':    cur.isoformat(),            # "2024-11-01"
#             'expected': fee_per_month,
#             'paid':     paid,
#             'debt':     max(debt, 0),               # manfiy bo'lmaydi
#             'overpaid': abs(min(debt, 0)),           # ortiqcha to'langan
#             'status':   status,
#         })

#         # Keyingi oy
#         if cur.month == 12:
#             cur = cur.replace(year=cur.year + 1, month=1)
#         else:
#             cur = cur.replace(month=cur.month + 1)

#     return rows


# def _total_debt(profile: StudentProfile) -> float:
#     """
#     Barcha oylar bo'yicha umumiy qarzdorlik (manfiy = ortiqcha to'lagan).
#     """
#     rows = _monthly_debt_rows(profile)
#     return round(sum(r['debt'] - r['overpaid'] for r in rows), 2)


# def _payment_status_smart(profile: StudentProfile) -> str:
#     """
#     Joriy oyning to'lov holati.
#     'paid' | 'partial' | 'overdue' | 'pending'
#     """
#     if not profile.group:
#         return 'pending'
#     today = date.today()
#     cur   = today.replace(day=1)
#     rows  = _monthly_debt_rows(profile)
#     for r in rows:
#         if r['month'] == cur.isoformat():
#             return r['status']
#     return 'pending'


# # ─── User ─────────────────────────────────────────────────────────────────────
# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model  = User
#         fields = ['id', 'username', 'first_name', 'last_name', 'role', 'phone', 'email']


# # ─── Group ────────────────────────────────────────────────────────────────────
# class GroupSerializer(serializers.ModelSerializer):
#     teacher_name  = serializers.SerializerMethodField()
#     student_count = serializers.SerializerMethodField()

#     def get_teacher_name(self, obj):
#         return obj.teacher.get_full_name() if obj.teacher else None

#     def get_student_count(self, obj):
#         return obj.students.count()

#     class Meta:
#         model  = Group
#         fields = [
#             'id', 'name', 'teacher', 'teacher_name', 'subject',
#             'schedule', 'monthly_fee', 'start_date', 'status', 'student_count',
#         ]


# # ─── StudentProfile ───────────────────────────────────────────────────────────
# class StudentProfileSerializer(serializers.ModelSerializer):
#     full_name       = serializers.SerializerMethodField()
#     phone           = serializers.SerializerMethodField()
#     group_name      = serializers.SerializerMethodField()
#     effective_fee   = serializers.SerializerMethodField()
#     payment_status  = serializers.SerializerMethodField()
#     attendance_rate = serializers.SerializerMethodField()
#     total_debt      = serializers.SerializerMethodField()   # eski: balance

#     def get_full_name(self, obj):
#         return obj.user.get_full_name()

#     def get_phone(self, obj):
#         return obj.user.phone

#     def get_group_name(self, obj):
#         return obj.group.name if obj.group else None

#     def get_effective_fee(self, obj):
#         return float(obj.get_effective_fee())

#     def get_payment_status(self, obj):
#         return _payment_status_smart(obj)

#     def get_attendance_rate(self, obj):
#         total = obj.attendance_records.count()
#         if not total:
#             return 0
#         present = obj.attendance_records.filter(is_present=True).count()
#         return round((present / total) * 100, 1)

#     def get_total_debt(self, obj):
#         """Manfiy = ortiqcha to'lagan, musbat = qarzdor"""
#         return _total_debt(obj)

#     class Meta:
#         model  = StudentProfile
#         fields = [
#             'id', 'full_name', 'phone', 'group', 'group_name', 'join_date',
#             'discount', 'payment_due_day', 'effective_fee', 'payment_status',
#             'attendance_rate', 'total_debt',
#         ]


# # ─── Student (User-based, admin ro'yxati uchun) ───────────────────────────────
# class StudentSerializer(serializers.ModelSerializer):
#     full_name       = serializers.SerializerMethodField()
#     group_name      = serializers.SerializerMethodField()
#     payment_due_day = serializers.SerializerMethodField()
#     discount        = serializers.SerializerMethodField()
#     payment_status  = serializers.SerializerMethodField()
#     effective_fee   = serializers.SerializerMethodField()
#     attendance_rate = serializers.SerializerMethodField()
#     total_debt      = serializers.SerializerMethodField()

#     class Meta:
#         model  = User
#         fields = [
#             'id', 'username', 'first_name', 'last_name', 'phone', 'email',
#             'full_name', 'group_name',
#             'payment_due_day', 'discount', 'payment_status',
#             'effective_fee', 'attendance_rate', 'total_debt',
#         ]

#     def get_full_name(self, obj):
#         return f"{obj.first_name} {obj.last_name}".strip() or obj.username

#     def get_group_name(self, obj):
#         try:
#             return obj.student_profile.group.name if obj.student_profile.group else None
#         except StudentProfile.DoesNotExist:
#             return None

#     def get_payment_due_day(self, obj):
#         try:
#             return obj.student_profile.payment_due_day
#         except StudentProfile.DoesNotExist:
#             return None

#     def get_discount(self, obj):
#         try:
#             return float(obj.student_profile.discount)
#         except StudentProfile.DoesNotExist:
#             return 0

#     def get_payment_status(self, obj):
#         try:
#             return _payment_status_smart(obj.student_profile)
#         except StudentProfile.DoesNotExist:
#             return 'pending'

#     def get_effective_fee(self, obj):
#         try:
#             return float(obj.student_profile.get_effective_fee())
#         except StudentProfile.DoesNotExist:
#             return 0

#     def get_attendance_rate(self, obj):
#         try:
#             profile = obj.student_profile
#         except StudentProfile.DoesNotExist:
#             return 0
#         total = Attendance.objects.filter(student=profile).count()
#         if not total:
#             return 0
#         present = Attendance.objects.filter(student=profile, is_present=True).count()
#         return round((present / total) * 100)

#     def get_total_debt(self, obj):
#         try:
#             return _total_debt(obj.student_profile)
#         except StudentProfile.DoesNotExist:
#             return 0


# # ─── Payment ──────────────────────────────────────────────────────────────────
# class PaymentSerializer(serializers.ModelSerializer):
#     student_name = serializers.SerializerMethodField()
#     group_name   = serializers.SerializerMethodField()

#     def get_student_name(self, obj):
#         return obj.student.user.get_full_name()

#     def get_group_name(self, obj):
#         return obj.student.group.name if obj.student.group else None

#     class Meta:
#         model  = Payment
#         fields = [
#             'id', 'student', 'student_name', 'group_name',
#             'amount', 'payment_date', 'month', 'note',
#         ]


# # ─── Attendance ───────────────────────────────────────────────────────────────
# class AttendanceSerializer(serializers.ModelSerializer):
#     student_name = serializers.SerializerMethodField()

#     def get_student_name(self, obj):
#         return obj.student.user.get_full_name()

#     class Meta:
#         model  = Attendance
#         fields = ['id', 'student', 'student_name', 'group', 'date', 'is_present', 'note']


# # ─── Grade ────────────────────────────────────────────────────────────────────
# class GradeSerializer(serializers.ModelSerializer):
#     student_name = serializers.SerializerMethodField()
#     teacher_name = serializers.SerializerMethodField()

#     def get_student_name(self, obj):
#         return obj.student.user.get_full_name()

#     def get_teacher_name(self, obj):
#         return obj.teacher.get_full_name() if obj.teacher else None

#     class Meta:
#         model  = Grade
#         fields = ['id', 'student', 'student_name', 'teacher', 'teacher_name',
#                   'topic', 'score', 'date', 'note']


# # ─── Expense ──────────────────────────────────────────────────────────────────
# class ExpenseSerializer(serializers.ModelSerializer):
#     category_display = serializers.SerializerMethodField()

#     def get_category_display(self, obj):
#         return obj.get_category_display()

#     class Meta:
#         model  = Expense
#         fields = ['id', 'title', 'category', 'category_display',
#                   'amount', 'expense_date', 'note', 'created_at']
#         read_only_fields = ['created_at']