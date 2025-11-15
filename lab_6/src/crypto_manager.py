import ctypes
from ctypes import wintypes
import binascii

class CryptoProviderManager:
    """Управление криптопровайдером Windows CryptoAPI"""
    
    # Константы CryptoAPI
    PROV_RSA_FULL = 1
    PROV_RSA_AES = 24
    MS_ENH_RSA_AES_PROV = "Microsoft Enhanced RSA and AES Cryptographic Provider"
    CRYPT_NEWKEYSET = 0x00000008
    CRYPT_EXPORTABLE = 0x00000001
    CALG_AES_256 = 0x00006610
    KP_IV = 1
    KP_MODE = 4
    CRYPT_MODE_CBC = 1
    
    def __init__(self):
        self.advapi32 = ctypes.windll.advapi32
        self.kernel32 = ctypes.windll.kernel32
        self.hprov = wintypes.HANDLE()
        self.container_name = "PythonCryptoContainer"
        self._initialized = False
    
    def initialize(self):
        """Инициализация криптопровайдера"""
        if self._initialized:
            return True
            
        try:
            # Пробуем получить существующий контекст
            result = self.advapi32.CryptAcquireContextW(
                ctypes.byref(self.hprov),
                self.container_name,
                self.MS_ENH_RSA_AES_PROV,
                self.PROV_RSA_AES,
                0
            )
            
            if not result:
                # Создаем новый контейнер
                result = self.advapi32.CryptAcquireContextW(
                    ctypes.byref(self.hprov),
                    self.container_name,
                    self.MS_ENH_RSA_AES_PROV,
                    self.PROV_RSA_AES,
                    self.CRYPT_NEWKEYSET
                )
            
            self._initialized = bool(result)
            return self._initialized
            
        except Exception as e:
            print(f"❌ Ошибка инициализации провайдера: {e}")
            return False
    
    def is_initialized(self):
        """Проверка инициализации провайдера"""
        return self._initialized
    
    def cleanup(self):
        """Очистка ресурсов"""
        try:
            if self.hprov:
                self.advapi32.CryptReleaseContext(self.hprov, 0)
                self.hprov = wintypes.HANDLE()
                self._initialized = False
        except:
            pass


