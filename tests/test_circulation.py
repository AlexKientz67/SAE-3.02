import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from server import position_autorisee, trop_proche


class CirculationTest(unittest.TestCase):
    def test_arrets_avant_les_feux(self):
        for ancienne, suivante, attendu in [
            ((340, 239, 'bas'), (340, 242, 'bas'), (340, 240, 'bas')),
            ((440, 511, 'haut'), (440, 508, 'haut'), (440, 510, 'haut')),
            ((259, 440, 'droite'), (262, 440, 'droite'), (260, 440, 'droite')),
            ((511, 340, 'gauche'), (508, 340, 'gauche'), (510, 340, 'gauche')),
        ]:
            for couleur in ('rouge', 'orange'):
                self.assertEqual(position_autorisee(suivante, ancienne, [], couleur, couleur), attendu)
            self.assertEqual(position_autorisee(suivante, ancienne, [], 'vert', 'vert'), suivante)

    def test_files_et_changements_de_feux(self):
        voitures = []
        departs = [(340, 0, 'bas'), (440, 800, 'haut'), (0, 440, 'droite'), (800, 340, 'gauche')]
        for _ in range(4):
            for depart in departs:
                voitures.append(position_autorisee(depart, None, voitures, 'rouge', 'rouge'))
        for tour in range(2500):
            vertical, horizontal = [('vert', 'rouge'), ('orange', 'rouge'), ('rouge', 'vert'), ('rouge', 'orange')][(tour // 40) % 4]
            for i, ancienne in enumerate(voitures):
                x, y, direction = ancienne
                dx, dy = {'bas': (0, 3), 'haut': (0, -3), 'droite': (3, 0), 'gauche': (-3, 0)}[direction]
                autres = voitures[:i] + voitures[i+1:]
                voitures[i] = position_autorisee((x+dx, y+dy, direction), ancienne, autres, vertical, horizontal)
                self.assertFalse(any(trop_proche(voitures[i], autre) for autre in autres))
        for x, y, direction in voitures:
            self.assertTrue(x > 800 or x < -40 or y > 800 or y < -40, (x, y, direction))


if __name__ == '__main__':
    unittest.main()
