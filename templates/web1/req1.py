import requests

try:
    # Make a GET request to an endpoint
    # response = requests.get('http://127.0.0.1:5000/api/v1/tasks')

    # response = requests.delete('http://127.0.0.1:5000/api/v1/tasks/1')

    # requests.post()

    # requests.put()

    response = requests.get('http://127.0.0.1:5000/api/v1/tasks')
    # response = requests.get('http://127.0.0.1:5000/about')

    # Raise an exception if the request returned an unsuccessful status code (4xx or 5xx)
    response.raise_for_status()

    # --- Inspecting the Response ---
    print(f"Status Code: {response.status_code}") # Should be 200

    # The response body can be accessed in different ways
    # .text gives you the raw text
    print(f"Response Text: {response.text}")

    # .json() automatically decodes a JSON response into a Python dictionary
    data = response.json()
    print("Response JSON:")
    print(data)

    tasklist = data['tasks']
    print(f"Numbers of tasks: {len(tasklist)}" )

except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")