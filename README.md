# PayFlow — Module de paiement ERP (Fil rouge : Métriques de produit)

Module de paiement simulé servant d'exemple pratique pour auditer et appliquer l'ensemble des **métriques de produit** (Vues 1, 2 et 3).

## Contexte de reprise
Le développeur principal a **démissionné subitement sans laisser aucune documentation technique**.
En tant qu'entreprise, nous devons prendre la relève et auditer ce module à l'aide des métriques de produit :
- **Vue 1 — Métriques internes** : Besoins, Conception (suite CK, MOOD), Développement (LOC, McCabe, Halstead, MI), Tests (couverture), Maintenance (SMI).
- **Vue 2 — Métriques externes** : Fiabilité (défauts/KLOC, MTBF, MTTR), Disponibilité, Performance.
- **Vue 3 — Métriques en usage** : ISO/IEC 25010 (clics, esthétique, contenu, navigation/abandon).

---

## Contenu du projet
```
PayFlow/
├── src/main/java/payflow/PaymentService.java     # Code hérité v1.2 (classe unique de 74 lignes)
├── src/test/java/payflow/PaymentServiceTest.java # 7 tests unitaires JUnit 5
├── refactored/                                   # Conception cible modulaire (6 classes découpées)
├── data/                                         # Données de scénario (releases, défauts, incidents, perf, ux)
│   ├── releases.csv                              # Historique des 3 versions (calcul du SMI)
│   ├── defects.csv                               # Défauts recensés (densité de défauts)
│   ├── incidents.csv                             # Arrêts et pannes (MTTR, MTBF, disponibilité)
│   ├── perf.csv                                  # Temps de réponse (moyenne, percentile 95)
│   └── ux.csv                                    # Données d'audit ergonomique et parcours utilisateur
├── tools/compute_metrics.py                      # Script de calcul automatisé de toutes les métriques
└── pom.xml                                       # Configuration Maven (JUnit 5, JaCoCo, PMD)
```

---

## Recalculer toutes les métriques
Le script Python calcule et affiche instantanément l'ensemble des valeurs métriques du projet :
```bash
python tools/compute_metrics.py
```
