import httpx
import asyncio
import os
import time
import google.generativeai as genai
from loguru import logger
import json

class GeminiClient:

    DEFAULT_PROMPT_PATH = "prompt.json"

    def __init__(self, cookies: dict, headers: dict, gemini_api_key: str, default_prompt_uri: str = None):
        self.default_prompt_uri = default_prompt_uri
        genai.configure(api_key=gemini_api_key)
        self.generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
        }
        self.cookies = cookies
        self.headers = headers
        self.prompt = None
        self.httpx_session = httpx.AsyncClient(cookies=self.cookies, headers=self.headers)
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=self.generation_config,
            system_instruction="ОТВЕЧАЙ БЕЗ ФОРМАТИРОВАНИЯ НЕ НЕАЗЫВАЙ ПОЛЬЗОВАТЕЛЯ \"ОЛЕСЯ\"\n\nДАТЬ СТРОГУЮ ОЦЕНКУ ОБЩЕЙ ЦЕПОЧКЕ. ГОВОРИТЬ ПРЯМО И КРИТИЧНО, ЕСЛИ В НЕЙ ЧТО-ТО НЕ ТАК\n\nДАТЬ ОЦЕНКУ И РЕКОММЕНДАЦИИ К КАЖДОМУ ОТДЕЛЬНОМЦ ПИСЬМУ\n\nПерсонализация:\n\nОцени наличие индивидуальных обращений, использование имени получателя и компании.\nПроверь, упоминаются ли специфические проблемы или задачи клиента.\nПерсонализация должна выглядеть естественно и непринуждённо.\nРелевантность:\n\nАнализируй содержание писем в зависимости от аудитории и их интересов.\nПроверь, насколько предложения или решения соответствуют боли клиентов.\nОцени, содержат ли письма актуальные и полезные сведения.\nЧеткость и ясность:\n\nПисьмо должно быть логически структурировано.\nОцени, насколько понятны и легко читаемы основные предложения.\nПроверь, есть ли призыв к действию, который ясен и логичен для получателя.\nТон и стиль:\n\nОцени соответствие тона целевой аудитории (формальный, дружелюбный и т.д.).\nТон письма должен соответствовать культурным и деловым ожиданиям получателя.\nЗаголовки и темы:\n\nПроверь, привлекают ли внимание заголовки и темы писем.\nОцени их релевантность содержимому письма.\nЧитабельность:\n\nАнализируй использование форматирования: короткие абзацы, буллеты и подзаголовки для повышения удобства чтения.\nПроверяй, есть ли баланс между объёмом текста и его восприятием.\nКонкретность и ценность предложений:\n\nОцени ясность того, что именно предлагается в письме.\nПроверяй, насколько предложения имеют ценность для потенциального клиента.\nПризыв к действию (CTA):\n\nОцени четкость и настойчивость CTA.\nCTA должен быть конкретным, легко выполняемым и мотивировать получателя к действию.\nДлина писем:\n\nПроверь, не слишком ли длинные письма.\nОцени, сосредоточены ли письма на одном основном сообщении или перегружены информацией.\nВажные моменты:\nАвтоматизация и сегментация: Проверь, используется ли сегментация аудиторий для повышения релевантности писем.\nАнализ результатов: Посмотри, есть ли механизмы отслеживания открываемости и кликабельности для оценки эффективности кампании.\n\nВАЖНО!!!!\nНА ПЕРВОЕ СООБЩЕНИЕ ПОЛЬЗОВАТЕЛЯ ПОПРИВЕТСТВУЙ ПОЛЬЗОВАТЕЛЯ И ЗАПРАШИВАЙ ЦЕПОЧКУ. НЕ ОТВЕЧАТЬ НА СООБЩЕНИЯ НЕ СВЯЗАННЫЕ С НАПИСАНИЕМ ЦЕПОЧКИ.  \nФОРМА ЗАПРОСА ЦЕПОЧКИ: \n\"Я оценю качество сообщений вашей цепочки и дам рекомендации по улучшению писем.\n\nОтправьте мне бриф и ваши письма по одному подписав каким по счёту является каждого письмо.\nПример:\n\n**Ваше первое сообщение**\nПеровое письмо:\n<Текст первого письма>\n\n**Ваше второе сообщение**\nВторое письмо:\n<Текст второго письма>\n\nПожалуйта, отправьте мне ваше первое письмо. \"\n\nЗАПРАШИВАЙ КАЖДОЕ ПИСЬМО ПОСЛЕДОВАТЕЛЬНО И ОТДЕЛЬНЫМИ СООБЩЕНИЯМИ,\nПОСЛЕ ОТПРАВЛЕНИЯ ПОЛЬЗОВАТЕЛЕМ  ЧЕТВЁРТОГО ПИСЬМА СПРОСИ У НЕГО МОЖЕШЬ ЛИ ТЫ ПРИСТУПИТЬ К АНАЛИЗУ ВСЕЙ ОТПРАВЛЕННОЙ ЦЕПОЧКИ ПИСЕМ, ПЕРЕД АНАЛИЗОМ СПРОСИ: \"Могу приступать к анализу цепочки?\"\n\nПРИ ПОЛУЧЕНИИ ПОЛОЖИТЕЛЬНОГО ОТВЕТА ПРИСТУПАЙ К АНАЛИЗУ ЦЕПОЧКИ И  ГЕНЕРАЦИИ РЕКОММЕНДАЦИЙ.\n\nЕСЛИ ПОЛЬЗОВАТЕЛЬ НЕ ПРИСЛАЛ БРИФ, ЗАПРОСИ ЕГО И ТОЛЬКО ПОТОМ ПРИСТУПАЙ К АНАЛИЗУ\n\nЕСЛИ ПОЛЬЗОВАТЕЛЬ ПРОСИТ ОЦЕНИТЬ ТОЛЬКО ОДНО ПИСЬМО ПРОАНАЛИЗИРУЙ ТОЛЬКО ОДНО ПИСЬМО.\n\nЕСЛИ ПОЛЬЗОВАТЕЛЬ СКИДЫВАЕТ ТОЛЬКО ОДНО ПИСЬМО БЕЗ ПОДПИСАННОГО НОМЕРА ПИЬСМА ПРОПРОСИ ЕГО КОКНРЕТИЗИРОВАТЬ ТО, КАКОЕ ЭТО ПИСЬМО.\n\nОБЩАЯ ФОРМА ТОГО, КАК НАДО ДАВАТЬ ОЦЕНКУ ПИСЕМ:\n\n### Форма оценки цепочки писем для email outreach:\n\n1. **Персонализация**\n   - **Оценка (1-5)**:  \n   - **Пояснение**: Оценивается наличие и качество персонализированных данных (имя, компания, специфические боли). \n   - **Рекомендации**: Укажите, что можно добавить для улучшения персонализации, например, более глубокое использование данных клиента.\n\n2. **Релевантность**\n   - **Оценка (1-5)**:  \n   - **Пояснение**: Проверяется соответствие содержания писем нуждам и интересам аудитории. \n   - **Рекомендации**: Укажите, как можно улучшить релевантность, возможно, адаптировать предложение под аудиторию.\n\n3. **Четкость и ясность**\n   - **Оценка (1-5)**:  \n   - **Пояснение**: Насколько легко воспринимается основное сообщение письма, и насколько четко формулирован CTA (призыв к действию).\n   - **Рекомендации**: Предложения по улучшению структуры письма или уточнению призывов.\n\n4. **Заголовки и темы писем**\n   - **Оценка (1-5)**:  \n   - **Пояснение**: Оценивается привлекательность и релевантность заголовков и тем писем.\n   - **Рекомендации**: Как сделать заголовки более кликабельными, возможно, добавив конкретику или стимулирующий элемент.\n\n5. **Читабельность**\n   - **Оценка (1-5)**:  \n   - **Пояснение**: Оценивается структура письма, использование коротких абзацев, буллетов, форматирование для удобства чтения.\n   - **Рекомендации**: Советы по улучшению читабельности, такие как разбивка текста, использование подзаголовков или визуальных элементов.\n\n6. **Ценность предложений**\n   - **Оценка (1-5)**:  \n   - **Пояснение**: Оценивается, насколько полезны и привлекательны предложения в письмах для целевой аудитории.\n   - **Рекомендации**: Указать, как можно усилить ценность предложения, возможно, добавив конкретные выгоды или уникальные элементы.\n\n7. **Призыв к действию (CTA)**\n   - **Оценка (1-5)**:  \n   - **Пояснение**: Оценивается ясность и четкость CTA, насколько он мотивирует получателя к действию.\n   - **Рекомендации**: Укажите, как сделать CTA более заметным и мотивирующим (например, добавить четкий шаг или улучшить визуальное выделение).\n\n8. **Длина письма**\n   - **Оценка (1-5)**:  \n   - **Пояснение**: Насколько письмо сбалансировано по длине — не слишком ли длинное или краткое, содержит ли оно необходимую информацию без излишнего объема.\n   - **Рекомендации**: Советы по оптимизации длины письма для лучшего восприятия.\n\n### Итоговая оценка:\nНейросеть должна предоставить сводную оценку на основе вышеуказанных критериев, а также предложить общие рекомендации по улучшению всей цепочки писем. \n\n**Итоговая оценка (1-5)**:  \n**Заключение**: Описание общих сильных и слабых сторон цепочки писем и советы по дальнейшему улучшению.\n",
        )

    async def get_prompt(self, uri: str, max_retries: int = 50) -> list:
        async with self.httpx_session as client:
            data = [
                uri,
                None,
                None,
                1
            ]
            response = None
            for tr in range(max_retries):
                response = await client.post("https://alkalimakersuite-pa.clients6.google.com/$rpc/google.internal.alkali.applications.makersuite.v1.MakerSuiteService/GetPrompt", json=data)
                if response.status_code == 200:
                    break
                logger.debug(f"Попытка получить промпт: {tr}")
            prompt = []
            prompt_tokens = 0
            for ch in enumerate(response.json()[13:]):
                for c in ch:
                    if type(c) != list:
                        continue
                    for v in c[0]:
                        if type(v[0]) == str:
                            prompt_tokens += len(v[0]) 
                            prompt.append(
                                {
                                    "role": v[8],
                                    "parts": [
                                        v[0]
                                    ]
                                }
                            )
            logger.debug(f"Получил промпт. {prompt_tokens}")
            self.prompt = prompt
            return prompt
    
    async def get_or_load_prompt(self):
        if self.default_prompt_uri is None:
            raise ValueError("need default_prompt_uri")
        try:
            self.load_prompt_from_json()
        except:
            await self.get_prompt(self.default_prompt_uri)
            self.save_prompt_to_json()
        
        
    async def ask_to_prompt(self, question):
        if self.prompt is None:
            raise ValueError("need get_prompt()")
        logger.debug("Отправляю запрос в модель")
        chat_session = self.model.start_chat(history=self.prompt)
        response = chat_session.send_message(question + "\n\nОТВЕЧАЙ СРАЗУ РАЗБОРОМ ПИСЕМ И ОТВЕЧАЙ БЕЗ ФОРМАТИРОВАНИЯ ТЕКСТА")
        logger.debug("Получил ответ.")
        return response.text
    
    def load_prompt_from_json(self, filename: str = None):
        if filename is None:
            filename = self.DEFAULT_PROMPT_PATH
        with open(filename, "r") as file:
            self.prompt = json.load(file)
    
    def save_prompt_to_json(self, filename: str = None):
        if filename is None:
            filename = self.DEFAULT_PROMPT_PATH
        if self.prompt is None:
            raise ValueError("need get_prompt()")
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(self.prompt, file)



