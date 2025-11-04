# ForgeCRM API Reference

Complete REST API documentation for ForgeCRM microservice.

## Base Information

- **Base URL:** `http://localhost:8003` (development) or `https://your-domain.com`
- **API Prefix:** `/api/` (for some endpoints) or direct routes
- **Authentication:** Token-based or Session-based
- **Content Type:** `application/json`
- **API Version:** 1.0.0

## Authentication

### Token Authentication (Recommended)

```bash
# Get authentication token
curl -X POST http://localhost:8003/api-token-auth/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "your_password"
  }'

# Response
{
  "token": "e488a469df374c7d0f536f3b5e7424731f7c8452"
}

# Use token in subsequent requests
curl -H "Authorization: Token e488a469df374c7d0f536f3b5e7424731f7c8452" \
  http://localhost:8003/accounts/
```

### Session Authentication

Login via admin interface at `/admin/` and API calls will use session cookies.

## Health Check

### GET /health/

Check service health and database connectivity.

**Response:**
```json
{
  "status": "healthy",
  "database": "connected", 
  "version": "1.0.0",
  "timestamp": "2025-11-04T12:00:00Z"
}
```

## Accounts API

### GET /accounts/
List all accounts with filtering and search.

**Query Parameters:**
- `search` - Search by name, email, or phone
- `account_type` - Filter by type (customer, prospect, partner)
- `industry` - Filter by industry
- `owner` - Filter by owner username
- `ordering` - Sort by field (name, created_at, -created_at)

**Example:**
```bash
curl -H "Authorization: Token YOUR_TOKEN" \
  "http://localhost:8003/accounts/?account_type=customer&search=tech"
```

**Response:**
```json
[
  {
    "account_uuid": "47e4bd9d-f563-4e31-a0ea-0d7198a31fb5",
    "name": "TechCorp Solutions",
    "account_type": "customer",
    "industry": "technology",
    "phone": "555-0101",
    "email": "contact@techcorp.com",
    "website": "https://techcorp.com",
    "owner": "admin",
    "created_at": "2025-11-04T16:02:53.264857Z"
  }
]
```

### POST /accounts/
Create a new account.

**Request Body:**
```json
{
  "name": "New Company Inc",
  "account_type": "prospect",
  "industry": "technology",
  "phone": "555-1234",
  "email": "contact@newcompany.com",
  "website": "https://newcompany.com",
  "billing_address": "123 Main St, City, State 12345",
  "shipping_address": "123 Main St, City, State 12345",
  "description": "Prospective client for software solutions"
}
```

### GET /accounts/{uuid}/
Get specific account details.

### PUT /accounts/{uuid}/
Update entire account.

### PATCH /accounts/{uuid}/
Partially update account.

### DELETE /accounts/{uuid}/
Delete account.

### GET /accounts/{uuid}/summary/
Get account summary with related data.

**Response:**
```json
{
  "account": {
    "name": "TechCorp Solutions",
    "account_type": "customer",
    "industry": "technology"
  },
  "leads_count": 5,
  "opportunities_count": 2,
  "tasks_count": 3,
  "notes_count": 8,
  "total_opportunity_value": "275000.00",
  "recent_activities": [...]
}
```

## Leads API

### GET /leads/
List all leads with filtering.

**Query Parameters:**
- `search` - Search by name, company, email
- `status` - Filter by status (new, contacted, qualified, lost)
- `rating` - Filter by rating (hot, warm, cold)
- `owner` - Filter by owner username

### POST /leads/
Create new lead.

**Request Body:**
```json
{
  "full_name": "John Smith",
  "company": "StartupXYZ",
  "email": "john@startupxyz.com",
  "phone": "555-0401",
  "status": "new",
  "rating": "hot",
  "source": "website",
  "description": "Interested in CRM solution"
}
```

### POST /leads/{uuid}/convert/
Convert lead to opportunity.

**Request Body:**
```json
{
  "account_uuid": "existing-account-uuid",
  "opportunity_name": "StartupXYZ CRM Project",
  "amount": "50000.00",
  "close_date": "2025-12-31"
}
```

### GET /leads/stats/
Get lead statistics.

**Response:**
```json
{
  "total_leads": 150,
  "by_status": {
    "new": 45,
    "contacted": 60,
    "qualified": 30,
    "lost": 15
  },
  "by_rating": {
    "hot": 50,
    "warm": 70,
    "cold": 30
  },
  "conversion_rate": 20.0
}
```

## Opportunities API

### GET /opportunities/
List opportunities with filtering.

**Query Parameters:**
- `search` - Search by name or account
- `stage` - Filter by stage
- `owner` - Filter by owner
- `min_amount`, `max_amount` - Filter by amount range
- `close_date_after`, `close_date_before` - Filter by close date

### POST /opportunities/
Create new opportunity.

**Request Body:**
```json
{
  "name": "Enterprise CRM Implementation",
  "account_uuid": "account-uuid-here",
  "stage": "prospecting",
  "amount": "125000.00",
  "probability": 75,
  "close_date": "2025-12-15",
  "description": "Full CRM implementation with training"
}
```

### GET /opportunities/pipeline/
Get sales pipeline analysis.

