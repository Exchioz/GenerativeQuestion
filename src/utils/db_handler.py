import mysql.connector
from mysql.connector import Error
import json

class DBHandler:
    def __init__(self, host: int = None, user: str = None, password: str = None, database: str = None) -> None:
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

    def add_resource(self, resource_data: dict) -> None:
        pass
    
    def add_question(self, question_data: dict) -> None:
        get_type = list(question_data.keys())[0]

        question_query = "INSERT INTO questions (type, content, difficulty, created_at) VALUES (%s, %s, %s, NOW())"
        question_values = (
            get_type,
            question_data[get_type][0].get('question'),
            question_data[get_type][0].get('level')
        )

        cursor = self.connection.cursor()
        cursor.execute(question_query, question_values)
        question_id = cursor.lastrowid
        self.connection.commit()
        cursor.close()

        self._insert_data(get_type, question_id, question_data[get_type])
        return {"message": "Question added successfully"}
    
    def _insert_data(self, question_type, question_id, question_details):
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

        if question_type not in query:
            raise ValueError(f"Invalid question type: {question_type}")

        query = query[question_type]
        values_list = []

        for question in question_details:
            if question_type == 'multiple_choices':
                values = ((
                    question_id,
                    question.get('option_a'),
                    question.get('option_b'),
                    question.get('option_c'),
                    question.get('option_d'),
                    question.get('answer')
                ))
            elif question_type in ['true_false', 'fill_the_blank']:
                values = ((
                    question_id,
                    question.get('answer')
                ))
            
            values_list.append(values)
        
        cursor = self.connection.cursor()
        cursor.executemany(query, values_list)
        self.connection.commit()
        cursor.close()