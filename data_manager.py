from psycopg2 import sql
import db_connect as db


@db.connection_handler
def get_all_entries(cursor,
                    limit=None,
                    table="question",
                    column="submission_time",
                    direction="DESC"):
    limited = " LIMIT {limit}".format(limit=limit) if limit is not None else ""
    query = sql.SQL("""
                    SELECT * FROM {table}
                    ORDER BY {column} {direction} {limit};
                    """.format(
            table=table,
            column=column,
            direction=direction,
            limit=limited)
            )
    cursor.execute(query)
    return cursor.fetchall()


@db.connection_handler
def get_entry_by_id(cursor, entry_id,
                    table="question"):
    query = sql.SQL("""
                    SELECT * FROM {table}
                    WHERE id=%(id)s;
                    """.format(
            table=table,
            column=sql.Identifier(entry_id))
            )
    data = {
            "id": entry_id
            }
    cursor.execute(query, data)
    return cursor.fetchone()


@db.connection_handler
def get_question(cursor, question_id):
    query = """SELECT * FROM question
               WHERE id = %(question_id)s;"""
    data = {
            "question_id": question_id
            }
    cursor.execute(query, data)
    return cursor.fetchone()


@db.connection_handler
def get_answer_for_question(cursor, question_id):
    query = """SELECT * FROM answer
               WHERE question_id = %(question_id)s;"""
    data = {
            "question_id": question_id
            }
    cursor.execute(query, data)
    return cursor.fetchall()


@db.connection_handler
def get_question_comments(cursor, question_id):
    query = """SELECT * FROM comment
               WHERE question_id = %(question_id)s;"""
    data = {
            "question_id": question_id,
            }
    cursor.execute(query, data)
    return cursor.fetchall()


@db.connection_handler
def get_answer_comments(cursor, answer_id):
    query = """SELECT * FROM comment
               WHERE answer_id = %(answer_id)s;"""
    data = {
            "answer_id": answer_id,
            }
    cursor.execute(query, data)
    return cursor.fetchall()


@db.connection_handler
def sort(cursor,
         criteria="submission_time",
         direction="DESC",
         table="question"):
    query = sql.SQL("""
            SELECT * FROM {table}
            ORDER BY %(criteria)s %(direction)s;
            """.format(
            table=sql.Identifier(table)
            ))
    data = {
            "criteria": criteria,
            "direction": direction,
            }
    cursor.execute(query, data)
    return cursor.fetchall()


@db.connection_handler
def edit_question(cursor, question_id, dict_with_updates):
    cursor.execute(""" UPDATE question SET message = %s, title = %s WHERE id = %s;

    """, (dict_with_updates['message'], dict_with_updates['title'], str(question_id),))


@db.connection_handler
def add_new_answer(cursor, new_answer):
    cursor.execute("""
        INSERT INTO answer( submission_time, vote_number, question_id, message, image) 
            VALUES (CURRENT_TIMESTAMP, 0, %s, %s, %s );
    """, (new_answer['question_id'], new_answer['message'], new_answer['image']))


@db.connection_handler
def delete_entry(cursor, row_id, table):
    query = sql.SQL("DELETE FROM {table} WHERE {pkey}=%(row_id)s").format(
            table=sql.Identifier(table),
            pkey=sql.Identifier("id"))
    data = {
            "row_id": row_id
            }
    cursor.execute(query, data)


@db.connection_handler
def vote(cursor, id, type, table):
    if type == "up":
        cursor.execute(
                sql.SQL(
                        "UPDATE {} SET vote_number = vote_number + 1 WHERE id={};".format(
                                # sql.Identifier(table),
                                table, id
                                )
                        )
                )
    elif type == "down":
        cursor.execute(
                sql.SQL(
                        "UPDATE {} SET vote_number = vote_number - 1 WHERE id={};".format(
                                table,
                                id
                                )
                        )
                )
    else:
        pass


@db.connection_handler
def edit_answer(cursor, id, updated_answer):
    cursor.execute(
            """ UPDATE answer SET message = %s, image = %s WHERE id = %s;""", (
                    updated_answer['message'], updated_answer['image'], str(id
                                                                            ),
                    )
            )


@db.connection_handler
def add_answer_comment(cursor, comments):
    cursor.execute("""INSERT INTO comment
               (question_id, answer_id, message, 
               submission_time, edited_count)
               VALUES (null, %s, %s, CURRENT_TIMESTAMP, null)
               """, (comments['answer_id'], comments['message'],))


@db.connection_handler
def add_question_comment(cursor, comment):
    cursor.execute("""INSERT INTO comment
                  (question_id, answer_id, message, 
                  submission_time, edited_count)
                  VALUES (%s, null, %s, CURRENT_TIMESTAMP, null)
                  """, (comment['question_id'], comment['message'],))


@db.connection_handler
def add_new_question(cursor, question_content):
    if len(question_content) >= 3:
        cursor.execute("""
            INSERT INTO question (submission_time, view_number, vote_number, title, message, image)
                VALUES (CURRENT_TIMESTAMP, 0, 0, %s, %s, %s )
        """, (question_content['title'], question_content['message'], question_content['image']))
    else:
        cursor.execute("""
                   INSERT INTO question (submission_time, view_number, vote_number, title, message, image)
                       VALUES (CURRENT_TIMESTAMP, 0, 0, %s, %s, null )
               """, (question_content['title'], question_content['message'], ))


@db.connection_handler
def search_question(cursor, key_words):
    key_words = key_words.replace("+", " ")
    list_of_key_words = key_words.split(" ")
    clause = ""
    columns = ["title", "message"]
    for key_word in list_of_key_words:
        for column in columns:
            clause += f"{column} ILIKE '%{key_word}%' OR "
    clause = clause[:-4]
    query = f"""
            SELECT * FROM question
            WHERE ({clause});
            """
    cursor.execute(query)
    return cursor.fetchall()


@db.connection_handler
def search_answer(cursor, key_words):
    key_words = key_words.replace("+", " ")
    list_of_key_words = key_words.split(" ")
    clause = ""
    columns = ["message"]
    for key_word in list_of_key_words:
        for column in columns:
            clause += f"{column} ILIKE '%{key_word}%' OR "
    clause = clause[:-4]
    query = f"""
            SELECT * FROM answer
            WHERE ({clause});
            """
    cursor.execute(query)
    return cursor.fetchall()


@db.connection_handler
def add_picture_to_db(cursor, table_id, filename, table):
    query = """UPDATE %(table)s
               SET picture=%(filename)s
               WHERE id=%(id)s
               """
    data = {
            "table": table,
            "filename": filename,
            "id": table_id
            }
    cursor.execute(query, data)


@db.connection_handler
def count_views(cursor, question_id):
    cursor.execute(f"""
                   UPDATE question
                   SET view_number = view_number + 1
                   WHERE id = %s ;
                   """, (question_id,))

@db.connection_handler
def question_id_by_answer_id(cursor, answer_id):
    cursor.execute("""
        SELECT question_id FROM answer     
        where id = %s;
        """, (answer_id,)
    )
    question = cursor.fetchall()
    for i in question:

        return i['question_id']