**Response:**
```json
{
  "pipeline": [
    {
      "stage": "prospecting",
      "count": 25,
      "total_amount": "1250000.00",
      "weighted_value": "312500.00"
    },
    {
      "stage": "proposal",
      "count": 15,
      "total_amount": "875000.00",
      "weighted_value": "656250.00"
    }
  ],
  "total_pipeline_value": "5250000.00",
  "total_weighted_value": "3280000.00"
}
```

### GET /opportunities/forecast/
Get sales forecast.

**Query Parameters:**
- `period` - Forecast period (month, quarter, year)

**Response:**
```json
{
  "period": "2025-Q4",
  "forecast": {
    "committed": "850000.00",
    "best_case": "1200000.00",
    "pipeline": "2100000.00"
  },
  "by_month": [
    {
      "month": "2025-11",
      "committed": "250000.00",
      "best_case": "350000.00"
    }
  ]
}
```

## Tasks API

### GET /tasks/
List tasks with filtering.

**Query Parameters:**
- `search` - Search by subject or description
- `status` - Filter by status
- `priority` - Filter by priority
- `task_type` - Filter by type
- `assigned_to` - Filter by assignee
- `due_date_after`, `due_date_before` - Filter by due date

### POST /tasks/
Create new task.

**Request Body:**
```json
{
  "subject": "Follow up with prospect",
  "description": "Call to discuss proposal details",
  "task_type": "call",
  "status": "not_started",
  "priority": "high",
  "due_date": "2025-11-06T14:00:00Z",
  "assigned_to_username": "salesrep",
  "related_account_uuid": "account-uuid-here"
}
```

### GET /tasks/my_tasks/
Get tasks assigned to current user.

### POST /tasks/{uuid}/complete/
Mark task as completed.

**Request Body:**
```json
{
  "completion_notes": "Called and scheduled demo for next week"
}
```

## Notes API

### GET /notes/
List notes with filtering.

**Query Parameters:**
- `search` - Search note content
- `related_object_type` - Filter by related object type
- `created_by` - Filter by creator

### POST /notes/
Create new note.

**Request Body:**
```json
{
  "subject": "Meeting Notes",
  "content": "Discussed requirements and timeline",
  "related_account_uuid": "account-uuid-here",
  "is_private": false
}
```

## Campaigns API

### GET /campaigns/
List campaigns.

### POST /campaigns/
Create new campaign.

**Request Body:**
```json
{
  "name": "Q1 Email Campaign",
  "campaign_type": "email",
  "status": "planning",
  "start_date": "2025-01-01",
  "end_date": "2025-03-31",
  "budget": "25000.00",
  "expected_response": 1000,
  "description": "Quarterly email marketing campaign"
}
```

### GET /campaigns/analytics/
Get campaign performance analytics.

**Response:**
```json
{
  "total_campaigns": 12,
  "active_campaigns": 3,
  "total_budget": "150000.00",
  "total_cost": "125000.00",
  "average_response_rate": 15.5,
  "roi": 2.4
}
```

## Contact Management API

### GET /api/contact/
List contacts.

### POST /api/contact/
Create new contact.

**Request Body:**
```json
{
  "first_name": "Jane",
  "last_name": "Doe", 
  "emails": ["jane@company.com"],
  "phone_numbers": ["555-1234"],
  "addresses": ["123 Main St, City, State"]
}
```

## Error Responses

All endpoints return consistent error formats:

### 400 Bad Request
```json
{
  "error": "Bad Request",
  "details": {
    "field_name": ["This field is required."]
  }
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal Server Error",
  "message": "An unexpected error occurred."
}
```

## Rate Limiting

- **Development:** No rate limits
- **Production:** 1000 requests per hour per IP
- **Authenticated:** 5000 requests per hour per user

## Pagination

List endpoints support pagination:

**Query Parameters:**
- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 20, max: 100)

**Response Format:**
```json
{
  "count": 150,
  "next": "http://localhost:8003/accounts/?page=2",
  "previous": null,
  "results": [...]
}
```

## Field Validation

### Common Validations
- **Email fields:** Must be valid email format
- **UUID fields:** Must be valid UUID4 format
- **Date fields:** ISO 8601 format (YYYY-MM-DD)
- **DateTime fields:** ISO 8601 format with timezone
- **Phone numbers:** Flexible format, stored as string
- **Amount fields:** Decimal with up to 2 decimal places

### Account Types
- `customer` - Paying customers
- `prospect` - Potential customers  
- `partner` - Business partners
- `vendor` - Suppliers/vendors

### Lead Statuses
- `new` - New lead, not contacted
- `contacted` - Initial contact made
- `qualified` - Qualified as potential customer
- `lost` - Lead lost or not interested

### Opportunity Stages
- `prospecting` - Initial stage
- `needs_analysis` - Analyzing requirements
- `proposal` - Proposal sent
- `negotiation` - In negotiation
- `closed_won` - Successfully closed
- `closed_lost` - Lost opportunity

### Task Priorities
- `low` - Low priority
- `medium` - Medium priority  
- `high` - High priority
- `urgent` - Urgent priority

## API Versioning

Currently on version 1.0.0. Future versions will be backward compatible or provide migration paths.

## SDKs and Libraries

Currently available:
- **cURL examples** (this documentation)
- **Python requests** (examples in setup docs)

Planned:
- JavaScript/TypeScript SDK
- Python SDK
- Go SDK