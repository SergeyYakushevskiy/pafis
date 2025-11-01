package dstu.csae;

public class Main {

    public static void main(String[] args) {
        // Тестирование класса
        BigInt a = new BigInt("12345678901234567890");
        BigInt b = new BigInt("98765432109876543210");

        System.out.println("a = " + a);
        System.out.println("b = " + b);
        System.out.println("a в двоичном: " + a.toBinaryString());
        System.out.println("b в двоичном: " + b.toBinaryString());

        BigInt sum = a.add(b);
        System.out.println("a + b = " + sum);

        BigInt diff = b.subtract(a);
        System.out.println("b - a = " + diff);

        // Большие числа
        BigInt big1 = new BigInt("123456789012345678901234567890000000000");
        BigInt big2 = new BigInt("987654321098765432109876543210000000000");

        System.out.println("\nbig1 = " + big1);
        System.out.println("big2 = " + big2);
        System.out.println("big1 + big2 = " + big1.add(big2));
        System.out.println("big1 - big2 = " + big1.subtract(big2));
    }

}