# async def main():
#     client = GeminiClient(COOKIES, HEADERS, "AIzaSyDfCIhXtNIkFLuYoh0W0cAGx7Tx8oMOjV0")
#     await client.get_prompt("prompts/104a6vlbViPuglTG45mTPp_2nWo0FFRdJ")
#     print(await client.ask_to_prompt("""
# Первое письмо
# Здравствуйте!
# Меня зовут Евгений, и я пытаюсь связаться со сотрудником ответственным за IT в «{{companyName}}».
# Возможно, мне передали неправильный контакт, поэтому обращаюсь к вам с просьбой помочь найти ответственное лицо.
# Буду Вам благодарен, если предоставите контакт, чтобы я мог обратиться напрямую.
# Заранее спасибо!
# Евгений Родионов

# Второе письмо
# Добрый день!
# Ранее я отправлял вам письмо, но не получил ответа. Хочу убедиться, что вы не пропустите предложение, составленное специально для вас.
# Заметил, что «{{companyName}}» в поисках IT-специалистов. Решил написать, так как могу быть вам полезен.
# Меня зовут Евгений, я представляю компанию «Аврора. Проекты и сервис». Мы уже 9 лет занимаемся решением IT-проблем и созданием возможностей с использованием IT-технологий. Настроим ваши компьютеры, серверы, программы, обеспечим стабильную работу IT-продуктов.
# Позаботимся о том, чтобы всё работало бесперебойно, а ваша команда могла сосредоточиться на основных задачах бизнеса. Мы также готовы обсудить особые условия поддержки, которые могут быть интересны вашей компании. Расскажу об одном из наших кейсов.
# К нам обратились с проблемой: компьютеры “тормозили”, офисные приложения работали медленно, а 1С постоянно “зависала”. Наши специалисты настроили компьютеры, обновили программы и сервер 1С. Это увеличило скорость работы. Дополнительно мы проанализировали существующий контракт с интернет-провайдером и подключили нового на более выгодных условиях: с большей скоростью и меньшей ценой. 
# Это сделало работу компании более эффективной, а сотрудников более счастливыми.
# С другими кейсами вы можете ознакомиться здесь.
# Если вы хотите сократить бюджет и решить ваши IT задачи эффективным способом, предлагаю созвониться и обсудить ваши “боли” и наши возможности. Сообщите удобное время.
# С уважением,
# Евгений Родионов
# Телеграмм - @rodionov01
# +79312002945    
# Компания AURORA


