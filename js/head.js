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

const initializeObservers = (target) => {
    // Инициализация слайдеров в 'subject-info' и 'add-range'
    initializeSliders(target, 'div.subject-info > div.info > div.range > div.subject_relevance')
    initializeSliders(target, 'div.add-range > div.range > div.slider-container')

    // Добавление обработчиков кликов для элементов навыков
    target
        .querySelectorAll('div.subject-info > div.info > div.info-skills > span.value > span.skill')
        .forEach(toggleClassOnClick)
}

/**
 * Инициализирует слайдеры для заданных элементов, если они не были инициализированы.
 * @param {Element} target - Элемент, внутри которого нужно инициализировать слайдеры.
 * @param {string} selector - Селектор для поиска элементов слайдеров.
 */
const initializeSliders = (target, selector) => {
    target.querySelectorAll(selector).forEach((element) => {
        if (!element.classList.contains('initialized')) {
            new Slider(element, { min: 1, max: 7, value: 4 })
            element.classList.add('initialized')
        }
    })
}

const NO_DATA = 'Нет данных'
const NOT_SPECIFIED = 'не указан'

/**
 * Извлекает данные из полей ввода с классами предков .user-info и .dropdown-user.
 * @param {string} containerSelector - Селектор контейнера с данными пользователя.
 * @returns {Object} Объект с данными полей ввода.
 */
function extractUserInputData(containerSelector) {
    const userContainer = document.querySelector(containerSelector)

    if (!userContainer) {
        console.error('Элемент контейнера пользователя не найден')
        return { error: 'Container not found' }
    }

    // Извлечение значений полей
    const userInfoLabels = userContainer.querySelectorAll('span[data-testid="block-info"]')
    const userInfoInputs = userContainer.querySelectorAll('.user-info input')
    const dropdownUserInput = userContainer.querySelector('.dropdown-user input')

    const userData = {
        [userInfoLabels[0]?.textContent.trim() || NO_DATA]: userInfoInputs[0]?.value || NO_DATA, // Первый input
        [userInfoLabels[1]?.textContent.trim() || NO_DATA]: userInfoInputs[1]?.value || NO_DATA, // Второй input
        [userInfoLabels[2]?.textContent.trim() || NO_DATA]: dropdownUserInput?.value || NO_DATA, // Третий input
    }

    return userData
}

/**
 * Извлекает навыки из указанного контейнера.
 * @param {Element} container - DOM-элемент, содержащий навыки.
 * @param {string} skillsSelector - Селектор для навыков.
 * @returns {Object} Объект с релевантными и удаленными навыками.
 */
function extractSkills(container, skillsSelector) {
    let skillsLabel = container.querySelector(`${skillsSelector} .label`)?.textContent.trim() || NO_DATA

    // Удаляем двоеточие из конца строки, если оно есть
    skillsLabel = skillsLabel.replace(/:$/, '')

    // Извлечение всех навыков
    const allSkills = [...container.querySelectorAll(`${skillsSelector} .value .skill`)].map((skill) =>
        skill.textContent.trim(),
    )

    // Извлечение навыков, которые помечены как удаленные
    const deletedSkills = [...container.querySelectorAll(`${skillsSelector} .value .skill.deleted`)].map((skill) =>
        skill.textContent.trim(),
    )

    // Фильтрация релевантных навыков
    const deletedSkillsSet = new Set(deletedSkills)
    const relevantSkills = allSkills.filter((skill) => !deletedSkillsSet.has(skill))

    return {
        [`${skillsLabel} (релевантные)`]: relevantSkills,
        [`${skillsLabel} (удаленные)`]: deletedSkills,
    }
}

/**
 * Извлекает данные о релевантности курса с возможностью задать кастомный лейбл.
 * @param {Element} infoBlock - Блок с информацией о курсе.
 * @param {string} [customLabel] - (Необязательный) Кастомный лейбл для диапазона.
 * @returns {Object} Объект с данными о релевантности курса.
 */
function extractRangeData(rangeBlock, customLabel) {
    // const rangeBlock = infoBlock.querySelector('.range');

    let rangeLabel = customLabel || rangeBlock.querySelector('label')?.textContent.trim() || NO_DATA
    const rangeValue = rangeBlock.querySelector('input[type="hidden"]')?.value || NO_DATA

    // Удаляем двоеточие из конца строки, если оно есть
    rangeLabel = rangeLabel.replace(/:$/, '')

    return { [rangeLabel]: rangeValue }
}

/**
 * Извлекает детали курса из блока информации.
 * @param {Element} infoBlock - Блок с информацией о курсе.
 * @returns {Object} Объект с деталями курса.
 */
function extractCourseData(infoBlock) {
    const infoItems = infoBlock.querySelectorAll('.info-item')
    const courseDetails = {}

    infoItems.forEach((item) => {
        const label = item.querySelector('.label')?.textContent.trim() || NO_DATA
        const value = item.querySelector('.value')?.textContent.trim() || NO_DATA
        courseDetails[label] = value
    })

    // Проверка наличия блока ошибки номера обучения
    if (infoBlock.querySelector('.info-number-education-error')) {
        courseDetails['Курс обучения'] = NOT_SPECIFIED
    }

    return courseDetails
}

