package dstu.csae.pafis.lab4.utils;

public class Complex {
    private final double real;
    private final double imag;

    public Complex(double real, double imag) {
        this.real = real;
        this.imag = imag;
    }

    public Complex add(Complex b) {
        return new Complex(this.real + b.real, this.imag + b.imag);
    }

    public Complex subtract(Complex b) {
        return new Complex(this.real - b.real, this.imag - b.imag);
    }

    public Complex multiply(Complex b) {
        double realPart = this.real * b.real - this.imag * b.imag;
        double imagPart = this.real * b.imag + this.imag * b.real;
        return new Complex(realPart, imagPart);
    }

    public double abs() {
        return Math.sqrt(real * real + imag * imag);
    }
}
