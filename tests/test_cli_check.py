import subprocess
import sys


def test_module_check_allows_tokenless_files(tmp_path):
    bot = tmp_path / "bot.ccd"
    bot.write_text(
        """при тексте:\n    ответ \"ok\"\n""",
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, "-m", "cicada.cli", "check", str(bot)],
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0
    assert "[OK]" in result.stdout
