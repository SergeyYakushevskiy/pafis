import os
import binascii

class FileService:
    """Сервис для работы с файловой системой"""
    
    @staticmethod
    def read_binary_file(file_path):
        """Чтение бинарного файла"""
        try:
            with open(file_path, 'rb') as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Файл не найден: {file_path}")
        except Exception as e:
            raise RuntimeError(f"Ошибка чтения файла {file_path}: {e}")
    
    @staticmethod
    def write_binary_file(file_path, data):
        """Запись бинарного файла"""
        try:
            # Создаем директорию если нужно
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'wb') as f:
                f.write(data)
        except Exception as e:
            raise RuntimeError(f"Ошибка записи файла {file_path}: {e}")
    
    @staticmethod
    def read_hex_file(file_path):
        """Чтение HEX-файла (игнорирует комментарии)"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Извлекаем HEX данные (игнорируем комментарии)
            hex_data = ""
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    hex_data += line
            
            if not hex_data:
                raise ValueError(f"Файл не содержит данных: {file_path}")
            
            return hex_data
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Файл не найден: {file_path}")
        except Exception as e:
            raise RuntimeError(f"Ошибка чтения HEX файла {file_path}: {e}")
    
    @staticmethod
    def write_hex_file(file_path, hex_data, metadata=None):
        """Запись HEX-файла с метаданными"""
        try:
            # Создаем директорию если нужно
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                # Записываем метаданные как комментарии
                if metadata:
                    for key, value in metadata.items():
                        f.write(f"# {key}: {value}\n")
                
                # Записываем HEX данные
                f.write(hex_data)
                
        except Exception as e:
            raise RuntimeError(f"Ошибка записи HEX файла {file_path}: {e}")
    
    @staticmethod
    def file_exists(file_path):
        """Проверка существования файла"""
        return os.path.exists(file_path)
    
    @staticmethod
    def create_test_file(file_path, content="Тестовое содержимое файла"):
        """Создание тестового файла"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            raise RuntimeError(f"Ошибка создания тестового файла {file_path}: {e}")