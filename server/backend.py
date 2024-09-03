import json

def get_raw():
    print("Getting raw data")
    with open('stats.json', 'r') as file:
        stats = json.load(file)
    with open('users.json', 'r') as file:
        users = json.load(file)
    return stats, users

def save_stats(data):
    """Save stats to JSON file."""
    with open('stats.json', 'w') as file:
        json.dump(data, file, indent=4)

def add_user(user_id):
    e, data = get_raw()

    if user_id in data:
        return 400

    # Initialize new user with empty clockins and total time
    data[user_id] = {'clockins': [], 'total_time': 0}
    save_stats(data)

    return jsonify({"message": f"User '{user_id}' added successfully"})

def new_user(id):
    with open('stats.json', 'w', encoding='utf-8') as statsjson:
        entry = {'name': args.name, 'url': args.url}

def get_leaderboard():
    print("Functionality not yet available")

def clockin(id):
    e, users = get_raw()

    if not any(user['id'] == id for user in users):
        