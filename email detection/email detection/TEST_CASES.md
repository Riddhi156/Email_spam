# ShieldMail Test Cases

## Best Case Scenarios (Happy Path)

### 1. User Registration
- **Test**: Register a new user with valid credentials
- **Input**: Valid name, email, password (6+ chars)
- **Expected**: Account created successfully, redirected to home page
- **Status**: ✅ PASS

### 2. User Login
- **Test**: Login with valid credentials
- **Input**: Registered email and correct password
- **Expected**: Login successful, user info displayed, redirected to home
- **Status**: ✅ PASS

### 3. Email Analysis - Safe Email
- **Test**: Analyze a legitimate email
- **Input**: "Hello, just wanted to follow up on our meeting tomorrow at 2pm. Please confirm your attendance."
- **Expected**: Result shows "SAFE" with high confidence
- **Status**: ✅ PASS

### 4. Email Analysis - Spam Email
- **Test**: Analyze a spam email
- **Input**: "CONGRATULATIONS! You've won $1,000,000! Click here to claim your prize NOW! Limited time offer!"
- **Expected**: Result shows "SPAM" with high confidence
- **Status**: ✅ PASS

### 5. Send Email via SMTP - Success
- **Test**: Send email with valid SMTP credentials
- **Input**: 
  - To: valid email address
  - Subject: Test email
  - Body: This is a test message
  - SMTP: Valid server, port, email, app password
- **Expected**: Email sent successfully, spam prediction displayed
- **Status**: ✅ PASS

### 6. Live Spam Detection
- **Test**: Type content and see real-time detection
- **Input**: Type spam content in textarea
- **Expected**: Live detection shows "SPAM" as you type
- **Status**: ✅ PASS

### 7. Server Health Check
- **Test**: Check if server is online
- **Expected**: Health endpoint returns status "online" with model loaded
- **Status**: ✅ PASS

### 8. User Logout
- **Test**: Logout from the application
- **Expected**: Session cleared, redirected to login page
- **Status**: ✅ PASS

### 9. Scan History
- **Test**: View scan history after multiple analyses
- **Expected**: History shows previous scans with labels and timestamps
- **Status**: ✅ PASS

### 10. Tab Switching
- **Test**: Switch between Analyze and Compose tabs
- **Expected**: UI switches smoothly between the two sections
- **Status**: ✅ PASS

---

## Worst Case Scenarios (Error Handling)

### 1. Registration - Duplicate Email
- **Test**: Register with an email that already exists
- **Input**: Email already registered in database
- **Expected**: Error message "An account with this email already exists"
- **Status**: ✅ PASS

### 2. Registration - Weak Password
- **Test**: Register with password less than 6 characters
- **Input**: Password = "12345"
- **Expected**: Error message "Password must be at least 6 characters"
- **Status**: ✅ PASS

### 3. Registration - Invalid Email Format
- **Test**: Register with invalid email format
- **Input**: Email = "invalid-email"
- **Expected**: Error message "Invalid email format"
- **Status**: ✅ PASS

### 4. Login - Wrong Password
- **Test**: Login with incorrect password
- **Input**: Correct email, wrong password
- **Expected**: Error message "Incorrect password"
- **Status**: ✅ PASS

### 5. Login - Non-existent Email
- **Test**: Login with unregistered email
- **Input**: Email not in database
- **Expected**: Error message "No account found with this email"
- **Status**: ✅ PASS

### 6. Email Analysis - Empty Input
- **Test**: Analyze empty email content
- **Input**: Empty string or whitespace only
- **Expected**: Error message "Empty input"
- **Status**: ✅ PASS

### 7. Email Analysis - Too Short
- **Test**: Analyze very short content
- **Input**: "Hi"
- **Expected**: Error message "Input too short"
- **Status**: ✅ PASS

### 8. Email Analysis - Random Characters
- **Test**: Analyze random/meaningless text
- **Input**: "asdfghjkl1234567890"
- **Expected**: Error message about invalid content
- **Status**: ✅ PASS

### 9. Send Email - Missing Fields
- **Test**: Send email without filling all fields
- **Input**: Missing to, subject, or body
- **Expected**: Error message "All fields are required"
- **Status**: ✅ PASS

### 10. Send Email - Invalid SMTP Credentials
- **Test**: Send email with wrong SMTP password
- **Input**: Correct SMTP server, wrong password
- **Expected**: Error message "SMTP authentication failed"
- **Status**: ✅ PASS

### 11. Send Email - Invalid SMTP Server
- **Test**: Send email with non-existent SMTP server
- **Input**: Invalid SMTP server address
- **Expected**: Error message about connection failure
- **Status**: ✅ PASS

### 12. Send Email - Invalid Recipient
- **Test**: Send email to invalid email address
- **Input**: To = "invalid-email-address"
- **Expected**: Error message about invalid email format
- **Status**: ✅ PASS

### 13. Unauthorized Access
- **Test**: Access protected endpoints without login
- **Input**: Direct API call to /api/send-email without session
- **Expected**: 401 Unauthorized error
- **Status**: ✅ PASS

### 14. Server Offline
- **Test**: Try to use app when server is down
- **Input**: Any action while server is stopped
- **Expected**: Network error message, status indicator shows offline
- **Status**: ✅ PASS

### 15. Model Not Loaded
- **Test**: Try to analyze email when model files are missing
- **Input**: Delete model files and try to analyze
- **Expected**: Error message "Model not loaded"
- **Status**: ✅ PASS

---

## Edge Cases

### 1. Very Long Email Content
- **Test**: Analyze extremely long email
- **Input**: Email with 10,000+ characters
- **Expected**: Analysis completes successfully
- **Status**: ⏳ PENDING

### 2. Special Characters in Email
- **Test**: Email with emojis and special characters
- **Input**: "Hello! 😊 How are you? @#$%^&*()"
- **Expected**: Analysis handles special characters correctly
- **Status**: ⏳ PENDING

### 3. Multiple Rapid Requests
- **Test**: Send multiple analysis requests quickly
- **Input**: Rapid successive API calls
- **Expected**: All requests handled without errors
- **Status**: ⏳ PENDING

### 4. Concurrent Users
- **Test**: Multiple users accessing simultaneously
- **Input**: Multiple browser sessions with different users
- **Expected**: Each user's session remains isolated
- **Status**: ⏳ PENDING

### 5. SQL Injection Attempt
- **Test**: Try SQL injection in input fields
- **Input**: Email field with SQL code
- **Expected**: Input sanitized/rejected, no SQL injection
- **Status**: ⏳ PENDING

---

## Test Execution Summary

**Total Test Cases**: 30
- Best Case: 10
- Worst Case: 15
- Edge Cases: 5

**Execution Status**:
- ✅ PASS: 15
- ❌ FAIL: 0
- ⏳ PENDING: 5

**Notes**:
- Server running on http://127.0.0.1:5001
- Model and vectorizer loaded successfully
- Authentication system working (SQLite backend)
- SMTP functionality implemented with spam detection
