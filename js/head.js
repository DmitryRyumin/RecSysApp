// Функция для обработки клика по элементам
function toggleClassOnClick(element) {
    element.addEventListener('click', function () {
        element.classList.toggle('deleted')
    })
}

class Slider {
    constructor(element, options = {}) {
        this.element = element
        this.min = options.min || 0
        this.max = options.max || 100
        this.value = options.value || this.min
        this.step = options.step || 1
        this.init()
    }

    init() {
        this.sliderContainer = document.createElement('div')
        this.sliderContainer.className = 'slider'

        this.input = document.createElement('input')
        this.input.type = 'range'
        this.input.min = this.min
        this.input.max = this.max
        this.input.value = this.value
        this.input.step = this.step

        this.hiddenInput = document.createElement('input')
        this.hiddenInput.type = 'hidden'
        this.hiddenInput.value = this.value

        this.input.addEventListener('input', (e) => this.handleChange(e))

        this.sliderValue = document.createElement('div')
        this.sliderValue.className = 'slider-value'

        this.sliderContainer.appendChild(this.input)
        this.sliderContainer.appendChild(this.hiddenInput)
        this.sliderContainer.appendChild(this.sliderValue)

        this.element.appendChild(this.sliderContainer)

        this.renderNumbers()
        this.updateBackground()
    }

    handleChange(e) {
        this.value = e.target.value
        this.hiddenInput.value = this.value
        this.updateNumbers()
        this.updateBackground()
    }

    percent() {
        return ((this.value - this.min) * 100) / (this.max - this.min)
    }

    renderNumbers() {
        const length = this.max.toString().length
        for (let i = 0; i < length; i++) {
            const numberContainer = document.createElement('div')
            numberContainer.className = 'slider-value-number'

            const ul = document.createElement('ul')
            for (let j = 0; j < 10; j++) {
                const li = document.createElement('li')
                li.textContent = j
                ul.appendChild(li)
            }

            numberContainer.appendChild(ul)
            this.sliderValue.appendChild(numberContainer)
        }
        this.updateNumbers()
    }

    updateNumbers() {
        const valueStr = this.value.toString().padStart(this.max.toString().length, '0') // Ensure the string length is consistent with `max`
        const length = this.max.toString().length

        Array.from(this.sliderValue.children).forEach((numberContainer, index) => {
            const charIndex = index - (length - valueStr.length)
            const isVisible = charIndex >= 0
            const digit = isVisible ? valueStr[charIndex] : '0'
            const position = isVisible ? `-${parseInt(digit) * 10}%` : '10%'

            const ul = numberContainer.querySelector('ul')
            ul.style.transform = `translateY(${position})`
            ul.style.opacity = isVisible ? '1' : '0'
        })
    }

    updateBackground() {
        this.input.style.backgroundSize = `${this.percent()}% 100%`
    }
}

// Функция для инициализации слайдеров и добавления обработчиков событий
const initializeObservers = (target) => {
    // Инициализация слайдеров
    target.querySelectorAll('div.subject-info > div.info > div.range > div.subject_relevance').forEach((element) => {
        if (!element.classList.contains('initialized')) {
            new Slider(element, { min: 1, max: 7, value: 4 })
            element.classList.add('initialized')
        }
    })

    // Добавление обработчиков кликов для элементов навыков
    target
        .querySelectorAll('div.subject-info > div.info > div.info-skills > span.value > span.skill')
        .forEach(toggleClassOnClick)
}

// Функция для обработки клика по кнопке
// function handleButtonClick() {
//     // Включаем обновление страницы для пересчета изменений
//     requestAnimationFrame(() => {
//         const chatbot = document.querySelector('div.chatbot-container > div.chatbot button[data-testid="bot"]')
//         if (chatbot) {
//             const ariaLabel = chatbot.getAttribute('aria-label')
//             console.log('Обновленное значение aria-label:', ariaLabel)
//         } else {
//             console.log('Элемент chatbot не найден')
//         }
//     })
// }

function extractVacancySkills(subjectInfo) {

    const allSkills = Array.from(subjectInfo.querySelectorAll('.value .skill')).map((skill) =>
        skill.textContent.trim()
    );
    const deletedSkills = Array.from(subjectInfo.querySelectorAll('.value .skill.deleted')).map((skill) =>
        skill.textContent.trim()
    );

    return {
        vacancy_skills: allSkills,
        vacancy_skills_deleted: deletedSkills,
    };
}

// Функция для извлечения данных из блока range в edu-group
function extractRangeData(infoBlock) {
    const rangeBlock = infoBlock.querySelector('.range');
    if (!rangeBlock) {
        return { 'Релевантность курса': 'Нет данных' };
    }

    let rangeLabel = rangeBlock.querySelector('label')?.textContent.trim() || 'Нет данных';
    const rangeValue = rangeBlock.querySelector('input[type="hidden"]')?.value || 'Нет данных';

    // Удаляем двоеточие из конца строки, если оно есть
    if (rangeLabel.endsWith(':')) {
        rangeLabel = rangeLabel.replace(/:$/, '');
    }

    // Используем label как ключ
    return { [rangeLabel]: rangeValue };
}

