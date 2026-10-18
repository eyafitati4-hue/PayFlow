package payflow;

import java.util.Map;

/** E6 : consultation de l'état d'un paiement. */
public class PaymentStatus {

    public String of(Map<String, Double> wallets, String user) {
        return "BALANCE=" + wallets.getOrDefault(user, 0.0);
    }
}
