# 11. Test Strategy and Coverage

Date: 2025-08-10

## Status

Accepted

## Context

The setup-environment CLI required comprehensive testing to ensure:

1. **Reliability**: Critical tool for developer onboarding
2. **Refactoring confidence**: Enable safe code changes
3. **Documentation**: Tests serve as usage examples
4. **Quality assurance**: Catch bugs before users encounter them
5. **Clean Architecture validation**: Ensure proper layer separation

We needed a testing strategy that would cover unit, integration, and end-to-end scenarios whilst remaining maintainable.

## Decision

We adopted a multi-layered testing approach:

```
tests/setup_environment/
├── unit/                    # Isolated component tests
│   ├── domain/             # Pure business logic tests
│   ├── application/        # Use case tests with mocks
│   ├── infrastructure/     # Service implementation tests
│   └── presentation/       # CLI command tests
└── integration/            # End-to-end workflow tests
```

### Testing Principles:
1. **Test pyramid**: Many unit tests, fewer integration tests
2. **Mock at boundaries**: Mock external dependencies only
3. **Test behaviour**: Focus on outcomes, not implementation
4. **Fast feedback**: Most tests run in milliseconds
5. **Deterministic**: No flaky tests dependent on external state

## Consequences

### Positive

- **High confidence**: 205 tests with comprehensive coverage
- **Fast execution**: Unit tests run in under 1 second
- **Easy refactoring**: Tests catch breaking changes
- **Living documentation**: Tests show how to use components
- **Layer validation**: Tests ensure architectural boundaries
- **Regression prevention**: Bugs stay fixed

### Negative

- **Maintenance overhead**: Tests need updates with code changes
- **Initial investment**: Time to write comprehensive tests
- **Mock complexity**: Some mocks become complicated
- **False confidence**: High coverage doesn't guarantee correctness

## Test Categories

### 1. Domain Tests (Pure Logic)
```python
def test_repository_from_ssh_url():
    """Test Repository creation from SSH URL."""
    url = "git@github.com:facebook/react.git"
    repo = Repository.from_url(url)
    
    assert repo.organisation == "facebook"
    assert repo.name == "react"
    assert repo.url == url

def test_dev_folder_path_validation():
    """Test DevFolderPath validation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir)
        dev_folder = DevFolderPath(path)
        assert dev_folder.path == path
    
    # Test invalid path
    with pytest.raises(ValueError, match="does not exist"):
        DevFolderPath(Path("/nonexistent"))
```

### 2. Use Case Tests (Business Logic)
```python
@patch("src.setup_environment.application.use_cases.GitService")
def test_setup_repositories_use_case(mock_git_service):
    """Test repository setup orchestration."""
    # Arrange
    mock_git_service.clone_repository.return_value = CloneResult(
        repository=repo,
        path=Path("/dev/org/repo"),
        status=CloneStatus.SUCCESS,
    )
    
    use_case = SetupRepositoriesUseCase(mock_git_service)
    
    # Act
    result = use_case.execute([repo], dev_folder)
    
    # Assert
    assert result.success_count == 1
    assert len(result.successful) == 1
    mock_git_service.clone_repository.assert_called_once()
```

### 3. Infrastructure Tests (External Integration)
```python
@patch("subprocess.run")
def test_git_clone_command(mock_run):
    """Test Git clone subprocess call."""
    mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
    
    service = GitPythonService()
    result = service.clone_repository(repo, target_path)
    
    assert result.status == CloneStatus.SUCCESS
    mock_run.assert_called_with(
        ["git", "clone", repo.url, str(target_path)],
        capture_output=True,
        text=True,
        check=False,
    )
```

### 4. CLI Tests (User Interface)
```python
def test_cli_with_dry_run():
    """Test CLI in dry-run mode."""
    runner = CliRunner()
    
    with runner.isolated_filesystem():
        # Create test directory
        Path("dev").mkdir()
        
        result = runner.invoke(
            setup_environment,
            ["--dev-folder", "dev", "--dry-run"],
        )
        
        assert result.exit_code == 0
        assert "Dry-run mode" in result.output
        assert "Would clone" in result.output
```

