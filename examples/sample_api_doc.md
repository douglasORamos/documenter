# Sample API Documentation

This is a sample API documentation in Markdown format to test the AI Documentation Enricher.

## Base URL

```
https://api.example.com/v1
```

## Authentication

All requests require a Bearer token in the Authorization header:

```
Authorization: Bearer your-token-here
```

## Endpoints

### 1. Create User

**POST** `/users`

Creates a new user in the system.

**Request Body:**

```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "secure_password123",
  "age": 25,
  "country": "US"
}
```

**Field Descriptions:**

- `username` (string, required): User's username. Must be unique and between 3-50 characters.
- `email` (string, required): User's email address. Must be a valid email format.
- `password` (string, required): User's password. Minimum 8 characters, must contain letters and numbers.
- `age` (integer, optional): User's age. Must be 18 or older.
- `country` (string, optional): User's country code (ISO 3166-1 alpha-2).

**Success Response (201 Created):**

```json
{
  "id": "usr_abc123",
  "username": "john_doe",
  "email": "john@example.com",
  "age": 25,
  "country": "US",
  "created_at": "2024-01-01T10:00:00Z",
  "status": "active"
}
```

**Error Responses:**

- **400 Bad Request**: Invalid input data
  - Missing required field
  - Invalid email format
  - Password too weak
  - Age under 18

- **409 Conflict**: User already exists
  - Username is already taken
  - Email is already registered

- **500 Internal Server Error**: Server error

---

### 2. Get User

**GET** `/users/{id}`

Retrieves information about a specific user.

**Path Parameters:**

- `id` (string, required): The user ID

**Success Response (200 OK):**

```json
{
  "id": "usr_abc123",
  "username": "john_doe",
  "email": "john@example.com",
  "age": 25,
  "country": "US",
  "created_at": "2024-01-01T10:00:00Z",
  "status": "active",
  "last_login": "2024-01-15T14:30:00Z"
}
```

**Error Responses:**

- **404 Not Found**: User not found
- **401 Unauthorized**: Invalid or missing token

---

### 3. Update User

**PATCH** `/users/{id}`

Updates user information.

**Path Parameters:**

- `id` (string, required): The user ID

**Request Body:**

You can send any combination of the following fields:

```json
{
  "username": "new_username",
  "email": "newemail@example.com",
  "age": 26,
  "country": "UK"
}
```

**Notes:**
- Only provided fields will be updated
- Email must be unique if changed
- Username must be unique if changed

**Success Response (200 OK):**

```json
{
  "id": "usr_abc123",
  "username": "new_username",
  "email": "newemail@example.com",
  "age": 26,
  "country": "UK",
  "updated_at": "2024-01-15T15:00:00Z"
}
```

**Error Responses:**

- **400 Bad Request**: Invalid input
- **404 Not Found**: User not found
- **409 Conflict**: Email or username already exists

---

### 4. Delete User

**DELETE** `/users/{id}`

Deletes a user account.

**Path Parameters:**

- `id` (string, required): The user ID

**Success Response (204 No Content):**

Empty response body.

**Error Responses:**

- **404 Not Found**: User not found
- **403 Forbidden**: Cannot delete other users

---

### 5. List Users

**GET** `/users`

Lists all users with pagination.

**Query Parameters:**

- `page` (integer, optional): Page number (default: 1)
- `limit` (integer, optional): Items per page (default: 10, max: 100)
- `status` (string, optional): Filter by status ("active", "inactive", "suspended")
- `country` (string, optional): Filter by country code

**Success Response (200 OK):**

```json
{
  "users": [
    {
      "id": "usr_abc123",
      "username": "john_doe",
      "email": "john@example.com",
      "status": "active"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 150,
    "total_pages": 15
  }
}
```

---

## Business Rules

### User Status

When a user is created, their status is automatically set to "active".

If a user doesn't login for 90 days, their status changes to "inactive".

If a user violates terms of service, their status can be set to "suspended" by an admin.

### Email Validation

All emails must:
- Be in valid email format
- Have a domain with MX records
- Not be from temporary email providers

### Password Requirements

Passwords must:
- Be at least 8 characters long
- Contain at least one letter
- Contain at least one number
- Not contain the username
- Not be in the common passwords list

### Username Rules

Usernames must:
- Be between 3 and 50 characters
- Contain only letters, numbers, and underscores
- Start with a letter
- Be unique across the system

## Rate Limiting

All endpoints are rate-limited to 100 requests per minute per IP address.

When rate limit is exceeded, the API returns HTTP 429 (Too Many Requests).

## Error Response Format

All errors follow this format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field": "Additional context about the error"
    }
  }
}
```

## Common Error Codes

- `INVALID_INPUT`: Input validation failed
- `RESOURCE_NOT_FOUND`: Requested resource doesn't exist
- `DUPLICATE_RESOURCE`: Resource already exists
- `UNAUTHORIZED`: Missing or invalid authentication
- `FORBIDDEN`: User doesn't have permission
- `RATE_LIMIT_EXCEEDED`: Too many requests

---

**Version**: 1.0.0  
**Last Updated**: 2024-01-15

