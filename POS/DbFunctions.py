from sqlite3 import connect


def database_all_lookup(db_path: str, what_selection: str, from_selection: str):
    db_connection = connect(db_path)
    writer = db_connection.cursor()
    lookup_command = f"SELECT {what_selection} FROM {from_selection}"

    writer.execute(lookup_command)
    result = writer.fetchall()
    db_connection.close()

    return result


def database_specified_lookup(db_path: str, what_selection: str, from_selection: str, where_selection: str,
                              value_select):
    db_connection = connect(db_path)
    writer = db_connection.cursor()
    lookup_command = f"SELECT {what_selection} FROM {from_selection} WHERE {where_selection} = ?"

    writer.execute(lookup_command, (value_select,))
    result = writer.fetchall()
    db_connection.close()

    return result


def database_like_lookup(db_path: str, what_selection: str, from_selection: str, where_selection: str, value_select):
    db_connection = connect(db_path)
    writer = db_connection.cursor()
    lookup_command = f"SELECT {what_selection} FROM {from_selection} WHERE {where_selection} LIKE ?"

    # Surround the value with '%' for partial matching
    like_value = f"%{value_select}%"

    writer.execute(lookup_command, (like_value,))
    result = writer.fetchall()
    db_connection.close()

    return result


def database_update(db_path: str, what_selection: str, set_selection: str, new_value, where_selection: str,
                    value_select):
    db_connection = connect(db_path)
    writer = db_connection.cursor()
    lookup_command = f"UPDATE {what_selection} SET {set_selection} = ? WHERE {where_selection} = ?"

    writer.execute(lookup_command, (new_value, value_select))
    db_connection.commit()  # Ensure changes are saved
    db_connection.close()


def database_delete(db_path: str, from_selection: str, where_selection: str, value_select):
    db_connection = connect(db_path)
    writer = db_connection.cursor()
    lookup_command = f"DELETE FROM {from_selection} WHERE {where_selection} = ?"

    writer.execute(lookup_command, (value_select,))
    db_connection.commit()  # Ensure changes are saved
    db_connection.close()


def database_insert(db_path: str, into_selection: str, new_values: tuple):
    values_length = len(new_values)
    parameters = '(' + ','.join('?' * values_length) + ')'

    db_connection = connect(db_path)
    writer = db_connection.cursor()
    lookup_command = f"INSERT INTO {into_selection} VALUES {parameters}"

    writer.execute(lookup_command, new_values)
    db_connection.commit()  # Make sure to commit the transaction
    db_connection.close()