import copy
import json
from pathlib import Path
from typing import Any, Dict, List, Optional


def extract_examples_from_request(details: Dict[str, Any]) -> Optional[Dict]:
    """
    Extrai exemplos do corpo da requisição em documentos OpenAPI.

    Args:
        details: Detalhes do endpoint no formato OpenAPI

    Returns:
        Dicionário com o exemplo ou None se não encontrado
    """
    request_body = details.get("requestBody", {})
    content = request_body.get("content", {}) if request_body else {}

    if not content:
        return None

    for media_content in content.values():
        # Procura por exemplos diretamente no content
        if "examples" in media_content:
            first_example = next(iter(media_content["examples"].values()))
            return first_example.get("value")

        if "example" in media_content:
            return media_content["example"]

        # Procura no schema
        schema = media_content.get("schema", {})
        if "example" in schema:
            return schema["example"]

        if "json_schema_extra" in schema and "example" in schema["json_schema_extra"]:
            return schema["json_schema_extra"]["example"]

    return None


def detect_api_prefix(openapi_data: Dict[str, Any]) -> str:
    """
    Detecta automaticamente o prefixo da API a partir dos caminhos.

    Args:
        openapi_data: Documento OpenAPI completo

    Returns:
        String contendo o prefixo detectado ou string vazia
    """
    paths = openapi_data.get("paths", {})
    if not paths:
        return ""

    first_path = next(iter(paths), "")
    parts = [p for p in first_path.split("/") if p]

    return parts[0] if parts and not parts[0].startswith("{") else ""


def openapi_to_postman(
    openapi_path: Optional[str] = None, postman_path: Optional[str] = None
) -> None:
    """
    Converte um arquivo OpenAPI em uma coleção Postman.

    Args:
        openapi_path: Caminho do arquivo OpenAPI (opcional)
        postman_path: Caminho onde salvar a coleção Postman (opcional)

    Raises:
        FileNotFoundError: Se o arquivo OpenAPI não for encontrado
        json.JSONDecodeError: Se o arquivo OpenAPI não for um JSON válido
    """
    # Define caminhos padrão usando Path para melhor manipulação
    openapi_path = openapi_path or "scripts/generate_postman_collection/openapi.json"
    postman_path = postman_path or "postman_collection.json"

    # Validar existência do arquivo
    if not Path(openapi_path).exists():
        raise FileNotFoundError(f"Arquivo OpenAPI não encontrado: {openapi_path}")

    # Carrega o arquivo OpenAPI
    try:
        with open(openapi_path, "r", encoding="utf-8") as f:
            openapi = json.load(f)
    except json.JSONDecodeError:
        raise json.JSONDecodeError(f"Arquivo OpenAPI inválido: {openapi_path}", "", 0)

    # Cria a coleção Postman
    collection = {
        "info": {
            "name": openapi.get("info", {}).get("title", "API Collection"),
            "description": openapi.get("info", {}).get("description", ""),
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
        },
        "item": [],
    }

    default_headers = [
        {"key": "Content-Type", "value": "application/json"},
        {"key": "Authorization", "value": "Bearer {{token}}"},
    ]

    # Organiza os endpoints por tags
    tag_folders: Dict[str, List] = {}

    for path, methods in openapi.get("paths", {}).items():
        for method, details in methods.items():
            # Ignora métodos especiais
            if method.startswith("x-"):
                continue

            tags = details.get("tags") or ["Geral"]
            tag = tags[0]

            # Cria o item do Postman
            item = {
                "name": details.get("summary") or f"{method.upper()} {path}",
                "description": details.get("description", ""),
                "request": {
                    "method": method.upper(),
                    "header": copy.deepcopy(default_headers),
                    "url": {
                        "raw": f"{{{{base_url}}}}/{path.lstrip('/')}",
                        "host": ["{{base_url}}"],
                        "path": [p for p in path.strip("/").split("/") if p],
                    },
                },
            }

            # Adiciona exemplos no corpo apenas para métodos apropriados
            if method.lower() in ["post", "put", "patch"]:
                example_body = extract_examples_from_request(details)
                if example_body is not None:
                    item["request"]["body"] = {
                        "mode": "raw",
                        "raw": json.dumps(example_body, ensure_ascii=False, indent=2),
                        "options": {"raw": {"language": "json"}},
                    }

            # Organiza por tag
            tag_folders.setdefault(tag, []).append(item)

    # Adiciona as pastas de tags à coleção
    for tag in sorted(tag_folders.keys()):
        collection["item"].append({"name": tag, "item": tag_folders[tag]})

    # Garante que o diretório de destino exista
    Path(postman_path).parent.mkdir(parents=True, exist_ok=True)

    # Salva a coleção Postman
    with open(postman_path, "w", encoding="utf-8") as f:
        json.dump(collection, f, indent=2, ensure_ascii=False)

    print(f"Coleção Postman gerada com sucesso: {postman_path}")


if __name__ == "__main__":
    openapi_to_postman()
