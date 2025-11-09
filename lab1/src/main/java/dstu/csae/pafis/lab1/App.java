package dstu.csae.pafis.lab1;

import dstu.csae.pafis.lab1.cipher.RSA;
import dstu.csae.pafis.lab1.converter.StringConverter;
import dstu.csae.pafis.lab1.utils.NumberOperator;

import java.io.*;
import java.math.BigInteger;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Scanner;
import java.util.stream.Collectors;

public class App {

    public static final Scanner SCANNER = new Scanner(System.in);
    public static final int RSA_BIT_COUNT = 512;

    public static final String DEFAULT_PATH = System.getProperty("user.home");

    public static final String[] KEY_INIT_MODES = {
            "1. Генерация пары ключей",
            "2. Задание пары ключей вручную"
    };
    public static final String[] TEXT_INPUT_MODES = {
            "1. Ввод текста вручную",
            "2. Считать текст из файла"
    };
    public static final String[] APP_MODES = {
            "1. Зашифровать текст",
            "2. Расшифровать текст"
    };

    public static void main(String[] args) {
        System.out.println("""
                === ЛАБОРАТОРНАЯ РАБОТА № 1 ===
                Реализация шифрования алгоритмом RSA
                """);
        int keyInitMode = getMode(KEY_INIT_MODES);
        RSA rsa = null;
        do {
            switch (keyInitMode) {
                case 1 -> {
                    BigInteger p = NumberOperator.nextPrimeBigInt(RSA_BIT_COUNT);
                    BigInteger q = NumberOperator.nextPrimeBigInt(RSA_BIT_COUNT);
                    BigInteger m = p.subtract(BigInteger.ONE).multiply(q.subtract(BigInteger.ONE));
                    BigInteger e = NumberOperator.nextPrimeBigInt(RSA_BIT_COUNT, BigInteger.TWO, m);
                    rsa = new RSA(p, q, e);
                    BigInteger d = rsa.getD();
                    System.out.println(rsa);
                    saveData(DEFAULT_PATH + "/public.key", e.toString(2), p.toString(2), q.toString(2));
                    saveData(DEFAULT_PATH + "/private.key", d.toString(2), p.toString(2), q.toString(2));
                }
                case 2 -> {
                    String publicKeyPath = "";
                    String privateKeyPath = "";
                    do {
                        System.out.print("Введите путь к файлу с открытым ключом: ");
                        publicKeyPath = SCANNER.next();
                    } while (publicKeyPath.isBlank());
                    do {
                        System.out.print("Введите путь к файлу с закрытым ключом: ");
                        privateKeyPath = SCANNER.next();
                    } while (privateKeyPath.isBlank());
                    List<BigInteger> values = initData(publicKeyPath);
                    BigInteger e = values.get(0);
                    BigInteger p = values.get(1);
                    BigInteger q = values.get(2);
                    values = initData(privateKeyPath);
                    BigInteger d = values.get(0);
                    rsa = new RSA(p, q, e);
                    System.out.println(rsa);
                }
                default -> System.out.println("Ошибка при выборе режима задания алгоритма");
            }
        }while (rsa == null);

        int inputTextMode = getMode(TEXT_INPUT_MODES);
        String text;
        if (SCANNER.hasNextLine()) {
            SCANNER.nextLine();
        }
        do{
            switch (inputTextMode) {
                case 1 -> {
                    System.out.print("Введите текст: ");
                    text = SCANNER.nextLine();
                    if(text.isBlank()){
                        System.out.println("Пустая строка. Повторите попытку.");
                    }
                    saveData(DEFAULT_PATH + "/" + "text.txt", text);
                }
                case 2 -> {
                    System.out.print("Введите путь к тексту: ");
                    String textPath = SCANNER.nextLine();
                    text = getText(textPath);
                    System.out.printf("Текст: %s\n", text);
                }
                default -> {
                    System.out.println("Ошибка при выборе режима ввода текста");
                    text = "";
                }
            }
        }while (text.isBlank());

        int appMode = getMode(APP_MODES);
        if(SCANNER.hasNextLine()){
            SCANNER.nextLine();
        }
        switch (appMode){
            case 1 -> {
                ArrayList<BigInteger> converted = StringConverter.toBigInt(text);
                ArrayList<BigInteger> encryptedList = new ArrayList<>(
                        converted.stream()
                        .map(rsa::encrypt)
                        .toList()
                );
                String encrypted = StringConverter.toString(encryptedList);
                System.out.printf("Шифртекст: %s\n", encrypted);
                saveData(DEFAULT_PATH + "/encryptedtext.txt",
                        encryptedList.stream()
                        .map(BigInteger::toString)
                        .collect(Collectors.joining(", ")
                        ));
            }
            case 2 -> {
                ArrayList<BigInteger> converted = StringConverter.toBigInt(text.split(", "));
                ArrayList<BigInteger> decryptedList = new ArrayList<>(
                    converted.stream()
                            .map(rsa::decrypt)
                            .toList()
                );
                String decrypted = StringConverter.toString(decryptedList);
                System.out.printf("Открытый текст: %s\n", decrypted);
                saveData(DEFAULT_PATH + "/plaintext.txt", decrypted);
            }
        }
    }

    public static int getMode(String ... options){
        if(options.length < 2){
            throw new IllegalArgumentException("Число режимов работы должно быть не меньше 2");
        }
        Arrays.stream(options).forEach(System.out::println);
        int mode = 0;
        do{
            try{
                System.out.print("Введите номер необходимого режима работы: ");
                 mode = SCANNER.nextInt();
            }catch (NumberFormatException ex){
                System.out.println("Повторите попытку.");
            }
        }while((0 < mode - 1) && (mode - 1 >= options.length));
        return mode;
    }

    public static List<BigInteger> initData(String path){
        List<BigInteger> values = new ArrayList<>();
        try(BufferedReader reader = new BufferedReader(new FileReader(path))){
            String line;
            while((line = reader.readLine()) != null){
                BigInteger value = new BigInteger(line, 2);
                values.add(value);
            }
        } catch (IOException e) {
            System.out.println("Ошибка: " + e.getMessage());
        }
        return values;
    }

    public static void saveData(String path, String ... values){
        try(FileWriter writer = new FileWriter(path)){
            String writable = String.join("\n", values);
            writer.write(writable);
            writer.flush();
            System.out.println("Данные успешно сохранены в файл: " + path);
        }catch (IOException ex){
            System.out.println("Ошибка при сохранении данных: " + ex.getMessage());
        }
    }

    public static String getText(String path){
        List<String> lines = new ArrayList<>();
        try(BufferedReader reader = new BufferedReader(new FileReader(path))){
            lines = reader.lines().toList();
        } catch (IOException e) {
            System.out.println("Ошибка: " + e.getMessage());
        }
        return String.join("\n", lines);
    }
}
