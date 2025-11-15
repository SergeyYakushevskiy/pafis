import os
import sys
from crypto_manager import AsymmetricCryptoProviderManager, RSAKeyPair
from file_service import FileService

class AsymmetricCryptoApp:
    """Консольное приложение для работы с асимметричным шифрованием"""
    
    def __init__(self):
        self.crypto_provider = AsymmetricCryptoProviderManager()
        self.current_keypair = None
    
    def clear_console(self):
        """Очистка консоли в зависимости от ОС"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def initialize(self):
        """Инициализация приложения"""
        self.clear_console()
        print("Инициализация криптопровайдера для асимметричного шифрования...")
        if self.crypto_provider.initialize():
            print("Криптопровайдер инициализирован")
            return True
        else:
            print("Не удалось инициализировать криптопровайдер")
            return False
    
    def show_menu(self):
        """Отображение главного меню"""
        self.clear_console()
        print("\n" + "="*60)
        print("ASYMMETRIC CRYPTOAPI ПРИЛОЖЕНИЕ ДЛЯ ШИФРОВАНИЯ")
        print("="*60)
        print("1. Сгенерировать новую пару RSA ключей")
        print("2. Сохранить публичный ключ в файл")
        print("3. Сохранить приватный ключ в файл")
        print("4. Загрузить публичный ключ из файла")
        print("5. Загрузить приватный ключ из файла")
        print("6. Зашифровать файл (публичным ключом)")
        print("7. Расшифровать файл (приватным ключом)")
        print("8. Создать тестовый файл")
        print("9. Выход")
        print("="*60)
    
    def show_status(self):
        """Показ статуса текущих ключей"""
        if self.current_keypair and self.current_keypair.is_generated():
            key_size = self.current_keypair.get_key_size()
            max_encrypt = self.current_keypair.get_max_encrypt_size()
            print(f"Текущие ключи: ЗАГРУЖЕНЫ (RSA-{key_size})")
            print(f"Макс. размер для шифрования: {max_encrypt} байт")
        else:
            print("Текущие ключи: ОТСУТСТВУЮТ")
    
    def generate_keypair(self):
        """Генерация новой пары RSA ключей"""
        self.clear_console()
        print("Генерация новой пары RSA ключей...")
        
        try:
            print("\nВыберите размер ключа:")
            print("1. RSA-1024 (быстрее, менее безопасно)")
            print("2. RSA-2048 (медленнее, более безопасно)")
            
            choice = input("Выберите размер (1-2, по умолчанию 2): ").strip()
            key_size = 2048 if choice != '1' else 1024
            
            self.current_keypair = RSAKeyPair(self.crypto_provider)
            self.current_keypair.generate(key_size)
            print(f"Новая пара RSA-{key_size} ключей успешно сгенерирована")
            print(f"Максимальный размер данных для шифрования: {self.current_keypair.get_max_encrypt_size()} байт")
            
        except Exception as e:
            print(f"Ошибка генерации ключей: {e}")
    
    def save_public_key(self):
        """Сохранение публичного ключа в файл"""
        self.clear_console()
        
        if not self.current_keypair or not self.current_keypair.is_generated():
            print("Сначала сгенерируйте пару ключей!")
            return
        
        print("Сохранение публичного ключа в файл...")
        self.show_status()
        print()
        
        file_path = input("Введите путь для сохранения публичного ключа: ").strip()
        if not file_path:
            print("Неверный путь к файлу")
            return
        
        try:
            hex_data = self.current_keypair.export_public_key_hex()
            key_size = self.current_keypair.get_key_size()
            
            metadata = {
                "Type": "RSA Public Key", 
                "Algorithm": f"RSA-{key_size}",
                "Usage": "Encryption"
            }
            
            FileService.write_hex_file(file_path, hex_data, metadata)
            print(f"Публичный ключ сохранен в {file_path}")
            print(f"HEX-превью: {hex_data[:64]}...")
            
        except Exception as e:
            print(f"Ошибка сохранения публичного ключа: {e}")
    
    def save_private_key(self):
        """Сохранение приватного ключа в файл"""
        self.clear_console()
        
        if not self.current_keypair or not self.current_keypair.is_generated():
            print("Сначала сгенерируйте пару ключей!")
            return
        
        print("Сохранение приватного ключа в файл...")
        self.show_status()
        print()
        
        file_path = input("Введите путь для сохранения приватного ключа: ").strip()
        if not file_path:
            print("Неверный путь к файлу")
            return
        
        try:
            hex_data = self.current_keypair.export_private_key_hex()
            key_size = self.current_keypair.get_key_size()
            
            metadata = {
                "Type": "RSA Private Key", 
                "Algorithm": f"RSA-{key_size}",
                "Usage": "Decryption",
                "Warning": "Keep this file secure!"
            }
            
            FileService.write_hex_file(file_path, hex_data, metadata)
            print(f"Приватный ключ сохранен в {file_path}")
            print(f"HEX-превью: {hex_data[:64]}...")
            print("ВНИМАНИЕ: Приватный ключ должен храниться в безопасном месте!")
            
        except Exception as e:
            print(f"Ошибка сохранения приватного ключа: {e}")
    
    def load_public_key(self):
        """Загрузка публичного ключа из файла"""
        self.clear_console()
        print("Загрузка публичного ключа из файла...")
        
        file_path = input("Введите путь к файлу с публичным ключом: ").strip()
        if not file_path:
            print("Неверный путь к файлу")
            return
        
        if not FileService.file_exists(file_path):
            print(f"Файл не существует: {file_path}")
            return
        
        try:
            hex_data = FileService.read_hex_file(file_path)
            self.current_keypair = RSAKeyPair(self.crypto_provider)
            self.current_keypair.import_public_key_hex(hex_data)
            print(f"Публичный ключ загружен из {file_path}")
            print(f"Размер ключа: RSA-{self.current_keypair.get_key_size()}")
            print(f"Макс. размер для шифрования: {self.current_keypair.get_max_encrypt_size()} байт")
                
        except Exception as e:
            print(f"Ошибка загрузки публичного ключа: {e}")
    
    def load_private_key(self):
        """Загрузка приватного ключа из файла"""
        self.clear_console()
        print("Загрузка приватного ключа из файла...")
        
        file_path = input("Введите путь к файлу с приватным ключом: ").strip()
        if not file_path:
            print("Неверный путь к файлу")
            return
        
        if not FileService.file_exists(file_path):
            print(f"Файл не существует: {file_path}")
            return
        
        try:
            hex_data = FileService.read_hex_file(file_path)
            self.current_keypair = RSAKeyPair(self.crypto_provider)
            self.current_keypair.import_private_key_hex(hex_data)
            print(f"Приватный ключ загружен из {file_path}")
            print(f"Размер ключа: RSA-{self.current_keypair.get_key_size()}")
                
        except Exception as e:
            print(f"Ошибка загрузки приватного ключа: {e}")
    
    def encrypt_file(self):
        """Шифрование файла публичным ключом"""
        self.clear_console()
        print("Шифрование файла публичным ключом...")
        self.show_status()
        print()
        
        if not self.current_keypair or not self.current_keypair.is_generated():
            print("Сначала загрузите или сгенерируйте ключи!")
            return
        
        input_file = input("Введите путь к исходному файлу: ").strip()
        output_file = input("Введите путь для зашифрованного файла: ").strip()
        
        if not input_file or not output_file:
            print("Неверные пути к файлам")
            return
        
        if not FileService.file_exists(input_file):
            print(f"Исходный файл не существует: {input_file}")
            return
        
        try:
            # Читаем исходный файл
            plaintext = FileService.read_binary_file(input_file)
            max_size = self.current_keypair.get_max_encrypt_size()
            
            print(f"Размер исходного файла: {len(plaintext)} байт")
            print(f"Максимальный размер для RSA шифрования: {max_size} байт")
            
            if len(plaintext) > max_size:
                print(f"Файл слишком большой для RSA шифрования!")
                print(f"Рекомендация: Используйте гибридное шифрование или разбейте файл на части")
                return
            
            # Шифруем данные
            hex_data = self.current_keypair.encrypt_bytes(plaintext)
            
            # Сохраняем зашифрованные данные
            key_size = self.current_keypair.get_key_size()
            metadata = {
                "Type": "RSA Encrypted File",
                "Original size": f"{len(plaintext)} bytes",
                "Algorithm": f"RSA-{key_size}",
                "Max block size": f"{max_size} bytes"
            }
            
            FileService.write_hex_file(output_file, hex_data, metadata)
            
            print(f"Файл зашифрован: {input_file} -> {output_file}")
            print(f"HEX-превью: {hex_data[:64]}...")
            print(f"Размер зашифрованных данных: {len(hex_data)//2} байт")
            
        except Exception as e:
            print(f"Ошибка шифрования: {e}")
    
    def decrypt_file(self):
        """Расшифрование файла приватным ключом"""
        self.clear_console()
        print("Расшифрование файла приватным ключом...")
        self.show_status()
        print()
        
        if not self.current_keypair or not self.current_keypair.is_generated():
            print("Сначала загрузите приватный ключ!")
            return
        
        input_file = input("Введите путь к зашифрованному файлу: ").strip()
        output_file = input("Введите путь для расшифрованного файла: ").strip()
        
        if not input_file or not output_file:
            print("Неверные пути к файлам")
            return
        
        if not FileService.file_exists(input_file):
            print(f"Зашифрованный файл не существует: {input_file}")
            return
        
        try:
            # Читаем HEX данные
            hex_data = FileService.read_hex_file(input_file)
            
            # Расшифровываем данные
            decrypted_data = self.current_keypair.decrypt_hex(hex_data)
            
            # Сохраняем расшифрованные данные
            FileService.write_binary_file(output_file, decrypted_data)
            
            print(f"Файл расшифрован: {input_file} -> {output_file}")
            print(f"Размер расшифрованного файла: {len(decrypted_data)} байт")
            
            # Показываем превью для текстовых файлов
            try:
                text_preview = decrypted_data[:100].decode('utf-8', errors='ignore')
                print(f"Превью: {text_preview}...")
            except:
                print(f"Первые 16 байт: {decrypted_data[:16].hex()}...")
                
        except Exception as e:
            print(f"Ошибка расшифрования: {e}")
    
    def create_test_file(self):
        """Создание тестового файла"""
        self.clear_console()
        print("Создание тестового файла для RSA шифрования...")
        
        file_path = input("Введите путь для тестового файла: ").strip()
        if not file_path:
            print("Неверный путь к файлу")
            return
        
        # Создаем тестовое содержимое подходящего размера для RSA
        if self.current_keypair and self.current_keypair.is_generated():
            max_size = self.current_keypair.get_max_encrypt_size()
            content = f"Это тестовый файл для RSA шифрования.\nМаксимальный размер для RSA-{self.current_keypair.get_key_size()}: {max_size} байт.\n" + "A" * (max_size - 100)
        else:
            content = "Это тестовый файл для RSA шифрования.\nРекомендуемый размер до 200 байт для RSA-2048.\n" + "A" * 50
        
        try:
            FileService.create_test_file(file_path, content)
            print(f"Тестовый файл создан: {file_path}")
            print(f"Размер файла: {len(content)} байт")
            
        except Exception as e:
            print(f"Ошибка создания тестового файла: {e}")
    
    def run(self):
        """Запуск приложения"""
        if not self.initialize():
            return
        
        print("Приложение для асимметричного шифрования готово к работе!")
        input("Нажмите Enter для продолжения...")
        
        while True:
            self.show_menu()
            self.show_status()
            print()
            
            choice = input("Выберите действие (1-9): ").strip()
            
            try:
                if choice == '1':
                    self.generate_keypair()
                elif choice == '2':
                    self.save_public_key()
                elif choice == '3':
                    self.save_private_key()
                elif choice == '4':
                    self.load_public_key()
                elif choice == '5':
                    self.load_private_key()
                elif choice == '6':
                    self.encrypt_file()
                elif choice == '7':
                    self.decrypt_file()
                elif choice == '8':
                    self.create_test_file()
                elif choice == '9':
                    print("Выход из программы...")
                    break
                else:
                    print("Неверный выбор! Попробуйте снова.")
            except KeyboardInterrupt:
                print("\n\nПрограмма прервана пользователем")
                break
            except Exception as e:
                print(f"Неожиданная ошибка: {e}")
            
            if choice != '9':
                input("\nНажмите Enter для продолжения...")
        
        # Очистка ресурсов
        if self.current_keypair:
            self.current_keypair.cleanup()
        self.crypto_provider.cleanup()


def main():
    """Точка входа в приложение"""
    try:
        app = AsymmetricCryptoApp()
        app.run()
    except KeyboardInterrupt:
        print("\n\nДо свидания!")
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        input("Нажмите Enter для выхода...")


if __name__ == "__main__":
    main()