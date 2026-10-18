# Journal d'apprentissage — @le.point.enigme

Mis à jour à chaque vidéo par la tâche quotidienne. Règle : **un seul changement testé à la fois**, gardé s'il bat la moyenne des 3 vidéos précédentes (vues ET taux de j'aime/commentaires), abandonné sinon.

## Données de départ (analyse du 17/10/2026, source Metricool)

| Date | Vidéo | Durée | Vues | J'aime | Comm. | J'aime/vues |
|---|---|---|---|---|---|---|
| 12/10 | Qui a volé le diamant ? (style crème) | 28 s | 299 | 8 | 1 | 2,7 % |
| 13/10 | Réponse d'hier (style crème) | 16 s | 300 | 6 | 0 | 2,0 % |
| 13/10 | Qui a mangé le gâteau ? (style crème) | 24 s | 342 | 5 | 0 | 1,5 % |
| 15/10 | Énigme #01 Deux portes (donjon + voix) | 24 s | 263 | 12 | 2 | **4,6 %** |
| 10/10 | Trouve l'intrus v1 (repère) | 31 s | 275 | 2 | 0 | 0,7 % — 3,8 s vus en moyenne, 1,4 % jusqu'au bout |

Temps de visionnage par vidéo : non fourni par Metricool pour l'instant (champ vide).

## Constats
1. **Plafond ~300 vues** sur toutes les vidéos = TikTok ne dépasse pas le premier lot de test : la rétention n'est pas assez bonne pour qu'il pousse plus loin.
2. **Le style donjon + voix off** fait le meilleur engagement (4,6 % de j'aime, 2 commentaires) malgré un peu moins de vues.
3. **Très peu de commentaires** : une question ouverte (« écris ta question ») demande trop d'effort.
4. L'intrus v1 a montré que les gens partent dès la 1re seconde si l'enjeu n'est pas visible immédiatement.

5. (18/10) Les stats de l'énigme #02 (publiée le 17/10 à 18 h, vidéo TikTok 7697668632939138326) ne sont pas encore remontées dans Metricool le lendemain matin : Metricool a ~24-48 h de retard sur TikTok → juger chaque test à J+2 plutôt qu'à J+1.

## Plan de tests (dans l'ordre, un par vidéo ou par série de 2)
- T1 — **Énigme d'abord, réponse d'hier à la fin** (les nouveaux spectateurs ne connaissent pas l'énigme d'hier : la réponse en ouverture leur fait swiper). Accroche voix + texte dès 0,0 s : l'enjeu en une phrase.
- T2 — **Réponse en un mot ou une lettre** (choix A/B/C/D ou un nombre) + premier commentaire épinglable rédigé par le compte (« Moi j'ai dit B… et toi ? »).
- T3 — **Durée 20-25 s** max (chrono 6 s au lieu de 8).
- T4 — **Heure** : tester l'heure conseillée par Metricool (getBestTimeToPostByNetwork) contre 18 h.
- T5 — **Couverture** : image de la contrainte + question en gros texte.

## Historique des tests
| Date | Énigme | Test appliqué | Vues (J+1) | J'aime | Comm. | Partages | Verdict |
|---|---|---|---|---|---|---|---|
| 15/10 | #01 Deux portes | référence (donjon + voix, question ouverte) | 263 | 12 | 2 | 0 | référence — 5,3 % (j'aime+comm.)/vues |
| 17/10 | #02 Les 1000 bouteilles | aucun (avant le plan) | — (pas encore dans Metricool au 18/10) | — | — | — | à confirmer |
| 18/10 | #03 Les 3 boîtes menteuses | **T1** énigme d'abord (enjeu dit + écrit à 0,0 s), réponse de #02 à la fin (6,6 s) + boucle ; choix A/B/C et 1er commentaire auto (règles actées) ; 30,5 s, chrono 8 s, 18:00 | | | | | à remplir |

Note : avec le choix A/B/C et le premier commentaire désormais imposés par les règles actées, T2 est de fait déjà appliqué → prochain test = **T3 (durée 20-25 s, chrono 6 s)**.
Scripts de génération (image, son, voix, vérification) : `outils/generateur/`.
