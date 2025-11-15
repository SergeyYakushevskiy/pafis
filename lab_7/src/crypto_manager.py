import ctypes
from ctypes import wintypes
import binascii

class AsymmetricCryptoProviderManager:
    """Управление криптопровайдером Windows CryptoAPI для асимметричного шифрования"""
    
    # Константы CryptoAPI
    PROV_RSA_FULL = 1
    PROV_RSA_AES = 24
    MS_ENH_RSA_AES_PROV = "Microsoft Enhanced RSA and AES Cryptographic Provider"
    CRYPT_NEWKEYSET = 0x00000008
    CRYPT_EXPORTABLE = 0x00000001
    AT_KEYEXCHANGE = 1
    AT_SIGNATURE = 2
    CALG_RSA_KEYX = 0x0000A400
    CALG_RSA_SIGN = 0x00002400
    SIMPLEBLOB = 1
    PUBLICKEYBLOB = 6
    PRIVATEKEYBLOB = 7
    RSA1024BIT_KEY = 0x04000000
    RSA2048BIT_KEY = 0x08000000
    
    def __init__(self):
        self.advapi32 = ctypes.windll.advapi32
        self.kernel32 = ctypes.windll.kernel32
        self.hprov = wintypes.HANDLE()
        self.container_name = "AsymmetricPythonCryptoContainer"
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
            print(f"Ошибка инициализации провайдера: {e}")
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


