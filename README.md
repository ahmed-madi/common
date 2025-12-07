# Common Customization - Frappe HR Management App

A comprehensive HR management application built on Frappe Framework, providing RESTful APIs and an integrated management system for administrative and human resources operations.

**English Version | [النسخة العربية](README.ar.md)**

## 📋 Overview

**Common Customization** is an advanced Frappe application that provides:

- Comprehensive HR Management System
- RESTful API with JWT authentication
- Leave and administrative request management
- Help Desk system
- Project and task management
- Firebase Cloud Messaging (FCM) notifications
- Comprehensive reports and analytics

**Developer**: Ahmed Madi  
**Email**: dev.amadi7@gmail.com  
**Version**: 0.0.1  
**License**: MIT

---

## 🚀 Installation

### Prerequisites

- Frappe Framework (version 14 or newer)
- Python 3.10+
- MariaDB/MySQL
- Node.js 16+

### Installation Steps

1. **Navigate to apps directory**

```bash
cd frappe-bench
```

2. **Get the app**

```bash
bench get-app https://github.com/ahmed-madi/common.git
```

3. **Install app on site**

```bash
bench --site [site-name] install-app common
```

4. **Run migrations**

```bash
bench --site [site-name] migrate
```

5. **Restart services**

```bash
bench restart
```

---

## 📦 Key Features

### 1. User Management & Authentication

- **Login/Logout** with JWT tokens
- **Refresh Tokens**
- **Personal settings management**
- **Password change**
- **Real-time notifications**

### 2. Human Resources Management

#### Administrative Requests

- **Leave Applications**
- **Compensatory Leave Requests**
- **Remote Work Requests**
- **Overtime Requests**
- **Resignation Requests**
- **Loan Applications**

#### Certificates & Documents

- **Salary Certificates**
- **Salary Identification Letters**
- **Clearance Letters**
- **Document Requests**

#### Allowances & Bonuses

- **Allowance Requests**
- **Bonus Requests**
- **Education Allowance**
- **End of Service Awards**

### 3. Common Data Management

- **Departments**
- **Designations**
- **Branches**
- **Clubs**
- **Nationalities**
- **Company Policies**

### 4. Project Management System

- **Project Management**
- **Tasks**
- **Time Tracking**
- **Reports**

### 5. Help Desk System

- **Support Tickets**
- **Status Tracking**
- **Priorities**
- **Comments & Attachments**

### 6. Notifications

- **In-app Notifications**
- **Firebase Cloud Messaging** (Push Notifications)
- **Customizable notification settings**

---

## 🔌 API Usage

### Base URL

```
http://your-domain.com/api/v1
```

### Authentication

All protected requests require the authentication header:

```http
Authorization: Bearer {access_token}
Content-Type: application/json
```

### Example: Login

**Request:**

```bash
curl -X POST http://your-domain.com/api/v1/user/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user@example.com",
    "password": "your_password"
  }'
```

**Response:**

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

### Example: Get Employee List

**Request:**

```bash
curl -X GET "http://your-domain.com/api/v1/hr-common/employee?page=1&limit=20" \
  -H "Authorization: Bearer {access_token}"
```

### Example: Create Leave Application

**Request:**

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

### Main Endpoints

#### User Management

- `POST /api/v1/user/auth/login` - Login
- `POST /api/v1/user/auth/logout` - Logout
- `POST /api/v1/user/auth/refresh-token` - Refresh token
- `GET /api/v1/user/info` - User information
- `PUT /api/v1/user/change-password` - Change password
- `GET /api/v1/user/notifications` - Notifications

#### Common Data

- `GET /api/v1/hr-common/employee` - Employee list
- `GET /api/v1/hr-common/department` - Departments
- `GET /api/v1/hr-common/designation` - Designations
- `GET /api/v1/hr-common/branch` - Branches
- `GET /api/v1/hr-common/club` - Clubs

#### HR Requests

- `GET /api/v1/hr-requests/leave-application` - Leave applications
- `POST /api/v1/hr-requests/leave-application` - Create leave application
- `GET /api/v1/hr-requests/overtime-request` - Overtime requests
- `GET /api/v1/hr-requests/remote-work-request` - Remote work requests
- `GET /api/v1/hr-requests/salary-certificate` - Salary certificates