### 5. Integration Tests (Full Workflow)
```python
def test_full_setup_workflow():
    """Test complete setup workflow end-to-end."""
    with tempfile.TemporaryDirectory() as tmpdir:
        dev_folder = Path(tmpdir)
        
        # Create test configuration
        config = {
            "repositories": [
                {"url": "https://github.com/test/repo.git"}
            ]
        }
        
        # Run full setup
        result = setup_environment_flow(
            dev_folder=dev_folder,
            config=config,
            dry_run=True,
        )
        
        assert result.success
        assert "Setup complete" in result.message
```

## Mocking Strategy

### Mock External Dependencies Only:
```python
# Good: Mock external service
@patch("subprocess.run")
def test_git_operation(mock_run):
    # Test git operation
    
# Bad: Mock internal component
@patch("src.domain.Repository")  # Don't mock domain objects
def test_bad_example(mock_repo):
    # This couples test to implementation
```

### Use Fixtures for Test Data:
```python
@pytest.fixture
def sample_repository():
    """Provide sample repository for tests."""
    return Repository.from_url("git@github.com:test/repo.git")

@pytest.fixture
def temp_dev_folder():
    """Provide temporary dev folder for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield DevFolderPath(Path(tmpdir))
```

## Coverage Strategy

### Target Coverage:
- **Domain Layer**: 100% (pure logic, easy to test)
- **Application Layer**: 95%+ (business logic coverage)
- **Infrastructure Layer**: 80%+ (mock external calls)
- **Presentation Layer**: 70%+ (CLI interaction tests)
- **Overall**: 85%+ coverage target

### Coverage Execution:
```bash
# Run with coverage
uv run pytest --cov=src/setup_environment --cov-report=term-missing

# Generate HTML report
uv run pytest --cov=src/setup_environment --cov-report=html

# Fail if below threshold
uv run pytest --cov=src/setup_environment --cov-fail-under=85
```

## Test Organisation

### Naming Conventions:
```python
# Test file: test_{module_name}.py
test_repository.py

# Test class: Test{ClassName}
class TestRepository:
    
# Test method: test_{scenario}_{expected_outcome}
def test_from_url_with_ssh_creates_repository(self):
def test_from_url_with_invalid_raises_error(self):
```

### Parametrised Tests:
```python
@pytest.mark.parametrize("url,expected_org,expected_name", [
    ("git@github.com:facebook/react.git", "facebook", "react"),
    ("https://github.com/microsoft/vscode.git", "microsoft", "vscode"),
    ("git@github.com:org/repo", "org", "repo"),
])
def test_repository_parsing(url, expected_org, expected_name):
    repo = Repository.from_url(url)
    assert repo.organisation == expected_org
    assert repo.name == expected_name
```

## Continuous Integration

### GitHub Actions Workflow:
```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh
      - name: Install dependencies
        run: uv sync
      - name: Run tests
        run: uv run pytest --cov=src/setup_environment
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## Best Practices

1. **Test one thing**: Each test should verify single behaviour
2. **Use descriptive names**: Test names should explain what and why
3. **Arrange-Act-Assert**: Structure tests consistently
4. **Don't test implementation**: Test behaviour, not how
5. **Keep tests simple**: Tests should be obviously correct
6. **Run tests frequently**: Part of development workflow
7. **Fix broken tests immediately**: Don't let them accumulate

## Lessons Learnt

1. **Unit tests catch most bugs**: Investment in unit tests pays off
2. **Mocking subprocess works well**: Reliable way to test CLI tools
3. **CliRunner is excellent**: Makes CLI testing straightforward
4. **Fixtures reduce duplication**: Reusable test data is valuable
5. **Coverage isn't everything**: Focus on meaningful tests
6. **Integration tests find issues**: Catch problems unit tests miss

## Future Improvements

- Add mutation testing to validate test effectiveness
- Performance benchmarks for critical paths
- Property-based testing for complex validation
- Snapshot testing for CLI output
- Contract tests for external services
- Load testing for concurrent operations

## References

- [pytest Documentation](https://docs.pytest.org/)
- [Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html)
- [Mocking Best Practices](https://docs.python.org/3/library/unittest.mock.html)