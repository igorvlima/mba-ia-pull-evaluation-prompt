"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)
"""

import os
import sys
from dotenv import load_dotenv
from langsmith import Client
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header, validate_prompt_structure

load_dotenv()

PROMPT_FILE = "prompts/bug_to_user_story_v2.yml"
PROMPT_NAME = "bug_to_user_story_v2"


def push_prompt_to_langsmith(client: Client, prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        client: Cliente do LangSmith
        prompt_name: Nome do prompt (ex: "bug_to_user_story_v2")
        prompt_data: Dados do prompt

    Returns:
        True se sucesso, False caso contrário
    """
    username = os.getenv("USERNAME_LANGSMITH_HUB", "").strip()
    if not username:
        print("❌ USERNAME_LANGSMITH_HUB não configurado no .env")
        print("   Crie seu handle público do Hub em LangSmith > Prompts > Make Public")
        return False

    full_name = f"{username}/{prompt_name}"

    print(f"   Montando ChatPromptTemplate...")
    system_prompt = prompt_data.get("system_prompt", "")
    user_prompt = prompt_data.get("user_prompt", "{bug_report}")

    # A variável do template precisa ser {bug_report}, que é a chave de entrada
    # usada no dataset de avaliação.
    template = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", user_prompt),
        ]
    )

    description = prompt_data.get("description", "Prompt otimizado para converter bugs em User Stories")
    tags = prompt_data.get("tags", []) or []
    techniques = prompt_data.get("techniques_applied", []) or []
    all_tags = list(dict.fromkeys([*tags, *techniques]))  # dedupe preservando ordem

    print(f"   Publicando prompt: {full_name}")
    url = client.push_prompt(
        full_name,
        object=template,
        is_public=True,
        description=description,
        tags=all_tags,
    )

    print(f"✓ Prompt publicado com sucesso!")
    print(f"   URL: {url}")
    return True


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    errors = []

    required_fields = ["description", "system_prompt", "user_prompt", "version"]
    for field in required_fields:
        if field not in prompt_data:
            errors.append(f"Campo obrigatório faltando: {field}")

    system_prompt = prompt_data.get("system_prompt", "").strip()
    if not system_prompt:
        errors.append("system_prompt está vazio")

    user_prompt = prompt_data.get("user_prompt", "").strip()
    if not user_prompt:
        errors.append("user_prompt está vazio")

    if "{bug_report}" not in user_prompt and "{bug_report}" not in system_prompt:
        errors.append("Nenhuma mensagem contém a variável {bug_report}")

    if "TODO" in system_prompt or "TODO" in user_prompt:
        errors.append("Prompt ainda contém TODOs")

    techniques = prompt_data.get("techniques_applied", [])
    if len(techniques) < 2:
        errors.append(f"Mínimo de 2 técnicas requeridas, encontradas: {len(techniques)}")

    return (len(errors) == 0, errors)


def main():
    """Função principal"""
    print_section_header("PUSH DE PROMPTS OTIMIZADOS AO LANGSMITH HUB")

    required_vars = ["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"]
    if not check_env_vars(required_vars):
        return 1

    print(f"Carregando prompt de: {PROMPT_FILE}")
    data = load_yaml(PROMPT_FILE)

    if data is None:
        print("❌ Não foi possível carregar o arquivo YAML")
        return 1

    # O YAML pode ter a chave raiz com o nome do prompt (ex: bug_to_user_story_v2:)
    prompt_data = data.get(PROMPT_NAME, data)

    print("Validando prompt...")
    is_valid, errors = validate_prompt(prompt_data)
    if not is_valid:
        print("❌ Prompt inválido:")
        for error in errors:
            print(f"   - {error}")
        return 1

    print("✓ Prompt válido\n")

    try:
        client = Client()
        success = push_prompt_to_langsmith(client, PROMPT_NAME, prompt_data)
        return 0 if success else 1
    except Exception as e:
        print(f"\n❌ Erro ao fazer push do prompt: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())