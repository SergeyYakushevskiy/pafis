package dstu.csae.pafis.cipher;

import java.math.BigInteger;

public interface Cipher<P, C> {

    C encrypt(P plaintext);

    P decrypt(C ciphertext);

}
