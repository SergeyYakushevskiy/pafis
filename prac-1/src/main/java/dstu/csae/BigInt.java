package dstu.csae;

import java.util.Arrays;

public class BigInt {
    private byte[] digits; // массив цифр в обратном порядке (младшие разряды сначала)
    private boolean isNegative; // знак числа

    // Конструктор из строки
    public BigInt(String number) {
        if (number == null || number.isEmpty()) {
            throw new IllegalArgumentException("Number cannot be null or empty");
        }

        // Обработка знака
        int startIndex = 0;
        if (number.charAt(0) == '-') {
            isNegative = true;
            startIndex = 1;
        } else if (number.charAt(0) == '+') {
            startIndex = 1;
        }

        // Пропускаем ведущие нули
        while (startIndex < number.length() && number.charAt(startIndex) == '0') {
            startIndex++;
        }

        // Если все цифры были нулями
        if (startIndex == number.length()) {
            digits = new byte[1];
            digits[0] = 0;
            isNegative = false;
            return;
        }

        // Преобразуем строку в массив цифр
        int length = number.length() - startIndex;
        digits = new byte[length];

        for (int i = 0; i < length; i++) {
            char c = number.charAt(startIndex + i);
            if (c < '0' || c > '9') {
                throw new IllegalArgumentException("Invalid character in number: " + c);
            }
            digits[length - 1 - i] = (byte)(c - '0'); // сохраняем в обратном порядке
        }
    }

    // Конструктор из long
    public BigInt(long number) {
        this(String.valueOf(number));
    }

    // Конструктор копирования
    public BigInt(BigInt other) {
        this.digits = Arrays.copyOf(other.digits, other.digits.length);
        this.isNegative = other.isNegative;
    }

    // Конструктор из массива цифр (внутренний)
    private BigInt(byte[] digits, boolean isNegative) {
        this.digits = removeLeadingZeros(digits);
        this.isNegative = this.digits.length == 1 && this.digits[0] == 0 ? false : isNegative;
    }

    // Сложение
    public BigInt add(BigInt other) {
        // Если знаки разные, выполняем вычитание
        if (this.isNegative != other.isNegative) {
            BigInt positive = this.isNegative ? other : this;
            BigInt negative = this.isNegative ? this : other;
            negative = new BigInt(negative);
            negative.isNegative = false;
            return positive.subtract(negative);
        }

        byte[] result = new byte[Math.max(this.digits.length, other.digits.length) + 1];
        int carry = 0;

        for (int i = 0; i < result.length; i++) {
            int sum = carry;
            if (i < this.digits.length) sum += this.digits[i];
            if (i < other.digits.length) sum += other.digits[i];

            result[i] = (byte)(sum % 10);
            carry = sum / 10;
        }

        return new BigInt(result, this.isNegative);
    }

    // Вычитание
    public BigInt subtract(BigInt other) {
        // Если знаки разные, выполняем сложение
        if (this.isNegative != other.isNegative) {
            BigInt result = this.add(new BigInt(other.digits, !other.isNegative));
            return result;
        }

        // Определяем какое число больше по модулю
        int comparison = compareAbsolute(other);

        if (comparison == 0) {
            return new BigInt("0");
        }

        boolean resultNegative;
        BigInt larger, smaller;

        if (comparison > 0) {
            larger = this;
            smaller = other;
            resultNegative = this.isNegative;
        } else {
            larger = other;
            smaller = this;
            resultNegative = !this.isNegative;
        }

        byte[] result = new byte[larger.digits.length];
        int borrow = 0;

        for (int i = 0; i < larger.digits.length; i++) {
            int diff = larger.digits[i] - borrow;
            if (i < smaller.digits.length) {
                diff -= smaller.digits[i];
            }

            if (diff < 0) {
                diff += 10;
                borrow = 1;
            } else {
                borrow = 0;
            }

            result[i] = (byte)diff;
        }

        return new BigInt(result, resultNegative);
    }

    // Сравнение по модулю
    private int compareAbsolute(BigInt other) {
        if (this.digits.length != other.digits.length) {
            return Integer.compare(this.digits.length, other.digits.length);
        }

        for (int i = this.digits.length - 1; i >= 0; i--) {
            if (this.digits[i] != other.digits[i]) {
                return Byte.compare(this.digits[i], other.digits[i]);
            }
        }

        return 0;
    }

    // Проверка на ноль
    private boolean isZero() {
        return digits.length == 1 && digits[0] == 0;
    }

    // Деление на 2 с остатком (для двоичного представления)
    private BigInt[] divideByTwo() {
        byte[] quotient = new byte[digits.length];
        int remainder = 0;

        for (int i = digits.length - 1; i >= 0; i--) {
            int current = remainder * 10 + digits[i];
            quotient[i] = (byte)(current / 2);
            remainder = current % 2;
        }

        return new BigInt[] {
                new BigInt(removeLeadingZeros(quotient), false),
                new BigInt(new byte[]{(byte)remainder}, false)
        };
    }

    // Удаление ведущих нулей
    private byte[] removeLeadingZeros(byte[] arr) {
        int firstNonZero = arr.length - 1;
        while (firstNonZero >= 0 && arr[firstNonZero] == 0) {
            firstNonZero--;
        }

        if (firstNonZero < 0) {
            return new byte[]{0};
        }

        return Arrays.copyOfRange(arr, 0, firstNonZero + 1);
    }

    // Геттеры для тестирования
    public byte[] getDigits() {
        return Arrays.copyOf(digits, digits.length);
    }

    public boolean isNegative() {
        return isNegative;
    }

    // Вывод в десятичном формате
    @Override
    public String toString() {
        if (digits.length == 1 && digits[0] == 0) {
            return "0";
        }

        StringBuilder sb = new StringBuilder();
        if (isNegative) {
            sb.append('-');
        }

        for (int i = digits.length - 1; i >= 0; i--) {
            sb.append(digits[i]);
        }

        return sb.toString();
    }

    // Вывод в двоичном формате
    public String toBinaryString() {
        if (digits.length == 1 && digits[0] == 0) {
            return "0";
        }

        StringBuilder binary = new StringBuilder();
        BigInt temp = new BigInt(this);
        temp.isNegative = false; // работаем с модулем

        while (!temp.isZero()) {
            BigInt[] divResult = temp.divideByTwo();
            binary.insert(0, divResult[1].digits[0]); // остаток (0 или 1)
            temp = divResult[0]; // частное
        }

        if (isNegative) {
            binary.insert(0, '-');
        }

        return binary.toString();
    }

}