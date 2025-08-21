# Sidekick AI Architecture

## Overview

Sidekick AI is a production-ready AI assistant built with LangGraph, OpenAI, and Gradio. The application follows a modular, scalable architecture designed for maintainability and extensibility.

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Gradio UI     │    │   LangGraph     │    │   OpenAI API    │
│   (Frontend)    │◄──►│   Workflow      │◄──►│   (LLM)        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   State Mgmt    │    │   Tool System   │    │   External      │
│   & Validation  │    │   & Execution   │    │   APIs          │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Core Components

### 1. User Interface Layer (`src/ui/`)

- **Gradio Interface**: Modern web-based UI built with Gradio
- **State Management**: Handles UI state and user interactions
- **Error Handling**: Graceful error handling and user feedback
- **Resource Management**: Proper cleanup of resources

### 2. Core Logic Layer (`src/core/`)

- **Sidekick Class**: Main orchestrator for the AI workflow
- **State Management**: Typed state definitions and validation
- **Workflow Engine**: LangGraph-based workflow execution
- **Evaluation System**: Self-assessment and improvement loop

### 3. Tool System (`src/tools/`)

- **Browser Tools**: Web automation with Playwright
- **File Tools**: File system operations
- **External APIs**: Search, Wikipedia, notifications
- **Python REPL**: Code execution capabilities

### 4. Configuration & Utilities (`src/utils/`)

- **Environment Management**: Configuration validation
- **Logging**: Structured logging system
- **Error Handling**: Centralized error management

## LangGraph Workflow

The core of Sidekick AI is a LangGraph workflow that implements an iterative improvement loop:

```
START → WORKER → ROUTER → TOOLS/EVALUATOR → DECISION → END
  ↑                                    ↓
  └─────────── CONTINUE ───────────────┘
```

### Workflow Nodes

1. **Worker Node**: Processes user requests using available tools
2. **Router Node**: Determines whether to use tools or evaluate
3. **Tools Node**: Executes tool calls (web browsing, file operations, etc.)
4. **Evaluator Node**: Assesses whether success criteria are met
5. **Decision Node**: Routes based on evaluation results

### State Management

The workflow maintains state through a typed `State` object:

```python
class State(TypedDict):
    messages: List[Any]           # Conversation history
    success_criteria: str         # User-defined success criteria
    feedback_on_work: Optional[str]  # Evaluation feedback
    success_criteria_met: bool   # Whether criteria are satisfied
    user_input_needed: bool      # Whether user input is required
```

## Tool Architecture

### Tool Categories

1. **Browser Tools**: Web automation and research
2. **File Tools**: File system operations
3. **Search Tools**: Web search and information retrieval
4. **Code Tools**: Python code execution
5. **Notification Tools**: Push notifications

### Tool Integration

Tools are integrated using LangChain's tool system:

```python
# Tool definition
tool = Tool(
    name="tool_name",
    func=tool_function,
    description="Tool description"
)

# Tool binding to LLM
llm_with_tools = llm.bind_tools([tool1, tool2, tool3])
```

## Configuration Management

### Environment Variables

- **Required**: `OPENAI_API_KEY`
- **Optional**: `PUSHOVER_TOKEN`, `PUSHOVER_USER`, `SERPER_API_KEY`
- **Application**: `APP_ENV`, `APP_DEBUG`, `APP_HOST`, `APP_PORT`
- **Logging**: `LOG_LEVEL`, `LOG_FILE`

### Configuration Validation

The system validates configuration at startup:

```python
@classmethod
def validate(cls) -> bool:
    if not cls.OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is required")
    return True
```

## Error Handling & Resilience

### Error Categories

1. **Configuration Errors**: Missing API keys, invalid settings
2. **Runtime Errors**: Tool failures, API timeouts
3. **Resource Errors**: Memory issues, cleanup failures

### Error Handling Strategy

- **Graceful Degradation**: Continue operation with reduced functionality
- **User Feedback**: Clear error messages and recovery suggestions
- **Logging**: Comprehensive error logging for debugging
- **Resource Cleanup**: Proper cleanup even on failures

## Security Considerations

### API Key Management

- Environment variable storage
- No hardcoded secrets
- Optional API integrations

### Tool Execution

- Sandboxed file operations
- Controlled Python code execution
- Web browsing in controlled environment

### Input Validation

- Type checking with Pydantic
- Input sanitization
- Rate limiting considerations

## Performance & Scalability

### Optimization Strategies

- **Async Operations**: Non-blocking I/O operations
- **Resource Pooling**: Efficient resource management
- **Caching**: Conversation state persistence
- **Lazy Loading**: Tools loaded on demand

### Scalability Considerations

- **Stateless Design**: Minimal server-side state
- **Horizontal Scaling**: Docker containerization
- **Load Balancing**: Nginx reverse proxy support
- **Monitoring**: Health checks and metrics

## Deployment Architecture

### Container Strategy

- **Docker**: Multi-stage builds for optimization
- **Docker Compose**: Local development and testing
- **Health Checks**: Application health monitoring
- **Volume Mounts**: Persistent data storage

### Production Considerations

- **Environment Variables**: Secure configuration management
- **Logging**: Structured logging with rotation
- **Monitoring**: Health checks and metrics
- **Backup**: Data persistence strategies

## Testing Strategy

### Test Types

1. **Unit Tests**: Individual component testing
2. **Integration Tests**: Component interaction testing
3. **End-to-End Tests**: Full workflow testing
4. **Security Tests**: Vulnerability scanning

### Testing Tools

- **Pytest**: Test framework
- **Pytest-asyncio**: Async test support
- **Coverage**: Code coverage reporting
- **Mocking**: Dependency isolation

## Monitoring & Observability

### Logging

- Structured logging with configurable levels
- File and console output
- Log rotation and management

### Health Checks

- Application health endpoints
- Dependency health monitoring
- Graceful degradation

### Metrics

- Performance metrics collection
- Error rate monitoring
- Resource usage tracking

## Future Enhancements

### Planned Features

1. **Multi-Modal Support**: Image and audio processing
2. **Plugin System**: Extensible tool architecture
3. **User Management**: Multi-user support
4. **Advanced Analytics**: Usage analytics and insights
5. **Mobile Support**: Mobile-optimized interface

### Architecture Evolution

- **Microservices**: Service decomposition
- **Event-Driven**: Asynchronous event processing
- **API Gateway**: Centralized API management
- **Distributed Tracing**: Request flow tracking
