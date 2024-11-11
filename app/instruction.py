"""
File: instruction.py
Author: Dmitry Ryumin and Alexandr Axyonov
Description: Project instructions for the Gradio app.
License: MIT License
"""

# Importing necessary components for the Gradio app

INSTRUCTION_TEXT = """\
<div class="instructions">
    <p>Вам предстоит оценить качество приложения EdFitter – новой рекомендательной системы, которая советует студентам выборные курсы исходя из их карьерных запросов.</p>
    <ul>
        <li>На экране 1 введите фамилию (любую), номер группы, если вы учитесь, и вашу роль.</li>
        <li>На экране 2 в текстовом поле введите запрос в форме <span>ищу позицию [название профессии]</span> по вашему желанию. Будьте реалистичны и вводите название профессии, на которую вы можете претендовать с учетом вашей программы обучения.</li>
        <li>В списке отобразившихся навыков вакансии кликните все, которые кажутся вам ЛИШНИМИ, НЕРЕЛЕВАНТНЫМИ.</li>
        <li>Напротив каждого курса оцените его соответствие вашему запросу по смыслу по семибалльной шкале, где 1 – совсем не подходит, 7 – отлично подходит.</li>
        <li>Прокрутите страницу ниже и ответьте на пять вопросов. Помните, что в вопросах со шкалами <span>1</span> означает совсем неудобно / неполезно, <span>7</span> – очень удобно / полезно.</li>
        <li>Выйдите из системы либо нажмите кнопку <span>сохранить ответы</span> и повторите все действия, на этот раз сформулировав запрос полностью самостоятельно, в свободной форме (например, <span>хочу работать в сфере IT</span>).</li>
    </ul>
</div>
"""