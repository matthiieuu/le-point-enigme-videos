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
| 15/10 | #01 Deux portes | référence (donjon + voix, question ouverte) | 263 → 275 → 286 | 12 | 2 | 0 | référence — 5,3 % (j'aime+comm.)/vues |
| 17/10 | #02 Les 1000 bouteilles | aucun (avant le plan) ; 37 s | 289 (J+2) → 323 (J+3) → 349 | 10 → 11 | 1 | 0 | pas de test — vues dans la moyenne des 3 précédentes (304, −5 %), engagement 3,8 % > moyenne 3,0 % (le donjon + voix confirme son avance) |
| 18/10 | #03 Les 3 boîtes menteuses | **T1** énigme d'abord (enjeu dit + écrit à 0,0 s), réponse de #02 à la fin (6,6 s) + boucle ; choix A/B/C et 1er commentaire auto (règles actées) ; 30,5 s, chrono 8 s, 18:00 | 252 (J+2) → 301 | 7 | 1 | 0 | **abandonné** selon la règle : vues −20 % (moy. 3 préc. 315) et engagement 3,2 % vs 3,5 % (−9 %). Mais revenir à « réponse d'hier en ouverture » violerait la règle actée n°4 (enjeu dès 0,0 s) → on garde l'ordre énigme d'abord ; le levier des vues est à chercher ailleurs (heure, couverture, accroche) |
| 19/10 | #04 Les chapeaux du cachot | T1 conservé (en attente de verdict) + **T3** durée courte : 24,9 s, chrono 6 s, réponse de #03 en 5 s ; réponse en un mot (BLANC/NOIR) ; 18:00 | 1096 (J+2) | 14 | 0 | 0 | **abandonné selon la règle stricte** : vues ×3,5 (moy. 3 préc. au 21/10 : 312) mais engagement 1,3 % vs 3,8 %. **1re vidéo > 1000 vues** → le format court (≈25 s, chrono 6 s) reste la base de fait (aucun format meilleur vers lequel revenir) ; à re-juger sur #05-#06 |
| 20/10 | #05 Le code de la bombe | format #04 conservé (26,0 s, chrono 6 s, T3 en attente) + **T4 heure** : 12:00 (créneau Metricool du mardi : 10 h = 1136 déjà passé à 11 h, 12 h = 1082, 18 h = 1119) ; choix A ÷ / B × / C + ; saboteur qui parle en bulle ; 1er commentaire « Indice : 4 × 6 est un piège » | 398 (J+1) → **905 (J+2)** | 10 | 1 | **1** | **abandonné selon la règle** : vues +51 % (moy. #02-#04 au 22/10 : 600) mais engagement 1,2 % vs 2,4 %. 2e vidéo la plus vue et **1er partage** de la série ; 12 h n'est pas retenu comme règle (le gain de vues ne s'accompagne pas d'engagement) → retour à 18 h, l'heure reste un levier à re-tester |
| 21/10 | #06 Les deux cordes | base format court (27,8 s, chrono 6 s, choix A 2 / B 3 / C 4, geôlier qui parle en bulle, grille qui descend) + **T5 couverture** : videoCoverMilliseconds 15200 (chrono + « COMBIEN DE BOUTS ? » + choix A/B/C + contrainte) ; retour à 18:00 (T4 en attente) ; 1er comm. « Couper la corde en deux ne marche pas… alors, A, B ou C ? » | 383 (J+2) | 2 | 0 | 0 | **abandonné** (T5 couverture) : vues −51 % (moy. #03-#05 au 23/10 : 787) et engagement 0,5 % vs 1,7 %. La couverture « chrono » n'a pas aidé → retour à la 1re image (enjeu + titre) comme couverture. Réponse vérifiée : B (3 bouts) |
| 22/10 | #07 L'île des menteurs | base format court (26,7 s, chrono 6 s, 2 insulaires humains face caméra, A parle en bulle) + couverture chrono conservée (videoCoverMilliseconds 13500, T5 en attente) + **T6 réponse binaire en un mot** : boutons VRAI / MENTEUR (au lieu de A/B/C), CTA « Écris VRAI ou MENTEUR » ; 18:00 ; 1er comm. « Un seul mot suffit : VRAI ou MENTEUR ? » | absente de Metricool au 23/10 | | | | à remplir (juger le 24/10) — couverture chrono abandonnée entre-temps (verdict T5) |
| 23/10 | #08 Qui a volé le diamant ? | base format court (24,0 s, chrono 6 s, 3 suspects humains Léa/Hugo/Nina qui parlent en bulles, choix LÉA/HUGO/NINA = réponse en un prénom ; T6 en attente) + **T8 réponse d'hier courte** : 3,7 s (« VRAI ! A dit vrai, donc B ment ») au lieu de 6-7 s ; pas de videoCoverMilliseconds (T5 abandonné) ; 18:00 ; 1er comm. « Un seul prénom suffit… Léa, Hugo ou Nina ? » | | | | | à remplir (juger le 25/10). Réponse vérifiée par script : NINA |

