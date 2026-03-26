from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request, session
from flask_cors import CORS
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import AssistantV2

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.getenv("CARDIOIA_DB_PATH", BASE_DIR / "cardioia_logs.sqlite3"))

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "cardioia-fase5-dev-secret")
app.config["JSON_AS_ASCII"] = False
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=False)

WA_API_KEY = os.getenv("WA_API_KEY")
WA_URL = os.getenv("WA_URL")
WA_ASSISTANT_ID = os.getenv("WA_ASSISTANT_ID")
WA_VERSION = os.getenv("WA_VERSION", "2021-06-14")
USE_LOCAL_STUB = os.getenv("USE_LOCAL_STUB", "true").strip().lower() == "true"


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_db_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS conversation_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                user_message TEXT NOT NULL,
                assistant_response TEXT NOT NULL,
                top_intent TEXT,
                entities_json TEXT,
                urgency_level TEXT,
                source TEXT NOT NULL
            )
            """
        )
        conn.commit()


def save_log(
    *,
    user_message: str,
    assistant_response: str,
    top_intent: str | None,
    entities: list[dict[str, Any]],
    urgency_level: str | None,
    source: str,
) -> None:
    with get_db_connection() as conn:
        conn.execute(
            """
            INSERT INTO conversation_log
                (created_at, user_message, assistant_response, top_intent, entities_json, urgency_level, source)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.now(timezone.utc).isoformat(),
                user_message,
                assistant_response,
                top_intent,
                json.dumps(entities, ensure_ascii=False),
                urgency_level,
                source,
            ),
        )
        conn.commit()


def get_assistant_client() -> AssistantV2:
    if not (WA_API_KEY and WA_URL and WA_ASSISTANT_ID):
        raise RuntimeError(
            "Credenciais do Watson Assistant ausentes. Configure WA_API_KEY, WA_URL e WA_ASSISTANT_ID."
        )

    authenticator = IAMAuthenticator(WA_API_KEY)
    assistant = AssistantV2(version=WA_VERSION, authenticator=authenticator)
    assistant.set_service_url(WA_URL)
    return assistant


def create_wa_session_if_needed() -> str:
    current_session_id = session.get("wa_session_id")
    if current_session_id:
        return current_session_id

    assistant = get_assistant_client()
    response = assistant.create_session(assistant_id=WA_ASSISTANT_ID).get_result()
    session_id = response["session_id"]
    session["wa_session_id"] = session_id
    return session_id


def delete_wa_session_if_exists() -> None:
    current_session_id = session.get("wa_session_id")
    if not current_session_id or not (WA_API_KEY and WA_URL and WA_ASSISTANT_ID):
        session.pop("wa_session_id", None)
        return

    assistant = get_assistant_client()
    try:
        assistant.delete_session(
            assistant_id=WA_ASSISTANT_ID,
            session_id=current_session_id,
        ).get_result()
    finally:
        session.pop("wa_session_id", None)


