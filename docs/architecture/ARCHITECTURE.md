# Clean Architecture - Setup Environment System

## Architecture Overview

The Setup Environment System follows **Clean Architecture** principles (also known as **Hexagonal Architecture**), ensuring separation of concerns, testability, and framework independence.

## Layer Structure

```
┌─────────────────────────────────────────────────────────────┐
│                    EXTERNAL SYSTEMS                         │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌────────┐ │
│  │  User   │ │   Git   │ │Homebrew │ │ GitHub  │ │ YAML   │ │  
│  │   CLI   │ │Command  │   CLI     │ │  API    │ │Config  │ │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └────────┘ │
└─────────────────────────────────────────────────────────────┘
         │                    ▲         ▲         ▲         ▲
         │                    │         │         │         │
┌────────▼────────────────────────────────────────────────────┐
│                 PRESENTATION LAYER                          │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              CLI Interface                          │    │
│  │  • Click framework integration                      │    │
│  │  • Command parsing & validation                     │    │
│  │  • User interaction & progress reporting            │    │
│  │  • Error handling & display                         │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
         │
         │
┌────────▼────────────────────────────────────────────────────┐
│                 APPLICATION LAYER                           │
│                                                             │
│  ┌─────────────────────────┐    ┌─────────────────────────┐ │
│  │      USE CASES          │    │      INTERFACES         │ │
│  │                         │    │       (PORTS)           │ │
│  │  ┌─────────────────┐    │    │  ┌─────────────────┐    │ │
│  │  │SetupRepositories│◄───┼────┼──┤   GitService    │    │ │
│  │  │   UseCase       │    │    │  └─────────────────┘    │ │
│  │  └─────────────────┘    │    │                         │ │
│  │  ┌─────────────────┐    │    │  ┌─────────────────┐    │ │
│  │  │ InstallSoftware │◄───┼────┼──┤ SoftwareService │    │ │
│  │  │   UseCase       │    │    │  └─────────────────┘    │ │
│  │  └─────────────────┘    │    │                         │ │
│  │  ┌─────────────────┐    │    │  ┌─────────────────┐    │ │
│  │  │ConfigureNPMRC   │◄───┼────┼──┤  NPMRCService   │    │ │
│  │  │   UseCase       │    │    │  └─────────────────┘    │ │
│  │  └─────────────────┘    │    │                         │ │
│  └─────────────────────────┘    └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
         │                                   ▲
         │                                   │
┌────────▼────────────────────────────────────────────────────┐
│                   DOMAIN LAYER                              │
│                  (CORE BUSINESS)                            │
│                                                             │
│  ┌─────────────────────────┐    ┌─────────────────────────┐ │
│  │      ENTITIES           │    │    VALUE OBJECTS        │ │
│  │                         │    │                         │ │
│  │  ┌─────────────────┐    │    │  ┌─────────────────┐    │ │
│  │  │   Repository    │    │    │  │  DevFolderPath  │    │ │
│  │  │   • url         │    │    │  │  • validation   │    │ │
│  │  │   • org/name    │    │    │  │  • immutable    │    │ │
│  │  │   • target_path │    │    │  └─────────────────┘    │ │
│  │  └─────────────────┘    │    │                         │ │
│  │  ┌─────────────────┐    │    │  ┌─────────────────┐    │ │
│  │  │    Software     │    │    │  │PersonalAccess   │    │ │
│  │  │   • name/desc   │    │    │  │    Token        │    │ │
│  │  │   • commands    │    │    │  │  • validation   │    │ │
│  │  │   • required    │    │    │  │  • masking      │    │ │
│  │  └─────────────────┘    │    │  └─────────────────┘    │ │
│  │  ┌─────────────────┐    │    │                         │ │
│  │  │NPMRC Config     │    │    │  ┌─────────────────┐    │ │
│  │  │   • token       │    │    │  │InstallResponse  │    │ │
│  │  │   • registry    │    │    │  │  • YES/NO/ALL   │    │ │
│  │  │   • settings    │    │    │  │  • SKIP         │    │ │
│  │  └─────────────────┘    │    │  └─────────────────┘    │ │
│  └─────────────────────────┘    └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                                   ▲
                                   │
┌─────────────────────────────────────────────────────────────┐
│                INFRASTRUCTURE LAYER                         │
│                                                             │
│  ┌─────────────────────────┐    ┌─────────────────────────┐ │
│  │    GIT ADAPTERS         │    │   SOFTWARE ADAPTERS     │ │
│  │                         │    │                         │ │
│  │  ┌─────────────────┐    │    │  ┌─────────────────┐    │ │
│  │  │GitPythonService │    │    │  │BrewSoftwareServ │    │ │
│  │  │• clone_repo()   │    │    │  │• install_pkg()  │    │ │
│  │  │• check_exists() │    │    │  │• check_install()│    │ │
│  │  └─────────────────┘    │    │  └─────────────────┘    │ │
│  │  ┌─────────────────┐    │    │  ┌─────────────────┐    │ │
│  │  │GitInstallService│    │    │  │  PythonService  │    │ │
│  │  │• setup_ssh()    │    │    │  │• setup_python() │    │ │
│  │  │• config_git()   │    │    │  │• install_uv()   │    │ │
│  │  └─────────────────┘    │    │  └─────────────────┘    │ │
│  └─────────────────────────┘    │  ┌─────────────────┐    │ │
│                                 │  │   NVMService    │    │ │
│  ┌─────────────────────────┐    │  │• setup_node()   │    │ │
│  │   CONFIG ADAPTERS       │    │  │• install_nvm()  │    │ │
│  │                         │    │  └─────────────────┘    │ │
│  │  ┌─────────────────┐    │    └─────────────────────────┘ │
│  │  │NPMRCFileService │    │                                │
│  │  │• write_config() │    │                                │
│  │  │• check_token()  │    │                                │
│  │  └─────────────────┘    │                                │
│  │  ┌─────────────────┐    │                                │
│  │  │RepositoryConfig │    │                                │
│  │  │    Service      │    │                                │
│  │  │• load_yaml()    │    │                                │
│  │  │• parse_repos()  │    │                                │
│  │  └─────────────────┘    │                                │
│  └─────────────────────────┘                                │
└─────────────────────────────────────────────────────────────┘
         │         │         │         │         │
         ▼         ▼         ▼         ▼         ▼
┌─────────────────────────────────────────────────────────────┐
│                EXTERNAL SYSTEMS                             │
│   [Git CLI] [Homebrew] [FileSystem] [GitHub] [YAML Files]   │
└─────────────────────────────────────────────────────────────┘
```

