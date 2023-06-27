import json
import random

import pyodbc
import names
from pyodbc import IntegrityError
from tqdm import tqdm


# funkcja importująca dane z pliku json do bazy lokalnej do tabeli Users
# import lokalny byl 10 krotnie szybszy niz import do bazy zdalnej
def import_data() -> None:
    data = []
    with open('database/reviews.json') as fh:
        data = json.load(fh)

    cnxn, cursor = create_local_db_connection()

    progress_bar = tqdm(total=len(data))

    counter = 0
    start_position = 0
    for line in data:
        if counter >= start_position:
            get_or_create_user(line, cursor)
        progress_bar.update(1)
        counter += 1
        if counter % 10000 == 0:
            cnxn.commit()
    cnxn.commit()

    cursor.close()
    cnxn.close()


# funkcja importująca produkty do bazy lokalnej
def import_products() -> None:
    data = []
    with open('database/products.json') as fh:
        data = json.load(fh)

    cnxn, cursor = create_local_db_connection()

    progress_bar = tqdm(total=len(data))

    counter = 0
    start_position = 0
    for line in data:
        if counter >= start_position:
            create_product(line, cursor)
        progress_bar.update(1)
        counter += 1
        if counter % 10000 == 0:
            cnxn.commit()
    cnxn.commit()

    cursor.close()
    cnxn.close()


# funkcja insertująca produkty do tabeli Products
def create_product(line: dict, cursor) -> None:
    external_ref = line['asin']
    name = line['title']

    try:
        count = cursor.execute(
            'insert into Products (external_ref, name) values (?, ?)',
            external_ref,
            name
        ).rowcount
        assert count == 1
    except IntegrityError:
        pass


# funkcja przenosząca dane z tabeli Users z bazy lokalnej do bazy zdalnej
def transfer_users() -> None:
    local_cnxn, local_cursor = create_local_db_connection()
    remote_cnxn, remote_cursor = create_remote_db_connection()

    total = local_cursor.execute("select count(*) from Users").fetchval()
    rows = local_cursor.execute('select id, external_ref, name, second_name, birthday, email, password from Users order by id').fetchall()

    progress_bar = tqdm(total=total)
    commit_counter = 0

    remote_cursor.execute('SET IDENTITY_INSERT Users ON')

    while progress_bar.n < progress_bar.total:
        data = []
        max_number_of_cumulative_inserts = 500
        number_of_collected_inserts = 0
        for line in rows:
            data.append(line)
            number_of_collected_inserts += 1
            progress_bar.update(1)
            if number_of_collected_inserts >= max_number_of_cumulative_inserts:
                values = ','.join([f"({line[0]}, '{line[1]}', '{line[2]}', '{line[3]}', '{line[4]}', '{line[5]}', '{line[6]}')" for line in data])
                try:

                    remote_cursor.execute(f'insert into Users (id, external_ref, name, second_name, birthday, email, password) values {values}')
                except Exception as e:
                    print(e)
                data = []
                number_of_collected_inserts = 0

            commit_counter += 1
            if commit_counter % 10000 == 0:
                remote_cnxn.commit()
    remote_cnxn.commit()

    remote_cursor.execute('SET IDENTITY_INSERT Users OFF')

    local_cursor.close()
    local_cnxn.close()
    remote_cursor.close()
    remote_cnxn.close()


# funkcja przenosząca dane z tabeli Friends z bazy lokalnej do bazy zdalnej
def transfer_friends() -> None:
    local_cnxn, local_cursor = create_local_db_connection()
    remote_cnxn, remote_cursor = create_remote_db_connection()

    total = local_cursor.execute("select count(*) from Friends").fetchval()
    rows = local_cursor.execute('select user_ref, friend_ref from Friends').fetchall()

    progress_bar = tqdm(total=total)
    commit_counter = 0

    while progress_bar.n < progress_bar.total:
        data = []
        max_number_of_cumulative_inserts = 500
        number_of_collected_inserts = 0
        for line in rows:
            data.append(line)
            number_of_collected_inserts += 1
            progress_bar.update(1)
            if number_of_collected_inserts >= max_number_of_cumulative_inserts:
                values = ','.join([f"({line[0]}, '{line[1]}')" for line in data])
                try:

                    remote_cursor.execute(f'insert into Friends (user_ref, friend_ref) values {values}')
                except Exception as e:
                    print(e)
                data = []
                number_of_collected_inserts = 0

            commit_counter += 1
            if commit_counter % 10000 == 0:
                remote_cnxn.commit()
    remote_cnxn.commit()

    local_cursor.close()
    local_cnxn.close()
    remote_cursor.close()
    remote_cnxn.close()


