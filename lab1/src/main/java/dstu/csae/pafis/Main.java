package dstu.csae.pafis;

import dstu.csae.pafis.cipher.RSA;
import dstu.csae.pafis.converter.StringConverter;
import dstu.csae.topg.prime.PrimeNumberOperator;

import java.math.BigInteger;
import java.util.ArrayList;
import java.util.Scanner;
import java.util.stream.Collectors;

public class Main {
    public static final String RETRY = "Повторите попытку ввода";
    public static final int MIN_KEY_BIT_COUNT = 1024;
    public static final int MIN_PRIME_BIT_COUNT = 1024;
    public static final String DEFAULT_USER_PATH = System.getProperty("user.home");


    public static RSA rsa;

    public static void main(String[] args) {
        String QUERY = "1. Генерация модуля n и числа e\n" +
                "2. Ввод чисел n и e вручную\n" +
                "Введите номер выбранного режима: ";
        boolean mode = setMode(QUERY);
        BigInteger p = !mode ? inputNumber("p") : generatePrime();
        BigInteger q = !mode ? inputNumber("q") : generatePrime();
        BigInteger n = p.multiply(q);
        BigInteger m = p.subtract(BigInteger.ONE).multiply(q.subtract(BigInteger.ONE));
        System.out.println("p = " + p);
        System.out.println("q = " + q);
        System.out.println("n = p * q = " + n);
        System.out.println("φ(n) = " + m);
        BigInteger e = !mode ?
                inputNumber("e", BigInteger.TWO, m) :
                generatePrime(BigInteger.TWO, m);
        RSA.setMinKeyBitCount(MIN_KEY_BIT_COUNT);
        rsa = new RSA(p, q, e);
        System.out.println(rsa);
        QUERY = "1. Зашифровать\n" +
                "2. Расшифровать\n" +
                "Введите номер нужной операции: ";
        boolean state = setMode(QUERY);
        String text = getText();
        String out = state ? "Шифртекст: " : "Открытый текст: ";
        ArrayList<BigInteger> bigIntegers = state ?
                StringConverter.toBigInt(text) :
                StringConverter.toBigInt(text.split(", "));
        bigIntegers = state ? encrypt(bigIntegers) : decrypt(bigIntegers);
        out += StringConverter.toString(bigIntegers);
        System.out.println(out);
        System.out.println(bigIntegers.stream()
                .map(BigInteger::toString)
                .collect(Collectors.joining(", ")));
    }

    public static String getText(){
        String text = "";
        Scanner scanner = new Scanner(System.in);
        while (text.isBlank()){
            System.out.print("Введите текст: ");
            text = scanner.nextLine();
        }
        return text;
    }

    public static boolean setMode(String query){
        Boolean mode = null;
        Scanner scanner = new Scanner(System.in);
        while (mode == null){
            System.out.print(query);
            try{
                int m = Integer.parseInt(scanner.nextLine());
                if(m < 1 || m > 2){
                    System.out.println(RETRY);
                    continue;
                }
                mode = m == 1;
            }catch (NumberFormatException ex){
                System.out.println(ex.getMessage());
                System.out.println(RETRY);
            }
        }
        return mode;
    }

    public static ArrayList<BigInteger> encrypt(ArrayList<BigInteger> plaintext){
        return plaintext.stream()
                .map(rsa::encrypt)
                .collect(Collectors.toCollection(ArrayList::new));
    }

    public static ArrayList<BigInteger> decrypt(ArrayList<BigInteger> ciphertext){
        return ciphertext.stream()
                .map(rsa::decrypt)
                .collect(Collectors.toCollection(ArrayList::new));
    }

    public static BigInteger generatePrime(BigInteger origin, BigInteger bound){
        return PrimeNumberOperator.nextBigInt(MIN_KEY_BIT_COUNT, origin, bound);
    }

    public static BigInteger generatePrime(){
        return PrimeNumberOperator.nextBigInt(MIN_PRIME_BIT_COUNT);
    }

    public static BigInteger inputNumber(String numberName, BigInteger origin, BigInteger bound){
        BigInteger out = null;
        while (out == null){
            out = inputNumber(numberName);
            if(out.compareTo(origin) < 0 || out.compareTo(bound) >= 0){
                System.out.println("Значение не входит в диапазон допустимых параметров");
                System.out.println(RETRY);
                out = null;
            }
        }
        return out;
    }

    public static BigInteger inputNumber(String numberName){
        String QUERY = String.format("Введите значение %s: ", numberName);
        Scanner scanner = new Scanner(System.in);
        BigInteger number = null;
        while (number == null ){
            System.out.print(QUERY);
            try{
                number = new BigInteger(scanner.nextLine());
                if(!PrimeNumberOperator.isProbablePrime(number)){
                    System.out.println("Число не является простым");
                    System.out.println(RETRY);
                    number = null;
                }
            }catch (Exception ex){
                System.out.println(ex.getMessage());
                System.out.println(RETRY);
            }
        }
        return number;
    }

}
