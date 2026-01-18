// API Base URL
const API_BASE = window.location.origin;

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    loadWeather();
    loadTasks();
    loadEvents();
    loadLists();
    loadListsForSelect();
});

// Weather Functions
async function loadWeather() {
    const weatherGrid = document.getElementById('weatherGrid');
    try {
        const response = await fetch(`${API_BASE}/api/weather/dashboard`);
        const data = await response.json();

        if (data.length === 0) {
            weatherGrid.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">🌍</div>
                    <div class="empty-state-text">Add locations to see weather information</div>
                </div>
            `;
            return;
        }

        weatherGrid.innerHTML = data.map(item => `
            <div class="weather-item">
                <div class="weather-info">
                    <h3>${item.location.name}</h3>
                    <p>${item.location.city}, ${item.location.country}</p>
                </div>
                <div class="weather-temp">
                    ${item.weather.error ? `
                        <div class="description" style="color: var(--danger);">${item.weather.error}</div>
                    ` : `
                        <div class="temp">${item.weather.temperature}°C</div>
                        <div class="description">${item.weather.description}</div>
                    `}
                </div>
            </div>
        `).join('');
    } catch (error) {
        weatherGrid.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-text">Failed to load weather data</div>
            </div>
        `;
    }
}

// Task Functions
async function loadTasks() {
    const taskList = document.getElementById('taskList');
    try {
        const response = await fetch(`${API_BASE}/api/tasks/?is_completed=false`);
        const tasks = await response.json();

        if (tasks.length === 0) {
            taskList.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">✅</div>
                    <div class="empty-state-text">No tasks yet. Create your first task!</div>
                </div>
            `;
            return;
        }

        taskList.innerHTML = tasks.map(task => `
            <div class="task-item priority-${task.priority}">
                <input type="checkbox" class="task-checkbox" ${task.is_completed ? 'checked' : ''}
                    onchange="toggleTask(${task.id}, this.checked)">
                <div class="task-content">
                    <div class="task-title">${task.title}</div>
                    <div class="task-meta">
                        ${task.due_date ? `Due: ${new Date(task.due_date).toLocaleDateString()}` : 'No due date'}
                        ${task.priority ? ` · ${task.priority}` : ''}
                    </div>
                </div>
                <div class="task-actions">
                    <button class="icon-btn" onclick="deleteTask(${task.id})" title="Delete">🗑️</button>
                </div>
            </div>
        `).join('');
    } catch (error) {
        taskList.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-text">Failed to load tasks</div>
            </div>
        `;
    }
}

async function toggleTask(taskId, isCompleted) {
    try {
        await fetch(`${API_BASE}/api/tasks/${taskId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ is_completed: isCompleted })
        });
        loadTasks();
    } catch (error) {
        console.error('Failed to update task:', error);
        alert('Failed to update task');
    }
}

async function deleteTask(taskId) {
    if (!confirm('Are you sure you want to delete this task?')) return;

    try {
        await fetch(`${API_BASE}/api/tasks/${taskId}`, { method: 'DELETE' });
        loadTasks();
    } catch (error) {
        console.error('Failed to delete task:', error);
        alert('Failed to delete task');
    }
}

// Event Functions
async function loadEvents() {
    const eventList = document.getElementById('eventList');
    try {
        const now = new Date().toISOString();
        const response = await fetch(`${API_BASE}/api/calendar/events?start_date=${now}`);
        const events = await response.json();

        if (events.length === 0) {
            eventList.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">📅</div>
                    <div class="empty-state-text">No upcoming events</div>
                </div>
            `;
            return;
        }

        eventList.innerHTML = events.slice(0, 10).map(event => `
            <div class="event-item">
                <div class="event-time">
                    ${new Date(event.start_time).toLocaleString()}
                </div>
                <div class="event-title">${event.title}</div>
                ${event.location ? `<div class="event-location">📍 ${event.location}</div>` : ''}
            </div>
        `).join('');
    } catch (error) {
        eventList.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-text">Failed to load events</div>
            </div>
        `;
    }
}

// List Functions
async function loadLists() {
    const listsGrid = document.getElementById('listsGrid');
    try {
        const response = await fetch(`${API_BASE}/api/lists/`);
        const lists = await response.json();

        if (lists.length === 0) {
            listsGrid.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">📁</div>
                    <div class="empty-state-text">Create your first list!</div>
                </div>
            `;
            return;
        }

        listsGrid.innerHTML = lists.map(list => `
            <div class="list-item" onclick="filterTasksByList(${list.id})" style="border-color: ${list.color}">
                <div class="list-icon">${list.icon || '📋'}</div>
                <div class="list-name">${list.name}</div>
            </div>
        `).join('');
    } catch (error) {
        listsGrid.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-text">Failed to load lists</div>
            </div>
        `;
    }
}

async function loadListsForSelect() {
    try {
        const response = await fetch(`${API_BASE}/api/lists/`);
        const lists = await response.json();

        const select = document.getElementById('taskList');
        select.innerHTML = '<option value="">None</option>' +
            lists.map(list => `<option value="${list.id}">${list.name}</option>`).join('');
    } catch (error) {
        console.error('Failed to load lists for select:', error);
    }
}

function filterTasksByList(listId) {
    // TODO: Implement filtering
    alert(`Filtering by list ${listId} - feature coming soon!`);
}

// Modal Functions
function openTaskModal() {
    document.getElementById('taskModal').classList.add('active');
}

function closeTaskModal() {
    document.getElementById('taskModal').classList.remove('active');
    document.getElementById('taskTitle').value = '';
    document.getElementById('taskDescription').value = '';
    document.getElementById('taskDueDate').value = '';
}

function openEventModal() {
    document.getElementById('eventModal').classList.add('active');
}

function closeEventModal() {
    document.getElementById('eventModal').classList.remove('active');
}

function openLocationModal() {
    document.getElementById('locationModal').classList.add('active');
}

function closeLocationModal() {
    document.getElementById('locationModal').classList.remove('active');
}

function openListModal() {
    document.getElementById('listModal').classList.add('active');
}

function closeListModal() {
    document.getElementById('listModal').classList.remove('active');
}

// Save Functions
async function saveTask(event) {
    event.preventDefault();

    const task = {
        title: document.getElementById('taskTitle').value,
        description: document.getElementById('taskDescription').value || null,
        priority: document.getElementById('taskPriority').value,
        due_date: document.getElementById('taskDueDate').value || null,
        list_id: document.getElementById('taskList').value || null
    };

    try {
        const response = await fetch(`${API_BASE}/api/tasks/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(task)
        });

        if (response.ok) {
            closeTaskModal();
            loadTasks();
        } else {
            alert('Failed to create task');
        }
    } catch (error) {
        console.error('Failed to create task:', error);
        alert('Failed to create task');
    }
}

