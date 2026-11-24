from database.parco_DAO import ParcoDAO
from database.escursione_DAO import EscursioneDAO
from database.punto_interesse_DAO import PuntoInteresseDAO

class Model:
    def __init__(self):
        self.escursioni_map = {}
        self.punti_interesse_map = {}

        self._pacchetto_ottimo = []
        self._valore_ottimo: int = -1
        self._costo = 0

        self._escursioni_parco = []
        self._max_giorni = None
        self._max_budget = None

        self.load_escursioni()
        self.load_punti_interesse()
        self.load_relazioni()

    @staticmethod
    def load_parchi():
        return ParcoDAO.get_parchi()

    def load_escursioni(self):
        self.escursioni_map = EscursioneDAO.get_escursioni()

    def load_punti_interesse(self):
        self.punti_interesse_map = PuntoInteresseDAO.get_punti_interesse()

    def load_relazioni(self):
        relazioni = EscursioneDAO.get_escursioni_punti_interesse()
        for relazione in relazioni:
            escursione = self.escursioni_map[relazione["id_escursione"]]
            punto = self.punti_interesse_map[relazione["id_punto_interesse"]]
            escursione.punti_interesse.add(punto)
            punto.escursioni.add(escursione)

    def genera_pacchetto(self, id_parco: str, max_giorni: int = None, max_budget: float = None):
        self._pacchetto_ottimo = []
        self._costo = 0
        self._valore_ottimo = -1

        self._escursioni_parco = [escursione for escursione in self.escursioni_map.values() if escursione.id_parco == id_parco]
        self._max_giorni = max_giorni
        self._max_budget = max_budget

        self._ricorsione(0, [], 0, 0, 0, set())

        return self._pacchetto_ottimo, self._costo, self._valore_ottimo

    def _ricorsione(self, start_index: int, pacchetto_parziale: list, durata_corrente: int, costo_corrente: float, valore_corrente: int, punti_usati: set):
        if valore_corrente > self._valore_ottimo or (valore_corrente == self._valore_ottimo and costo_corrente < self._costo):
            self._valore_ottimo = valore_corrente
            self._costo = costo_corrente
            self._pacchetto_ottimo = pacchetto_parziale.copy()

        for i in range(start_index, len(self._escursioni_parco)):
            escursione = self._escursioni_parco[i]
            nuova_durata = durata_corrente + escursione.durata_giorni
            nuovo_costo = costo_corrente + escursione.costo

            giorni_ok = self._max_giorni is None or nuova_durata <= self._max_giorni
            budget_ok = self._max_budget is None or nuovo_costo <= self._max_budget
            punti_ok = punti_usati.isdisjoint(escursione.punti_interesse)

            if giorni_ok and budget_ok and punti_ok:
                valore_escursione = sum(punto.voto_visitatori for punto in escursione.punti_interesse)

                pacchetto_parziale.append(escursione)
                punti_usati.update(escursione.punti_interesse)

                self._ricorsione(i + 1, pacchetto_parziale, nuova_durata, nuovo_costo, valore_corrente + valore_escursione, punti_usati)

                pacchetto_parziale.pop()
                punti_usati.difference_update(escursione.punti_interesse)