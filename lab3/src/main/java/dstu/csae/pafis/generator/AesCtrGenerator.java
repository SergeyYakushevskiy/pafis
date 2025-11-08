package dstu.csae.pafis.generator;

import javax.crypto.Cipher;
import javax.crypto.spec.SecretKeySpec;
import javax.crypto.spec.IvParameterSpec;
import java.security.SecureRandom;

/**
 * Статический класс для генерации криптографически безопасных
 * псевдослучайных чисел с использованием AES в режиме CTR.
 * Использует внутренний 128-битный буфер, обновляемый при необходимости.
 */
public final class AesCtrGenerator {

    private static final String ALGORITHM = "AES";
    private static final String TRANSFORMATION = "AES/CTR/NoPadding";

    private static byte[] key = new byte[16]; // 128-битный ключ по умолчанию
    private static byte[] iv = new byte[16];  // 128-битный IV/Nonce
    private static Cipher cipher;
    private static byte[] keystreamBuffer = new byte[16]; // Буфер для одного блока AES
    private static int keystreamIndex = 16; // Индекс в буфере. 16 означает "буфер пуст"

    static {
        // Инициализация с безопасным случайным ключом и IV
        reseed();
        try {
            cipher = Cipher.getInstance(TRANSFORMATION);
        } catch (Exception e) {
            throw new RuntimeException("Не удалось инициализировать AES/CTR", e);
        }
    }

    private AesCtrGenerator() {
        // Запретить создание экземпляров
    }

    /**
     * Перезапускает генератор с новым случайным ключом и IV.
     * Должен вызываться при инициализации и, при необходимости, периодически.
     */
    public static void reseed() {
        SecureRandom random = new SecureRandom();
        random.nextBytes(key);
        random.nextBytes(iv);
        keystreamIndex = 16; // Сброс индекса, чтобы сгенерировать новый блок при следующем обращении
    }

    /**
     * Обновляет внутренний буфер зашифрованным значением текущего счётчика.
     */
    private static void generateKeystreamBlock() throws RuntimeException {
        try {
            IvParameterSpec ivSpec = new IvParameterSpec(iv);
            SecretKeySpec keySpec = new SecretKeySpec(key, ALGORITHM);
            cipher.init(Cipher.ENCRYPT_MODE, keySpec, ivSpec);
            // Шифруем текущее значение IV как блок счётчика
            cipher.doFinal(iv, 0, iv.length, keystreamBuffer, 0);
            keystreamIndex = 0;

            // Увеличиваем счётчик (IV) на 1 (работа с байтами как с big-endian числом)
            for (int i = iv.length - 1; i >= 0; i--) {
                iv[i]++;
                if (iv[i] != 0) { // Если не было переполнения
                    break;
                }
                // Иначе переполнение, переходим к следующему байту
            }
        } catch (Exception e) {
            throw new RuntimeException("Ошибка при генерации блока AES-CTR", e);
        }
    }

    /**
     * Возвращает следующий псевдослучайный бит (0 или 1).
     * @return 0 или 1
     */
    public static byte nextBit() {
        if (keystreamIndex == 16) {
            generateKeystreamBlock();
        }
        byte b = keystreamBuffer[keystreamIndex];
        // Извлекаем бит, начиная с младшего (LSB)
        byte bit = (byte) (b & 0x01);
        // Сдвигаем внутренний индекс бита в байте
        // Для оптимизации можно использовать отдельный индекс бита,
        // но для простоты и близости к байтовому интерфейсу
        // будем вызывать nextByte и брать бит оттуда.
        // Перепишем логику: nextBit будет использовать байт целиком.
        // Правильная реализация: отдельный индекс бита.
        // Введем статическую переменную для индекса бита в байте.
        // Или, проще: генерируем байт, возвращаем его биты по одному.
        // Ниже приведена переработанная версия с внутренним байтом и индексом бита.
        // Эта версия сначала возвращает nextByte, а затем nextBit на его основе.
        // Но для чистоты реализации, перепишем nextBit напрямую.
        // --- Переписанная версия ---
        // Статические переменные для состояния бита
        if (bitIndexInByte == 8) {
            currentByte = nextByte(); // Получаем новый байт
            bitIndexInByte = 0;       // Сбрасываем индекс бита
        }
        byte bitValue = (byte) ((currentByte >> bitIndexInByte) & 0x01);
        bitIndexInByte++;
        return bitValue;
    }

    // --- Добавлены статические переменные для nextBit ---
    private static byte currentByte = 0;
    private static int bitIndexInByte = 8; // 8 означает "новый байт нужен"
    // ----------------------------------------------

    /**
     * Возвращает следующий псевдослучайный байт.
     * @return Случайный байт.
     */
    public static byte nextByte() {
        if (keystreamIndex == 16) {
            generateKeystreamBlock();
        }
        byte b = keystreamBuffer[keystreamIndex];
        keystreamIndex++;
        return b;
    }

    /**
     * Возвращает следующее 32-битное псевдослучайное целое число со знаком.
     * @return Случайное 32-битное целое число.
     */
    public static int nextInt() {
        int result = 0;
        for (int i = 0; i < 4; i++) {
            result = (result << 8) | (nextByte() & 0xFF);
        }
        return result;
    }

    /**
     * Возвращает следующее 64-битное псевдослучайное целое число со знаком.
     * @return Случайное 64-битное целое число.
     */
    public static long nextLong() { // Исправлено на nextLong, а не nextLog
        long result = 0;
        for (int i = 0; i < 8; i++) {
            result = (result << 8) | (nextByte() & 0xFF);
        }
        return result;
    }
}