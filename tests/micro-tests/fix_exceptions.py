import re
with open('../../pyegeria/core/_exceptions.py', 'r') as f: content = f.read()
content = content.replace('logger.info(self.__str__())', 'logger.debug(self.__str__())')
content = content.replace('logger.info(self.__str__(), ', 'logger.debug(self.__str__(), ')
content = content.replace('logger.info(escaped_msg, ', 'logger.debug(escaped_msg, ') 
content = content.replace('logger.info(response.json())', 'logger.debug(response.json())')
content = re.sub(r'def __str__\(self\):.*?return msg', 'def __str__(self):
        return f\"{self.pyegeria_code}: {self.message}\"', content, flags=re.DOTALL)
with open('../../pyegeria/core/_exceptions.py', 'w') as f: f.write(content)