// Peter Griffin Console Dashboard - Complete Rewrite

let eventSource = null;
let statusInterval = null;
let eventCount = 0;
let currentStreamingThought = null;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    console.log('[Dashboard] Initializing...');
    connectSSE();
    startStatusPolling();
    setupSuggestionForm();
});

// SSE Connection
function connectSSE() {
    if (eventSource) {
        eventSource.close();
    }
    
    eventSource = new EventSource('/api/activity/stream');
    
    eventSource.onopen = () => {
        console.log('[SSE] Connected');
        updateStatus('running');
    };
    
    eventSource.onmessage = (e) => {
        try {
            const activity = JSON.parse(e.data);
            handleActivity(activity);
        } catch (err) {
            console.error('[SSE] Parse error:', err);
        }
    };
    
    eventSource.onerror = () => {
        console.error('[SSE] Connection lost, reconnecting...');
        updateStatus('error');
        setTimeout(connectSSE, 5000);
    };
}

// Handle incoming activity
function handleActivity(activity) {
    const { type, details, timestamp } = activity;
    
    // Handle streaming thoughts specially
    if (type === 'thought_chunk') {
        handleStreamingThought(details);
        return;
    }
    
    // Finalize streaming thought
    if (type === 'thought' && currentStreamingThought) {
        finalizeStreamingThought();
        return;
    }
    
    // Create event element
    const event = createEvent(type, details, timestamp);
    appendEvent(event);
    
    eventCount++;
    document.getElementById('event-count').textContent = `${eventCount} events`;
}

// Handle streaming thought chunks
function handleStreamingThought(details) {
    if (!currentStreamingThought) {
        // Create new streaming thought
        const event = document.createElement('div');
        event.className = 'event thought streaming';
        event.innerHTML = `
            <div class="event-header">
                <span class="event-icon">💭</span>
                <span class="event-type">thinking</span>
                <span class="event-time">${formatTime(Date.now() / 1000)}</span>
            </div>
            <div class="event-content"></div>
        `;
        
        const feed = document.getElementById('console-feed');
        feed.appendChild(event);
        currentStreamingThought = event;
        scrollToBottom();
    }
    
    // Update content
    const content = currentStreamingThought.querySelector('.event-content');
    content.textContent = details.accumulated || details.chunk;
    scrollToBottom();
}

// Finalize streaming thought
function finalizeStreamingThought() {
    if (currentStreamingThought) {
        currentStreamingThought.classList.remove('streaming');
        currentStreamingThought = null;
    }
}

// Create event element
function createEvent(type, details, timestamp) {
    const event = document.createElement('div');
    event.className = `event ${type}`;
    
    const icon = getEventIcon(type);
    const label = getEventLabel(type);
    const content = getEventContent(type, details);
    
    event.innerHTML = `
        <div class="event-header">
            <span class="event-icon">${icon}</span>
            <span class="event-type">${label}</span>
            <span class="event-time">${formatTime(timestamp)}</span>
        </div>
        <div class="event-content">${content}</div>
    `;
    
    return event;
}

// Get event icon
function getEventIcon(type) {
    const icons = {
        thinking: '🤔',
        thought: '💭',
        get_feed: '📰',
        read_post: '👀',
        post_created: '📝',
        comment_created: '💬',
        upvote: '👍',
        downvote: '👎',
        search: '🔍',
        follow: '👤',
        rate_limit: '⏱️',
        error: '❌',
        suggestion_received: '💡',
        user_response: '💬',
        system: 'ℹ️'
    };
    return icons[type] || '•';
}

// Get event label
function getEventLabel(type) {
    const labels = {
        thinking: 'THINKING',
        thought: 'THOUGHT',
        get_feed: 'FETCH FEED',
        read_post: 'READ POST',
        post_created: 'POST',
        comment_created: 'COMMENT',
        upvote: 'UPVOTE',
        downvote: 'DOWNVOTE',
        search: 'SEARCH',
        follow: 'FOLLOW',
        rate_limit: 'RATE LIMIT',
        error: 'ERROR',
        suggestion_received: 'SUGGESTION',
        user_response: 'RESPONSE',
        system: 'SYSTEM'
    };
    return labels[type] || type.toUpperCase();
}

