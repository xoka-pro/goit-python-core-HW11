from collections import UserDict
import datetime
import re


class AddressBook(UserDict):
    """Клас AddressBook - зберігає, додає записи та віддає записи книги контактів через ітератор"""

    def add_record(self, record):
        self.data[record.name.value] = record

    def iterator(self, count: int):
        for key, value in self:
            i = 1
            container = {}
            while i <= count:
                container[key] = value
                i += 1
            yield container

    def __iter__(self):
        for key, value in self.data.items():
            yield key, value


class Field:
    """Батьківський клас для всіх записів у книзі контактів"""
    def __init__(self, value=None):
        self._value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value


class Name(Field):
    """Обов'язкове поле з ім'ям в книзі контактів"""

    def __init__(self, value):
        super().__init__(value)
        self.value = value


class Phone(Field):
    """Необов'язкове поле з номером телефону(або кількома)"""

    def __init__(self, phone):
        super().__init__()
        self.value = Phone.check_phone(phone)

    @classmethod
    def check_phone(cls, phone):
        """Метод для валідації синтаксису номера телефона"""
        regex = r"\([0-9]{3}\)[0-9]{3}-[0-9]{2}-[0-9]{2}"
        if len(re.findall(regex, phone)) == 0:
            raise ValueError('Incorrect phone format, should be (XXX)AAA-BB-CC')
        return phone

    @Field.value.setter
    def value(self, value):
        super(Phone, self.__class__).value.fset(self, Phone.check_phone(value))


class Birthday(Field):
    """Необов'язкове поле з датою народження"""

    @Field.value.setter
    def value(self, value):
        try:
            super(Birthday, self.__class__).value.fset(self, datetime.datetime.strptime(value, '%d-%m-%Y'))
        except ValueError:
            print('Incorrect date format, should be DD-MM-YYYY')


class Record(Field):
    """Відповідає за логіку додавання/видалення/редагування полів.
    А також реалізує метод розрахунку днів до наступного дня народження(якщо параметр задано для поля)"""

    def __init__(self, name, phone=None, birthday=None):
        super().__init__()
        self.name = Name(name)
        self.birthday = Birthday()

        if phone:
            self.phones = [Phone(phone)]
        else:
            self.phones = []

        if birthday:
            self.birthday.value = birthday

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def change_phone(self, old_phone, new_phone):
        for el in self.phones:
            if el.value == old_phone:
                el.value = new_phone

    def del_phone(self, phone):
        for el in self.phones:
            if el.value == phone:
                self.phones.remove(el)

    def days_to_birthday(self):
        today = datetime.date.today()
        birthday = self.birthday.value
        next_birthday = datetime.date(year=today.year, month=birthday.month, day=birthday.day)

        if next_birthday < today:
            next_birthday = datetime.date(year=today.year + 1, month=birthday.month, day=birthday.day)

        delta = next_birthday - today

        if delta.days == 0:
            return "birthday today!"
        else:
            return f'{delta.days} days to birthday'


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


@input_error
def phone_func(*args) -> str:
    """Повертає номер телефону для зазначеного контакту"""

    name = args[0]
    if name in contacts:
        for name, numbers in contacts.items():
            return f'Name: {name} | Numbers: {", ".join(phone.value for phone in numbers.phones)}'
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