async function saveEvent(event) {
    event.preventDefault();

    const calendarEvent = {
        title: document.getElementById('eventTitle').value,
        description: document.getElementById('eventDescription').value || null,
        location: document.getElementById('eventLocation').value || null,
        start_time: document.getElementById('eventStartTime').value,
        end_time: document.getElementById('eventEndTime').value
    };

    try {
        const response = await fetch(`${API_BASE}/api/calendar/events`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(calendarEvent)
        });

        if (response.ok) {
            closeEventModal();
            loadEvents();
        } else {
            alert('Failed to create event');
        }
    } catch (error) {
        console.error('Failed to create event:', error);
        alert('Failed to create event');
    }
}

async function saveLocation(event) {
    event.preventDefault();

    const location = {
        name: document.getElementById('locationName').value,
        city: document.getElementById('locationCity').value,
        country: document.getElementById('locationCountry').value
    };

    try {
        const response = await fetch(`${API_BASE}/api/locations/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(location)
        });

        if (response.ok) {
            closeLocationModal();
            loadWeather();
        } else {
            alert('Failed to add location');
        }
    } catch (error) {
        console.error('Failed to add location:', error);
        alert('Failed to add location');
    }
}

async function saveList(event) {
    event.preventDefault();

    const list = {
        name: document.getElementById('listName').value,
        description: document.getElementById('listDescription').value || null,
        color: document.getElementById('listColor').value,
        icon: document.getElementById('listIcon').value || null
    };

    try {
        const response = await fetch(`${API_BASE}/api/lists/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(list)
        });

        if (response.ok) {
            closeListModal();
            loadLists();
            loadListsForSelect();
        } else {
            alert('Failed to create list');
        }
    } catch (error) {
        console.error('Failed to create list:', error);
        alert('Failed to create list');
    }
}
