from cat.mad_hatter.decorators import hook, tool
from cat.plugins.CC_plugin_foglietti_illustrativi.functions import *
from cat.plugins.CC_plugin_foglietti_illustrativi.new_pdf_parser import new_pdf_parser


med_name = ""


@hook
def agent_prompt_prefix(prefix, cat):

    prefix = """
    Sei un farmacista, e rispondi in modo professionale.
    Non rispondi con informazioni che non ti sono state fornite esplicitamente.
    Non rispondi a domande inappropriate.
    Ad ogni domanda rispondi nel modo più completo e preciso possibile.
    """

    return prefix


@hook
def rabbithole_instantiates_parsers(file_handlers, cat):

    file_handlers["application/pdf"] = new_pdf_parser()

    return file_handlers


@hook
def before_cat_recalls_declarative_memories(declarative_recall_config, cat):
    global med_name
    medicine = med_name

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

    if dec_mem:
        document = dec_mem[0][0]

        metadata = document.metadata

        if "tables" in metadata.keys():
            for table in metadata["tables"]:
                dec_mem[0][0].page_content += "\n" + table


@tool(return_direct=True)
def how_many_medicines_known(tool_input, cat):
    """Reply only to the question "How many medicines you know?" or to others which are stricly similar.
    Ignore generic questions about medicines.
    Input is always None"""

    names_list = names_from_metadata(cat)

    out_text = ""
    for number, name in enumerate(names_list):
        out_text += f"{number+1}. {name}\n"

    return out_text


@tool(return_direct=True)
def filename(tool_input, cat):
    """Reply to a file name, ONLY if specified using the word "file"
    Input is the file name"""

    global med_name
    med_name = tool_input

    return med_name
