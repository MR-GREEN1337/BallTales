# BallTales Backend Routes Documentation

## Chat Routes (`/chat`)

### 1. Message Processing (`POST /chat`)
Handles general chat interactions with the MLB Agent.

```python
@router.post("")
async def chat(request: Request, chat_request: ChatRequest)
```

**Features:**
- Processes natural language queries about baseball
- Maintains conversation context and history
- Integrates user preferences into responses
- Rate limited to 30 requests per 60 seconds
- Returns structured MLB responses with:
  - Natural language message
  - Conversation context
  - Data analysis
  - Media suggestions
  - Chart visualizations

### 2. Video Analysis (`POST /chat/analyze-video`)
Processes baseball video content for detailed analysis.

```python
@router.post("/analyze-video")
async def analyze_video(request: Request, analysis_request: VideoAnalysisRequest, background_tasks: BackgroundTasks)
```

**Features:**
- Analyzes baseball video content using AI
- Provides insights on:
  - Player movements
  - Game situations
  - Strategic analysis
- Background task logging
- Rate limited to 30 requests/minute
- Language localization support

### 3. Image Analysis (`POST /chat/analyze-image`)
Analyzes baseball images for context and insights.

```python
@router.post("/analyze-image")
async def analyze_image(request: Request, analysis_request: ImageAnalysisRequest, background_tasks: BackgroundTasks)
```

**Features:**
- Supports multiple image types (SVG, JPEG)
- Identifies players, teams, and game situations
- Provides contextual suggestions
- Enhanced metadata tracking
- Background logging
- Error handling with detailed context
- Language localization

### 4. Suggestion Handler (`POST /chat/{suggestion_type}`)
Processes contextual suggestions based on media analysis.

```python
@router.post("/{suggestion_type}")
async def handle_suggestion(request: Request, suggestion_type: str, mediaUrl: str, userLang: str, analyzer: MediaAnalyzer)
```

**Features:**
- Entity recognition (teams/players)
- Pattern matching for media URLs
- Custom workflow handling
- Chart integration
- Language translation support
- Structured response formatting

## User Routes (`/user`)

### 1. Preference Updates (`POST /user/update-preferences`)
Manages user profile and baseball preferences.

```python
@router.post("/update-preferences")
async def update_preferences(request: Request, user_req: UpdateUserDataRequest)
```

**Features:**
- AI-powered preference analysis
- Conversation context understanding
- Structured preference schema:
  - Favorite home runs
  - Favorite players
  - Favorite teams
  - Language preferences
  - Stats preferences
  - Usage statistics
- Rate limiting protection
- Error handling

## Data Models

### Request Models

#### ChatRequest
```python
class ChatRequest(BaseModel):
    message: str
    history: List[Message]
    user_data: UserData
```

#### VideoAnalysisRequest
```python
class VideoAnalysisRequest(AnalysisRequest):
    videoUrl: HttpUrl
    userLang: str
```

#### ImageAnalysisRequest
```python
class ImageAnalysisRequest(BaseModel):
    imageUrl: HttpUrl
    message: str
    metadata: Optional[Dict[str, Any]]
    generate_variation: bool
```

#### UpdateUserDataRequest
```python
class UpdateUserDataRequest(BaseModel):
    messages: List[Dict[str, Any]]
    preferences: Dict[str, Any]
    user: Dict[str, Any]
```

### Response Models

#### MLBResponse
```python
class MLBResponse(TypedDict):
    message: str
    conversation: str
    data_type: str
    data: Dict[str, Any]
    context: Dict[str, Any]
    suggestions: List[str]
    media: Optional[Dict[str, Any]]
    chart: Optional[Dict[str, Any]]
```

#### AnalysisResponse
```python
class AnalysisResponse(BaseModel):
    summary: str
    details: Dict[str, Any]
    timestamp: datetime
    request_id: str
```

#### ImageAnalysisResponse
```python
class ImageAnalysisResponse(BaseModel):
    summary: str
    details: ImageAnalysisDetails
    timestamp: datetime
    request_id: str
    suggestions: List[SuggestionItem]
    metrics: Optional[Dict[str, Any]]
```

## Implementation Details

### Rate Limiting
- All endpoints protected with rate limiting
- 30 requests per 60 seconds per endpoint
- Configurable through FastAPI decorators

### Error Handling
- Structured error responses
- Detailed logging with context
- Background task error tracking
- HTTP exception mapping

### Localization
- Multi-language support
- Translation integration
- Language preference tracking
- Localized responses

### Background Tasks
- Asynchronous logging
- Performance metrics collection
- Error tracking
- Analytics processing

### Security
- Request validation
- Input sanitization
- Rate limiting
- Error masking

## Usage Examples

### Chat Interaction
```python
chat_request = ChatRequest(
    message="How's Judge doing this season?",
    history=[...],
    user_data=UserData(...)
)
response = await chat(request, chat_request)
```

### Image Analysis
```python
analysis_request = ImageAnalysisRequest(
    imageUrl="https://example.com/image.jpg",
    message="What can you tell me about this player?",
    userLang="en"
)
response = await analyze_image(request, analysis_request, background_tasks)
```

### User Preference Update
```python
user_request = UpdateUserDataRequest(
    messages=[...],
    preferences={"favoriteTeam": "Yankees"},
    user={"id": "123", "name": "John"}
)
response = await update_preferences(request, user_request)
```