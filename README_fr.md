[English](README.md)

Télécharger les données d'observations météorologiques canadiennes (_Get Canadian Weather Observations_)
=============

Introduction
------------


`get_canadian_weather_obervation.py` est un logiciel python3 utilisé pour télécharger les [fichiers d'observations d'Environnement et Changement climatique Canada](http://climate.weather.gc.ca/historical_data/search_historic_data_f.html) (ECCC) sur un ordinateur. Ce logiciel est à l'origine un projet personnel de Miguel Tremblay et n'appartient pas à ECCC.

Ce script est basé sur l'information fournie sur le [fichier README disponible sur site web du climat d'ECCC](ftp://client_climate@ftp.tor.ec.gc.ca/Pub/Get_More_Data_Plus_de_donnees/Lisezmoi.txt). De l'information supplémentaire sur le format de données peut-être trouvé sur le [Documentation technique des archives nationales de données climatologiques](ftp://client_climate@ftp.tor.ec.gc.ca/Pub/Documentation_Technical/Documentation_technique.pdf). Bien que ce logiciel soit distribué avec la licence GPL version 3, les données téléchargées sont sous la [Convention de droits d’utilisation d’un produit logiciel et de données d’Environnement et Changement climatique Canada](http://climate.weather.gc.ca/prods_servs/attachment1_f.html).

Ce logiciel fonctionne sous GNU/Linux, Windows et Mac OS X.
___

Prérequis
------------

* [python3](https://www.python.org/downloads/)
* [python3-dateutil](https://pypi.python.org/pypi/python-dateutil)
* [python3-progress](https://pypi.python.org/pypi/progress)

___

Téléchargement
--------
La dernière version peut être téléchargée ici:<br>
https://framagit.org/MiguelTremblay/get_canadian_weather_observations   

La version git peut être téléchargée ici:<br>
 ```git clone https://framagit.org/MiguelTremblay/get_canadian_weather_observations.git```


Manuel
--------

De façon générale, ce logiciel devrait être appelé en ligne de commande de cette manière:
```bash
python get_canadian_weather_obervation.py [OPTIONS] [PERIODE] ENTREE
```
<br />
où:
* OPTIONS sont décrites dans la table plus bas.
* PERIODE est la période pour laquelle les observations sont demandées. Cette option est valide pour les observations de type horaire, quotidienne et mensuelle ([--hourly&#124;--daily&#124;--monthly])
* ENTREE est une ou plusieurs de ces valeurs:
 * [identificateur ECCC de station](ftp://client_climate@ftp.tor.ec.gc.ca/Pub/Get_More_Data_Plus_de_donnees/R%E9pertoire%20des%20stations%20FR.csv)
 * [code de province de deux lettres](http://www12.statcan.gc.ca/census-recensement/2011/ref/dict/table-tableau/table-tableau-8-fra.cfm)
 * [Code aéroport de trois lettres IATA](https://fr.wikipedia.org/wiki/Liste_des_codes_AITA_des_a%C3%A9roports/Y) (lorsqu'il y a plus d'une station correspondant à un code, toutes les stations sont ajoutées à la liste)
 * `all` pour toutes les stations disponibles


| Options                                  | Description |
| -------                                  | ------------|
| `-h`, `--help`                           | Afficher ce message d'aide et quitter.|
| `-o` `--output-directory`&nbsp;REPERTOIRE | Répertoire où les fichiers seront téléchargés, dans leurs sous-répertoires lorsque demandé (voir l'option `--no-tree`). La valeur par défaut est l'endroit où se trouve le script get_canadian_weather_observations.py. Les sous-répertoires prennent la forme de STATION-ID/OBS-TYPE, où "STATION-ID" est le code de station d'ECCC et "OBS-TYP" est l'un des quatre types d'observation: "hourly", "daily", "monthly" ou "almanac".|
| `-n` `--no-tree`                         | Ne pas créer de répertoire, télécharger tous les fichiers dans le répertoire de sortie.|
| `-N` `--no-clobber`                      | Ne pas écraser un fichier existant. Le fichier n'est pas téléchargé.|
| `-S` `--station-list`&nbsp;CHEMIN        | Utiliser la liste de station sur votre ordinateur local à CHEMIN plutôt que de télécharger le fichier en ligne sur le site du climat d'ECCC à chaque appel du logiciel.  Vous pouvez télécharger le fichier de la liste des stations (en [anglais](ftp://client_climate@ftp.tor.ec.gc.ca/Pub/Get_More_Data_Plus_de_donnees/Station%20Inventory%20EN.csv) ou en [français](ftp://client_climate@ftp.tor.ec.gc.ca/Pub/Get_More_Data_Plus_de_donnees/R%E9pertoire%20des%20stations%20FR.csv)). Utiliser le fichier local peut sauver pas mal de temps. Si vous utilisez ce fichier, vous devez appeler la langue correspondante avec l'option `--lang`.|
| `-l` `--lang` [en&#124;fr]               | Langue dans laquelle les fichiers seront téléchargés (en = anglais, fr = français). Le valeur par défaut est l'anglais.|
|`-t`  `--dry-run`                         | Executer le programme, imprimer l'URL mais ne pas télécharger les fichiers.|
|`-F` `--format`&nbsp;[csv&#124;xml]       | Télécharger les fichiers en format CSV ou XML. La valeur par défaut est CSV.|
|`-d` `--date` YYYY[-MM]                   | Télécharger les observations pour cette date spécifique seulement. Les valeurs de `--end-date` et  `--start-date` sont ignorées si cette option est utilisée. Si aucune date n'est fournie, télécharger les données pour la période complète.|
|`-e` `--start-date` YYYY[-MM]             | Télécharger les observations après cette date. Arrête à `--end-date` si cette option est utilisée, sinon les observations sont téléchargées jusqu'à la dernière observation disponible.|
|`-f` `--end-date` YYYY[-MM]               | Télécharger les observations avant cette date. Arrête à `--start-date` si cette option est utilisée, sinon les observations sont téléchargées à partir de la première observation disponible.|
|`-H` `--hourly`                           | Télécharger les observations horaires (1 fichier par mois).|
|`-D` `--daily`                            | Télécharger les observations quotidiennes (1 fichier par année).|
|`-M` `--monthly`                          | Télécharger les moyennes mensuelles, calculées à partir des observations quotidiennes (1 fichier pour toute la période).|
|`-C` `--climate`                          | Télécharger les moyennes et records de l'almanach (1 fichier pour toute la période).|
|`-I` `--info`                             | Télécharger et afficher l'information (lat, lon, code, date début/fin, etc.) pour la/les station(s) choisie(s) et quitter.|
|`-v` `--verbose`                          | Expliquer ce qui se passe.|
|`-V` `--version`                          | Écrire l'information sur la version et quitter.|

Utilisation
-----

Télécharger les moyennes mensuelles pour l'[aéroport de Bagotville](https://fr.wikipedia.org/wiki/Base_des_Forces_canadiennes_Bagotville) en format XML en français (aucune date requise car l'historique des moyennes mensuelles est contenu dans un seul fichier):
```bash
 python get_canadian_weather_obervation.py --monthly -o /home/miguel/bagotville -f xml -l fr YBG
```
<br />

Télécharger toutes les observations horaires pour toutes les stations canadiennes pour l'année 2012 en anglais en format CSV: 
```bash
 python get_canadian_weather_obervation.py --hourly -o /home/miguel/download --date 2012 all
```
<br />

Télécharger toutes les observations horaires et quotidiennes pour toutes les stations de Colombie-Britannique pour la décennie 1980-1989 en format CSV en anglais:
```bash
 python get_canadian_weather_obervation.py --hourly --daily --start-date 1980-01 --end-date 1990-01 -o /home/miguel/download BC
```
<br />

Afficher l'information pour la station de Bagotville:
```bash
 python get_canadian_weather_observations.py --info YBG
----
Station ID: 5889
Name:BAGOTVILLE A
DLY Last Year:2017
HLY Last Year:2017
MLY First Year:1942
Elevation (m):159.1
TC ID:YBG
Station ID:5889
First Year:1942
MLY Last Year:2014
Longitude:-710000000
Latitude:482000000
Climate ID:7060400
Province:QUEBEC
Longitude (Decimal Degrees):-71
Last Year:2017
HLY First Year:1953
DLY First Year:1942
Latitude (Decimal Degrees):48.33
WMO ID:71727
```

Bogues
-----

Si vous trouvez un bogue, vous devez le rapporter à [get_canadian_weather_observations.miguel@ptaff.ca](mailto:get_canadian_weather_observations.miguel@ptaff.ca)

Auteur
-----

[Miguel Tremblay](http://ptaff.ca/miguel/)

Licence
-----

Copyright © 2018 Miguel Tremblay.

get_canadian_weather_observations est un logiciel libre; vous pouvez le redistribuer et/ou le modifier selon les termes de la GNU General Public License (Licence Publique Générale GNU) telle qu'elle a été publiée par la Free Software Foundation; soit la version 3 de la licence, soit (comme vous le souhaitez) toute version ultérieure.