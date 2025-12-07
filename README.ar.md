# Common Customization - تطبيق Frappe للموارد البشرية

تطبيق شامل لإدارة الموارد البشرية مبني على إطار عمل Frappe، يوفر واجهات برمجية RESTful API ونظام إدارة متكامل للعمليات الإدارية والموارد البشرية.

**[English Version](README.md) | النسخة العربية**

## 📋 نظرة عامة

**Common Customization** هو تطبيق Frappe متقدم يوفر:

- نظام إدارة موارد بشرية متكامل (HR Management)
- واجهات برمجية RESTful API مع مصادقة JWT
- إدارة الإجازات والطلبات الإدارية
- نظام دعم فني (Help Desk)
- إدارة المشاريع والمهام
- إشعارات Firebase Cloud Messaging (FCM)
- تقارير وتحليلات شاملة

**المطور**: Ahmed Madi  
**البريد الإلكتروني**: dev.amadi7@gmail.com  
**الإصدار**: 0.0.1  
**الترخيص**: MIT

---

## 🚀 التثبيت

### المتطلبات الأساسية

- Frappe Framework (الإصدار 14 أو أحدث)
- Python 3.10+
- MariaDB/MySQL
- Node.js 16+

### خطوات التثبيت

1. **الانتقال إلى مجلد التطبيقات**

```bash
cd frappe-bench
```

2. **تحميل التطبيق**

```bash
bench get-app https://github.com/ahmed-madi/common.git
```

3. **تثبيت التطبيق على الموقع**

```bash
bench --site [site-name] install-app common
```

4. **تشغيل الترحيلات**

```bash
bench --site [site-name] migrate
```

5. **إعادة تشغيل الخدمات**

```bash
bench restart
```

---

## 📦 الميزات الرئيسية

### 1. إدارة المستخدمين والمصادقة

- **تسجيل الدخول/الخروج** مع JWT tokens
- **تحديث الرموز** (Refresh Tokens)
- **إدارة الإعدادات الشخصية**
- **تغيير كلمة المرور**
- **الإشعارات الفورية**

### 2. إدارة الموارد البشرية

#### الطلبات الإدارية

- **طلبات الإجازات** (Leave Applications)
- **طلبات الإجازة التعويضية** (Compensatory Leave)
- **طلبات العمل عن بُعد** (Remote Work Requests)
- **طلبات العمل الإضافي** (Overtime Requests)
- **طلبات الاستقالة** (Resignation Requests)
- **طلبات القروض** (Loan Applications)

#### الشهادات والوثائق

- **شهادات الراتب** (Salary Certificates)
- **خطابات التعريف بالراتب** (Salary Identification Letters)
- **خطابات المخالصة** (Clearance Letters)
- **طلبات الوثائق** (Document Requests)

#### البدلات والمكافآت

- **طلبات البدلات** (Allowance Requests)
- **طلبات المكافآت** (Bonus Requests)
- **بدل التعليم** (Education Allowance)
- **مكافأة نهاية الخدمة** (End of Service Awards)

### 3. إدارة البيانات المشتركة

- **الأقسام** (Departments)
- **المسميات الوظيفية** (Designations)
- **الفروع** (Branches)
- **الأندية** (Clubs)
- **الجنسيات** (Nationalities)
- **سياسات الشركة** (Company Policies)

### 4. نظام المشاريع

- **إدارة المشاريع** (Project Management)
- **المهام** (Tasks)
- **تتبع الوقت** (Time Tracking)
- **التقارير** (Reports)

### 5. نظام الدعم الفني

- **تذاكر الدعم** (Support Tickets)
- **تتبع الحالة** (Status Tracking)
- **الأولويات** (Priorities)
- **التعليقات والمرفقات** (Comments & Attachments)

### 6. الإشعارات

- **إشعارات داخل التطبيق** (In-app Notifications)
- **Firebase Cloud Messaging** (Push Notifications)
- **إعدادات الإشعارات القابلة للتخصيص**

---

## 🔌 استخدام الواجهات البرمجية (API)

### عنوان الأساس (Base URL)

