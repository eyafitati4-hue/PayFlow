package payflow;

import java.util.ArrayList;
import java.util.List;

/** E3 : enregistrement de chaque transaction. */
public class TransactionLog {

    private final List<String> entries = new ArrayList<>();

    public void record(String user, double amount) {
        entries.add("TX " + user + " " + amount);
    }

    public int count() {
        return entries.size();
    }
}
