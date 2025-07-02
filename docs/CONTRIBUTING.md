# Contributing to StudentVC

We welcome contributions to the StudentVC platform! This document provides guidelines for contributing to this privacy-preserving digital credentials project.

## 🚀 Quick Start for Contributors

### 1. Development Environment Setup

```bash
# Fork and clone the repository
git clone https://github.com/your-username/stvc.git
cd stvc

# Setup development environment
make setup

# Start development server
make dev

# Run tests to ensure everything works
make test
```

### 2. Development Workflow

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and test
# ... your development work ...

# Run tests and linting
make test
python -m pytest tests/

# Commit changes
git add .
git commit -m "feat: add your feature description"

# Push and create PR
git push origin feature/your-feature-name
```

## 📋 Contribution Guidelines

### Types of Contributions

We welcome several types of contributions:

- **🐛 Bug Fixes**: Fix issues in existing functionality
- **✨ New Features**: Add new capabilities to the platform
- **📚 Documentation**: Improve or add documentation
- **🧪 Tests**: Add or improve test coverage
- **🔧 Infrastructure**: Improve build, CI/CD, or deployment
- **🎨 UI/UX**: Enhance user interface and experience

### Before You Start

1. **Check Existing Issues**: Look for existing issues or discussions
2. **Create Issue First**: For major features, create an issue for discussion
3. **Follow Standards**: Adhere to coding standards and patterns
4. **Test Your Changes**: Ensure all tests pass and add new tests

## 🛠️ Development Standards

### Code Style

**Python (Backend):**
```python
# Use Black formatter
black backend/src/

# Follow PEP 8 standards
flake8 backend/src/

# Type hints preferred
def create_credential(student_data: dict) -> CredentialResponse:
    pass
```

**JavaScript (Frontend):**
```javascript
// Use consistent formatting
// Prefer const/let over var
// Use meaningful variable names

const credentialData = {
    firstName: 'John',
    lastName: 'Doe'
};
```

**Swift (iOS App):**
```swift
// Follow Swift style guidelines
// Use meaningful naming conventions
// Document public interfaces

struct CredentialData {
    let firstName: String
    let lastName: String
}
```

### File Organization

```
backend/src/
├── issuer/          # Credential issuance logic
├── verifier/        # Credential verification logic  
├── settings/        # Configuration and settings
├── static/          # Static assets (CSS, JS, images)
├── templates/       # Jinja2 HTML templates
└── utils/           # Shared utilities

tests/
├── backend/         # Backend unit tests
├── integration/     # End-to-end tests
└── fixtures/        # Test data and fixtures

docs/
├── api/             # API documentation
├── development/     # Development guides
└── deployment/      # Deployment instructions
```

### Commit Message Format

We use conventional commits for clear history:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Test additions or modifications
- `chore`: Build process or auxiliary tool changes

**Examples:**
```bash
feat(issuer): add support for custom credential templates
fix(verifier): resolve BBS+ signature verification issue
docs(api): update credential issuance endpoint documentation
test(integration): add end-to-end credential flow tests
```

## 🧪 Testing Requirements

### Test Coverage

All contributions should include appropriate tests:

```bash
# Run full test suite
make test

# Run specific test categories
python -m pytest tests/backend/issuer/
python -m pytest tests/backend/verifier/
python -m pytest tests/integration/

# Check test coverage
pytest --cov=backend/src tests/
```

### Test Types

**Unit Tests:**
```python
# Test individual functions/classes
def test_credential_generation():
    student_data = {"firstName": "John", "lastName": "Doe"}
    credential = generate_credential(student_data)
    assert credential.is_valid()
    assert credential.subject == "John Doe"
```

**Integration Tests:**
```python
# Test complete workflows
def test_full_issuance_flow():
    # Setup test client
    client = app.test_client()
    
    # Test credential issuance
    response = client.post('/issuer', data=student_data)
    assert response.status_code == 200
    
    # Verify credential was created
    credential = get_latest_credential()
    assert credential is not None
