from dataclasses import dataclass, asdict
import json
import os
import subprocess
from typing import Sequence
import uuid

from dotenv import find_dotenv, load_dotenv
from langchain_core.language_models import LanguageModelLike
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import BaseTool, tool
from langchain_gigachat.chat_models import GigaChat
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver
from mail import fetch_recent_emails


load_dotenv(find_dotenv())
model = GigaChat(
    model="GigaChat-2-Max",
    verify_ssl_certs=False,
)

PATH_FILE = "C:/Users/smoly/LangChain/LangChain-and-GigaChat/Zadanie-5-Obrazets-akta-1-1.png"

@dataclass
class Bank:
    """Банковские реквизиты заказчика"""
    name: str  # наименование банка
    current_account: str  # расчётный счёт
    corporate_account: str  # корреспондентский счёт

@dataclass
class Customer:
    """Заказчик"""
    name: str  # полное название юридического лица, наприемер, ООО «Рога и копыта»
    INN: str  # ИНН
    KPP: str  # ОГРН или ОГРНИП
    address: str  # юридический адрес
    signatory: str  # подписант
    bank: Bank  # банковские реквизиты заказчика

@dataclass
class Job:
    task: str  # выполненная задача
    count: int  # количество
    unit: str  # единица измерения
    price: int  # цена за задачу
    price_total: int  # общая стоимость
    price_nds: int  # стоимость с НДС
    price_nds_18: int  # стоимость с НДС 18%
    price_nds_10: int  # стоимость с НДС 10%

def generate_pdf_act(customer: Customer, jobs: list[Job]) -> None:
    """
    Генерирует PDF-акт, в котором заполнены данные
    клиента, его банковские реквизиты, а также выполненные задачи

    Args:
        customer (Customer): данные клиента
        jobs (list[Job]): список выполненных задач для внесения в акт

    Returns:
        None
    """
    print(f"generate_pdf_act({asdict(customer)}, {list(map(lambda j: asdict(j), jobs))})")

class LLMAgent:
    def __init__(self, model: LanguageModelLike, tools: Sequence[BaseTool]):
        self._model = model
        self._agent = create_react_agent(
            model,
            tools=tools,
            checkpointer=InMemorySaver())
        self._config: RunnableConfig = {
                "configurable": {"thread_id": uuid.uuid4().hex}}

    def upload_file(self, file):
        file_uploaded_id = self._model.upload_file(file).id_  # type: ignore
        return file_uploaded_id

    def invoke(
        self,
        content: str,
        attachments: list[str]|None=None,
        temperature: float=0.1
    ) -> str:
        """Отправляет сообщение в чат"""
        message: dict = {
            "role": "user",
            "content": content,
            **({"attachments": attachments} if attachments else {}) 
        }
        return self._agent.invoke(
            {
                "messages": [message],
                "temperature": temperature
            },
            config=self._config)["messages"][-1].content
    
def main():
    system_prompt = (
        "Твоя задача спросить у пользователя, что он хочет сгенерировать — акт или счёт или оба документа. "
        "Затем нужно сгенерировать акт или счёт, для этого тебе надо взять реквизиты "
        "контрагента из приложенного файла, а также запроси работы для включения в "
        "акт (наименования задач и их стоимость), работ может быть несколько. "
        "Если пользователь указывает в качетсве работы курс, то для документов берём одну работу, в точности такую "
        "/'Услуги по подготовке товара к продаже/', стоимостью 1750 руб."
        "Никакие данные не придумывай, всё необходимое строго запроси у "
        "пользователя. Мои реквизиты заказчика не запрашивай, они есть в моём коде. "
        "Имя и отчество подписанта сокращаем до одной первой буквы, "
        "например, Иванов А.Е. "
        "Название компании оборачиваем в кавычки ёлочкой, например, "
        "ООО «Рога и копыта», то есть до названия компании ставим « и после названия "
        "ставим »."
    )
    model = GigaChat(
    model="GigaChat-2-Max",
    verify_ssl_certs=False,
    )
    agent = LLMAgent(model, tools=[generate_pdf_act])
    file_uploaded_id= agent.upload_file(open(PATH_FILE, "rb"))
    agent_response = agent.invoke(content=system_prompt, attachments=[file_uploaded_id])

    print("Agent response: ", agent_response)
    while(True):
        prompt = input("Prompt: ")
        llm_response = agent.invoke(content=prompt)
        print("Agent response: ", llm_response)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nПока, буду ждать ещё!")