```
http://your-domain.com/api/v1
```

### المصادقة (Authentication)

جميع الطلبات المحمية تتطلب رأس المصادقة:

```http
Authorization: Bearer {access_token}
Content-Type: application/json
```

### مثال: تسجيل الدخول

**الطلب:**

```bash
curl -X POST http://your-domain.com/api/v1/user/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user@example.com",
    "password": "your_password"
  }'
```

**الاستجابة:**

```json
{
  "status": "success",
  "status_code": 200,
  "data": {
    "user": "user@example.com",
    "full_name": "Ahmed Ali",
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "WXF0kgFWiiU5BC6GbMNX9M0VsD_LdxIdKOSrgznuA9A"
  },
  "message": "Login successful"
}
```

### مثال: الحصول على قائمة الموظفين

**الطلب:**

```bash
curl -X GET "http://your-domain.com/api/v1/hr-common/employee?page=1&limit=20" \
  -H "Authorization: Bearer {access_token}"
```

### مثال: إنشاء طلب إجازة

**الطلب:**

```bash
curl -X POST http://your-domain.com/api/v1/hr-requests/leave-application \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "leave_type": "Annual Leave",
    "from_date": "2025-12-20",
    "to_date": "2025-12-22",
    "description": "Family vacation"
  }'
```

### نقاط النهاية الرئيسية (Main Endpoints)

#### إدارة المستخدمين

- `POST /api/v1/user/auth/login` - تسجيل الدخول
- `POST /api/v1/user/auth/logout` - تسجيل الخروج
- `POST /api/v1/user/auth/refresh-token` - تحديث الرمز
- `GET /api/v1/user/info` - معلومات المستخدم
- `PUT /api/v1/user/change-password` - تغيير كلمة المرور
- `GET /api/v1/user/notifications` - الإشعارات

#### البيانات المشتركة

- `GET /api/v1/hr-common/employee` - قائمة الموظفين
- `GET /api/v1/hr-common/department` - الأقسام
- `GET /api/v1/hr-common/designation` - المسميات الوظيفية
- `GET /api/v1/hr-common/branch` - الفروع
- `GET /api/v1/hr-common/club` - الأندية

#### طلبات الموارد البشرية

- `GET /api/v1/hr-requests/leave-application` - طلبات الإجازات
- `POST /api/v1/hr-requests/leave-application` - إنشاء طلب إجازة
- `GET /api/v1/hr-requests/overtime-request` - طلبات العمل الإضافي
- `GET /api/v1/hr-requests/remote-work-request` - طلبات العمل عن بُعد
- `GET /api/v1/hr-requests/salary-certificate` - شهادات الراتب

#### المشاريع

- `GET /api/v1/project-management/project` - قائمة المشاريع
- `GET /api/v1/project-management/task` - المهام
- `POST /api/v1/project-management/task` - إنشاء مهمة

#### الدعم الفني

- `GET /api/v1/help-desk/issue` - تذاكر الدعم
- `POST /api/v1/help-desk/issue` - إنشاء تذكرة
- `PUT /api/v1/help-desk/issue/{id}` - تحديث تذكرة

للحصول على التوثيق الكامل للواجهات البرمجية، راجع ملف [API_Documentation.md](common/api/API_Documentation.md).

---

## ⚙️ الإعدادات

### تخصيص الأنماط (CSS)

يتضمن التطبيق ملف CSS مخصص:

```python
app_include_css = [
    "/assets/common/css/common-style3.css",
]
```

### تجاوز DocTypes

يتم تجاوز DocTypes القياسية التالية:

- `Leave Application` - طلبات الإجازات
- `Leave Type` - أنواع الإجازات
- `Compensatory Leave Request` - طلبات الإجازة التعويضية
- `Loan Application` - طلبات القروض
- `Notification` - الإشعارات
- `Employee Checkin` - تسجيل حضور الموظفين

### الصلاحيات المخصصة

```python
permission_query_conditions = {
    "Employee HR Feedback": "common.permissions.employee_hr_feedback.get_permission_query_conditions",
}

has_permission = {
    "Employee HR Feedback": "common.permissions.employee_hr_feedback.has_permission",
}
```

