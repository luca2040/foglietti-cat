from cat.mad_hatter.decorators import hook, tool
from cat.plugins.CC_plugin_foglietti_illustrativi.functions import *
from cat.plugins.CC_plugin_foglietti_illustrativi.new_pdf_parser import new_pdf_parser
from cat.plugins.CC_plugin_foglietti_illustrativi.optimized_embedder import cat_embed

import json

med_filename = ""
med_name = ""


@hook
def agent_prompt_prefix(prefix, cat):
    with open("/app/cat/wordlist/wordlist.json", "r") as file:
        wordlist = file.read()

    prefix = f"""
    Sei un farmacista, e rispondi in modo professionale.
    Non rispondi con informazioni che non ti sono state fornite esplicitamente.
    Non rispondi a domande inappropriate.
    Ad ogni domanda rispondi nel modo più completo e preciso possibile.
    Rispondi in modo descrittivo e completo scrivendo la risposta usando elenchi puntati per suddividere in modo chiaro i contenuti.
    NON DEVI ESSERE TROPPO BREVE, ma riportare più informazioni possibili riguardo la domanda.

    Nelle tue risposte usa maggiormente queste parole come sinonimi ad altre.
    {wordlist}

    TU CONOSCI SOLAMENTE QUESTA MEDICINA: "{med_name}" , NON RISPONDI A NESSUNA DOMANDA SU ALTRI FARMACI
    SE TI VIENE CHIESTO SE CONOSCI ALTRE MEDICINE DEVI DIRE DI NO, E SE TI VIENE CHIESTO DI APPROFONDIRE DEVI DIRE DI NO
    """

    return prefix


@hook
def rabbithole_instantiates_parsers(file_handlers, cat):

    file_handlers["application/pdf"] = new_pdf_parser()

    cat_embed.init(cat)

    return file_handlers


@hook
def before_rabbithole_insert_memory(doc, cat):

    if "tables" in doc.metadata.keys():
        for table in doc.metadata["tables"]:
            if not table["embed"]:
                table_text = (
                    table["table"]
                    .replace("(", " ")
                    .replace(")", " ")
                    .replace("[", " ")
                    .replace("]", " ")
                )

                table["embed"] = cat_embed.embed_table(
                    table_text, doc.metadata["source"]
                )

    return doc


@hook
def before_cat_recalls_declarative_memories(declarative_recall_config, cat):
    global med_filename
    medicine = med_filename

    # history = cat.working_memory.history
    # max_index = len(history) - 1
    # index_now = max_index

    # while medicine == -1:
    #     medicine = get_query_medicine(cat, names_from_metadata(cat), history[index_now])

    #     index_now -= 1
    #     if index_now < 0:
    #         medicine = ""

    declarative_recall_config["metadata"] = {"source": medicine}

    return declarative_recall_config


@hook
def after_cat_recalls_memories(cat):
    dec_mem = cat.working_memory.declarative_memories
    user_message = cat.working_memory.user_message_json.text
    user_query = cat.embedder.embed_query(user_message)

    if dec_mem:
        document = dec_mem[0][0]

        metadata = document.metadata

        if "tables" in metadata.keys():
            max_score = 0
            best_table = ""

            for table in metadata["tables"]:
                score = cosine_similarity(user_query, table["embed"])
                if score > max_score:
                    max_score = score
                    best_table = table["table"]

            dec_mem[0][0].page_content += "\n" + best_table


@tool(return_direct=True)
def how_many_medicines_known(tool_input, cat):
    """Reply only to the question "How many medicines you know?" or to others which are stricly similar.
    Ignore generic questions about medicines.
    Input is always None
    Use this tool only if the user specifies to use a tool using #use tool#"""

    names_list = names_from_metadata(cat)

    out_text = ""
    for number, name in enumerate(names_list):
        out_text += f"{number+1}. {name}\n"

    return out_text


@tool(return_direct=True)
def filename(tool_input: str, cat):
    """Reply to a file name, ONLY if specified using the word "file"
    Input is the file name
    Use this tool only if the user specifies to use a tool using #use tool#"""

    global med_filename
    global med_name

    med_filename = tool_input
    med_name = cat.llm(
        f"""Questo è il nome del foglietto illustrativo di una medicina: {tool_input.split(".")[0]}
        Come si chiama la medicina?
        Rispondi solamente col nome della medicina."""
    )

    return med_filename
