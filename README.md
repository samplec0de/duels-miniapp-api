# API для VK MiniApp "Школьные дуэли"

Доступные на данный момент предметы: ('math', 'russian', 'informatics', 'english')

**GET** */tasks/random/<subject>/<vk_user_id>*

Получить случайную задачу

subject: предмет <br/>
vk_user_id: идентификатор пользователя от вк <br/>

Результат: { <br/>
            'task_id': string <br/>
            'subject': string, предмет <br/>
            'text': string, <br/>
            'variants': list, элементы string <br/>
        } <br/>


**POST** */check_answer*

Проверить правильность ответа <br />
answer: int, индекс ответа пользователя <br />
subject: string, предмет <br />
task_id: string, айди задачи <br />
vk_user_id: integer, идентификатор пользователя от вк <br/>

Результат: {"correct": boolean}


**GET** */correct_answer/<subject>/<task_id>/<vk_user_id>*

Получить правильный ответ. Можно вызывать только для задач, которые вернул /tasks/random

subject: string, предмет <br/>
task_id: string, айди задачи <br/>
vk_user_id: идентификатор пользователя от вк

Результат: {"answer": <верный ответ строкой>, "points": количество очков за задачу, int/float (пока int)}
