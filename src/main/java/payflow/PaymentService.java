package payflow;

import java.util.HashMap;
import java.util.Map;

/**
 * PayFlow : module de paiement d'une boutique en ligne.
 * Code "hérité" : auteur parti, aucune documentation.
 */
public class PaymentService {

    private Map<String, Double> wallets = new HashMap<>();

    public void credit(String user, double amount) {
        wallets.put(user, wallets.getOrDefault(user, 0.0) + amount);
    }

    public String pay(String type, double amount, String currency,
                      String user, boolean promo, int retry) {
        String result = "";
        if (amount <= 0) {
            result = "ERR1";
        } else {
            if (type.equals("CARD")) {
                if (validateCard(user)) {
                    if (user.startsWith("VIP") || promo) {
                        amount = amount * 0.9;
                    }
                    if (!currency.equals("TND")) {
                        amount = amount * 3.1;
                    }
                    if (amount > 5000) {
                        if (retry > 2) {
                            result = "ERR2";
                        } else {
                            result = "PENDING_CHECK";
                        }
                    } else {
                        recordTransaction(user, amount);
                        sendReceipt(user, amount);
                        result = "OK";
                    }
                } else {
                    result = "ERR3";
                }
            } else {
                if (type.equals("WALLET")) {
                    if (wallets.getOrDefault(user, 0.0) >= amount) {
                        wallets.put(user, wallets.get(user) - amount);
                        recordTransaction(user, amount);
                        sendReceipt(user, amount);
                        result = "OK";
                    } else {
                        result = "ERR4";
                    }
                } else {
                    if (type.equals("REFUND")) {
                        result = refund(user, amount);
                    } else {
                        result = getStatus(user);
                    }
                }
            }
        }
        return result;
    }

    private boolean validateCard(String user) {
        return user.matches("[A-Za-z0-9]{4,}");
    }

    private void recordTransaction(String user, double amount) {
        System.out.println("TX " + user + " " + amount);
    }

    private String refund(String user, double amount) {
        wallets.put(user, wallets.getOrDefault(user, 0.0) + amount);
        return "REFUNDED";
    }

    private void sendReceipt(String user, double amount) {
        System.out.println("RECU " + user + " : " + amount);
    }

    private String getStatus(String user) {
        return "BALANCE=" + wallets.getOrDefault(user, 0.0);
    }
}
