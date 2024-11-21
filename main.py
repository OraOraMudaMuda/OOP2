def delete_task(index):
    if 0 <= index < len(tasks):
        removed_task = tasks.pop(index)  
        print(f"Задача '{removed_task['task']}' удалена!")
    else:
        print("Ошибка: Неверный индекс задачи.")  

def mark_completed(index):
    if 0 <= index < len(tasks):  
        tasks[index]["completed"] = True  
        print(f"Задача '{tasks[index]['task']}' выполнена!")
    else:
        print("Ошибка: Неверный индекс задачи.") 

def show_tasks():
    if not tasks:  
        print("Список задач пуст.")
    else:
        print("Список задач:")
        for i, task in enumerate(tasks): 
            status = "✔" if task["completed"] else "✘"  
            print(f"{i}: {task['task']} [{status}]")
