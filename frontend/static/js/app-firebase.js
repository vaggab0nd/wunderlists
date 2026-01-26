// Wunderlists - Firebase Edition
// Main application file with Firebase Authentication and Firestore

import {
  auth,
  db,
  googleProvider,
  onAuthStateChanged,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signOut,
  signInWithPopup,
  collection,
  doc,
  setDoc,
  getDoc,
  getDocs,
  addDoc,
  updateDoc,
  deleteDoc,
  query,
  where,
  orderBy,
  onSnapshot,
  serverTimestamp
} from './firebase-config.js';

// Current user reference
let currentUser = null;
let unsubscribeTasks = null;
let unsubscribeLists = null;
let unsubscribeEvents = null;
let unsubscribeLocations = null;

// ============================================
// AUTHENTICATION
// ============================================

// Initialize auth state listener
onAuthStateChanged(auth, async (user) => {
  if (user) {
    currentUser = user;
    await ensureUserDocument(user);
    showMainApp(user);
    initializeDataListeners();
  } else {
    currentUser = null;
    showAuthScreen();
    cleanupListeners();
  }
});

// Create user document in Firestore if it doesn't exist
async function ensureUserDocument(user) {
  const userRef = doc(db, 'users', user.uid);
  const userSnap = await getDoc(userRef);

  if (!userSnap.exists()) {
    await setDoc(userRef, {
      email: user.email,
      displayName: user.displayName || user.email.split('@')[0],
      createdAt: serverTimestamp(),
      settings: {
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
      }
    });
  }
}

// Show/hide screens
function showAuthScreen() {
  document.getElementById('authScreen').style.display = 'flex';
  document.getElementById('mainApp').style.display = 'none';
}

function showMainApp(user) {
  document.getElementById('authScreen').style.display = 'none';
  document.getElementById('mainApp').style.display = 'block';
  document.getElementById('userEmail').textContent = user.email;
}

// Auth form handlers - exposed to window for onclick handlers
window.showLogin = function() {
  document.getElementById('loginForm').style.display = 'block';
  document.getElementById('signupForm').style.display = 'none';
  clearAuthErrors();
};

window.showSignup = function() {
  document.getElementById('loginForm').style.display = 'none';
  document.getElementById('signupForm').style.display = 'block';
  clearAuthErrors();
};

function clearAuthErrors() {
  document.getElementById('loginError').textContent = '';
  document.getElementById('signupError').textContent = '';
}

// Login with email/password
window.handleLogin = async function(event) {
  event.preventDefault();
  const email = document.getElementById('loginEmail').value;
  const password = document.getElementById('loginPassword').value;
  const errorEl = document.getElementById('loginError');

  try {
    await signInWithEmailAndPassword(auth, email, password);
  } catch (error) {
    errorEl.textContent = getErrorMessage(error.code);
  }
};

// Signup with email/password
window.handleSignup = async function(event) {
  event.preventDefault();
  const name = document.getElementById('signupName').value;
  const email = document.getElementById('signupEmail').value;
  const password = document.getElementById('signupPassword').value;
  const errorEl = document.getElementById('signupError');

  try {
    const userCredential = await createUserWithEmailAndPassword(auth, email, password);
    // Create user document with display name
    await setDoc(doc(db, 'users', userCredential.user.uid), {
      email: email,
      displayName: name,
      createdAt: serverTimestamp(),
      settings: {
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
      }
    });
  } catch (error) {
    errorEl.textContent = getErrorMessage(error.code);
  }
};

// Login with Google
window.handleGoogleLogin = async function() {
  try {
    await signInWithPopup(auth, googleProvider);
  } catch (error) {
    const errorEl = document.getElementById('loginError');
    errorEl.textContent = getErrorMessage(error.code);
  }
};

// Logout
window.handleLogout = async function() {
  try {
    await signOut(auth);
  } catch (error) {
    console.error('Logout error:', error);
  }
};

// Convert Firebase error codes to user-friendly messages
function getErrorMessage(errorCode) {
  const errorMessages = {
    'auth/email-already-in-use': 'This email is already registered. Please sign in instead.',
    'auth/invalid-email': 'Please enter a valid email address.',
    'auth/operation-not-allowed': 'Email/password accounts are not enabled.',
    'auth/weak-password': 'Password should be at least 6 characters.',
    'auth/user-disabled': 'This account has been disabled.',
    'auth/user-not-found': 'No account found with this email.',
    'auth/wrong-password': 'Incorrect password. Please try again.',
    'auth/invalid-credential': 'Invalid email or password.',
    'auth/too-many-requests': 'Too many failed attempts. Please try again later.',
    'auth/popup-closed-by-user': 'Sign-in popup was closed before completing.',
    'auth/cancelled-popup-request': 'Sign-in was cancelled.',
    'auth/popup-blocked': 'Sign-in popup was blocked by the browser.'
  };
  return errorMessages[errorCode] || 'An error occurred. Please try again.';
}