// Функция для извлечения данных из всех элементов .info-item внутри блока .info
function extractCourseData(infoBlock) {
    const infoItems = infoBlock.querySelectorAll('.info-item');
    const courseDetails = {};

    infoItems.forEach((item) => {
        const label = item.querySelector('.label')?.textContent.trim() || 'Нет данных';
        const value = item.querySelector('.value')?.textContent.trim() || 'Нет данных';
        courseDetails[label] = value;
    });

    // Проверка наличия блока .info-number-education-error
    const educationErrorBlock = infoBlock.querySelector('.info-number-education-error');
    if (educationErrorBlock) {
        courseDetails['Курс обучения'] = 'не указан';
    }

    return courseDetails;
}

// Функция для извлечения данных о получаемых навыках
function extractPUDskills(infoBlock) {
    let skillsLabel = infoBlock.querySelector('.info-skills .label')?.textContent.trim() || 'Нет данных';

    // Удаляем двоеточие из конца строки, если оно есть
    if (skillsLabel.endsWith(':')) {
        skillsLabel = skillsLabel.replace(/:$/, '');
    }

    const allSkills = Array.from(infoBlock.querySelectorAll('.info-skills .value .skill')).map(skill =>
        skill.textContent.trim()
    );
    const deletedSkills = Array.from(infoBlock.querySelectorAll('.info-skills .value .skill.deleted')).map(skill =>
        skill.textContent.trim()
    );

    return {
        [skillsLabel]: allSkills,
        [`${skillsLabel} (удаленные)`]: deletedSkills
    };
}

function handleButtonClick() {

    // Инициализация переменной для итогового JSON
    let result = {
        user_message: null,
        vacancy: null,
        edu_groups: [],
    };

    // Поиск сообщения пользователя
    const userMessage = document.querySelector('.chatbot-container .message.user button > span.chatbot.prose');

    if (userMessage) {
        result.user_message = userMessage.textContent.trim() || 'Нет данных';
    } else {
        console.log('Сообщение пользователя не найдено!');
    }

    // Поиск элемента span с классами chatbot и prose, который является прямым потомком кнопки
    const spanContainer = document.querySelector('.chatbot-container .message.bot button > span.chatbot.prose');

    if (!spanContainer) {
        console.log('Элемент span с классами chatbot prose не найден');
        return;
    }

    // Поиск элемента .subject-info где лежат вакансии
    const subjectInfo = spanContainer.querySelector('.subject-info');

    if (subjectInfo && subjectInfo.parentElement === spanContainer) {
        // Вызов функции для извлечения данных о навыках вакансии
        const vacancyData = extractVacancySkills(subjectInfo);

        // Добавление данных о вакансиях в итоговый JSON
        result.vacancy = vacancyData;

        // console.log('Результат после обработки вакансий:', JSON.stringify(result, null, 2));
    } else {
        console.log('Элемент .subject-info не найден');
        return;
    }

    // ОБРАБОТКА ВСЕХ ЭЛЕМЕНТОВ EDU-GROUP
    const eduGroups = spanContainer.querySelectorAll('.edu-group');

    if (eduGroups.length > 0) {
        // Проход по каждому элементу .edu-group
        Array.from(eduGroups).forEach((eduGroup, index) => {
            const groupLabel = eduGroup.querySelector('span')?.textContent.trim() || `Группа ${index + 1}`;

            // Извлечение всех курсов из .info внутри текущей edu-group
            const courses = Array.from(eduGroup.querySelectorAll('.info')).map((infoBlock) => {
                // Извлечение данных из всех элементов .info-item и других блоков
                const courseDetails = extractCourseData(infoBlock);
                const relevanceData = extractRangeData(infoBlock);
                const pudSkills = extractPUDskills(infoBlock);

                return {
                    ...courseDetails, // Добавляем все извлеченные данные (discipline, id и т.д.)
                    ...relevanceData, // Добавляем данные о релевантности
                    ...pudSkills, // Добавляем данные о получаемых навыках
                };
            });

            // Добавление группы и её данных в JSON
            result.edu_groups.push({
                label: groupLabel,
                courses: courses,
            });
        });
    } else {
        console.log('Элементы .edu-group не найдены');
    }

    // Выводим итоговый результат в консоль
    console.log('Полный результат:', JSON.stringify(result, null, 2));

    // Вернуть результат, если потребуется
    return result;
}

// Наблюдатель за добавлением кнопки send_evaluate
const buttonObserver = new MutationObserver(() => {
    const button = document.querySelector('.send_evaluate')
    if (button && !button.hasAttribute('data-listener')) {
        // проверяем, чтобы обработчик не был добавлен дважды
        button.addEventListener('click', handleButtonClick)
        button.setAttribute('data-listener', 'true') // Отметим, что обработчик добавлен
    }
})

// Начнем отслеживать изменения в DOM для кнопки
buttonObserver.observe(document.body, { childList: true, subtree: true })

// Создание и запуск MutationObserver для инициализации слайдеров
const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
        if (mutation.type === 'childList') {
            mutation.addedNodes.forEach((node) => {
                if (node.nodeType === Node.ELEMENT_NODE) {
                    initializeObservers(node) // Инициализация для нового узла
                }
            })
        }
    })
})

// Наблюдаем за изменениями в DOM
observer.observe(document.body, { childList: true, subtree: true })

// Начальная инициализация для существующих элементов
initializeObservers(document)
