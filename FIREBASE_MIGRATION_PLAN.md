# Firebase Migration Plan for Wunderlists

## Executive Summary

This document evaluates migrating Wunderlists from the current Railway/PostgreSQL/Lovable stack to Google Firebase. The migration is **feasible and recommended** for a hobby project due to Firebase's generous free tier and simplified architecture.

---

## Current vs Firebase Architecture

| Component | Current | Firebase |
|-----------|---------|----------|
| **Frontend Hosting** | Lovable | Firebase Hosting |
| **Backend API** | FastAPI on Railway | Eliminated (direct Firestore SDK) |
| **Database** | PostgreSQL on Railway | Cloud Firestore |
| **Authentication** | Custom (hashed passwords) | Firebase Authentication |
| **External APIs** | OpenWeatherMap, Google Calendar | Same (called from frontend or Cloud Functions) |

### Key Architectural Change

**Before:** Frontend → FastAPI REST API → PostgreSQL
**After:** Frontend → Firestore SDK (direct) → Cloud Firestore

This eliminates the need for a backend server entirely for basic CRUD operations.

---

## Cloud Firestore Data Structure

### Recommended Collection Schema

```
/users/{userId}
├── email: string
├── displayName: string
├── createdAt: timestamp
├── settings: map
│   └── timezone: string
│
├── /tasks/{taskId}
│   ├── title: string
│   ├── description: string
│   ├── isCompleted: boolean
│   ├── isTravelDay: boolean
│   ├── priority: string ("low" | "medium" | "high" | "urgent")
│   ├── dueDate: timestamp
│   ├── reminderDate: timestamp
│   ├── completedAt: timestamp
│   ├── listId: string (reference)
│   ├── createdAt: timestamp
│   └── updatedAt: timestamp
│
├── /lists/{listId}
│   ├── name: string
│   ├── description: string
│   ├── color: string (#hex)
│   ├── icon: string (emoji)
│   ├── isArchived: boolean
│   ├── createdAt: timestamp
│   └── updatedAt: timestamp
│
├── /calendarEvents/{eventId}
│   ├── title: string
│   ├── description: string
│   ├── location: string
│   ├── startTime: timestamp
│   ├── endTime: timestamp
│   ├── isAllDay: boolean
│   ├── color: string
│   ├── externalId: string
│   ├── externalSource: string
│   ├── createdAt: timestamp
│   └── updatedAt: timestamp
│
└── /locations/{locationId}
    ├── name: string
    ├── city: string
    ├── country: string
    ├── latitude: number
    ├── longitude: number
    ├── isFavorite: boolean
    ├── showInDashboard: boolean
    ├── createdAt: timestamp
    └── updatedAt: timestamp
```

### Why Subcollections Under Users?

- **Security**: Firestore rules can easily restrict access to user's own data
- **Scalability**: Each user's data is isolated
- **Querying**: Efficient queries within a user's scope
- **Real-time**: Listeners on subcollections for instant updates

---

## Firebase Authentication Setup

### Recommended Auth Providers

1. **Email/Password** (migrate existing users)
2. **Google Sign-In** (easy addition)

### Migration Path for Existing Users

```javascript
// One-time migration script using Firebase Admin SDK
const admin = require('firebase-admin');

async function migrateUsers(existingUsers) {
  for (const user of existingUsers) {
    await admin.auth().createUser({
      uid: `migrated_${user.id}`,  // or generate new
      email: user.email,
      displayName: user.full_name,
      // Users will need to reset passwords (Firebase won't accept existing hashes)
    });
  }
}
```

**Note**: Users will need to reset their passwords since Firebase Auth can't import bcrypt hashes.

---

## Frontend Code Changes

### Before (Current REST API calls)

```javascript
// Current: REST API with fetch
async function loadTasks() {
  const response = await fetch(`${API_BASE}/api/tasks/?is_completed=false`);
  const tasks = await response.json();
  // render tasks...
}

async function saveTask(task) {
  await fetch(`${API_BASE}/api/tasks/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(task)
  });
}
```

### After (Firestore SDK)

```javascript
// Firebase: Direct Firestore access
import { collection, query, where, onSnapshot, addDoc, serverTimestamp } from 'firebase/firestore';
import { auth, db } from './firebase-config';

function loadTasks() {
  const userId = auth.currentUser.uid;
  const tasksRef = collection(db, 'users', userId, 'tasks');
  const q = query(tasksRef, where('isCompleted', '==', false));

  // Real-time listener - UI updates automatically!
  onSnapshot(q, (snapshot) => {
    const tasks = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
    renderTasks(tasks);
  });
}

async function saveTask(task) {
  const userId = auth.currentUser.uid;
  await addDoc(collection(db, 'users', userId, 'tasks'), {
    ...task,
    createdAt: serverTimestamp(),
    updatedAt: serverTimestamp()
  });
  // No need to reload - real-time listener handles it!
}
```

---

## Firestore Security Rules

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can only access their own data
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;

      // Subcollections inherit user check
      match /tasks/{taskId} {
        allow read, write: if request.auth != null && request.auth.uid == userId;
      }

      match /lists/{listId} {
        allow read, write: if request.auth != null && request.auth.uid == userId;
      }

      match /calendarEvents/{eventId} {
        allow read, write: if request.auth != null && request.auth.uid == userId;
      }

      match /locations/{locationId} {
        allow read, write: if request.auth != null && request.auth.uid == userId;
      }
    }
  }
}
```

---

## Weather API Handling

### Option 1: Call directly from frontend (with API key protection)

Not recommended - exposes API key.

### Option 2: Cloud Functions (Recommended)

