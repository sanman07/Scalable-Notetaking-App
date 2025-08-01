# Security Documentation

## Overview

This document outlines the security features implemented in the Notes Application to ensure data protection, user privacy, and system integrity.

## Authentication System

### JWT Token Authentication

The application uses JSON Web Tokens (JWT) for secure authentication:

- **Access Tokens**: Short-lived (30 minutes) for API access
- **Refresh Tokens**: Long-lived (7 days) for token renewal
- **Secure Token Storage**: Tokens are stored in memory and not persisted
- **Token Validation**: All tokens are cryptographically signed and validated

### Password Security

- **Bcrypt Hashing**: Passwords are hashed using bcrypt with salt
- **Password Strength Requirements**:
  - Minimum 8 characters
  - At least one uppercase letter
  - At least one lowercase letter
  - At least one digit
  - At least one special character
- **No Plain Text Storage**: Passwords are never stored in plain text

### User Registration & Login

#### Registration Requirements
- Username: 3-20 characters, alphanumeric and underscores only
- Email: Valid email format
- Password: Must meet strength requirements
- Full Name: Optional

#### Login Security
- Rate limiting on login attempts
- Secure password verification
- Session tracking with last login timestamps

## API Security

### Protected Endpoints

All data endpoints require authentication:
- `GET /notes` - Get user's notes
- `POST /notes` - Create new note
- `PUT /notes/{id}` - Update note
- `DELETE /notes/{id}` - Delete note
- `GET /folders` - Get user's folders
- `POST /folders` - Create new folder
- `PUT /folders/{id}` - Update folder
- `DELETE /folders/{id}` - Delete folder

### Public Endpoints

Only these endpoints are publicly accessible:
- `GET /` - API information
- `GET /health` - Health check
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/refresh` - Token refresh

### Data Isolation

- **User-Specific Data**: All notes and folders are tied to user accounts
- **Access Control**: Users can only access their own data
- **Cross-User Protection**: No data leakage between users

## Security Headers

The application implements comprehensive security headers:

```http
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';
```

## Rate Limiting

- **Window**: 60 seconds
- **Limit**: 100 requests per window
- **Exempt Paths**: Health check and documentation endpoints
- **IP-Based**: Rate limiting is applied per client IP

## CORS Configuration

Configured for secure cross-origin requests:

```python
allow_origins = [
    "http://localhost:3000",
    "http://localhost:5173", 
    "http://localhost:80",
    "http://localhost"
]
allow_credentials = True
allow_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
allow_headers = ["*"]
```

## Database Security

### Connection Security
- **Encrypted Connections**: Database connections use SSL/TLS
- **Connection Pooling**: Efficient and secure connection management
- **Parameterized Queries**: Protection against SQL injection

### Data Protection
- **User Isolation**: Database queries filter by user_id
- **Input Validation**: All inputs are validated before database operations
- **Transaction Safety**: All operations use database transactions

## Environment Security

### Required Environment Variables

```env
# Security Configuration
SECRET_KEY=your-super-secret-key-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Database Configuration
DATABASE_URL=postgresql+asyncpg://user:password@host:port/dbname
POSTGRES_USER=notesuser
POSTGRES_PASSWORD=notespassword
POSTGRES_DB=notesdb

# Application Configuration
ENVIRONMENT=production
API_HOST=0.0.0.0
API_PORT=8000
```

### Production Security Checklist

- [ ] Change default `SECRET_KEY`
- [ ] Use strong database passwords
- [ ] Enable SSL/TLS for database connections
- [ ] Configure proper CORS origins
- [ ] Set up proper logging
- [ ] Use HTTPS in production
- [ ] Configure firewall rules
- [ ] Regular security updates

## Security Testing

### Authentication Tests

Run the test script to verify security features:

```bash
cd backend
python test_auth.py
```

This will test:
- User registration with validation
- Login with valid/invalid credentials
- Protected endpoint access
- Token refresh functionality
- Unauthorized access prevention

### Manual Testing

1. **Registration Test**:
   ```bash
   curl -X POST "http://localhost:8000/auth/register" \
        -H "Content-Type: application/json" \
        -d '{"username":"testuser","email":"test@example.com","password":"TestPass123!","full_name":"Test User"}'
   ```

2. **Login Test**:
   ```bash
   curl -X POST "http://localhost:8000/auth/login" \
        -H "Content-Type: application/json" \
        -d '{"username":"testuser","password":"TestPass123!"}'
   ```

3. **Protected Endpoint Test**:
   ```bash
   curl -X GET "http://localhost:8000/notes" \
        -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
   ```

## Security Best Practices

### For Developers

1. **Never commit secrets** to version control
2. **Use environment variables** for configuration
3. **Validate all inputs** before processing
4. **Use parameterized queries** to prevent injection
5. **Implement proper error handling** without exposing internals
6. **Keep dependencies updated** for security patches

### For Administrators

1. **Regular security audits** of the application
2. **Monitor access logs** for suspicious activity
3. **Backup data regularly** with encryption
4. **Use strong passwords** for all accounts
5. **Enable two-factor authentication** where possible
6. **Keep systems updated** with security patches

## Incident Response

### Security Breach Response

1. **Immediate Actions**:
   - Disable compromised accounts
   - Revoke all active tokens
   - Check system logs for unauthorized access
   - Isolate affected systems if necessary

2. **Investigation**:
   - Review access logs
   - Check for data exfiltration
   - Identify attack vectors
   - Document findings

3. **Recovery**:
   - Reset compromised credentials
   - Restore from clean backups if needed
   - Implement additional security measures
   - Notify affected users if required

### Contact Information

For security issues, please contact:
- **Email**: security@notesapp.com
- **Response Time**: 24 hours for critical issues
- **Disclosure Policy**: Responsible disclosure preferred

## Compliance

This application implements security measures to comply with:

- **OWASP Top 10** security risks
- **GDPR** data protection requirements
- **SOC 2** security controls
- **ISO 27001** information security standards

## Updates

This security documentation is updated regularly. Last updated: December 2024

For questions or concerns about security, please refer to the contact information above. 