## Key Principles

### 1. Dependency Rule
**Dependencies point INWARD only**: External → Presentation → Application → Domain

- ✅ Domain layer has NO dependencies on outer layers
- ✅ Application layer only depends on Domain
- ✅ Infrastructure implements interfaces from Application layer

### 2. Port & Adapter Pattern

**Primary Ports** (driven by external actors):
- CLI Interface receives commands from User

**Secondary Ports** (drive external systems):
- GitService, SoftwareService, NPMRCService interfaces
- Implemented by Infrastructure adapters

### 3. Benefits

- **🧪 Testable**: All external dependencies can be mocked
- **🔧 Flexible**: Easy to swap infrastructure components
- **📦 Framework Independent**: Core business logic isolated
- **🎯 Single Responsibility**: Each layer has distinct concerns

## Component Responsibilities

### Domain Layer (Core)
- **Entities**: Business objects with identity and lifecycle
- **Value Objects**: Immutable objects with validation rules
- **Domain Services**: Business logic that doesn't belong to entities

### Application Layer
- **Use Cases**: Orchestrate business workflows
- **Interfaces**: Define contracts for external dependencies
- **Business Rules**: Coordinate domain objects and external services

### Infrastructure Layer
- **Adapters**: Implement interfaces, handle I/O operations
- **External API Integration**: Git, Homebrew, File System access
- **Configuration**: YAML parsing, environment setup

### Presentation Layer
- **CLI Interface**: User interaction and command processing
- **Input Validation**: Command parsing and user input handling
- **Output Formatting**: Results presentation and error reporting

## Data Flow Example

```
1. User runs: setup-environment --dev-folder ~/dev
2. CLI parses command and validates inputs
3. CLI calls SetupRepositoriesUseCase.execute()
4. Use Case loads repositories via RepositoryConfigService
5. Use Case creates Repository entities from YAML data
6. Use Case calls GitService.clone_repository() for each repo
7. GitPythonService (adapter) executes actual git commands
8. Results flow back through layers to CLI
9. CLI presents formatted results to user
```

This architecture ensures maintainability, testability, and flexibility while keeping business logic separate from implementation details.