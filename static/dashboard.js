let eventSource = null;
let statusInterval = null;

const activityIcons = {
    post_created: '📝',
    comment_created: '💬',
    upvote: '👍',
    downvote: '👎',
    search: '🔍',
    follow: '👤',
    suggestion_received: '💡',
    thinking: '🤔',
    thought: '💭',
    get_feed: '📰',
    read_post: '👀',
    user_response: '💬',
    rate_limit: '⏱️',
    error: '❌',
    system: 'ℹ️'
};

function formatTimestamp(timestamp) {
    const now = Date.now() / 1000;
    const diff = now - timestamp;
    
    if (diff < 60) return 'Just now';
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    return `${Math.floor(diff / 86400)}d ago`;
}

function updateTimestamps() {
    document.querySelectorAll('.feed-item-time').forEach(elem => {
        const timestamp = parseFloat(elem.getAttribute('data-timestamp'));
        if (timestamp > 0) {
            elem.textContent = formatTimestamp(timestamp);
        }
    });
}

function createFeedItem(activity) {
    const item = document.createElement('div');
    item.className = `feed-item ${activity.type} new`;
    
    const icon = activityIcons[activity.type] || '📌';
    const details = activity.details || {};
    
    let detailsHTML = '';
    
    if (activity.type === 'post_created') {
        detailsHTML = `
            <div class="feed-item-title">${details.title || 'Untitled Post'}</div>
            <div class="feed-item-details">Posted to m/${details.submolt || 'unknown'}</div>
        `;
    } else if (activity.type === 'comment_created') {
        detailsHTML = `
            <div class="feed-item-details">
                ${details.content ? details.content.substring(0, 100) + (details.content.length > 100 ? '...' : '') : 'Commented on a post'}
            </div>
        `;
    } else if (activity.type === 'upvote') {
        detailsHTML = `
            <div class="feed-item-details">Upvoted: ${details.title ? details.title.substring(0, 60) : 'a post'}</div>
        `;
    } else if (activity.type === 'downvote') {
        detailsHTML = `
            <div class="feed-item-details">Downvoted: ${details.title ? details.title.substring(0, 60) : 'a post'}</div>
        `;
    } else if (activity.type === 'search') {
        detailsHTML = `
            <div class="feed-item-details">Searched for: "${details.query || 'unknown'}"</div>
        `;
    } else if (activity.type === 'suggestion_received') {
        detailsHTML = `
            <div class="feed-item-details">New suggestion: ${details.text || 'No text'}</div>
        `;
    } else if (activity.type === 'thinking') {
        detailsHTML = `
            <div class="feed-item-details thinking-indicator">Peter is thinking...</div>
        `;
    } else if (activity.type === 'thought') {
        const content = details.content || '';
        const truncated = content.length > 200 ? content.substring(0, 200) + '...' : content;
        detailsHTML = `
            <div class="feed-item-details thought-bubble">${truncated}</div>
            ${content.length > 200 ? '<button class="expand-btn" onclick="expandThought(this)">Show more</button>' : ''}
        `;
    } else if (activity.type === 'get_feed') {
        detailsHTML = `
            <div class="feed-item-details">Fetched ${details.count || 0} posts (${details.sort || 'hot'})</div>
        `;
    } else if (activity.type === 'read_post') {
        detailsHTML = `
            <div class="feed-item-title">${details.title || 'Unknown post'}</div>
            <div class="feed-item-details">Reading post...</div>
        `;
    } else if (activity.type === 'user_response') {
        detailsHTML = `
            <div class="feed-item-details user-message">💬 Peter says: "${details.message || 'No message'}"</div>
        `;
    } else if (activity.type === 'rate_limit') {
        detailsHTML = `
            <div class="feed-item-details rate-limit-message">⏱️ ${details.message || 'Rate limit reached'}</div>
            ${details.comments_remaining !== undefined ? `<div class="feed-item-details">Comments remaining today: ${details.comments_remaining}</div>` : ''}
        `;
    } else if (activity.type === 'error') {
        detailsHTML = `
            <div class="feed-item-details">Error: ${details.error || 'Unknown error'}</div>
        `;
    } else {
        detailsHTML = `
            <div class="feed-item-details">${JSON.stringify(details)}</div>
        `;
    }
    
    item.innerHTML = `
        <div class="feed-item-icon">${icon}</div>
        <div class="feed-item-content">
            <div class="feed-item-header">
                <span class="feed-item-type">${activity.type.replace(/_/g, ' ')}</span>
                <span class="feed-item-time" data-timestamp="${activity.timestamp}">${formatTimestamp(activity.timestamp)}</span>
            </div>
            ${detailsHTML}
        </div>
    `;
    
    return item;
}

function addActivityToFeed(activity) {
    const feedContent = document.getElementById('feed-content');
    const item = createFeedItem(activity);
    
    feedContent.appendChild(item);
    
    setTimeout(() => {
        item.classList.remove('new');
    }, 300);
    
    feedContent.scrollTop = feedContent.scrollHeight;
    
    if (feedContent.children.length > 100) {
        feedContent.removeChild(feedContent.firstChild);
    }
}

function expandThought(button) {
    const thoughtBubble = button.parentNode.querySelector('.thought-bubble');
    const content = button.parentNode.querySelector('.thought-content');
    
    if (content) {
        content.style.display = 'block';
        thoughtBubble.style.display = 'none';
        button.style.display = 'none';
    } else {
        const details = button.parentNode.parentNode.querySelector('.feed-item-details');
        const text = details.querySelector('.thought-bubble').textContent;
        const fullText = details.querySelector('.full-text').textContent;
        
        details.innerHTML = `
            <div class="feed-item-details thought-bubble">${text}</div>
            <div class="thought-content" style="display: block;">${fullText}</div>
            <button class="collapse-btn" onclick="collapseThought(this)">Show less</button>
        `;
    }
}

