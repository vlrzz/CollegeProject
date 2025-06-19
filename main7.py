import random
import os
import hashlib
from datetime import datetime
import pytz

# Часовые пояса
moscow_tz = pytz.timezone('Europe/Moscow')

# Путь к файлам
products_name = os.path.join('products.txt')
DATABASE_FILE = os.path.join('source', 'databases', 'database01.txt')

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_date(timezone):
    current_date = datetime.now(timezone)
    formatted_date = current_date.strftime('%Y-%m-%d_%H-%M-%S')
    return formatted_date

def hash_password(password, salt):
    return hashlib.sha256((salt + password).encode()).hexdigest()

def load_users():
    users = {}
    if os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, 'r', encoding='UTF-8') as file:
            for line in file:
                parts = line.strip().split(':')
                if len(parts) == 4:
                    login, salt, hashed_password, hashed_second_password = parts
                    users[login] = (salt, hashed_password, hashed_second_password)
                else:
                    print(f"Некорректная запись в файле: {line.strip()}")
    return users

def login_user(users):
    while True:
        clear_console()
        print('\n-----Авторизация-----')
        login = input("Логин: ").strip()
        
        if not login:
            print("Логин не может быть пустым!")
            input('\n[!] Нажмите ENTER для продолжения')
            continue
        if ' ' in login:
            print("Логин не должен содержать пробелов!")
            input('\n[!] Нажмите ENTER для продолжения')
            continue
            
        if login in users:
            password = input("Пароль: ").strip()
            second_password = input("Второй пароль: ").strip()
            
            if not password or not second_password:
                print("Пароли не могут быть пустыми!")
                input('\n[!] Нажмите ENTER для продолжения')
                continue
            if ' ' in password or ' ' in second_password:
                print("Пароли не должны содержать пробелов!")
                input('\n[!] Нажмите ENTER для продолжения')
                continue
                
            salt, hashed_password, hashed_second_password = users[login]
            hashed_input_password = hash_password(password, salt)
            hashed_input_second_password = hash_password(second_password, salt)
            if hashed_input_password == hashed_password and hashed_input_second_password == hashed_second_password:
                print("Авторизация успешна!")
                input('\n[!] Нажмите ENTER для продолжения')
                clear_console()
                return True, login
            else:
                input("Один из паролей неверный. Попробуйте снова.\n[!] Нажмите ENTER для продолжения")
                clear_console()
        else:
            print("Пользователь не найден.")
            action = input("Хотите зарегистрироваться? (Y/n)\n>> ")
            if action.lower() == 'y':
                success, new_login = register_user(users)
                if success:
                    return True, new_login
                break
            else:
                print("Возврат в главное меню.")
                clear_console()
                continue
    return False, None

def register_user(users):
    while True:
        print('\n-----Регистрация-----')
        login = input("Логин: ").strip()
        
        if not login:
            print("Логин не может быть пустым!")
            continue
        if ' ' in login:
            print("Логин не должен содержать пробелов!")
            continue
        if login in users:
            print("Этот логин уже занят. Попробуйте другой.")
            continue
            
        password = input("Пароль: ").strip()
        second_password = input("Второй пароль: ").strip()
        
        if not password or not second_password:
            print("Пароли не могут быть пустыми!")
            continue
        if ' ' in password or ' ' in second_password:
            print("Пароли не должны содержать пробелов!")
            continue
            
        salt = os.urandom(16).hex()
        hashed_password = hash_password(password, salt)
        hashed_second_password = hash_password(second_password, salt)
        
        # Запись
        with open(DATABASE_FILE, 'a', encoding='UTF-8') as file:
            file.write(f"{login}:{salt}:{hashed_password}:{hashed_second_password}\n")
        
        users[login] = (salt, hashed_password, hashed_second_password)
        
        print("Регистрация успешна! Выполняется автоматический вход...")
        input('\n[!] Нажмите ENTER для продолжения')
        clear_console()
        return True, login

