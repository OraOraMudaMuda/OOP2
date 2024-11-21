class Task:
    def __init__(self, task_id, name):
        self.id = task_id
        self.name = name
        self.completed = False

    def mark_completed(self):
        self.completed = True


class TaskManager:
    def __init__(self):
        self.tasks = []

    def add_task(self, task):
        self.tasks.append(task)

    def delete_task(self, task_id):
        self.tasks = [task for task in self.tasks if task.id != task_id]

    def get_tasks(self):
        return self.tasks


class UserInterface:
    def __init__(self, task_manager):
        self.task_manager = task_manager

    def show_menu(self):
        print("\nМеню:")
        print("1. Добавить задачу")
        print("2. Удалить задачу")
        print("3. Показать задачи")
        print("4. Отметить задачу выполненной")
        print("5. Выход")

    def get_user_input(self):
        while True:
            self.show_menu()
            choice = input("Выберите действие: ")

            if choice == "1":
                name = input("Введите название задачи: ")
                task = Task(len(self.task_manager.get_tasks()) + 1, name)
                self.task_manager.add_task(task)
                print("Задача добавлена!")

            elif choice == "2":
                task_id = int(input("Введите ID задачи для удаления: "))
                self.task_manager.delete_task(task_id)
                print("Задача удалена!")

            elif choice == "3":
                self.display_tasks(self.task_manager.get_tasks())

            elif choice == "4":
                task_id = int(input("Введите ID задачи для выполнения: "))
                for task in self.task_manager.get_tasks():
                    if task.id == task_id:
                        task.mark_completed()
                        print("Задача отмечена выполненной!")
                        break

            elif choice == "5":
                print("Выход из программы.")
                break

            else:
                print("Ошибка: Неверный выбор!")

    def display_tasks(self, tasks):
        if not tasks:
            print("Список задач пуст.")
        else:
            print("Список задач:")
            for task in tasks:
                status = "✔" if task.completed else "✘"
                print(f"ID: {task.id}, Название: {task.name}, Статус: {status}")


if __name__ == "__main__":
    task_manager = TaskManager()
    ui = UserInterface(task_manager)
    ui.get_user_input()
