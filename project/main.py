import sys
import shutil
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, \
    QMessageBox, QDialog, QFormLayout, QTableWidget, QTableWidgetItem, QComboBox, QFileDialog
import mysql.connector
import os

#Лаба №6
class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Вход")
        self.resize(300, 100)

        layout = QFormLayout()

        self.username_entry = QLineEdit()
        layout.addRow("Логин:", self.username_entry)

        self.password_entry = QLineEdit()
        self.password_entry.setEchoMode(QLineEdit.Password)
        layout.addRow("Пароль:", self.password_entry)

        self.login_button = QPushButton("Войти")
        self.login_button.clicked.connect(self.login)
        layout.addRow(self.login_button)

        self.setLayout(layout)

    def login(self):
        username = self.username_entry.text()
        password = self.password_entry.text()

        if username and password:
            if check_credentials(username, password):
                self.accept()
            else:
                QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль")
        else:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите логин и пароль")


def check_credentials(username, password):
    try:
        host = "127.0.0.1"
        port = 3305
        user = "root"
        database = "project"

        conn = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            database=database
        )
        cur = conn.cursor()

        cur.execute("SELECT * FROM Accounts WHERE username = %s AND password = %s", (username, password))
        account = cur.fetchone()

        cur.close()
        conn.close()

        if account:
            return True
        else:
            return False
    except mysql.connector.Error as e:
        print("Ошибка при проверке учетных данных:", e)
        return False


class Application:
    def __init__(self, sender_email, recipient_email, details, priority, comment='', attachment_path=''):
        self.sender_email = sender_email
        self.recipient_email = recipient_email
        self.details = details
        self.priority = priority
        self.status = "Pending"
        self.comment = comment
        self.attachment_path = attachment_path

    def update_status(self, new_status):
        self.status = new_status

    def __str__(self):
        return f"Sender Email: {self.sender_email}\nRecipient Email: {self.recipient_email}\nDetails: {self.details}\nPriority: {self.priority}\nStatus: {self.status}\nComment: {self.comment}\nAttachment Path: {self.attachment_path}"


class ApplicationSystem:
    def __init__(self, host, user, database, port):
        self.conn = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            database=database
        )
        self.cur = self.conn.cursor()

    def create_application(self, sender_email, recipient_email, details, priority, comment='', attachment_path=''):
        new_application = Application(sender_email, recipient_email, details, priority, comment, attachment_path)
        sql = "INSERT INTO Applications (sender_email, recipient_email, details, status, priority, comment, attachment_path) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        val = (new_application.sender_email, new_application.recipient_email, new_application.details,
               new_application.status, new_application.priority, new_application.comment, new_application.attachment_path)
        self.cur.execute(sql, val)
        self.conn.commit()

    def display_applications_for_email(self, email, sender_filter='', recipient_filter='', status_filter='',
                                       priority_filter=''):
        query = "SELECT * FROM Applications WHERE recipient_email = %s"
        params = [email]

        if sender_filter:
            query += " AND sender_email LIKE %s"
            params.append(f"%{sender_filter}%")
        if recipient_filter:
            query += " AND recipient_email LIKE %s"
            params.append(f"%{recipient_filter}%")
        if status_filter:
            query += " AND status LIKE %s"
            params.append(f"%{status_filter}%")
        if priority_filter:
            query += " AND priority LIKE %s"
            params.append(f"%{priority_filter}%")

        self.cur.execute(query, tuple(params))
        applications = self.cur.fetchall()
        return applications

    def display_applications_from_email(self, email, sender_filter='', recipient_filter='', status_filter='', priority_filter=''):
        query = "SELECT * FROM Applications WHERE sender_email = %s"
        params = [email]

        if sender_filter:
            query += " AND sender_email LIKE %s"
            params.append(f"%{sender_filter}%")
        if recipient_filter:
            query += " AND recipient_email LIKE %s"
            params.append(f"%{recipient_filter}%")
        if status_filter:
            query += " AND status LIKE %s"
            params.append(f"%{status_filter}%")
        if priority_filter:
            query += " AND priority LIKE %s"
            params.append(f"%{priority_filter}%")

        self.cur.execute(query, tuple(params))
        applications = self.cur.fetchall()
        return applications

    def update_application(self, application_id, recipient_email, status, comment, priority):
        sql = "UPDATE Applications SET recipient_email = %s, status = %s, comment = %s, priority = %s WHERE id = %s"
        val = (recipient_email, status, comment, priority, application_id)
        self.cur.execute(sql, val)
        self.conn.commit()

    def get_all_users_with_roles(self):
        self.cur.execute("""
            SELECT a.username, r.role
            FROM Accounts a
            LEFT JOIN Roles r ON a.role_id = r.id
        """)
        users = self.cur.fetchall()
        return [(user[0], user[1] or 'No role') for user in users]

    def get_attachment_path(self, application_id):
        self.cur.execute("SELECT attachment_path FROM Applications WHERE id = %s", (application_id,))
        result = self.cur.fetchone()
        return result[0] if result else None

    def add_attachment_to_application(self, application_id, new_attachment_path):
        self.cur.execute("SELECT attachment_path FROM Applications WHERE id = %s", (application_id,))
        result = self.cur.fetchone()
        if result:
            current_attachment_path = result[0]
            if current_attachment_path:
                new_attachment_path = f"{current_attachment_path};{new_attachment_path}"
            sql = "UPDATE Applications SET attachment_path = %s WHERE id = %s"
            val = (new_attachment_path, application_id)
            self.cur.execute(sql, val)
            self.conn.commit()

    def get_distinct_column_values(self, column):
        self.cur.execute(f"SELECT DISTINCT {column} FROM Applications")
        results = self.cur.fetchall()
        return [result[0] for result in results]


