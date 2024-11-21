tasks = []
def add_task(task):
    tasks.append({"task": task, "completed": False})
    print(f"Задача '{task}' добавлена!")
if __name__ == "__main__":
    while True:
        print("\nМеню:")
        print("1. Добавить задачу")
        print("2. Удалить задачу")
        print("3. Отметить задачу выполненной")
        print("4. Показать задачи")
        print("5. Выход")

        choice = input("Выберите действие: ")

        if choice == "1":
            task = input("Введите задачу: ")
            add_task(task)
        elif choice == "2":
            try:
                index = int(input("Введите номер задачи для удаления: "))
                delete_task(index)
            except ValueError:
                print("Ошибка: Введите корректный номер задачи.")
        elif choice == "3":  # Отметка задачи выполненной.
            try:
                index = int(input("Введите номер задачи для выполнения: "))
                mark_completed(index)
            except ValueError:  # Обрабатываем неверный ввод (не число).
                print("Ошибка: Введите корректный номер задачи.")
        elif choice == "4":  # Показать список задач.
            show_tasks()
        elif choice == "5":  # Выход из программы.
            print("Выход из программы. До свидания!")
            break
        else:  # Неверный выбор.
            print("Ошибка: Неверный выбор.")