Note : avec le choix A/B/C et le premier commentaire désormais imposés par les règles actées, T2 est de fait déjà appliqué → prochain test = **T3 (durée 20-25 s, chrono 6 s)**.
6. (19/10) Confirmé : la vidéo de la veille n'apparaît pas dans Metricool le lendemain matin (#03 absente au 19/10) ; #02 est remontée à J+2 (289 vues, 10 j'aime, 1 comm.). Les durées 24 s et 37 s font des vues similaires (267 vs 289) : la durée seule ne débloque pas le plafond de ~300 vues.

Scripts de génération (image, son, voix, vérification) : `outils/generateur/` (version #04 dans `outils/generateur/enigme04/`, version #05 « bombe + saboteur » dans `outils/generateur/enigme05/`, version #06 « deux cordes + geôlier » dans `outils/generateur/enigme06/` : video06.py, audio06.py, verif06.py, voix.py, lignes.json ; version #07 « île des menteurs, 2 insulaires + hublot sur la mer, choix VRAI/MENTEUR » dans `outils/generateur/enigme07/` ; version #08 « diamant volé, 3 suspects Léa/Hugo/Nina en bulles » dans `outils/generateur/enigme08/`).
Prochain test après verdicts de T1/T3 : **T4 (heure conseillée Metricool)**.
7. (20/10) Toutes les vidéos restent entre 250 et 350 vues, quel que soit le format testé (durée, ordre énigme/réponse) : les écarts de ±20 % ressemblent à du bruit autour du premier lot de diffusion TikTok. Les vidéos se stabilisent vers J+3 (#02 : 289 à J+2 → 323 à J+3) → comparer les vidéos au même âge. Partages toujours à 0 : aucune vidéo n'a encore donné envie d'être envoyée à un ami.
8. (20/10) T4 appliqué à #05 : publication à 12:00 au lieu de 18:00. Pour T4 suivant (si 12 h n'est pas concluant) : viser 10:00 ou 18:00 selon getBestTimeToPostByNetwork, en programmant avant 10 h.
Prochain test après T4 : **T5 (couverture : contrainte + question en gros texte, via videoCoverMilliseconds sur l'image la plus lisible)**.
9. (21/10) **#04 « Les chapeaux du cachot » a dépassé 1000 vues (1096)** — la seule à casser le plafond de ~300. Ce qu'elle a de différent : la plus courte des énigmes (24 s, chrono 6 s) ; réponse **binaire en un mot** (BLANC/NOIR, pas de A/B/C) ; **3 personnages humains face caméra** (les prisonniers) au lieu d'objets ; publiée lundi 18 h. Mais 0 commentaire et 1,3 % de j'aime : la portée vient du « Pour toi » (rétention), pas de la conversation. Commentaires quasi nuls depuis #03 malgré choix A/B/C + 1er commentaire.
10. (21/10) Metricool ne fournit toujours ni temps moyen vu (TKPO15), ni % vu en entier (TKPO13), ni portée (TKPO11), ni part « Pour toi » (TKPO16) : on ne juge que sur vues/j'aime/comm./partages.
Prochains tests proposés (après T5) : **T6 — réponse binaire en un mot** (2 choix au lieu de 3, comme #04) ; **T7 — personnages humains au centre de l'histoire** (comme les prisonniers de #04).
11. (22/10) Chiffres au 22/10 : #02 366 vues, #03 317, #04 **1118**, #05 **905** (J+2, 1 partage = le 1er de la série). Les deux vidéos qui cassent le plafond (#04, #05) sont les deux plus courtes du format « court » (24-26 s, chrono 6 s) → le format court se confirme comme base. Mais l'engagement baisse quand les vues montent (1,2-1,3 % contre 3-5 % au début) : les nouveaux spectateurs « Pour toi » regardent sans répondre.
Prochain test après T6 : **T7 — personnages humains au centre** (déjà présent de fait dans #07 : à isoler sur une énigme sans personnage, ex. #09 l'escargot, en ajoutant un prisonnier qui parle) ; puis **T8 — réponse d'hier plus courte (≤ 5 s)** ou **T9 — re-tester 12 h** sur une énigme au format court.
12. (23/10) Chiffres au 23/10 : #01 312, #02 368, #03 324, #04 **1124**, #05 **912** (1 partage), #06 **383** (J+2, 2 j'aime, 0 comm.). #06 retombe au plafond ~300-400 malgré le format court : la durée seule n'explique pas #04/#05. Différences de #06 : objet (cordes) au centre et non des personnages face caméra, question chiffrée A/B/C peu intuitive, couverture chrono. → renforce l'hypothèse **T7 (personnages humains au centre)**, déjà présente de fait dans #07 et #08.
Prochain test après T8 : **T9 — re-tester 12 h** sur une énigme au format court, ou **T7 isolé** sur #09 l'escargot (ajouter un prisonnier qui parle).
