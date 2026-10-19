package com.bankpulse.payments;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import jakarta.validation.Validation;
import jakarta.validation.Validator;
import jakarta.validation.ValidatorFactory;
import java.math.BigDecimal;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;

class PaymentRequestValidationTest {
    private static ValidatorFactory factory;
    private static Validator validator;

    @BeforeAll
    static void setUp() {
        factory = Validation.buildDefaultValidatorFactory();
        validator = factory.getValidator();
    }

    @AfterAll
    static void close() { factory.close(); }

    @Test
    void acceptsValidPaymentRequest() {
        var request = new PaymentController.PaymentRequest("EC-4242", new BigDecimal("500.00"), "USD");
        assertTrue(validator.validate(request).isEmpty());
    }

    @ParameterizedTest
    @ValueSource(strings = {"0", "-1"})
    void rejectsNonPositiveAmount(String amount) {
        var request = new PaymentController.PaymentRequest("EC-4242", new BigDecimal(amount), "USD");
        assertFalse(validator.validate(request).isEmpty());
    }

    @Test
    void rejectsMalformedCurrency() {
        var request = new PaymentController.PaymentRequest("EC-4242", new BigDecimal("500.00"), "US");
        assertFalse(validator.validate(request).isEmpty());
    }
}
