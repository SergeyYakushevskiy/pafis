package dstu.csae.pafis.lab1.cipher;

public interface Cipher<P, C> {

    C encrypt(P plaintext);

    P decrypt(C ciphertext);

}
