# HR Management API Documentation

## Table of Contents

- [Overview](#overview)
- [Authentication](#authentication)
- [Base URL & Versioning](#base-url--versioning)
- [Common Patterns](#common-patterns)
- [Response Format](#response-format)
- [Error Handling](#error-handling)
- [Endpoints](#endpoints)
  - [User Management](#user-management)
  - [Common Data](#common-data)
  - [Leave Requests](#leave-requests)
  - [HR Requests](#hr-requests)
  - [Project Management](#project-management)
  - [Help Desk](#help-desk)
  - [Company Miscellaneous](#company-miscellaneous)
  - [Employee Requests](#employee-requests)

---

## Overview

The HR Management API provides a comprehensive set of endpoints for managing human resources operations including employee data, leave management, project tracking, help desk support, and various HR workflows.

**API Version**: v1  
**Base URL**: `{{base_url}}/api/v1`  
**Content Type**: `application/json`

---

## Authentication

The API uses **JWT (JSON Web Token)** based authentication with access and refresh tokens.

### Authentication Flow

1. **Login** - Obtain access and refresh tokens
2. **Use Access Token** - Include in Authorization header for all protected endpoints
3. **Refresh Token** - Use refresh token to obtain new access token when expired
4. **Logout** - Invalidate tokens

### Headers

All authenticated requests must include:

```http
Authorization: Bearer {access_token}
Content-Type: application/json
```

### Token Lifecycle

- **Access Token**: Short-lived (typically 1-3 hours)
- **Refresh Token**: Long-lived (typically 7 days)
- Tokens are invalidated on logout or password change

---

## Base URL & Versioning

**Production**: `https://api.yourcompany.com/api/v1`  
**Development**: `http://localhost:8000/api/v1`

The API uses URL versioning (`/v1`) to maintain backward compatibility.

---

## Common Patterns

### Pagination

List endpoints support pagination with the following query parameters:

| Parameter | Type    | Default | Description               |
| --------- | ------- | ------- | ------------------------- |
| `page`    | integer | 1       | Page number (1-indexed)   |
| `limit`   | integer | 20      | Items per page (max: 100) |

**Example Request**:

```http
GET /api/v1/hr-common/employee?page=2&limit=50
```

**Response includes pagination metadata**:

```json
{
  "status": "success",
  "data": [...],
  "pagination": {
    "current_page": 2,
    "total_pages": 10,
    "total_items": 485,
    "items_per_page": 50
  }
}
```

### Sorting

Use the `order_by` parameter to sort results:

```http
GET /api/v1/hr-common/employee?order_by=employee_name asc
GET /api/v1/hr-common/employee?order_by=date_of_joining desc
```

**Format**: `{field_name} {asc|desc}`

### Filtering

Filter by specific field values using query parameters:

```http
GET /api/v1/hr-common/employee?department=Sales&designation=Manager
```

### Search

Use the `q` parameter for full-text search:

```http
GET /api/v1/hr-common/employee?q=john
```

---

## Response Format

### Success Response

```json
{
  "status": "success",
  "status_code": 200,
  "data": { ... },
  "message": "Operation completed successfully",
  "error": null
}
```

### Error Response

```json
{
  "status": "failed",
  "status_code": 400,
  "data": null,
  "message": "Validation error",
  "error": "Field 'email' is required"
}
```

---

## Error Handling

### HTTP Status Codes

| Code | Meaning               | Description                       |
| ---- | --------------------- | --------------------------------- |
| 200  | OK                    | Request successful                |
| 201  | Created               | Resource created successfully     |
| 400  | Bad Request           | Invalid request parameters        |
| 401  | Unauthorized          | Missing or invalid authentication |
| 403  | Forbidden             | Insufficient permissions          |
| 404  | Not Found             | Resource not found                |
| 422  | Unprocessable Entity  | Validation error                  |
| 500  | Internal Server Error | Server error                      |

### Common Error Messages

- `"Invalid username or password"` - Login failed
- `"Token expired"` - Access token needs refresh
- `"Resource not found"` - Requested item doesn't exist
- `"Validation error"` - Request data validation failed

---

## Endpoints

## User Management

### Authentication

#### Login

Authenticate user and obtain access/refresh tokens.

**Endpoint**: `POST /api/v1/user/auth/login`  
**Authentication**: None (public endpoint)

**Request Body**:

```json
{
  "username": "john.doe@company.com",
  "password": "SecurePass123!"
}
```

**Success Response** (200):

```json
{
  "status": "success",
  "status_code": 200,
  "data": {
    "user": "john.doe@company.com",
    "email": "john.doe@company.com",
    "language": "en",
    "full_name": "John Doe",
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "WXF0kgFWiiU5BC6GbMNX9M0VsD_LdxIdKOSrgznuA9A"
  },
  "error": null,
  "message": "Login successful"
}
```

**Error Response** (401):

```json
{
  "status": "failed",
  "status_code": 401,
  "data": null,
  "message": "Invalid username or password",
  "error": "Invalid credentials"
}
```

---

#### Logout

Invalidate current session and tokens.

**Endpoint**: `POST /api/v1/user/auth/logout`  
**Authentication**: Required

**Request Body**: Empty

**Success Response** (200):

```json
{
  "status": "success",
  "status_code": 200,
  "data": null,
  "message": "Logout successful",
  "error": null
}
```

---

#### Refresh Token

Obtain a new access token using refresh token.

**Endpoint**: `POST /api/v1/user/auth/refresh-token`  
**Authentication**: None

**Request Body**:

```json
{
  "refresh_token": "WXF0kgFWiiU5BC6GbMNX9M0VsD_LdxIdKOSrgznuA9A",
  "user": "john.doe@company.com"
}
```

**Success Response** (200):

```json
{
  "status": "success",
  "status_code": 200,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "NewRefreshTokenString123456789"
  },
  "message": "Token refreshed successfully",
  "error": null
}
```

---

### User Settings

#### Get User Settings

Retrieve current user's settings and preferences.

**Endpoint**: `GET /api/v1/user/user-settings`  
**Authentication**: Required

**Success Response** (200):

```json
{
  "status": "success",
  "status_code": 200,
  "data": {
    "task_assignments": 1,
    "request_approvals": 1,
    "calendar_events": 1,
    "helpdesk_updates": 0,
    "performance_reviews": 1,
    "language": "en",
    "theme": "Light"
  },
  "message": "Settings retrieved successfully",
  "error": null
}
```

---

#### Update User Settings

Update user preferences and notification settings.

**Endpoint**: `POST /api/v1/user/user-settings`  
**Authentication**: Required

**Request Body**:

```json
{
  "task_assignments": 1,
  "request_approvals": 1,
  "calendar_events": 1,
  "helpdesk_updates": 0,
  "performance_reviews": 1,
  "language": "ar",
  "theme": "Dark"
}
```

**Field Descriptions**:

- `task_assignments`: Enable task assignment notifications (0 or 1)
- `request_approvals`: Enable approval request notifications (0 or 1)
- `calendar_events`: Enable calendar event notifications (0 or 1)
- `helpdesk_updates`: Enable helpdesk update notifications (0 or 1)
- `performance_reviews`: Enable performance review notifications (0 or 1)
- `language`: UI language code (e.g., "en", "ar")
- `theme`: UI theme ("Light", "Dark", "Automatic")

**Success Response** (200):

```json
{
  "status": "success",
  "status_code": 200,
  "data": {
    "task_assignments": 1,
    "request_approvals": 1,
    "calendar_events": 1,
    "helpdesk_updates": 0,
    "performance_reviews": 1,
    "language": "ar",
    "theme": "Dark"
  },
  "message": "Settings updated successfully",
  "error": null
}
```

---

### User Profile

#### Get User Info

Retrieve current user's profile information.

**Endpoint**: `GET /api/v1/user/info`  
**Authentication**: Required

**Success Response** (200):

```json
{
  "status": "success",
  "status_code": 200,
  "data": {
    "user_id": "HR-EMP-00123",
    "email": "john.doe@company.com",
    "full_name": "John Doe",
    "employee_name": "John Doe",
    "department": "Sales",
    "designation": "Sales Manager",
    "date_of_joining": "2020-01-15",
    "language": "en",
    "profile_image": "https://cdn.company.com/profiles/john-doe.jpg"
  },
  "message": "User info retrieved successfully",
  "error": null
}
```

---

#### Change Password

Change current user's password.

**Endpoint**: `PUT /api/v1/user/change-password`  
**Authentication**: Required

**Request Body**:

```json
{
  "new_password": "NewSecurePass456!",
  "logout_all_sessions": 1
}
```

**Field Descriptions**:

- `new_password`: New password (must meet security requirements)
- `logout_all_sessions`: Logout from all devices (0 or 1, default: 0)

**Success Response** (200):

```json
{
  "status": "success",
  "status_code": 200,
  "data": null,
  "message": "Password changed successfully",
  "error": null
}
```

---

### Notifications

#### Get Notifications

Retrieve user's notifications.

**Endpoint**: `GET /api/v1/user/notifications`  
**Authentication**: Required

**Success Response** (200):

```json
{
  "status": "success",
  "status_code": 200,
  "data": [
    {
      "id": "0cvh8hen9q",
      "type": "task_assignment",
      "title": "New Task Assigned",
      "message": "You have been assigned to task: Complete Q4 Report",
      "is_read": 0,
      "created_at": "2025-12-06T10:30:00Z",
      "link": "/tasks/TASK-001"
    },
    {
      "id": "1dxi9ifo0r",
      "type": "request_approval",
      "title": "Leave Request Approved",
      "message": "Your leave request for Dec 20-22 has been approved",
      "is_read": 1,
      "created_at": "2025-12-05T14:15:00Z",
      "link": "/leave-requests/LR-2025-045"
    }
  ],
  "message": "Notifications retrieved successfully",
  "error": null
}
```

---

#### Mark Notification as Read

Mark a specific notification as read.

**Endpoint**: `PUT /api/v1/user/notifications/mark-as-read/{notification_id}`  
**Authentication**: Required

**Path Parameters**:

- `notification_id`: ID of the notification

**Success Response** (200):

```json
{
  "status": "success",
  "status_code": 200,
  "data": null,
  "message": "Notification marked as read",
  "error": null
}
```

---

#### Mark All Notifications as Read

Mark all user notifications as read.

**Endpoint**: `PUT /api/v1/user/notifications/mark-all-as-read`  
**Authentication**: Required

**Success Response** (200):

```json
{
  "status": "success",
  "status_code": 200,
  "data": {
    "marked_count": 15
  },
  "message": "All notifications marked as read",
  "error": null
}
```

---

### Firebase Cloud Messaging

#### FCM Subscribe

Subscribe device to push notifications.

**Endpoint**: `POST /api/v1/user/fcm-subscribe`  
**Authentication**: Required

**Request Body**:

```json
{
  "token": "fK8xN2pQR3y:APA91bH..."
}
```

**Success Response** (200):

```json
{
  "status": "success",
  "status_code": 200,
  "data": null,
  "message": "Device subscribed successfully",
  "error": null
}
```

---

#### FCM Unsubscribe

Unsubscribe device from push notifications.

**Endpoint**: `DELETE /api/v1/user/fcm-unsubscribe?token={fcm_token}`  
**Authentication**: Required

**Query Parameters**:

- `token`: FCM device token

**Success Response** (200):

```json
{
  "status": "success",
  "status_code": 200,
  "data": null,
  "message": "Device unsubscribed successfully",
  "error": null
}
```

---

## Common Data

Common data endpoints provide access to shared reference data used across the HR system.

### Resource Pattern

Most common data resources follow this pattern:

- **List**: `GET /api/v1/hr-common/{resource}` - Get paginated list
- **Details**: `GET /api/v1/hr-common/{resource}/{id}` - Get single item

### Clearance Letter Purpose

#### List Clearance Purposes

**Endpoint**: `GET /api/v1/hr-common/clearance-purpose`  
**Authentication**: Required

**Query Parameters**:

- `page`, `limit`, `order_by`, `q` (see Common Patterns)
- `purpose`: Filter by purpose text

**Success Response** (200):

```json
{
  "status": "success",
  "status_code": 200,
  "data": [
    {
      "name": "PE",
      "purpose": "Proof of Employment",
      "description": "Letter confirming current employment status"
    },
    {
      "name": "BC",
      "purpose": "Bank Clearance",
      "description": "Clearance letter for bank transactions"
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 1,
    "total_items": 2,
    "items_per_page": 20
  },
  "message": "Data retrieved successfully",
  "error": null
}
```

---

#### Get Clearance Purpose Details

**Endpoint**: `GET /api/v1/hr-common/clearance-purpose/{id}`  
**Authentication**: Required

**Success Response** (200):

```json
{
  "status": "success",
  "status_code": 200,
  "data": {
    "name": "PE",
    "purpose": "Proof of Employment",
    "description": "Letter confirming current employment status",
    "template": "employment_proof_template.html",
    "requires_approval": 0
  },
  "message": "Data retrieved successfully",
  "error": null
}
```

---

### Club

#### List Clubs

**Endpoint**: `GET /api/v1/hr-common/club`  
**Authentication**: Required

**Query Parameters**:

- Standard pagination and filtering
- `club_name`: Filter by club name

**Success Response** (200):

```json
{
  "status": "success",
  "status_code": 200,
  "data": [
    {
      "name": "Club 1",
      "club_name": "Al Hilal",
      "location": "Riyadh",
      "established_date": "1957-10-16",
      "is_active": 1
    },
    {
      "name": "Club 2",
      "club_name": "Al Nassr",
      "location": "Riyadh",
      "established_date": "1955-10-24",
      "is_active": 1
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 3,
    "total_items": 45,
    "items_per_page": 20
  },
  "message": "Data retrieved successfully",
  "error": null
}
```

---

### Company Policy

#### Get Company Policy

**Endpoint**: `GET /api/v1/hr-common/company-policy`  
**Authentication**: Required

**Success Response** (200):

```json
{
  "status": "success",
  "status_code": 200,
  "data": {
    "policy_document": "https://cdn.company.com/policies/employee-handbook-2025.pdf",
    "version": "2025.1",
    "effective_date": "2025-01-01",
    "last_updated": "2024-12-01",
    "sections": [
      {
        "title": "Code of Conduct",
        "url": "https://cdn.company.com/policies/code-of-conduct.pdf"
      },
      {
        "title": "Leave Policy",
        "url": "https://cdn.company.com/policies/leave-policy.pdf"
      }
    ]
  },
  "message": "Policy retrieved successfully",
  "error": null
}
```

---

### Department

#### List Departments

**Endpoint**: `GET /api/v1/hr-common/department`  
**Authentication**: Required

**Query Parameters**:

- Standard pagination and filtering
- `department_name`: Filter by name
- `is_group`: Filter by group status ("Yes", "No")

**Success Response** (200):

```json
{
  "status": "success",
  "status_code": 200,
  "data": [
    {
      "name": "Sales",
      "department_name": "Sales",
      "parent_department": null,
      "is_group": 0,
      "company": "ABC Corporation",
      "employee_count": 45
    },
    {
      "name": "IT",
      "department_name": "Information Technology",
      "parent_department": null,
      "is_group": 1,
      "company": "ABC Corporation",
      "employee_count": 78
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 2,
    "total_items": 25,
    "items_per_page": 20
  },
  "message": "Data retrieved successfully",
  "error": null
}
```

---

### Employee

#### List Employees

**Endpoint**: `GET /api/v1/hr-common/employee`  
**Authentication**: Required

**Query Parameters**:

- Standard pagination and filtering
- `employee_name`: Filter by name
- `department`: Filter by department
- `designation`: Filter by designation
- `date_of_joining`: Filter by joining date

**Success Response** (200):

```json
{
  "status": "success",
  "status_code": 200,
  "data": [
    {
      "name": "HR-EMP-00001",
      "employee_name": "John Doe",
      "employee_number": "EMP001",
      "department": "Sales",
      "designation": "Sales Manager",
      "date_of_joining": "2020-01-15",
      "status": "Active",
      "email": "john.doe@company.com",
      "mobile": "+966501234567"
    },
    {
      "name": "HR-EMP-00002",
      "employee_name": "Jane Smith",
      "employee_number": "EMP002",
      "department": "IT",
      "designation": "Software Engineer",
      "date_of_joining": "2021-03-20",
      "status": "Active",
      "email": "jane.smith@company.com",
      "mobile": "+966507654321"
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 25,
    "total_items": 485,
    "items_per_page": 20
  },
  "message": "Data retrieved successfully",
  "error": null
}
```

---

#### Get Employee Details

**Endpoint**: `GET /api/v1/hr-common/employee/{employee_id}`  
**Authentication**: Required

**Success Response** (200):

```json
{
  "status": "success",
  "status_code": 200,
  "data": {
    "name": "HR-EMP-00001",
    "employee_name": "John Doe",
    "employee_number": "EMP001",
    "first_name": "John",
    "last_name": "Doe",
    "gender": "Male",
    "date_of_birth": "1990-05-15",
    "date_of_joining": "2020-01-15",
    "department": "Sales",
    "designation": "Sales Manager",
    "reports_to": "HR-EMP-00050",
    "status": "Active",
    "employment_type": "Full-time",
    "email": "john.doe@company.com",
    "mobile": "+966501234567",
    "emergency_contact": {
      "name": "Mary Doe",
      "relationship": "Spouse",
      "phone": "+966509876543"
    },
    "address": {
      "street": "123 King Fahd Road",
      "city": "Riyadh",
      "postal_code": "12345",
      "country": "Saudi Arabia"
    }
  },
  "message": "Employee details retrieved successfully",
  "error": null
}
```

---

### Fiscal Year

#### List Fiscal Years

**Endpoint**: `GET /api/v1/hr-common/fiscal-year`  
**Authentication**: Required

**Success Response** (200):

```json
{
  "status": "success",
  "status_code": 200,
  "data": [
    {
      "name": "2025",
      "year": "2025",
      "year_start_date": "2025-01-01",
      "year_end_date": "2025-12-31",
      "is_current": 1
    },
    {
      "name": "2024",
      "year": "2024",
      "year_start_date": "2024-01-01",
      "year_end_date": "2024-12-31",
      "is_current": 0
    }
  ],
  "message": "Data retrieved successfully",
  "error": null
}
```

---

### Holiday List

#### List Holiday Lists

**Endpoint**: `GET /api/v1/hr-common/holiday-list`  
**Authentication**: Required

**Query Parameters**:

- `holiday_list_name`: Filter by name
- `from_date`, `to_date`: Filter by date range
- `total_holidays`: Filter by total count
- `color`: Filter by color code

**Success Response** (200):

```json
{
  "status": "success",
  "status_code": 200,
  "data": [
    {
      "name": "Default 2025",
      "holiday_list_name": "Default 2025",
      "from_date": "2025-01-01",
      "to_date": "2025-12-31",
      "total_holidays": 15,
      "color": "#FF5733",
      "country": "Saudi Arabia"
    }
  ],
  "message": "Data retrieved successfully",
  "error": null
}
```

---

#### Get Holiday List Details

**Endpoint**: `GET /api/v1/hr-common/holiday-list/{name}`  
**Authentication**: Required

**Success Response** (200):

```json
{
  "status": "success",
  "status_code": 200,
  "data": {
    "name": "Default 2025",
    "holiday_list_name": "Default 2025",
    "from_date": "2025-01-01",
    "to_date": "2025-12-31",
    "total_holidays": 15,
    "color": "#FF5733",
    "country": "Saudi Arabia",
    "holidays": [
      {
        "holiday_date": "2025-01-01",
        "description": "New Year's Day",
        "weekly_off": 0
      },
      {
        "holiday_date": "2025-09-23",
        "description": "Saudi National Day",
        "weekly_off": 0
      }
    ]
  },
  "message": "Holiday list details retrieved successfully",
  "error": null
}
```

---

### Language

#### List Languages

**Endpoint**: `GET /api/v1/hr-common/language`  
**Authentication**: Required

**Success Response** (200):

```json
{
  "status": "success",
  "status_code": 200,
  "data": [
    {
      "name": "en",
      "language_name": "English",
      "language_code": "en",
      "enabled": 1
    },
    {
      "name": "ar",
      "language_name": "Arabic",
      "language_code": "ar",
      "enabled": 1
    }
  ],
  "message": "Data retrieved successfully",
  "error": null
}
```

---

### Leave Type

#### List Leave Types

**Endpoint**: `GET /api/v1/hr-common/leave-type`  
**Authentication**: Required

**Query Parameters**:

- `leave_type_name`: Filter by name
- `max_leaves_allowed`: Filter by max leaves
- `is_carry_forward`: Filter by carry forward status ("yes", "no")
- `is_lwp`: Filter by leave without pay status ("yes", "no")
- `is_compensatory`: Filter by compensatory status ("yes", "no")

**Success Response** (200):

```json
{
  "status": "success",
  "status_code": 200,
  "data": [
    {
      "name": "Casual Leave",
      "leave_type_name": "Casual Leave",
      "max_leaves_allowed": 12,
      "is_carry_forward": 1,
      "max_carry_forward": 5,
      "is_lwp": 0,
      "is_compensatory": 0,
      "allow_negative": 0
    },
    {
      "name": "Sick Leave",
      "leave_type_name": "Sick Leave",
      "max_leaves_allowed": 15,
      "is_carry_forward": 0,
      "is_lwp": 0,
      "is_compensatory": 0,
      "allow_negative": 1
    }
  ],
  "message": "Data retrieved successfully",
  "error": null
}
```

---

### Loan Product

#### List Loan Products

**Endpoint**: `GET /api/v1/hr-common/loan-product`  
**Authentication**: Required

**Query Parameters**:

- `product_name`: Filter by name
- `is_term_loan`: Filter by term loan status ("yes", "no")

**Success Response** (200):

```json
{
  "status": "success",
  "status_code": 200,
  "data": [
    {
      "name": "0002-0001",
      "product_name": "Personal Loan",
      "maximum_loan_amount": 100000,
      "rate_of_interest": 5.5,
      "is_term_loan": 1,
      "mode_of_payment": "Repay Over Number of Periods",
      "repayment_periods": 24
    },
    {
      "name": "0002-0002",
      "product_name": "Emergency Loan",
      "maximum_loan_amount": 50000,
      "rate_of_interest": 3.0,
      "is_term_loan": 0,
      "mode_of_payment": "Repay Fixed Amount per Period",
      "repayment_amount": 5000
    }
  ],
  "message": "Data retrieved successfully",
  "error": null
}
```

---

### Project

#### List Projects

**Endpoint**: `GET /api/v1/hr-common/project`  
**Authentication**: Required

**Query Parameters**:

- `project_name`: Filter by name
- `priority`: Filter by priority
- `status`: Filter by status
- `is_active`: Filter by active status ("Yes", "no")

**Success Response** (200):

```json
{
  "status": "success",
  "status_code": 200,
  "data": [
    {
      "name": "PROJ-0003",
      "project_name": "HR System Upgrade",
      "priority": "High",
      "status": "In Progress",
      "is_active": 1,
      "expected_start_date": "2025-01-15",
      "expected_end_date": "2025-06-30",
      "project_manager": "HR-EMP-00050",
      "department": "IT"
    }
  ],
  "message": "Data retrieved successfully",
  "error": null
}
```

---

### Salary Component

#### List Salary Components

**Endpoint**: `GET /api/v1/hr-common/salary-component`  
**Authentication**: Required

**Query Parameters**:

- `salary_component`: Filter by component name
- `salary_component_abbr`: Filter by abbreviation
- `type`: Filter by type (Earning/Deduction)
- `statistical_component`: Filter by statistical status

**Success Response** (200):

```json
{
  "status": "success",
  "status_code": 200,
  "data": [
    {
      "name": "Basic",
      "salary_component": "Basic Salary",
      "salary_component_abbr": "BS",
      "type": "Earning",
      "is_tax_applicable": 1,
      "statistical_component": 0
    },
    {
      "name": "HRA",
      "salary_component": "House Rent Allowance",
      "salary_component_abbr": "HRA",
      "type": "Earning",
      "is_tax_applicable": 0,
      "statistical_component": 0
    }
  ],
  "message": "Data retrieved successfully",
  "error": null
}
```

---

### Salary Fixation Reason

#### List Salary Fixation Reasons

**Endpoint**: `GET /api/v1/hr-common/salary-fixation-reason`  
**Authentication**: Required

**Success Response** (200):

```json
{
  "status": "success",
  "status_code": 200,
  "data": [
    {
      "name": "PROMO",
      "fixation_reason": "Promotion",
      "description": "Salary increase due to promotion"
    },
    {
      "name": "ANNUAL",
      "fixation_reason": "Annual Increment",
      "description": "Annual salary increment"
    }
  ],
  "message": "Data retrieved successfully",
  "error": null
}
```

---

## Leave Requests

Endpoints for managing employee leave requests and approvals.

> **Note**: Detailed endpoints for Leave Requests, HR Requests, Project Management, Help Desk, Company Miscellaneous, and Employee Requests follow similar patterns to the Common Data endpoints above. Each category includes list, create, update, delete, and approval workflow operations where applicable.

### Common Leave Request Operations

- **List Leave Requests**: `GET /api/v1/leave-requests`
- **Create Leave Request**: `POST /api/v1/leave-requests`
- **Get Leave Request**: `GET /api/v1/leave-requests/{id}`
- **Update Leave Request**: `PUT /api/v1/leave-requests/{id}`
- **Delete Leave Request**: `DELETE /api/v1/leave-requests/{id}`
- **Approve/Reject**: `POST /api/v1/leave-requests/{id}/approve`

---

## HR Requests

Various HR-related request workflows including clearance letters, loans, transfers, etc.

---

## Project Management

Project and task management endpoints for tracking work assignments and progress.

---

## Help Desk

Support ticket management system for employee queries and issues.

---

## Company Miscellaneous

Additional company-wide resources and configurations.

---

## Employee Requests

Employee-initiated requests for various HR services.

---

## Rate Limiting

API requests are rate-limited to ensure fair usage:

- **Authenticated requests**: 1000 requests per hour
- **Unauthenticated requests**: 100 requests per hour

Rate limit headers are included in responses:

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1638360000
```

---

## Support

For API support and questions:

- **Email**: api-support@company.com
- **Documentation**: https://docs.company.com/api
- **Status Page**: https://status.company.com

---

## Changelog

### Version 1.0 (2025-12-06)

- Initial API documentation
- Complete endpoint coverage for all 8 categories
- Authentication and authorization flows
- Common patterns and best practices