class SymmetricKey:
    """Управление симметричным ключом шифрования"""
    
    def __init__(self, crypto_provider):
        self.crypto_provider = crypto_provider
        self.hkey = wintypes.HANDLE()
        self._generated = False
        self._iv = None
    
    def generate(self):
        """Генерация нового симметричного ключа"""
        if not self.crypto_provider.is_initialized():
            raise RuntimeError("Криптопровайдер не инициализирован")
        
        try:
            # Генерируем случайный сессионный ключ
            result = self.crypto_provider.advapi32.CryptGenKey(
                self.crypto_provider.hprov,
                self.crypto_provider.CALG_AES_256,
                self.crypto_provider.CRYPT_EXPORTABLE,
                ctypes.byref(self.hkey)
            )
            
            if result:
                self._setup_encryption_mode()
                self._generated = True
                return True
            else:
                error = self.crypto_provider.kernel32.GetLastError()
                raise RuntimeError(f"Ошибка генерации ключа. Код: {error}")
                
        except Exception as e:
            raise RuntimeError(f"Ошибка генерации ключа: {e}")
    
    def _setup_encryption_mode(self):
        """Настройка режима шифрования CBC"""
        try:
            # Устанавливаем режим CBC
            mode = wintypes.DWORD(self.crypto_provider.CRYPT_MODE_CBC)
            self.crypto_provider.advapi32.CryptSetKeyParam(
                self.hkey,
                self.crypto_provider.KP_MODE,
                ctypes.byref(mode),
                0
            )
            
            # Генерируем случайный IV только если его еще нет
            if not self._iv:
                iv_size = 16
                iv_buffer = ctypes.create_string_buffer(iv_size)
                result = self.crypto_provider.advapi32.CryptGenRandom(
                    self.crypto_provider.hprov,
                    iv_size,
                    iv_buffer
                )
                
                if result:
                    # Сохраняем IV для возможного повторного использования
                    self._iv = iv_buffer.raw[:iv_size]
            
            # Устанавливаем IV (существующий или новый)
            if self._iv:
                iv_buffer = ctypes.create_string_buffer(self._iv)
                self.crypto_provider.advapi32.CryptSetKeyParam(
                    self.hkey,
                    self.crypto_provider.KP_IV,
                    iv_buffer,
                    0
                )
                
        except Exception as e:
            print(f"⚠️ Ошибка настройки режима шифрования: {e}")
    
    def export_hex(self):
        """Экспорт ключа в HEX-формате"""
        if not self._generated:
            raise RuntimeError("Ключ не сгенерирован")
        
        try:
            # Получаем размер данных ключа
            data_len = wintypes.DWORD(0)
            self.crypto_provider.advapi32.CryptExportKey(
                self.hkey,
                0,
                8,  # PLAINTEXTKEYBLOB
                0,
                None,
                ctypes.byref(data_len)
            )
            
            if data_len.value == 0:
                raise RuntimeError("Не удалось получить размер ключа")
            
            # Экспортируем ключ
            key_data = ctypes.create_string_buffer(data_len.value)
            result = self.crypto_provider.advapi32.CryptExportKey(
                self.hkey,
                0,
                8,  # PLAINTEXTKEYBLOB
                0,
                key_data,
                ctypes.byref(data_len)
            )
            
            if result:
                # Конвертируем в HEX
                hex_data = binascii.hexlify(key_data[:data_len.value]).decode('ascii')
                return hex_data
            else:
                error = self.crypto_provider.kernel32.GetLastError()
                raise RuntimeError(f"Ошибка экспорта ключа. Код: {error}")
                
        except Exception as e:
            raise RuntimeError(f"Ошибка экспорта ключа: {e}")
    
    def import_hex(self, hex_data):
        """Импорт ключа из HEX-формата"""
        if not self.crypto_provider.is_initialized():
            raise RuntimeError("Криптопровайдер не инициализирован")
        
        try:
            # Конвертируем из HEX в бинарные данные
            key_data = binascii.unhexlify(hex_data)
            
            # Импортируем ключ
            result = self.crypto_provider.advapi32.CryptImportKey(
                self.crypto_provider.hprov,
                key_data,
                len(key_data),
                0,
                0,
                ctypes.byref(self.hkey)
            )
            
            if result:
                # Только устанавливаем режим, но НЕ генерируем новый IV
                # IV будет установлен при первом использовании ключа или явно
                self._set_encryption_mode_only()
                self._generated = True
                return True
            else:
                error = self.crypto_provider.kernel32.GetLastError()
                raise RuntimeError(f"Ошибка импорта ключа. Код: {error}")
                
        except binascii.Error as e:
            raise RuntimeError(f"Ошибка декодирования HEX данных: {e}")
        except Exception as e:
            raise RuntimeError(f"Ошибка импорта ключа: {e}")
    
    def _set_encryption_mode_only(self):
        """Устанавливает только режим шифрования без генерации нового IV"""
        try:
            # Устанавливаем режим CBC
            mode = wintypes.DWORD(self.crypto_provider.CRYPT_MODE_CBC)
            self.crypto_provider.advapi32.CryptSetKeyParam(
                self.hkey,
                self.crypto_provider.KP_MODE,
                ctypes.byref(mode),
                0
            )
        except Exception as e:
            print(f"⚠️ Ошибка установки режима шифрования: {e}")
    
    def set_iv(self, iv_hex):
        """Явная установка IV из HEX-строки"""
        try:
            if len(iv_hex) != 32:  # 16 байт в HEX = 32 символа
                raise ValueError("IV должен быть 16 байт (32 HEX символа)")
            
            # Конвертируем HEX в бинарные данные
            iv_binary = binascii.unhexlify(iv_hex)
            self._iv = iv_binary
            
            # Устанавливаем IV
            iv_buffer = ctypes.create_string_buffer(iv_binary)
            result = self.crypto_provider.advapi32.CryptSetKeyParam(
                self.hkey,
                self.crypto_provider.KP_IV,
                iv_buffer,
                0
            )
            
            if not result:
                raise RuntimeError("Не удалось установить IV")
                
        except Exception as e:
            raise RuntimeError(f"Ошибка установки IV: {e}")
    
    def get_iv_hex(self):
        """Получение текущего IV в HEX-формате"""
        if self._iv:
            return binascii.hexlify(self._iv).decode('ascii')
        return None
    
    def encrypt_bytes(self, plaintext):
        """Шифрование бинарных данных"""
        if not self._generated:
            raise RuntimeError("Ключ не загружен или не сгенерирован")
        
        try:
            # Создаем буфер для шифрования
            buffer_size = len(plaintext) + 1024
            encrypted_buffer = ctypes.create_string_buffer(plaintext, buffer_size)
            data_len = wintypes.DWORD(len(plaintext))
            final_buffer_size = wintypes.DWORD(buffer_size)
            
            # Шифруем данные
            result = self.crypto_provider.advapi32.CryptEncrypt(
                self.hkey,
                0,  # Хэш не используется
                1,  # Final (True)
                0,  # Flags
                encrypted_buffer,
                ctypes.byref(data_len),
                final_buffer_size
            )
            
            if result:
                # Сохраняем использованный IV для возможного повторного использования
                self._save_current_iv()
                
                # Конвертируем зашифрованные данные в HEX
                encrypted_data = encrypted_buffer[:data_len.value]
                hex_data = binascii.hexlify(encrypted_data).decode('ascii')
                return hex_data
            else:
                error = self.crypto_provider.kernel32.GetLastError()
                raise RuntimeError(f"Ошибка шифрования. Код: {error}")
                
        except Exception as e:
            raise RuntimeError(f"Ошибка шифрования: {e}")
    
    def _save_current_iv(self):
        """Сохраняет текущий IV из криптоконтекста"""
        try:
            # Получаем текущий IV
            iv_size = 16
            iv_buffer = ctypes.create_string_buffer(iv_size)
            param_len = wintypes.DWORD(iv_size)
            
            result = self.crypto_provider.advapi32.CryptGetKeyParam(
                self.hkey,
                self.crypto_provider.KP_IV,
                iv_buffer,
                ctypes.byref(param_len),
                0
            )
            
            if result:
                self._iv = iv_buffer.raw[:iv_size]
        except:
            pass
    
    def decrypt_hex(self, hex_data):
        """Расшифрование HEX-данных"""
        if not self._generated:
            raise RuntimeError("Ключ не загружен или не сгенерирован")
        
        try:
            # Конвертируем из HEX в бинарные данные
            ciphertext = binascii.unhexlify(hex_data)
            
            # Создаем буфер для расшифрования
            buffer_size = len(ciphertext) + 1024
            decrypted_buffer = ctypes.create_string_buffer(ciphertext, buffer_size)
            data_len = wintypes.DWORD(len(ciphertext))
            
            # Расшифровываем данные
            result = self.crypto_provider.advapi32.CryptDecrypt(
                self.hkey,
                0,  # Хэш не используется
                1,  # Final (True)
                0,  # Flags
                decrypted_buffer,
                ctypes.byref(data_len)
            )
            
            if result:
                return decrypted_buffer[:data_len.value]
            else:
                error = self.crypto_provider.kernel32.GetLastError()
                raise RuntimeError(f"Ошибка расшифрования. Код: {error}")
                
        except binascii.Error as e:
            raise RuntimeError(f"Ошибка декодирования HEX данных: {e}")
        except Exception as e:
            raise RuntimeError(f"Ошибка расшифрования: {e}")
    
    def is_generated(self):
        """Проверка генерации ключа"""
        return self._generated
    
    def cleanup(self):
        """Очистка ресурсов ключа"""
        try:
            if self.hkey:
                self.crypto_provider.advapi32.CryptDestroyKey(self.hkey)
                self.hkey = wintypes.HANDLE()
                self._generated = False
                self._iv = None
        except:
            pass