def print_products(products_file):
    try:
        if not os.path.exists(products_file):
            print("Файл с товарами не найден. Пожалуйста, проверьте его наличие.")
            return
        with open(products_file, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        if not lines:
            print("Список товаров пуст.")
            return
        formatted_output = []
        for index, line in enumerate(lines, start=1):
            parts = line.strip().split(':')
            if len(parts) == 3:
                item_name, item_price, item_count = parts
                item_name = item_name.strip().strip('"')
                try:
                    item_price = float(item_price.strip())
                    item_count = int(item_count.strip())
                except ValueError:
                    print(f"Ошибка: некорректная цена для товара '{item_name}'. Пропускаем...")
                    continue
                formatted_output.append(f"{index}) {item_name}: {item_price}₽ x{item_count}")
        result = " | ".join(formatted_output) + " |"
        print(result)
    except Exception as e:
        print(f"Произошла ошибка при выводе товаров: {e}")

def print_receipt(cart):
    if not cart:
        print("Корзина пуста. Невозможно распечатать чек.")
        input('\n[!] Нажмите ENTER для продолжения')
        clear_console()
        return None
    total = sum(details['price'] * details['quantity'] for details in cart.values())
    receipt_date = get_date(moscow_tz)
    print(f"\nЧек ({receipt_date}):")
    for item, details in cart.items():
        print(
            f"• {item}: {details['price']:.2f}₽ x {details['quantity']}шт. = {details['price'] * details['quantity']:.2f}₽")
    print(f"Итого: {total:.2f}₽")
    return total

def save_receipt(cart, total, username):
    if not cart:
        print("Корзина пуста. Чек не может быть сохранён.")
        input('\n[!] Нажмите ENTER для продолжения')
        clear_console()
        return
    receipt_id = random.randint(100000, 999999)
    receipt_date = get_date(moscow_tz)
    file_name = f"Чек_{username}_{receipt_date}_({receipt_id}).txt"
    with open(file_name, 'w', encoding='UTF-8') as file:
        file.write(f"Маркетплейс Mountain\n КАССОВЫЙ ЧЕК:\n")
        file.write(f'Наименование   |   Кол-во   |  Цена   |   Стоимость\n')
        for item, details in cart.items():
            price_per_unit = details['price']
            quantity = details['quantity']
            total_price_for_item = price_per_unit * quantity
            file.write(f"{item}---{quantity:.3f}шт   {price_per_unit:.2f}   {total_price_for_item:.2f}\n")
        file.write(f"ИТОГ:----------------------{total:.2f}\nСУММА НДС 20%\n{receipt_date}\n")
        file.write('\nООО "МАУНТЬИН" 644042, г.Омск, Набережная.Иртышская, д. 10, к.1\nКонтактный номер: +7 914 710 88 99\nПочта: mountainwee@gmail.com')
    print(f"\nЧек сохранён в файл: {file_name}")

def load_products(file_name):
    products = {}
    try:
        if not os.path.exists(file_name):
            print("Файл товаров не найден.")
            return products
        with open(file_name, 'r', encoding='UTF-8') as file:
            for index, line in enumerate(file, start=1):
                line = line.strip()
                if not line:
                    continue
                parts = line.split(':')
                if len(parts) == 3:
                    name, price, count = parts
                    name = name.strip().strip('"')
                    try:
                        price = float(price.strip())
                        count = int(count.strip())
                    except ValueError:
                        print(f"Ошибка: некорректная цена для товара '{name}' в строке {index}. Пропускаем...")
                        continue
                    products[index] = {'name': name, 'price': price, 'count': count}
                else:
                    print(f"Ошибка: некорректный формат строки '{line}' в строке {index}. Пропускаем...")
    except Exception as e:
        print(f"Произошла ошибка при загрузке товаров: {e}")
    return products

def save_products(file_name, products):
    try:
        with open(file_name, 'w', encoding='UTF-8') as file:
            for index, product in products.items():
                file.write(f'"{product["name"]}":{product["price"]}:{product["count"]}\n')
        print("Информация о товарах обновлена.")
    except Exception as e:
        print(f"Ошибка при сохранении товаров: {e}")

def add_to_cart(cart, products):
    try:
        selected_index = int(input("\n(Для отмены нажмите ENTER)\nВведите индекс товара для добавления в корзину: "))
        if selected_index in products:
            product = products[selected_index]
            quantity = int(input("Введите количество: "))
            if quantity <= 0:
                print("Количество должно быть больше 0.")
                return
            if quantity > product['count']:
                print(f'Слишком большое количество товара! Доступно: {product["count"]} шт.')
                return
            if product['name'] in cart:
                cart[product['name']]['quantity'] += quantity
            else:
                cart[product['name']] = {'price': product['price'], 'quantity': quantity}

            products[selected_index]['count'] -= quantity
            print(f"{quantity} шт. '{product['name']}' добавлено в корзину.")
        else:
            print("Неверный индекс товара!")
    except ValueError:
        print("\nОперация была отменена.\nПожалуйста, введите корректный индекс или количество.")

def remove_from_cart(cart, products):
    if not cart:
        print("Корзина пуста. Нечего удалять.")
        return
    print("\nТовары в корзине:")
    for index, (name, details) in enumerate(cart.items(), start=1):
        print(
            f"{index}) {name}: {details['price']:.2f}₽ x {details['quantity']}шт. = {details['price'] * details['quantity']:.2f}₽")
    try:
        selected_index = int(input("\nВведите номер товара для удаления: "))
        if 1 <= selected_index <= len(cart):
            item_to_remove = list(cart.keys())[selected_index - 1]
            removed_item = cart.pop(item_to_remove)
            for idx, prod in products.items():
                if prod['name'] == item_to_remove:
                    products[idx]['count'] += removed_item['quantity']
                    break
            print(
                f"Товар '{item_to_remove}' удален из корзины. Сумма: {removed_item['price'] * removed_item['quantity']:.2f}₽")
        else:
            print("Неверный номер товара!")
    except ValueError:
        print("Пожалуйста, введите корректный номер.")

def update_cart_item(cart, products):
    if not cart:
        print("Корзина пуста. Нечего изменять.")
        return
    
    print("\nТовары в корзине:")
    for index, (name, details) in enumerate(cart.items(), start=1):
        print(f"{index}) {name}: {details['price']:.2f}₽ x {details['quantity']}шт.")
    
    try:
        selected_index = int(input("\nВведите номер товара для изменения количества: "))
        if 1 <= selected_index <= len(cart):
            item_to_update = list(cart.keys())[selected_index - 1]
            current_quantity = cart[item_to_update]['quantity']
            
            original_product = None
            for prod in products.values():
                if prod['name'] == item_to_update:
                    original_product = prod
                    break
            
            if original_product:
                new_quantity = int(input(f"Текущее количество: {current_quantity}. Введите новое количество: "))
                
                if new_quantity <= 0:
                    print("Количество должно быть больше 0.")
                    return
                
                difference = new_quantity - current_quantity
                
                if difference > 0:
                    if difference > original_product['count']:
                        print(f"Недостаточно товара на складе! Доступно: {original_product['count']} шт.")
                        return
                    original_product['count'] -= difference
                else:
                    original_product['count'] += abs(difference)
                
                cart[item_to_update]['quantity'] = new_quantity
                print(f"Количество товара '{item_to_update}' изменено на {new_quantity} шт.")
            else:
                print("Ошибка: товар не найден в основном списке.")
        else:
            print("Неверный номер товара!")
    except ValueError:
        print("Пожалуйста, введите корректное число.")

def main():
    cart = {}
    clear_console()
    if not os.path.exists(products_name):
        print("Файл с товарами не найден. Программа завершает работу.")
        return
    users = load_users()
    products = load_products(products_name)

    if not products:
        print("Список товаров пуст. Программа завершает работу.")
        return

    logged_in = False
    current_user = None
    
    while not logged_in:
        action = input("Добро пожаловать!\n{1}--Войти\n{2}--Зарегистрироваться\n>> ")
        if action == '1':
            logged_in, current_user = login_user(users)
        elif action == '2':
            logged_in, current_user = register_user(users)
        else:
            print("Пожалуйста, выберите 1 или 2.")

    while logged_in:
        print(f"\nДобро пожаловать, {current_user}!")
        print("\nДоступные товары:")
        temp_products = {idx: {'name': p['name'], 'price': p['price'], 'count': p['count']} for idx, p in
                         products.items()}
        formatted_output = []
        for index, product in temp_products.items():
            formatted_output.append(f"{index}) {product['name']}: {product['price']}₽ x{product['count']}")
        result = " | ".join(formatted_output)
        print(result + " |")
        if not cart:
            print('\nВаша корзина пустая :(')
            print('Желаете что-нибудь приобрести?')
        else:
            print("\n----Корзина----")
            total = sum(details['price'] * details['quantity'] for details in cart.values())
            for index, (name, details) in enumerate(cart.items(), start=1):
                print(
                    f"{index}) {name}: {details['price']:.2f}₽ x {details['quantity']}шт. = {details['price'] * details['quantity']:.2f}₽")
            print(f"Итого: {total:.2f}₽")

        print("\nДействия с корзиной:")
        print("[1] Добавить товар в корзину")
        print("[2] Убрать товар из корзины")
        print("[3] Изменить количество товара")
        print("[4] Посмотреть корзину")
        print("[5] Распечатать чек")
        print("[6] Выход")
        choice = input(">> ")

        if choice == '1':
            add_to_cart(cart, products)
        elif choice == '2':
            remove_from_cart(cart, products)
        elif choice == '3':
            update_cart_item(cart, products)
        elif choice == '4':
            if not cart:
                print('\nВаша корзина пустая :(')
                print('Желаете что-нибудь приобрести?')
            else:
                print("\n----Корзина----")
                total = sum(details['price'] * details['quantity'] for details in cart.values())
                for index, (name, details) in enumerate(cart.items(), start=1):
                    print(
                        f"{index}) {name}: {details['price']:.2f}₽ x {details['quantity']}шт. = {details['price'] * details['quantity']:.2f}₽")
                print(f"Итого: {total:.2f}₽")
        elif choice == '5':
            total_price = print_receipt(cart)
            if total_price is not None:
                confirm = input("Хотите сохранить чек? (Y/n): ").strip().lower()
                if confirm == 'y':
                    save_receipt(cart, total_price, current_user)
                    save_products(products_name, products)
                    cart.clear()
                    print('(Корзина была очищена.)')
                    print('Товары успешно обновлены.')
                elif confirm == 'n':
                    print("Покупка отменена. Количество товаров восстановлено.")
        elif choice == '6':
            exitAns = input('Вы точно хотите выйти из программы? (Y/n)\n>> ').lower()
            if exitAns in ['y', 'да', 'yes']:
                print("\nВыход из программы.")
                break
            else:
                print('\nОперация выхода отменена!')

        input('\n[!] Нажмите ENTER для продолжения')
        clear_console()

if __name__ == "__main__":
    main()