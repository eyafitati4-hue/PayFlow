package payflow;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;

import org.junit.jupiter.api.Test;

class PaymentServiceTest {

    private final PaymentService service = new PaymentService();

    @Test
    void montantInvalideRetourneErr1() {
        assertEquals("ERR1", service.pay("CARD", -5, "TND", "USER01", false, 0));
    }

    @Test
    void paiementCarteSimple() {
        String r = service.pay("CARD", 100, "TND", "USER01", false, 0);
        assertNotNull(r);
    }

    @Test
    void paiementCarteVipDeviseEtrangere() {
        String r = service.pay("CARD", 200, "EUR", "VIP001", false, 0);
        assertNotNull(r);
    }

    @Test
    void grosMontantApresPlusieursEssais() {
        String r = service.pay("CARD", 9000, "TND", "USER01", false, 3);
        assertNotNull(r);
    }

    @Test
    void grosMontantEnAttenteDeControle() {
        String r = service.pay("CARD", 9000, "TND", "USER01", false, 0);
        assertNotNull(r);
    }

    @Test
    void paiementPortefeuille() {
        service.credit("USER01", 500);
        String r = service.pay("WALLET", 100, "TND", "USER01", false, 0);
        assertNotNull(r);
    }

    @Test
    void remboursement() {
        String r = service.pay("REFUND", 50, "TND", "USER01", false, 0);
        assertNotNull(r);
    }
}
