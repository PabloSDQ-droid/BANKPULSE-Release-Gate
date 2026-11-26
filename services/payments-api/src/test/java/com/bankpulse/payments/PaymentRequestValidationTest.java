package com.bankpulse.payments;

import jakarta.validation.Validation;
import jakarta.validation.Validator;
import jakarta.validation.ValidatorFactory;
import java.math.BigDecimal;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

class PaymentRequestValidationTest {

    private static ValidatorFactory factory;
    private static Validator validator;

    @BeforeAll
    static void preparar() {
        factory = Validation.buildDefaultValidatorFactory();
        validator = factory.getValidator();
    }

    @AfterAll
    static void cerrar() {
        factory.close();
    }

    @Test
    void aceptaPagoDe500Dolares() {
        var request = new PaymentController.PaymentRequest(
                "EC-4242", new BigDecimal("500.00"), "USD"
        );

        assertTrue(validator.validate(request).isEmpty());
    }

    @ParameterizedTest
    @ValueSource(strings = {"0", "-1"})
    void rechazaImportesNoPositivos(String amount) {
        var request = new PaymentController.PaymentRequest(
                "EC-4242", new BigDecimal(amount), "USD"
        );

        assertFalse(validator.validate(request).isEmpty());
    }
}