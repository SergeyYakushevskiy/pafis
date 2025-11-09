package dstu.csae.pafis.lab4.test;

import dstu.csae.pafis.lab4.utils.Complex;
import java.util.ArrayList;
import java.util.List;

public class SpectralTest {

    /**
     * Длина блока для спектрального теста (степень двойки)
     */
    private static final int BLOCK_SIZE = 1024; // 2^10

    /**
     * Проверяет битовую строку на случайность с помощью спектрального теста.
     * Разбивает последовательность на блоки и усредняет результаты.
     *
     * @param sequence строка из '0' и '1'
     * @return p-value
     */
    public static double test(String sequence) {
        int n = sequence.length();

        // Разбиваем последовательность на блоки
        List<String> blocks = splitIntoBlocks(sequence);

        if (blocks.isEmpty()) {
            System.err.println("Нет подходящих блоков для анализа. Минимальная длина: " + BLOCK_SIZE);
            return 0.0;
        }

        System.out.println("Общая длина последовательности: " + n);
        System.out.println("Размер блока: " + BLOCK_SIZE);
        System.out.println("Количество блоков: " + blocks.size());
        System.out.println("Обработано битов: " + (blocks.size() * BLOCK_SIZE));
        System.out.println("Отброшено битов: " + (n - blocks.size() * BLOCK_SIZE));

        // Выполняем тест для каждого блока и собираем результаты
        List<Double> pValues = new ArrayList<>();
        List<Double> chiSquares = new ArrayList<>();

        for (int i = 0; i < blocks.size(); i++) {
            System.out.println("\n--- Обработка блока " + (i + 1) + " ---");
            BlockResult result = processBlock(blocks.get(i));
            pValues.add(result.pValue);
            chiSquares.add(result.chiSquare);
        }

        // Усредняем результаты по всем блокам
        return calculateOverallPValue(pValues, chiSquares);
    }

    /**
     * Разбивает последовательность на блоки заданного размера.
     * Последний неполный блок отбрасывается.
     */
    private static List<String> splitIntoBlocks(String sequence) {
        List<String> blocks = new ArrayList<>();
        int totalBlocks = sequence.length() / BLOCK_SIZE;

        for (int i = 0; i < totalBlocks; i++) {
            int start = i * BLOCK_SIZE;
            int end = start + BLOCK_SIZE;
            blocks.add(sequence.substring(start, end));
        }

        return blocks;
    }

    /**
     * Обрабатывает один блок последовательности.
     */
    private static BlockResult processBlock(String block) {
        int n = BLOCK_SIZE;

        // Преобразуем биты в последовательность {-1, +1}
        double[] x = new double[n];
        for (int i = 0; i < n; i++) {
            x[i] = (block.charAt(i) == '1') ? 1.0 : -1.0;
        }

        // Применяем FFT
        Complex[] X = fft(x);

        // Вычисляем модули (амплитуды) для первых n/2 значений
        double[] m = new double[n / 2];
        for (int i = 0; i < n / 2; i++) {
            m[i] = X[i].abs();
        }

        // Порог (95% порог для нормального распределения)
        double threshold = Math.sqrt(2.995732273554 * n);
        System.out.println("Порог: " + threshold);

        // Считаем количество значений выше порога
        int count = 0;
        for (double mi : m) {
            if (mi > threshold) {
                count++;
            }
        }

        System.out.println("Количество амплитуд выше порога: " + count);

        // Ожидаемое количество (95% доверительный интервал)
        double expected = 0.05 * (n / 2.0);
        System.out.println("Ожидаемое количество: " + expected);

        // Вычисляем chi-square
        double chiSquare = Math.pow(count - expected, 2) / expected;
        System.out.println("Chi-square: " + chiSquare);

        // P-value используя гамма-функцию для распределения хи-квадрат
        double pValue = 1.0 - gammaRegularized(0.5, chiSquare / 2.0);
        System.out.println("P-value: " + pValue);

        return new BlockResult(pValue, chiSquare);
    }

