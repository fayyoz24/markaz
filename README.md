# 🎓 IT Klaster — O'quv Markazi Boshqaruv Tizimi

## Loyiha tuzilishi

```
it-klaster/
├── backend/          (Django REST API)
│   ├── api/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   └── settings.py
└── frontend/         (React)
    └── ITKlaster.jsx  ← Asosiy React komponenti
```

---

## 🔧 Backend ishga tushirish (Django)

```bash
# 1. Virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Paketlarni o'rnatish
pip install django djangorestframework djangorestframework-simplejwt django-cors-headers

# 3. Django proyektini boshlash
django-admin startproject itklaster .
python manage.py startapp api

# 4. settings.py'dagi kodni ko'chiring

# 5. Ma'lumotlar bazasini yaratish
python manage.py makemigrations
python manage.py migrate

# 6. Admin yaratish
python manage.py createsuperuser

# 7. Ishga tushirish
python manage.py runserver
```

---

## ⚛️ Frontend ishga tushirish (React)

```bash
# 1. Yangi React proyekti
npm create vite@latest it-klaster-frontend -- --template react
cd it-klaster-frontend

# 2. Paketlarni o'rnatish
npm install recharts axios

# 3. ITKlaster.jsx faylini src/ papkasiga ko'chiring
# 4. App.jsx ichida import qiling

npm run dev
```

---

## 🔑 Rollar va imkoniyatlar

### 👑 Admin
- Yangi gruppa yaratish (nom, o'qituvchi, fan, jadval, oylik to'lov)
- O'quvchilarni qo'shish, gruppaga biriktirish
- Chegirma belgilash (%)
- To'lov qabul qilish va kuzatish
- Qarzdorlar ro'yxati
- Oylik va kunlik tushum hisobotlari

### 👨‍🏫 O'qituvchi
- Davomat belgilash (har bir dars uchun)
- Baho qo'yish (mavzu bo'yicha)
- O'z guruhlari o'quvchilarini ko'rish

### 🎓 O'quvchi
- Baholarini ko'rish
- Davomatini ko'rish
- To'lovlar tarixi
- Gruppa ma'lumotlari

---

## 📡 API Endpointlar

| Method | URL | Tavsif |
|--------|-----|--------|
| POST | `/api/auth/login/` | Login (JWT token) |
| POST | `/api/auth/refresh/` | Token yangilash |
| GET/POST | `/api/groups/` | Gruppalar |
| GET/POST | `/api/students/` | O'quvchilar |
| GET/POST | `/api/payments/` | To'lovlar |
| POST | `/api/attendance/bulk_create/` | Davomat (ommaviy) |
| GET/POST | `/api/grades/` | Baholar |
| GET | `/api/reports/summary/` | Dashboard statistika |
| GET | `/api/reports/monthly_revenue/` | Oylik tushum |
| GET | `/api/reports/daily_revenue/` | Kunlik tushum |
| GET | `/api/reports/debtors/` | Qarzdorlar |

---

## 🗄️ Ma'lumotlar bazasi modellari

- **User** — Foydalanuvchi (admin/teacher/student roli bilan)
- **Group** — Gruppa (o'qituvchi, fan, jadval, to'lov miqdori)
- **StudentProfile** — O'quvchi profili (chegirma, to'lov sanasi)
- **Payment** — To'lov (oy, miqdor, sana)
- **Attendance** — Davomat (kel/kelmaganlik)
- **Grade** — Baho (mavzu, ball, sana)

---

## 🖥️ React App — Demo login

| Login | Parol | Rol |
|-------|-------|-----|
| admin | admin123 | Admin |
| teacher1 | teacher123 | O'qituvchi |
| student1 | student123 | O'quvchi |

> React komponentida barcha ma'lumotlar mock (demo) ko'rinishda. Real backendga ulash uchun `axios` yoki `fetch` orqali API'ga so'rov yuboring.
