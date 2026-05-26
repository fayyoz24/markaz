# from django.db import models
# from django.contrib.auth.models import AbstractUser


# class User(AbstractUser):
#     ROLE_CHOICES = [
#         ('admin', 'Admin'),
#         ('teacher', 'O\'qituvchi'),
#         ('student', 'O\'quvchi'),
#     ]
#     role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
#     phone = models.CharField(max_length=15, blank=True)

#     def __str__(self):
#         return f"{self.get_full_name()} ({self.role})"


# class Group(models.Model):
#     name = models.CharField(max_length=100)
#     teacher = models.ForeignKey(
#         User, on_delete=models.SET_NULL, null=True,
#         related_name='teaching_groups',
#         limit_choices_to={'role': 'teacher'}
#     )
#     subject = models.CharField(max_length=100)
#     schedule = models.CharField(max_length=100)
#     monthly_fee = models.DecimalField(max_digits=12, decimal_places=2)
#     start_date = models.DateField()
#     status = models.CharField(
#         max_length=10,
#         choices=[('active', 'Faol'), ('inactive', 'Nofaol')],
#         default='active'
#     )
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.name


# class StudentProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
#     group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, related_name='students')
#     join_date = models.DateField(auto_now_add=True)
#     discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)
#     payment_due_day = models.IntegerField(default=15)  # Month day (1-31)

#     def get_effective_fee(self):
#         if not self.group:
#             return 0
#         fee = self.group.monthly_fee
#         return fee * (1 - self.discount / 100)

#     def __str__(self):
#         return f"{self.user.get_full_name()} - {self.group}"


# class Payment(models.Model):
#     student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='payments')
#     amount = models.DecimalField(max_digits=12, decimal_places=2)
#     payment_date = models.DateField(auto_now_add=True)
#     month = models.DateField()  # First day of the month being paid for
#     note = models.TextField(blank=True)
#     created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='recorded_payments')

#     class Meta:
#         unique_together = ('student', 'month')

#     def __str__(self):
#         return f"{self.student} - {self.month.strftime('%B %Y')} - {self.amount}"


# class Attendance(models.Model):
#     student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='attendance_records')
#     group = models.ForeignKey(Group, on_delete=models.CASCADE)
#     date = models.DateField()
#     is_present = models.BooleanField(default=False)
#     note = models.TextField(blank=True)
#     recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

#     class Meta:
#         unique_together = ('student', 'date')

#     def __str__(self):
#         status = "Keldi" if self.is_present else "Kelmadi"
#         return f"{self.student} - {self.date} - {status}"


# class Grade(models.Model):
#     student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='grades')
#     teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, limit_choices_to={'role': 'teacher'})
#     topic = models.CharField(max_length=200)
#     score = models.IntegerField()  # 0-100
#     date = models.DateField(auto_now_add=True)
#     note = models.TextField(blank=True)

#     def __str__(self):
#         return f"{self.student} - {self.topic}: {self.score}"







from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('teacher', "O'qituvchi"),
        ('student', "O'quvchi"),
    ]
    role  = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    phone = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"


class Group(models.Model):
    STATUS_CHOICES = [('active', 'Faol'), ('inactive', 'Nofaol')]

    name        = models.CharField(max_length=100)
    teacher     = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='teaching_groups',
        limit_choices_to={'role': 'teacher'},
    )
    subject     = models.CharField(max_length=100)
    schedule    = models.CharField(max_length=100)
    monthly_fee = models.DecimalField(max_digits=12, decimal_places=2)
    start_date  = models.DateField()
    status      = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class StudentProfile(models.Model):
    user            = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    group           = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    join_date       = models.DateField(auto_now_add=True)
    discount        = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    payment_due_day = models.IntegerField(default=15)  # 1–31

    def get_effective_fee(self):
        if not self.group:
            return 0
        return self.group.monthly_fee * (1 - self.discount / 100)

    def __str__(self):
        return f"{self.user.get_full_name()} — {self.group}"


class Payment(models.Model):
    """
    Bir o'quvchi bir oyga bir necha marta to'lov qilishi mumkin
    (bo'lib-bo'lib to'lash).  unique_together olib tashlandi.
    """
    student      = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='payments')
    amount       = models.DecimalField(max_digits=12, decimal_places=2)
    payment_date = models.DateField(auto_now_add=True)
    month        = models.DateField()   # Oyning 1-kuni  →  2024-11-01
    note         = models.TextField(blank=True)
    created_by   = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='recorded_payments')

    class Meta:
        ordering = ['-payment_date', '-id']
        indexes  = [
            models.Index(fields=['student', 'month']),
        ]

    def __str__(self):
        return f"{self.student} — {self.month.strftime('%B %Y')} — {self.amount}"


class Attendance(models.Model):
    student     = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='attendance_records')
    group       = models.ForeignKey(Group, on_delete=models.CASCADE)
    date        = models.DateField()
    is_present  = models.BooleanField(default=False)
    note        = models.TextField(blank=True)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        unique_together = ('student', 'date')

    def __str__(self):
        status = "Keldi" if self.is_present else "Kelmadi"
        return f"{self.student} — {self.date} — {status}"


class Grade(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='grades')
    teacher = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        limit_choices_to={'role': 'teacher'},
    )
    topic   = models.CharField(max_length=200)
    score   = models.IntegerField()   # 0–100
    date    = models.DateField(auto_now_add=True)
    note    = models.TextField(blank=True)

    def __str__(self):
        return f"{self.student} — {self.topic}: {self.score}"


class Expense(models.Model):
    """O'quv markazi xarajatlari (maosh, ijara, kommunal, jihozlar …)"""
    CATEGORY_CHOICES = [
        ('salary',    'Maosh'),
        ('utility',   'Kommunal'),
        ('rent',      'Ijara'),
        ('equipment', 'Jihozlar'),
        ('marketing', 'Marketing'),
        ('other',     'Boshqa'),
    ]

    title        = models.CharField(max_length=200)
    category     = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    amount       = models.DecimalField(max_digits=12, decimal_places=2)
    expense_date = models.DateField()
    note         = models.TextField(blank=True)
    created_by   = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='recorded_expenses')
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-expense_date', '-created_at']

    def __str__(self):
        return f"{self.title} — {self.amount} ({self.expense_date})"