function collapseThought(button) {
    const thoughtBubble = button.parentNode.parentNode.querySelector('.thought-bubble');
    const content = button.parentNode;
    
    thoughtBubble.style.display = 'block';
    content.style.display = 'none';
    button.style.display = 'none';
}

function connectSSE() {
    if (eventSource) {
        eventSource.close();
    }
    
    eventSource = new EventSource('/api/activity/stream');
    
    eventSource.onopen = () => {
        console.log('[SSE] Connected');
        updateStatusBadge('running', 'Connected');
    };
    
    eventSource.onmessage = (event) => {
        try {
            const activity = JSON.parse(event.data);
            
            if (activity.type === 'connected') {
                console.log('[SSE] Stream ready');
                loadRecentActivity();
            } else {
                addActivityToFeed(activity);
            }
        } catch (e) {
            console.error('[SSE] Failed to parse message:', e);
        }
    };
    
    eventSource.onerror = (error) => {
        console.error('[SSE] Error:', error);
        updateStatusBadge('error', 'Disconnected');
        
        eventSource.close();
        
        setTimeout(() => {
            console.log('[SSE] Reconnecting...');
            connectSSE();
        }, 5000);
    };
}

function loadRecentActivity() {
    fetch('/api/activity/recent')
        .then(res => res.json())
        .then(data => {
            if (data.success && data.activities.length > 0) {
                const feedContent = document.getElementById('feed-content');
                feedContent.innerHTML = '';
                
                data.activities.forEach(activity => {
                    addActivityToFeed(activity);
                });
            }
        })
        .catch(err => {
            console.error('[API] Failed to load recent activity:', err);
        });
}

function updateStatus() {
    fetch('/api/status')
        .then(res => res.json())
        .then(data => {
            document.getElementById('uptime').textContent = `${data.uptime_hours}h`;
            document.getElementById('total-actions').textContent = data.total_actions;
            document.getElementById('success-rate').textContent = `${data.success_rate}%`;
            
            if (data.rate_limits) {
                const comments = data.rate_limits.comments;
                const commentsUsed = document.getElementById('comments-used');
                const nextComment = document.getElementById('next-comment');
                
                commentsUsed.textContent = `${comments.used}/${comments.limit}`;
                if (comments.remaining === 0) {
                    commentsUsed.classList.add('limit-reached');
                } else if (comments.remaining < 10) {
                    commentsUsed.classList.add('limit-warning');
                } else {
                    commentsUsed.classList.remove('limit-reached', 'limit-warning');
                }
                
                nextComment.textContent = comments.next_available;
            }
            
            if (data.running) {
                updateStatusBadge('running', 'Running');
            } else {
                updateStatusBadge('idle', 'Idle');
            }
        })
        .catch(err => {
            console.error('[API] Failed to fetch status:', err);
            updateStatusBadge('error', 'Error');
        });
}

function updateStatusBadge(state, text) {
    const badge = document.getElementById('status-badge');
    const statusText = badge.querySelector('.status-text');
    
    badge.className = 'status-badge ' + state;
    statusText.textContent = text;
}

function sendSuggestion(text) {
    const statusElem = document.getElementById('suggestion-status');
    const sendBtn = document.getElementById('send-btn');
    const input = document.getElementById('suggestion-input');
    
    sendBtn.disabled = true;
    input.disabled = true;
    statusElem.textContent = 'Sending...';
    statusElem.className = 'suggestion-status';
    
    fetch('/api/suggestions', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ text })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            statusElem.textContent = 'Suggestion sent to Peter!';
            statusElem.className = 'suggestion-status success';
            input.value = '';
        } else {
            statusElem.textContent = 'Failed to send suggestion';
            statusElem.className = 'suggestion-status error';
        }
        
        setTimeout(() => {
            statusElem.textContent = '';
        }, 3000);
    })
    .catch(err => {
        console.error('[API] Failed to send suggestion:', err);
        statusElem.textContent = 'Network error';
        statusElem.className = 'suggestion-status error';
        
        setTimeout(() => {
            statusElem.textContent = '';
        }, 3000);
    })
    .finally(() => {
        sendBtn.disabled = false;
        input.disabled = false;
        input.focus();
    });
}

document.addEventListener('DOMContentLoaded', () => {
    connectSSE();
    
    statusInterval = setInterval(updateStatus, 5000);
    updateStatus();
    
    setInterval(updateTimestamps, 30000);
    
    document.getElementById('suggestion-form').addEventListener('submit', (e) => {
        e.preventDefault();
        
        const input = document.getElementById('suggestion-input');
        const text = input.value.trim();
        
        if (text) {
            sendSuggestion(text);
        }
    });
    
    document.getElementById('clear-feed').addEventListener('click', () => {
        const feedContent = document.getElementById('feed-content');
        feedContent.innerHTML = '<div class="feed-item system"><div class="feed-item-icon">ℹ️</div><div class="feed-item-content"><div class="feed-item-header"><span class="feed-item-type">System</span><span class="feed-item-time" data-timestamp="0">Just now</span></div><div class="feed-item-details">Feed cleared</div></div></div>';
    });
});

window.addEventListener('beforeunload', () => {
    if (eventSource) {
        eventSource.close();
    }
    if (statusInterval) {
        clearInterval(statusInterval);
    }
});