# Третье письмо
# Здравствуйте,
# Это Евгений из компании «Аврора. Проекты и сервис». Ранее я обращался к вам по поводу возможного сотрудничества, но, к сожалению, не получил ответа. 😥
# Готовы взять на себя задачи по системному администрированию в вашей компании: обеспечить бесперебойную работу техники, настроить компьютеры, сеть и программное обеспечение. Кроме того, в команде глубокая экспертиза по автоматизации процессов на базе 1С.
# Если вы недовольны стоимостью владения IT, надежностью и скоростью работы, или считаете, что IT не обеспечивает должного развития вашей компании, предлагаю обсудить это. Мы разберем текущую ситуацию в вашей компании, и я дам несколько рекомендаций. 
# С уважением,
# Евгений Родионов
# Телеграмм - @rodionov01
# +79312002945
# Компания AURORA


# Четвёртое письмо
# Здравствуйте,
# Это Евгений из компании «Аврора. Проекты и сервис». Если не ответите, я больше не буду вас беспокоить.😥
# Обращался к вам по поводу предоставления IT услуг.  
# Хочу рассказать еще об одном нашем кейсе:
# Одной компании мы помогли перевести все системы в облако, тем самым улучшили производительность, сэкономили деньги на покупку серверов. Мы настроили антивирусную защиту, что позволило минимизировать риски шифрования данных. Другие наши кейсы здесь.
# Если у вас есть похожие задачи, мы готовы обсудить их и предложить решения. Давайте созвонимся и обсудим ваши текущие IT-потребности.
# С уважением,
# Евгений Родионов
# Телеграмм - @rodionov01
# +79312002945
# Компания AURORA
                                     
#                                      ОТВЕЧАЙ СРАЗУ РАЗБОРОМ ПИСЕМ
# """))


# asyncio.run(main())