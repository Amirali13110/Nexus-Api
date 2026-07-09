##  Authentication

The application includes a secure and modern authentication system built with FastAPI.

### Features

✅ User registration (Sign Up)
✅ User authentication (Sign In)
✅ JWT-based authentication
✅ Password hashing using secure cryptographic algorithms
✅ Forgot Password functionality
✅ Password Reset via secure magic link
✅ Secure Password Update
✅ Secure Email Change with verification
✅ One-time reset tokens with expiration
✅ Protected routes using JWT authentication
✅ Input validation and proper error handling


### Authentication Flow

1. A user creates an account using the **Sign Up** endpoint.
2. The user authenticates through the **Sign In** endpoint and receives a JWT access token.
3. Protected endpoints require a valid JWT in the `Authorization` header.
4. Authenticated users can securely change their password by providing their current password.
5. Authenticated users can request an email change, which sends a verification link to the new email address.
6. The email address is updated only after the verification link is successfully confirmed.
7. If the user forgets their password, they can request a password reset.
8. A secure, time-limited magic link is sent to the user's email.
9. Opening the magic link allows the user to set a new password.
10. After resetting or updating their password, the user can sign in with their new credentials.

### Security

* Passwords are never stored in plain text.
* Passwords are securely hashed using industry-standard cryptographic algorithms.
* Current password verification is required before changing the account password.
* Password reset links are cryptographically secure and expire automatically.
* Reset tokens are single-use and invalidated after successful password reset.
* Email changes require ownership verification of the new email address before taking effect.
* JWTs are signed using a secure secret key with configurable expiration times.
* Authentication endpoints include proper validation and consistent error responses.
* Sensitive account operations are accessible only to authenticated users.


## Profile Management

The application includes a scalable and secure profile management system built with FastAPI and SQLAlchemy.

### Features

✅ Automatic profile creation after user registration
✅ One-to-one relationship between User and Profile
✅ Secure profile update endpoint
✅ Username uniqueness validation
✅ Full name, bio, and avatar URL support
✅ Optional profile fields with strict validation
✅ Authentication-protected profile operations
✅ Clean request and response schemas using Pydantic
✅ Optimized SQLAlchemy relationships

### Profile Flow

1. A user creates an account using the **Sign Up** endpoint.
2. A profile is automatically created and linked to the newly registered user.
3. The user can retrieve their profile through authenticated endpoints.
4. The user can update their username, full name, bio, and avatar URL.
5. All profile updates are validated before being saved.
6. Username uniqueness is enforced across all profiles.
7. Every profile remains securely associated with its corresponding user account



Workspace Management

The application provides a complete workspace management system, allowing users to organize their projects in a secure and scalable way.

Features
✅ Create new workspaces
✅ Retrieve all accessible workspaces
✅ Update workspace information
✅ Delete workspaces
✅ Unique workspace slugs per owner
✅ Secure ownership verification
✅ Input validation and proper error handling
Workspace Flow
A signed-in user creates a new workspace.
Each workspace is assigned to its owner.
Every workspace includes a unique slug within the owner's account.
Users can retrieve all workspaces they own.
Workspace details can be updated at any time.
Workspaces can be permanently deleted by their owner.
Security
Only authenticated users can manage workspaces.
Users can only create workspaces under their own account.
Workspace ownership is verified before every update or deletion.
Duplicate workspace slugs are prevented for the same owner.
Database constraints ensure data integrity even during concurrent requests.


# Workspace Invitations

✅ Create workspace invitations
✅ Retrieve received invitations
✅ Retrieve sent invitations
✅ Accept workspace invitations
✅ Decline workspace invitations
✅ Cancel workspace invitations
✅ Invitation expiration support
✅ Automatic workspace member creation on acceptance
✅ Workspace role assignment through invitations
✅ Pending, Accepted, Declined, Canceled and Expired invitation lifecycle
✅ Duplicate invitation prevention
✅ Secure invitation ownership verification
✅ Authentication and authorization checks
✅ Joined loading for related workspace and user data
✅ ULID-based invitation identifiers
✅ Input validation and comprehensive error handling