def extract_text_from_generic(generic_items: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    for item in generic_items:
        response_type = item.get("response_type")
        if response_type == "text" and item.get("text"):
            parts.append(item["text"])
        elif response_type == "option" and item.get("title"):
            options = item.get("options") or []
            option_titles = [opt.get("label", "") for opt in options if opt.get("label")]
            suffix = f" Opções: {', '.join(option_titles)}." if option_titles else ""
            parts.append(f"{item['title']}{suffix}")
    return "\n".join(part.strip() for part in parts if part.strip())


def normalize_entities(output_entities: list[dict[str, Any]]) -> list[dict[str, str]]:
    normalized: list[dict[str, str]] = []
    for entity in output_entities:
        normalized.append(
            {
                "entity": str(entity.get("entity", "")),
                "value": str(entity.get("value", "")),
            }
        )
    return normalized


def infer_urgency_level(top_intent: str | None, entities: list[dict[str, str]]) -> str:
    urgent_signals = {
        ("sintoma", "dor_no_peito"),
        ("sintoma", "falta_de_ar"),
        ("sintoma", "desmaio"),
    }
    if top_intent == "emergencia":
        return "alta"
    if any((item["entity"], item["value"]) in urgent_signals for item in entities):
        return "alta"
    if top_intent in {"informar_sintoma", "informar_pressao"}:
        return "moderada"
    return "baixa"


def call_watson_assistant(user_message: str) -> dict[str, Any]:
    session_id = create_wa_session_if_needed()
    assistant = get_assistant_client()

    response = assistant.message(
        assistant_id=WA_ASSISTANT_ID,
        session_id=session_id,
        input={
            "message_type": "text",
            "text": user_message,
        },
    ).get_result()

    output = response.get("output", {})
    intents = output.get("intents", [])
    entities = normalize_entities(output.get("entities", []))
    generic = output.get("generic", [])

    reply_text = extract_text_from_generic(generic)
    top_intent = intents[0]["intent"] if intents else None
    urgency_level = infer_urgency_level(top_intent, entities)

    if not reply_text:
        reply_text = (
            "Recebi sua mensagem, mas o fluxo do Watson Assistant não retornou um texto "
            "de saída configurado para esta situação."
        )

    return {
        "response": reply_text,
        "top_intent": top_intent,
        "entities": entities,
        "urgency_level": urgency_level,
        "source": "watson_assistant",
    }


def call_local_stub(user_message: str) -> dict[str, Any]:
    text = user_message.strip().lower()

    def has_any(words: list[str]) -> bool:
        return any(word in text for word in words)

    entities: list[dict[str, str]] = []
    top_intent = "anything_else"

    if has_any(["dor no peito", "aperto no peito", "falta de ar", "desmaio", "suor frio"]):
        top_intent = "emergencia"
        if "dor no peito" in text or "aperto no peito" in text:
            entities.append({"entity": "sintoma", "value": "dor_no_peito"})
        if "falta de ar" in text:
            entities.append({"entity": "sintoma", "value": "falta_de_ar"})
        if "desmaio" in text:
            entities.append({"entity": "sintoma", "value": "desmaio"})
        reply = (
            "⚠️ Sinais como dor no peito forte, falta de ar importante, desmaio ou suor frio "
            "podem indicar urgência.\n\n"
            "Procure atendimento imediato ou acione o serviço de emergência. "
            "Eu posso ajudar a organizar o que você está sentindo, mas não substituo avaliação médica."
        )
    elif has_any(["oi", "olá", "ola", "bom dia", "boa tarde", "boa noite"]):
        top_intent = "saudacao"
        reply = (
            "Olá! Sou o protótipo do Assistente Cardiológico Conversacional.\n\n"
            "Posso orientar sobre sintomas, pressão arterial, exames cardíacos, preparo para consulta "
            "e hábitos saudáveis. Em caso de urgência, procure atendimento imediato."
        )
    elif has_any(["palpitação", "palpitacao", "coração acelerado", "taquicardia"]):
        top_intent = "informar_sintoma"
        entities.append({"entity": "sintoma", "value": "palpitacao"})
        reply = (
            "Palpitações podem ter várias causas, como ansiedade, cafeína, esforço, febre ou arritmias.\n\n"
            "Anote quando acontece, quanto tempo dura, se vem com tontura, dor no peito ou falta de ar, "
            "e leve essas informações à consulta."
        )
    elif has_any(["tontura", "tonto", "cabeça leve"]):
        top_intent = "informar_sintoma"
        entities.append({"entity": "sintoma", "value": "tontura"})
        reply = (
            "Tontura pode se relacionar a pressão alterada, desidratação, efeito de medicamentos ou outras causas.\n\n"
            "Se houver queda, desmaio, dor no peito ou falta de ar, trate como urgência."
        )
    elif has_any(["pressão", "pressao", "14 por 9", "15 por 10", "baixa", "alta"]):
        top_intent = "informar_pressao"
        if has_any(["alta", "14 por 9", "15 por 10", "16 por 10"]):
            entities.append({"entity": "pressao_estado", "value": "alta"})
            reply = (
                "Pressão elevada merece acompanhamento.\n\n"
                "Repita a medida após alguns minutos de repouso, evite interpretar um valor isolado "
                "como diagnóstico e procure orientação profissional se os valores estiverem persistentes "
                "ou se vierem junto com sintomas."
            )
        elif "baixa" in text:
            entities.append({"entity": "pressao_estado", "value": "baixa"})
            reply = (
                "Pressão baixa pode causar tontura, fraqueza e mal-estar.\n\n"
                "Hidrate-se, sente-se ou deite-se se estiver tonto e procure avaliação se os sintomas forem intensos "
                "ou recorrentes."
            )
        else:
            entities.append({"entity": "pressao_estado", "value": "normal"})
            reply = (
                "A interpretação da pressão arterial depende do contexto, da técnica de medida "
                "e do histórico da pessoa.\n\n"
                "O ideal é observar medições repetidas e discutir o resultado com um profissional de saúde."
            )
    elif has_any(["eletrocardiograma", "ecg", "ecocardiograma", "eco", "holter", "mapa", "raio x", "raiox"]):
        top_intent = "explicar_exame"
        if has_any(["eletrocardiograma", "ecg"]):
            entities.append({"entity": "exame", "value": "eletrocardiograma"})
            reply = "O eletrocardiograma registra a atividade elétrica do coração e pode ajudar a identificar ritmo, frequência e alterações elétricas."
        elif has_any(["ecocardiograma", "eco"]):
            entities.append({"entity": "exame", "value": "ecocardiograma"})
            reply = "O ecocardiograma usa ultrassom para avaliar estruturas do coração, funcionamento das válvulas e força de bombeamento."
        elif "holter" in text:
            entities.append({"entity": "exame", "value": "holter"})
            reply = "O Holter monitora os batimentos cardíacos por 24 horas ou mais para investigar palpitações, arritmias e sintomas intermitentes."
        elif "mapa" in text:
            entities.append({"entity": "exame", "value": "mapa"})
            reply = "O MAPA acompanha a pressão arterial ao longo do dia e da noite, ajudando a entender variações fora do consultório."
        else:
            entities.append({"entity": "exame", "value": "raio_x_torax"})
            reply = "O raio-X de tórax ajuda a avaliar o tamanho do coração e sinais pulmonares, mas não substitui exames específicos para função cardíaca."
    elif has_any(["remédio", "remedio", "medicamento"]):
        top_intent = "medicamentos"
        reply = (
            "Não interrompa medicamento cardíaco por conta própria.\n\n"
            "Se esqueceu uma dose ou teve efeito colateral, registre o nome do remédio, o horário e o sintoma percebido, "
            "e confirme a conduta com o profissional que acompanha seu caso."
        )
    elif has_any(["consulta", "cardiologista", "o que levar", "preparar"]):
        top_intent = "preparo_consulta"
        reply = (
            "Para a consulta, leve exames recentes, lista de medicamentos com doses, anotações de sintomas, "
            "horários em que ocorrem e valores de pressão, se você tiver."
        )
    elif has_any(["exercício", "exercicio", "sal", "alimentação", "alimentacao", "coração saudável", "coracao saudavel"]):
        top_intent = "habitos_saudaveis"
        reply = (
            "Cuidar do coração envolve rotina: alimentação equilibrada, controle do sal, atividade física orientada, "
            "sono adequado, não fumar e seguir o plano terapêutico indicado."
        )
    elif has_any(["obrigado", "valeu", "agradecido"]):
        top_intent = "agradecimento"
        reply = "De nada! Quando quiser, posso continuar com sintomas, exames, pressão arterial ou preparo para consulta."
    elif has_any(["tchau", "até mais", "encerrar", "fim"]):
        top_intent = "despedida"
        reply = "Até mais! Cuide-se e lembre-se: em caso de sinais de urgência, procure atendimento imediato."
    else:
        reply = (
            "Não entendi completamente sua solicitação.\n\n"
            "Tente reformular em frases como: 'estou com palpitação', 'minha pressão está alta', "
            "'o que é ecocardiograma' ou 'como me preparar para a consulta?'."
        )

    urgency_level = infer_urgency_level(top_intent, entities)
    return {
        "response": reply,
        "top_intent": top_intent,
        "entities": entities,
        "urgency_level": urgency_level,
        "source": "local_stub",
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify(
        {
            "status": "ok",
            "use_local_stub": USE_LOCAL_STUB,
            "watson_configured": bool(WA_API_KEY and WA_URL and WA_ASSISTANT_ID),
        }
    )


@app.route("/api/chat", methods=["POST"])
def chat():
    payload = request.get_json(silent=True) or {}
    user_message = str(payload.get("message", "")).strip()

    if not user_message:
        return jsonify({"error": "Envie uma mensagem válida."}), 400

    try:
        if WA_API_KEY and WA_URL and WA_ASSISTANT_ID:
            result = call_watson_assistant(user_message)
        elif USE_LOCAL_STUB:
            result = call_local_stub(user_message)
        else:
            return (
                jsonify(
                    {
                        "error": (
                            "Credenciais do Watson Assistant não configuradas e modo local desativado."
                        )
                    }
                ),
                500,
            )
    except Exception as exc:
        if USE_LOCAL_STUB:
            result = call_local_stub(user_message)
            result["source"] = "local_stub_after_error"
            result["response"] = (
                "O backend encontrou um problema ao tentar acessar o Watson Assistant. "
                "Para manter a demonstração funcional, respondi com o fluxo local.\n\n"
                f"Detalhe técnico: {exc}"
            )
        else:
            return jsonify({"error": f"Falha ao consultar o Watson Assistant: {exc}"}), 500

    save_log(
        user_message=user_message,
        assistant_response=result["response"],
        top_intent=result["top_intent"],
        entities=result["entities"],
        urgency_level=result["urgency_level"],
        source=result["source"],
    )
    return jsonify(result)


@app.route("/api/reset", methods=["POST"])
def reset_conversation():
    delete_wa_session_if_exists()
    return jsonify({"status": "ok", "message": "Sessão reiniciada com sucesso."})


@app.route("/api/history", methods=["GET"])
def history():
    limit = min(int(request.args.get("limit", 20)), 100)
    with get_db_connection() as conn:
        rows = conn.execute(
            """
            SELECT created_at, user_message, assistant_response, top_intent, entities_json, urgency_level, source
            FROM conversation_log
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    data = []
    for row in rows:
        data.append(
            {
                "created_at": row["created_at"],
                "user_message": row["user_message"],
                "assistant_response": row["assistant_response"],
                "top_intent": row["top_intent"],
                "entities": json.loads(row["entities_json"] or "[]"),
                "urgency_level": row["urgency_level"],
                "source": row["source"],
            }
        )

    return jsonify({"items": data})


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