class ApplicationDetailDialog(QDialog):
    def __init__(self, application_id, application_data, app_system, username):
        super().__init__()
        self.application_id = application_data[0]
        self.application_data = application_data
        self.app_system = app_system
        self.setWindowTitle("Детали заявки")
        self.resize(400, 200)

        layout = QFormLayout()

        self.recipient_combo = QComboBox()
        self.recipient_combo.setEditable(True)
        self.populate_recipient_combo()

        self.sender_label = QLabel(application_data[1])
        layout.addRow("Отправитель:", self.sender_label)

        layout.addRow("Получатель:", self.recipient_combo)

        self.details_label = QLabel(application_data[3])
        layout.addRow("Детали:", self.details_label)

        self.status_entry = QLineEdit(application_data[4])
        layout.addRow("Статус:", self.status_entry)

        self.comment_entry = QLineEdit(application_data[6])
        layout.addRow("Комментарий:", self.comment_entry)

        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["Низкий", "Средний", "Высокий"])
        self.priority_combo.setCurrentText(application_data[8])
        layout.addRow("Приоритет:", self.priority_combo)

        self.attachment_label = QLabel(os.path.basename(application_data[7]) if application_data[7] else "Нет файла")
        layout.addRow("Файл:", self.attachment_label)

        button_layout = QHBoxLayout()
        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        self.download_button = QPushButton("Скачать файл")
        self.download_button.clicked.connect(self.download_file)
        button_layout.addWidget(self.download_button)

        self.add_attachment_button = QPushButton("Добавить файл")
        self.add_attachment_button.clicked.connect(self.add_attachment)
        button_layout.addWidget(self.add_attachment_button)

        self.update_button = QPushButton("Изменить")
        self.update_button.clicked.connect(self.update_application)
        button_layout.addWidget(self.update_button)

        layout.addRow(button_layout)
        self.setLayout(layout)

    def populate_recipient_combo(self):
        users_with_roles = self.app_system.get_all_users_with_roles()
        for username, role in users_with_roles:
            self.recipient_combo.addItem(f"{username} ({role})", userData=username)

    def update_application(self):
        recipient_email = self.recipient_combo.currentData()
        status = self.status_entry.text()
        comment = self.comment_entry.text()
        priority = self.priority_combo.currentText()

        self.app_system.update_application(self.application_data[0], recipient_email, status, comment, priority)
        QMessageBox.information(self, "Успех", "Заявка успешно обновлена!")
        self.accept()

    def download_file(self):
        attachment_path = self.app_system.get_attachment_path(self.application_id)
        if attachment_path:
            options = QFileDialog.Options()
            filename = os.path.basename(attachment_path)
            save_path, _ = QFileDialog.getSaveFileName(self, "Сохранить файл как", filename, "Все файлы (*)", options=options)
            if save_path:
                try:
                    shutil.copy(attachment_path, save_path)
                    QMessageBox.information(self, "Успех", "Файл успешно сохранен!")
                except Exception as e:
                    QMessageBox.warning(self, "Ошибка", f"Не удалось сохранить файл: {e}")
        else:
            QMessageBox.warning(self, "Ошибка", "Файл не найден")

    def add_attachment(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите файл", "", "Все файлы (*);;Текстовые файлы (*.txt)", options=options)
        if file_path:
            self.app_system.add_attachment_to_application(self.application_id, file_path)
            QMessageBox.information(self, "Успех", "Файл успешно добавлен!")
            self.attachment_label.setText(os.path.basename(file_path))
            self.download_button.setEnabled(True)

class ApplicationUI(QWidget):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.attachment_path = ''
        self.init_ui()

        self.display_applications()

    def init_ui(self):
        layout = QVBoxLayout()

        filter_layout = QHBoxLayout()

        # Фильтр по отправителю
        self.sender_filter = QComboBox()
        self.sender_filter.setEditable(True)
        self.populate_filter_options(self.sender_filter, "sender_email")
        self.sender_filter.setCurrentText('Фильтр по отправителю')
        self.sender_filter.setPlaceholderText("Фильтр по отправителю")
        filter_layout.addWidget(self.sender_filter)

        # Фильтр по получателю
        self.recipient_filter = QComboBox()
        self.recipient_filter.setEditable(True)
        self.populate_filter_options(self.recipient_filter, "recipient_email")
        self.recipient_filter.setCurrentText('Фильтр по получателю')
        self.recipient_filter.setPlaceholderText("Фильтр по получателю")
        filter_layout.addWidget(self.recipient_filter)
        self.recipient_filter.hide()

        # Фильтр по статусу
        self.status_filter = QComboBox()
        self.status_filter.setEditable(True)
        self.populate_filter_options(self.status_filter, "status")
        self.status_filter.setCurrentText('Фильтр по статусу')
        self.status_filter.setPlaceholderText("Фильтр по статусу")
        filter_layout.addWidget(self.status_filter)

        # Фильтр по приоритету
        self.priority_filter = QComboBox()
        self.priority_filter.setEditable(True)
        self.populate_filter_options(self.priority_filter, "priority")
        self.priority_filter.setCurrentText('Фильтр по приоритету')
        self.priority_filter.setPlaceholderText("Фильтр по приоритету")
        filter_layout.addWidget(self.priority_filter)

        # Кнопка для применения фильтров
        self.filter_button = QPushButton("Применить фильтры")
        self.filter_button.clicked.connect(self.display_applications)
        filter_layout.addWidget(self.filter_button)

        layout.addLayout(filter_layout)

        self.display_button = QPushButton("Показать входящие заявки")
        self.display_button.clicked.connect(self.display_applications)
        layout.addWidget(self.display_button)

        self.display_sent_button = QPushButton("Показать отправленные заявки")
        self.display_sent_button.clicked.connect(self.display_sent_applications)
        layout.addWidget(self.display_sent_button)

        self.applications_table = QTableWidget()
        self.applications_table.setColumnCount(7)
        self.applications_table.setHorizontalHeaderLabels(
            ["Номер заявки", "Отправитель", "Получатель", "Детали", "Статус", "Приоритет", "Комментарий", "Файл"])
        self.applications_table.cellDoubleClicked.connect(self.show_application_details)
        layout.addWidget(self.applications_table)

        application_layout = QHBoxLayout()

        recipient_label = QLabel("Логин получателя:")
        self.recipient_combo = QComboBox()
        self.recipient_combo.setEditable(True)
        self.populate_recipient_combo()
        application_layout.addWidget(recipient_label)
        application_layout.addWidget(self.recipient_combo)

        details_label = QLabel("Детали:")
        self.details_entry = QLineEdit()
        application_layout.addWidget(details_label)
        application_layout.addWidget(self.details_entry)

        priority_label = QLabel("Приоритет:")
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["Низкий", "Средний", "Высокий"])
        application_layout.addWidget(priority_label)
        application_layout.addWidget(self.priority_combo)

        self.attachment_button = QPushButton("Прикрепить файл")
        self.attachment_button.clicked.connect(self.attach_file)
        application_layout.addWidget(self.attachment_button)

        self.send_button = QPushButton("Отправить заявку")
        self.send_button.clicked.connect(self.send_application)
        application_layout.addWidget(self.send_button)

        layout.addLayout(application_layout)
        self.setLayout(layout)

    def populate_recipient_combo(self):
        users_with_roles = app_system.get_all_users_with_roles()
        for username, role in users_with_roles:
            self.recipient_combo.addItem(f"{username} ({role})", userData=username)

    def populate_filter_options(self, combo_box, column):
        options = app_system.get_distinct_column_values(column)
        for option in options:
            combo_box.addItem(option)

    def display_applications(self):
        self.sender_filter.show()
        self.recipient_filter.hide()
        login_email = self.username
        sender_filter = self.sender_filter.currentText()
        if sender_filter == 'Фильтр по отправителю':
            sender_filter = ''
        recipient_filter = self.recipient_filter.currentText()
        if recipient_filter == 'Фильтр по получателю':
            recipient_filter = ''
        status_filter = self.status_filter.currentText()
        if status_filter == 'Фильтр по статусу':
            status_filter = ''
        priority_filter = self.priority_filter.currentText()
        if priority_filter == 'Фильтр по приоритету':
            priority_filter = ''

        applications = app_system.display_applications_for_email(
            login_email, sender_filter, recipient_filter, status_filter, priority_filter)
        self.applications_table.setRowCount(len(applications))
        self.applications_table.setHorizontalHeaderLabels(
            ["Номер заявки", "Отправитель", "Детали", "Статус", "Приоритет", "Комментарий", "Файл"])
        for i, application in enumerate(applications):
            self.applications_table.setItem(i, 0, QTableWidgetItem(str(application[0])))
            self.applications_table.setItem(i, 1, QTableWidgetItem(application[1]))
            self.applications_table.setItem(i, 2, QTableWidgetItem(application[3]))
            self.applications_table.setItem(i, 3, QTableWidgetItem(application[4]))
            self.applications_table.setItem(i, 4, QTableWidgetItem(application[8]))
            self.applications_table.setItem(i, 5, QTableWidgetItem(application[6]))
            self.applications_table.setItem(i, 6, QTableWidgetItem(os.path.basename(application[7]) if application[7] else "Нет файла"))

    def display_sent_applications(self):
        self.sender_filter.hide()
        self.recipient_filter.show()
        login_email = self.username
        sender_filter = self.sender_filter.currentText()
        if sender_filter == 'Фильтр по отправителю':
            sender_filter = ''
        recipient_filter = self.recipient_filter.currentText()
        if recipient_filter == 'Фильтр по получателю':
            recipient_filter = ''
        status_filter = self.status_filter.currentText()
        if status_filter == 'Фильтр по статусу':
            status_filter = ''
        priority_filter = self.priority_filter.currentText()
        if priority_filter == 'Фильтр по приоритету':
            priority_filter = ''

        applications = app_system.display_applications_from_email(
            login_email, sender_filter, recipient_filter, status_filter, priority_filter)
        self.applications_table.setRowCount(len(applications))
        self.applications_table.setHorizontalHeaderLabels(
            ["Номер заявки", "Получатель", "Детали", "Статус", "Приоритет", "Комментарий", "Файл"])
        for i, application in enumerate(applications):
            self.applications_table.setItem(i, 0, QTableWidgetItem(str(application[0])))
            self.applications_table.setItem(i, 1, QTableWidgetItem(application[2]))
            self.applications_table.setItem(i, 2, QTableWidgetItem(application[3]))
            self.applications_table.setItem(i, 3, QTableWidgetItem(application[4]))
            self.applications_table.setItem(i, 4, QTableWidgetItem(application[8]))
            self.applications_table.setItem(i, 5, QTableWidgetItem(application[6]))
            self.applications_table.setItem(i, 6, QTableWidgetItem(os.path.basename(application[7]) if application[7] else "Нет файла"))

    def show_application_details(self, row, column):
        if self.applications_table.rowCount() > row:
            application_id = int(self.applications_table.item(row, 0).text())
            print(f"Selected Application ID: {application_id}")  # Debug message
            applications = app_system.display_applications_for_email(self.username)
            application_data = applications[row]
            print(f"Application Data: {application_data}")  # Debug message
            dialog = ApplicationDetailDialog(application_id, application_data, app_system, self.username)
            dialog.exec_()

    def attach_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите файл", "", "Все файлы (*);;Текстовые файлы (*.txt)", options=options)
        if file_path:
            self.attachment_path = file_path

    def send_application(self):
        sender_email = self.username
        recipient_email = self.recipient_combo.currentData()
        details = self.details_entry.text()
        priority = self.priority_combo.currentText()

        if recipient_email and details:
            new_application = app_system.create_application(self.username, recipient_email, details, priority, '', self.attachment_path)
            QMessageBox.information(self, "Успех", "Заявка успешно отправлена!")
            self.display_applications()
        else:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните все поля")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    login_dialog = LoginDialog()
    if login_dialog.exec_() == QDialog.Accepted:
        username = login_dialog.username_entry.text()

        host = "127.0.0.1"
        port = 3305
        user = "root"
        database = "project"

        app_system = ApplicationSystem(host, user, database, port)
        ui = ApplicationUI(username)
        ui.show()
        sys.exit(app.exec_())
