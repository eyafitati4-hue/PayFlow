package payflow;

import java.util.HashMap;
import java.util.Map;

/** E1 : paiement d'une commande. Façade qui orchestre les services spécialisés. */
public class PaymentService {

    private final Map<String, Double> wallets = new HashMap<>();
    private final CardValidator validator = new CardValidator();
    private final TransactionLog log = new TransactionLog();
    private final RefundService refunds = new RefundService();
    private final ReceiptService receipts = new ReceiptService();
    private final PaymentStatus status = new PaymentStatus();

    public void credit(String user, double amount) {
        wallets.put(user, wallets.getOrDefault(user, 0.0) + amount);
    }

    public String pay(String type, double amount, String currency,
                      String user, boolean promo, int retry) {
        if (amount <= 0) {
            return "ERR1";
        }
        if (type.equals("CARD")) {
            return payByCard(amount, currency, user, promo, retry);
        }
        if (type.equals("WALLET")) {
            return payByWallet(amount, user);
        }
        if (type.equals("REFUND")) {
            return refunds.refund(wallets, user, amount);
        }
        return status.of(wallets, user);
    }

    private String payByCard(double amount, String currency, String user, boolean promo, int retry) {
        if (!validator.validate(user)) {
            return "ERR3";
        }
        if (user.startsWith("VIP") || promo) {
            amount = amount * 0.9;
        }
        if (!currency.equals("TND")) {
            amount = amount * 3.1;
        }
        if (amount > 5000) {
            if (retry > 2) {
                return "ERR2";
            }
            return "PENDING_CHECK";
        }
        log.record(user, amount);
        receipts.send(user, amount);
        return "OK";
    }

    private String payByWallet(double amount, String user) {
        if (wallets.getOrDefault(user, 0.0) < amount) {
            return "ERR4";
        }
        wallets.put(user, wallets.get(user) - amount);
        log.record(user, amount);
        receipts.send(user, amount);
        return "OK";
    }
}
