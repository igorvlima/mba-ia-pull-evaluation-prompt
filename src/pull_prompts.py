"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull do prompt semente do desafio (leonanluppi/bug_to_user_story_v1)
3. Salva localmente em prompts/bug_to_user_story_v1.yml
"""

import os
import sys
from dotenv import load_dotenv
from langsmith import Client
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()

PROMPT_NAME = "leonanluppi/bug_to_user_story_v1"
OUTPUT_FILE = "prompts/bug_to_user_story_v1.yml"


def extract_messages(prompt) -> list:
    """
    Extrai os templates das mensagens de um ChatPromptTemplate.

    Cada mensagem de um ChatPromptTemplate é um MessagePromptTemplate
    (ex: SystemMessagePromptTemplate) cujo conteúdo está em `.prompt.template`.
    """
    templates = []
    for message in prompt.messages:
        if hasattr(message, "prompt") and hasattr(message.prompt, "template"):
            templates.append(message.prompt.template)
        else:
            # Fallback: mensagem já em texto puro
            templates.append(str(message))
    return templates


def pull_prompts_from_langsmith():
    print_section_header(f"PULL DO PROMPT: {PROMPT_NAME}")

    client = Client()

    print(f"Conectado ao LangSmith. Puxando prompt...")

    # dangerously_pull_public_prompt=True é obrigatório quando o identificador
    # tem dono explícito (owner/nome): o LangSmith bloqueia o pull de prompts
    # de terceiros por padrão, pois podem ser objetos LangChain serializados.
    prompt = client.pull_prompt(
        PROMPT_NAME,
        dangerously_pull_public_prompt=True,
    )

    messages = extract_messages(prompt)
    if len(messages) < 2:
        print(f"⚠️  Prompt puxado com apenas {len(messages)} mensagem(ns)")

    # Monta o YAML no mesmo formato esperado por push_prompts.py e pelos testes
    # (system_prompt + user_prompt + metadados).
    data = {
        "bug_to_user_story_v1": {
            "description": "Prompt para converter relatos de bugs em User Stories",
            "system_prompt": messages[0] if messages else "",
            "user_prompt": messages[1] if len(messages) > 1 else "{bug_report}",
            "version": "v1",
            "tags": ["bug-analysis", "user-story", "product-management"],
        }
    }

    if save_yaml(data, OUTPUT_FILE):
        print(f"✓ Prompt salvo em {OUTPUT_FILE}")
    else:
        print("❌ Falha ao salvar prompt")
        return False

    return True


def main():
    """Função principal"""
    print_section_header("PULL DE PROMPTS DO LANGSMITH HUB")

    required_vars = ["LANGSMITH_API_KEY"]
    if not check_env_vars(required_vars):
        return 1

    try:
        success = pull_prompts_from_langsmith()
        return 0 if success else 1
    except Exception as e:
        print(f"\n❌ Erro ao fazer pull do prompt: {e}")
        print("\nVerifique:")
        print("- LANGSMITH_API_KEY está configurada corretamente no .env")
        print("- Sua conexão com a internet está funcionando")
        return 1


if __name__ == "__main__":
    sys.exit(main())