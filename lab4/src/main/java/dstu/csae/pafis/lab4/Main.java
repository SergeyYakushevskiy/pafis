package dstu.csae.pafis.lab4;

import dstu.csae.pafis.lab4.test.SpectralTest;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;

public class Main{

    public static final String FILE_SEPARATOR = File.separator;
    public static final String[] PATH_TO_SEQUENCE = {
            System.getProperty("user.dir"),
            "lab3",
            "src",
            "main",
            "resources",
            "sts-2.1.2",
            "data.00001"
    };

    public static void main(String[] args) throws IOException {
        BufferedReader reader = new BufferedReader(new FileReader(String.join(FILE_SEPARATOR, PATH_TO_SEQUENCE)));
        String sequence = reader.readLine();
        reader.close();
        System.out.printf("Последовательность: %s\n", sequence);
        double pValue = SpectralTest.test(sequence);
        System.out.printf("Spectral Test p-value: %.6f%n", pValue);

        if (pValue >= 0.01) {
            System.out.println("Последовательность проходит тест (p >= 0.01)");
        } else {
            System.out.println("Последовательность не проходит тест (p < 0.01)");
        }
    }

}
