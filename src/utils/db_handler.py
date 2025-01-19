import mysql.connector
from mysql.connector import Error

class DBHandler:
    def __init__(self, host: str = None, user: str = None, password: str = None, database: str = None) -> None:
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
        except Error as e:
            raise ConnectionError(f"Failed to connect to database: {e}")

    def close(self): 
        if self.connection.is_connected():
            self.connection.close()

    def add_resource(self, resource_name: str, resource_path: str) -> None:
        query = "INSERT INTO resources (resource_name, resource_path, created_at) VALUES (%s, %s, NOW())"
        values = (resource_name, resource_path)

        cursor = self.connection.cursor()
        cursor.execute(query, values)
        self.connection.commit()
        cursor.close()
        return {"message": "Resource added successfully"}

    def check_resource_exist(self, resource_name: str) -> bool:
        query = "SELECT id FROM resources WHERE resource_name = %s"
        values = (resource_name,)

        cursor = self.connection.cursor()
        cursor.execute(query, values)
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result else None

    def add_question(self, quiz_type: str, question_data: dict) -> None:
        resource_id = self.check_resource_exist(question_data['category'])
        question_query = "INSERT INTO questions (resource_id, type, question, difficulty, created_at) VALUES (%s, %s, %s, %s, NOW())"
        question_values = (
            resource_id,
            quiz_type,
            question_data['question'],
            question_data['level'] 
        )

        cursor = self.connection.cursor()
        cursor.execute(question_query, question_values)
        question_id = cursor.lastrowid
        self.connection.commit()
        cursor.close()

        self._insert_data(quiz_type, question_id, question_data)
        return {"message": "Question added successfully"}

    def _insert_data(self, quiz_type: str, question_id: int, question_data: dict) -> None:
        query = {
            'multiple_choices': """
            INSERT INTO multiple_questions (question_id, option_a, option_b, option_c, option_d, correct_answer)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            'true_false': """
            INSERT INTO truefalse_questions (question_id, correct_answer)
            VALUES (%s, %s)
            """,
            'fill_the_blank': """
            INSERT INTO filltheblank_questions (question_id, correct_answer)
            VALUES (%s, %s)
            """
        }

        if quiz_type not in query:
            raise ValueError(f"Invalid question type: {quiz_type}")

        sql_query = query[quiz_type]
        values_list = []

        if quiz_type == 'multiple_choices':
            values = (
                question_id,
                question_data['option_a'],
                question_data['option_b'],
                question_data['option_c'],
                question_data['option_d'],
                question_data['answer']
            )
            values_list.append(values)
        elif quiz_type == 'true_false':
            values = (question_id, question_data['answer'])
            values_list.append(values)
        elif quiz_type == 'fill_the_blank':
            values = (question_id, question_data['answer'])
            values_list.append(values)

        cursor = self.connection.cursor()
        cursor.executemany(sql_query, values_list)
        self.connection.commit()
        cursor.close()