// ============================================
// DATA LISTENERS (Real-time updates)
// ============================================

function initializeDataListeners() {
  if (!currentUser) return;

  // Tasks listener
  const tasksRef = collection(db, 'users', currentUser.uid, 'tasks');
  const tasksQuery = query(tasksRef, where('isCompleted', '==', false), orderBy('createdAt', 'desc'));
  unsubscribeTasks = onSnapshot(tasksQuery, (snapshot) => {
    const tasks = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
    renderTasks(tasks);
  }, (error) => {
    console.error('Tasks listener error:', error);
    renderTasksError();
  });

  // Lists listener
  const listsRef = collection(db, 'users', currentUser.uid, 'lists');
  const listsQuery = query(listsRef, orderBy('createdAt', 'desc'));
  unsubscribeLists = onSnapshot(listsQuery, (snapshot) => {
    const lists = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
    renderLists(lists);
    updateListsSelect(lists);
  }, (error) => {
    console.error('Lists listener error:', error);
    renderListsError();
  });

  // Calendar events listener
  const eventsRef = collection(db, 'users', currentUser.uid, 'calendarEvents');
  const eventsQuery = query(eventsRef, orderBy('startTime', 'asc'));
  unsubscribeEvents = onSnapshot(eventsQuery, (snapshot) => {
    const now = new Date();
    const events = snapshot.docs
      .map(doc => ({ id: doc.id, ...doc.data() }))
      .filter(event => event.startTime?.toDate() >= now);
    renderEvents(events.slice(0, 10));
  }, (error) => {
    console.error('Events listener error:', error);
    renderEventsError();
  });

  // Locations listener
  const locationsRef = collection(db, 'users', currentUser.uid, 'locations');
  const locationsQuery = query(locationsRef, where('showInDashboard', '==', true));
  unsubscribeLocations = onSnapshot(locationsQuery, (snapshot) => {
    const locations = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
    renderWeather(locations);
  }, (error) => {
    console.error('Locations listener error:', error);
    renderWeatherError();
  });
}

function cleanupListeners() {
  if (unsubscribeTasks) unsubscribeTasks();
  if (unsubscribeLists) unsubscribeLists();
  if (unsubscribeEvents) unsubscribeEvents();
  if (unsubscribeLocations) unsubscribeLocations();
}

// ============================================
// RENDER FUNCTIONS
// ============================================

function renderTasks(tasks) {
  const taskList = document.getElementById('taskList');

  if (tasks.length === 0) {
    taskList.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">checkmark</div>
        <div class="empty-state-text">No tasks yet. Create your first task!</div>
      </div>
    `;
    return;
  }

  taskList.innerHTML = tasks.map(task => `
    <div class="task-item priority-${task.priority || 'medium'}">
      <input type="checkbox" class="task-checkbox" ${task.isCompleted ? 'checked' : ''}
        onchange="toggleTask('${task.id}', this.checked)">
      <div class="task-content">
        <div class="task-title">${escapeHtml(task.title)}</div>
        <div class="task-meta">
          ${task.dueDate ? `Due: ${formatDate(task.dueDate)}` : 'No due date'}
          ${task.priority ? ` - ${task.priority}` : ''}
        </div>
      </div>
      <div class="task-actions">
        <button class="icon-btn" onclick="deleteTask('${task.id}')" title="Delete">delete</button>
      </div>
    </div>
  `).join('');
}

function renderTasksError() {
  document.getElementById('taskList').innerHTML = `
    <div class="empty-state">
      <div class="empty-state-text">Failed to load tasks</div>
    </div>
  `;
}

function renderLists(lists) {
  const listsGrid = document.getElementById('listsGrid');

  if (lists.length === 0) {
    listsGrid.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">folder</div>
        <div class="empty-state-text">Create your first list!</div>
      </div>
    `;
    return;
  }

  listsGrid.innerHTML = lists.map(list => `
    <div class="list-item" onclick="filterTasksByList('${list.id}')" style="border-color: ${list.color || '#3B82F6'}">
      <div class="list-icon">${list.icon || 'list'}</div>
      <div class="list-name">${escapeHtml(list.name)}</div>
    </div>
  `).join('');
}

