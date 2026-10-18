package payflow;

import java.util.Map;

/** E4 : remboursement d'un paiement. */
public class RefundService {

    public String refund(Map<String, Double> wallets, String user, double amount) {
        wallets.put(user, wallets.getOrDefault(user, 0.0) + amount);
        return "REFUNDED";
    }
}
