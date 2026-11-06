package com.depa.consumer.security;

import io.jsonwebtoken.Jwts;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.io.File;
import java.nio.file.Files;
import java.security.KeyFactory;
import java.security.KeyPair;
import java.security.KeyPairGenerator;
import java.security.MessageDigest;
import java.security.interfaces.RSAPrivateKey;
import java.security.interfaces.RSAPublicKey;
import java.security.spec.PKCS8EncodedKeySpec;
import java.security.spec.X509EncodedKeySpec;
import java.time.Instant;
import java.util.Base64;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

@Component
public class CollegeBAssertionKeyPairProvider {

    private static final Logger log = LoggerFactory.getLogger(CollegeBAssertionKeyPairProvider.class);

    private final RSAPrivateKey privateKey;
    private final RSAPublicKey publicKey;
    private final String keyId;
    private final String collegeCode;
    private final String issuer;

    public CollegeBAssertionKeyPairProvider(
            @Value("${app.college.code:COLLEGE_B}") String collegeCode,
            @Value("${app.jwt.issuer:college-b}") String issuer,
            @Value("${app.rsa.keys-dir:./keys}") String keysDirPath
    ) {
        this.collegeCode = collegeCode;
        this.issuer = issuer;
        File directory = new File(keysDirPath);
        if (!directory.exists() && !directory.mkdirs()) {
            throw new IllegalStateException("Could not create College B assertion key directory: " + directory.getAbsolutePath());
        }

        File privateFile = new File(directory, "college_b_rsa.key");
        File publicFile = new File(directory, "college_b_rsa.pub");
        try {
            KeyFactory keyFactory = KeyFactory.getInstance("RSA");
            if (privateFile.exists() && publicFile.exists()) {
                log.info("Loading existing College B assertion key pair from {}", directory.getAbsolutePath());
                this.privateKey = (RSAPrivateKey) keyFactory.generatePrivate(
                        new PKCS8EncodedKeySpec(Files.readAllBytes(privateFile.toPath())));
                this.publicKey = (RSAPublicKey) keyFactory.generatePublic(
                        new X509EncodedKeySpec(Files.readAllBytes(publicFile.toPath())));
            } else {
                log.info("Generating persistent College B assertion key pair in {}", directory.getAbsolutePath());
                KeyPairGenerator generator = KeyPairGenerator.getInstance("RSA");
                generator.initialize(2048);
                KeyPair pair = generator.generateKeyPair();
                this.privateKey = (RSAPrivateKey) pair.getPrivate();
                this.publicKey = (RSAPublicKey) pair.getPublic();
                Files.write(privateFile.toPath(), privateKey.getEncoded());
                Files.write(publicFile.toPath(), publicKey.getEncoded());
            }
            privateFile.setReadable(false, false);
            privateFile.setReadable(true, true);
            privateFile.setWritable(false, false);
            privateFile.setWritable(true, true);
        } catch (Exception e) {
            throw new IllegalStateException("Failed to load or create College B assertion keys.", e);
        }
        this.keyId = computeKeyId(this.collegeCode, this.publicKey);
        log.info("Initialized College B assertion key pair (kid={})", keyId);
    }

    public RSAPublicKey getPublicKey() {
        return publicKey;
    }

    public String getKeyId() {
        return keyId;
    }

    public String getPublicKeyPem() {
        String base64 = Base64.getMimeEncoder(64, new byte[]{'\n'}).encodeToString(publicKey.getEncoded());
        return "-----BEGIN PUBLIC KEY-----\n" + base64 + "\n-----END PUBLIC KEY-----";
    }

    public String signStudentAssertion(String studentId, String action, String targetId) {
        Instant now = Instant.now();
        Map<String, Object> claims = new HashMap<>();
        claims.put("orgCode", collegeCode);
        claims.put("role", "STUDENT");
        claims.put("action", action);
        claims.put("targetId", targetId != null ? targetId : "ALL");

        return Jwts.builder()
                .header().keyId(keyId).and()
                .issuer(issuer)
                .audience().add("consent-manager").and()
                .subject(studentId)
                .claims(claims)
                .id(UUID.randomUUID().toString())
                .issuedAt(Date.from(now))
                .expiration(Date.from(now.plusSeconds(300)))
                .signWith(privateKey, Jwts.SIG.RS256)
                .compact();
    }

    private static String computeKeyId(String orgPrefix, RSAPublicKey key) {
        try {
            byte[] digest = MessageDigest.getInstance("SHA-256").digest(key.getEncoded());
            StringBuilder id = new StringBuilder(orgPrefix.toUpperCase()).append("_KEY_");
            for (int i = 0; i < 5; i++) {
                id.append(String.format("%02X", digest[i]));
            }
            return id.toString();
        } catch (Exception e) {
            throw new IllegalStateException("Could not compute College B assertion key ID.", e);
        }
    }
}
