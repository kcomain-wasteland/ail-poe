"""
* May you do good and not evil
* May you find forgiveness for yourself and forgive others
* May you share freely, never taking more than you give.

    -- SQLite Source Code

ail: AI Literacy Chatbot 2nd Generation
"""

from os import getenv
from time import sleep

from dotenv import load_dotenv

from . import logging
from .data import Data
from .api import Client
from .tools import handle
from .state import History
from .commands import Commands
from .args import parse as parse_arguments


## Code
def app():
    args = parse_arguments()
    logging.configure_logging(args)
    logger = logging.get_logger("main")

    run_app = True
    history = History()
    commands = Commands(history)

    logger.debug("Loading credentials from .env")
    load_dotenv()

    data = Data()
    client = Client(getenv("COHERE_API_KEY"), data, history, args.document_mode)

    tool_results = None
    repeat = False

    while run_app:
        if not repeat:
            try:
                tool_results = None
                user_in = input("User: ")
            except EOFError:
                print()
                break
        else:
            repeat = not repeat
        if len(user_in.strip()) < 1:
            # user didn't write anything, skip sending requests
            continue

        if commands.check(user_in):
            # handle commands
            out = commands.run(user_in)
            if out == "stop":
                run_app = False
            continue

        skip_rest = False
        print("Bot: ", end="")
        sleep(0.2)
        for event in client.send(user_in, tool_results):
            if skip_rest:
                continue
            logger.debug(event)
            match event.event_type:
                case "text-generation":
                    print(event.text, end="")

                case "tool-calls-generation":
                    repeat = True
                    logger.info("tool calls initiated")
                    print("(tool requested, no output this turn)")
                    tool_results = handle(data, event.tool_calls)
                    break

                case "stream-end":
                    logger.info("ended with reason: %s", event.finish_reason)

                    # HACK: because i cannot deal with this anymore
                    try:
                        for citation in event.response.get("citations", []):
                            logger.info(f"Citation: %s", citation)
                        history.set(event.response.get("chat_history"))
                    except AttributeError:
                        for citation in event.response.citations or []:
                            logger.info(f"Citation: %s", citation)
                        history.set(event.response.chat_history)
                    print("\n")
