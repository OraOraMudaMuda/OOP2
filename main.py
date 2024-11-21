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
