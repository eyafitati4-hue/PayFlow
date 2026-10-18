package payflow;

/** E5 : envoi du reçu après chaque paiement. */
public class ReceiptService {

    public void send(String user, double amount) {
        System.out.println("RECU " + user + " : " + amount);
    }
}