# funkcja przenosząca dane z tabeli Products z bazy lokalnej do bazy zdalnej
def transfer_products() -> None:
    local_cnxn, local_cursor = create_local_db_connection()
    remote_cnxn, remote_cursor = create_remote_db_connection()

    total = local_cursor.execute("select count(*) from Products").fetchval()
    rows = local_cursor.execute('select id, external_ref, name from Products order by id').fetchall()

    progress_bar = tqdm(total=total)
    commit_counter = 0

    remote_cursor.execute('SET IDENTITY_INSERT Products ON')
    remote_cursor.fast_executemany = True

    while progress_bar.n < progress_bar.total:
        data = []
        max_number_of_cumulative_inserts = 500
        number_of_collected_inserts = 0
        for line in rows:
            data.append(line)
            number_of_collected_inserts += 1
            progress_bar.update(1)
            if number_of_collected_inserts >= max_number_of_cumulative_inserts:
                try:
                    remote_cursor.executemany(f'insert into Products (id, external_ref, name) values (?, ?, ?)', data)
                except Exception as e:
                    print(e)
                data = []
                number_of_collected_inserts = 0

            commit_counter += 1
            if commit_counter % 10000 == 0:
                remote_cnxn.commit()
    remote_cnxn.commit()

    remote_cursor.execute('SET IDENTITY_INSERT Products OFF')

    local_cursor.close()
    local_cnxn.close()
    remote_cursor.close()
    remote_cnxn.close()


# funkcja tworząca połączenie do bazy zdalnej
def create_remote_db_connection():
    server = 'tcp:recommendation-sqlserver.database.windows.net,1433'
    database = 'RecommendationDataBase'
    username = 'azureuser'
    password = 'haslo12345!'
    return create_db_connection(server, database, username, password)


# funkcja tworząca połączenie do bazy lokalnej
def create_local_db_connection():
    server = 'localhost'
    database = 'recommendation_system'
    username = 'sa'
    password = 'praktyka'
    return create_db_connection(server, database, username, password)


# funkcja tworząca połączenie do bazy
def create_db_connection(server: str, database: str, username: str, password: str):
    cnxn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=' + server +
        ';DATABASE=' + database +
        ';ENCRYPT=no;UID=' + username +
        ';PWD=' + password
    )
    cursor = cnxn.cursor()
    return cnxn, cursor


# funkcja insertująca użytkowników do tabeli Users
def get_or_create_user(line: dict, cursor) -> None:
    external_ref = line['reviewerID']

    name, second_name, birthday, email, password = create_user_data(external_ref)

    try:
        count = cursor.execute(
            'insert into Users (name, second_name, birthday, email, password, external_ref) values (?, ?, ?, ?, ?, ?)',
            name,
            second_name,
            birthday,
            email,
            password,
            external_ref,
        ).rowcount
        assert count == 1
    except IntegrityError:
        pass


# funkcja tworząca dane potrzebne do wypełnienia tabeli Users. Funkcja losuje imię i nazwisko,
# data urodzin jest ustawiona na sztywno, e-mail składa się z id użytkownika + @gmail.com,
# hasło jest takie samo jak id użytkownika
def create_user_data(reviewer_id: str):
    name = names.get_first_name()
    second_name = names.get_last_name()
    birthday = '2001-04-14'
    email = f'{reviewer_id}@gmail.com'
    password = reviewer_id
    return name, second_name, birthday, email, password


# funkcja generująca sieć znajomych i wrzucająca je do bazy lokalnej
def generate_friends() -> None:
    cnxn, cursor = create_local_db_connection()

    rows = cursor.execute('select id from Users order by id').fetchall()
    user_ids = []
    for line in rows:
        user_ids.append(line[0])

    progress_bar = tqdm(total=len(rows))
    counter = 0

    for user_id in user_ids:
        max_number_of_friends = random.randint(1, 100)

        data = []
        for friend_id in random.choices(user_ids, k=max_number_of_friends):
            if friend_id != user_id:
                data.append(friend_id)

        data = set(data)

        values = ','.join([f'({user_id}, {i})' for i in data])
        try:
            cursor.execute(f'insert into Friends (user_ref, friend_ref) values {values}')
        except Exception as e:
            print(e)
        progress_bar.update(1)

        counter += 1
        if counter % 10000 == 0:
            cnxn.commit()
    cnxn.commit()

    cursor.close()
    cnxn.close()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    import_data()
    # import_products()
    # generate_friends()
    # transfer_users()
    # transfer_friends()
    # transfer_products()