function renderListsError() {
  document.getElementById('listsGrid').innerHTML = `
    <div class="empty-state">
      <div class="empty-state-text">Failed to load lists</div>
    </div>
  `;
}

function updateListsSelect(lists) {
  const select = document.getElementById('taskListSelect');
  if (select) {
    select.innerHTML = '<option value="">None</option>' +
      lists.map(list => `<option value="${list.id}">${escapeHtml(list.name)}</option>`).join('');
  }
}

function renderEvents(events) {
  const eventList = document.getElementById('eventList');

  if (events.length === 0) {
    eventList.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">calendar</div>
        <div class="empty-state-text">No upcoming events</div>
      </div>
    `;
    return;
  }

  eventList.innerHTML = events.map(event => `
    <div class="event-item">
      <div class="event-time">
        ${formatDateTime(event.startTime)}
      </div>
      <div class="event-title">${escapeHtml(event.title)}</div>
      ${event.location ? `<div class="event-location">location: ${escapeHtml(event.location)}</div>` : ''}
    </div>
  `).join('');
}

function renderEventsError() {
  document.getElementById('eventList').innerHTML = `
    <div class="empty-state">
      <div class="empty-state-text">Failed to load events</div>
    </div>
  `;
}

function renderWeather(locations) {
  const weatherGrid = document.getElementById('weatherGrid');

  if (locations.length === 0) {
    weatherGrid.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">globe</div>
        <div class="empty-state-text">Add locations to see weather information</div>
      </div>
    `;
    return;
  }

  // For now, show locations without weather data
  // Weather API calls will be handled by Cloud Functions in production
  weatherGrid.innerHTML = locations.map(loc => `
    <div class="weather-item">
      <div class="weather-info">
        <h3>${escapeHtml(loc.name)}</h3>
        <p>${escapeHtml(loc.city)}, ${escapeHtml(loc.country)}</p>
      </div>
      <div class="weather-temp">
        <div class="description">Weather data requires Cloud Functions setup</div>
      </div>
    </div>
  `).join('');
}

function renderWeatherError() {
  document.getElementById('weatherGrid').innerHTML = `
    <div class="empty-state">
      <div class="empty-state-text">Failed to load weather data</div>
    </div>
  `;
}

// ============================================
// CRUD OPERATIONS
// ============================================

// Tasks
window.toggleTask = async function(taskId, isCompleted) {
  if (!currentUser) return;

  try {
    const taskRef = doc(db, 'users', currentUser.uid, 'tasks', taskId);
    await updateDoc(taskRef, {
      isCompleted: isCompleted,
      completedAt: isCompleted ? serverTimestamp() : null,
      updatedAt: serverTimestamp()
    });
  } catch (error) {
    console.error('Failed to update task:', error);
    alert('Failed to update task');
  }
};

window.deleteTask = async function(taskId) {
  if (!currentUser) return;
  if (!confirm('Are you sure you want to delete this task?')) return;

  try {
    await deleteDoc(doc(db, 'users', currentUser.uid, 'tasks', taskId));
  } catch (error) {
    console.error('Failed to delete task:', error);
    alert('Failed to delete task');
  }
};

window.saveTask = async function(event) {
  event.preventDefault();
  if (!currentUser) return;

  const title = document.getElementById('taskTitle').value;
  const description = document.getElementById('taskDescription').value;
  const priority = document.getElementById('taskPriority').value;
  const dueDate = document.getElementById('taskDueDate').value;
  const listId = document.getElementById('taskListSelect').value;

  try {
    await addDoc(collection(db, 'users', currentUser.uid, 'tasks'), {
      title,
      description: description || null,
      priority,
      dueDate: dueDate ? new Date(dueDate) : null,
      listId: listId || null,
      isCompleted: false,
      isTravelDay: false,
      createdAt: serverTimestamp(),
      updatedAt: serverTimestamp()
    });
    closeTaskModal();
  } catch (error) {
    console.error('Failed to create task:', error);
    alert('Failed to create task');
  }
};

