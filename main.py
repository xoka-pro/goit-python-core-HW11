from classes import AddressBook
from classes import Record

contacts = AddressBook()


def input_error(func):
    """ Errors handler """
    def wrapper(*args):
        try:
            return func(*args)
        except KeyError as error:
            return f'No name in contacts. Error: {error}'
        except IndexError as error:
            return f'Sorry, not enough params for command. Error: {error}'
        except ValueError as error:
            return f'Value error: {error}'
        except TypeError as error:
            return f'Not enough arguments. Error: {error}'
    return wrapper


def hello() -> str:
    """Функція для вітання користувача"""
    return (f'How can I help you?\n'
            f'Type "h" or "help" to show help')


def goodbye():
    """Функція завершення програми"""
    print(f'Good bye!')
    quit()


@input_error
def add(name, number, birthday=None) -> str:
    """Функція для додавання нового запису або додавання нового телефону контакту"""

    if name not in contacts:
        new_number = Record(name, number, birthday)
        contacts.add_record(new_number)
        return f'Contact add successfully'
    else:
        contacts[name].add_phone(number)
        return f'New number added to {name}'


@input_error
def change(*args) -> str:
    """Функція для заміни номеру телефона контакту"""

    name, old_number, new_number, *_ = args
    if name in contacts:
        contacts[name].change_phone(old_number, new_number)
    else:
        return f'No contact "{name}"'
    return f'Contact change successfully'


@input_error
def del_phone(name, phone) -> str:
    """Функція видалення номера телефона у контакту"""

    if name in contacts:
        contacts[name].del_phone(phone)
    else:
        return f'No contact "{name}"'
    return f'Phone number deleted successfully'


# @input_error
def phone_func(*args) -> str:
    """Повертає номер телефону для зазначеного контакту"""

    name = args[0]

    for el in contacts.iterator(5):
        for key, data in el.items():
            if key == name:
                return f'Name: {key} | Numbers: {", ".join(phone.value for phone in data.phones)}'
            else:
                return f'No contact "{name}"'


@input_error
def show_all() -> str:
    """Повертає всю книгу контактів"""

    result = []
    for el in contacts.iterator(5):
        for name, data in el.items():
            numbers = ", ".join(phone.value for phone in data.phones)
            if data.birthday.value:
                bday = data.birthday.value.date().strftime('%d-%m-%Y')
                to_birthday = contacts[name].days_to_birthday()
                result.append(f'Name: {name} | Numbers: {numbers} | Birthday: {bday} - {to_birthday}')
            else:
                result.append(f'Name: {name} | Numbers: {numbers}')
    if len(result) < 1:
        return f'Contact list is empty'
    return '\n'.join(result)


def hlp(*args) -> str:
    """Повертає коротку допомогу по командах"""
    return (f'Known commands:\n'
            f'hello, help -- this help\n'
            f'add -- add new contact or new number for contact\n'
            f'change -- change specified number for contact\n'
            f'phone --  show phone numbers for specified contact\n'
            f'show all -- show all contacts\n'
            f'delete -- delete specified number from contact\n'
            f'good bye, close, exit -- shutdown application')


def parser(msg: str):
    """ Parser and handler AIO """
    command = None
    params = []

    operations = {
        'hello': hello,
        'h': hlp,
        'help': hlp,
        'add': add,
        'change': change,
        'phone': phone_func,
        'show all': show_all,
        'good bye': goodbye,
        'close': goodbye,
        'exit': goodbye,
        'delete': del_phone,
    }

    for key in operations:
        if msg.lower().startswith(key):
            command = operations[key]
            msg = msg.lstrip(key)
            for item in filter(lambda x: x != '', msg.split(' ')):
                params.append(item)
            return command, params
    return command, params


def main():
    """ Main function - all interaction with user """
    print(hello())
    while True:
        msg = input("Input command: ")
        command, params = parser(msg)
        if command:
            print(command(*params))
        else:
            print(f'Sorry, unknown command, try again. Type "h" for help.')


if __name__ == '__main__':
    main()
