import http.server
import socketserver
import json
from urllib.parse import parse_qs, urlparse

# Store tasks in a JSON file
TASK_FILE = "tasks.json"

# Initialize tasks
def init_tasks():
    try:
        with open(TASK_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        with open(TASK_FILE, "w") as file:
            json.dump([], file)
        return []

tasks = init_tasks()

# Save tasks to file
def save_tasks():
    with open(TASK_FILE, "w") as file:
        json.dump(tasks, file)

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Serve the list of tasks
        if self.path == "/tasks":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(tasks).encode())
        
        # Handle marking a task as complete
        elif self.path.startswith("/complete"):
            query_components = parse_qs(urlparse(self.path).query)
            task_id = int(query_components.get("id", [0])[0])
            for task in tasks:
                if task["id"] == task_id:
                    task["completed"] = True
                    break
            save_tasks()
            self.send_response(303)
            self.send_header("Location", "/")
            self.end_headers()
        
        # Handle deleting a task
        elif self.path.startswith("/delete"):
            query_components = parse_qs(urlparse(self.path).query)
            task_id = int(query_components.get("id", [0])[0])
            global tasks
            tasks = [task for task in tasks if task["id"] != task_id]
            save_tasks()
            self.send_response(303)
            self.send_header("Location", "/")
            self.end_headers()
        
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == "/add":
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)
            params = parse_qs(post_data.decode())
            task_content = params.get("task", [""])[0]
            if task_content:
                tasks.append({"id": len(tasks) + 1, "content": task_content, "completed": False})
                save_tasks()
            self.send_response(303)
            self.send_header("Location", "/")
            self.end_headers()

# Run the server
if __name__ == "__main__":
    PORT = 8000
    handler = MyHandler
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"Serving at http://localhost:{PORT}")
        httpd.serve_forever()
