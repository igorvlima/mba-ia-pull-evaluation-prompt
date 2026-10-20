"""
Testes automatizados para validação de prompts.
"""
import pytest
import yaml
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure

PROMPT_FILE = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"


def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def prompt_data():
    """Carrega o prompt otimizado (v2) uma única vez para a suíte."""
    data = load_prompts(str(PROMPT_FILE))
    assert data is not None, f"Arquivo YAML não encontrado: {PROMPT_FILE}"
    return data.get("bug_to_user_story_v2", data)


class TestPrompts:
    def test_prompt_has_system_prompt(self, prompt_data):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        system_prompt = prompt_data.get("system_prompt", "").strip()
        assert system_prompt, "system_prompt está ausente ou vazio"

    def test_prompt_has_role_definition(self, prompt_data):
        """Verifica se o prompt define uma persona (ex: "Você é um Product Manager")."""
        system_prompt = prompt_data.get("system_prompt", "").lower()
        assert any(
            marker in system_prompt
            for marker in [
                "você é um",
                "you are a",
                "product manager",
                "persona",
                "sênior",
                "senior",
            ]
        ), "O prompt não define uma persona (role definition)"

    def test_prompt_mentions_format(self, prompt_data):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        system_prompt = prompt_data.get("system_prompt", "").lower()
        has_markdown_format = "markdown" in system_prompt or "## user story" in system_prompt
        has_user_story_format = (
            "como um" in system_prompt
            and "eu quero" in system_prompt
            and ("para que" in system_prompt or "para que eu" in system_prompt)
        )
        assert has_markdown_format or has_user_story_format, (
            "O prompt não exige formato Markdown nem o formato padrão de User Story"
        )

    def test_prompt_has_few_shot_examples(self, prompt_data):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        system_prompt = prompt_data.get("system_prompt", "").lower()
        has_example_marker = "exemplo" in system_prompt or "exemplos" in system_prompt
        has_inout_marker = (
            "relato de bug" in system_prompt
            and "resposta esperada" in system_prompt
        )
        assert has_example_marker and has_inout_marker, (
            "O prompt não contém exemplos de entrada/saída (few-shot)"
        )

    def test_prompt_no_todos(self, prompt_data):
        """Garante que você não esqueceu nenhum `[TODO]` no texto."""
        for key, value in prompt_data.items():
            if isinstance(value, str) and "[TODO]" in value.upper():
                pytest.fail(f"Campo '{key}' ainda contém [TODO]")
        assert "[TODO]" not in str(prompt_data).upper()

    def test_minimum_techniques(self, prompt_data):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        techniques = prompt_data.get("techniques_applied", [])
        assert isinstance(techniques, list) and len(techniques) >= 2, (
            f"Mínimo de 2 técnicas requeridas em techniques_applied, encontradas: {len(techniques)}"
        )

    def test_validate_prompt_structure_utils(self, prompt_data):
        """Teste extra: validar com a função utilitária do projeto (system, version, técnicas)."""
        is_valid, errors = validate_prompt_structure(prompt_data)
        assert is_valid, f"Estrutura inválida: {errors}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])