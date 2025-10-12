# Development Guide

## Development Phases

This project follows a structured development plan with 6 phases:

### Phase 0: Repository Setup ✅
- [x] Initialize project structure with directories
- [x] Create `.gitignore` for Python, Node.js, and environment files
- [x] Add `README.md` with project overview and setup instructions
- [x] Create `env.example` template for all required credentials

### Phase 1: Database & Backend Infrastructure
- [ ] Create Supabase project and implement database schema
- [ ] Build FastAPI backend with CRUD endpoints
- [ ] Set up Row Level Security (RLS) policies
- [ ] Create database functions for employee search and availability

### Phase 2: Enhanced Agent Implementation
- [ ] Integrate Supabase client into agent
- [ ] Implement warm transfer flow
- [ ] Add message taking and delivery services
- [ ] Replace mock data with real database queries

### Phase 3: Twilio & SIP Configuration
- [ ] Configure Twilio Elastic SIP Trunk
- [ ] Set up LiveKit SIP integration
- [ ] Implement call routing and room management
- [ ] Test inbound and outbound call flows

### Phase 4: Web Management Interface
- [ ] Create Next.js frontend application
- [ ] Build management dashboard pages
- [ ] Add real-time features with Supabase subscriptions
- [ ] Implement UI components for employee management

### Phase 5: Environment & Configuration
- [ ] Set up environment variables
- [ ] Create Docker configuration
- [ ] Add development setup scripts
- [ ] Document deployment procedures

### Phase 6: Testing & Deployment
- [ ] Test end-to-end call flows
- [ ] Test warm transfers and message delivery
- [ ] Deploy to production
- [ ] Set up monitoring and logging

## Development Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker (optional)
- Git

### Environment Setup

1. Copy environment template:
```bash
cp env.example .env
```

2. Fill in your credentials in `.env`:
   - LiveKit credentials
   - Twilio account details
   - Supabase project settings
   - AI service API keys

### Python Dependencies

Install using UV (recommended):
```bash
uv sync
```

Or using pip:
```bash
pip install -r requirements.txt
```

### Node.js Dependencies

For frontend development:
```bash
cd frontend
npm install
```

## Database Schema

### Tables

#### employees
- `id` (UUID, Primary Key)
- `name` (VARCHAR)
- `phone` (VARCHAR)
- `email` (VARCHAR)
- `department_id` (UUID, Foreign Key)
- `office` (VARCHAR)
- `roles` (TEXT[])
- `status` (VARCHAR)
- `availability_hours` (JSONB)

#### departments
- `id` (UUID, Primary Key)
- `name` (VARCHAR)
- `description` (TEXT)
- `available_hours` (JSONB)
- `routing_priority` (INTEGER)

#### company_info
- `id` (UUID, Primary Key)
- `company_name` (VARCHAR)
- `greeting_message` (TEXT)
- `business_hours` (JSONB)
- `settings` (JSONB)

#### call_logs
- `id` (UUID, Primary Key)
- `caller_phone` (VARCHAR)
- `caller_name` (VARCHAR)
- `employee_id` (UUID, Foreign Key)
- `timestamp` (TIMESTAMP)
- `duration` (INTERVAL)
- `status` (VARCHAR)
- `recording_url` (VARCHAR)

#### messages
- `id` (UUID, Primary Key)
- `from_caller` (VARCHAR)
- `to_employee_id` (UUID, Foreign Key)
- `message_text` (TEXT)
- `delivered_via` (TEXT[])
- `timestamp` (TIMESTAMP)
- `status` (VARCHAR)

## API Endpoints

### Backend API Structure

```
/api/
├── employees/          # Employee management
├── departments/        # Department management
├── company/           # Company settings
├── call-logs/         # Call history
└── messages/          # Message history
```

## Agent Architecture

### Basic Agent Flow
1. Receive SIP call
2. Extract caller information
3. Create unique room
4. Greet caller and understand intent
5. Search employee directory
6. Offer warm transfer or message taking
7. Handle transfer/message delivery
8. Log call details

### Warm Transfer Flow
1. Create consultation room
2. Call employee via SIP
3. Present caller information to employee
4. Employee chooses: accept/reject/message
5. Transfer caller to employee room
6. Disconnect agent from consultation

## Testing

### Unit Tests
```bash
pytest tests/
```

### Integration Tests
```bash
pytest tests/integration/
```

### End-to-End Tests
```bash
pytest tests/e2e/
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Code Style

### Python
- Follow PEP 8
- Use type hints
- Document functions with docstrings
- Use async/await for I/O operations

### TypeScript/React
- Use ESLint and Prettier
- Follow React best practices
- Use TypeScript strict mode
- Component-based architecture

## Git Workflow

1. Create feature branch from `main`
2. Make changes with descriptive commits
3. Add tests for new functionality
4. Run tests and linting
5. Create pull request
6. Code review and merge

## Deployment

### Development
```bash
# Backend
cd backend
uvicorn main:app --reload

# Frontend
cd frontend
npm run dev

# Agent
python livekit_basic_agent.py dev
```

### Production
```bash
# Using Docker
docker-compose up -d

# Or manual deployment
# See DEPLOYMENT.md for details
```

## Monitoring

### Logs
- Application logs: Structured JSON logging
- Error tracking: Sentry integration
- Performance: Custom metrics

### Health Checks
- Backend API health endpoint
- Database connection status
- External service availability

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Check Supabase credentials
   - Verify network connectivity
   - Check RLS policies

2. **SIP Call Issues**
   - Verify Twilio configuration
   - Check LiveKit SIP settings
   - Test with Twilio console

3. **Agent Not Responding**
   - Check API keys
   - Verify model downloads
   - Check audio device permissions

### Debug Mode

Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
python livekit_basic_agent.py dev
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Update documentation
6. Submit a pull request

## Resources

- [LiveKit Agents Documentation](https://docs.livekit.io/agents/)
- [Supabase Documentation](https://supabase.com/docs)
- [Twilio SIP Documentation](https://www.twilio.com/docs/sip-trunking)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)


