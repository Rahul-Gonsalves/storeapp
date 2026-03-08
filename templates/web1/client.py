# client.py
import requests

# The base URL of our running Flask API
BASE_URL = 'http://127.0.0.1:5000/api/v1'

def get_all_tasks():
    """Fetches all tasks from the API."""
    try:
        response = requests.get(f"{BASE_URL}/tasks")
        response.raise_for_status()
        return response.json().get('tasks', [])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching tasks: {e}")
        return None

def create_task(title, description=""):
    """Creates a new task."""
    payload = {'title': title, 'description': description}
    try:
        response = requests.post(f"{BASE_URL}/tasks", json=payload)
        response.raise_for_status()
        print("Task created successfully!")
        return response.json().get('task')
    except requests.exceptions.RequestException as e:
        print(f"Error creating task: {e}")
        return None

def update_task_status(task_id, done):
    """Updates a task's 'done' status."""
    payload = {'done': done}
    try:
        response = requests.put(f"{BASE_URL}/tasks/{task_id}", json=payload)
        response.raise_for_status()
        print(f"Task {task_id} updated successfully!")
        return response.json().get('task')
    except requests.exceptions.RequestException as e:
        print(f"Error updating task {task_id}: {e}")
        return None

def delete_task(task_id):
    """Deletes a task."""
    try:
        response = requests.delete(f"{BASE_URL}/tasks/{task_id}")
        response.raise_for_status() # Will raise error on 404
        print(f"Task {task_id} deleted successfully.")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error deleting task {task_id}: {e}")
        return False

# --- Main script execution ---
if __name__ == "__main__":
    print("--- To-Do List API Client ---")

    # 1. Get all tasks at the beginning
    print("\nFetching all tasks...")
    tasks = get_all_tasks()
    if tasks is not None:
        for task in tasks:
            print(f"  - ID: {task['id']}, Title: {task['title']}, Done: {task['done']}")

    # 2. Create a new task
    print("\nCreating a new task...")
    new_task = create_task("Write a Python client", "Use the requests library.")
    if new_task:
        print(f"  -> Created Task ID: {new_task['id']}")

    # 3. Update the new task to be 'done'
    if new_task:
        print(f"\nUpdating task {new_task['id']}...")
        update_task_status(new_task['id'], True)

    # 4. Get all tasks again to see the changes
    print("\nFetching all tasks again...")
    tasks = get_all_tasks()
    if tasks is not None:
        for task in tasks:
            print(f"  - ID: {task['id']}, Title: {task['title']}, Done: {task['done']}")

    # 5. Delete the task we created
    #if new_task:
    #    print(f"\nDeleting task {new_task['id']}...")
    #    delete_task(new_task['id'])

    # 6. Final check
    print("\nFetching all tasks one last time...")
    tasks = get_all_tasks()
    if tasks is not None:
        for task in tasks:
            print(f"  - ID: {task['id']}, Title: {task['title']}, Done: {task['done']}")