// Get event content
function getEventContent(type, details) {
    switch(type) {
        case 'thinking':
            return 'Peter is thinking...';
            
        case 'thought':
            return details.content || '';
            
        case 'get_feed':
            return `Fetched ${details.count || 0} posts (${details.sort || 'hot'})`;
            
        case 'read_post':
            return `<strong>${details.title || 'Unknown post'}</strong>`;
            
        case 'post_created':
            return `<strong>${details.title || 'Untitled'}</strong><br>→ ${details.submolt || 'unknown'}`;
            
        case 'comment_created':
            return details.content || '';
            
        case 'upvote':
        case 'downvote':
            return details.title ? details.title.substring(0, 80) : 'a post';
            
        case 'search':
            return `Query: "${details.query || 'unknown'}"`;
            
        case 'rate_limit':
            return `${details.message || 'Rate limit reached'}<br><span class="text-muted">→ ${details.comments_remaining !== undefined ? `${details.comments_remaining} comments left` : details.wait_until || 'Check limits'}</span>`;
            
        case 'error':
            return `<span class="text-error">${details.error || 'Unknown error'}</span>`;
            
        case 'suggestion_received':
            return details.text || 'No text';
            
        case 'user_response':
            return `<strong>Peter:</strong> "${details.message || 'No message'}"`;
            
        default:
            return JSON.stringify(details);
    }
}

// Append event to feed
function appendEvent(event) {
    const feed = document.getElementById('console-feed');
    feed.appendChild(event);
    scrollToBottom();
}

// Scroll to bottom
function scrollToBottom() {
    const feed = document.getElementById('console-feed');
    feed.scrollTop = feed.scrollHeight;
}

// Format time
function formatTime(timestamp) {
    const now = Date.now() / 1000;
    const diff = now - timestamp;
    
    if (diff < 5) return 'now';
    if (diff < 60) return `${Math.floor(diff)}s`;
    if (diff < 3600) return `${Math.floor(diff / 60)}m`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h`;
    return `${Math.floor(diff / 86400)}d`;
}

// Status polling
function startStatusPolling() {
    updateStatusInfo();
    statusInterval = setInterval(updateStatusInfo, 5000);
}

function updateStatusInfo() {
    fetch('/api/status')
        .then(res => res.json())
        .then(data => {
            // Update metrics
            const uptimeHours = Math.floor(data.uptime_hours);
            const uptimeMinutes = Math.floor((data.uptime_hours - uptimeHours) * 60);
            document.getElementById('uptime').textContent = `${uptimeHours}h ${uptimeMinutes}m`;
            document.getElementById('total-actions').textContent = data.total_actions;
            document.getElementById('success-rate').textContent = `${data.success_rate}%`;
            
            // Update rate limits
            if (data.rate_limits) {
                const { comments, posts } = data.rate_limits;
                
                // Comments
                const commentsUsed = document.getElementById('comments-used');
                const commentsBar = document.getElementById('comments-bar');
                const nextComment = document.getElementById('next-comment');
                
                commentsUsed.textContent = `${comments.used}/${comments.limit}`;
                const percentage = (comments.used / comments.limit) * 100;
                commentsBar.style.width = `${percentage}%`;
                
                if (comments.remaining === 0) {
                    commentsUsed.classList.add('limit-reached');
                    commentsBar.classList.add('warning');
                } else if (comments.remaining < 10) {
                    commentsUsed.classList.add('limit-warning');
                    commentsBar.classList.add('warning');
                } else {
                    commentsUsed.classList.remove('limit-reached', 'limit-warning');
                    commentsBar.classList.remove('warning');
                }
                
                nextComment.textContent = comments.next_available;
                
                // Posts
                const nextPost = document.getElementById('next-post');
                nextPost.textContent = posts.next_available;
                if (!posts.can_post) {
                    nextPost.classList.add('limit-warning');
                } else {
                    nextPost.classList.remove('limit-warning');
                }
            }
            
            // Update status
            if (data.running) {
                updateStatus('running');
            }
        })
        .catch(err => {
            console.error('[API] Status fetch error:', err);
            updateStatus('error');
        });
}

function updateStatus(status) {
    const indicator = document.getElementById('status-indicator');
    const text = document.getElementById('status-text');
    
    const statuses = {
        running: { text: 'Active', class: '' },
        error: { text: 'Error', class: 'error' },
        idle: { text: 'Idle', class: 'idle' }
    };
    
    const statusInfo = statuses[status] || statuses.idle;
    text.textContent = statusInfo.text;
    indicator.className = `status-indicator ${statusInfo.class}`;
}

// Suggestion form
function setupSuggestionForm() {
    const input = document.getElementById('suggestion-input');
    const button = document.getElementById('send-suggestion');
    
    button.addEventListener('click', sendSuggestion);
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendSuggestion();
        }
    });
}

function sendSuggestion() {
    const input = document.getElementById('suggestion-input');
    const text = input.value.trim();
    
    if (!text) return;
    
    fetch('/api/suggestions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            input.value = '';
            console.log('[Suggestion] Sent successfully');
        }
    })
    .catch(err => {
        console.error('[Suggestion] Error:', err);
    });
}

// Cleanup
window.addEventListener('beforeunload', () => {
    if (eventSource) eventSource.close();
    if (statusInterval) clearInterval(statusInterval);
});
