# Simple Authentication for StudentVC

Protect your StudentVC platform with simple password authentication and optional email verification.

## Quick Setup (5 minutes)

### Option 1: Automatic Setup
```bash
./deploy/scripts/setup-simple-auth.sh
```

### Option 2: Manual Setup
1. Copy environment template:
   ```bash
   cp env.example .env
   ```

2. Edit `.env` file:
   ```bash
   ENABLE_AUTH=true
   ACCESS_PASSWORD=your_secure_password
   ```

3. Start server:
   ```bash
   make dev
   ```

## Authentication Options

### 🔐 Password Only (Simplest)
```bash
ENABLE_AUTH=true
ACCESS_PASSWORD=mySecurePassword123
REQUIRE_EMAIL_2FA=false
```

**How it works:**
- Users visit your site → See login page
- Enter password → Access granted
- Session stays active for 31 days

### 📧 Password + Email 2FA (More Secure)
```bash
ENABLE_AUTH=true
ACCESS_PASSWORD=mySecurePassword123
REQUIRE_EMAIL_2FA=true
ADMIN_EMAIL=your-email@example.com
SMTP_EMAIL=your-smtp@gmail.com
SMTP_PASSWORD=your_app_password
```

**How it works:**
- Users enter password → Email code sent
- Enter 6-digit code → Access granted
- Codes expire in 10 minutes

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ENABLE_AUTH` | Yes | `false` | Enable/disable authentication |
| `ACCESS_PASSWORD` | Yes | `studentvc2024` | Main access password |
| `REQUIRE_EMAIL_2FA` | No | `false` | Enable email verification |
| `ADMIN_EMAIL` | No | - | Email to receive verification codes |
| `SMTP_EMAIL` | No | - | Email account for sending codes |
| `SMTP_PASSWORD` | No | - | App password for SMTP |
| `SMTP_SERVER` | No | `smtp.gmail.com` | SMTP server |
| `SMTP_PORT` | No | `587` | SMTP port |

## Email Setup (Gmail Example)

1. Enable 2-factor authentication on your Gmail
2. Generate an App Password:
   - Google Account → Security → App Passwords
   - Generate password for "Mail"
3. Use the app password (not your regular password)

```bash
SMTP_EMAIL=your-email@gmail.com
SMTP_PASSWORD=abcd-efgh-ijkl-mnop  # App password
```

## Usage

### For You (Admin)
- Share the password with colleagues
- Change password anytime in `.env`
- Disable auth by setting `ENABLE_AUTH=false`

### For Colleagues
1. Visit your StudentVC URL
2. See login page
3. Enter the password you shared
4. (If 2FA enabled) Check email for code
5. Access granted!

## Security Features

- ✅ Session-based authentication (31-day expiry)
- ✅ Password protection for all routes
- ✅ Optional email 2FA
- ✅ Rate limiting (5 attempts per second)
- ✅ Secure session management
- ✅ Auto-logout on browser close (optional)

## Disable Authentication

Set in `.env`:
```bash
ENABLE_AUTH=false
```

Or run:
```bash
./deploy/scripts/setup-simple-auth.sh
# Choose option 3 for custom setup
```

## Troubleshooting

### "Login page not showing"
- Check `ENABLE_AUTH=true` in `.env`
- Restart server: `make dev`

### "Email codes not sending"
- Verify SMTP settings
- Check Gmail app password
- Look at server logs for email errors

### "Can't access after login"
- Clear browser cookies
- Check server logs
- Verify session settings

## Advanced Configuration

### Custom Login URL
The login page is automatically at `/login`

### Custom Session Timeout
Edit `simple_auth.py`:
```python
session.permanent = True  # 31 days (default)
# or
app.permanent_session_lifetime = timedelta(hours=24)  # Custom
```

### Logout URL
Users can logout at `/logout`

That's it! Simple, secure, and easy to manage. 