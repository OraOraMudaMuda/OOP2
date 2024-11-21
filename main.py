def delete_task(index):
    if 0 <= index < len(tasks):
        removed_task = tasks.pop(index)  
        print(f"Задача '{removed_task['task']}' удалена!")
    else:
        print("Ошибка: Неверный индекс задачи.")  
