package dstu.csae.pafis.generator;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

public class Main {

    public static final int PRN_COUNT = 15625;
    public static final String SEPARATOR = File.separator;
    public static final List<String> DEFAULT_PATH = List.of(
            System.getProperty("user.dir"),
            "lab3",
            "src",
            "main",
            "resources",
            "sts-2.1.2",
            "experiments",
            "AlgorithmTesting"
    );
    public static final String FILE_NAME = "data.00001";

    public static void main(String[] args) {
        System.out.println("Выполняется генерация чисел...");
        List<Long> numbers = IntStream.range(0, PRN_COUNT)
                .mapToObj(x -> AesCtrGenerator.nextLong())
                .toList();
        System.out.printf("Готово! Числа: %s\n", numbers.stream()
                .map(String::valueOf)
                .collect(Collectors.joining(", "))
        );
        String path = String.join(SEPARATOR, DEFAULT_PATH) + SEPARATOR + FILE_NAME;
        String sequence = numbers.stream()
                .map(Long::toBinaryString)
                .map(x -> String.format("%64s", x).replaceAll(" ","0"))
                .collect(Collectors.joining(""));
        try(FileWriter writer = new FileWriter(path)){
            writer.write(sequence);
            writer.flush();
            System.out.println("Значения успешно записаны в файл: " + path);
        } catch (IOException e) {
            System.out.println("Ошибка: " + e.getMessage());
        }
    }

}
