"""Unit tests for the bundled name-day repository."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from datetime import date
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_MODULE_PATH = _REPO_ROOT / "custom_components" / "varda_dienas" / "repository.py"


def _load_repository_module():
    # Load repository.py directly so tests do not need Home Assistant installed.
    package_name = "custom_components.varda_dienas"
    if package_name not in sys.modules:
        pkg = type(sys)("varda_dienas_pkg")
        pkg.__path__ = [str(_MODULE_PATH.parent)]  # type: ignore[attr-defined]
        sys.modules["custom_components"] = type(sys)("custom_components")
        sys.modules["custom_components"].__path__ = [  # type: ignore[attr-defined]
            str(_REPO_ROOT / "custom_components")
        ]
        sys.modules[package_name] = pkg

    const_name = f"{package_name}.const"
    if const_name not in sys.modules:
        const_path = _MODULE_PATH.parent / "const.py"
        const_spec = importlib.util.spec_from_file_location(const_name, const_path)
        assert const_spec and const_spec.loader
        const_module = importlib.util.module_from_spec(const_spec)
        sys.modules[const_name] = const_module
        const_spec.loader.exec_module(const_module)

    module_name = f"{package_name}.repository"
    if module_name in sys.modules:
        return sys.modules[module_name]

    spec = importlib.util.spec_from_file_location(module_name, _MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


_repository = _load_repository_module()
NameDayRepository = _repository.NameDayRepository
date_key = _repository.date_key


class NameDayRepositoryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.repo = NameDayRepository()

    def test_new_years_day_main_names(self) -> None:
        names = self.repo.names_for(date(2026, 1, 1))
        self.assertEqual(names.main, ("Laimnesis", "Solvita", "Solvija"))
        self.assertIn("Afrodīte", names.extended)
        self.assertNotIn("Solvita", names.extended)

    def test_date_key(self) -> None:
        self.assertEqual(date_key(date(2026, 3, 5)), "03-05")

    def test_favorites_match_case_insensitive(self) -> None:
        matches = self.repo.matching_favorites(
            date(2026, 1, 1),
            ["solvita", "Missing"],
            include_extended=True,
        )
        self.assertEqual(matches, ["Solvita"])

    def test_normalize_favorites_dedupes(self) -> None:
        normalized = self.repo.normalize_favorites(["Anna", " anna ", "", "Jānis"])
        self.assertEqual(normalized, ["Anna", "Jānis"])

    def test_find_dates_for_known_name(self) -> None:
        days = self.repo.find_dates_for_name("Gatis")
        self.assertTrue(days)
        self.assertIn("01-08", days)

    def test_every_day_has_main_names(self) -> None:
        self.assertGreaterEqual(len(self.repo._main), 366)
        for key, values in self.repo._main.items():
            self.assertTrue(values, msg=f"{key} missing traditional names")


if __name__ == "__main__":
    unittest.main()