// Events
window.saveEvent = async function(event) {
  event.preventDefault();
  if (!currentUser) return;

  const title = document.getElementById('eventTitle').value;
  const description = document.getElementById('eventDescription').value;
  const location = document.getElementById('eventLocation').value;
  const startTime = document.getElementById('eventStartTime').value;
  const endTime = document.getElementById('eventEndTime').value;

  try {
    await addDoc(collection(db, 'users', currentUser.uid, 'calendarEvents'), {
      title,
      description: description || null,
      location: location || null,
      startTime: new Date(startTime),
      endTime: new Date(endTime),
      isAllDay: false,
      createdAt: serverTimestamp(),
      updatedAt: serverTimestamp()
    });
    closeEventModal();
  } catch (error) {
    console.error('Failed to create event:', error);
    alert('Failed to create event');
  }
};

// Locations
window.saveLocation = async function(event) {
  event.preventDefault();
  if (!currentUser) return;

  const name = document.getElementById('locationName').value;
  const city = document.getElementById('locationCity').value;
  const country = document.getElementById('locationCountry').value;

  try {
    await addDoc(collection(db, 'users', currentUser.uid, 'locations'), {
      name,
      city,
      country,
      latitude: null,
      longitude: null,
      isFavorite: false,
      showInDashboard: true,
      createdAt: serverTimestamp(),
      updatedAt: serverTimestamp()
    });
    closeLocationModal();
  } catch (error) {
    console.error('Failed to add location:', error);
    alert('Failed to add location');
  }
};

// Lists
window.saveList = async function(event) {
  event.preventDefault();
  if (!currentUser) return;

  const name = document.getElementById('listName').value;
  const description = document.getElementById('listDescription').value;
  const color = document.getElementById('listColor').value;
  const icon = document.getElementById('listIcon').value;

  try {
    await addDoc(collection(db, 'users', currentUser.uid, 'lists'), {
      name,
      description: description || null,
      color,
      icon: icon || null,
      isArchived: false,
      createdAt: serverTimestamp(),
      updatedAt: serverTimestamp()
    });
    closeListModal();
  } catch (error) {
    console.error('Failed to create list:', error);
    alert('Failed to create list');
  }
};

window.filterTasksByList = function(listId) {
  // TODO: Implement filtering
  alert(`Filtering by list ${listId} - feature coming soon!`);
};

// ============================================
// MODAL FUNCTIONS
// ============================================

window.openTaskModal = function() {
  document.getElementById('taskModal').classList.add('active');
};

window.closeTaskModal = function() {
  document.getElementById('taskModal').classList.remove('active');
  document.getElementById('taskTitle').value = '';
  document.getElementById('taskDescription').value = '';
  document.getElementById('taskDueDate').value = '';
  document.getElementById('taskPriority').value = 'medium';
};

window.openEventModal = function() {
  document.getElementById('eventModal').classList.add('active');
};

window.closeEventModal = function() {
  document.getElementById('eventModal').classList.remove('active');
  document.getElementById('eventTitle').value = '';
  document.getElementById('eventDescription').value = '';
  document.getElementById('eventLocation').value = '';
  document.getElementById('eventStartTime').value = '';
  document.getElementById('eventEndTime').value = '';
};

window.openLocationModal = function() {
  document.getElementById('locationModal').classList.add('active');
};

window.closeLocationModal = function() {
  document.getElementById('locationModal').classList.remove('active');
  document.getElementById('locationName').value = '';
  document.getElementById('locationCity').value = '';
  document.getElementById('locationCountry').value = '';
};

window.openListModal = function() {
  document.getElementById('listModal').classList.add('active');
};

window.closeListModal = function() {
  document.getElementById('listModal').classList.remove('active');
  document.getElementById('listName').value = '';
  document.getElementById('listDescription').value = '';
  document.getElementById('listColor').value = '#3B82F6';
  document.getElementById('listIcon').value = '';
};

// Manual refresh functions (for button clicks)
window.loadTasks = function() {
  // Real-time listener handles this automatically
  console.log('Tasks are updated in real-time');
};

window.loadEvents = function() {
  // Real-time listener handles this automatically
  console.log('Events are updated in real-time');
};

window.loadWeather = function() {
  // Real-time listener handles this automatically
  console.log('Weather locations are updated in real-time');
};

window.loadLists = function() {
  // Real-time listener handles this automatically
  console.log('Lists are updated in real-time');
};

// ============================================
// UTILITY FUNCTIONS
// ============================================

function escapeHtml(text) {
  if (!text) return '';
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function formatDate(timestamp) {
  if (!timestamp) return '';
  const date = timestamp.toDate ? timestamp.toDate() : new Date(timestamp);
  return date.toLocaleDateString();
}

function formatDateTime(timestamp) {
  if (!timestamp) return '';
  const date = timestamp.toDate ? timestamp.toDate() : new Date(timestamp);
  return date.toLocaleString();
}