/**
 * Извлекает дополнительные навыки из блока .dropdown-add-vacancy-skills.
 * @param {string} containerSelector - Селектор контейнера с дополнительными навыками.
 * @returns {Array} Массив дополнительных навыков.
 */
function extractAdditionalVacancySkills(containerSelector) {
    const container = document.querySelector(containerSelector)

    if (!container) {
        console.error('Элемент контейнера дополнительных навыков не найден')
        return []
    }

    // Находим все элементы с классом 'token' внутри контейнера
    const tokenElements = container.querySelectorAll('.token')

    // Извлекаем текстовые значения из span внутри каждого элемента 'token'
    const skills = [...tokenElements].map((token) => {
        const skillText = token.querySelector('span')?.textContent.trim() || NO_DATA
        return skillText
    })

    return skills
}

// Функция для отправки данных на сервер
function sendDataToServer(data) {
    fetch('http://127.0.0.1:8000/api/submit', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    })
        .then((response) => {
            if (!response.ok) {
                throw new Error('Ошибка сети при отправке данных')
            }
            return response.json()
        })
        .then((responseData) => {
            if (responseData.status === 'success') {
                // Действия при успешной обработке
                alert(responseData.message)
            } else if (responseData.status === 'error') {
                // Действия при ошибке на сервере
                alert('Ошибка сервера: ' + responseData.error)
                // Дополнительная информация об ошибке: responseData.error
            } else {
                // Обработка неожиданных статусов
                alert('Неизвестный статус ответа от сервера.')
            }
        })
        .catch((error) => {
            // Обработка ошибок без вывода деталей в консоль
            alert('Не удалось отправить данные на сервер. Пожалуйста, попробуйте позже.')
        })
}

/**
 * Основная функция для обработки данных при нажатии кнопки.
 */

function handleButtonClick() {
    const result = {
        user_id: null,
        user_data: null,
        user_message: NO_DATA,
        vacancy: null,
        edu_groups: [],
        additional_vacancy_skills: [],
        feedback: null,
    }

    // Извлечение данных пользователя
    result.user_id = document.querySelector('.block.user-id input')?.value.trim() || NO_DATA;

    // Извлечение данных пользователя
    result.user_data = extractUserInputData('.user-container .form')

    // Поиск сообщения пользователя
    result.user_message =
        document.querySelector('.chatbot-container .message.user button > span.chatbot.prose')?.textContent.trim() ||
        NO_DATA

    // Поиск контейнера с ответом бота
    const spanContainer = document.querySelector('.chatbot-container .message.bot button > span.chatbot.prose')

    if (!spanContainer) {
        console.error('Элемент span с классами chatbot prose не найден')
        return
    }

    // Извлечение информации о вакансии
    const subjectInfo = spanContainer.querySelector('.subject-info')
    if (subjectInfo && subjectInfo.parentElement === spanContainer) {
        result.vacancy = extractSkills(subjectInfo, '.info-skills')
    } else {
        console.error('Элемент .subject-info не найден')
        return
    }

    // Обработка групп образовательных программ
    const eduGroups = spanContainer.querySelectorAll('.edu-group')

    if (eduGroups.length > 0) {
        eduGroups.forEach((eduGroup, index) => {
            const groupLabel = eduGroup.querySelector('span')?.textContent.trim() || `Группа ${index + 1}`

            // Извлечение курсов из текущей группы
            const courses = [...eduGroup.querySelectorAll('.info')].map((infoBlock) => {
                const courseDetails = extractCourseData(infoBlock)
                const relevanceData = extractRangeData(infoBlock.querySelector('.range'))
                const pudSkills = extractSkills(infoBlock, '.info-skills')

                return {
                    ...courseDetails,
                    ...relevanceData,
                    ...pudSkills,
                }
            })

            result.edu_groups.push({
                label: groupLabel,
                courses: courses,
            })
        })
    } else {
        console.error('Элементы .edu-group не найдены')
    }

    // Извлечение дополнительных навыков вакансии
    result.additional_vacancy_skills = extractAdditionalVacancySkills('.dropdown-add-vacancy-skills')

    // Извлечение данных из блока с оценкой сервиса
    const addRangeContainer = document.querySelector('.block.add-range')
    if (addRangeContainer) {
        const customLabels = ['Полезность', 'Востребованность', 'Удобство']

        const ranges = [...addRangeContainer.querySelectorAll('.range')].map((rangeBlock, index) => {
            // Получаем кастомный лейбл для текущего rangeBlock
            const customLabel = customLabels[index] || `Диапазон ${index + 1}`
            return extractRangeData(rangeBlock, customLabel)
        })

        // Объединяем все диапазоны в один объект
        result.additional_ranges = Object.assign({}, ...ranges)
    } else {
        console.error('Элемент .add-range не найден')
    }

    // Извлечение отзыва пользователя из textarea внутри .block .feedback
    result.feedback = document.querySelector('.block.feedback textarea')?.value.trim() || NO_DATA

    // Вывод итогового результата
    console.log('Полный результат:', JSON.stringify(result, null, 2))

    // Отправка данных на сервер
    sendDataToServer(result)

    return result
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
