package payflow;

/** E2 : contrôle des données de la carte avant l'envoi. */
public class CardValidator {

    public boolean validate(String user) {
        return user.matches("[A-Za-z0-9]{4,}");
    }
}
