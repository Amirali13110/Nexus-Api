## 🔐 Authentication

The application includes a secure and modern authentication system built with FastAPI.

### Features

* ✅ User registration (Sign Up)
* ✅ User authentication (Sign In)
* ✅ Password hashing using secure cryptographic algorithms
* ✅ JWT-based authentication
* ✅ Forgot Password functionality
* ✅ Password Reset via secure magic link
* ✅ One-time reset tokens with expiration
* ✅ Protected routes using JWT authentication
* ✅ Input validation and proper error handling

### Authentication Flow

1. A user creates an account using the **Sign Up** endpoint.
2. The user authenticates through the **Sign In** endpoint and receives a JWT access token.
3. Protected endpoints require a valid JWT in the `Authorization` header.
4. If the user forgets their password, they can request a password reset.
5. A secure, time-limited magic link is sent to the user's email.
6. Opening the magic link allows the user to set a new password.
7. After resetting the password, the user can sign in with their new credentials.

### Security

* Passwords are never stored in plain text.
* Password reset links are cryptographically secure and expire automatically.
* Reset tokens are single-use and invalidated after successful password reset.
* JWTs are signed using a secure secret key and configurable expiration time.
* Authentication endpoints include proper validation and consistent error responses.


## Profile Management

The application includes a scalable and secure profile management system built with FastAPI and SQLAlchemy.

### Features

* ✅ Automatic profile creation after user registration
* ✅ One-to-one relationship between User and Profile
* ✅ Secure profile update endpoint
* ✅ Username uniqueness validation
* ✅ Full name, bio, and avatar URL support
* ✅ Optional profile fields with strict validation
* ✅ Authentication-protected profile operations
* ✅ Clean request and response schemas using Pydantic
* ✅ Optimized SQLAlchemy relationships

### Profile Flow

1. A user creates an account using the **Sign Up** endpoint.
2. A profile is automatically created and linked to the newly registered user.
3. The user can retrieve their profile through authenticated endpoints.
4. The user can update their username, full name, bio, and avatar URL.
5. All profile updates are validated before being saved.
6. Username uniqueness is enforced across all profiles.
7. Every profile remains securely associated with its corresponding user account