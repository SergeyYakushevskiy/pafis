import win32api
import win32con

def enum_providers_from_registry():
    """
    Выводит список установленных криптопровайдеров, читая информацию из реестра Windows.
    """
    reg_path = r"SOFTWARE\Microsoft\Cryptography\Defaults\Provider"
    try:
        # Открываем ключ реестра с правами на чтение
        key = win32api.RegOpenKeyEx(win32con.HKEY_LOCAL_MACHINE, reg_path, 0, win32con.KEY_READ)
        index = 0
        print("Список криптопровайдеров из реестра:")
        while True:
            try:
                # Перечисляем подключи (имена провайдеров)
                prov_name = win32api.RegEnumKey(key, index)
                # Путь к подключу конкретного провайдера
                subkey_path = f"{reg_path}\\{prov_name}"
                subkey = win32api.RegOpenKeyEx(win32con.HKEY_LOCAL_MACHINE, subkey_path, 0, win32con.KEY_READ)
                
                # Пытаемся получить тип провайдера из значения "Type" в подключе
                try:
                    prov_type, _ = win32api.RegQueryValueEx(subkey, "Type")
                    print(f"  Имя: {prov_name}, Тип: {prov_type}")
                except FileNotFoundError:
                    # Значение "Type" может отсутствовать, выводим без него
                    print(f"  Имя: {prov_name}, Тип: <не указан в реестре>")
                finally:
                    win32api.RegCloseKey(subkey)

                index += 1
            except win32api.error as e:
                # ERROR_NO_MORE_ITEMS (259 / 0x103) означает конец списка подключей
                if e.winerror == 259: # ERROR_NO_MORE_ITEMS
                    if index == 0:
                        print("  Не найдено ни одного криптопровайдера в реестре.")
                    break
                else:
                    raise e # Пробрасываем другие ошибки реестра
    except FileNotFoundError:
        print(f"Ключ реестра {reg_path} не найден.")
    except Exception as e:
        print(f"Произошла ошибка при доступе к реестру: {e}")
    finally:
        try:
            win32api.RegCloseKey(key)
        except:
            pass # Игнорируем ошибку при закрытии, если key не был открыт

if __name__ == "__main__":
    enum_providers_from_registry()