# ADR-0002: AWS Credentials Automation Implementation

## Status
Accepted

## Context

Development teams using AWS SSO face a repetitive and error-prone manual process to retrieve temporary credentials:

1. Navigate to AWS SSO portal (https://d-9c67542c51.awsapps.com/start/#)
2. Select target account (What ever is configured in the aws_accounts.yaml file)
3. Click "Access keys"
4. Copy environment variables from Option 1 (macOS/Linux)
5. Paste and execute in terminal
6. Repeat every 12 hours when credentials expire

This manual process causes:
- **Developer friction**: 5+ manual steps, multiple clicks and copy-paste operations
- **Time waste**: 2-3 minutes per credential refresh, multiplied by team size and frequency
- **Error susceptibility**: Easy to copy wrong credentials, miss variables, or use expired tokens
- **Inconsistency**: Different developers use different methods and tools
- **Security risks**: Credentials may be accidentally logged or persisted in shell history

## Decision

We will implement automated AWS SSO credential retrieval integrated into the existing `setup-environment` CLI tool with the following architecture:

### Technical Architecture

**Clean Architecture Implementation:**
- **Domain Layer**: `AWSAccount`, `AWSCredentials` entities with business logic and validation
- **Value Objects**: `SSOConfig`, `AWSSession` for immutable configuration and session data
- **Application Layer**: `SetupAWSCredentialsUseCase` orchestrating the credential retrieval flow
- **Infrastructure Layer**: `AWSSSOService` using boto3 SDK with browser automation fallback
- **Presentation Layer**: Click-based CLI interface with multiple output formats

### Authentication Strategy

**Primary Approach**: boto3 AWS SDK
- Programmatic SSO client integration
- Native AWS API interaction
- Automatic token refresh capabilities
- Secure credential handling

**Fallback Approach**: Browser automation
- Selenium/Playwright integration for edge cases
- Visual feedback of credential retrieval process
- Manual fallback with clear instructions

### Configuration Management

**Account Configuration**: YAML-based account definitions

Developers must configure multiple accounts in `src/setup_environment/config/aws_accounts.yaml`:
```yaml
accounts:
  - name: production
    account_id: "123456789012" 
    email: aws-admin@example.com
    role: Engineer
    default: true
    description: "Production environment"
    
  - name: development
    account_id: "234567890123"
    email: aws-dev@example.com
    role: Engineer
    description: "Development environment"
    
  - name: staging
    account_id: "345678901234"
    email: aws-staging@example.com
    role: Engineer
    description: "Staging environment"
```

**Important**: Replace the example account details with your actual AWS account information before use. Do not commit real account details to source control.

**SSO Configuration**: Environment-based settings
```bash
AWS_SSO_START_URL=https://your-sso.awsapps.com/start/#
AWS_SSO_REGION=eu-west-2
AWS_DEFAULT_REGION=eu-west-2
```

### Output Formats

Support for multiple shell environments:
- **Bash/Zsh**: `export AWS_ACCESS_KEY_ID="..."`
- **Fish**: `set -x AWS_ACCESS_KEY_ID "..."`
- **PowerShell**: `$env:AWS_ACCESS_KEY_ID="..."`
- **AWS Config File**: Standard `~/.aws/credentials` format

### Integration Points

**CLI Integration**: 
- New subcommand: `setup-environment aws-credentials`
- Makefile shortcuts: `make aws-credentials`, `make aws-creds-init`
- Global installation support via `uv tool install`

**Workflow Integration**:
- Interactive account selection for flexibility
- Direct account specification for automation
- File output for persistent configuration
- Dry-run mode for testing and validation

## Alternatives Considered

### 1. AWS CLI Built-in SSO (`aws configure sso`)
**Pros**: Official AWS solution, well-maintained
**Cons**: 
- Requires separate AWS CLI installation
- Complex initial setup per developer
- Doesn't integrate with existing setup workflow
- Limited customisation for team-specific needs

### 2. Third-party Tools (aws-vault, saml2aws)
**Pros**: Feature-rich, community-tested
**Cons**:
- Additional dependencies to manage
- Learning curve for team adoption
- May not integrate well with existing tooling
- Potential security and maintenance concerns

### 3. Custom Shell Scripts
**Pros**: Simple, customisable
**Cons**:
- Limited error handling and validation
- Difficult to maintain and extend
- No testing framework integration
- Platform-specific implementation challenges

### 4. Manual Process Improvements (documentation, aliases)
**Pros**: No additional tooling required
**Cons**:
- Still manual and error-prone
- Doesn't scale with team growth
- No automation benefits
- Limited improvement to developer experience

## Consequences

### Positive
- **Developer Experience**: Single command replaces 5+ manual steps
- **Time Savings**: ~2-3 minutes per credential refresh eliminated
- **Error Reduction**: Automated validation and format checking
- **Consistency**: Standardised process across all developers
- **Integration**: Seamless integration with existing CLI tooling
- **Flexibility**: Multiple output formats and account configurations
- **Security**: Secure credential handling with masking and validation
- **Testing**: Comprehensive test coverage ensures reliability
- **Maintainability**: Clean Architecture enables easy extension and modification

### Negative
- **Complexity**: Additional code to maintain and test
- **Dependencies**: boto3 and potential browser automation dependencies
- **Learning Curve**: Team needs to learn new commands (minimal, following existing patterns)
- **Network Dependency**: Requires internet connectivity for SSO authentication
- **Initial Setup**: One-time configuration required per developer

### Risk Mitigation
- **Comprehensive Testing**: 187+ unit and integration tests ensure reliability
- **Fallback Strategies**: Multiple authentication methods prevent single points of failure
- **Clear Documentation**: Extensive usage examples and troubleshooting guides
- **Security Best Practices**: Credential masking, temporary storage, format validation
- **Graceful Degradation**: Manual fallback instructions when automation fails
- **Configuration Security**: Example-only data in version control to prevent accidental exposure of real account information

### Security Risks

**Configuration File Exposure Risk - HIGH** (*if public repo*)
If developers accidentally commit real AWS account information to `aws_accounts.yaml`:

**Information at Risk:**
- AWS account IDs (enables targeted attacks)
- Corporate email patterns (phishing/social engineering)
- Internal account structure (reconnaissance)
- Company organizational details (competitive intelligence)

**Attack Scenarios:**
1. **Targeted Social Engineering**: Attackers use real email patterns and names for convincing phishing campaigns
2. **AWS Account Targeting**: Account IDs enable focused attacks on specific AWS resources
3. **Reconnaissance**: Internal infrastructure mapping and organizational structure discovery
4. **Supply Chain Attacks**: If repository is public, attackers gain insight into company's AWS footprint

**Mitigation Strategies:**
1. **Example-Only Approach**: Repository contains only generic example data
2. **Clear Warnings**: Multiple warnings in code comments and documentation
3. **Local Configuration**: Developers use local, untracked configuration files
4. **Git Hooks**: Pre-commit hooks to detect and block real account patterns
5. **Security Training**: Team education on configuration file security risks
6. **Regular Audits**: Periodic checks for accidentally committed sensitive information

**Alternative Secure Approaches:**
- Use environment variables only (no YAML files)
- Implement `.aws-accounts.local.yaml` (gitignored) approach
- Runtime account discovery via AWS APIs (no static configuration)

## Implementation Details

### Development Approach
1. **Test-Driven Development**: Write tests first for each component
2. **Clean Architecture**: Maintain separation of concerns and testability
3. **Security First**: Implement credential masking and validation from the start
4. **User Experience**: Design CLI interface with clear feedback and error messages

### Rollout Strategy
1. **Internal Testing**: Validate with development team members
2. **Documentation**: Create comprehensive usage guides and troubleshooting docs
3. **Training**: Team session to demonstrate new workflow
4. **Gradual Adoption**: Optional usage while maintaining manual process knowledge
5. **Full Migration**: Remove manual process documentation after successful adoption

### Success Metrics
- **Time Savings**: Measure reduction in credential retrieval time
- **Error Rate**: Track reduction in authentication-related issues
- **Adoption Rate**: Monitor command usage across team members
- **Feedback**: Collect developer experience improvements

## Related Decisions
- [ADR-0002: Clean Architecture Adoption](0002-clean-architecture-adoption.md) - Architectural foundation
- Future: ADR-0003: Multi-cloud credential management (if needed)

## Notes
This implementation focuses specifically on AWS SSO automation while maintaining the flexibility to extend to other cloud providers in the future. The Clean Architecture approach ensures that the core business logic remains independent of specific authentication mechanisms, making future enhancements straightforward.

The decision prioritises developer productivity and experience while maintaining security best practices and code quality standards established in the existing codebase.