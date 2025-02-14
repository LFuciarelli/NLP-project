import re
import contractions
from typing import List
from rasa.engine.graph import GraphComponent
from rasa.shared.nlu.constants import TEXT
from rasa.shared.nlu.training_data.message import Message
from rasa.engine.recipes.default_recipe import DefaultV1Recipe

@DefaultV1Recipe.register(
    [DefaultV1Recipe.ComponentType.INTENT_CLASSIFIER], is_trainable=False
)
class Preprocesser(GraphComponent):
    name = "large_number_formatter"
    provides = ["text"]
    requires = []
    defaults = {}
    language_list = ["en"]

    def process(self, messages: List[Message], **kwargs) -> List[Message]:
        for message in messages:
            text = message.get(TEXT)
            if text:

                # Expand contractions
                expanded_text = contractions.fix(text)

                # Format large numbers (10+ digits)
                def format_large_number(match):
                    num = match.group()
                    return "{:,}".format(int(num))

                formatted_text = re.sub(r"\b\d{10,}\b", format_large_number, expanded_text)

                # Convert text to lowercase
                processed_text = formatted_text.lower()

                # Handle operation recognition in cases in which word order is more complex
                processed_text = re.sub(r"increase (.+) by (.+)", r"\1 increased by \2", processed_text)
                processed_text = re.sub(r"decrease (.+) by (.+)", r"\1 decreased by \2", processed_text)
                processed_text = re.sub(r"multiply (.+) by (.+)", r"\1 multiplied by \2", processed_text)
                processed_text = re.sub(r"divide (.+) by (.+)", r"\1 divided by \2", processed_text)

                processed_text = re.sub(r"subtract (.+) from (.+)", r"\1 subtract \2", processed_text)
                processed_text = re.sub(r"difference between (.+) and (.+)", r"\1 minus \2", processed_text)
                processed_text = re.sub(r"sum between (.+) and (.+)", r"\1 plus \2", processed_text)
                processed_text = re.sub(r"sum of (.+) and (.+)", r"\1 plus \2", processed_text)

                message.set(TEXT, processed_text)

        return messages