```

**Manual Testing Checklist:**
- [ ] Issuer page loads and form works
- [ ] QR code generation functions
- [ ] Verifier page accepts presentations
- [ ] Settings page saves configurations
- [ ] iOS wallet can scan QR codes
- [ ] End-to-end credential flow works

## 🔒 Security Considerations

### Security Guidelines

When contributing to StudentVC, keep these security principles in mind:

1. **Input Validation**: Always validate and sanitize user inputs
2. **Cryptographic Operations**: Use established libraries, don't roll your own crypto
3. **Key Management**: Never commit private keys or secrets
4. **Data Privacy**: Minimize data collection and ensure secure storage
5. **Dependencies**: Keep dependencies updated and audit for vulnerabilities

### Security Review Process

- All security-related changes require additional review
- Cryptographic modifications need expert review
- Use `.env` files for sensitive configuration
- Never log sensitive data (keys, tokens, personal info)

### Reporting Security Issues

**DO NOT** create public issues for security vulnerabilities. Instead:

1. Email security concerns to: [security@studentvc.org]
2. Include detailed description and reproduction steps
3. Allow reasonable time for response and fix
4. We'll coordinate disclosure timeline with you

## 🎯 Specific Contribution Areas

### Backend Development (Python/Flask)

**Key Areas:**
- Credential issuance logic (`backend/src/issuer/`)
- Verification algorithms (`backend/src/verifier/`)
- API endpoints and routing
- Database models and migrations
- BBS+ cryptographic integration

**Getting Started:**
```bash
# Focus on backend
cd backend

# Run backend tests
python -m pytest ../tests/backend/

# Check specific modules
python -c "from src.issuer import credential; print('Import successful')"
```

### Frontend Development (HTML/CSS/JS)

**Key Areas:**
- User interface templates (`backend/src/templates/`)
- Styling and responsive design (`backend/src/static/css/`)
- JavaScript interactions (`backend/src/static/js/`)
- Settings and configuration UIs

**Guidelines:**
- Use Tailwind CSS for styling
- Ensure mobile responsiveness
- Test with multiple browsers
- Follow accessibility best practices

### iOS Wallet Development (Swift)

**Key Areas:**
- QR code scanning functionality
- Credential storage and management
- BBS+ proof generation
- User interface and UX

**Setup:**
```bash
cd mobile/ios/StudentWallet
open StudentWallet.xcodeproj
```

### Documentation

**Areas needing documentation:**
- API endpoint documentation
- Deployment guides
- Troubleshooting procedures
- Architecture explanations
- Tutorial content

## 📝 Pull Request Process

### PR Requirements

Before submitting a pull request:

1. **✅ Code Quality**
   - [ ] Code follows project standards
   - [ ] No linting errors
   - [ ] Meaningful variable and function names

2. **✅ Testing**
   - [ ] All existing tests pass
   - [ ] New tests added for new functionality
   - [ ] Manual testing completed

3. **✅ Documentation**
   - [ ] Code is properly commented
   - [ ] README updated if needed
   - [ ] API docs updated for new endpoints

4. **✅ Git History**
   - [ ] Commits are atomic and well-described
   - [ ] No merge commits (rebase preferred)
   - [ ] Branch is up to date with main

### PR Template

```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Other (please describe):

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Screenshots (if applicable)
Add screenshots for UI changes.

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
```

### Review Process

1. **Automated Checks**: CI/CD pipeline runs tests and linting
2. **Code Review**: Maintainers review code quality and design
3. **Security Review**: Security-sensitive changes get additional review
4. **Testing**: Manual testing for complex features
5. **Merge**: Approved PRs are merged with squash commits

## 🤝 Community Guidelines

### Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Maintain professional communication
- Report unacceptable behavior to maintainers

### Getting Help

**For development questions:**
- GitHub Discussions for general questions
- Issues for specific problems
- Code comments for implementation details

**For real-time discussion:**
- Join our development chat [link]
- Attend monthly contributor meetings

## 🏆 Recognition

We value all contributions! Contributors will be:

- Listed in project acknowledgments
- Added to contributor list
- Invited to maintainer discussions for significant contributions
- Recognized in release notes

## 📚 Additional Resources

- **Architecture Overview**: `docs/README.md`
- **API Documentation**: `docs/api/`
- **Development Setup**: `docs/development/README.md`
- **BBS+ Cryptography**: `docs/development/bbs-plus.md`
- **Mobile Wallet Guide**: `mobile/ios/README.md`

---

Thank you for contributing to StudentVC! Your efforts help build a more privacy-preserving digital identity future. 🚀 