```javascript
// functions/index.js
const functions = require('firebase-functions');
const fetch = require('node-fetch');

exports.getWeather = functions.https.onCall(async (data, context) => {
  // Verify user is authenticated
  if (!context.auth) {
    throw new functions.https.HttpsError('unauthenticated', 'Must be logged in');
  }

  const { city, country } = data;
  const apiKey = functions.config().openweather.key;

  const response = await fetch(
    `https://api.openweathermap.org/data/2.5/weather?q=${city},${country}&appid=${apiKey}&units=metric`
  );

  return response.json();
});
```

---

## GitHub Actions Deployment

### firebase.json

```json
{
  "hosting": {
    "public": "frontend/static",
    "ignore": ["firebase.json", "**/.*", "**/node_modules/**"],
    "rewrites": [
      {
        "source": "**",
        "destination": "/index.html"
      }
    ]
  },
  "firestore": {
    "rules": "firestore.rules",
    "indexes": "firestore.indexes.json"
  },
  "functions": {
    "source": "functions"
  }
}
```

### .github/workflows/firebase-deploy.yml

```yaml
name: Deploy to Firebase

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build_and_deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      # If you add a build step later (e.g., bundling)
      # - name: Install dependencies
      #   run: npm ci
      # - name: Build
      #   run: npm run build

      - name: Deploy to Firebase Hosting (Preview)
        if: github.event_name == 'pull_request'
        uses: FirebaseExtended/action-hosting-deploy@v0
        with:
          repoToken: ${{ secrets.GITHUB_TOKEN }}
          firebaseServiceAccount: ${{ secrets.FIREBASE_SERVICE_ACCOUNT }}
          projectId: your-firebase-project-id
          channelId: preview-${{ github.event.pull_request.number }}

      - name: Deploy to Firebase Hosting (Production)
        if: github.event_name == 'push' && github.ref == 'refs/heads/main'
        uses: FirebaseExtended/action-hosting-deploy@v0
        with:
          repoToken: ${{ secrets.GITHUB_TOKEN }}
          firebaseServiceAccount: ${{ secrets.FIREBASE_SERVICE_ACCOUNT }}
          projectId: your-firebase-project-id
          channelId: live
```

---

## Migration Steps

### Phase 1: Setup (Day 1)
1. Create Firebase project in console
2. Enable Firestore, Authentication, Hosting
3. Install Firebase CLI: `npm install -g firebase-tools`
4. Initialize: `firebase init` (select Hosting, Firestore, Functions)
5. Add Firebase config to frontend

### Phase 2: Authentication (Day 2)
1. Add Firebase Auth SDK to frontend
2. Create login/signup UI
3. Implement auth state management
4. Migrate existing users (password reset flow)

### Phase 3: Data Migration (Day 3)
1. Write migration script to export PostgreSQL data
2. Transform to Firestore format
3. Import to Firestore using Admin SDK
4. Verify data integrity

### Phase 4: Frontend Refactor (Days 4-5)
1. Replace fetch calls with Firestore SDK
2. Add real-time listeners
3. Update error handling
4. Test all CRUD operations

### Phase 5: Cloud Functions (Day 6)
1. Move weather API to Cloud Function
2. Move Google Calendar sync to Cloud Function
3. Test external integrations

### Phase 6: Deployment (Day 7)
1. Set up GitHub Actions workflow
2. Configure Firebase secrets in GitHub
3. Test preview deployments
4. Deploy to production
5. Update DNS if using custom domain

### Phase 7: Cleanup
1. Archive Railway backend
2. Cancel Lovable hosting
3. Monitor Firebase usage/costs

---

## Cost Comparison

### Current (Railway + Lovable)
- Railway: ~$5-10/month (depending on usage)
- Lovable: Free tier likely
- **Total: ~$5-10/month**

### Firebase Free Tier (Spark Plan)
- Firestore: 1GB storage, 50K reads/day, 20K writes/day
- Hosting: 10GB storage, 360MB/day transfer
- Authentication: Unlimited
- Cloud Functions: 2M invocations/month
- **Total: $0/month** (for hobby use)

### Firebase Pay-as-you-go (Blaze Plan)
Only needed if you exceed free tier:
- Firestore: $0.18/100K reads, $0.18/100K writes
- Hosting: $0.026/GB
- Functions: $0.40/million invocations

**For a personal task app, you'll likely stay in free tier indefinitely.**

---

## Pros and Cons

### Pros
- **Free hosting** for hobby projects
- **Real-time sync** out of the box
- **No backend to maintain** (serverless)
- **Built-in authentication** with social logins
- **Automatic scaling** (not that you need it)
- **Better developer experience** with Firebase console
- **Offline support** with Firestore persistence

### Cons
- **Vendor lock-in** to Google ecosystem
- **NoSQL learning curve** if unfamiliar
- **Limited querying** compared to SQL (no JOINs)
- **Migration effort** required
- **Data export** more complex than PostgreSQL
- **Less control** over infrastructure

---

## Recommendation

**Go for it!** For a hobby/learning project, Firebase is an excellent choice because:

1. **Cost**: Free tier easily covers personal use
2. **Simplicity**: Eliminates backend maintenance
3. **Features**: Real-time sync, offline support, auth built-in
4. **Learning**: Great skills to have for modern web development
5. **Speed**: Faster development once set up

The migration effort is moderate (about a week of casual work), but the reduced complexity afterward is worth it.

---

## Next Steps

1. Create Firebase project at https://console.firebase.google.com
2. Run `firebase init` in this repository
3. Start with Phase 1 setup
4. Ask for help implementing any specific phase!

---

*Document created: January 2026*
*Last updated: January 2026*
