import json
import time
import logging
from flask import Flask, render_template, request, jsonify, Response
from threading import Thread
from activity_logger import ActivityLogger
from suggestions_manager import SuggestionsManager
from rate_limit_tracker import RateLimitTracker

logger = logging.getLogger(__name__)

app = Flask(__name__, 
            template_folder='../templates',
            static_folder='../static')

activity_logger = ActivityLogger()
suggestions_manager = SuggestionsManager()
rate_limiter = RateLimitTracker()

agent_status = {
    "running": False,
    "start_time": None,
    "total_actions": 0,
    "successful_actions": 0,
    "last_activity": None
}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/status')
def get_status():
    uptime_hours = 0
    if agent_status["start_time"]:
        uptime_hours = (time.time() - agent_status["start_time"]) / 3600
    
    success_rate = 0
    if agent_status["total_actions"] > 0:
        success_rate = (agent_status["successful_actions"] / agent_status["total_actions"]) * 100
    
    rate_limits = rate_limiter.get_status()
    
    return jsonify({
        "running": agent_status["running"],
        "uptime_hours": round(uptime_hours, 2),
        "total_actions": agent_status["total_actions"],
        "successful_actions": agent_status["successful_actions"],
        "success_rate": round(success_rate, 1),
        "last_activity": agent_status["last_activity"],
        "rate_limits": rate_limits
    })


@app.route('/api/suggestions', methods=['GET', 'POST'])
def handle_suggestions():
    if request.method == 'POST':
        data = request.get_json()
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({"success": False, "error": "Empty suggestion"}), 400
        
        suggestion = suggestions_manager.add_suggestion(text)
        
        activity_logger.log_activity("suggestion_received", {
            "text": text,
            "suggestion_id": suggestion["id"]
        })
        
        return jsonify({"success": True, "suggestion": suggestion})
    
    else:
        pending = suggestions_manager.get_pending()
        return jsonify({"success": True, "suggestions": pending})


@app.route('/api/activity/recent')
def get_recent_activity():
    activities = activity_logger.get_recent(limit=50)
    return jsonify({"success": True, "activities": activities})


@app.route('/api/activity/stream')
def stream_activity():
    def event_stream():
        sub_queue = activity_logger.subscribe()
        
        try:
            yield f"data: {json.dumps({'type': 'connected', 'message': 'Connected to activity stream'})}\n\n"
            
            while True:
                try:
                    activity = sub_queue.get(timeout=30)
                    yield f"data: {json.dumps(activity)}\n\n"
                except:
                    yield f": heartbeat\n\n"
        finally:
            activity_logger.unsubscribe(sub_queue)
    
    return Response(event_stream(), mimetype='text/event-stream')


def update_agent_status(running=None, start_time=None, total_actions=None, 
                       successful_actions=None, last_activity=None):
    if running is not None:
        agent_status["running"] = running
    if start_time is not None:
        agent_status["start_time"] = start_time
    if total_actions is not None:
        agent_status["total_actions"] = total_actions
    if successful_actions is not None:
        agent_status["successful_actions"] = successful_actions
    if last_activity is not None:
        agent_status["last_activity"] = last_activity


def run_dashboard(host='0.0.0.0', port=5000, debug=False):
    logger.info(f"[DASHBOARD] Starting on http://{host}:{port}")
    app.run(host=host, port=port, debug=debug, threaded=True, use_reloader=False)


def start_dashboard_thread(host='0.0.0.0', port=5000):
    dashboard_thread = Thread(target=run_dashboard, args=(host, port, False), daemon=True)
    dashboard_thread.start()
    logger.info(f"[DASHBOARD] Running in background thread")
    return dashboard_thread