    /**
     * Вычисляет общий p-value на основе результатов всех блоков.
     */
    private static double calculateOverallPValue(List<Double> pValues, List<Double> chiSquares) {
        // Метод Фишера для объединения p-values
        double fisherStatistic = 0.0;
        for (double pValue : pValues) {
            fisherStatistic += Math.log(pValue);
        }
        fisherStatistic *= -2;

        int degreesOfFreedom = 2 * pValues.size();
        double combinedPValue = 1.0 - gammaRegularized(degreesOfFreedom / 2.0, fisherStatistic / 2.0);

        System.out.println("\n=== ОБЩИЕ РЕЗУЛЬТАТЫ ===");
        System.out.println("Количество блоков: " + pValues.size());
        System.out.println("Объединенный p-value: " + combinedPValue);

        return combinedPValue;
    }

    /**
     * Вспомогательный класс для хранения результатов блока
     */
    private static class BlockResult {
        double pValue;
        double chiSquare;

        BlockResult(double pValue, double chiSquare) {
            this.pValue = pValue;
            this.chiSquare = chiSquare;
        }
    }

    // Регуляризованная неполная гамма-функция
    private static double gammaRegularized(double a, double x) {
        return gammaIncomplete(a, x) / gamma(a);
    }

    // Неполная гамма-функция
    private static double gammaIncomplete(double a, double x) {
        return gammaIncompleteSeries(a, x);
    }

    // Ряд для неполной гамма-функции
    private static double gammaIncompleteSeries(double a, double x) {
        if (x < 0.0) return 0.0;
        if (x == 0.0) return 0.0;

        double sum = 0.0;
        double term = 1.0 / a;
        double n = 0;

        while (Math.abs(term) > 1e-12 && n < 1000) {
            sum += term;
            n += 1;
            term = term * x / (a + n);
        }

        return sum * Math.pow(x, a) * Math.exp(-x);
    }

    // Гамма-функция
    private static double gamma(double x) {
        // Аппроксимация Ланцоша
        double[] p = {676.5203681218851, -1259.1392167224028, 771.32342877765313,
                -176.61502916214059, 12.507343278686905, -0.13857109526572012,
                9.9843695780195716e-6, 1.5056327351493116e-7};

        if (x < 0.5) {
            return Math.PI / (Math.sin(Math.PI * x) * gamma(1 - x));
        }

        x -= 1;
        double t = 0.99999999999980993;
        for (int i = 0; i < p.length; i++) {
            t += p[i] / (x + i + 1);
        }

        double w = x + p.length - 0.5;
        return Math.sqrt(2 * Math.PI) * Math.pow(w, x + 0.5) * Math.exp(-w) * t;
    }

    // Реализация FFT (Cooley-Tukey)
    private static Complex[] fft(double[] input) {
        int n = input.length;

        // Проверка степени двойки
        if ((n & (n - 1)) != 0) {
            throw new IllegalArgumentException("Размер должен быть степенью двойки");
        }

        Complex[] x = new Complex[n];
        for (int i = 0; i < n; i++) {
            x[i] = new Complex(input[i], 0);
        }

        return fftRecursive(x);
    }

    private static Complex[] fftRecursive(Complex[] x) {
        int n = x.length;

        if (n <= 1) {
            return x;
        }

        // Разделение на четные и нечетные
        Complex[] even = new Complex[n / 2];
        Complex[] odd = new Complex[n / 2];
        for (int i = 0; i < n / 2; i++) {
            even[i] = x[2 * i];
            odd[i] = x[2 * i + 1];
        }

        // Рекурсивный вызов
        even = fftRecursive(even);
        odd = fftRecursive(odd);

        // Объединение
        Complex[] result = new Complex[n];
        for (int i = 0; i < n / 2; i++) {
            double k = -2 * Math.PI * i / n;
            Complex w = new Complex(Math.cos(k), Math.sin(k));
            w = w.multiply(odd[i]);
            result[i] = even[i].add(w);
            result[i + n / 2] = even[i].subtract(w);
        }

        return result;
    }

    // Комплиментарная функция ошибок (для вычисления p-value)
    private static double erfc(double x) {
        return 1.0 - erf(x);
    }

    // Функция ошибок (аппроксимация)
    private static double erf(double x) {
        // sign
        int sign = x < 0 ? -1 : 1;
        x = Math.abs(x);

        // constants
        double a1 = 0.254829592;
        double a2 = -0.284496736;
        double a3 = 1.421413741;
        double a4 = -1.453152027;
        double a5 = 1.061405429;
        double p = 0.3275911;

        double t = 1.0 / (1.0 + p * x);
        double y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * Math.exp(-x * x);

        return sign * y;
    }
}