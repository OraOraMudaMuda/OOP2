tasks = []
def add_task(task):
    tasks.append({"task": task, "completed": False})
    print(f"Задача '{task}' добавлена!")