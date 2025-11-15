import os
import sys
from crypto_manager import CryptoProviderManager, SymmetricKey
from file_service import FileService

class CryptoApp:
    """Консольное приложение для работы с шифрованием"""
    
    def __init__(self):
        self.crypto_provider = CryptoProviderManager()
        self.current_key = None
    
    def clear_console(self):
        """Очистка консоли в зависимости от ОС"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def initialize(self):
        """Инициализация приложения"""
        self.clear_console()
        print("🔐 Инициализация криптопровайдера...")
        if self.crypto_provider.initialize():
            print("✅ Криптопровайдер инициализирован")
            return True
        else:
            print("❌ Не удалось инициализировать криптопровайдер")
            return False
    
    def show_menu(self):
        """Отображение главного меню"""
        self.clear_console()
        print("\n" + "="*50)
        print("🔐 CRYPTOAPI ПРИЛОЖЕНИЕ ДЛЯ ШИФРОВАНИЯ")
        print("="*50)
        print("1. Сгенерировать новый ключ")
        print("2. Сохранить ключ в файл")
        print("3. Загрузить ключ из файла")
        print("4. Зашифровать файл")
        print("5. Расшифровать файл")
        print("6. Создать тестовый файл")
        print("7. Выход")
        print("="*50)
    
    def show_status(self):
        """Показ статуса текущего ключа"""
        if self.current_key and self.current_key.is_generated():
            print(f"🔑 Текущий ключ: ЗАГРУЖЕН (AES-256)")
            iv = self.current_key.get_iv_hex()
            if iv:
                print(f"🔢 Текущий IV: {iv[:16]}...")
        else:
            print("🔑 Текущий ключ: ОТСУТСТВУЕТ")
    
    def generate_key(self):
        """Генерация нового ключа"""
        self.clear_console()
        print("🔑 Генерация нового ключа...")
        
        try:
            self.current_key = SymmetricKey(self.crypto_provider)
            self.current_key.generate()
            print("✅ Новый ключ AES-256 успешно сгенерирован")
            iv = self.current_key.get_iv_hex()
            if iv:
                print(f"🔢 Сгенерирован IV: {iv}")
        except Exception as e:
            print(f"❌ Ошибка генерации ключа: {e}")
    
    def save_key(self):
        """Сохранение ключа в файл"""
        self.clear_console()
        
        if not self.current_key or not self.current_key.is_generated():
            print("❌ Сначала сгенерируйте ключ!")
            return
        
        print("💾 Сохранение ключа в файл...")
        self.show_status()
        print()
        
        file_path = input("Введите путь для сохранения ключа: ").strip()
        if not file_path:
            print("❌ Неверный путь к файлу")
            return
        
        try:
            hex_data = self.current_key.export_hex()
            iv = self.current_key.get_iv_hex()
            
            metadata = {
                "Type": "Symmetric Key", 
                "Algorithm": "AES-256",
                "IV": iv if iv else "Not available"
            }
            
            FileService.write_hex_file(file_path, hex_data, metadata)
            print(f"✅ Ключ сохранен в {file_path}")
            print(f"🔑 HEX-превью: {hex_data[:64]}...")
            if iv:
                print(f"🔢 IV сохранен: {iv}")
        except Exception as e:
            print(f"❌ Ошибка сохранения ключа: {e}")
    
    def load_key(self):
        """Загрузка ключа из файла"""
        self.clear_console()
        print("📂 Загрузка ключа из файла...")
        
        file_path = input("Введите путь к файлу с ключом: ").strip()
        if not file_path:
            print("❌ Неверный путь к файлу")
            return
        
        if not FileService.file_exists(file_path):
            print(f"❌ Файл не существует: {file_path}")
            return
        
        try:
            hex_data = FileService.read_hex_file(file_path)
            self.current_key = SymmetricKey(self.crypto_provider)
            self.current_key.import_hex(hex_data)
            print(f"✅ Ключ загружен из {file_path}")
            
            # Пытаемся получить IV из метаданных файла
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    for line in lines:
                        if line.startswith('# IV:'):
                            iv_hex = line.split(':')[1].strip()
                            if len(iv_hex) == 32:  # Проверяем что это валидный IV
                                self.current_key.set_iv(iv_hex)
                                print(f"🔢 IV восстановлен из файла")
                                break
            except:
                print("⚠️  Не удалось восстановить IV из файла")
                
        except Exception as e:
            print(f"❌ Ошибка загрузки ключа: {e}")
    
    def encrypt_file(self):
        """Шифрование файла"""
        self.clear_console()
        print("🔒 Шифрование файла...")
        self.show_status()
        print()
        
        if not self.current_key or not self.current_key.is_generated():
            print("❌ Сначала загрузите или сгенерируйте ключ!")
            return
        
        input_file = input("Введите путь к исходному файлу: ").strip()
        output_file = input("Введите путь для зашифрованного файла: ").strip()
        
        if not input_file or not output_file:
            print("❌ Неверные пути к файлам")
            return
        
        if not FileService.file_exists(input_file):
            print(f"❌ Исходный файл не существует: {input_file}")
            return
        
        try:
            # Читаем исходный файл
            plaintext = FileService.read_binary_file(input_file)
            print(f"📊 Размер исходного файла: {len(plaintext)} байт")
            
            # Шифруем данные
            hex_data = self.current_key.encrypt_bytes(plaintext)
            
            # Получаем IV для сохранения в метаданных
            iv = self.current_key.get_iv_hex()
            
            # Сохраняем зашифрованные данные
            metadata = {
                "Type": "Encrypted File",
                "Original size": f"{len(plaintext)} bytes",
                "Algorithm": "AES-256-CBC",
                "IV": iv if iv else "Not available"
            }
            
            FileService.write_hex_file(output_file, hex_data, metadata)
            
            print(f"✅ Файл зашифрован: {input_file} -> {output_file}")
            print(f"🔐 HEX-превью: {hex_data[:64]}...")
            if iv:
                print(f"🔢 Использован IV: {iv}")
            
        except Exception as e:
            print(f"❌ Ошибка шифрования: {e}")
    
    def decrypt_file(self):
        """Расшифрование файла"""
        self.clear_console()
        print("🔓 Расшифрование файла...")
        self.show_status()
        print()
        
        if not self.current_key or not self.current_key.is_generated():
            print("❌ Сначала загрузите или сгенерируйте ключ!")
            return
        
        input_file = input("Введите путь к зашифрованному файлу: ").strip()
        output_file = input("Введите путь для расшифрованного файла: ").strip()
        
        if not input_file or not output_file:
            print("❌ Неверные пути к файлам")
            return
        
        if not FileService.file_exists(input_file):
            print(f"❌ Зашифрованный файл не существует: {input_file}")
            return
        
        try:
            # Читаем HEX данные
            hex_data = FileService.read_hex_file(input_file)
            
            # Пытаемся получить IV из метаданных файла
            try:
                with open(input_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    for line in lines:
                        if line.startswith('# IV:'):
                            iv_hex = line.split(':')[1].strip()
                            if len(iv_hex) == 32:  # Проверяем что это валидный IV
                                self.current_key.set_iv(iv_hex)
                                print(f"🔢 Использован IV из файла: {iv_hex}")
                                break
            except:
                print("⚠️  Не удалось прочитать IV из файла, используется текущий IV")
            
            # Расшифровываем данные
            decrypted_data = self.current_key.decrypt_hex(hex_data)
            
            # Сохраняем расшифрованные данные
            FileService.write_binary_file(output_file, decrypted_data)
            
            print(f"✅ Файл расшифрован: {input_file} -> {output_file}")
            print(f"📊 Размер расшифрованного файла: {len(decrypted_data)} байт")
            
            # Показываем превью для текстовых файлов
            try:
                text_preview = decrypted_data[:100].decode('utf-8', errors='ignore')
                print(f"🔍 Превью: {text_preview}...")
            except:
                print(f"🔍 Первые 16 байт: {decrypted_data[:16].hex()}...")
                
        except Exception as e:
            print(f"❌ Ошибка расшифрования: {e}")
    
    def create_test_file(self):
        """Создание тестового файла"""
        self.clear_console()
        print("📄 Создание тестового файла...")
        
        file_path = input("Введите путь для тестового файла: ").strip()
        if not file_path:
            print("❌ Неверный путь к файлу")
            return
        
        content = input("Введите содержимое файла (или Enter для стандартного): ").strip()
        if not content:
            content = "Это тестовый файл для проверки работы шифрования.\nМожно использовать для тестирования."
        
        try:
            FileService.create_test_file(file_path, content)
            print(f"✅ Тестовый файл создан: {file_path}")
        except Exception as e:
            print(f"❌ Ошибка создания тестового файла: {e}")
    
    def run(self):
        """Запуск приложения"""
        if not self.initialize():
            return
        
        print("🚀 Приложение готово к работе!")
        input("Нажмите Enter для продолжения...")
        
        while True:
            self.show_menu()
            self.show_status()
            print()
            
            choice = input("Выберите действие (1-7): ").strip()
            
            try:
                if choice == '1':
                    self.generate_key()
                elif choice == '2':
                    self.save_key()
                elif choice == '3':
                    self.load_key()
                elif choice == '4':
                    self.encrypt_file()
                elif choice == '5':
                    self.decrypt_file()
                elif choice == '6':
                    self.create_test_file()
                elif choice == '7':
                    print("Выход из программы...")
                    break
                else:
                    print("❌ Неверный выбор! Попробуйте снова.")
            except KeyboardInterrupt:
                print("\n\n⏹️  Программа прервана пользователем")
                break
            except Exception as e:
                print(f"❌ Неожиданная ошибка: {e}")
            
            if choice != '7':
                input("\nНажмите Enter для продолжения...")
        
        # Очистка ресурсов
        if self.current_key:
            self.current_key.cleanup()
        self.crypto_provider.cleanup()


def main():
    """Точка входа в приложение"""
    try:
        app = CryptoApp()
        app.run()
    except KeyboardInterrupt:
        print("\n\n👋 До свидания!")
    except Exception as e:
        print(f"💥 Критическая ошибка: {e}")
        input("Нажмите Enter для выхода...")


if __name__ == "__main__":
    main()