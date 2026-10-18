import unittest

from server import agent
from server.materials import RULE_FILES, ROUTES, evidence_bundle, read_text, system_instructions
from server.paths import RULES
from server.snapshot import pitch_deck_snapshot


class MaterialsConnectivityTests(unittest.TestCase):
    def test_rule_files_exist_and_load_into_system_prompt(self):
        for name in RULE_FILES:
            self.assertTrue((RULES / name).exists(), name)
        text = system_instructions()
        self.assertIn("Bare minimum for critical understanding", text)
        self.assertGreater(len(text), 1000)

    def test_every_routed_file_is_readable(self):
        for topic, _words, paths in ROUTES:
            for relative in paths:
                with self.subTest(topic=topic, file=relative):
                    self.assertTrue(read_text(relative).strip())

    def test_every_task_file_is_readable(self):
        for task, paths in agent.TASK_FILES.items():
            for relative in paths:
                with self.subTest(task=task, file=relative):
                    self.assertTrue(read_text(relative).strip())

    def test_snapshot_files_are_all_readable(self):
        pack = pitch_deck_snapshot()
        for relative in pack["files"]:
            with self.subTest(file=relative):
                self.assertTrue(read_text(relative).strip())
        bundle = evidence_bundle(pack["files"], limit=2000)
        self.assertNotIn("Files not opened", bundle)

    def test_case_qa_and_glossary_examples_are_wired(self):
        investor_files = set(agent.TASK_FILES["investor_meeting"])
        self.assertIn("workspace/tidewell-systems/04-investor-qa.md", investor_files)
        financial_files = set(agent.TASK_FILES["financial_numbers"])
        self.assertIn("workspace/tidewell-systems/glossary-examples.md", financial_files)

    def test_csv_is_not_passed_as_model_text(self):
        pack = pitch_deck_snapshot()
        self.assertFalse(any(path.endswith(".csv") for path in pack["files"]))


if __name__ == "__main__":
    unittest.main()
