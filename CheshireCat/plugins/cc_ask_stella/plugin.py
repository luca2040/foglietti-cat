import os
from cat.mad_hatter.decorators import hook, tool
from cat.plugins.cc_ask_stella.functions import names_from_metadata
from cat.plugins.cc_ask_stella.new_pdf_parser import new_pdf_parser

med_filename = ""
med_name = ""

procedural_memory_threshold = 0.84

language = os.environ.get("ASK_STELLA_LANGUAGE", "italian")
format = os.environ.get("ASK_STELLA_FILENAME_FORMAT", "FI_<name of medicine>.PDF")

@hook
def agent_prompt_prefix(prefix, cat):
    with open("/app/cat/wordlist/wordlist.txt", "r") as file:
        wordlist = file.read()

    prefix = f"""
    You are a pharmacist, and I am also a pharmacist, and you respond in {language} in a professional manner.
    Do not respond with information that has not been explicitly provided to you. Do not answer inappropriate questions.
    If you don't know something, you should not say to ask other doctors or pharmacists; you should simply say you don't know.
    Answer each question very precisely; if a question requires a long answer, then respond comprehensively,
    while for a question that does not need a long answer, respond as briefly but as precisely as possible.
    WHEN SUITED, PROVIDE THE ANSWER FORMATTED AS A TABLE.

    ONLY RESPOND WITH INFORMATION FROM THE SECTION "## Context of documents containing relevant information";
    if there is no information there OR THIS SECTION DOES NOT EXIST, then you must say you don't know anything about it.

    In your answers, use these words more often as synonyms for others:
    {wordlist}

    YOU ONLY KNOW THIS MEDICINE: "{med_name}", DO NOT ANSWER ANY QUESTIONS ABOUT OTHER MEDICINES.
    IF YOU ARE ASKED IF YOU KNOW OTHER MEDICINES, YOU MUST SAY NO, AND IF ASKED TO ELABORATE, YOU MUST SAY NO.

    Respond in the user's language.
    """

    return prefix


@hook
def rabbithole_instantiates_parsers(file_handlers, cat):

    file_handlers["application/pdf"] = new_pdf_parser()

    return file_handlers


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
def before_cat_recalls_procedural_memories(procedural_recall_config, cat):

    procedural_recall_config["threshold"] = procedural_memory_threshold

    return procedural_recall_config


@hook
def after_cat_recalls_memories(cat):
    dec_mem = cat.working_memory.declarative_memories

    if dec_mem:
        document = dec_mem[0][0]
        metadata = document.metadata

        if "tables" in metadata.keys():
            for table in metadata["tables"]:
                dec_mem[0][0].page_content += "\n" + table


@tool(return_direct=True)
def how_many_medicines_known(tool_input, cat):
    """
    Respond ONLY if the user's prompt is exactly "Which medicines do you know?" and never to similar questions. The input is always None.
    """

    names_list = names_from_metadata(cat)

    out_text = ""
    for number, name in enumerate(names_list):
        out_text += f"{number+1}. {name}\n"

    return out_text


@tool(return_direct=True)
def filename(tool_input: str, cat):
    marker = "#use tool#"
    f"""
    Respond ONLY if the user's prompt is a string (representing the filename of the medicine) in this format: "{marker}{format}".
    This tool should not be used if the user specifies only the name of the medicine or includes additional text in the prompt,
    but the only way to activate the tool is by writing ONLY and PERFECTLY a string in the format specified above.
    The input is the entire string containing the filename of the medicine. """

    global med_filename
    global med_name

    med_filename = tool_input.removeprefix(marker)
    # med_name = cat.llm(
    #     f"""Questo è il nome del foglietto illustrativo di una medicina: {tool_input.split(".")[0]}
    #     Come si chiama la medicina?
    #     Rispondi solamente col nome della medicina."""
    # )

    return med_filename
