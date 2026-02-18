# Pulse & Passion API - Frontend Integration Guide

**Base URL:** `https://your-railway-domain.railway.app` or `http://localhost:8000` (development)

**Last Updated:** February 19, 2026

---

## 📋 Table of Contents

1. [Authentication](#authentication)
2. [Articles API](#articles-api)
3. [Podcasts API](#podcasts-api)
4. [Videos API](#videos-api)
5. [Categories API](#categories-api)
6. [Homepage API](#homepage-api)
7. [Search & Recommendations](#search--recommendations)
8. [Error Handling](#error-handling)
9. [File Upload Guidelines](#file-upload-guidelines)
10. [Admin Panel Requirements](#admin-panel-requirements)

---

## 🔐 Authentication

All write operations (CREATE, UPDATE, DELETE) require authentication using JWT tokens.

### Login

**Endpoint:** `POST /api/auth/login/`

**Request:**
```json
{
  "email": "editor@example.com",
  "password": "your_password"
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Frontend Implementation:**
```typescript
// Store tokens in localStorage or secure storage
localStorage.setItem('access_token', response.access);
localStorage.setItem('refresh_token', response.refresh);

// Add to all authenticated requests
headers: {
  'Authorization': `Bearer ${localStorage.getItem('access_token')}`
}
```

### Refresh Token

**Endpoint:** `POST /api/auth/refresh/`

**Request:**
```json
{
  "refresh": "your_refresh_token"
}
```

**Response:**
```json
{
  "access": "new_access_token"
}
```

### Get Current User

**Endpoint:** `GET /api/users/me/`

**Headers:** `Authorization: Bearer {access_token}`

**Response:**
```json
{
  "id": 1,
  "email": "editor@example.com",
  "full_name": "John Doe",
  "is_editor": true,
  "is_admin": false
}
```

---

## 📰 Articles API

### List Articles (Public)

**Endpoint:** `GET /api/articles/`

**Query Parameters:**
- `status` - Filter by status: `DRAFT`, `REVIEW`, `PUBLISHED`
- `category` - Filter by category slug (e.g., `technology`)
- `content_type` - Filter by type: `NEWS`, `RESEARCH`, `ESSAY`
- `is_editor_pick` - Filter featured articles: `true` or `false`
- `ordering` - Sort by: `-published_at`, `view_count`, `-created_at`
- `page` - Page number (default: 1)

**Example Request:**
```
GET /api/articles/?status=PUBLISHED&ordering=-published_at&page=1
```

**Response:**
```json
{
  "count": 42,
  "next": "https://api.example.com/api/articles/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Breaking News: Climate Summit",
      "slug": "breaking-news-climate-summit",
      "subtitle": "World leaders gather to discuss...",
      "summary": "A comprehensive summary of the event...",
      "hero_image": "https://cdn.example.com/media/articles/heroes/2026/02/image.jpg",
      "category": {
        "id": 1,
        "name": "Environment",
        "slug": "environment"
      },
      "tags": ["climate", "politics", "environment"],
      "author": {
        "id": 5,
        "full_name": "Jane Reporter",
        "email": "jane@example.com"
      },
      "content_type": "NEWS",
      "status": "PUBLISHED",
      "is_editor_pick": true,
      "is_paywalled": false,
      "confidence_rating": "HIGH",
      "sources_count": 12,
      "experts_interviewed": 3,
      "view_count": 1542,
      "published_at": "2026-02-18T10:30:00Z",
      "created_at": "2026-02-17T15:00:00Z"
    }
  ]
}
```

### Get Single Article (Public)

**Endpoint:** `GET /api/articles/{slug}/`

**Response:** Same structure as list item, plus:
```json
{
  "body_content": "Full article content...",
  "what_we_dont_know": "Transparency note...",
  "meta_title": "SEO title",
  "meta_description": "SEO description",
  "schema_type": "NewsArticle",
  "updated_at": "2026-02-18T11:00:00Z"
}
```

**Note:** If `is_paywalled: true` and user is not authenticated, `body_content` will be truncated to 30%.

### Create Article (Authenticated - Editor/Admin)

**Endpoint:** `POST /api/articles/`

**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**For JSON data (no image):**
```json
{
  "title": "New Article Title",
  "slug": "new-article-title",
  "subtitle": "Subtitle here",
  "summary": "Brief summary for listing pages",
  "body": "Full article content in markdown or HTML",
  "category": 1,
  "tags": ["tag1", "tag2", "tag3"],
  "content_type": "NEWS",
  "status": "DRAFT",
  "is_editor_pick": false,
  "is_paywalled": false,
  "sources_count": 5,
  "experts_interviewed": 2,
  "confidence_rating": "MEDIUM",
  "what_we_dont_know": "Optional transparency note",
  "meta_title": "Optional SEO title",
  "meta_description": "Optional SEO description"
}
```

**For FormData (with image upload):**
```typescript
const formData = new FormData();
formData.append('title', 'New Article Title');
formData.append('slug', 'new-article-title');
formData.append('summary', 'Brief summary');
formData.append('body', 'Full content');
formData.append('category', '1');
formData.append('tags', JSON.stringify(['tag1', 'tag2']));
formData.append('content_type', 'NEWS');
formData.append('status', 'DRAFT');
formData.append('is_editor_pick', 'false');
formData.append('is_paywalled', 'false');
formData.append('sources_count', '5');
formData.append('confidence_rating', 'MEDIUM');

// Add image file
if (imageFile) {
  formData.append('hero_image', imageFile);
}

// Send request
fetch('/api/articles/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
    // Don't set Content-Type - browser sets it automatically with boundary
  },
  body: formData
});
```

**Field Constraints:**
- `title`: Max 300 characters (required)
- `slug`: Max 320 characters, unique, URL-safe (auto-generated if not provided)
- `summary`: Max 500 characters (required)
- `body`: No limit (required)
- `content_type`: One of `NEWS`, `RESEARCH`, `ESSAY`
- `status`: One of `DRAFT`, `REVIEW`, `PUBLISHED` (only editors can publish)
- `confidence_rating`: One of `HIGH`, `MEDIUM`, `LOW`
- `hero_image`: Image file (JPG, PNG, WebP) - max 10MB recommended

### Update Article (Authenticated - Editor/Admin)

**Endpoint:** `PATCH /api/articles/{slug}/`

**Headers:**
```
Authorization: Bearer {access_token}
```

**For JSON updates (no image change):**
```json
{
  "title": "Updated Title",
  "summary": "Updated summary",
  "status": "PUBLISHED"
}
```

**For FormData updates (with image):**
```typescript
const formData = new FormData();
formData.append('title', 'Updated Title');

// Only include fields you want to update
if (newImageFile) {
  formData.append('hero_image', newImageFile);
}

fetch(`/api/articles/${slug}/`, {
  method: 'PATCH',
  headers: {
    'Authorization': `Bearer ${token}`
  },
  body: formData
});
```

**Permission Rules:**
- Editors can only edit their own articles
- Editors cannot delete published articles
- Admins can edit/delete any article

### Delete Article (Authenticated - Admin only)

**Endpoint:** `DELETE /api/articles/{slug}/`

**Response:** `204 No Content`

### Increment Article View (Public)

**Endpoint:** `POST /api/articles/{slug}/increment_view/`

**No body required**

**Response:**
```json
{
  "view_count": 1543,
  "slug": "article-slug"
}
```

**When to use:** Call this when a user views the full article (not on list pages).

### Get Article Schema (Public - for SEO)

**Endpoint:** `GET /api/articles/{slug}/schema/`

**Response:** JSON-LD schema for SEO
```json
{
  "@context": "https://schema.org",
  "@type": "NewsArticle",
  "headline": "Article Title",
  "description": "Article summary",
  "datePublished": "2026-02-18T10:30:00Z",
  "dateModified": "2026-02-18T11:00:00Z",
  "author": {
    "@type": "Person",
    "name": "Jane Reporter"
  },
  "image": "https://cdn.example.com/media/articles/heroes/image.jpg"
}
```

---

## 🎙️ Podcasts API

### List Podcasts (Public)

**Endpoint:** `GET /api/podcasts/`

**Query Parameters:**
- `is_featured` - Filter featured: `true` or `false`
- `episode_number` - Filter by episode number
- `search` - Search in title, description, transcript
- `ordering` - Sort by: `-published_at`, `episode_number`

**Response:**
```json
{
  "count": 25,
  "results": [
    {
      "id": 1,
      "title": "Episode 10: The Future of AI",
      "slug": "episode-10-future-of-ai",
      "description": "We discuss artificial intelligence...",
      "audio_file": "https://cdn.example.com/media/podcasts/2026/02/episode10.mp3",
      "thumbnail": "https://cdn.example.com/media/podcasts/thumbnails/ep10.jpg",
      "episode_number": 10,
      "duration_seconds": 3600,
      "transcript": "Full transcript text...",
      "tags": ["ai", "technology", "future"],
      "related_articles": [...],
      "author": {...},
      "is_featured": true,
      "view_count": 523,
      "published_at": "2026-02-15T08:00:00Z",
      "created_at": "2026-02-14T10:00:00Z"
    }
  ]
}
```

### Get Single Podcast (Public)

**Endpoint:** `GET /api/podcasts/{slug}/`

### Create Podcast (Authenticated - Editor/Admin)

**Endpoint:** `POST /api/podcasts/`

**Use FormData for file uploads:**
```typescript
const formData = new FormData();
formData.append('title', 'Episode 11: Climate Tech');
formData.append('slug', 'episode-11-climate-tech');
formData.append('description', 'Full description');
formData.append('episode_number', '11');
formData.append('duration_seconds', '3600');
formData.append('tags', JSON.stringify(['climate', 'tech']));
formData.append('is_featured', 'false');

// Add audio file (required)
formData.append('audio_file', audioFile);

// Add thumbnail (optional)
if (thumbnailFile) {
  formData.append('thumbnail', thumbnailFile);
}

// Add transcript (optional)
if (transcript) {
  formData.append('transcript', transcript);
}
```

**Field Constraints:**
- `audio_file`: MP3, WAV, or M4A - required
- `thumbnail`: Image file - optional
- `duration_seconds`: Integer (seconds) - required
- `episode_number`: Integer - optional but recommended

### Update Podcast (Authenticated - Editor/Admin)

**Endpoint:** `PATCH /api/podcasts/{slug}/`

**Use FormData:**
```typescript
const formData = new FormData();

// Only include fields to update
formData.append('title', 'Updated Title');

if (newAudioFile) {
  formData.append('audio_file', newAudioFile);
}

fetch(`/api/podcasts/${slug}/`, {
  method: 'PATCH',
  headers: {
    'Authorization': `Bearer ${token}`
  },
  body: formData
});
```

### Delete Podcast (Authenticated - Admin only)

**Endpoint:** `DELETE /api/podcasts/{slug}/`

### Increment Podcast View (Public)

**Endpoint:** `POST /api/podcasts/{slug}/increment_view/`

**Response:**
```json
{
  "view_count": 524,
  "slug": "episode-10-future-of-ai"
}
```

---

## 🎥 Videos API

### List Videos (Public)

**Endpoint:** `GET /api/videos/`

**Query Parameters:**
- `is_featured` - Filter featured videos
- `search` - Search in title, description
- `ordering` - Sort by: `-published_at`

**Response:**
```json
{
  "count": 15,
  "results": [
    {
      "id": 1,
      "title": "Video Explainer: Quantum Computing",
      "slug": "video-explainer-quantum-computing",
      "description": "A visual guide to quantum computing",
      "video_file": null,
      "external_url": "https://youtube.com/watch?v=xyz123",
      "thumbnail": "https://cdn.example.com/media/videos/thumbnails/quantum.jpg",
      "duration_seconds": 600,
      "tags": ["quantum", "physics", "explainer"],
      "related_articles": [...],
      "author": {...},
      "is_featured": true,
      "view_count": 823,
      "published_at": "2026-02-16T12:00:00Z"
    }
  ]
}
```

### Create Video (Authenticated - Editor/Admin)

**Endpoint:** `POST /api/videos/`

**Option 1: External URL (YouTube/Vimeo)**
```json
{
  "title": "Video Title",
  "slug": "video-title",
  "description": "Video description",
  "external_url": "https://youtube.com/watch?v=example",
  "duration_seconds": 600,
  "tags": ["tag1", "tag2"],
  "is_featured": false
}
```

**Option 2: Uploaded Video File (FormData)**
```typescript
const formData = new FormData();
formData.append('title', 'Video Title');
formData.append('slug', 'video-title');
formData.append('description', 'Description');
formData.append('duration_seconds', '600');
formData.append('video_file', videoFile); // MP4 recommended
formData.append('thumbnail', thumbnailFile);
formData.append('tags', JSON.stringify(['tag1', 'tag2']));
```

**Note:** Either `video_file` OR `external_url` must be provided.

### Update Video (Authenticated - Editor/Admin)

**Endpoint:** `PATCH /api/videos/{slug}/`

### Delete Video (Authenticated - Admin only)

**Endpoint:** `DELETE /api/videos/{slug}/`

### Increment Video View (Public)

**Endpoint:** `POST /api/videos/{slug}/increment_view/`

**Response:**
```json
{
  "view_count": 824,
  "slug": "video-explainer-quantum-computing"
}
```

---

## 📁 Categories API

### List Categories (Public)

**Endpoint:** `GET /api/categories/`

**Response:**
```json
[
  {
    "id": 1,
    "name": "Technology",
    "slug": "technology",
    "description": "Tech news and analysis",
    "parent": null,
    "article_count": 42
  },
  {
    "id": 2,
    "name": "AI & Machine Learning",
    "slug": "ai-machine-learning",
    "description": "Artificial intelligence coverage",
    "parent": 1,
    "article_count": 15
  }
]
```

### Get Single Category (Public)

**Endpoint:** `GET /api/categories/{slug}/`

---

## 🏠 Homepage API

### Get Homepage Sections (Public)

**Endpoint:** `GET /api/homepage/`

**Response:**
```json
[
  {
    "id": 1,
    "title": "Editor's Picks",
    "slug": "editors-picks",
    "description": "Top stories selected by our editors",
    "position": 1,
    "is_active": true,
    "articles": [...],
    "podcasts": [...],
    "videos": [...]
  },
  {
    "id": 2,
    "title": "Latest News",
    "slug": "latest-news",
    "position": 2,
    "is_active": true,
    "articles": [...]
  }
]
```

---

## 🔍 Search & Recommendations

### Search Articles (Public)

**Endpoint:** `GET /api/search/?q={query}`

**Example:** `GET /api/search/?q=climate change`

**Response:**
```json
{
  "query": "climate change",
  "count": 8,
  "results": [
    // Array of articles matching the query
  ]
}
```

**Search Coverage:** Searches in article title, summary, body, and tags.

### Get Personalized Recommendations (Authenticated)

**Endpoint:** `GET /api/recommendations/`

**Headers:** `Authorization: Bearer {access_token}`

**Response:**
```json
{
  "recommendations": [
    // Array of recommended articles based on reading history
  ],
  "based_on": 15  // Number of articles in user's reading history
}
```

**Logic:**
- New users get editor picks
- Returning users get articles with similar tags to their reading history
- Reading profiles reset after 30 days of inactivity

---

## ⚠️ Error Handling

### HTTP Status Codes

| Code | Meaning | When it happens |
|------|---------|----------------|
| 200 | OK | Successful GET/PUT/PATCH |
| 201 | Created | Successful POST |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Invalid data (validation errors) |
| 401 | Unauthorized | Missing or invalid token |
| 403 | Forbidden | Not enough permissions |
| 404 | Not Found | Resource doesn't exist |
| 500 | Server Error | Backend error |

### Error Response Format

```json
{
  "detail": "Error message here"
}
```

**Validation errors (400):**
```json
{
  "title": ["This field is required."],
  "category": ["Invalid pk \"999\" - object does not exist."]
}
```

### Frontend Error Handling Example

```typescript
try {
  const response = await fetch('/api/articles/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(articleData)
  });

  if (!response.ok) {
    if (response.status === 401) {
      // Token expired - refresh or redirect to login
      await refreshToken();
    } else if (response.status === 400) {
      // Validation errors - show to user
      const errors = await response.json();
      showValidationErrors(errors);
    } else if (response.status === 403) {
      // Permission denied
      alert('You don\'t have permission to perform this action');
    }
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data = await response.json();
  return data;
} catch (error) {
  console.error('API Error:', error);
  throw error;
}
```

---

## 📤 File Upload Guidelines

### Supported File Types

**Images (hero_image, thumbnail):**
- JPG/JPEG
- PNG
- WebP
- GIF
- Max size: 10MB (recommended)

**Audio (podcast audio_file):**
- MP3 (recommended)
- WAV
- M4A
- Max size: 100MB (recommended)

**Video (video_file):**
- MP4 (recommended)
- WebM
- MOV
- Max size: 500MB (recommended)

### FormData Best Practices

```typescript
// ✅ CORRECT - Use FormData for file uploads
const formData = new FormData();
formData.append('title', 'Article Title');
formData.append('hero_image', imageFile);

fetch('/api/articles/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
    // ⚠️ DON'T set Content-Type for FormData
  },
  body: formData
});

// ❌ WRONG - Don't use JSON for file uploads
const jsonData = {
  title: 'Article Title',
  hero_image: imageFile  // This won't work!
};
```

### Image Upload Example (React)

```typescript
const handleImageUpload = async (file: File) => {
  const formData = new FormData();
  formData.append('title', title);
  formData.append('summary', summary);
  formData.append('body', body);
  formData.append('category', categoryId);
  formData.append('hero_image', file);
  
  const response = await fetch('/api/articles/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${getToken()}`
    },
    body: formData
  });
  
  return await response.json();
};
```

---

## 🎨 Admin Panel Requirements

### Recent Articles Section

**Endpoint to use:** `GET /api/articles/?ordering=-created_at`

**Display:**
- Show all articles (including drafts if user is editor/admin)
- Include edit button for each article
- Include delete button (admin only)
- Show status badge (DRAFT, REVIEW, PUBLISHED)

### Recent Podcasts Section

**Endpoint to use:** `GET /api/podcasts/?ordering=-created_at`

**Display:**
- Show all podcasts
- Include edit button
- Include delete button (admin only)
- Show play button with audio player

### Edit Functionality

**For Articles:**
1. Fetch article: `GET /api/articles/{slug}/`
2. Display form with current values
3. On submit: `PATCH /api/articles/{slug}/` with updated data
4. Show success/error messages

**For Podcasts:**
1. Fetch podcast: `GET /api/podcasts/{slug}/`
2. Display form with current values
3. On submit: `PATCH /api/podcasts/{slug}/` with FormData
4. Handle file updates (audio/thumbnail)

### Permission Checks

```typescript
// Check user permissions before showing edit/delete buttons
const canEdit = (item) => {
  if (currentUser.is_admin) return true;
  if (currentUser.is_editor && item.author.id === currentUser.id) return true;
  return false;
};

const canDelete = (item) => {
  if (currentUser.is_admin) return true;
  if (currentUser.is_editor && item.status !== 'PUBLISHED') return true;
  return false;
};
```

### Status Management

```typescript
// Status options based on user role
const getStatusOptions = (userRole) => {
  if (userRole === 'admin') {
    return ['DRAFT', 'REVIEW', 'PUBLISHED'];
  } else if (userRole === 'editor') {
    return ['DRAFT', 'REVIEW'];  // Can't directly publish
  }
  return ['DRAFT'];
};
```

---

## 🚀 Quick Start Checklist for Frontend Team

### Setup (5 minutes)
- [ ] Set base API URL in environment config
- [ ] Import Postman collection for testing
- [ ] Test login endpoint and store tokens
- [ ] Verify CORS settings with backend team

### Authentication (15 minutes)
- [ ] Implement login form
- [ ] Store JWT tokens securely
- [ ] Add auth interceptor for API calls
- [ ] Implement token refresh logic
- [ ] Handle 401 errors (redirect to login)

### Article Features (30 minutes)
- [ ] List articles with pagination
- [ ] Display single article
- [ ] Implement article create/edit forms
- [ ] Handle hero image uploads
- [ ] Add view tracking on article read

### Podcast Features (20 minutes)
- [ ] List podcasts
- [ ] Display podcast player
- [ ] Implement podcast create/edit forms
- [ ] Handle audio file uploads
- [ ] Add view tracking

### Admin Panel (45 minutes)
- [ ] Create dashboard with recent items
- [ ] Add edit buttons (permission-based)
- [ ] Add delete buttons (admin only)
- [ ] Implement status badges
- [ ] Add confirmation dialogs for destructive actions

---

## 📞 Support

**Backend Issues:** Check Railway logs at `https://railway.app/project/{project-id}/deployments`

**API Testing:** Import `Pulse_Passion_API.postman_collection.json` into Postman

**Common Issues:**
1. **404 on media files** - Media storage not configured (see media storage setup guide)
2. **401 Unauthorized** - Token expired, implement token refresh
3. **400 Bad Request on file upload** - Use FormData, not JSON
4. **403 Forbidden** - Check user permissions (editor vs admin)

---

**End of Documentation**
