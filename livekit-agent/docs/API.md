# API Documentation

## Overview

The Switchboard Assistant API provides RESTful endpoints for managing employees, departments, company settings, call logs, and messages. The API is built with FastAPI and provides automatic OpenAPI documentation.

## Base URL

- Development: `http://localhost:8000`
- Production: `https://your-domain.com/api`

## Authentication

The API uses Supabase Auth for authentication. Include the JWT token in the Authorization header:

```
Authorization: Bearer <jwt_token>
```

## Response Format

All API responses follow a consistent format:

### Success Response
```json
{
  "data": <response_data>,
  "message": "Success message",
  "status": "success"
}
```

### Error Response
```json
{
  "error": "Error message",
  "status": "error",
  "code": "ERROR_CODE"
}
```

## Endpoints

### Employees

#### GET /api/employees
Get all employees with optional filtering.

**Query Parameters:**
- `department_id` (optional): Filter by department
- `status` (optional): Filter by status (available, busy, offline)
- `search` (optional): Search by name or email
- `limit` (optional): Number of results (default: 100)
- `offset` (optional): Pagination offset (default: 0)

**Response:**
```json
{
  "data": [
    {
      "id": "uuid",
      "name": "John Smith",
      "phone": "+1234567890",
      "email": "john@company.com",
      "department_id": "uuid",
      "department": {
        "id": "uuid",
        "name": "Sales"
      },
      "office": "Main Office",
      "roles": ["sales_rep", "manager"],
      "status": "available",
      "availability_hours": {
        "monday": {"start": "09:00", "end": "17:00"},
        "tuesday": {"start": "09:00", "end": "17:00"}
      },
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "limit": 100,
  "offset": 0
}
```

#### GET /api/employees/{employee_id}
Get a specific employee by ID.