#### Projects

- `GET /api/v1/project-management/project` - Project list
- `GET /api/v1/project-management/task` - Tasks
- `POST /api/v1/project-management/task` - Create task

#### Help Desk

- `GET /api/v1/help-desk/issue` - Support tickets
- `POST /api/v1/help-desk/issue` - Create ticket
- `PUT /api/v1/help-desk/issue/{id}` - Update ticket

For complete API documentation, refer to [API_Documentation.md](common/api/API_Documentation.md).

---

## ⚙️ Configuration

### CSS Customization

The app includes a custom CSS file:

```python
app_include_css = [
    "/assets/common/css/common-style3.css",
]
```

### DocType Overrides

The following standard DocTypes are overridden:

- `Leave Application` - Leave applications
- `Leave Type` - Leave types
- `Compensatory Leave Request` - Compensatory leave requests
- `Loan Application` - Loan applications
- `Notification` - Notifications
- `Employee Checkin` - Employee check-ins

### Custom Permissions

```python
permission_query_conditions = {
    "Employee HR Feedback": "common.permissions.employee_hr_feedback.get_permission_query_conditions",
}

has_permission = {
    "Employee HR Feedback": "common.permissions.employee_hr_feedback.has_permission",
}
```

---

## 📱 HR Service (Frontend)

The app includes a modern user interface built with:

- React/Vue.js
- TypeScript
- Modern UI Components

Access the interface at:

```
http://your-domain.com/hr-services/
```

---

## 🔧 Development

### Project Structure

```
common/
├── common/
│   ├── api/                    # API endpoints
│   │   ├── controllers/        # Controllers
│   │   ├── routes/             # URL Routes
│   │   └── utils/              # Utilities
│   ├── common_customization/   # Main DocTypes
│   │   └── doctype/
│   ├── hr_fcm/                 # Firebase Cloud Messaging
│   ├── hr_support/             # Help Desk system
│   ├── overrides/              # DocType overrides
│   ├── permissions/            # Permission logic
│   ├── public/                 # Static files
│   └── hooks.py                # Frappe Hooks
├── hr-service/                 # Frontend Application
└── README.md
```

### Running Development Environment

```bash
# Start development server
bench start

# Watch for changes
bench watch
```

### Adding a New DocType

1. Create DocType from Frappe interface
2. Add Controller in `common/common_customization/doctype/`
3. Add API Route in `common/api/routes/`
4. Add Controller in `common/api/controllers/`

---

## 📊 Reports & Analytics

The app provides comprehensive reports:

- Attendance reports
- Leave reports
- Salary reports
- Performance reports
- Project reports

---

## 🔐 Security

- **JWT Authentication** - Secure token-based authentication
- **Role-Based Access Control** - Permission control by roles
- **Permission Queries** - Custom permission queries
- **Secure Password Handling** - Secure password management
- **API Rate Limiting** - Request rate limiting

---

## 🧪 Testing

```bash
# Run tests
bench --site [site-name] run-tests --app common

# Test specific module
bench --site [site-name] run-tests --app common --module common.tests.test_leave_application
```

---

## 📚 Additional Resources

- **Complete API Documentation**: [API_Documentation.md](common/api/API_Documentation.md)
- **Postman Collection**: [HR Final Endpoints.postman_collection.json](common/api/HR%20Final%20Endpoints.postman_collection.json)
- **Frappe Documentation**: https://frappeframework.com/docs
- **ERPNext HR Module**: https://docs.erpnext.com/docs/user/manual/en/human-resources

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the project
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](license.txt) file for details.

---

## 📞 Support & Contact

- **Developer**: Ahmed Madi
- **Email**: dev.amadi7@gmail.com
- **GitHub**: https://github.com/ahmed-madi/common

---

## 🔄 Recent Updates

### Version 0.0.1

- Initial release
- Comprehensive HR management system
- RESTful API
- JWT authentication system
- Firebase Cloud Messaging support
- Modern user interface

---

**Note**: This application is under active development. Please refer to the documentation regularly for the latest updates.
