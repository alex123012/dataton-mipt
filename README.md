# dataton-mipt

<!DOCTYPE html>
<html>
<head>
</head>
<body>

<h1>Сервис по отслеживанию чистоты пляжей</h1>

<p>Команда энтузиастов, состоящая из трёх человек – Игоря Климова, Алексея Махонина и Константина Матвеева, которые заботятся об экологии, представляет вам свой сервис. Он призван сохранять чистоту общественных пляжей и вносить вклад в экологию, улучшая нашу общую жизнь.</p>

<h2>Кратко о нашем сервисе</h2>

<p>Наш сервис, основанный на технологиях искусственного интеллекта, определяет степень загрязнения пляжа, опираясь на онлайн-видеопоток. В случае обнаружения сильного загрязнения, мы уведомляем вас или муниципальные службы о необходимости очистки этого пляжа. Мы уверены, что такой подход поможет сохранить пляжи в чистоте и сделает жизнь более комфортной.</p>

<h2>Технологии, используемые сервисом</h2>

<ol>
    <li><strong>Искусственный интеллект и машинное обучение:</strong>
        <p>В своем проекте мы используем модель "keremberke/yolov5m-garbage"  [ https://huggingface.co/keremberke/yolov5m-garbage], которая является продвинутой реализацией архитектуры YOLOv5 (You Only Look Once, версия 5), адаптированной для обнаружения и классификации мусора. YOLOv5 - это выдающаяся архитектура для задач обнаружения объектов в реальном времени, отличающаяся своей скоростью и точностью. Эта модификация учитывает специфические требования обнаружения отходов, оптимизируя процесс обнаружения разнообразных типов мусора. Основываясь на стандартной структуре YOLOv5, модель "keremberke/yolov5m-garbage" обеспечивает эффективную работу в реальных условиях.

На Hugging Face модель “keremberke/yolov5m-garbage” предлагает удобную установку и использование, поддерживая различные параметры для предсказаний. Она может быть дополнительно настроена на пользовательских наборах данных. На валидационном наборе модель показала mAP@0.5 равное 0.427. Важно отметить, что модель обучена на датасете Garbage Classification от Roboflow [https://universe.roboflow.com/material-identification/garbage-classification-3/dataset/1/images], который включает в себя около 16 тысяч фотографий мусора, обеспечивая широкий диапазон данных для эффективного обучения. <a href="./images/">примеры работы модели</a></p>
    </li>
    <li><strong>Обработка и анализ видеоданных:</strong>
        <p>Для анализа видеопотоков в реальном времени мы используем комбинацию OpenCV и других библиотек обработки изображений. Для преобразования видеопотока в анализируемые кадры используется алгоритм frame sampling, который извлекает изображения из видео с заданной периодичностью.</p>
    </li>
    <li><strong>Обнаружение и классификация мусора:</strong>
        <p>Наша система не только обнаруживает присутствие мусора, но и классифицирует его по типам (пластик, стекло, металл и т.д.), что позволяет проводить более целенаправленные очистительные операции.</p>
    </li>
    <li><strong>Оповещения и интеграция с муниципальными службами:</strong>
        <p>При обнаружении загрязнения пляжа, сервис автоматически генерирует уведомления. Мы используем различные библиотеки Python, такие как SMTP библиотеки для отправки электронной почты.</p>
    </li>
    <li><strong>Пользовательский интерфейс и доступ:</strong>
        <p>Наш веб-сайт предлагает интуитивно понятный интерфейс, где пользователи могут загружать ссылки на видеопотоки и настраивать параметры оповещений. Мы используем современные фреймворки веб-разработки для создания динамичного и отзывчивого пользовательского интерфейса.</p>
    </li>
</ol>

<h2>Пользовательский путь</h2>

<p>Мы предоставляем доступ к нашему сайту по ссылке. Там вы можете указать ссылку на видеопоток, который будет анализировать наш сервис, а также выбрать канал связи для получения оповещений о загрязненности пляжа, если таковая будет обнаружена.</p>

<p class="conclusion">Мы стремимся сделать мир лучше и чище, внося свой вклад в сохранение чистоты пляжей!</p>

</body>
</html>