class RSAKeyPair:
    """Управление парой RSA ключей"""
    
    def __init__(self, crypto_provider):
        self.crypto_provider = crypto_provider
        self.hkey = wintypes.HANDLE()
        self._generated = False
        self.key_size = 2048  # Размер ключа по умолчанию
    
    def generate(self, key_size=2048):
        """Генерация новой пары RSA ключей"""
        if not self.crypto_provider.is_initialized():
            raise RuntimeError("Криптопровайдер не инициализирован")
        
        self.key_size = key_size
        
        try:
            # Определяем флаги в зависимости от размера ключа
            key_flags = self.crypto_provider.CRYPT_EXPORTABLE
            if key_size == 1024:
                key_flags |= self.crypto_provider.RSA1024BIT_KEY
            elif key_size == 2048:
                key_flags |= self.crypto_provider.RSA2048BIT_KEY
            
            # Генерируем пару ключей
            result = self.crypto_provider.advapi32.CryptGenKey(
                self.crypto_provider.hprov,
                self.crypto_provider.CALG_RSA_KEYX,
                key_flags,
                ctypes.byref(self.hkey)
            )
            
            if result:
                self._generated = True
                return True
            else:
                error = self.crypto_provider.kernel32.GetLastError()
                raise RuntimeError(f"Ошибка генерации RSA ключей. Код: {error}")
                
        except Exception as e:
            raise RuntimeError(f"Ошибка генерации RSA ключей: {e}")
    
    def export_public_key_hex(self):
        """Экспорт публичного ключа в HEX-формате"""
        if not self._generated:
            raise RuntimeError("Ключи не сгенерированы")
        
        try:
            # Получаем размер данных публичного ключа
            data_len = wintypes.DWORD(0)
            self.crypto_provider.advapi32.CryptExportKey(
                self.hkey,
                0,
                self.crypto_provider.PUBLICKEYBLOB,
                0,
                None,
                ctypes.byref(data_len)
            )
            
            if data_len.value == 0:
                raise RuntimeError("Не удалось получить размер публичного ключа")
            
            # Экспортируем публичный ключ
            key_data = ctypes.create_string_buffer(data_len.value)
            result = self.crypto_provider.advapi32.CryptExportKey(
                self.hkey,
                0,
                self.crypto_provider.PUBLICKEYBLOB,
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
                raise RuntimeError(f"Ошибка экспорта публичного ключа. Код: {error}")
                
        except Exception as e:
            raise RuntimeError(f"Ошибка экспорта публичного ключа: {e}")
    
    def export_private_key_hex(self):
        """Экспорт приватного ключа в HEX-формате"""
        if not self._generated:
            raise RuntimeError("Ключи не сгенерированы")
        
        try:
            # Получаем размер данных приватного ключа
            data_len = wintypes.DWORD(0)
            self.crypto_provider.advapi32.CryptExportKey(
                self.hkey,
                0,
                self.crypto_provider.PRIVATEKEYBLOB,
                0,
                None,
                ctypes.byref(data_len)
            )
            
            if data_len.value == 0:
                raise RuntimeError("Не удалось получить размер приватного ключа")
            
            # Экспортируем приватный ключ
            key_data = ctypes.create_string_buffer(data_len.value)
            result = self.crypto_provider.advapi32.CryptExportKey(
                self.hkey,
                0,
                self.crypto_provider.PRIVATEKEYBLOB,
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
                raise RuntimeError(f"Ошибка экспорта приватного ключа. Код: {error}")
                
        except Exception as e:
            raise RuntimeError(f"Ошибка экспорта приватного ключа: {e}")
    
    def import_public_key_hex(self, hex_data):
        """Импорт публичного ключа из HEX-формата"""
        if not self.crypto_provider.is_initialized():
            raise RuntimeError("Криптопровайдер не инициализирован")
        
        try:
            # Конвертируем из HEX в бинарные данные
            key_data = binascii.unhexlify(hex_data)
            
            # Импортируем публичный ключ
            result = self.crypto_provider.advapi32.CryptImportKey(
                self.crypto_provider.hprov,
                key_data,
                len(key_data),
                0,
                0,
                ctypes.byref(self.hkey)
            )
            
            if result:
                self._generated = True
                # Определяем размер ключа на основе размера данных
                self.key_size = 2048 if len(key_data) > 300 else 1024
                return True
            else:
                error = self.crypto_provider.kernel32.GetLastError()
                raise RuntimeError(f"Ошибка импорта публичного ключа. Код: {error}")
                
        except binascii.Error as e:
            raise RuntimeError(f"Ошибка декодирования HEX данных: {e}")
        except Exception as e:
            raise RuntimeError(f"Ошибка импорта публичного ключа: {e}")
    
    def import_private_key_hex(self, hex_data):
        """Импорт приватного ключа из HEX-формата"""
        if not self.crypto_provider.is_initialized():
            raise RuntimeError("Криптопровайдер не инициализирован")
        
        try:
            # Конвертируем из HEX в бинарные данные
            key_data = binascii.unhexlify(hex_data)
            
            # Импортируем приватный ключ
            result = self.crypto_provider.advapi32.CryptImportKey(
                self.crypto_provider.hprov,
                key_data,
                len(key_data),
                0,
                0,
                ctypes.byref(self.hkey)
            )
            
            if result:
                self._generated = True
                # Определяем размер ключа на основе размера данных
                self.key_size = 2048 if len(key_data) > 1000 else 1024
                return True
            else:
                error = self.crypto_provider.kernel32.GetLastError()
                raise RuntimeError(f"Ошибка импорта приватного ключа. Код: {error}")
                
        except binascii.Error as e:
            raise RuntimeError(f"Ошибка декодирования HEX данных: {e}")
        except Exception as e:
            raise RuntimeError(f"Ошибка импорта приватного ключа: {e}")
    
    def encrypt_bytes(self, plaintext):
        """Шифрование данных публичным ключом"""
        if not self._generated:
            raise RuntimeError("Ключ не загружен или не сгенерирован")
        
        try:
            # Для RSA шифруем данные блоками
            # Максимальный размер блока зависит от размера ключа
            max_block_size = (self.key_size // 8) - 11  # PKCS#1 padding
            
            if len(plaintext) > max_block_size:
                raise RuntimeError(f"Данные слишком большие для RSA шифрования. Максимум: {max_block_size} байт")
            
            # Создаем буфер для шифрования
            buffer_size = self.key_size // 8  # Размер зашифрованного блока
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
                # Конвертируем зашифрованные данные в HEX
                encrypted_data = encrypted_buffer[:final_buffer_size.value]
                hex_data = binascii.hexlify(encrypted_data).decode('ascii')
                return hex_data
            else:
                error = self.crypto_provider.kernel32.GetLastError()
                raise RuntimeError(f"Ошибка шифрования. Код: {error}")
                
        except Exception as e:
            raise RuntimeError(f"Ошибка шифрования: {e}")
    
    def decrypt_hex(self, hex_data):
        """Расшифрование данных приватным ключом"""
        if not self._generated:
            raise RuntimeError("Ключ не загружен или не сгенерирован")
        
        try:
            # Конвертируем из HEX в бинарные данные
            ciphertext = binascii.unhexlify(hex_data)
            
            # Создаем буфер для расшифрования
            buffer_size = len(ciphertext)
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
    
    def get_max_encrypt_size(self):
        """Получение максимального размера данных для шифрования"""
        if not self._generated:
            return 0
        return (self.key_size // 8) - 11  # PKCS#1 padding
    
    def is_generated(self):
        """Проверка генерации ключей"""
        return self._generated
    
    def get_key_size(self):
        """Получение размера ключа"""
        return self.key_size if self._generated else 0
    
    def cleanup(self):
        """Очистка ресурсов ключа"""
        try:
            if self.hkey:
                self.crypto_provider.advapi32.CryptDestroyKey(self.hkey)
                self.hkey = wintypes.HANDLE()
                self._generated = False
                self.key_size = 2048
        except:
            pass