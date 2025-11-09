package dstu.csae.pafis.lab1.converter;

import java.math.BigInteger;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.stream.Collector;
import java.util.stream.Collectors;

public class StringConverter {

    private StringConverter(){}

    public static ArrayList<BigInteger> toBigInt(String ... integers){
        return Arrays.stream(integers)
                .map(BigInteger::new)
                .collect(Collectors.toCollection(ArrayList::new));
    }

    public static ArrayList<BigInteger> toBigInt(String text){
        return text.chars()
                .mapToObj(BigInteger::valueOf)
                .collect(Collectors.toCollection(ArrayList::new));
    }

    public static String toString(ArrayList<BigInteger> numbers){
        return numbers.stream()
                .map(x -> (char)x.intValue())
                .collect(Collector.of(
                        StringBuilder::new,
                        StringBuilder::append,
                        StringBuilder::append,
                        StringBuilder::toString));
    }

}