**Response:**
```json
{
  "data": {
    "id": "uuid",
    "name": "John Smith",
    "phone": "+1234567890",
    "email": "john@company.com",
    "department_id": "uuid",
    "department": {
      "id": "uuid",
      "name": "Sales"
    },
    "office": "Main Office",
    "roles": ["sales_rep", "manager"],
    "status": "available",
    "availability_hours": {
      "monday": {"start": "09:00", "end": "17:00"}
    },
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

#### POST /api/employees
Create a new employee.

**Request Body:**
```json
{
  "name": "Jane Doe",
  "phone": "+1234567891",
  "email": "jane@company.com",
  "department_id": "uuid",
  "office": "Branch Office",
  "roles": ["support_rep"],
  "status": "available",
  "availability_hours": {
    "monday": {"start": "09:00", "end": "17:00"},
    "tuesday": {"start": "09:00", "end": "17:00"}
  }
}
```

**Response:**
```json
{
  "data": {
    "id": "uuid",
    "name": "Jane Doe",
    "phone": "+1234567891",
    "email": "jane@company.com",
    "department_id": "uuid",
    "office": "Branch Office",
    "roles": ["support_rep"],
    "status": "available",
    "availability_hours": {
      "monday": {"start": "09:00", "end": "17:00"}
    },
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  },
  "message": "Employee created successfully"
}
```

#### PUT /api/employees/{employee_id}
Update an existing employee.

**Request Body:**
```json
{
  "name": "Jane Smith",
  "status": "busy",
  "availability_hours": {
    "monday": {"start": "10:00", "end": "18:00"}
  }
}
```

#### DELETE /api/employees/{employee_id}
Delete an employee.

**Response:**
```json
{
  "message": "Employee deleted successfully"
}
```

### Departments

#### GET /api/departments
Get all departments.

**Response:**
```json
{
  "data": [
    {
      "id": "uuid",
      "name": "Sales",
      "description": "Sales and business development",
      "available_hours": {
        "monday": {"start": "09:00", "end": "17:00"},
        "friday": {"start": "09:00", "end": "17:00"}
      },
      "routing_priority": 1,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

#### POST /api/departments
Create a new department.

**Request Body:**
```json
{
  "name": "Support",
  "description": "Customer support and technical assistance",
  "available_hours": {
    "monday": {"start": "08:00", "end": "20:00"},
    "sunday": {"start": "10:00", "end": "18:00"}
  },
  "routing_priority": 2
}
```

#### PUT /api/departments/{department_id}
Update a department.

#### DELETE /api/departments/{department_id}
Delete a department.

### Company Settings

#### GET /api/company
Get company information and settings.

**Response:**
```json
{
  "data": {
    "id": "uuid",
    "company_name": "Your Company",
    "greeting_message": "Thank you for calling. How may I direct your call?",
    "business_hours": {
      "monday": {"start": "09:00", "end": "17:00"},
      "friday": {"start": "09:00", "end": "17:00"}
    },
    "settings": {
      "language": "en",
      "timezone": "America/New_York",
      "max_call_duration": 3600,
      "enable_recording": true,
      "warm_transfer_enabled": true
    },
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

#### PUT /api/company
Update company settings.

**Request Body:**
```json
{
  "company_name": "Updated Company Name",
  "greeting_message": "Welcome to our company. How can we help you?",
  "settings": {
    "language": "en",
    "timezone": "America/Los_Angeles",
    "max_call_duration": 1800,
    "enable_recording": false,
    "warm_transfer_enabled": true
  }
}
```

### Call Logs

#### GET /api/call-logs
Get call logs with filtering and pagination.

**Query Parameters:**
- `employee_id` (optional): Filter by employee
- `status` (optional): Filter by call status
- `date_from` (optional): Start date (ISO format)
- `date_to` (optional): End date (ISO format)
- `limit` (optional): Number of results (default: 50)
- `offset` (optional): Pagination offset (default: 0)

**Response:**
```json
{
  "data": [
    {
      "id": "uuid",
      "caller_phone": "+1234567890",
      "caller_name": "John Caller",
      "employee_id": "uuid",
      "employee": {
        "id": "uuid",
        "name": "Jane Smith"
      },
      "timestamp": "2024-01-01T10:00:00Z",
      "duration": "00:05:30",
      "status": "completed",
      "recording_url": "https://storage.example.com/recordings/call-uuid.mp3",
      "created_at": "2024-01-01T10:00:00Z"
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

#### POST /api/call-logs
Create a new call log entry.

**Request Body:**
```json
{
  "caller_phone": "+1234567890",
  "caller_name": "John Caller",
  "employee_id": "uuid",
  "duration": "00:05:30",
  "status": "completed",
  "recording_url": "https://storage.example.com/recordings/call-uuid.mp3"
}
```

### Messages

#### GET /api/messages
Get messages with filtering.

**Query Parameters:**
- `employee_id` (optional): Filter by employee
- `status` (optional): Filter by delivery status
- `date_from` (optional): Start date (ISO format)
- `date_to` (optional): End date (ISO format)
- `limit` (optional): Number of results (default: 50)
- `offset` (optional): Pagination offset (default: 0)

**Response:**
```json
{
  "data": [
    {
      "id": "uuid",
      "from_caller": "+1234567890",
      "to_employee_id": "uuid",
      "employee": {
        "id": "uuid",
        "name": "Jane Smith"
      },
      "message_text": "Please call me back about the project proposal.",
      "delivered_via": ["sms", "email"],
      "timestamp": "2024-01-01T10:00:00Z",
      "status": "delivered",
      "created_at": "2024-01-01T10:00:00Z"
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

#### POST /api/messages
Create a new message.

**Request Body:**
```json
{
  "from_caller": "+1234567890",
  "to_employee_id": "uuid",
  "message_text": "Please call me back about the project proposal.",
  "delivered_via": ["sms", "email"]
}
```

#### PUT /api/messages/{message_id}/status
Update message delivery status.

**Request Body:**
```json
{
  "status": "delivered",
  "delivery_details": {
    "sms": {"status": "delivered", "timestamp": "2024-01-01T10:05:00Z"},
    "email": {"status": "delivered", "timestamp": "2024-01-01T10:05:00Z"}
  }
}
```

## WebSocket Endpoints

### Real-time Updates

Connect to WebSocket for real-time updates:

```
ws://localhost:8000/ws
```

#### Message Types

**Call Status Update:**
```json
{
  "type": "call_status",
  "data": {
    "call_id": "uuid",
    "status": "in_progress",
    "participants": ["caller", "agent"],
    "timestamp": "2024-01-01T10:00:00Z"
  }
}
```

**Message Notification:**
```json
{
  "type": "message_notification",
  "data": {
    "message_id": "uuid",
    "employee_id": "uuid",
    "status": "delivered",
    "timestamp": "2024-01-01T10:00:00Z"
  }
}
```

**Employee Status Update:**
```json
{
  "type": "employee_status",
  "data": {
    "employee_id": "uuid",
    "status": "busy",
    "timestamp": "2024-01-01T10:00:00Z"
  }
}
```

## Error Codes

| Code | Description |
|------|-------------|
| `VALIDATION_ERROR` | Request validation failed |
| `NOT_FOUND` | Resource not found |
| `UNAUTHORIZED` | Authentication required |
| `FORBIDDEN` | Insufficient permissions |
| `CONFLICT` | Resource already exists |
| `RATE_LIMITED` | Too many requests |
| `INTERNAL_ERROR` | Server error |

## Rate Limiting

API endpoints are rate limited:
- 100 requests per minute per IP
- 1000 requests per hour per authenticated user

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 99
X-RateLimit-Reset: 1640995200
```

## Pagination

List endpoints support pagination with `limit` and `offset` parameters:

```
GET /api/employees?limit=20&offset=40
```

Response includes pagination metadata:
```json
{
  "data": [...],
  "total": 100,
  "limit": 20,
  "offset": 40,
  "has_next": true,
  "has_prev": true
}
```

## Filtering and Search

Many endpoints support filtering and search:

```
GET /api/employees?department_id=uuid&status=available&search=john
```

## Sorting

List endpoints support sorting with the `sort` parameter:

```
GET /api/employees?sort=name:asc
GET /api/employees?sort=created_at:desc
```

## Field Selection

Use the `fields` parameter to select specific fields:

```
GET /api/employees?fields=id,name,phone
```

## Bulk Operations

Some endpoints support bulk operations:

#### POST /api/employees/bulk
Create multiple employees.

**Request Body:**
```json
{
  "employees": [
    {
      "name": "Employee 1",
      "phone": "+1234567890",
      "email": "emp1@company.com"
    },
    {
      "name": "Employee 2",
      "phone": "+1234567891",
      "email": "emp2@company.com"
    }
  ]
}
```

## Webhooks

The API supports webhooks for real-time notifications:

#### POST /api/webhooks
Create a webhook endpoint.

**Request Body:**
```json
{
  "url": "https://your-app.com/webhook",
  "events": ["call.created", "message.delivered"],
  "secret": "webhook_secret"
}
```

#### Webhook Payload Example
```json
{
  "event": "call.created",
  "data": {
    "call_id": "uuid",
    "caller_phone": "+1234567890",
    "timestamp": "2024-01-01T10:00:00Z"
  },
  "timestamp": "2024-01-01T10:00:00Z"
}
```

## SDK Examples

### Python
```python
import requests

# Get employees
response = requests.get(
    "http://localhost:8000/api/employees",
    headers={"Authorization": "Bearer <token>"}
)
employees = response.json()["data"]

# Create employee
new_employee = {
    "name": "John Doe",
    "phone": "+1234567890",
    "email": "john@company.com"
}
response = requests.post(
    "http://localhost:8000/api/employees",
    json=new_employee,
    headers={"Authorization": "Bearer <token>"}
)
```

### JavaScript
```javascript
// Get employees
const response = await fetch('/api/employees', {
  headers: {
    'Authorization': 'Bearer <token>'
  }
});
const { data: employees } = await response.json();

// Create employee
const newEmployee = {
  name: 'John Doe',
  phone: '+1234567890',
  email: 'john@company.com'
};
const response = await fetch('/api/employees', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer <token>'
  },
  body: JSON.stringify(newEmployee)
});
```

## Testing

### Interactive API Documentation

Visit the interactive API documentation:
- Development: `http://localhost:8000/docs`
- Production: `https://your-domain.com/api/docs`

### Postman Collection

Import the Postman collection for testing:
```json
{
  "info": {
    "name": "Switchboard Assistant API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Employees",
      "item": [
        {
          "name": "Get All Employees",
          "request": {
            "method": "GET",
            "header": [],
            "url": {
              "raw": "{{base_url}}/api/employees",
              "host": ["{{base_url}}"],
              "path": ["api", "employees"]
            }
          }
        }
      ]
    }
  ]
}
```

## Changelog

### v1.0.0
- Initial API release
- Employee management endpoints
- Department management endpoints
- Company settings endpoints
- Call logs endpoints
- Message management endpoints
- WebSocket support for real-time updates
- Authentication with Supabase Auth
- Rate limiting and pagination