---

## 📱 خدمة HR Service (Frontend)

يتضمن التطبيق واجهة مستخدم حديثة مبنية بتقنيات:

- React/Vue.js
- TypeScript
- Modern UI Components

الوصول إلى الواجهة:

```
http://your-domain.com/hr-services/
```

---

## 🔧 التطوير

### هيكل المشروع

```
common/
├── common/
│   ├── api/                    # الواجهات البرمجية
│   │   ├── controllers/        # Controllers
│   │   ├── routes/             # URL Routes
│   │   └── utils/              # Utilities
│   ├── common_customization/   # DocTypes الرئيسية
│   │   └── doctype/
│   ├── hr_fcm/                 # Firebase Cloud Messaging
│   ├── hr_support/             # نظام الدعم الفني
│   ├── overrides/              # تجاوزات DocTypes
│   ├── permissions/            # منطق الصلاحيات
│   ├── public/                 # الملفات الثابتة
│   └── hooks.py                # Frappe Hooks
├── hr-service/                 # Frontend Application
└── README.md
```

### تشغيل بيئة التطوير

```bash
# تشغيل خادم التطوير
bench start

# مراقبة التغييرات
bench watch
```

### إضافة DocType جديد

1. إنشاء DocType من واجهة Frappe
2. إضافة Controller في `common/common_customization/doctype/`
3. إضافة API Route في `common/api/routes/`
4. إضافة Controller في `common/api/controllers/`

---

## 📊 التقارير والتحليلات

يوفر التطبيق تقارير شاملة:

- تقارير الحضور والانصراف
- تقارير الإجازات
- تقارير الرواتب
- تقارير الأداء
- تقارير المشاريع

---

## 🔐 الأمان

- **JWT Authentication** - مصادقة آمنة بالرموز
- **Role-Based Access Control** - التحكم بالصلاحيات حسب الأدوار
- **Permission Queries** - استعلامات صلاحيات مخصصة
- **Secure Password Handling** - معالجة آمنة لكلمات المرور
- **API Rate Limiting** - تحديد معدل الطلبات

---

## 🧪 الاختبار

```bash
# تشغيل الاختبارات
bench --site [site-name] run-tests --app common

# اختبار وحدة معينة
bench --site [site-name] run-tests --app common --module common.tests.test_leave_application
```

---

## 📚 الموارد الإضافية

- **التوثيق الكامل للـ API**: [API_Documentation.md](common/api/API_Documentation.md)
- **Postman Collection**: [HR Final Endpoints.postman_collection.json](common/api/HR%20Final%20Endpoints.postman_collection.json)
- **Frappe Documentation**: https://frappeframework.com/docs
- **ERPNext HR Module**: https://docs.erpnext.com/docs/user/manual/en/human-resources

---

## 🤝 المساهمة

نرحب بالمساهمات! يرجى:

1. عمل Fork للمشروع
2. إنشاء فرع للميزة الجديدة (`git checkout -b feature/amazing-feature`)
3. Commit التغييرات (`git commit -m 'Add amazing feature'`)
4. Push للفرع (`git push origin feature/amazing-feature`)
5. فتح Pull Request

---

## 📝 الترخيص

هذا المشروع مرخص بموجب رخصة MIT - راجع ملف [LICENSE](license.txt) للتفاصيل.

---

## 📞 الدعم والتواصل

- **المطور**: Ahmed Madi
- **البريد الإلكتروني**: dev.amadi7@gmail.com
- **GitHub**: https://github.com/ahmed-madi/common

---

## 🔄 التحديثات الأخيرة

### الإصدار 0.0.1

- إطلاق النسخة الأولى
- نظام إدارة موارد بشرية متكامل
- واجهات برمجية RESTful API
- نظام المصادقة JWT
- دعم Firebase Cloud Messaging
- واجهة مستخدم حديثة

---

**ملاحظة**: هذا التطبيق قيد التطوير النشط. يرجى الرجوع إلى التوثيق بانتظام للحصول على آخر التحديثات.
